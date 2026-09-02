# Finam Trade API — Python SDK

Python SDK Finam для gRPC Trade API. Оборачивает сгенерированные заглушки:

- одна точка входа `FinamClient` / `AsyncFinamClient`;
- автоматический выпуск JWT и фоновое обновление (через
  `AuthService.SubscribeJwtRenewal`);
- помощник `from_rpc_error()` для типизированных ошибок;
- повторы с экспоненциальной задержкой для `UNAVAILABLE` и одобренные сервером
  повторы при ограничении частоты запросов.

Методы сервисов вызываются напрямую на сгенерированных заглушках, без
дополнительного слоя преобразования запросов и ответов.

## Установка

Нужен Python 3.10 или новее.

Текущий checkout соответствует версии `2.19.1`. Создайте и активируйте
виртуальное окружение, затем установите пакет:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install finam-sdk==2.19.1
```

> Дистрибутив в PyPI называется `finam-sdk`; имя импорта в Python —
> `finam_trade_api`. (Имя `finam-trade-api` в PyPI занято сторонним
> REST-клиентом, не связанным с этим проектом.)

## Быстрый старт

Первая программа аутентифицируется и печатает ID счетов, видимых секрету. Она
ограничена и не выставляет заявку.

Сохраните это как `quickstart.py`:

```python
import os

from finam_trade_api import FinamClient
from finam_trade_api.auth_messages import TokenDetailsRequest


secret = os.environ["TRADE_API_SECRET"]

with FinamClient(secret=secret) as client:
    token = client.get_token()
    if token is None:
        raise RuntimeError("Authentication did not return a token")

    details = client.auth.TokenDetails(TokenDetailsRequest(token=token))
    print("Available account IDs:", list(details.account_ids))
```

Запустите внутри активированного виртуального окружения:

```sh
TRADE_API_SECRET=... python quickstart.py
```

Если аутентификация не проходит, убедитесь, что секрет активен. Пустой список
счетов означает, что токен не открывает торговый счёт; он всё ещё может
подходить для рыночных данных, если у него есть соответствующее право.

Чтобы получить один из обнаруженных счетов, расширьте программу так:

```python
import os

from finam_trade_api import FinamClient
from finam_trade_api.accounts import GetAccountRequest
from finam_trade_api.auth_messages import TokenDetailsRequest


with FinamClient(secret=os.environ["TRADE_API_SECRET"]) as client:
    token = client.get_token()
    if token is None:
        raise RuntimeError("Authentication did not return a token")

    details = client.auth.TokenDetails(TokenDetailsRequest(token=token))
    if not details.account_ids:
        raise RuntimeError("This secret exposes no accounts")

    account_id = details.account_ids[0]
    account = client.accounts.GetAccount(GetAccountRequest(account_id=account_id))
    print(account)
```

## Быстрый старт с asyncio

```python
import asyncio
import os

from finam_trade_api import AsyncFinamClient
from finam_trade_api.auth_messages import TokenDetailsRequest


async def main() -> None:
    async with AsyncFinamClient(secret=os.environ["TRADE_API_SECRET"]) as client:
        token = client.get_token()
        if token is None:
            raise RuntimeError("Authentication did not return a token")

        details = await client.auth.TokenDetails(TokenDetailsRequest(token=token))
        print("Available account IDs:", list(details.account_ids))


asyncio.run(main())
```

## Подписка на рыночные данные

Потоковые RPC возвращают итераторы. Этот синхронный пример работает до Ctrl-C;
выход из контекстного менеджера закрывает канал и поток обновления токена:

```python
import os

from finam_trade_api import FinamClient
from finam_trade_api.market_data import SubscribeQuoteRequest


with FinamClient(secret=os.environ["TRADE_API_SECRET"]) as client:
    for tick in client.market_data.SubscribeQuote(
        SubscribeQuoteRequest(symbols=["SBER@MISX"])
    ):
        print(tick)
