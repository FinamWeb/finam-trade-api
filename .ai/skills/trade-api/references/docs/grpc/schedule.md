# Schedule

> Получение расписания торгов для инструмента

**Protocol:** grpc | **Type:** unary
**Path:** /grpc.tradeapi.v1.assets.AssetsService/Schedule

Получение расписания торгов для инструмента
 Пример HTTP запроса:
 GET /v1/assets/SBER@MISX/schedule
 Authorization: <token>

## Request

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| symbol | string | no | Символ инструмента |

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| symbol | string | no | Символ инструмента |
| sessions | Sessions[] | yes | Сессии инструмента |
| sessions.type | string | no |  |
| sessions.interval | Interval | no |  |
| sessions.interval.start_time | Timestamp | no | Optional. Inclusive start of the interval.

 If specified, a Timestamp matching this interval will have to be the same
 or after the start. |
| sessions.interval.start_time.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| sessions.interval.start_time.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |
| sessions.interval.end_time | Timestamp | no | Optional. Exclusive end of the interval.

 If specified, a Timestamp matching this interval will have to be before the
 end. |
| sessions.interval.end_time.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| sessions.interval.end_time.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |

## Response: OK

### Example

```json
{
  "symbol": "string",
  "sessions": [
    {
      "type": "string",
      "interval": {
        "start_time": {
          "seconds": 0,
          "nanos": 0
        },
        "end_time": {
          "seconds": 0,
          "nanos": 0
        }
      }
    }
  ]
}
```

## Code Examples

### grpcurl

```shell
TOKEN=$(grpcurl \
  -d '{
  "secret": "YOUR_API_TOKEN"
}' \
  api.finam.ru:443 grpc.tradeapi.v1.auth.AuthService/Auth | jq -r '.token')

grpcurl \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
  "symbol": "string"
}' \
  api.finam.ru:443 grpc.tradeapi.v1.assets.AssetsService/Schedule
```