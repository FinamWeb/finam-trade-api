"""Command-line configuration for the RSI threshold example."""

from __future__ import annotations

import argparse
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from finam_trade_api.market_data import TimeFrame

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


@dataclass(frozen=True, slots=True)
class Config:
    secret: str
    symbol: str
    timeframe: str
    quantity: Decimal
    execute: bool
    check: bool
    log_level: str


def parse_config(
    argv: Sequence[str] | None = None,
    environ: Mapping[str, str] = os.environ,
) -> Config:
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="Run the RSI 14 threshold strategy",
    )
    parser.add_argument("--secret", default=environ.get("TRADE_API_SECRET"))
    parser.add_argument("--symbol", default=environ.get("TRADE_API_SYMBOL"))
    parser.add_argument(
        "--timeframe",
        choices=sorted(TIMEFRAMES),
        default=environ.get("TRADE_API_TIMEFRAME", "M5").upper(),
    )
    parser.add_argument("--quantity", default=environ.get("TRADE_API_QUANTITY", "1"))
    parser.add_argument("--execute", action="store_true", help="Place real market orders")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Calculate from historical bars and exit read-only",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=environ.get("TRADE_API_LOG_LEVEL", "INFO").upper(),
    )
    args = parser.parse_args(argv)

    if not args.secret:
        parser.error("--secret or TRADE_API_SECRET is required")
    if not args.symbol or "@" not in args.symbol:
        parser.error("--symbol must use ticker@mic format, for example SBER@MISX")
    if args.check and args.execute:
        parser.error("--check and --execute cannot be used together")

    try:
        quantity = Decimal(str(args.quantity))
    except InvalidOperation:
        parser.error("--quantity must be a decimal number")
    if not quantity.is_finite() or quantity <= 0:
        parser.error("--quantity must be positive")

    return Config(
        secret=str(args.secret),
        symbol=str(args.symbol),
        timeframe=str(args.timeframe),
        quantity=quantity,
        execute=bool(args.execute),
        check=bool(args.check),
        log_level=str(args.log_level),
    )
