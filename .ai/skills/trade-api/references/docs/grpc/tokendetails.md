# TokenDetails

> Получение информации о токене сессии

**Protocol:** grpc | **Type:** unary
**Path:** /grpc.tradeapi.v1.auth.AuthService/TokenDetails

Получение информации о токене сессии
 Пример HTTP запроса:
 POST /v1/sessions/details
 Content-Type: application/json

 {
   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
 }

 Токен передается в теле запроса для безопасности
 Получение информации о токене. Также включает список доступных счетов.

## Request

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| token | string | no | JWT-токен |

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| created_at | Timestamp | no | Дата и время создания |
| created_at.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| created_at.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |
| expires_at | Timestamp | no | Дата и время экспирации |
| expires_at.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| expires_at.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |
| md_permissions | MDPermission[] | yes | Информация о доступе к рыночным данным |
| md_permissions.quote_level | QuoteLevel | no | Уровень котировок — QUOTE_LEVEL_UNSPECIFIED, QUOTE_LEVEL_LAST_PRICE, QUOTE_LEVEL_BEST_BID_OFFER, QUOTE_LEVEL_DEPTH_OF_MARKET, QUOTE_LEVEL_DEPTH_OF_BOOK, QUOTE_LEVEL_ACCESS_FORBIDDEN |
| md_permissions.delay_minutes | int32 | no | Задержка в минутах |
| md_permissions.mic | string | no | Идентификатор биржи mic |
| md_permissions.country | string | no | Страна |
| md_permissions.continent | string | no | Континент |
| md_permissions.worldwide | bool | no | Весь мир |
| account_ids | string[] | yes | Идентификаторы аккаунтов |
| readonly | bool | no | Сессия и торговые счета в токене будут помечены readonly |

## Response: OK

### Example

```json
{
  "created_at": {
    "seconds": 0,
    "nanos": 0
  },
  "expires_at": {
    "seconds": 0,
    "nanos": 0
  },
  "md_permissions": [
    {
      "quote_level": 0,
      "delay_minutes": 0,
      "mic": "string",
      "country": "string",
      "continent": "string",
      "worldwide": false
    }
  ],
  "account_ids": [
    "string"
  ],
  "readonly": false
}
```

## Code Examples

### grpcurl

```shell
grpcurl \
  -d '{
  "token": "string"
}' \
  api.finam.ru:443 grpc.tradeapi.v1.auth.AuthService/TokenDetails
```