# GetUsageMetrics

> Получение текущих метрик использования для пользователя

**Protocol:** grpc | **Type:** unary
**Path:** /grpc.tradeapi.v1.metrics.UsageMetricsService/GetUsageMetrics

Получение текущих метрик использования для пользователя
 Пример HTTP запроса:
 GET /v1/usage
 Authorization: <token>

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| quotas | QuotaUsage[] | yes | Список текущих квот и их использование. |
| quotas.name | string | no |  |
| quotas.limit | int64 | no |  |
| quotas.remaining | int64 | no |  |
| quotas.reset_time | Timestamp | no |  |
| quotas.reset_time.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| quotas.reset_time.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |

## Response: OK

### Example

```json
{
  "quotas": [
    {
      "name": "string",
      "limit": 0,
      "remaining": 0,
      "reset_time": {
        "seconds": 0,
        "nanos": 0
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
  api.finam.ru:443 grpc.tradeapi.v1.metrics.UsageMetricsService/GetUsageMetrics
```