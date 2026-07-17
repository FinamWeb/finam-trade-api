# CreateAccountReport

> Запустить генерацию отчета по счету за период

**Protocol:** grpc | **Type:** unary
**Path:** /grpc.tradeapi.v1.reports.ReportsService/CreateAccountReport

Запустить генерацию отчета по счету за период
 Пример HTTP запроса:
 POST /v1/report
 Authorization: <token>

## Request

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| date_range | DateRange | no | Временной интервал. Максимальный интервал дат - 92 дня |
| date_range.date_begin | Timestamp | no | Дата начала временного интервала |
| date_range.date_begin.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| date_range.date_begin.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |
| date_range.date_end | Timestamp | no | Дата конца временного интервала |
| date_range.date_end.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| date_range.date_end.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |
| report_form | ReportForm | no | Форма отчета — REPORT_FORM_UNKNOWN, REPORT_FORM_SHORT, REPORT_FORM_LONG |
| account_id | int64 | no | Идентификатор счета |

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| report_id | string | no | Идентификатор отчёта |

## Response: OK

### Example

```json
{
  "report_id": "string"
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
  "date_range": {
    "date_begin": {
      "seconds": 0,
      "nanos": 0
    },
    "date_end": {
      "seconds": 0,
      "nanos": 0
    }
  },
  "report_form": 0,
  "account_id": 0
}' \
  api.finam.ru:443 grpc.tradeapi.v1.reports.ReportsService/CreateAccountReport
```