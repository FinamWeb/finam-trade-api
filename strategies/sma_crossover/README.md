# SMA 9/30 crossover example

This example implements the following long-only rule with the public Python
SDK:

- **Entry:** previous SMA 9 ≤ previous SMA 30, and current SMA 9 > current SMA 30.
- **Exit:** previous SMA 9 ≥ previous SMA 30, and current SMA 9 < current SMA 30.
- Averages use completed candle close prices.
- No signal is emitted while the 30-candle window is warming up.
- A signal is emitted once on the crossover candle, not on every candle while
  one average remains above the other.

## Read the implementation in this order

1. [`strategy.py`](strategy.py) — the small, pure SMA calculation and crossover rule.
2. [`main.py`](main.py) — history, completed live bars, dry-run, and guarded orders.
3. [`tests/test_sma_crossover.py`](tests/test_sma_crossover.py) — executable examples of expected behavior.

The calculation is deliberately independent of the SDK. Developers can test or
reuse it without credentials, networking, or protobuf messages.

## Data and execution flow

```text
client.market_data.Bars ───────┐
                               ├─> completed candles ─> SMA 9/30 ─> signal
client.market_data.SubscribeBars┘                                  │
                                                                  ├─> dry-run log
client.accounts.GetAccount ────────────────────────────────────────┤
client.orders.PlaceOrder <─────────────────────────────────────────┘
```

The SDK already provides all required operations; the example does not import
generated stubs directly or implement a separate transport.

## Run from the repository root

Install the local SDK once:

```sh
python -m pip install -e "./python[dev]"
```

Run safely without placing orders:

```sh
TRADE_API_SECRET=... \
python -m strategies.sma_crossover \
  --symbol SBER@MISX \
  --timeframe M5 \
  --quantity 1
```

You can use environment variables instead of flags. Copy `.env.example` as a
reference; Python does not automatically load that file.

| Environment variable | Required | Default |
| --- | --- | --- |
| `TRADE_API_SECRET` | Yes | — |
| `TRADE_API_SYMBOL` | If `--symbol` is omitted | — |
| `TRADE_API_ACCOUNT_ID` | Only with `--execute` | — |
| `TRADE_API_TIMEFRAME` | No | `M5` |
| `TRADE_API_QUANTITY` | No | `1` |
| `TRADE_API_LOG_LEVEL` | No | `INFO` |

Supported timeframes are `M1`, `M5`, `M15`, `M30`, `H1`, `H2`, `H4`, `H8`,
`D`, `W`, `MN`, and `QR`.

## Smoke-test the real API read-only

Use `--check` to authenticate, fetch historical bars, calculate the latest
confirmed SMA values, print one result, and exit:

```sh
TRADE_API_SECRET=... \
python -m strategies.sma_crossover \
  --symbol SBER@MISX \
  --timeframe M5 \
  --check
```

This mode never opens the live bar subscription, reads an account, or places an
order.
A successful result looks like:

```text
History check passed: close=... sma9=... sma30=... signal=...
```

## How completed candles are handled

The newest historical or streamed candle is kept pending. Updates with the same
timestamp replace it. Only a bar with a later timestamp confirms that the
pending candle has closed, at which point it is passed to the SMA calculator.

Historical bars warm up the averages without placing orders. The example keeps
the live loop intentionally direct; production applications should add stream
reconnection, missed-bar backfill, persistent position state, monitoring, and
risk limits around this core flow.

## Enable real orders explicitly

```sh
TRADE_API_SECRET=... \
TRADE_API_ACCOUNT_ID=... \
python -m strategies.sma_crossover \
  --symbol SBER@MISX \
  --timeframe M5 \
  --quantity 1 \
  --execute
```

Before an order is submitted:

- entry requires the current position to be exactly zero;
- exit requires a positive long position;
- exit quantity is capped by the current long position, preventing a new short;
- the signal candle produces a deterministic client order ID.

Use a dedicated account/position for this example. The API exposes the aggregate
position for a symbol, so the process cannot distinguish a manual position from
one opened by the strategy. Real market orders also carry price and liquidity
risk.

## Run tests

No secret or network access is required:

```sh
python -m pytest strategies/sma_crossover/tests
python -m ruff check strategies
python -m ruff format --check strategies
python -m mypy --config-file strategies/pyproject.toml strategies/sma_crossover
```
