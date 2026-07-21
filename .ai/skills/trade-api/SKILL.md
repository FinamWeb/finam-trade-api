---
name: trade-api
description: "Use this skill for any work with Finam / Финам broker and Trade API: questions about the API, developing algorithmic trading strategies and scripts, and interacting with the broker programmatically. Trigger on: Finam/Финам mentions, api.finam.ru URLs, ticker@mic symbol format, finam-sdk. Also trigger for Russian-market trading workflows even without explicit Finam mention — portfolio analysis, scanning Moscow Exchange stocks (MISX/RTSX), volatility/momentum/arbitrage strategies, order placement and cancellation, real-time quotes via gRPC or WebSocket, OHLCV candles, backtesting on Russian equities, risk management for algo trading."
metadata: '{"openclaw": {"emoji": "📈", "homepage": "https://api.finam.ru/", "requires": {"bins": ["curl", "jq", "python3"], "env": ["FINAM_API_KEY", "FINAM_ACCOUNT_ID"]}}}'
---

# Finam Trade API Skill

## Setup

To execute Trade API requests, configure two credentials:

- `FINAM_API_KEY` — API token. Get it at [api.finam.ru/docs/tokens](https://api.finam.ru/docs/tokens)
- `FINAM_ACCOUNT_ID` — your account number from [lk.finam.ru](https://lk.finam.ru/). Digits only, without the `КлФ-` prefix.

You can use this skill without them — to design strategies, explore docs, or write scripts.

**Before sending any request, run this check via Bash tool:**

```shell
[ ${#FINAM_API_KEY} -gt 0 ] && echo "✅ FINAM_API_KEY is set" || echo "❌ FINAM_API_KEY is not set"
echo "FINAM_ACCOUNT_ID=${FINAM_ACCOUNT_ID:-❌ not set}"
```

If either is missing — stop and ask the user to configure credentials using one of the options below.

If missing, set them in any of these ways:

**Option 1 — export directly:**
```shell
export FINAM_API_KEY="your_token"
export FINAM_ACCOUNT_ID="your_account_number"
```

**Option 2 — `.env` file** (create it, fill in values, then load):
```
FINAM_API_KEY=your_token_here
FINAM_ACCOUNT_ID=your_account_number_here
```
Linux/macOS: `source .env` · Windows PowerShell:
```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]*)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}
```

**Option 3 — Claude Code** (`.claude/settings.local.json`):
```json
{ "env": { "FINAM_API_KEY": "...", "FINAM_ACCOUNT_ID": "..." } }
```

Using the API Key, obtain a **JWT token** — it expires after 15 minutes and does not persist between shell calls. Always fetch it inline before each request:

```shell
TOKEN=$(curl -sL "https://api.finam.ru/v1/sessions" \
  --header "Content-Type: application/json" \
  --data '{"secret": "'"$FINAM_API_KEY"'"}' | jq -r '.token') && \
curl -sL "https://api.finam.ru/v1/..." --header "Authorization: $TOKEN" | jq
```

**Demo account:** Can be opened at the [tokens page](https://tradeapi.finam.ru/docs/tokens). Valid for 2 weeks; works identically to a real account.

**Rate limits:** 200 requests/min per method.

**Maintenance window:** 05:00–06:15 MSK daily — API may be unavailable.

## Market assets

### List Available Exchanges

**Symbol Format:** All symbols must be in `ticker@mic` format (e.g., `SBER@MISX`)

**Base MIC Codes:**
- `MISX` - Moscow Exchange (all markets)
- `RTSX` - Moscow Exchange, Derivatives Market (futures & options)
- `XNYS` - New York Stock Exchange
- `ARCX` - NYSE Arca (ETFs)
- `XNGS` - NASDAQ/NGS (Global Select Market)
- `XNMS` - NASDAQ/NNS (Global Market)
- `XNCM` - NASDAQ Capital Market

View all supported exchanges with their MIC codes:

```shell
TOKEN=$(curl -sL "https://api.finam.ru/v1/sessions" \
  --header "Content-Type: application/json" \
  --data '{"secret": "'"$FINAM_API_KEY"'"}' | jq -r '.token')
curl -sL "https://api.finam.ru/v1/exchanges" --header "Authorization: $TOKEN" | \
  jq -r '.exchanges[] | "\(.mic) - \(.name)"'
```

### Get Asset Specification

Fetch detailed specification for a specific instrument (lot size, price step, decimals, trading schedule, etc.):

```shell
SYMBOL="SBER@MISX"
curl -sL "https://api.finam.ru/v1/assets/$SYMBOL?account_id=$FINAM_ACCOUNT_ID" \
  --header "Authorization: $TOKEN" | jq
```

`account_id` is optional but recommended — returns account-specific fields (margin, available quantity, etc.).

### Search Assets

Search instruments by ticker glob pattern and/or name substring:

```shell
# By ticker glob
python3 scripts/asset_search.py 'SBER*'

# By name (case-insensitive substring)
python3 scripts/asset_search.py --name 'apple'

# By ticker glob + type + exchange filter
python3 scripts/asset_search.py 'NG*' --type FUTURES --mic RTSX

# Search expired/archived instruments (e.g. expired futures contracts)
python3 scripts/asset_search.py 'NGF6' --type FUTURES --mic RTSX --archived

# By name + exchange + archived
python3 scripts/asset_search.py --name 'NG-' --type FUTURES --mic RTSX --archived
```

Available types: `EQUITIES`, `FUTURES`, `BONDS`, `FUNDS`, `SPREADS`, `OTHER`, `CURRENCIES`, `OPTIONS`, `SWAPS`, `INDICES`

`--mic MIC` filters by exchange (e.g. `RTSX`, `MISX`). `--archived` fetches expired/delisted instruments via `GET /v1/assets/all?only_disabled=true`. `--max=N` sets the pagination cap (default: 200 000).

### Get Top Stocks

Fetch current index components — IMOEX for RU market, NDX for US market:

```shell
# Table output (default)
python3 scripts/top_stocks.py ru
python3 scripts/top_stocks.py us

# First N entries
python3 scripts/top_stocks.py ru --n 10

# JSON output (for piping to other tools)
python3 scripts/top_stocks.py ru --json
```

## Account Management

### Get Account Portfolio

Retrieve portfolio information including positions, balances, and P&L:

```shell
curl -sL "https://api.finam.ru/v1/accounts/$FINAM_ACCOUNT_ID" \
  --header "Authorization: $TOKEN" | jq
```

## Market Data

### Get Latest Quote

Retrieve current bid/ask prices and last trade:

```shell
SYMBOL="SBER@MISX"
curl -sL "https://api.finam.ru/v1/instruments/$SYMBOL/quotes/latest" \
  --header "Authorization: $TOKEN" | jq
```

### Get Order Book (Depth)

View current market depth with bid/ask levels:

```shell
SYMBOL="SBER@MISX"
curl -sL "https://api.finam.ru/v1/instruments/$SYMBOL/orderbook" \
  --header "Authorization: $TOKEN" | jq
```

### Get Recent Trades

List the most recent executed trades:

```shell
SYMBOL="SBER@MISX"
curl -sL "https://api.finam.ru/v1/instruments/$SYMBOL/trades/latest" \
  --header "Authorization: $TOKEN" | jq
```

### Get Historical Candles (OHLCV)

Retrieve historical price data with specified timeframe:

```shell
SYMBOL="SBER@MISX"
TIMEFRAME="TIME_FRAME_D"
START_TIME="2024-01-01T00:00:00Z"
END_TIME="2024-04-01T00:00:00Z"
curl -sL "https://api.finam.ru/v1/instruments/$SYMBOL/bars?timeframe=$TIMEFRAME&interval.start_time=$START_TIME&interval.end_time=$END_TIME" \
  --header "Authorization: $TOKEN" | jq
```

**Available Timeframes:**

| Timeframe | Description | Max data depth (end_time - start_time) |
|---|---|---|
| `TIME_FRAME_UNSPECIFIED` | Not specified | — |
| `TIME_FRAME_M1` | 1 minute | 7 days |
| `TIME_FRAME_M5` | 5 minutes | 30 days |
| `TIME_FRAME_M15` | 15 minutes | 30 days |
| `TIME_FRAME_M30` | 30 minutes | 30 days |
| `TIME_FRAME_H1` | 1 hour | 30 days |
| `TIME_FRAME_H2` | 2 hours | 30 days |
| `TIME_FRAME_H4` | 4 hours | 30 days |
| `TIME_FRAME_H8` | 8 hours | 30 days |
| `TIME_FRAME_D` | Day | 365 days |
| `TIME_FRAME_W` | Week | ~5 years |
| `TIME_FRAME_MN` | Month | ~5 years |
| `TIME_FRAME_QR` | Quarter | ~5 years |

> **Note:** The max data depth is the maximum allowed range for `end_time - start_time`. If the range exceeds the limit, the API returns empty data.

**Date Format (RFC 3339):**

- Format: `YYYY-MM-DDTHH:MM:SSZ` or `YYYY-MM-DDTHH:MM:SS+HH:MM`
- `start_time` - Inclusive (interval start, included in results)
- `end_time` - Exclusive (interval end, NOT included in results)
- Examples:
    - `2024-01-15T10:30:00Z` (UTC)
    - `2024-01-15T10:30:00+03:00` (Moscow time, UTC+3)

## News

### Get Latest Market News

Fetch and display the latest news headlines via Finam. No JWT token required.

Russian market news

```shell
curl -sL "https://www.finam.ru/analysis/conews/rsspoint/" | python3 -c "
import sys, xml.etree.ElementTree as ET
root = ET.parse(sys.stdin).getroot()
for item in reversed(root.findall('.//item')):
    t=item.findtext('title',''); d=item.findtext('description','').split('...')[0]
    print(f'* {t}. {d}')
"
```

US market news

```shell
curl -sL "https://www.finam.ru/international/advanced/rsspoint/" | python3 -c "
import sys, xml.etree.ElementTree as ET
root = ET.parse(sys.stdin).getroot()
for item in reversed(root.findall('.//item')):
    t=item.findtext('title',''); d=item.findtext('description','').split('...')[0]
    print(f'* {t}. {d}')
"
```

## Order Management

> **IMPORTANT:** Before placing or cancelling any order, you MUST explicitly confirm the details with the user and
> receive their approval. State the full order parameters (symbol, side, quantity, type, price) and wait for confirmation
> before executing.

### Place Order

**Order Types:**

- `ORDER_TYPE_MARKET` - Market order (executes immediately, no `limit_price` required)
- `ORDER_TYPE_LIMIT` - Limit order (requires `limit_price`)

```shell
curl -sL "https://api.finam.ru/v1/accounts/$FINAM_ACCOUNT_ID/orders" \
  --header "Authorization: $TOKEN" \
  --header "Content-Type: application/json" \
  --data "$(jq -n \
    --arg symbol   "SBER@MISX" \
    --arg quantity "10" \
    --arg side     "SIDE_BUY" \
    --arg type     "ORDER_TYPE_LIMIT" \
    --arg price    "310.50" \
    '{symbol: $symbol, quantity: {value: $quantity}, side: $side, type: $type, limit_price: {value: $price}}')" \
  | jq
```

**Parameters:**

- `symbol` - Instrument (e.g., `SBER@MISX`)
- `quantity.value` - Number of shares/contracts
- `side` - `SIDE_BUY` or `SIDE_SELL`
- `type` - `ORDER_TYPE_MARKET` or `ORDER_TYPE_LIMIT`
- `limit_price` - Only for `ORDER_TYPE_LIMIT` (omit for market orders)

### Get Order Status

Check the status of a specific order:

```shell
ORDER_ID="12345678"
curl -sL "https://api.finam.ru/v1/accounts/$FINAM_ACCOUNT_ID/orders/$ORDER_ID" \
  --header "Authorization: $TOKEN" | jq
```

### Cancel Order

Cancel a pending order:

```shell
ORDER_ID="12345678"
curl -sL --request DELETE "https://api.finam.ru/v1/accounts/$FINAM_ACCOUNT_ID/orders/$ORDER_ID" \
  --header "Authorization: $TOKEN" | jq
```

## Building Strategies

### Pattern: scan → signal → execute

Every algo strategy follows the same loop:
1. **Scan** — fetch market data for a universe of instruments (candles, quotes, scanner)
2. **Signal** — compute metrics (growth, volatility, momentum) and decide action per symbol
3. **Execute** — place or cancel orders based on signals; confirm with user before executing

For one-off runs use `FinamClient` (sync). For continuous bots, use `AsyncFinamClient` with a reconnection loop (see Python SDK section).

### Momentum strategy

Buy if the stock grew over the last N days, sell otherwise:

```python
import os
from datetime import datetime, timedelta, timezone
from google.type.decimal_pb2 import Decimal
from finam_trade_api import FinamClient
from finam_trade_api.market_data import BarsRequest, TimeFrame
from finam_trade_api.orders import Order, OrderType, Side, TimeInForce

SYMBOLS = ["SBER@MISX", "GAZP@MISX", "LKOH@MISX"]
LOOKBACK_DAYS = 30
QUANTITY = "1"

def get_growth(client, symbol, days):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    req = BarsRequest(symbol=symbol, timeframe=TimeFrame.TIME_FRAME_D)
    req.interval.start_time.FromDatetime(start)
    req.interval.end_time.FromDatetime(end)
    bars = list(client.market_data.Bars(req).bars)
    if len(bars) < 2:
        return None
    first, last = float(bars[0].close.value), float(bars[-1].close.value)
    return (last - first) / first * 100

account_id = os.environ["FINAM_ACCOUNT_ID"]

with FinamClient(secret=os.environ["FINAM_API_KEY"]) as client:
    for symbol in SYMBOLS:
        growth = get_growth(client, symbol, LOOKBACK_DAYS)
        if growth is None:
            print(f"{symbol}: not enough data, skipping")
            continue

        side = Side.SIDE_BUY if growth > 0 else Side.SIDE_SELL
        print(f"{symbol}: growth={growth:+.1f}% → {'BUY' if side == Side.SIDE_BUY else 'SELL'}")

        # IMPORTANT: confirm with user before uncommenting
        # state = client.orders.PlaceOrder(Order(
        #     account_id=account_id,
        #     symbol=symbol,
        #     quantity=Decimal(value=QUANTITY),
        #     side=side,
        #     type=OrderType.ORDER_TYPE_MARKET,
        #     time_in_force=TimeInForce.TIME_IN_FORCE_DAY,
        # ))
        # print(f"  Order placed: {state.order_id}")
```

### Backtesting

To backtest a strategy on historical data, shift the `start`/`end` window in `BarsRequest` to a past period and replay your signal logic bar by bar. No external framework needed:

```python
# Simulate momentum over 2024
backtest_end = datetime(2025, 1, 1, tzinfo=timezone.utc)
backtest_start = datetime(2024, 1, 1, tzinfo=timezone.utc)

req = BarsRequest(symbol="SBER@MISX", timeframe=TimeFrame.TIME_FRAME_D)
req.interval.start_time.FromDatetime(backtest_start)
req.interval.end_time.FromDatetime(backtest_end)
bars = list(client.market_data.Bars(req).bars)

# Walk forward: at each bar, compute signal on the preceding window
window = 30
for i in range(window, len(bars)):
    segment = bars[i - window:i]
    first = float(segment[0].close.value)
    last = float(segment[-1].close.value)
    signal = "BUY" if last > first else "SELL"
    print(f"{bars[i].time.ToDatetime():%Y-%m-%d}  {signal}  close={last}")
```

> Max historical depth per request depends on timeframe (e.g. `TIME_FRAME_D` → 365 days). For longer periods, paginate by shifting the window.

## Market Scanner

Scans top-100 stocks for volatility, growth, and volume. Supports filtering and sorting by any metric.

**Usage:**

```shell
python3 scripts/scanner.py [ru|us] [N] [--sort volatility|growth|volume] [--days N] [--min-growth PCT] [--min-volume VAL]
```

**Examples:**

```shell
# Top 10 most volatile Russian stocks (last 60 days)
python3 scripts/scanner.py ru 10

# Stocks up >5% this week with avg daily volume >500M rubles
python3 scripts/scanner.py ru --days 5 --sort growth --min-growth 5 --min-volume 500000000

# Top 5 most volatile US stocks
python3 scripts/scanner.py us 5
```

All scripts support `--help` for usage details (e.g. `python3 scripts/scanner.py --help`).

## API Protocols

### REST

Endpoint: `https://api.finam.ru/v1` (HTTP/2 required — HTTP/1 causes method errors)

Use for one-off requests: historical OHLCV data, account info, positions, balances, trade history, instrument search, placing or cancelling orders where 100–200 ms latency is acceptable.

### gRPC

Endpoint: `api.finam.ru:443`

Use for low-latency and streaming scenarios: real-time quotes, order book, trade feed, live bar data for signal generation, monitoring own orders/trades via subscription, long-running trading bots with persistent auto-reconnecting connections.

**Note:** Streams disconnect once per day (~86400s from subscription start) — implement reconnection logic in long-running bots.

### WebSocket / AsyncAPI

Endpoints: `api.finam.ru/ws` or `api.finam.ru/tradinginfo`

Use when you need a browser-compatible or firewall-friendly alternative to gRPC for real-time data: streaming quotes, order book updates, and trade events over a standard WebSocket connection.

## Fetching API Documentation

**Always fetch live docs** — never rely on local cached copies. Use the `WebFetch` tool to load documentation on demand.

### Algorithm

1. **Fetch the index** for the relevant protocol to discover available docs:

   | Protocol | Index URL |
   | --- | --- |
   | REST | `https://api.finam.ru/docs/rest/llms.txt` |
   | gRPC | `https://api.finam.ru/docs/grpc/llms.txt` |
   | WebSocket / AsyncAPI | `https://api.finam.ru/docs/async-api/llms.txt` |

2. **Fetch the specific endpoint doc** linked from the index. URL patterns:
   - REST: `https://api.finam.ru/docs/rest/<servicename_methodname>.md` (e.g. `ordersservice_placeorder.md`)
   - gRPC: `https://api.finam.ru/docs/grpc/<methodname>.md` (e.g. `placeorder.md`)
   - AsyncAPI: `https://api.finam.ru/docs/async-api/<topicname>.md`

Fetch only the docs you actually need for the current task.

## Python SDK

Use the Finam SDK (`pip install finam-sdk`) for any Python scripts that interact with the API — both for one-off queries and streaming/trading bots. It handles JWT issuance and refresh automatically, provides typed exceptions, and exposes the full gRPC surface via a single `FinamClient` / `AsyncFinamClient` entry point.

Full reference: fetch live from `https://raw.githubusercontent.com/FinamWeb/finam-trade-api/main/python/README.md` (source: https://github.com/FinamWeb/finam-trade-api/tree/main/python)

### Authenticate and fetch account info

```python
import os
from finam_trade_api import FinamClient
from finam_trade_api.accounts import GetAccountRequest

with FinamClient(secret=os.environ["FINAM_API_KEY"]) as client:
    account = client.accounts.GetAccount(
        GetAccountRequest(account_id=os.environ["FINAM_ACCOUNT_ID"])
    )
    print(account)
```

### Place a limit order and cancel it

```python
import os
from google.type.decimal_pb2 import Decimal
from finam_trade_api import FinamClient
from finam_trade_api.orders import (
    CancelOrderRequest, Order, OrderType, Side, TimeInForce,
)

with FinamClient(secret=os.environ["FINAM_API_KEY"]) as client:
    account_id = os.environ["FINAM_ACCOUNT_ID"]

    state = client.orders.PlaceOrder(Order(
        account_id=account_id,
        symbol="SBER@MISX",
        quantity=Decimal(value="1"),
        side=Side.SIDE_BUY,
        type=OrderType.ORDER_TYPE_LIMIT,
        time_in_force=TimeInForce.TIME_IN_FORCE_DAY,
        limit_price=Decimal(value="100.00"),  # far below market — won't fill
        client_order_id="example-001",
    ))
    print(f"Placed: {state.order_id} status={state.status}")

    cancelled = client.orders.CancelOrder(
        CancelOrderRequest(account_id=account_id, order_id=state.order_id)
    )
    print(f"Cancelled: {cancelled.order_id} status={cancelled.status}")
```

### Stream live quotes (async)

```python
import asyncio, os, sys
from finam_trade_api import AsyncFinamClient
from finam_trade_api.market_data import SubscribeQuoteRequest

async def main(symbols: list[str]) -> None:
    async with AsyncFinamClient(secret=os.environ["FINAM_API_KEY"]) as client:
        async for tick in client.market_data.SubscribeQuote(
            SubscribeQuoteRequest(symbols=symbols)
        ):
            print(tick, flush=True)

asyncio.run(main(sys.argv[1:] or ["SBER@MISX"]))
```

### Reconnection loop for long-running bots

Streams can disconnect for two reasons: the server closes them after ~86400 s, or the JWT token expires mid-stream (`UNAUTHENTICATED`). In both cases the client must be recreated — reusing the same `AsyncFinamClient` instance after `UNAUTHENTICATED` will fail again immediately. Create the client **inside** the loop:

```python
import asyncio, os, grpc
from finam_trade_api import AsyncFinamClient
from finam_trade_api.market_data import SubscribeQuoteRequest

async def stream_with_reconnect(symbols: list[str]) -> None:
    while True:
        try:
            async with AsyncFinamClient(secret=os.environ["FINAM_API_KEY"]) as client:
                async for tick in client.market_data.SubscribeQuote(
                    SubscribeQuoteRequest(symbols=symbols)
                ):
                    process(tick)
        except grpc.RpcError:
            await asyncio.sleep(5)  # brief pause before reconnect
```