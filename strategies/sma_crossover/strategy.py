"""The SMA 9/30 rule, independent from APIs and order execution."""

from decimal import Decimal
from typing import Literal, Optional, Sequence

Signal = Optional[Literal["entry", "exit"]]


def _mean(values: Sequence[Decimal]) -> Decimal:
    return sum(values, start=Decimal(0)) / Decimal(len(values))


def evaluate(
    closes: Sequence[Decimal],
    fast_window: int = 9,
    slow_window: int = 30,
) -> tuple[Decimal, Decimal, Signal]:
    """Return current SMA values and an entry/exit crossover signal.

    At least ``slow_window`` closes calculate the averages. One additional
    close is needed before a crossover can be detected against the previous
    candle.
    """

    if fast_window <= 0 or slow_window <= fast_window:
        raise ValueError("windows must satisfy 0 < fast_window < slow_window")
    if len(closes) < slow_window:
        raise ValueError(f"at least {slow_window} closes are required")

    fast = _mean(closes[-fast_window:])
    slow = _mean(closes[-slow_window:])
    if len(closes) == slow_window:
        return fast, slow, None

    previous = closes[:-1]
    previous_fast = _mean(previous[-fast_window:])
    previous_slow = _mean(previous[-slow_window:])

    if previous_fast <= previous_slow and fast > slow:
        return fast, slow, "entry"
    if previous_fast >= previous_slow and fast < slow:
        return fast, slow, "exit"
    return fast, slow, None
