# Finam Trade API

This monorepo contains the Trade API protocol definitions and generated SDKs
for Python, Kotlin, JavaScript, and Go.

## Start here

- [Python SDK](sdk/python/README.md)
- [JavaScript SDK](js/README.md)
- [Go SDK](go/README.md)
- [Kotlin examples](kotlin/examples/README.md)
- [API migration guide](MIGRATION_GUIDE.md)

## Trading strategy examples

The [strategies directory](strategies/README.md) contains readable, runnable
examples built with the published SDKs. Each strategy is described once in a
language-neutral README, then implemented per language in a self-contained
directory beneath it.

Start with the [SMA 9/30 crossover](strategies/sma_crossover/README.md), which
demonstrates:

- historical and streaming candles;
- completed-candle handling;
- signal calculation separated from SDK integration;
- dry-run execution by default;
- guarded market order placement.

Its [Python implementation](strategies/sma_crossover/python/) runs against
`finam-sdk` from PyPI:

```sh
cd strategies/sma_crossover/python
python -m pip install -r requirements.txt
TRADE_API_SECRET=... python main.py --symbol SBER@MISX --check
```
