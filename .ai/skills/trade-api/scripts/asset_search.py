#!/usr/bin/env python3
"""Search Finam instruments by ticker glob pattern or name substring."""

import argparse
import fnmatch
import os
import sys

from finam_trade_api import FinamClient
from finam_trade_api.assets import AssetsRequest, AllAssetsRequest


VALID_TYPES = {"EQUITIES", "FUTURES", "BONDS", "FUNDS", "SPREADS", "OTHER", "CURRENCIES", "OPTIONS", "SWAPS", "INDICES"}

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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Search Finam instruments by ticker glob pattern and/or name substring.",
        epilog=(
            "examples:\n"
            "  asset_search.py 'SBER*'\n"
            "  asset_search.py 'NG*' --type FUTURES --mic RTSX\n"
            "  asset_search.py 'NGF6' --type FUTURES --mic RTSX --archived\n"
            "  asset_search.py --name 'natural gas' --type FUTURES --mic RTSX --archived\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("pattern", nargs="?", help="glob pattern matched against ticker and symbol (e.g. SBER*, NG*@RTSX)")
    parser.add_argument("--name", metavar="QUERY", help="case-insensitive substring search on instrument name")
    parser.add_argument("--type", metavar="TYPE", choices=VALID_TYPES, type=str.upper, help=f"filter by type: {', '.join(sorted(VALID_TYPES))}")
    parser.add_argument("--mic", metavar="MIC", type=str.upper, help="filter by exchange MIC code (e.g. RTSX, MISX)")
    parser.add_argument("--archived", action="store_true", default=False, help="include expired/archived instruments (uses AllAssets endpoint)")
    parser.add_argument("--max", metavar="N", type=int, default=200_000, help="max assets to fetch when --archived is set (default: 200000)")
    parser.add_argument("--debug", action="store_true", help="verbose output")

    args = parser.parse_args()

    if args.pattern is None and args.name is None:
        parser.error("at least one of pattern or --name is required")

    global _debug
    _debug = args.debug

    return args.pattern, args.name.lower() if args.name else None, args.type, args.mic, args.archived, args.max


def fetch_assets(client):
    resp = client.assets.Assets(AssetsRequest())
    assets = list(resp.assets)
    dprint(f"  Fetched {len(assets)} assets")
    return assets


def fetch_assets_all(client, only_disabled, max_assets):
    assets = []
    cursor = 0
    while True:
        resp = client.assets.AllAssets(AllAssetsRequest(cursor=cursor, only_disabled=only_disabled))
        batch = list(resp.assets)
        assets.extend(batch)
        dprint(f"  Fetched {len(batch)} assets (total: {len(assets)})")

        if max_assets and len(assets) >= max_assets:
            assets = assets[:max_assets]
            break

        next_cursor = resp.next_cursor
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor

    return assets


def main():
    pattern, name_query, type_filter, mic_filter, include_archived, max_assets = parse_args()

    with make_client() as client:
        if include_archived:
            dprint(f"Fetching archived assets only (max={max_assets})...")
            assets = fetch_assets_all(client, only_disabled=True, max_assets=max_assets)
        else:
            dprint("Fetching active assets...")
            assets = fetch_assets(client)

    dprint(f"Total assets fetched: {len(assets)}")

    matches = []
    for a in assets:
        if type_filter and a.type.upper() != type_filter:
            continue
        if mic_filter and a.mic.upper() != mic_filter:
            continue
        ticker_ok = not pattern or fnmatch.fnmatch(a.ticker, pattern) or fnmatch.fnmatch(a.symbol, pattern)
        name_ok = not name_query or name_query in a.name.lower()
        if ticker_ok and name_ok:
            matches.append(a)

    parts = []
    if pattern:
        parts.append(f"'{pattern}'")
    if name_query:
        parts.append(f"name='{name_query}'")
    if type_filter:
        parts.append(f"type={type_filter}")
    if mic_filter:
        parts.append(f"mic={mic_filter}")
    filter_desc = " ".join(parts)

    if not matches:
        print(f"No instruments found matching {filter_desc}.")
        return

    print(f"\nFound {len(matches)} instrument(s) matching {filter_desc}:\n")
    header = f"{'Ticker':<16}{'Symbol':<20}{'MIC':<10}{'Type':<16}{'Name'}"
    print(header)
    print("─" * (len(header) + 20))
    for a in matches:
        archived = " [archived]" if a.is_archived else ""
        print(
            f"{a.ticker:<16}"
            f"{a.symbol:<20}"
            f"{a.mic:<10}"
            f"{a.type:<16}"
            f"{a.name}{archived}"
        )


if __name__ == "__main__":
    main()