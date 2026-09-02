# Finam Trade API — Node.js SDK

Небольшой функциональный TypeScript SDK для gRPC Trade API Finam.

- одна асинхронная точка входа `createTradeApi()`;
- обычные объекты для запросов — без конструкторов сообщений;
- Promise для унарных RPC и `AsyncIterable` для потоков;
- автоматический выпуск, подстановка и обновление JWT;
- типизированные ошибки и повторы при временных сбоях;
- сгенерированные типы для всего protobuf API.

Пакет отличается от `@finam/grpc-tradeapi` (каталог `js/`): тот содержит
только «сырые» привязки, сгенерированные buf для gRPC-Web и Connect, без
клиента, аутентификации и повторов.

## Установка

Нужен Node.js 20 или новее.

Текущий checkout соответствует версии `2.19.1`:

```sh
npm install @finam/trade-api@2.19.1
```

## Быстрый старт

Первая программа аутентифицируется и печатает ID счетов, видимых секрету. Она
ограничена и не выставляет заявку.

Создайте чистый каталог приложения:

```sh
mkdir finam-node-quickstart
cd finam-node-quickstart
npm init -y
npm install @finam/trade-api@2.19.1
```

Сохраните это как `quickstart.mjs`. Расширение `.mjs` позволяет ESM-импорту
SDK работать без дополнительной настройки проекта:

```ts
import { withTradeApi } from "@finam/trade-api";

const secret = process.env.TRADE_API_SECRET;
if (!secret) throw new Error("Set TRADE_API_SECRET");

await withTradeApi({ secret }, async (api) => {
  const details = await api.auth.tokenDetails({ token: api.getToken() });
  console.log("Available account IDs:", details.accountIds);
});
```

Запустите со своим секретом:

```sh
TRADE_API_SECRET=... node quickstart.mjs
```

Если аутентификация не проходит, убедитесь, что секрет активен. Пустой список
счетов означает, что токен не открывает торговый счёт; он всё ещё может
подходить для рыночных данных, если у него есть соответствующее право.

`withTradeApi()` всегда закрывает канал и поток обновления токена. Когда это
заработает, сохраните ещё один `.mjs`-файл, чтобы получить счёт по одному из
обнаруженных ID:

```ts
import { withTradeApi } from "@finam/trade-api";

const secret = process.env.TRADE_API_SECRET;
if (!secret) throw new Error("Set TRADE_API_SECRET");

await withTradeApi({ secret }, async (api) => {
  const details = await api.auth.tokenDetails({ token: api.getToken() });
  const accountId = details.accountIds[0];
  if (!accountId) throw new Error("This secret exposes no accounts");

  const account = await api.accounts.getAccount({ accountId });
  console.log(account);
});
```

## Подписка на рыночные данные

Серверные потоки — асинхронные итерируемые объекты. Этот пример работает до
Ctrl-C и корректно закрывается через `AbortSignal`:

```ts
import { withTradeApi } from "@finam/trade-api";

const secret = process.env.TRADE_API_SECRET;
if (!secret) throw new Error("Set TRADE_API_SECRET");

const abort = new AbortController();
process.once("SIGINT", () => abort.abort());

await withTradeApi({ secret }, async (api) => {
  for await (const update of api.marketData.subscribeQuote(
    { symbols: ["SBER@MISX"] },
    { signal: abort.signal },
  )) {
    console.log(update);
  }
});
```

В репозитории также есть точечные примеры для
[аутентификации и счетов](../../examples/sdk/node/auth-and-account.ts),
[потока котировок](../../examples/sdk/node/subscribe-quotes.ts) и
[настоящей заявки](../../examples/sdk/node/place-limit-order.ts). Они живут в
[автономном проекте-потребителе](../../examples/sdk/node/), который по умолчанию
устанавливает опубликованный пакет.

## Сервисы

Возвращаемый объект открывает сгенерированные методы напрямую:

| Свойство | Сервис | Примеры |
| --- | --- | --- |
| `auth` | `AuthService` | `tokenDetails` |
| `accounts` | `AccountsService` | `getAccount`, `trades`, `subscribeAccount` |
| `assets` | `AssetsService` | `allAssets`, `getAsset`, `schedule` |
| `corporateActions` | `CorporateActionsService` | сплиты, облигации, дивиденды |
| `marketData` | `MarketDataService` | `bars`, `lastQuote`, потоки котировок/стакана/свечей |
| `orders` | `OrdersService` | выставление, отмена, запрос, потоки заявок/сделок |
| `reports` | `ReportsService` | `createAccountReport`, `getAccountReportInfo` (только российский контур) |
| `metrics` | `UsageMetricsService` | `getUsageMetrics` |

