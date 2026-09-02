set shell := ["zsh", "-cu"]

# Каждый рецепт ниже загружает .env из корня репозитория, поэтому один файл
# задаёт TRADE_API_SECRET и общие настройки примеров. Скопируйте .env.example
# в .env, чтобы создать его. Переменные, уже экспортированные в оболочке,
# имеют приоритет.
set dotenv-load := true
set dotenv-path := "."

default: check

# Установить все зависимости для разработки из lock-файлов.
bootstrap:
    npm --prefix sdk/node ci
    npm --prefix examples/sdk/node ci
    npm --prefix examples/strategies/sma_crossover/node ci
    npm --prefix examples/strategies/macd_zero_cross/node ci
    npm --prefix examples/strategies/rsi_threshold/node ci
    cd sdk/python && uv sync --locked
    cd examples/sdk/python && uv sync --locked
    cd examples/strategies/sma_crossover/python && uv sync --locked
    cd examples/strategies/macd_zero_cross/python && uv sync --locked
    cd examples/strategies/rsi_threshold/python && uv sync --locked
    uv tool install pre-commit
    pre-commit install
    just generate

# Пересобрать привязки Python и Node.js из исходных proto-файлов.
# Go-привязки, JS-привязки (js/) и Kotlin SDK собираются своими инструментами;
# см. README соответствующих каталогов.
generate:
    npm --prefix sdk/node run generate
    cd sdk/python && uv run ./scripts/generate_proto.sh

# Применить детерминированное форматирование и безопасные автоисправления линтера.
format:
    npm --prefix sdk/node run format
    npm --prefix examples/sdk/node run format
    npm --prefix examples/strategies/sma_crossover/node run format
    npm --prefix examples/strategies/macd_zero_cross/node run format
    npm --prefix examples/strategies/rsi_threshold/node run format
    cd sdk/python && uv run ruff check --fix finam_trade_api tests
    cd sdk/python && uv run ruff format finam_trade_api tests
    cd examples/sdk/python && uv run --no-sync ruff check --fix .
    cd examples/sdk/python && uv run --no-sync ruff format .
    cd examples/strategies/sma_crossover/python && uv run --no-sync ruff check --fix .
    cd examples/strategies/sma_crossover/python && uv run --no-sync ruff format .
    cd examples/strategies/macd_zero_cross/python && uv run --no-sync ruff check --fix .
    cd examples/strategies/macd_zero_cross/python && uv run --no-sync ruff format .
    cd examples/strategies/rsi_threshold/python && uv run --no-sync ruff check --fix .
    cd examples/strategies/rsi_threshold/python && uv run --no-sync ruff format .

# Быстрые статические проверки; файлы не изменяются.
lint:
    npm --prefix sdk/node run lint
    npm --prefix examples/sdk/node run lint
    npm --prefix examples/strategies/sma_crossover/node run lint
    npm --prefix examples/strategies/macd_zero_cross/node run lint
    npm --prefix examples/strategies/rsi_threshold/node run lint
    cd sdk/python && uv run ruff check finam_trade_api tests
    cd sdk/python && uv run ruff format --check finam_trade_api tests
    cd examples/sdk/python && uv run --no-sync ruff check .
    cd examples/sdk/python && uv run --no-sync ruff format --check .
    cd examples/strategies/sma_crossover/python && uv run --no-sync ruff check .
    cd examples/strategies/sma_crossover/python && uv run --no-sync ruff format --check .
    cd examples/strategies/macd_zero_cross/python && uv run --no-sync ruff check .
    cd examples/strategies/macd_zero_cross/python && uv run --no-sync ruff format --check .
    cd examples/strategies/rsi_threshold/python && uv run --no-sync ruff check .
    cd examples/strategies/rsi_threshold/python && uv run --no-sync ruff format --check .

typecheck: generate
    npm --prefix sdk/node run typecheck
    npm --prefix examples/sdk/node run typecheck
    npm --prefix examples/strategies/sma_crossover/node run typecheck
    npm --prefix examples/strategies/macd_zero_cross/node run typecheck
    npm --prefix examples/strategies/rsi_threshold/node run typecheck
    cd sdk/python && uv run mypy finam_trade_api
    cd examples/sdk/python && uv run --no-sync mypy .
    cd examples/strategies/sma_crossover/python && uv run --no-sync mypy .
    cd examples/strategies/macd_zero_cross/python && uv run --no-sync mypy .
    cd examples/strategies/rsi_threshold/python && uv run --no-sync mypy .