```

В репозитории также есть точечные примеры для
[аутентификации и счетов](../../examples/sdk/python/auth_and_account.py),
[асинхронного потока котировок](../../examples/sdk/python/subscribe_quotes_async.py)
и [настоящей заявки с отменой](../../examples/sdk/python/place_limit_order.py).
Они живут в [автономном проекте-потребителе](../../examples/sdk/python/),
который по умолчанию устанавливает опубликованный пакет.

## Доступные сервисы

Клиент открывает эти сервисы Trade API как подклиенты:

| Атрибут              | gRPC-сервис           | Назначение                                           |
| -------------------- | --------------------- | ---------------------------------------------------- |
| `client.auth`        | `AuthService`         | Выпуск токена и его детали (обычно автоматически).   |
| `client.accounts`    | `AccountsService`     | Счета, позиции, сделки, транзакции.                  |
| `client.assets`      | `AssetsService`       | Инструменты, биржи, расписания, опционы.             |
| `client.corporate_actions` | `CorporateActionsService` | Сплиты, дивиденды, события по облигациям.      |
| `client.market_data` | `MarketDataService`   | Свечи, котировки, стакан, потоки сделок.             |
| `client.orders`      | `OrdersService`       | Выставление и отмена заявок, потоки заявок и сделок. |
| `client.reports`     | `ReportsService`      | Отчёты по счёту (только российский контур).          |
| `client.metrics`     | `UsageMetricsService` | Метрики использования API и квоты.                   |

## Справочник API

Каждый RPC перечисленных ниже сервисов доступен напрямую на своём подклиенте.
Типы сообщений запросов и ответов реэкспортируются из коротких модулей по
сервисам:

| Модуль                          | Используется с                                              |
| ------------------------------- | ----------------------------------------------------------- |
| `finam_trade_api.accounts`      | `client.accounts.*`                                         |
| `finam_trade_api.assets`        | `client.assets.*`                                           |
| `finam_trade_api.corporate_actions` | `client.corporate_actions.*`                            |
| `finam_trade_api.market_data`   | `client.market_data.*`                                      |
| `finam_trade_api.orders`        | `client.orders.*` (включая `Side`)                          |
| `finam_trade_api.reports`       | `client.reports.*`                                          |
| `finam_trade_api.metrics`       | `client.metrics.*`                                          |
| `finam_trade_api.auth_messages` | `client.auth.*` (нужно редко — JWT обрабатывается автоматически) |

Исходные глубоко вложенные пути
(`finam_trade_api.proto.grpc.tradeapi.v1.<service>.<service>_service_pb2`)
по-прежнему работают и остаются источником истины.

Обозначения: ▶ унарный · ⇉ серверный поток · ⇄ двунаправленный поток

### `client.auth` — `AuthService`

| Метод                                             | Вид | Назначение                                                            |
| ------------------------------------------------- | :-: | --------------------------------------------------------------------- |
| `Auth(AuthRequest)`                               |  ▶  | Обменять секрет API на JWT. _Вызывается за вас при создании клиента._ |
| `TokenDetails(TokenDetailsRequest)`               |  ▶  | Проверить JWT — срок действия, права на рыночные данные, ID счетов.   |
| `SubscribeJwtRenewal(SubscribeJwtRenewalRequest)` |  ⇉  | Поток обновлённых JWT. _Потребляется за вас в фоне._                  |

`AuthService` принимает секрет или токен в теле запроса и должен вызываться без
заголовка `Authorization`: сервер отклоняет `TokenDetails`, если заголовок
присутствует. SDK держит `client.auth` на отдельном канале без учётных данных
вызова, поэтому вручную ничего делать не нужно.

### `client.accounts` — `AccountsService`

| Метод                                 | Вид | Назначение                                        |
| ------------------------------------- | :-: | ------------------------------------------------- |
| `GetAccount(GetAccountRequest)`       |  ▶  | Информация о счёте: средства, позиции, маржа.     |
| `Trades(TradesRequest)`               |  ▶  | Исторические сделки по счёту.                     |
| `Transactions(TransactionsRequest)`   |  ▶  | Движения денег и другие неторговые транзакции.    |
| `SubscribeAccount(GetAccountRequest)` |  ⇉  | Потоковые обновления счёта.                       |

### `client.assets` — `AssetsService`

| Метод                                     | Вид | Назначение                                        |
| ----------------------------------------- | :-: | ------------------------------------------------- |
| `Exchanges(ExchangesRequest)`             |  ▶  | Список поддерживаемых бирж.                       |
| `Assets(AssetsRequest)`                   |  ▶  | Торгуемые инструменты (с фильтром).               |
| `AllAssets(AllAssetsRequest)`             |  ▶  | Полный каталог инструментов.                      |
| `GetAsset(GetAssetRequest)`               |  ▶  | Один инструмент по символу.                       |
| `GetAssetParams(GetAssetParamsRequest)`   |  ▶  | Торговые параметры инструмента.                   |
| `OptionsChain(OptionsChainRequest)`       |  ▶  | Цепочка опционов по базовому активу.              |
| `Schedule(ScheduleRequest)`               |  ▶  | Расписание торговых сессий.                       |
| `Clock(ClockRequest)`                     |  ▶  | Серверное время (для операций, привязанных ко времени). |
| `GetConstituents(GetConstituentsRequest)` |  ▶  | Состав индекса.                                   |

### `client.corporate_actions` — `CorporateActionsService`

| Метод                                                 | Вид | Назначение                                        |
| ----------------------------------------------------- | :-: | ------------------------------------------------- |
| `GetFutureSplits(GetFutureSplitsRequest)`             |  ▶  | Предстоящие сплиты и консолидации.                |
| `GetPastSplits(GetPastSplitsRequest)`                 |  ▶  | Прошедшие сплиты и консолидации.                  |
| `GetFutureDividends(GetFutureDividendsRequest)`       |  ▶  | Предстоящие дивиденды.                            |
| `GetPastDividends(GetPastDividendsRequest)`           |  ▶  | Выплаченные дивиденды.                            |
| `GetFutureBondsEvents(GetFutureBondsEventsRequest)`   |  ▶  | Предстоящие купоны, амортизации и оферты.         |
| `GetPastBondsEvents(GetPastBondsEventsRequest)`       |  ▶  | Прошедшие события по облигациям.                  |

### `client.market_data` — `MarketDataService`

| Метод                                                 | Вид | Назначение                                          |
| ----------------------------------------------------- | :-: | --------------------------------------------------- |
| `Bars(BarsRequest)`                                   |  ▶  | Свечи OHLC (любой таймфрейм через enum `TimeFrame`). |
| `LastQuote(QuoteRequest)`                             |  ▶  | Последний снимок котировки.                         |
| `OrderBook(OrderBookRequest)`                         |  ▶  | Снимок стакана.                                     |
| `LatestTrades(LatestTradesRequest)`                   |  ▶  | Последние сделки по инструменту.                    |
| `SubscribeQuote(SubscribeQuoteRequest)`               |  ⇉  | Поток котировок.                                    |
| `SubscribeOrderBook(SubscribeOrderBookRequest)`       |  ⇉  | Поток обновлений стакана.                           |
| `SubscribeLatestTrades(SubscribeLatestTradesRequest)` |  ⇉  | Поток сделок.                                       |
| `SubscribeBars(SubscribeBarsRequest)`                 |  ⇉  | Поток свечей.                                       |

### `client.orders` — `OrdersService`

| Метод                                           | Вид | Назначение                                                    |
| ----------------------------------------------- | :-: | ------------------------------------------------------------- |
| `PlaceOrder(Order)`                             |  ▶  | Выставить рыночную / лимитную / стоп / стоп-лимит / многоногую заявку. |
| `PlaceSLTPOrder(SLTPOrder)`                     |  ▶  | Выставить заявку SL/TP (стоп-лосс + тейк-профит).             |
| `CancelOrder(CancelOrderRequest)`               |  ▶  | Отменить активную заявку.                                     |
| `GetOrders(OrdersRequest)`                      |  ▶  | Список активных заявок по счёту.                              |
| `GetOrder(GetOrderRequest)`                     |  ▶  | Одна заявка по ID.                                            |
| `SubscribeOrders(SubscribeOrdersRequest)`       |  ⇉  | Поток изменений состояния заявок.                             |
| `SubscribeTrades(SubscribeTradesRequest)`       |  ⇉  | Поток исполнений.                                             |
| `SubscribeOrderTrade(stream OrderTradeRequest)` |  ⇄  | Двунаправленный поток — события заявок и сделок по запросу.   |

### `client.reports` — `ReportsService`

| Метод                                                           | Вид | Назначение                                     |
| --------------------------------------------------------------- | :-: | ---------------------------------------------- |
| `CreateAccountReport(CreateAccountReportRequest)`               |  ▶  | Заказать отчёт по счёту за период.             |
| `GetAccountReportInfo(GetAccountReportInfoRequest)`             |  ▶  | Статус и ссылка на готовый отчёт.              |
| `SubscribeAccountReportInfo(SubscribeAccountReportInfoRequest)` |  ⇉  | Поток обновлений статуса отчёта.               |

### `client.metrics` — `UsageMetricsService`

| Метод                                     | Вид | Назначение                                              |
| ----------------------------------------- | :-: | ------------------------------------------------------- |
| `GetUsageMetrics(GetUsageMetricsRequest)` |  ▶  | Статистика использования API и квот для текущего токена. |

### Жизненный цикл клиента

| Операция          | Sync                                                                                                 | Async                                                                |
| ----------------- | ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Создание          | `FinamClient(secret, *, endpoint=DEFAULT_ENDPOINT, retry_policy=DEFAULT_POLICY, channel_options=None)` | `AsyncFinamClient(secret, ...)` — те же аргументы                    |
| Запуск            | _сразу, блокируется до получения первого JWT_                                                        | `await client.start()` — или используйте `async with`                |
| Текущий JWT       | `client.get_token()` → `str \| None`                                                                 | `client.get_token()` → `str \| None` (синхронное чтение снимка)      |
| Закрытие          | `client.close()`                                                                                     | `await client.close()`                                               |
| Контекстный менеджер | `with FinamClient(...) as client:`                                                                | `async with AsyncFinamClient(...) as client:`                        |
| Тестирование (без TLS) | `FinamClient.for_testing(secret, endpoint="localhost:50051")`                                   | `AsyncFinamClient.for_testing(secret, endpoint="localhost:50051")`   |

> `for_testing(...)` открывает небезопасный (plaintext) канал к локальному
> фейковому серверу. **Никогда не используйте его с `api.finam.ru`** — JWT
> уйдёт открытым текстом.

## Обработка ошибок

Вызовы SDK поднимают «сырые» `grpc.RpcError`. Используйте `from_rpc_error()`,
когда приложению полезна типизированная иерархия `FinamError`:

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

Классы исключений: `AuthError` (401), `PermissionDeniedError` (403),
`InvalidArgumentError` (400), `NotFoundError` (404), `RateLimitError` (429),
`InternalError` (500), `ServiceUnavailableError` (503),
`DeadlineExceededError` (504). Все наследуются от `FinamError`.

## Повторы

Унарные RPC автоматически повторяются при `UNAVAILABLE` с экспоненциальной
задержкой и джиттером. `RESOURCE_EXHAUSTED` повторяется только когда сервер
передаёт `grpc-retry-pushback-ms`; иначе SDK возвращает ошибку ограничения
частоты, а не усиливает нагрузку. Потоковые RPC _не_ повторяются — ожидается,
что вызывающий код переподключится на осмысленной границе, например с последней
полученной свечи.

Переопределить политику:

```python
from finam_trade_api import FinamClient, RetryPolicy

