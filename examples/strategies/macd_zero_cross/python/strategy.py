"""The MACD zero-cross rule, independent from APIs and order execution."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

FAST_WINDOW = 12
SLOW_WINDOW = 26
SIGNAL_WINDOW = 9

Signal = Literal["entry", "exit"] | None


@dataclass(frozen=True, slots=True)
class Evaluation:
    macd: Decimal
    signal_line: Decimal
    histogram: Decimal
    signal: Signal


def required_closes(
    slow_window: int = SLOW_WINDOW,
    signal_window: int = SIGNAL_WINDOW,
) -> int:
    """Closes needed for a signal line and for three MACD values.

    The first MACD value needs ``slow_window`` closes. The signal line adds
    ``signal_window - 1`` more, and the two-declining-bars rule compares three
    MACD values.
    """

    return max(slow_window + signal_window - 1, slow_window + 2)


# Closes kept while streaming. Ten slow windows make the EMA seed irrelevant to
# the newest value, so a restart converges on the same MACD.
HISTORY_CLOSES = SLOW_WINDOW * 10
MINIMUM_CLOSES = required_closes()


def _ema(values: Sequence[Decimal], window: int) -> list[Decimal]:
    """Return the EMA series, seeded with the average of the first window."""

    multiplier = Decimal(2) / Decimal(window + 1)
    current = sum(values[:window], start=Decimal(0)) / Decimal(window)
    series = [current]
    for value in values[window:]:
        current = (value - current) * multiplier + current
        series.append(current)
    return series


def macd_series(
    closes: Sequence[Decimal],
    fast_window: int = FAST_WINDOW,
    slow_window: int = SLOW_WINDOW,
) -> list[Decimal]:
    """Return MACD values, one per close that both EMAs cover."""

    fast = _ema(closes, fast_window)
    slow = _ema(closes, slow_window)
    aligned = fast[len(fast) - len(slow) :]
    return [f - s for f, s in zip(aligned, slow, strict=True)]


def evaluate(
    closes: Sequence[Decimal],
    in_position: bool = False,
    fast_window: int = FAST_WINDOW,
    slow_window: int = SLOW_WINDOW,
    signal_window: int = SIGNAL_WINDOW,
) -> Evaluation:
    """Return current MACD values and an entry/exit signal.

    Entry is the MACD line crossing zero upwards while flat. Exit is two
    consecutive declining MACD values while holding a position. The signal line
    and histogram are reported for context; neither rule reads them.
    """

    if fast_window <= 0 or slow_window <= fast_window:
        raise ValueError("windows must satisfy 0 < fast_window < slow_window")
    if signal_window <= 0:
        raise ValueError("signal_window must be positive")
    minimum = required_closes(slow_window, signal_window)
    if len(closes) < minimum:
        raise ValueError(f"at least {minimum} closes are required")

    macd = macd_series(closes, fast_window, slow_window)
    signal_line = _ema(macd, signal_window)[-1]
    older, previous, current = macd[-3], macd[-2], macd[-1]

    signal: Signal = None
    if in_position:
        if current < previous < older:
            signal = "exit"
    elif previous <= 0 < current:
        signal = "entry"

    return Evaluation(current, signal_line, current - signal_line, signal)
