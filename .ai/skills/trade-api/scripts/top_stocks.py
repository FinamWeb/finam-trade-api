#!/usr/bin/env python3
"""List top RU/US stocks from index constituents (IMOEX or NDX)."""

import argparse
import json
import os
import sys

from finam_trade_api import FinamClient
from finam_trade_api.assets import GetConstituentsRequest


INDEX_MAP = {"ru": "IMOEX@RTSX", "us": "NDX@_SCI"}


def make_client() -> FinamClient:
    api_key = os.environ.get("FINAM_API_KEY")
    if not api_key:
        print("Error: FINAM_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return FinamClient(secret=api_key)


def fetch_constituents(client, index_symbol):
    results = []
    cursor = 0
    while True:
        req = GetConstituentsRequest(symbol=index_symbol, cursor=cursor)
        resp = client.assets.GetConstituents(req)
        results.extend(resp.constituents)
        cursor = resp.next_cursor
        if not cursor:
            break
    return [{"symbol": c.symbol, "name": c.name} for c in results]


def main():
    parser = argparse.ArgumentParser(description="List top RU/US stocks (IMOEX or NDX constituents).")
    parser.add_argument("market", nargs="?", default="ru", choices=("ru", "us"))
    parser.add_argument("--n", type=int, default=None, metavar="N", help="limit output to first N entries")
    parser.add_argument("--json", action="store_true", help="output raw JSON instead of table")
    args = parser.parse_args()

    with make_client() as client:
        constituents = fetch_constituents(client, INDEX_MAP[args.market])

    if args.n:
        constituents = constituents[: args.n]

    if args.json:
        print(json.dumps(constituents, ensure_ascii=False, indent=2))
        return

    market_label = "RU (IMOEX)" if args.market == "ru" else "US (NDX)"
    print(f"\nTop {len(constituents)} {market_label} stocks:\n")
    header = f"{'#':<5}{'Symbol':<16}{'Name'}"
    print(header)
    print("─" * 50)
    for i, c in enumerate(constituents, 1):
        print(f"{i:<5}{c['symbol']:<16}{c['name']}")


if __name__ == "__main__":
    main()