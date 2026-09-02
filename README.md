# Finam Trade API

Используйте [Finam Trade API](https://tradeapi.finam.ru/) из Python или Node.js
или начните с готовой стратегии-примера. SDK берут на себя gRPC-транспорт,
аутентификацию, обновление токена, повторы и потоки, чтобы приложение занималось
только торговой логикой.

## С чего начать

| Цель | Рекомендуемый путь |
| --- | --- |
| Увидеть работу API, не выставляя заявку | [Запустить проверку истории для SMA-стратегии](#безопасная-проверка-стратегии) |
| Написать приложение на Python | [Быстрый старт Python SDK](sdk/python/README.md#быстрый-старт) |
| Написать приложение на Node.js | [Быстрый старт Node.js SDK](sdk/node/README.md#быстрый-старт) |
| Разобрать полную стратегию | [Пересечение SMA 9/30](examples/strategies/sma_crossover/) |
| Посмотреть второе, асимметричное правило | [Пересечение нуля MACD 12/26/9](examples/strategies/macd_zero_cross/) |
| Посмотреть правило возврата к среднему | [Пороги RSI 14](examples/strategies/rsi_threshold/) |
| Использовать Kotlin, Go или сырые JS-привязки | [Другие языки](#другие-языки) |
| Перейти со старого Trade API | [Руководство по миграции](MIGRATION_GUIDE.md) |
| Работать над этим репозиторием | [Разработка репозитория](#разработка-репозитория) |

Текущий checkout соответствует релизу `2.19.1`. Пакет Node.js `@finam/trade-api`
публикуется в npm, пакет Python `finam-sdk` — в PyPI.

## Перед началом

Нужен секрет Trade API. Выпустите его на странице
[Токены](https://tradeapi.finam.ru/docs/tokens/) портала Finam Trade API.
Обращайтесь с ним как с паролем: держите в переменных окружения или в
игнорируемом git файле `.env` и никогда не вставляйте в исходный код, чаты,
задачи и логи. Контрибьюторы этого checkout могут положить его в один корневой
`.env`; см. [Один файл окружения для всех примеров](#один-файл-окружения-для-всех-примеров).

Инструменты в примерах записываются как `ticker@mic`, например `SBER@MISX`.
Какие операции и инструменты доступны, определяют права на счёт и рыночные
данные, привязанные к секрету.

## Безопасная проверка стратегии

Ограниченный режим `--check` аутентифицируется, загружает исторические свечи,
считает последние значения SMA, печатает одну строку результата и завершается.
Он не подписывается на поток, не читает счёт и не выставляет заявку.

### Python

Нужны Python 3.10 или новее и [uv](https://docs.astral.sh/uv/).

```sh
cd examples/strategies/sma_crossover/python
uv sync --locked
TRADE_API_SECRET=... uv run python main.py --symbol SBER@MISX --check
```

### Node.js

Нужен Node.js 20 или новее.

```sh
cd examples/strategies/sma_crossover/node
npm ci
TRADE_API_SECRET=... npm start -- --symbol SBER@MISX --check
```

Ожидаемый вывод начинается так:

```text
History check passed: close=... sma9=... sma30=... signal=...
```

Продолжите с [описания стратегии](examples/strategies/sma_crossover/), чтобы
узнать, как устроены потоковый dry-run, закрытие свечей, сигналы и защищённое
исполнение.

## Использовать SDK

- [Python SDK](sdk/python/README.md) — синхронный и asyncio-клиенты;
  устанавливается как `finam-sdk`, импортируется как `finam_trade_api`.
- [Node.js SDK](sdk/node/README.md) — унарные вызовы через Promise и потоки
  через `AsyncIterable`; устанавливается как `@finam/trade-api`.

Оба быстрых старта начинаются с аутентификации и обнаружения счетов. Автономные
примеры-потребители лежат в [`examples/sdk/`](examples/sdk/); их манифесты и
lock-файлы устанавливают опубликованные SDK. Полные приложения-стратегии лежат в
[`examples/strategies/`](examples/strategies/).

## Другие языки

- [Kotlin SDK и примеры](kotlin/examples/README.md) — Gradle-проект с
  клиентом, WebSocket-подписками и примерами; публикуется в Maven Central как
  `ru.finam.tradeapi:finam-trade-api-kotlin`.
- [Go-привязки](go/README.md) — сгенерированный gRPC-клиент; модуль
  `github.com/FinamWeb/finam-trade-api/go`.
- [JavaScript-привязки](js/README.md) — пакет `@finam/grpc-tradeapi`,
  сгенерированный buf для gRPC-Web и Connect. Без клиента и аутентификации:
  для приложений на Node.js используйте `@finam/trade-api`.
- [REST-спецификация](docs/swagger/api.swagger.json) и
  [AsyncAPI для WebSocket](specs/asyncapi/).

## Карта репозитория

```text
proto/                  исходные protobuf-контракты (проекция proto-repo, scope ru)
sdk/python/             публикуемый Python SDK
sdk/node/               публикуемый Node.js SDK
js/                     сырые JS-привязки (@finam/grpc-tradeapi)
go/                     Go-привязки, закоммичены и перегенерируются CI
kotlin/                 Kotlin SDK и примеры
examples/sdk/           точечные примеры на опубликованных SDK
examples/strategies/    полные приложения на опубликованных SDK
docs/swagger/           REST-спецификация, генерируется CI
specs/asyncapi/         спецификация WebSocket API
```

Пространство имён protobuf на проводе — `grpc.tradeapi.v1`. Сгенерированные
привязки — артефакты сборки; контракты в `proto/` приходят из вышестоящего
репозитория и здесь не редактируются.

## Разработка репозитория

Этот раздел для контрибьюторов, а не для пользователей SDK. Установите Node.js
20+, Python 3.10+, `uv`, `just` и `zsh`, затем из корня репозитория:

```sh
just bootstrap
just check
```

`just bootstrap` устанавливает зафиксированные зависимости, настраивает
pre-commit и генерирует привязки. `just check` запускает проверки
форматирования, линтер, проверку типов и тесты без учётных данных для обоих SDK
и всех проектов-примеров. `just format` применяет форматирование, `just generate`
пересобирает привязки после изменения файлов в `proto/`.

После `just bootstrap` примеры используют опубликованные SDK. Чтобы отлаживать
каждый пример против SDK из текущего checkout, не трогая манифесты и lock-файлы:

```sh
just examples-use-local
just examples-status
```

`just examples-use-published` возвращает зафиксированные пакеты. При наличии
`TRADE_API_SECRET` команды `just smoke-examples-local` и
`just smoke-examples-published` запускают ограниченные проверки аутентификации
и стратегий в выбранном режиме. Ни одна из них не выставляет заявки.

### Один файл окружения для всех примеров

Каждый рецепт `just` загружает один игнорируемый git файл `.env` из корня
репозитория, поэтому секрет и общие настройки примеров задаются один раз:

```sh
cp .env.example .env
# Отредактируйте .env, затем:
just env-status
just run-strategy-python sma_crossover --check
just run-strategy-node sma_crossover --check
just run-sdk-python auth_and_account.py
just run-sdk-node auth
```

`just env-status` печатает загруженные настройки и маскирует секрет.
Переменные, уже экспортированные в оболочке, имеют приоритет над файлом,
поэтому `TRADE_API_SYMBOL=GAZP@MISX just run-strategy-node sma_crossover --check`
тоже работает. Сами программы-примеры никогда не читают `.env`: они читают
окружение процесса, и каждый каталог остаётся запускаемым после копирования из
репозитория.

## Релизы

Все SDK репозитория используют одну версию. GitHub Release с «голым» тегом
версии публикует пакеты Python и Node.js, JS-привязки и Kotlin SDK.
Мейнтейнерам следует придерживаться
[общего руководства по выпуску SDK](sdk/node/RELEASING.md).

## Контакты

Официальный сайт Trade API: <https://tradeapi.finam.ru/>.

Чтобы задать вопрос или сообщить о проблеме, напишите в официальный чат
поддержки: «Контакты» → «Чат на сайте». Репозиторий и трекер задач:
<https://github.com/FinamWeb/finam-trade-api>.
