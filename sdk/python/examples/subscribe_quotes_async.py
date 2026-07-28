"""Subscribe to live quotes using the asyncio client.

Usage:
    FINAM_SECRET=... python examples/subscribe_quotes_async.py SBER@MISX GAZP@MISX
"""

from __future__ import annotations

import asyncio
import os
import sys

from finam_trade_api import AsyncFinamClient
from finam_trade_api.market_data import SubscribeQuoteRequest


async def main(symbols: list[str]) -> None:
    secret = os.environ["FINAM_SECRET"]
    async with AsyncFinamClient(secret=secret) as client:
        async for tick in client.market_data.SubscribeQuote(
            SubscribeQuoteRequest(symbols=symbols)
        ):
            # flush=True so the stream is visible under `timeout`, `tee`,
            # or any other pipeline that truncates buffered stdout on exit.
            print(tick, flush=True)


if __name__ == "__main__":
    syms = sys.argv[1:] or ["SBER@MISX"]
    asyncio.run(main(syms))
