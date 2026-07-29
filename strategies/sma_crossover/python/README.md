# SMA 9/30 crossover — Python

Python implementation of the [SMA 9/30 crossover strategy](../README.md), built
on the published SDK (`pip install finam-sdk`, imported as `finam_trade_api`).

Read [`../README.md`](../README.md) first for the rule, candle handling, and
safety guards. This page covers only how to install, run, and test the Python
version.

This directory is self-contained — copy it out of the repository and it still
runs.

## Read the implementation in this order

1. [`strategy.py`](strategy.py) — the small, pure SMA calculation and crossover rule.
2. [`main.py`](main.py) — history, completed live bars, dry-run, and guarded orders.
3. [`tests/test_sma_crossover.py`](tests/test_sma_crossover.py) — executable examples of expected behavior.

The calculation is deliberately independent of the SDK. It can be tested or
reused without credentials, networking, or protobuf messages.

## Install

Python 3.10 or newer is required — the published SDK wheel carries protobuf 7
gencode, and protobuf 7 dropped Python 3.9.

```sh
cd strategies/sma_crossover/python
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run

Dry-run is the default: the example reads real market data and prints signals,
but never reads an account or places an order.

```sh
TRADE_API_SECRET=... \
python main.py \
  --symbol SBER@MISX \
  --timeframe M5 \
  --quantity 1
```

Environment variables work in place of flags — see the table in
[`../README.md`](../README.md#configuration). Python does not load
[`../.env.example`](../.env.example) automatically; it is a reference.

For the bounded read-only smoke test against the live API:

```sh
TRADE_API_SECRET=... python main.py --symbol SBER@MISX --check
```

To place real market orders, pass an account ID and `--execute`:

```sh
TRADE_API_SECRET=... \
TRADE_API_ACCOUNT_ID=... \
python main.py --symbol SBER@MISX --quantity 1 --execute
```

Full flag reference: `python main.py --help`.

The example is deliberately flat — two modules and a test file, no package
scaffolding — so it can be read top to bottom and dropped into an existing
project without rewiring imports.

## Test

No secret or network access is required:

```sh
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy .
```
