import math
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest

from trade_api import Bar, BarsResponse, GetAccountResponse, OrderState, Position, Side

from strategies.sma_crossover.main import _ordered_bars, _place_order, run
from strategies.sma_crossover.strategy import evaluate


def make_bar(seconds: int, close: str = "0") -> Bar:
    bar = Bar()
    bar.timestamp.seconds = seconds
    bar.close.value = close
    return bar


def args(**overrides: Any) -> SimpleNamespace:
    values = {
        "symbol": "SBER@MISX",
        "timeframe": "M5",
        "quantity": Decimal("2"),
        "account_id": "A1",
        "execute": False,
        "check": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class FakeClient:
    def __init__(self, bars: list[Bar], position: str = "0") -> None:
        self.market_data = SimpleNamespace(
            Bars=lambda request: BarsResponse(symbol="SBER@MISX", bars=bars),
            SubscribeBars=lambda request: (_ for _ in ()),
        )
        positions = [] if position == "0" else [Position(symbol="SBER@MISX")]
        if positions:
            positions[0].quantity.value = position
        self.account_calls = 0

        def get_account(request: Any) -> GetAccountResponse:
            self.account_calls += 1
            return GetAccountResponse(account_id="A1", positions=positions)

        self.accounts = SimpleNamespace(GetAccount=get_account)
        self.placed: list[Any] = []

        def place_order(order: Any) -> OrderState:
            self.placed.append(order)
            return OrderState(order_id="order-1")

        self.orders = SimpleNamespace(PlaceOrder=place_order)


def test_evaluate_detects_one_entry_and_one_exit() -> None:
    closes = []
    for index in range(92):
        if index < 32:
            base = 121 - index * 0.42
        elif index < 62:
            base = 107.56 + (index - 32) * 0.72
        else:
            base = 129.16 - (index - 62) * 0.82
        value = base + math.sin(index * 0.7) * 0.65 + math.sin(index * 0.19) * 0.35
        closes.append(Decimal(str(value)))

    signals = [evaluate(closes[: index + 1])[2] for index in range(29, len(closes))]
    assert signals.count("entry") == 1
    assert signals.count("exit") == 1


def test_evaluate_requires_slow_window() -> None:
    with pytest.raises(ValueError, match="30 closes"):
        evaluate([Decimal("1")] * 29)


def test_ordered_bars_sorts_and_keeps_latest_update() -> None:
    bars = _ordered_bars([make_bar(2, "old"), make_bar(1), make_bar(2, "new")])
    assert [bar.timestamp.seconds for bar in bars] == [1, 2]
    assert bars[-1].close.value == "new"


def test_history_check_is_read_only(capsys: pytest.CaptureFixture[str]) -> None:
    client = FakeClient([make_bar(index, str(index)) for index in range(1, 33)])
    run(client, args(check=True))  # type: ignore[arg-type]
    assert "History check passed" in capsys.readouterr().out
    assert client.account_calls == 0
    assert client.placed == []


def test_dry_run_does_not_read_account_or_place_order() -> None:
    client = FakeClient([])
    _place_order(client, args(), "entry", make_bar(1))  # type: ignore[arg-type]
    assert client.account_calls == 0
    assert client.placed == []


def test_live_entry_buys_only_when_flat() -> None:
    client = FakeClient([])
    _place_order(client, args(execute=True), "entry", make_bar(1))  # type: ignore[arg-type]
    assert client.placed[0].side == Side.SIDE_BUY
    assert client.placed[0].quantity.value == "2"


def test_live_exit_cannot_create_a_short() -> None:
    client = FakeClient([], position="0.5")
    _place_order(client, args(execute=True), "exit", make_bar(1))  # type: ignore[arg-type]
    assert client.placed[0].side == Side.SIDE_SELL
    assert client.placed[0].quantity.value == "0.5"