`AuthService` принимает секрет или токен в теле запроса и должен вызываться без
заголовка `Authorization`: сервер отклоняет `tokenDetails`, если заголовок
присутствует. SDK создаёт `api.auth` без этого заголовка, а все остальные
сервисы получают его автоматически.

Поля запросов используют идиоматический lower camel case. TypeScript проверяет
каждый обычный объект по сгенерированному protobuf-типу:

> **Внимание:** следующий вызов выставляет настоящую заявку. Используйте
> выделенный счёт, проверьте ID счёта и параметры заявки и не делайте его первым
> тестом SDK.

```ts
import { OrderType, Side, TimeInForce } from "@finam/trade-api/orders";

const order = await api.orders.placeOrder({
  accountId: "A12345",
  symbol: "SBER@MISX",
  quantity: { value: "1" },
  side: Side.SIDE_BUY,
  type: OrderType.ORDER_TYPE_LIMIT,
  timeInForce: TimeInForce.TIME_IN_FORCE_DAY,
  limitPrice: { value: "280.00" },
  clientOrderId: crypto.randomUUID().replaceAll("-", "").slice(0, 20),
});
```

Сгенерированные типы и enum доступны через импорты по сервисам:

```ts
import type { GetAccountResponse } from "@finam/trade-api/accounts";
import { TimeFrame } from "@finam/trade-api/market-data";
import { OrderType, Side } from "@finam/trade-api/orders";
import type { CreateAccountReportRequest } from "@finam/trade-api/reports";
```

Protobuf-метки времени отображаются в `Date`, 64-битные целые — в `bigint`, а
`google.type.Decimal` представлен как `{ value: string }`.

## Потоки и отмена

Серверные потоки — обычные асинхронные итерируемые объекты. Передайте
`AbortSignal`, чтобы отменить:

```ts
const abort = new AbortController();

process.once("SIGINT", () => abort.abort());

for await (const update of api.marketData.subscribeQuote(
  { symbols: ["SBER@MISX"] },
  { signal: abort.signal },
)) {
  console.log(update);
}
```

Потоки не повторяются автоматически, потому что только приложение знает, как
возобновить их без потери или дублирования событий.

## Жизненный цикл клиента

Используйте `withTradeApi()` для ограниченной работы. В долгоживущем приложении
управляйте клиентом явно и всегда закрывайте его:

```ts
import { createTradeApi } from "@finam/trade-api";

const secret = process.env.TRADE_API_SECRET;
if (!secret) throw new Error("Set TRADE_API_SECRET");

const api = await createTradeApi({ secret });
try {
  const details = await api.auth.tokenDetails({ token: api.getToken() });
  console.log(details.accountIds);
} finally {
  await api.close();
}
```

## Ошибки и повторы

Сбои gRPC автоматически отображаются в подклассы `TradeApiError`: `AuthError`,
`PermissionDeniedError`, `InvalidArgumentError`, `NotFoundError`,
`RateLimitError`, `InternalError`, `ServiceUnavailableError` и
`DeadlineExceededError`.

```ts
import { RateLimitError } from "@finam/trade-api";

try {
  await api.assets.getAsset({ symbol: "UNKNOWN@XXXX" });
} catch (error) {
  if (error instanceof RateLimitError) {
    // Подождите или поставьте запрос в очередь.
  }
  throw error;
}
```

Унарные вызовы по умолчанию повторяют `UNAVAILABLE` три раза с экспоненциальной
задержкой, что соответствует четырём попыткам всего в Python SDK. Отключите
повторы глобально через `retry: false`, настройте политику при создании клиента
или переопределите её для одного вызова:

```ts
await api.orders.placeOrder(order, { retry: false });
```

Для RPC, меняющих состояние, используйте стабильный идентификатор идемпотентности,
например `clientOrderId`, или отключите повторы для этого вызова.

## Локальная разработка

Из `sdk/node`:

```sh
npm ci
npm run format
npm run check
npm run build
npm pack --dry-run
```

Запускайте `npm run generate` при каждом изменении файлов в `../../proto`.
Сгенерированные файлы — артефакты сборки и не коммитятся. Потребителям пакета
`protoc` по-прежнему не нужен, потому что релизы содержат скомпилированный
вывод.

Мейнтейнерам релизов следует придерживаться [RELEASING.md](./RELEASING.md).
