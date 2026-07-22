"""Runnable SMA 9/30 example using the brand-neutral SDK facade."""

from __future__ import annotations

import argparse
import logging
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Optional, Sequence

from google.protobuf.timestamp_pb2 import Timestamp
from google.type.decimal_pb2 import Decimal as ProtoDecimal
from google.type.interval_pb2 import Interval

from trade_api import (
    Bar,
    BarsRequest,
    Client,
    GetAccountRequest,
    Order,
    OrderStatus,
    OrderType,
    Side,
    SubscribeBarsRequest,
    TimeFrame,
    TimeInForce,
)

from .strategy import Signal, evaluate

logger = logging.getLogger(__name__)

# CLI name -> (SDK enum, historical lookback in days).
TIMEFRAMES: dict[str, tuple[int, int]] = {
    "M1": (TimeFrame.TIME_FRAME_M1, 7),
    "M5": (TimeFrame.TIME_FRAME_M5, 14),
    "M15": (TimeFrame.TIME_FRAME_M15, 30),
    "M30": (TimeFrame.TIME_FRAME_M30, 30),
    "H1": (TimeFrame.TIME_FRAME_H1, 30),
    "H2": (TimeFrame.TIME_FRAME_H2, 30),
    "H4": (TimeFrame.TIME_FRAME_H4, 30),
    "H8": (TimeFrame.TIME_FRAME_H8, 30),
    "D": (TimeFrame.TIME_FRAME_D, 180),
    "W": (TimeFrame.TIME_FRAME_W, 365 * 2),
    "MN": (TimeFrame.TIME_FRAME_MN, 365 * 5),
    "QR": (TimeFrame.TIME_FRAME_QR, 365 * 5),
}


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SMA 9/30 crossover strategy")
    parser.add_argument("--secret", default=os.getenv("TRADE_API_SECRET"))
    parser.add_argument("--account-id", default=os.getenv("TRADE_API_ACCOUNT_ID"))
    parser.add_argument("--symbol", default=os.getenv("TRADE_API_SYMBOL"))
    parser.add_argument(
        "--timeframe",
        choices=sorted(TIMEFRAMES),
        default=os.getenv("TRADE_API_TIMEFRAME", "M5").upper(),
    )
    parser.add_argument("--quantity", default=os.getenv("TRADE_API_QUANTITY", "1"))
    parser.add_argument("--execute", action="store_true", help="Place real market orders")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Calculate from historical bars and exit read-only",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=os.getenv("TRADE_API_LOG_LEVEL", "INFO").upper(),
    )
    args = parser.parse_args(argv)

    if not args.secret:
        parser.error("--secret or TRADE_API_SECRET is required")
    if not args.symbol or "@" not in args.symbol:
        parser.error("--symbol must use ticker@mic format, for example SBER@MISX")
    if args.check and args.execute:
        parser.error("--check and --execute cannot be used together")
    if args.execute and not args.account_id:
        parser.error("--account-id or TRADE_API_ACCOUNT_ID is required with --execute")
    try:
        args.quantity = Decimal(args.quantity)
    except InvalidOperation:
        parser.error("--quantity must be a decimal number")
    if not args.quantity.is_finite() or args.quantity <= 0:
        parser.error("--quantity must be positive")
    return args


def _bar_key(bar: Bar) -> tuple[int, int]:
    return bar.timestamp.seconds, bar.timestamp.nanos


def _ordered_bars(bars: Sequence[Bar]) -> list[Bar]:
    """Sort bars and keep the newest update for each timestamp."""

    by_timestamp = {_bar_key(bar): bar for bar in bars}
    return [by_timestamp[key] for key in sorted(by_timestamp)]


def _decimal(value: ProtoDecimal) -> Decimal:
    return Decimal(value.value or "0")