policy = RetryPolicy(max_attempts=6, initial_backoff=0.5, max_backoff=10.0)
client = FinamClient(secret="...", retry_policy=policy)
```

## Локальная сборка

Из корня репозитория:

```sh
cd sdk/python
uv sync --locked
uv run ./scripts/generate_proto.sh
uv run ruff check finam_trade_api tests
uv run mypy finam_trade_api
uv run pytest
```

`scripts/generate_proto.sh` компилирует `.proto`-файлы из `../../proto/` в
`finam_trade_api/proto/`. Перезапускайте его при каждом изменении контрактов.

## Структура

```
sdk/python/
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── scripts/
│   ├── generate_proto.sh       # вызов protoc (только для контрибьюторов)
│   └── verify_distribution.py  # проверка содержимого wheel и sdist в CI
└── finam_trade_api/
    ├── __init__.py
    ├── client.py               # FinamClient (sync)
    ├── aio.py                  # AsyncFinamClient
    ├── auth.py                 # жизненный цикл JWT
    ├── retry.py                # политика повторов + интерсепторы
    ├── exceptions.py           # типизированные ошибки
    ├── _insecure_auth.py       # аутентификация на plaintext-канале для тестов
    ├── _metadata.py            # передача заголовка Authorization
    ├── _services.py            # ленивый реестр сгенерированных сервисов
    ├── accounts.py             # реэкспорт сообщений (по сервисам)
    ├── assets.py
    ├── auth_messages.py
    ├── corporate_actions.py
    ├── market_data.py
    ├── orders.py
    ├── reports.py
    ├── metrics.py
    └── proto/                  # генерируется CI; входит в wheel и sdist
```
