# Примеры Python SDK

Это автономные примеры приложений для опубликованного пакета `finam-sdk`
версии `2.19.0`. Они не импортируют исходники SDK и сгенерированные
protobuf-файлы из этого репозитория.

## Установка и аутентификация

Нужны Python 3.10 или новее и `uv`. Из корня репозитория:

```sh
cd examples/sdk/python
uv sync --locked
TRADE_API_SECRET=... uv run python auth_and_account.py
```

Ограниченный smoke-тест аутентифицируется, печатает видимые ID счетов и
запрашивает первый счёт, если он есть. Он никогда не выставляет заявку.

Чтобы держать секрет в одном месте, а не в каждой команде, заполните корневой
`.env` (см. [Настройку секрета](../README.md#настройка-секрета)) и запустите
тот же пример через `just`, который его загружает:

```sh
just run-sdk-python auth_and_account.py
```

## Поток котировок через asyncio

Этот пример только читает и работает до Ctrl-C:

```sh
TRADE_API_SECRET=... \
uv run python subscribe_quotes_async.py SBER@MISX GAZP@MISX
```

## Выставить и попытаться отменить настоящую лимитную заявку

> **Внимание:** пример отправляет настоящую заявку, которая может исполниться до
> отмены. Используйте выделенный счёт и проверьте инструмент, количество и цену.

```sh
TRADE_API_SECRET=... \
TRADE_API_SYMBOL=SBER@MISX \
TRADE_API_QUANTITY=1 \
TRADE_API_LIMIT_PRICE=REPLACE_WITH_LIMIT_PRICE \
TRADE_API_EXECUTE=1 \
uv run python place_limit_order.py
```

У примера с заявкой намеренно нет цены по умолчанию.

## Контрибьюторам: локальный SDK

Закоммиченная зависимость и lock-файл всегда указывают на опубликованный wheel.
Из корня репозитория можно подключить SDK из текущего checkout в editable-режиме:

```sh
just examples-use-local-python
just examples-status
```

Пока действует editable-переопределение, используйте `uv run --no-sync`:
обычный `uv run` синхронизирует окружение обратно с опубликованным lock-файлом.
Корневая smoke-команда делает это сама:

```sh
just smoke-python-examples
```

Вернуть опубликованный wheel детерминированно:

```sh
just examples-use-published-python
```
