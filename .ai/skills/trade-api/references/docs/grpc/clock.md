# Clock

> Получение времени на сервере

**Protocol:** grpc | **Type:** unary
**Path:** /grpc.tradeapi.v1.assets.AssetsService/Clock

Получение времени на сервере
 Пример HTTP запроса:
 GET /v1/assets/clock
 Authorization: <token>

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| timestamp | Timestamp | no | Метка времени |
| timestamp.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| timestamp.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |

## Response: OK

### Example

```json
{
  "timestamp": {
    "seconds": 0,
    "nanos": 0
  }
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
  api.finam.ru:443 grpc.tradeapi.v1.assets.AssetsService/Clock
```