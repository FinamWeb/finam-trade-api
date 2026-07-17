# REST

> API для торговых операций

**Version:** version not set
**Protocol:** rest
**Spec version:** 2.0

## Servers

| URL | Protocol | Description |
| --- | --- | --- |
| https://api.finam.ru |  |  |

## Authentication

**Authorization** (apiKey)
JWT токен авторизации
In: header

## AuthService

- [Auth](/docs/rest/authservice_auth.md): Получение JWT токена из API токена
Пример HTTP запроса:
POST /v1/sessions
Content-Type: application/json
- [TokenDetails](/docs/rest/authservice_tokendetails.md): Получение информации о токене сессии
Пример HTTP запроса:
POST /v1/sessions/details
Content-Type: application/json

## AccountsService

- [GetAccount](/docs/rest/accountsservice_getaccount.md): Получение информации по конкретному аккаунту
Пример HTTP запроса:
GET /v1/accounts/A12345
Authorization: <token>
- [Trades](/docs/rest/accountsservice_trades.md): Получение истории по сделкам аккаунта
Пример HTTP запроса:
GET /v1/accounts/A12345/trades?limit=50&interval.start_time=2023-01-01T00:00:00Z&interval.end_time=2023-01-31T23:59:59Z
Authorization: <token>
- [Transactions](/docs/rest/accountsservice_transactions.md): Получение списка транзакций аккаунта
Пример HTTP запроса:
GET /v1/accounts/A12345/transactions?limit=50&interval.start_time=2023-01-01T00:00:00Z&interval.end_time=2023-01-31T23:59:59Z
Authorization: <token>

## OrdersService

- [GetOrders](/docs/rest/ordersservice_getorders.md): Получение списка заявок для аккаунта
Пример HTTP запроса:
GET /v1/accounts/A12345/orders
Authorization: <token>
- [PlaceOrder](/docs/rest/ordersservice_placeorder.md): Выставление биржевой заявки
Пример HTTP запроса:
POST /v1/accounts/A12345/orders
Content-Type: application/json
Authorization: <token>
- [GetOrder](/docs/rest/ordersservice_getorder.md): Получение информации о конкретном ордере
Пример HTTP запроса:
GET /v1/accounts/A12345/orders/ORD789012
Authorization: <token>
- [CancelOrder](/docs/rest/ordersservice_cancelorder.md): Отмена биржевой заявки
Пример HTTP запроса:
DELETE /v1/accounts/A12345/orders/ORD789012
Authorization: <token>
- [PlaceSLTPOrder](/docs/rest/ordersservice_placesltporder.md): Выставление SL/TP заявки
Пример HTTP запроса:
POST /v1/accounts/A12345/sltp-orders
Content-Type: application/json
Authorization: <token>

## MarketDataService

- [Bars](/docs/rest/marketdataservice_bars.md): Получение исторических данных по инструменту (агрегированные свечи)
Пример HTTP запроса:
GET /v1/instruments/SBER@MISX/bars?timeframe=TIME_FRAME_D&interval.start_time=2023-01-01T00:00:00Z&interval.end_time=2023-01-31T23:59:59Z
Authorization: <token>
- [OrderBook](/docs/rest/marketdataservice_orderbook.md): Получение текущего стакана по инструменту
Пример HTTP запроса:
GET /v1/instruments/SBER@MISX/orderbook
Authorization: <token>
- [LastQuote](/docs/rest/marketdataservice_lastquote.md): Получение последней котировки по инструменту
Пример HTTP запроса:
GET /v1/instruments/SBER@MISX/quotes/latest
Authorization: <token>
- [LatestTrades](/docs/rest/marketdataservice_latesttrades.md): Получение списка последних сделок по инструменту
Пример HTTP запроса:
GET /v1/instruments/SBER@MISX/trades/latest
Authorization: <token>

## AssetsService

- [Assets](/docs/rest/assetsservice_assets.md): Получение списка доступных для торговли инструментов, их описание
Пример HTTP запроса:
GET /v1/assets
Authorization: <token>
- [AllAssets](/docs/rest/assetsservice_allassets.md): Получение списка всех инструментов, в том числе индикативных и архивных, их описание
Пример HTTP запроса:
GET /v1/assets/all?cursor=56658&only_disabled=true
Authorization: <token>
- [Clock](/docs/rest/assetsservice_clock.md): Получение времени на сервере
Пример HTTP запроса:
GET /v1/assets/clock
Authorization: <token>
- [GetAsset](/docs/rest/assetsservice_getasset.md): Получение информации по конкретному инструменту
Пример HTTP запроса:
GET /v1/assets/SBER@MISX?account_id=1440399
Authorization: <token>
- [GetConstituents](/docs/rest/assetsservice_getconstituents.md): Получить состав биржевого индекса по его символу
- [GetAssetParams](/docs/rest/assetsservice_getassetparams.md): Получение торговых параметров по инструменту
Пример HTTP запроса:
GET /v1/assets/SBER@MISX/params?account_id=1440399
Authorization: <token>
- [Schedule](/docs/rest/assetsservice_schedule.md): Получение расписания торгов для инструмента
Пример HTTP запроса:
GET /v1/assets/SBER@MISX/schedule
Authorization: <token>
- [OptionsChain](/docs/rest/assetsservice_optionschain.md): Получение цепочки опционов для базового актива
Пример HTTP запроса:
GET /v1/assets/SBER@MISX/options
Authorization: <token>
- [Exchanges](/docs/rest/assetsservice_exchanges.md): Получение списка доступных бирж, названия и mic коды
Пример HTTP запроса:
GET /v1/exchanges
Authorization: <token>

## UsageMetricsService

- [GetUsageMetrics](/docs/rest/usagemetricsservice_getusagemetrics.md): Получение текущих метрик использования для пользователя
Пример HTTP запроса:
GET /v1/usage
Authorization: <token>

## ReportsService

- [CreateAccountReport](/docs/rest/reportsservice_createaccountreport.md): Запустить генерацию отчета по счету за период
Пример HTTP запроса:
POST /v1/report
Authorization: <token>
- [GetAccountReportInfo](/docs/rest/reportsservice_getaccountreportinfo.md): Получение информации о результате генерации отчета по счету
Пример HTTP запроса:
GET /v1/report/01KBMPQ3CEZ4BBCVGBW5JS8S8Y/info
Authorization: <token>

## CorporateActionsService

- [GetFutureBondsEvents](/docs/rest/corporateactionsservice_getfuturebondsevents.md): Получить календарь будущих событий по облигациям
- [GetPastBondsEvents](/docs/rest/corporateactionsservice_getpastbondsevents.md): Получить календарь исторических событий по облигациям
- [GetFutureDividends](/docs/rest/corporateactionsservice_getfuturedividends.md): Получить список предстоящих (будущих) дивидендных выплат по инструменту.
- [GetPastDividends](/docs/rest/corporateactionsservice_getpastdividends.md): Получить исторические данные по выплаченным дивидендам инструмента
- [GetFutureSplits](/docs/rest/corporateactionsservice_getfuturesplits.md): Получить предстоящие события сплитов по инструменту
- [GetPastSplits](/docs/rest/corporateactionsservice_getpastsplits.md): Получить историю сплитов по инструменту

## See also

- [Tokens](/tokens.md): API token management