#!/usr/bin/env python3
"""Market scanner for Finam top-100 stocks: volatility, growth, and volume."""

import argparse
import json
import math
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path

from finam_trade_api import FinamClient
from finam_trade_api.market_data import BarsRequest, TimeFrame


ASSETS_DIR = Path(__file__).parent.parent / "assets"

_debug = False


def dprint(*args, **kwargs):
    if _debug:
        print(*args, **kwargs)


def make_client() -> FinamClient:
    api_key = os.environ.get("FINAM_API_KEY")
    if not api_key:
        print("Error: FINAM_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return FinamClient(secret=api_key)


def load_equities(market):
    path = ASSETS_DIR / f"top_{market}_equities.json"
    with open(path) as f:
        return json.load(f)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scan top-100 stocks for volatility, growth, and volume.",
        epilog=(
            "examples:\n"
            "  volatility.py ru 10\n"
            "  volatility.py us 5 --sort growth --days 5\n"
            "  volatility.py ru --sort volume --min-growth 5 --min-volume 500000000\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("market", nargs="?", default="ru", choices=("ru", "us"), help="market to scan (default: ru)")
    parser.add_argument("n", nargs="?", default=10, type=int, metavar="N", help="number of top results to display (default: 10)")
    parser.add_argument("--sort", default="volatility", choices=("volatility", "growth", "volume"), help="metric to sort by (default: volatility)")
    parser.add_argument("--days", default=60, type=int, help="lookback period in days (default: 60)")
    parser.add_argument("--min-growth", default=None, type=float, metavar="PCT", help="filter: minimum growth %% over the period")
    parser.add_argument("--min-volume", default=None, type=float, metavar="VAL", help="filter: minimum average daily volume")
    parser.add_argument("--debug", action="store_true", help="verbose output")

    args = parser.parse_args()

    global _debug
    _debug = args.debug

    return args


def fetch_bars(client, symbol, days=60):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    req = BarsRequest(symbol=symbol, timeframe=TimeFrame.TIME_FRAME_D)
    req.interval.start_time.FromDatetime(start)
    req.interval.end_time.FromDatetime(end)

    try:
        resp = client.market_data.Bars(req)
        return list(resp.bars)
    except Exception as e:
        print(f"  Warning: error fetching {symbol}: {e}", file=sys.stderr)
        return []


def compute_volatility(bars):
    closes = [float(b.close.value) for b in bars]
    if len(closes) < 5:
        return None
    log_returns = [math.log(b / a) for a, b in zip(closes, closes[1:])]
    n = len(log_returns)
    mean = sum(log_returns) / n
    variance = sum((r - mean) ** 2 for r in log_returns) / (n - 1)
    return math.sqrt(variance * 252)


def compute_growth(bars):
    if len(bars) < 2:
        return None
    first = float(bars[0].close.value)
    last = float(bars[-1].close.value)
    if first == 0:
        return None
    return (last - first) / first * 100


def compute_avg_volume(bars):
    """Returns average daily volume in rubles (shares × close price)."""
    if not bars:
        return None
    volumes = [float(b.volume.value) * float(b.close.value) for b in bars if float(b.volume.value) > 0]
    if not volumes:
        return None
    return sum(volumes) / len(volumes)


def main():
    args = parse_args()
    market, n = args.market, args.n

    equities = load_equities(market)
    total = len(equities)
    dprint(f"Fetching bars for {total} {market.upper()} tickers (last {args.days} days)...")

    results = {}
    with make_client() as client:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(fetch_bars, client, eq["symbol"], args.days): eq
                for eq in equities
            }
            done = 0
            for future in as_completed(futures):
                eq = futures[future]
                bars = future.result()
                done += 1
                if not bars:
                    dprint(f"  [{done}/{total}] {eq['symbol']} — skipped (no data)")
                    continue
                vol = compute_volatility(bars)
                growth = compute_growth(bars)
                avg_vol = compute_avg_volume(bars)
                if vol is None:
                    dprint(f"  [{done}/{total}] {eq['symbol']} — skipped (only {len(bars)} bars)")
                    continue
                results[eq["symbol"]] = {"name": eq["name"], "vol": vol, "growth": growth, "avg_volume": avg_vol}
                dprint(f"  [{done}/{total}] {eq['symbol']} — vol={vol*100:.1f}% growth={growth:+.1f}% avg_vol={avg_vol:.0f}")

    if not results:
        print("No results to display.")
        return

    # apply filters
    if args.min_growth is not None:
        results = {s: v for s, v in results.items() if v["growth"] is not None and v["growth"] >= args.min_growth}
    if args.min_volume is not None:
        results = {s: v for s, v in results.items() if v["avg_volume"] is not None and v["avg_volume"] >= args.min_volume}

    if not results:
        print("No stocks match the filters.")
        return

    sort_key = {"volatility": "vol", "growth": "growth", "volume": "avg_volume"}[args.sort]
    sorted_results = sorted(results.items(), key=lambda x: x[1][sort_key] or 0, reverse=True)
    top = sorted_results[:n]

    market_label = "RU" if market == "ru" else "US"
    print(f"\nTop {n} {market_label} stocks by {args.sort} (last {args.days} days):\n")
    header = f"{'#':<5}{'Symbol':<18}{'Name':<35}{'Volatility':>12}{'Growth':>9}{'Avg Volume':>16}"
    print(header)
    print("─" * len(header))
    for i, (symbol, info) in enumerate(top, 1):
        growth_str = f"{info['growth']:+.1f}%" if info["growth"] is not None else "n/a"
        vol_str = f"{info['vol']*100:.1f}%"
        vol_num = f"{info['avg_volume']:,.0f}" if info["avg_volume"] is not None else "n/a"
        print(f"{i:<5}{symbol:<18}{info['name']:<35}{vol_str:>12}{growth_str:>9}{vol_num:>16}")


if __name__ == "__main__":
    main()