test: generate
    npm --prefix sdk/node test
    npm --prefix examples/strategies/sma_crossover/node test
    npm --prefix examples/strategies/macd_zero_cross/node test
    npm --prefix examples/strategies/rsi_threshold/node test
    cd sdk/python && uv run pytest
    cd examples/strategies/sma_crossover/python && uv run --no-sync pytest
    cd examples/strategies/macd_zero_cross/python && uv run --no-sync pytest
    cd examples/strategies/rsi_threshold/python && uv run --no-sync pytest

check: lint typecheck test

# Заменить опубликованные SDK в каждом автономном примере на SDK из текущего
# checkout. Манифесты и lock-файлы не изменяются.
examples-use-local-node:
    npm --prefix sdk/node run build
    cd examples/sdk/node && npm install --no-save ../../../sdk/node
    cd examples/strategies/sma_crossover/node && npm install --no-save ../../../../sdk/node
    cd examples/strategies/macd_zero_cross/node && npm install --no-save ../../../../sdk/node
    cd examples/strategies/rsi_threshold/node && npm install --no-save ../../../../sdk/node

examples-use-local-python:
    cd sdk/python && uv sync --locked
    cd sdk/python && uv run ./scripts/generate_proto.sh
    cd examples/sdk/python && uv sync --locked
    cd examples/sdk/python && uv pip install --python .venv/bin/python --editable ../../../sdk/python
    cd examples/strategies/sma_crossover/python && uv sync --locked
    cd examples/strategies/sma_crossover/python && uv pip install --python .venv/bin/python --editable ../../../../sdk/python
    cd examples/strategies/macd_zero_cross/python && uv sync --locked
    cd examples/strategies/rsi_threshold/python && uv sync --locked
    cd examples/strategies/macd_zero_cross/python && uv pip install --python .venv/bin/python --editable ../../../../sdk/python
    cd examples/strategies/rsi_threshold/python && uv pip install --python .venv/bin/python --editable ../../../../sdk/python

examples-use-local: examples-use-local-node examples-use-local-python

# Пересобирать подключённый Node.js SDK при изменении исходников. Запускайте
# во втором терминале после examples-use-local-node для итеративной отладки.
watch-node-sdk:
    npm --prefix sdk/node run dev

# Вернуть каждый автономный пример к зафиксированной опубликованной зависимости.
examples-use-published-node:
    npm --prefix examples/sdk/node ci
    npm --prefix examples/strategies/sma_crossover/node ci
    npm --prefix examples/strategies/macd_zero_cross/node ci
    npm --prefix examples/strategies/rsi_threshold/node ci

examples-use-published-python:
    cd examples/sdk/python && uv sync --locked
    cd examples/strategies/sma_crossover/python && uv sync --locked
    cd examples/strategies/macd_zero_cross/python && uv sync --locked
    cd examples/strategies/rsi_threshold/python && uv sync --locked

examples-use-published: examples-use-published-node examples-use-published-python

# Показать реальные пути импорта: так видно, установлен ли пакет из реестра
# или подключён локально, даже если версии совпадают.
examples-status:
    cd examples/sdk/node && node --input-type=module --eval 'import { realpathSync } from "node:fs"; import { fileURLToPath } from "node:url"; console.log("Node SDK example:", realpathSync(fileURLToPath(import.meta.resolve("@finam/trade-api"))))'
    cd examples/strategies/sma_crossover/node && node --input-type=module --eval 'import { realpathSync } from "node:fs"; import { fileURLToPath } from "node:url"; console.log("Node SMA strategy:", realpathSync(fileURLToPath(import.meta.resolve("@finam/trade-api"))))'
    cd examples/strategies/macd_zero_cross/node && node --input-type=module --eval 'import { realpathSync } from "node:fs"; import { fileURLToPath } from "node:url"; console.log("Node MACD strategy:", realpathSync(fileURLToPath(import.meta.resolve("@finam/trade-api"))))'
    cd examples/strategies/rsi_threshold/node && node --input-type=module --eval 'import { realpathSync } from "node:fs"; import { fileURLToPath } from "node:url"; console.log("Node RSI strategy:", realpathSync(fileURLToPath(import.meta.resolve("@finam/trade-api"))))'
    uv run --project examples/sdk/python --no-sync python -c 'import finam_trade_api; print("Python SDK example:", finam_trade_api.__file__)'
    uv run --project examples/strategies/sma_crossover/python --no-sync python -c 'import finam_trade_api; print("Python SMA strategy:", finam_trade_api.__file__)'
    uv run --project examples/strategies/macd_zero_cross/python --no-sync python -c 'import finam_trade_api; print("Python MACD strategy:", finam_trade_api.__file__)'
    uv run --project examples/strategies/rsi_threshold/python --no-sync python -c 'import finam_trade_api; print("Python RSI strategy:", finam_trade_api.__file__)'