def _history(client: Client, args: argparse.Namespace) -> tuple[list[Decimal], Bar]:
    timeframe, lookback_days = TIMEFRAMES[args.timeframe]
    end = datetime.now(timezone.utc)
    start_timestamp, end_timestamp = Timestamp(), Timestamp()
    start_timestamp.FromDatetime(end - timedelta(days=lookback_days))
    end_timestamp.FromDatetime(end)

    response = client.market_data.Bars(
        BarsRequest(
            symbol=args.symbol,
            timeframe=timeframe,
            interval=Interval(start_time=start_timestamp, end_time=end_timestamp),
        )
    )
    bars = _ordered_bars(response.bars)
    if len(bars) < 31:
        raise RuntimeError(f"at least 31 historical bars are required; received {len(bars)}")

    # Conservatively keep the newest bar pending because it may still be changing.
    return [_decimal(bar.close) for bar in bars[:-1]], bars[-1]


def _position(client: Client, account_id: str, symbol: str) -> Decimal:
    account = client.accounts.GetAccount(GetAccountRequest(account_id=account_id))
    for position in account.positions:
        if position.symbol == symbol:
            return _decimal(position.quantity)
    return Decimal(0)


def _place_order(
    client: Client,
    args: argparse.Namespace,
    signal: Signal,
    bar: Bar,
) -> None:
    if signal is None:
        return
    if not args.execute:
        logger.warning("DRY RUN: %s %s units of %s", signal, args.quantity, args.symbol)
        return

    position = _position(client, args.account_id, args.symbol)
    if signal == "entry" and position != 0:
        logger.warning("Skipping entry: current position is %s, expected zero", position)
        return
    if signal == "exit" and position <= 0:
        logger.warning("Skipping exit: there is no long position")
        return

    side = Side.SIDE_BUY if signal == "entry" else Side.SIDE_SELL
    quantity = args.quantity if signal == "entry" else min(position, args.quantity)
    suffix = str(bar.timestamp.seconds)[-10:]
    state = client.orders.PlaceOrder(
        Order(
            account_id=args.account_id,
            symbol=args.symbol,
            quantity=ProtoDecimal(value=format(quantity, "f")),
            side=side,
            type=OrderType.ORDER_TYPE_MARKET,
            time_in_force=TimeInForce.TIME_IN_FORCE_DAY,
            client_order_id=f"sma9x30-{'b' if signal == 'entry' else 's'}-{suffix}",
            comment="SMA 9/30 crossover",
        )
    )
    logger.warning("Submitted order %s: %s", state.order_id, OrderStatus.Name(state.status))


def run(client: Client, args: argparse.Namespace) -> None:
    closes, pending = _history(client, args)
    fast, slow, signal = evaluate(closes)
    logger.info("History ready: close=%s sma9=%s sma30=%s", closes[-1], fast, slow)

    if args.check:
        print(
            f"History check passed: close={closes[-1]} "
            f"sma9={fast} sma30={slow} signal={signal or 'none'}"
        )
        return

    timeframe = TIMEFRAMES[args.timeframe][0]
    for response in client.market_data.SubscribeBars(
        SubscribeBarsRequest(symbol=args.symbol, timeframe=timeframe)
    ):
        for bar in _ordered_bars(response.bars):
            if _bar_key(bar) < _bar_key(pending):
                continue
            if _bar_key(bar) == _bar_key(pending):
                pending = bar  # another update to the candle still being formed
                continue

            closes.append(_decimal(pending.close))
            closes = closes[-31:]  # two adjacent SMA 30 values need 31 closes
            fast, slow, signal = evaluate(closes)
            logger.info(
                "Closed bar: close=%s sma9=%s sma30=%s signal=%s",
                closes[-1],
                fast,
                slow,
                signal or "none",
            )
            _place_order(client, args, signal, pending)
            pending = bar


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = _parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    if not args.execute and not args.check:
        logger.warning("Dry-run mode: signals are logged but orders are disabled")

    try:
        with Client(secret=args.secret) as client:
            run(client, args)
    except KeyboardInterrupt:
        logger.info("Strategy stopped")


if __name__ == "__main__":
    main()
