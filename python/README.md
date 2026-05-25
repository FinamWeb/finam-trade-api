# Finam Trade API — Python SDK

Thin Python SDK for the [Finam Trade API](https://tradeapi.finam.ru/). Wraps
the generated gRPC stubs with:

- a single `FinamClient` / `AsyncFinamClient` entry point,
- automatic JWT issuance and background refresh (via `AuthService.SubscribeJwtRenewal`),
- typed exceptions mapped from gRPC status codes,
- exponential-backoff retries on transient failures (`UNAVAILABLE`, `RESOURCE_EXHAUSTED`).

Service methods are invoked directly on the generated stubs, so the full proto
surface is available without an extra translation layer.

## Installation

```sh
pip install finam-trade-api
```

> Until the package is published, install from source — see *Local build* below.

## Quickstart (sync)

```python
from finam_trade_api import FinamClient
from finam_trade_api.proto.grpc.tradeapi.v1.accounts.accounts_service_pb2 import (
    GetAccountRequest,
)
from finam_trade_api.proto.grpc.tradeapi.v1.marketdata.marketdata_service_pb2 import (
    SubscribeQuoteRequest,
)

with FinamClient(secret="YOUR_API_TOKEN") as client:
    account = client.accounts.GetAccount(GetAccountRequest(account_id="A12345"))
    print(account)

    # Streaming RPCs return iterators.
    for tick in client.market_data.SubscribeQuote(
        SubscribeQuoteRequest(symbols=["SBER@MISX"])
    ):
        print(tick)
```

## Quickstart (asyncio)

```python
import asyncio

from finam_trade_api import AsyncFinamClient
from finam_trade_api.proto.grpc.tradeapi.v1.marketdata.marketdata_service_pb2 import (
    SubscribeQuoteRequest,
)


async def main() -> None:
    async with AsyncFinamClient(secret="YOUR_API_TOKEN") as client:
        async for tick in client.market_data.SubscribeQuote(
            SubscribeQuoteRequest(symbols=["SBER@MISX"])
        ):
            print(tick)


asyncio.run(main())
```

## Available services

The client exposes the full Trade API surface via sub-clients:

| Attribute            | gRPC service           | What it does                                  |
| -------------------- | ---------------------- | --------------------------------------------- |
| `client.auth`        | `AuthService`          | Token issuance + details (usually automatic). |
| `client.accounts`    | `AccountsService`      | Accounts, positions, trades, transactions.    |
| `client.assets`      | `AssetsService`        | Instruments, exchanges, schedules, options.   |
| `client.market_data` | `MarketDataService`    | Bars, quotes, order book, trade streams.      |
| `client.orders`      | `OrdersService`        | Place / cancel orders, order + trade streams. |
| `client.reports`     | `ReportsService`       | Account reports.                              |
| `client.metrics`     | `UsageMetricsService`  | API usage / quota metrics.                    |

## API reference

Every RPC defined in the `.proto` files is exposed directly on the sub-client.
Request and response message types live under
`finam_trade_api.proto.grpc.tradeapi.v1.<service>.<service>_service_pb2`.

Legend: ▶ unary · ⇉ server-stream · ⇄ bidi-stream

### `client.auth` — `AuthService`

| Method | Kind | Purpose |
| --- | :---: | --- |
| `Auth(AuthRequest)` | ▶ | Exchange API secret for a JWT. *Called for you on construction.* |
| `TokenDetails(TokenDetailsRequest)` | ▶ | Inspect a JWT — expiry, market-data permissions, visible account IDs. |
| `SubscribeJwtRenewal(SubscribeJwtRenewalRequest)` | ⇉ | Stream of refreshed JWTs. *Consumed for you in the background.* |

### `client.accounts` — `AccountsService`

| Method | Kind | Purpose |
| --- | :---: | --- |
| `GetAccount(GetAccountRequest)` | ▶ | Account info: equity, cash, positions, margin. |
| `Trades(TradesRequest)` | ▶ | Historical trades for an account. |
| `Transactions(TransactionsRequest)` | ▶ | Cash movements and other non-trade transactions. |
| `SubscribeAccount(GetAccountRequest)` | ⇉ | Streaming account updates. |

### `client.assets` — `AssetsService`

| Method | Kind | Purpose |
| --- | :---: | --- |
| `Exchanges(ExchangesRequest)` | ▶ | List of supported exchanges. |
| `Assets(AssetsRequest)` | ▶ | Tradable instruments (filtered). |
| `AllAssets(AllAssetsRequest)` | ▶ | Full instrument catalog. |
| `GetAsset(GetAssetRequest)` | ▶ | Single instrument by symbol. |
| `GetAssetParams(GetAssetParamsRequest)` | ▶ | Trading parameters for an instrument. |
| `OptionsChain(OptionsChainRequest)` | ▶ | Options chain for an underlying. |
| `Schedule(ScheduleRequest)` | ▶ | Trading session schedule. |
| `Clock(ClockRequest)` | ▶ | Server clock (use for time-aligned operations). |
| `GetConstituents(GetConstituentsRequest)` | ▶ | Index constituents. |

### `client.market_data` — `MarketDataService`

| Method | Kind | Purpose |
| --- | :---: | --- |
| `Bars(BarsRequest)` | ▶ | OHLC candles (any timeframe via `TimeFrame` enum). |
| `LastQuote(QuoteRequest)` | ▶ | Most recent quote snapshot. |
| `OrderBook(OrderBookRequest)` | ▶ | Order book snapshot. |
| `LatestTrades(LatestTradesRequest)` | ▶ | Most recent trades for a symbol. |
| `SubscribeQuote(SubscribeQuoteRequest)` | ⇉ | Live quote stream. |
| `SubscribeOrderBook(SubscribeOrderBookRequest)` | ⇉ | Live order-book updates. |
| `SubscribeLatestTrades(SubscribeLatestTradesRequest)` | ⇉ | Live trades stream. |
| `SubscribeBars(SubscribeBarsRequest)` | ⇉ | Live candle stream. |

### `client.orders` — `OrdersService`

| Method | Kind | Purpose |
| --- | :---: | --- |
| `PlaceOrder(Order)` | ▶ | Place market / limit / stop / stop-limit / multi-leg order. |
| `PlaceSLTPOrder(SLTPOrder)` | ▶ | Place an SL/TP (stop-loss + take-profit) order. |
| `CancelOrder(CancelOrderRequest)` | ▶ | Cancel an active order. |
| `GetOrders(OrdersRequest)` | ▶ | List active orders for an account. |
| `GetOrder(GetOrderRequest)` | ▶ | Single order by ID. |
| `SubscribeOrders(SubscribeOrdersRequest)` | ⇉ | Live order-state updates. |
| `SubscribeTrades(SubscribeTradesRequest)` | ⇉ | Live execution / fill stream. |
| `SubscribeOrderTrade(stream OrderTradeRequest)` | ⇄ | Bidi stream — order + trade events, request-driven. |

### `client.reports` — `ReportsService`

| Method | Kind | Purpose |
| --- | :---: | --- |
| `CreateAccountReport(CreateAccountReportRequest)` | ▶ | Generate an account report (async — returns a job handle). |
| `GetAccountReportInfo(GetAccountReportInfoRequest)` | ▶ | Poll report status. |
| `SubscribeAccountReportInfo(SubscribeAccountReportInfoRequest)` | ⇉ | Stream report status updates instead of polling. |

### `client.metrics` — `UsageMetricsService`

| Method | Kind | Purpose |
| --- | :---: | --- |
| `GetUsageMetrics(GetUsageMetricsRequest)` | ▶ | API usage / quota stats for the current token. |

### Client lifecycle

| Operation | Sync | Async |
| --- | --- | --- |
| Construct | `FinamClient(secret, *, endpoint=DEFAULT_ENDPOINT, retry_policy=DEFAULT_POLICY, channel_options=None, insecure=False)` | `AsyncFinamClient(secret, ...)` — same args |
| Start | *immediate, blocks for initial JWT* | `await client.start()` — or use `async with` |
| Current JWT | `client.token` | `await client.token` |
| Close | `client.close()` | `await client.close()` |
| Context manager | `with FinamClient(...) as client:` | `async with AsyncFinamClient(...) as client:` |

> `insecure=True` is for local testing against an in-process fake server only — it disables TLS and routes the Authorization header through a plaintext interceptor. **Never use against `api.finam.ru`.**

## Error handling

Wrap raw `grpc.RpcError` into a typed `FinamError`:

```python
import grpc
from finam_trade_api import FinamClient, RateLimitError, from_rpc_error

with FinamClient(secret="...") as client:
    try:
        client.accounts.GetAccount(GetAccountRequest(account_id="A12345"))
    except grpc.RpcError as raw:
        err = from_rpc_error(raw)
        if isinstance(err, RateLimitError):
            ...
        raise err
```

Exception classes: `AuthError` (401), `PermissionDeniedError` (403),
`InvalidArgumentError` (400), `NotFoundError` (404), `RateLimitError` (429),
`InternalError` (500), `ServiceUnavailableError` (503), `DeadlineExceededError` (504).
All inherit from `FinamError`.

## Retries

Unary RPCs are retried automatically on `UNAVAILABLE` and `RESOURCE_EXHAUSTED`
with exponential backoff + jitter. Streaming RPCs are *not* retried — the
caller is expected to handle reconnection at a meaningful boundary
(e.g. resuming from the last received bar).

Override the policy:

```python
from finam_trade_api import FinamClient, RetryPolicy

policy = RetryPolicy(max_attempts=6, initial_backoff=0.5, max_backoff=10.0)
client = FinamClient(secret="...", retry_policy=policy)
```

## Local build

From the repository root:

```sh
cd python
pip install -e ".[dev]"
./scripts/generate_proto.sh
```

`scripts/generate_proto.sh` compiles the `.proto` files in `../proto/` into
`finam_trade_api/proto/`. Re-run it whenever the protos change.

## Layout

```
python/
├── pyproject.toml
├── README.md
├── scripts/
│   └── generate_proto.sh      # protoc invocation
├── examples/                   # runnable scripts
└── finam_trade_api/
    ├── __init__.py
    ├── client.py               # FinamClient (sync)
    ├── aio.py                  # AsyncFinamClient
    ├── auth.py                 # JWT lifecycle
    ├── retry.py                # retry policy + interceptors
    ├── exceptions.py           # typed errors
    ├── _metadata.py            # Authorization header plumbing
    └── proto/                  # generated stubs (not in git)
```
