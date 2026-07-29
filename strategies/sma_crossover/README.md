# SMA 9/30 crossover

A long-only moving-average crossover strategy, implemented once per language
against the corresponding published Trade API SDK.

| Language | Implementation | SDK |
| --- | --- | --- |
| Python | [`python/`](python/) | [`finam-sdk`](https://pypi.org/project/finam-sdk/) |

This page describes the strategy itself: the rule, how candles are handled, and
the safety guards every implementation must honor. Each language directory has
its own README covering only installation, running, and tests for that
ecosystem.

## The rule

- **Entry:** previous SMA 9 ≤ previous SMA 30, and current SMA 9 > current SMA 30.
- **Exit:** previous SMA 9 ≥ previous SMA 30, and current SMA 9 < current SMA 30.
- Averages use completed candle close prices.
- No signal is emitted while the 30-candle window is warming up.
- A signal is emitted once on the crossover candle, not on every candle while
  one average remains above the other.

Two adjacent SMA 30 values are needed to detect a crossover, so the rule needs
31 closes before it can emit its first signal.

## Data and execution flow

```text
market_data.Bars ───────┐
                        ├─> completed candles ─> SMA 9/30 ─> signal
market_data.SubscribeBars┘                                  │
                                                           ├─> dry-run log
accounts.GetAccount ────────────────────────────────────────┤
orders.PlaceOrder <─────────────────────────────────────────┘
```

Each SDK already provides all required operations. An implementation should not
import generated stubs directly or build its own transport.

## How completed candles are handled

The newest historical or streamed candle is kept pending. Updates carrying the
same timestamp replace it. Only a bar with a later timestamp confirms that the
pending candle has closed, at which point it is passed to the SMA calculation.

Historical bars warm up the averages without placing orders.

## Safety guards

Dry-run is the default. Reading market data and printing signals must never
require an account ID, and must never read an account or place an order. Real
trading requires an account ID plus an explicit opt-in flag.

Before an order is submitted:

- entry requires the current position to be exactly zero;
- exit requires a positive long position;
- exit quantity is capped by the current long position, preventing a new short;
- the signal candle produces a deterministic client order ID.

Use a dedicated account for this example. The API exposes the aggregate position
for a symbol, so the process cannot distinguish a manual position from one
opened by the strategy. Real market orders also carry price and liquidity risk.

## Configuration

Every implementation reads the same settings, whether from flags or environment
variables. Copy [`.env.example`](.env.example) as a reference.

| Environment variable | Required | Default |
| --- | --- | --- |
| `TRADE_API_SECRET` | Yes | — |
| `TRADE_API_SYMBOL` | Yes | — |
| `TRADE_API_ACCOUNT_ID` | Only when placing real orders | — |
| `TRADE_API_TIMEFRAME` | No | `M5` |
| `TRADE_API_QUANTITY` | No | `1` |
| `TRADE_API_LOG_LEVEL` | No | `INFO` |

Symbols use `ticker@mic` format, for example `SBER@MISX`. Supported timeframes
are `M1`, `M5`, `M15`, `M30`, `H1`, `H2`, `H4`, `H8`, `D`, `W`, `MN`, and `QR`.

## Read-only smoke test

Every implementation offers a check mode that authenticates, fetches historical
bars, calculates the latest confirmed SMA values, prints one line, and exits
without opening the live subscription, reading an account, or placing an order:

```text
History check passed: close=... sma9=... sma30=... signal=...
```

## Scope

This is learning material, not a production trading system. Applications derived
from it still need persistent state, stream reconnection, missed-bar backfill,
monitoring, risk limits, reconciliation, and operational controls appropriate to
their use case.
