"""The RSI threshold rule, independent from APIs and order execution."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from itertools import pairwise
from typing import Literal

PERIOD = 14
ENTRY_LEVEL = Decimal("0.2")
EXIT_LEVEL = Decimal("0.8")

# A flat market has no gains and no losses, which leaves the ratio undefined.
# The midpoint is the conventional reading and sits between both levels, so a
# gap in the data cannot by itself trigger a trade.
NEUTRAL = Decimal("0.5")

Signal = Literal["entry", "exit"] | None


@dataclass(frozen=True, slots=True)
class Evaluation:
    rsi: Decimal
    average_gain: Decimal
    average_loss: Decimal
    signal: Signal


def required_closes(period: int = PERIOD) -> int:
    """Closes needed for one RSI value.

    Wilder's averages cover ``period`` price changes, and the first change also
    needs the close before it.
    """

    return period + 1


# Closes kept while streaming. Ten periods make the seed irrelevant to the
# newest value, so a restart converges on the same RSI.
HISTORY_CLOSES = PERIOD * 10
MINIMUM_CLOSES = required_closes()


def _changes(closes: Sequence[Decimal]) -> tuple[list[Decimal], list[Decimal]]:
    """Split consecutive close-to-close changes into gains and losses.

    Both are reported as non-negative magnitudes, and an unchanged close
    contributes zero to each.
    """

    gains: list[Decimal] = []
    losses: list[Decimal] = []
    for previous, current in pairwise(closes):
        change = current - previous
        gains.append(max(change, Decimal(0)))
        losses.append(max(-change, Decimal(0)))
    return gains, losses


def wilder_averages(
    closes: Sequence[Decimal],
    period: int = PERIOD,
) -> tuple[Decimal, Decimal]:
    """Return Wilder's smoothed average gain and loss for the newest close.

    The averages are seeded with the simple mean of the first ``period``
    changes and then smoothed with weight ``1 / period``, which is Wilder's
    original formulation rather than a standard EMA.
    """

    gains, losses = _changes(closes)
    divisor = Decimal(period)
    average_gain = sum(gains[:period], start=Decimal(0)) / divisor
    average_loss = sum(losses[:period], start=Decimal(0)) / divisor
    for gain, loss in zip(gains[period:], losses[period:], strict=True):
        average_gain = (average_gain * (period - 1) + gain) / divisor
        average_loss = (average_loss * (period - 1) + loss) / divisor
    return average_gain, average_loss


def relative_strength_index(average_gain: Decimal, average_loss: Decimal) -> Decimal:
    """Return the RSI on a 0..1 scale; multiply by 100 for the 0..100 form.

    This is the usual ``100 - 100 / (1 + gain / loss)`` rearranged into
    ``gain / (gain + loss)``. The two agree everywhere, but this form needs no
    special case for a period without losses.
    """

    total = average_gain + average_loss
    return NEUTRAL if total == 0 else average_gain / total


def evaluate(
    closes: Sequence[Decimal],
    in_position: bool = False,
    period: int = PERIOD,
    entry_level: Decimal = ENTRY_LEVEL,
    exit_level: Decimal = EXIT_LEVEL,
) -> Evaluation:
    """Return the current RSI and an entry/exit signal.

    Entry is an RSI below ``entry_level`` while flat. Exit is an RSI above
    ``exit_level`` while holding a position. Both are levels rather than
    crossings, so the caller's position state is what stops a signal from
    repeating on every candle that stays beyond its level.
    """

    if period <= 0:
        raise ValueError("period must be positive")
    if not Decimal(0) <= entry_level < exit_level <= Decimal(1):
        raise ValueError("levels must satisfy 0 <= entry_level < exit_level <= 1")
    minimum = required_closes(period)
    if len(closes) < minimum:
        raise ValueError(f"at least {minimum} closes are required")

    average_gain, average_loss = wilder_averages(closes, period)
    rsi = relative_strength_index(average_gain, average_loss)

    signal: Signal = None
    if in_position:
        if rsi > exit_level:
            signal = "exit"
    elif rsi < entry_level:
        signal = "entry"

    return Evaluation(rsi, average_gain, average_loss, signal)
