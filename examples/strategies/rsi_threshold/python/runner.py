"""Market-data and order orchestration for the RSI threshold example."""

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
from strategy import HISTORY_CLOSES, MINIMUM_CLOSES, Signal, evaluate

logger = logging.getLogger(__name__)

_DISPLAY = Decimal("0.000001")


def _bar_key(bar: Bar) -> tuple[int, int]:
    return bar.timestamp.seconds, bar.timestamp.nanos


def ordered_bars(bars: Sequence[Bar]) -> list[Bar]:
    """Sort bars and keep the newest update for each timestamp."""

    by_timestamp = {_bar_key(bar): bar for bar in bars}
    return [by_timestamp[timestamp] for timestamp in sorted(by_timestamp)]


def _decimal(value: ProtoDecimal) -> Decimal:
    return Decimal(value.value or "0")


def _format(value: Decimal) -> str:
    """Round a value for display only; the rule uses the full value."""

    return str(value.quantize(_DISPLAY))


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
    required = MINIMUM_CLOSES + 1
    if len(bars) < required:
        raise RuntimeError(
            f"at least {required} historical bars are required; received {len(bars)}"
        )

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
) -> bool:
    """Act on a signal and report whether to adopt the position it implies.

    A dry run only logs, but still adopts, so the simulated position tracks the
    rule. An entry blocked by a guard is not adopted, which keeps the strategy
    flat and free to act on the next signal. An exit blocked because the account
    holds nothing is adopted, because the guard has just confirmed that the
    strategy is flat; an order that never filled cannot strand it.
    """

    if signal is None:
        return False
    if not config.execute:
        logger.warning("DRY RUN: %s %s units of %s", signal, config.quantity, config.symbol)
        return True
    if not account_id:
        raise RuntimeError("account ID is required in execute mode")

    current = _position(client, account_id, config.symbol)
    if signal == "entry" and current != 0:
        logger.warning("Skipping entry: current position is %s, expected zero", current)
        return False
    if signal == "exit" and current <= 0:
        logger.warning("Skipping exit: there is no long position")
        return True

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
            client_order_id=f"rsi14-{'b' if signal == 'entry' else 's'}-{suffix}",
            comment="RSI threshold",
        )
    )
    logger.warning("Submitted order %s: %s", state.order_id, OrderStatus.Name(state.status))
    return True


def run(client: FinamClient, config: Config) -> None:
    account_id = resolve_account_id(client) if config.execute else None
    closes, pending = _history(client, config)
    result = evaluate(closes)
    logger.info("History ready: close=%s rsi=%s", closes[-1], _format(result.rsi))

    if config.check:
        print(
            f"History check passed: close={closes[-1]} rsi={_format(result.rsi)} "
            f"average_gain={_format(result.average_gain)} "
            f"average_loss={_format(result.average_loss)} signal={result.signal or 'none'}"
        )
        return

    # The strategy starts flat and never adopts a position it did not open.
    in_position = False
    timeframe = TIMEFRAMES[config.timeframe][0]
    request = SubscribeBarsRequest(symbol=config.symbol, timeframe=timeframe)
    for response in client.market_data.SubscribeBars(request):
        for bar in ordered_bars(response.bars):
            if _bar_key(bar) < _bar_key(pending):
                continue
            if _bar_key(bar) == _bar_key(pending):
                pending = bar
                continue

            closes = [*closes, _decimal(pending.close)][-HISTORY_CLOSES:]
            result = evaluate(closes, in_position)
            logger.info(
                "Closed bar: close=%s rsi=%s average_gain=%s average_loss=%s signal=%s",
                closes[-1],
                _format(result.rsi),
                _format(result.average_gain),
                _format(result.average_loss),
                result.signal or "none",
            )
            if place_order(client, config, account_id, result.signal, pending):
                in_position = result.signal == "entry"
            pending = bar
