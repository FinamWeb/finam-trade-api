# Finam Trade API

This monorepo contains the Trade API protocol definitions and generated SDKs
for Python, Kotlin, JavaScript, and Go.

## Start here

- [Python SDK](python/README.md)
- [JavaScript SDK](js/README.md)
- [Go SDK](go/README.md)
- [Kotlin examples](kotlin/examples/README.md)
- [API migration guide](MIGRATION_GUIDE.md)

## Trading strategy examples

The [strategies directory](strategies/README.md) contains readable, runnable
examples built with the local Python SDK. Start with the
[SMA 9/30 crossover](strategies/sma_crossover/README.md), which demonstrates:

- historical and streaming candles;
- completed-candle handling;
- signal calculation separated from SDK integration;
- dry-run execution by default;
- guarded market order placement.

From the repository root, install the local SDK and open the example guide:

```sh
python -m pip install -e "./python[dev]"
python -m strategies.sma_crossover --help
```

With an API secret, run a bounded read-only smoke test:

```sh
TRADE_API_SECRET=... python -m strategies.sma_crossover --symbol SBER@MISX --check
```
