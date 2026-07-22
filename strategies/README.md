# Strategy examples

This directory shows how to build trading strategies with the Python SDK in
this monorepo. The examples favor readable code, safe defaults, and explicit
API calls so developers can copy the patterns into their own applications.

## Available strategies

| Strategy | Rule | Start here |
| --- | --- | --- |
| SMA 9/30 crossover | Enter when SMA 9 crosses above SMA 30; exit on the reverse crossover | [`sma_crossover/README.md`](sma_crossover/README.md) |

## Run the SMA example in three steps

Run these commands from the repository root.

1. Create a virtual environment:

   ```sh
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install the local Python SDK and development tools:

   ```sh
   python -m pip install -e "./python[dev]"
   ```

3. Start the strategy in safe dry-run mode:

   ```sh
   TRADE_API_SECRET=... \
   python -m strategies.sma_crossover \
     --symbol SBER@MISX \
     --timeframe M5 \
     --quantity 1
   ```

Dry-run is the default: the example reads real market data and prints signals,
but it does not read an account or place orders. Real trading requires both an
account ID and the explicit `--execute` flag.

For a bounded read-only smoke test that exits after loading history:

```sh
TRADE_API_SECRET=... \
python -m strategies.sma_crossover --symbol SBER@MISX --check
```

## Example conventions

Every strategy added here should:

- have its own directory and README;
- keep signal calculation separate from API and order code;
- evaluate completed candles rather than changing candles;
- start in dry-run mode;
- require an explicit flag before placing orders;
- include focused unit tests that do not need credentials or network access.

The strategy examples are learning material, not a production trading system.
Applications derived from them still need persistent state, monitoring, risk
limits, reconciliation, and operational controls appropriate to their use case.
