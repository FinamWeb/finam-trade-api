# sendRequest

> Клиент отправляет команды SUBSCRIBE/UNSUBSCRIBE/UNSUBSCRIBE_ALL

**Protocol:** asyncapi | **Type:** publish
**Path:** /ws

## WsRequest

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| action | enum | yes | Действие — SUBSCRIBE, UNSUBSCRIBE, UNSUBSCRIBE_ALL |
| type | enum | no | Тип подписки — ORDERS, TRADES, QUOTES, ORDER_BOOK, BARS, INSTRUMENT_TRADES |
| data | object | no | Данные запроса. Структура зависит от типа подписки. Подробнее в examples |
| token | string | yes | Валидный JWT |

## Response: WsRequest

### SubscribeBars

Подписка на агрегированные свечи

```json
{
  "action": "SUBSCRIBE",
  "type": "BARS",
  "data": {
    "symbol": "SBERF@RTSX",
    "timeframe": "TIME_FRAME_D"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```

### UnsubscribeBars

Закрыть подписку на агрегированные свечи

```json
{
  "action": "UNSUBSCRIBE",
  "type": "BARS",
  "data": {
    "symbol": "SBERF@RTSX",
    "timeframe": "TIME_FRAME_D"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```

### SubscribeOrderBook

Подписка на стакан по инструменту

```json
{
  "action": "SUBSCRIBE",
  "type": "ORDER_BOOK",
  "data": {
    "symbol": "SBERF@RTSX"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```

### UnsubscribeOrderBook

Закрыть подписку на стакан по инструменту

```json
{
  "action": "UNSUBSCRIBE",
  "type": "ORDER_BOOK",
  "data": {
    "symbol": "SBERF@RTSX"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```

### SubscribeQuotes

Подписка на котировки по инструментам

```json
{
  "action": "SUBSCRIBE",
  "type": "QUOTES",
  "data": {
    "symbols": [
      "SBERF@RTSX",
      "OKEY@MISX"
    ]
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```

### UnsubscribeQuotes

Закрыть подписку на котировки по инструментам

```json
{
  "action": "UNSUBSCRIBE",
  "type": "QUOTES",
  "data": {
    "symbols": [
      "SBERF@RTSX",
      "OKEY@MISX"
    ]
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```

### SubscribeLatestTrades

Подписка на сделки по инструментам

```json
{
  "action": "SUBSCRIBE",
  "type": "INSTRUMENT_TRADES",
  "data": {
    "symbol": "SBERF@RTSX"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```

### UnsubscribeLatestTrades

Закрыть подписку на сделки по инструментам

```json
{
  "action": "UNSUBSCRIBE",
  "type": "INSTRUMENT_TRADES",
  "data": {
    "symbol": "SBERF@RTSX"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```

### SubscribeOrders

Подписка на заявки по счету

```json
{
  "action": "SUBSCRIBE",
  "type": "ORDERS",
  "data": {
    "account_id": "00000000"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```

### UnsubscribeOrders

Закрыть подписку на заявки по счету

```json
{
  "action": "UNSUBSCRIBE",
  "type": "ORDERS",
  "data": {
    "account_id": "00000000"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```

### SubscribeTrades

Подписка на сделки по счету

```json
{
  "action": "SUBSCRIBE",
  "type": "TRADES",
  "data": {
    "account_id": "00000000"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```

### UnsubscribeTrades

Закрыть подписку на сделки по счету

```json
{
  "action": "UNSUBSCRIBE",
  "type": "TRADES",
  "data": {
    "account_id": "00000000"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```

### SubscribeAccount

Подписка на изменения по портфелю

```json
{
  "action": "SUBSCRIBE",
  "type": "ACCOUNT",
  "data": {
    "account_id": "00000000"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```

### UnsubscribeAccount

Закрыть подписку на изменения по портфелю

```json
{
  "action": "UNSUBSCRIBE",
  "type": "ACCOUNT",
  "data": {
    "account_id": "00000000"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```

### UnsubscribeAll

Закрыть все подписки

```json
{
  "action": "UNSUBSCRIBE_ALL",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
}
```