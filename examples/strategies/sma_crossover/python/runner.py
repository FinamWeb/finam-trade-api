"""Market-data and order orchestration for the SMA crossover example."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from finam_trade_api import FinamClient
from finam_trade_api.accounts import GetAccountRequest
from finam_trade_api.auth_messages import TokenDetailsRequest
from finam_trade_api.market_data import Bar, BarsRequest, SubscribeBarsRequest
from finam_trade_api.orders import Order, OrderStatus, OrderType, Side, TimeInForce
from google.protobuf.timestamp_pb2 import Timestamp
from google.type.decimal_pb2 import Decimal as ProtoDecimal
from google.type.interval_pb2 import Interval

from config import TIMEFRAMES, Config
from strategy import Signal, evaluate

logger = logging.getLogger(__name__)


def _bar_key(bar: Bar) -> tuple[int, int]:
    return bar.timestamp.seconds, bar.timestamp.nanos


def ordered_bars(bars: Sequence[Bar]) -> list[Bar]:
    """Sort bars and keep the newest update for each timestamp."""

    by_timestamp = {_bar_key(bar): bar for bar in bars}
    return [by_timestamp[timestamp] for timestamp in sorted(by_timestamp)]


def _decimal(value: ProtoDecimal) -> Decimal:
    return Decimal(value.value or "0")


def _history(client: FinamClient, config: Config) -> tuple[list[Decimal], Bar]:
    timeframe, lookback_days = TIMEFRAMES[config.timeframe]
    end = datetime.now(timezone.utc)
    start_timestamp, end_timestamp = Timestamp(), Timestamp()
    start_timestamp.FromDatetime(end - timedelta(days=lookback_days))
    end_timestamp.FromDatetime(end)

    response = client.market_data.Bars(
        BarsRequest(
            symbol=config.symbol,
            timeframe=timeframe,
            interval=Interval(start_time=start_timestamp, end_time=end_timestamp),
        )
    )
    bars = ordered_bars(response.bars)
    if len(bars) < 31:
        raise RuntimeError(f"at least 31 historical bars are required; received {len(bars)}")

    # Keep the newest bar pending because it may still be changing.
    return [_decimal(bar.close) for bar in bars[:-1]], bars[-1]


def _position(client: FinamClient, account_id: str, symbol: str) -> Decimal:
    account = client.accounts.GetAccount(GetAccountRequest(account_id=account_id))
    match = next((item for item in account.positions if item.symbol == symbol), None)
    return _decimal(match.quantity) if match else Decimal(0)


def resolve_account_id(client: FinamClient) -> str:
    token = client.get_token() or ""
    details = client.auth.TokenDetails(TokenDetailsRequest(token=token))
    if len(details.account_ids) != 1:
        raise RuntimeError(
            f"expected exactly one available account; received {len(details.account_ids)}"
        )
    return str(details.account_ids[0])


def place_order(
    client: FinamClient,
    config: Config,
    account_id: str | None,
    signal: Signal,
    bar: Bar,
) -> None:
    if signal is None:
        return
    if not config.execute:
        logger.warning("DRY RUN: %s %s units of %s", signal, config.quantity, config.symbol)
        return
    if not account_id:
        raise RuntimeError("account ID is required in execute mode")

    current = _position(client, account_id, config.symbol)
    if signal == "entry" and current != 0:
        logger.warning("Skipping entry: current position is %s, expected zero", current)
        return
    if signal == "exit" and current <= 0:
        logger.warning("Skipping exit: there is no long position")
        return

    side = Side.SIDE_BUY if signal == "entry" else Side.SIDE_SELL
    quantity = config.quantity if signal == "entry" else min(current, config.quantity)
    suffix = str(bar.timestamp.seconds)[-10:]
    state = client.orders.PlaceOrder(
        Order(
            account_id=account_id,
            symbol=config.symbol,
            quantity=ProtoDecimal(value=format(quantity, "f")),
            side=side,
            type=OrderType.ORDER_TYPE_MARKET,
            time_in_force=TimeInForce.TIME_IN_FORCE_DAY,
            client_order_id=f"sma9x30-{'b' if signal == 'entry' else 's'}-{suffix}",
            comment="SMA 9/30 crossover",
        )
    )
    logger.warning("Submitted order %s: %s", state.order_id, OrderStatus.Name(state.status))


def run(client: FinamClient, config: Config) -> None:
    account_id = resolve_account_id(client) if config.execute else None
    closes, pending = _history(client, config)
    result = evaluate(closes)
    logger.info("History ready: close=%s sma9=%s sma30=%s", closes[-1], result.fast, result.slow)

    if config.check:
        print(
            f"History check passed: close={closes[-1]} "
            f"sma9={result.fast} sma30={result.slow} signal={result.signal or 'none'}"
        )
        return

    timeframe = TIMEFRAMES[config.timeframe][0]
    request = SubscribeBarsRequest(symbol=config.symbol, timeframe=timeframe)
    for response in client.market_data.SubscribeBars(request):
        for bar in ordered_bars(response.bars):
            if _bar_key(bar) < _bar_key(pending):
                continue
            if _bar_key(bar) == _bar_key(pending):
                pending = bar
                continue

            closes = [*closes, _decimal(pending.close)][-31:]
            result = evaluate(closes)
            logger.info(
                "Closed bar: close=%s sma9=%s sma30=%s signal=%s",
                closes[-1],
                result.fast,
                result.slow,
                result.signal or "none",
            )
            place_order(client, config, account_id, result.signal, pending)
            pending = bar
