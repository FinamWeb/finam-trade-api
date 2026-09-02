import logging
import math
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest
from finam_trade_api.accounts import GetAccountResponse, Position
from finam_trade_api.auth_messages import TokenDetailsResponse
from finam_trade_api.market_data import Bar, BarsResponse
from finam_trade_api.orders import OrderState, Side

from config import Config
from runner import ordered_bars, place_order, resolve_account_id, run
from strategy import evaluate


def make_bar(seconds: int, close: str = "0") -> Bar:
    bar = Bar()
    bar.timestamp.seconds = seconds
    bar.close.value = close
    return bar


def config(**overrides: Any) -> Config:
    values = {
        "secret": "secret",
        "symbol": "SBER@MISX",
        "timeframe": "M5",
        "quantity": Decimal(2),
        "execute": False,
        "check": False,
        "log_level": "INFO",
    }
    values.update(overrides)
    return Config(**values)


class FakeClient:
    def __init__(
        self,
        bars: list[Bar],
        position: str = "0",
        updates: list[BarsResponse] | None = None,
        account_ids: list[str] | None = None,
    ) -> None:
        self.token_details_calls = 0

        def token_details(request: Any) -> TokenDetailsResponse:
            self.token_details_calls += 1
            return TokenDetailsResponse(account_ids=account_ids or ["A1"])

        self.auth = SimpleNamespace(TokenDetails=token_details)
        self.get_token = lambda: "jwt"
        self.market_data = SimpleNamespace(
            Bars=lambda request: BarsResponse(symbol="SBER@MISX", bars=bars),
            SubscribeBars=lambda request: iter(updates or []),
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

    signals = [evaluate(closes[: index + 1]).signal for index in range(29, len(closes))]
    assert signals.count("entry") == 1
    assert signals.count("exit") == 1


def test_evaluate_requires_slow_window() -> None:
    with pytest.raises(ValueError, match="30 closes"):
        evaluate([Decimal(1)] * 29)


def test_ordered_bars_sorts_and_keeps_latest_update() -> None:
    bars = ordered_bars([make_bar(2, "old"), make_bar(1), make_bar(2, "new")])
    assert [bar.timestamp.seconds for bar in bars] == [1, 2]
    assert bars[-1].close.value == "new"


def test_history_check_is_read_only(capsys: pytest.CaptureFixture[str]) -> None:
    client = FakeClient([make_bar(index, str(index)) for index in range(1, 33)])
    run(client, config(check=True))  # type: ignore[arg-type]
    assert "History check passed" in capsys.readouterr().out
    assert client.token_details_calls == 0
    assert client.account_calls == 0
    assert client.placed == []


def test_stream_confirms_the_pending_bar(caplog: pytest.LogCaptureFixture) -> None:
    history = [make_bar(index, str(index)) for index in range(1, 33)]
    update = BarsResponse(bars=[make_bar(32, "32.5"), make_bar(33, "33")])
    client = FakeClient(history, updates=[update])

    with caplog.at_level(logging.INFO, logger="runner"):
        run(client, config())  # type: ignore[arg-type]

    assert "Closed bar: close=32.5" in caplog.text
    assert client.account_calls == 0
    assert client.placed == []


def test_dry_run_does_not_read_account_or_place_order() -> None:
    client = FakeClient([])
    place_order(client, config(), None, "entry", make_bar(1))  # type: ignore[arg-type]
    assert client.token_details_calls == 0
    assert client.account_calls == 0
    assert client.placed == []


def test_live_entry_buys_only_when_flat() -> None:
    client = FakeClient([])
    place_order(client, config(execute=True), "A1", "entry", make_bar(1))  # type: ignore[arg-type]
    assert client.placed[0].side == Side.SIDE_BUY
    assert client.placed[0].quantity.value == "2"


def test_live_exit_cannot_create_a_short() -> None:
    client = FakeClient([], position="0.5")
    place_order(client, config(execute=True), "A1", "exit", make_bar(1))  # type: ignore[arg-type]
    assert client.placed[0].side == Side.SIDE_SELL
    assert client.placed[0].quantity.value == "0.5"


def test_resolves_the_sole_account_from_token_details() -> None:
    client = FakeClient([])
    assert resolve_account_id(client) == "A1"  # type: ignore[arg-type]
    assert client.token_details_calls == 1


def test_rejects_ambiguous_account_access() -> None:
    client = FakeClient([], account_ids=["A1", "A2"])
    with pytest.raises(RuntimeError, match="expected exactly one available account; received 2"):
        resolve_account_id(client)  # type: ignore[arg-type]
