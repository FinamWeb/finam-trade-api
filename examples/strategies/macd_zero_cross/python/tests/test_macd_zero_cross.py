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
from strategy import MINIMUM_CLOSES, evaluate

# One entry cross and one two-declining-bars exit; see the walk-forward test.
ENTRY_INDEX = 57
EXIT_INDEX = 82


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


def sample_closes(count: int = 110) -> list[Decimal]:
    """A fall, then a rally through zero, then a decline."""

    closes = []
    for index in range(count):
        if index < 45:
            base = 121 - index * 0.42
        elif index < 80:
            base = 102.1 + (index - 45) * 0.72
        else:
            base = 127.3 - (index - 80) * 0.82
        value = base + math.sin(index * 0.7) * 0.65 + math.sin(index * 0.19) * 0.35
        closes.append(Decimal(str(value)))
    return closes


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


def history_bars(count: int = MINIMUM_CLOSES + 1) -> list[Bar]:
    return [make_bar(index, str(index)) for index in range(1, count + 1)]


def test_evaluate_enters_on_the_zero_cross_and_exits_after_two_declines() -> None:
    closes = sample_closes()
    in_position = False
    events = []
    for index in range(MINIMUM_CLOSES, len(closes) + 1):
        signal = evaluate(closes[:index], in_position).signal
        if signal:
            events.append((index - 1, signal))
            in_position = signal == "entry"

    assert events == [(ENTRY_INDEX, "entry"), (EXIT_INDEX, "exit")]


def test_entry_crosses_zero_upwards() -> None:
    closes = sample_closes()
    previous = evaluate(closes[:ENTRY_INDEX]).macd
    current = evaluate(closes[: ENTRY_INDEX + 1]).macd
    assert previous <= 0 < current


def test_exit_follows_two_declining_values() -> None:
    closes = sample_closes()
    values = [evaluate(closes[: EXIT_INDEX + 1 - offset], True).macd for offset in (2, 1, 0)]
    assert values[2] < values[1] < values[0]


def test_evaluate_ignores_a_zero_cross_while_in_position() -> None:
    closes = sample_closes()
    assert evaluate(closes[: ENTRY_INDEX + 1], True).signal is None


def test_evaluate_ignores_declining_values_while_flat() -> None:
    closes = sample_closes()
    assert evaluate(closes[: EXIT_INDEX + 1], False).signal is None


def test_evaluate_reports_the_signal_line_and_histogram() -> None:
    # A unit-slope ramp holds every EMA exactly (window - 1) / 2 behind price,
    # so the MACD line settles on (slow_window - fast_window) / 2.
    result = evaluate([Decimal(index) for index in range(1, MINIMUM_CLOSES + 1)])
    assert result.macd == Decimal(7)
    assert result.signal_line == Decimal(7)
    assert result.histogram == Decimal(0)
    assert result.signal is None


def test_evaluate_requires_the_warm_up_window() -> None:
    with pytest.raises(ValueError, match="34 closes"):
        evaluate([Decimal(1)] * (MINIMUM_CLOSES - 1))


def test_ordered_bars_sorts_and_keeps_latest_update() -> None:
    bars = ordered_bars([make_bar(2, "old"), make_bar(1), make_bar(2, "new")])
    assert [bar.timestamp.seconds for bar in bars] == [1, 2]
    assert bars[-1].close.value == "new"


def test_history_check_is_read_only(capsys: pytest.CaptureFixture[str]) -> None:
    client = FakeClient(history_bars())
    run(client, config(check=True))  # type: ignore[arg-type]
    assert "History check passed" in capsys.readouterr().out
    assert client.token_details_calls == 0
    assert client.account_calls == 0
    assert client.placed == []


def test_history_requires_a_warmed_up_window() -> None:
    client = FakeClient(history_bars(MINIMUM_CLOSES))
    with pytest.raises(RuntimeError, match="at least 35 historical bars are required"):
        run(client, config(check=True))  # type: ignore[arg-type]


def test_stream_confirms_the_pending_bar(caplog: pytest.LogCaptureFixture) -> None:
    history = history_bars()
    update = BarsResponse(bars=[make_bar(35, "35.5"), make_bar(36, "36")])
    client = FakeClient(history, updates=[update])

    with caplog.at_level(logging.INFO, logger="runner"):
        run(client, config())  # type: ignore[arg-type]

    assert "Closed bar: close=35.5" in caplog.text
    assert client.account_calls == 0
    assert client.placed == []


def test_dry_run_stream_alternates_entry_and_exit(caplog: pytest.LogCaptureFixture) -> None:
    bars = [make_bar(index + 1, str(close)) for index, close in enumerate(sample_closes())]
    client = FakeClient(bars[:40], updates=[BarsResponse(bars=bars[40:])])

    with caplog.at_level(logging.WARNING, logger="runner"):
        run(client, config())  # type: ignore[arg-type]

    signals = [line for line in caplog.text.splitlines() if "DRY RUN" in line]
    assert len(signals) == 2
    assert "DRY RUN: entry" in signals[0]
    assert "DRY RUN: exit" in signals[1]


def test_dry_run_does_not_read_account_or_place_order() -> None:
    client = FakeClient([])
    assert place_order(client, config(), None, "entry", make_bar(1)) is True  # type: ignore[arg-type]
    assert client.token_details_calls == 0
    assert client.account_calls == 0
    assert client.placed == []


def test_no_signal_leaves_the_position_unchanged() -> None:
    client = FakeClient([])
    assert place_order(client, config(execute=True), "A1", None, make_bar(1)) is False  # type: ignore[arg-type]
    assert client.account_calls == 0
    assert client.placed == []


def test_live_entry_buys_only_when_flat() -> None:
    client = FakeClient([])
    assert place_order(client, config(execute=True), "A1", "entry", make_bar(1)) is True  # type: ignore[arg-type]
    assert client.placed[0].side == Side.SIDE_BUY
    assert client.placed[0].quantity.value == "2"
    assert client.placed[0].client_order_id == "macd0-b-1"


def test_live_entry_is_skipped_when_a_position_exists() -> None:
    client = FakeClient([], position="3")
    assert place_order(client, config(execute=True), "A1", "entry", make_bar(1)) is False  # type: ignore[arg-type]
    assert client.placed == []


def test_live_exit_without_a_position_returns_the_strategy_to_flat() -> None:
    client = FakeClient([])
    assert place_order(client, config(execute=True), "A1", "exit", make_bar(1)) is True  # type: ignore[arg-type]
    assert client.placed == []


def test_live_exit_cannot_create_a_short() -> None:
    client = FakeClient([], position="0.5")
    assert place_order(client, config(execute=True), "A1", "exit", make_bar(1)) is True  # type: ignore[arg-type]
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
