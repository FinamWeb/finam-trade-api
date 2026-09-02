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
from strategy import MINIMUM_CLOSES, NEUTRAL, evaluate

# One oversold entry and one overbought exit; see the walk-forward test.
ENTRY_INDEX = 24
EXIT_INDEX = 71


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


def sample_closes(count: int = 95) -> list[Decimal]:
    """Sideways, then a sell-off into oversold, then a rally into overbought."""

    closes = []
    for index in range(count):
        if index < 20:
            base = 100.0
        elif index < 50:
            base = 100 - (index - 20) * 0.8
        else:
            base = 76 + (index - 50) * 0.8
        value = base + math.sin(index * 0.7) * 0.45 + math.sin(index * 0.19) * 0.3
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


def ramp(step: int) -> list[Decimal]:
    """A warm-up window whose closes all move by the same step."""

    return [Decimal(50 + index * step) for index in range(MINIMUM_CLOSES)]


def history_bars(count: int = MINIMUM_CLOSES + 1) -> list[Bar]:
    return [make_bar(index, str(index)) for index in range(1, count + 1)]


def test_evaluate_enters_when_oversold_and_exits_when_overbought() -> None:
    closes = sample_closes()
    in_position = False
    events = []
    for index in range(MINIMUM_CLOSES, len(closes) + 1):
        signal = evaluate(closes[:index], in_position).signal
        if signal:
            events.append((index - 1, signal))
            in_position = signal == "entry"

    assert events == [(ENTRY_INDEX, "entry"), (EXIT_INDEX, "exit")]


def test_entry_is_the_first_close_below_the_entry_level() -> None:
    closes = sample_closes()
    before = evaluate(closes[:ENTRY_INDEX])
    assert before.rsi >= Decimal("0.2")
    assert before.signal is None
    assert evaluate(closes[: ENTRY_INDEX + 1]).rsi < Decimal("0.2")


def test_exit_is_the_first_close_above_the_exit_level() -> None:
    closes = sample_closes()
    previous = evaluate(closes[:EXIT_INDEX], True).rsi
    current = evaluate(closes[: EXIT_INDEX + 1], True).rsi
    assert previous <= Decimal("0.8") < current


def test_evaluate_ignores_an_oversold_reading_while_in_position() -> None:
    # The candle after the entry is still oversold; the position flag, not the
    # level, is what stops a second entry.
    closes = sample_closes()
    assert evaluate(closes[: ENTRY_INDEX + 2], True).signal is None
    assert evaluate(closes[: ENTRY_INDEX + 2], False).signal == "entry"


def test_evaluate_ignores_an_overbought_reading_while_flat() -> None:
    closes = sample_closes()
    assert evaluate(closes[: EXIT_INDEX + 2], False).signal is None
    assert evaluate(closes[: EXIT_INDEX + 2], True).signal == "exit"


# A steady ramp puts every change on one side of the ratio, and a flat series
# has no change at all.
@pytest.mark.parametrize(
    ("market", "step", "in_position", "rsi", "signal"),
    [
        ("only gains", 1, True, Decimal(1), "exit"),
        ("only losses", -1, False, Decimal(0), "entry"),
        ("no change", 0, False, NEUTRAL, None),
    ],
)
def test_evaluate_reads_a_one_sided_market(
    market: str,
    step: int,
    in_position: bool,
    rsi: Decimal,
    signal: str | None,
) -> None:
    result = evaluate(ramp(step), in_position)
    assert result.rsi == rsi, market
    assert result.signal == signal


def test_evaluate_reports_wilder_averages_alongside_the_ratio() -> None:
    result = evaluate(ramp(1))
    assert result.average_gain == Decimal(1)
    assert result.average_loss == Decimal(0)


def test_evaluate_requires_the_warm_up_window() -> None:
    with pytest.raises(ValueError, match="15 closes"):
        evaluate([Decimal(1)] * (MINIMUM_CLOSES - 1))


def test_evaluate_rejects_levels_out_of_order() -> None:
    closes = sample_closes()
    with pytest.raises(ValueError, match="entry_level < exit_level"):
        evaluate(closes, entry_level=Decimal("0.8"), exit_level=Decimal("0.2"))


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
    with pytest.raises(RuntimeError, match="at least 16 historical bars are required"):
        run(client, config(check=True))  # type: ignore[arg-type]


def test_stream_confirms_the_pending_bar(caplog: pytest.LogCaptureFixture) -> None:
    history = history_bars()
    update = BarsResponse(bars=[make_bar(16, "16.5"), make_bar(17, "17")])
    client = FakeClient(history, updates=[update])

    with caplog.at_level(logging.INFO, logger="runner"):
        run(client, config())  # type: ignore[arg-type]

    assert "Closed bar: close=16.5" in caplog.text
    assert client.account_calls == 0
    assert client.placed == []


def test_dry_run_stream_alternates_entry_and_exit(caplog: pytest.LogCaptureFixture) -> None:
    bars = [make_bar(index + 1, str(close)) for index, close in enumerate(sample_closes())]
    client = FakeClient(bars[:20], updates=[BarsResponse(bars=bars[20:])])

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
    assert client.placed[0].client_order_id == "rsi14-b-1"


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