# Показать общие настройки из корневого .env. Секрет маскируется.
env-status:
    for name in TRADE_API_SECRET TRADE_API_SYMBOL TRADE_API_TIMEFRAME TRADE_API_QUANTITY TRADE_API_LOG_LEVEL TRADE_API_LIMIT_PRICE TRADE_API_EXECUTE; do value="${(P)name:-}"; if [ -z "$value" ]; then printf '%-22s unset\n' "$name"; elif [ "$name" = TRADE_API_SECRET ]; then printf '%-22s set (%d characters)\n' "$name" "${#value}"; else printf '%-22s %s\n' "$name" "$value"; fi; done

# Запустить реализацию стратегии с настройками из корневого .env. STRATEGY —
# sma_crossover, macd_zero_cross или rsi_threshold; остальные аргументы
# передаются программе. По умолчанию dry-run; --check ограничен и только читает.
#   just run-strategy-python sma_crossover --check
run-strategy-python strategy *args:
    uv run --project examples/strategies/{{strategy}}/python --no-sync python examples/strategies/{{strategy}}/python/main.py {{args}}

# Node.js-аналог run-strategy-python.
#   just run-strategy-node sma_crossover --check
run-strategy-node strategy *args:
    npm --prefix examples/strategies/{{strategy}}/node start -- {{args}}

# Запустить точечный пример SDK с настройками из корневого .env. SCRIPT — имя
# файла в examples/sdk/python/.
#   just run-sdk-python auth_and_account.py
run-sdk-python script *args:
    uv run --project examples/sdk/python --no-sync python examples/sdk/python/{{script}} {{args}}

# Node.js-аналог run-sdk-python. SCRIPT — скрипт пакета: auth, quotes или order.
#   just run-sdk-node auth
run-sdk-node script *args:
    npm --prefix examples/sdk/node run {{script}} -- {{args}}

# Ограниченные проверки только на чтение против реального API в текущем режиме SDK.
smoke-node-examples:
    npm --prefix examples/sdk/node run smoke
    npm --prefix examples/strategies/sma_crossover/node start -- --symbol "${TRADE_API_SYMBOL:-SBER@MISX}" --check
    npm --prefix examples/strategies/macd_zero_cross/node start -- --symbol "${TRADE_API_SYMBOL:-SBER@MISX}" --check
    npm --prefix examples/strategies/rsi_threshold/node start -- --symbol "${TRADE_API_SYMBOL:-SBER@MISX}" --check

smoke-python-examples:
    uv run --project examples/sdk/python --no-sync python examples/sdk/python/auth_and_account.py
    uv run --project examples/strategies/sma_crossover/python --no-sync python examples/strategies/sma_crossover/python/main.py --symbol "${TRADE_API_SYMBOL:-SBER@MISX}" --check
    uv run --project examples/strategies/macd_zero_cross/python --no-sync python examples/strategies/macd_zero_cross/python/main.py --symbol "${TRADE_API_SYMBOL:-SBER@MISX}" --check
    uv run --project examples/strategies/rsi_threshold/python --no-sync python examples/strategies/rsi_threshold/python/main.py --symbol "${TRADE_API_SYMBOL:-SBER@MISX}" --check

smoke-examples: smoke-node-examples smoke-python-examples

smoke-examples-local: examples-use-local smoke-examples

smoke-examples-published: examples-use-published smoke-examples
