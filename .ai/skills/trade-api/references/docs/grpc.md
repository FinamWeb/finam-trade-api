# Trade API

**Protocol:** grpc

## Servers

| URL | Protocol | Description |
| --- | --- | --- |
| api.finam.ru | gRPC | production |

## Authentication

**jwt-token** (apiKey)
In: metadata

## AuthService

- [Auth](/docs/grpc/auth.md): Получение JWT токена из API токена
- [TokenDetails](/docs/grpc/tokendetails.md): Получение информации о токене сессии
- [SubscribeJwtRenewal](/docs/grpc/subscribejwtrenewal.md): Подписка на обновление JWT токена. Стрим метод

## AccountsService

- [GetAccount](/docs/grpc/getaccount.md): Получение информации по конкретному аккаунту
- [Trades](/docs/grpc/trades.md): Получение истории по сделкам аккаунта
- [Transactions](/docs/grpc/transactions.md): Получение списка транзакций аккаунта
- [SubscribeAccount](/docs/grpc/subscribeaccount.md): Подписка на информацию по аккаунту. Стрим метод

## OrdersService

- [PlaceOrder](/docs/grpc/placeorder.md): Выставление биржевой заявки
- [CancelOrder](/docs/grpc/cancelorder.md): Отмена биржевой заявки
- [GetOrders](/docs/grpc/getorders.md): Получение списка заявок для аккаунта
- [GetOrder](/docs/grpc/getorder.md): Получение информации о конкретном ордере
- [SubscribeOrderTrade](/docs/grpc/subscribeordertrade.md): Подписка на собственные заявки и сделки. Стрим метод
- [SubscribeOrders](/docs/grpc/subscribeorders.md): Подписка на собственные заявки. Стрим метод
- [SubscribeTrades](/docs/grpc/subscribetrades.md): Подписка на собственные сделки. Стрим метод
- [PlaceSLTPOrder](/docs/grpc/placesltporder.md): Выставление SL/TP заявки

## MarketDataService

- [Bars](/docs/grpc/bars.md): Получение исторических данных по инструменту (агрегированные свечи)
- [LastQuote](/docs/grpc/lastquote.md): Получение последней котировки по инструменту
- [OrderBook](/docs/grpc/orderbook.md): Получение текущего стакана по инструменту
- [LatestTrades](/docs/grpc/latesttrades.md): Получение списка последних сделок по инструменту
- [SubscribeQuote](/docs/grpc/subscribequote.md): Подписка на котировки по инструменту. Стрим метод
- [SubscribeOrderBook](/docs/grpc/subscribeorderbook.md): Подписка на стакан по инструменту. Стрим метод
- [SubscribeLatestTrades](/docs/grpc/subscribelatesttrades.md): Подписка на сделки по инструменту. Стрим метод
- [SubscribeBars](/docs/grpc/subscribebars.md): Подписка на агрегированные свечи. Стрим метод

## AssetsService

- [Exchanges](/docs/grpc/exchanges.md): Получение списка доступных бирж, названия и mic коды
- [Assets](/docs/grpc/assets.md): Получение списка доступных для торговли инструментов, их описание
- [AllAssets](/docs/grpc/allassets.md): Получение списка всех инструментов, в том числе индикативных и архивных, их описание
- [GetAsset](/docs/grpc/getasset.md): Получение информации по конкретному инструменту
- [GetAssetParams](/docs/grpc/getassetparams.md): Получение торговых параметров по инструменту
- [OptionsChain](/docs/grpc/optionschain.md): Получение цепочки опционов для базового актива
- [Schedule](/docs/grpc/schedule.md): Получение расписания торгов для инструмента
- [Clock](/docs/grpc/clock.md): Получение времени на сервере
- [GetConstituents](/docs/grpc/getconstituents.md): Получить состав биржевого индекса по его символу

## UsageMetricsService

- [GetUsageMetrics](/docs/grpc/getusagemetrics.md): Получение текущих метрик использования для пользователя

## ReportsService

- [CreateAccountReport](/docs/grpc/createaccountreport.md): Запустить генерацию отчета по счету за период
- [GetAccountReportInfo](/docs/grpc/getaccountreportinfo.md): Получение информации о результате генерации отчета по счету
- [SubscribeAccountReportInfo](/docs/grpc/subscribeaccountreportinfo.md): Подписка на информацию о результатах генерации отчета по счету. Стрим метод

## CorporateActionsService

- [GetFutureSplits](/docs/grpc/getfuturesplits.md): Получить предстоящие события сплитов по инструменту
- [GetPastSplits](/docs/grpc/getpastsplits.md): Получить историю сплитов по инструменту
- [GetFutureBondsEvents](/docs/grpc/getfuturebondsevents.md): Получить календарь будущих событий по облигациям
- [GetPastBondsEvents](/docs/grpc/getpastbondsevents.md): Получить календарь исторических событий по облигациям
- [GetFutureDividends](/docs/grpc/getfuturedividends.md): Получить список предстоящих (будущих) дивидендных выплат по инструменту.
- [GetPastDividends](/docs/grpc/getpastdividends.md): Получить исторические данные по выплаченным дивидендам инструмента

## See also

- [Tokens](/tokens.md): API token management