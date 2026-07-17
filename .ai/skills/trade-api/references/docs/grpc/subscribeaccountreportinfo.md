# SubscribeAccountReportInfo

> Подписка на информацию о результатах генерации отчета по счету. Стрим метод

**Protocol:** grpc | **Type:** server-stream
**Path:** /grpc.tradeapi.v1.reports.ReportsService/SubscribeAccountReportInfo

## Request

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| report_id | string | no | Идентификатор отчёта |

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| info | AccountReportInfo | no | Информация о статусе генерации отчёта |
| info.report_id | string | no | Идентификатор отчёта |
| info.status | ReportCreationStatus | no | Статус генерации отчёта — NOT_FOUND, PENDING, IN_PROGRESS, SUCCESS, ERROR |
| info.date_range | DateRange | no | Временной интервал отчёта. Берётся из запроса на генерацию отчёта |
| info.date_range.date_begin | Timestamp | no | Дата начала временного интервала |
| info.date_range.date_begin.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| info.date_range.date_begin.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |
| info.date_range.date_end | Timestamp | no | Дата конца временного интервала |
| info.date_range.date_end.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| info.date_range.date_end.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |
| info.report_form | ReportForm | no | Форма отчета. Берётся из запроса на генерацию отчёта — REPORT_FORM_UNKNOWN, REPORT_FORM_SHORT, REPORT_FORM_LONG |
| info.account_id | int64 | no | Идентификатор счета. Берётся из запроса на генерацию отчёта |
| info.url | StringValue | no | Ссылка на скачивание отчёта. Появляется только в случае успешной генерации отчёта (ReportCreationStatus = SUCCESS). Для скачивания отчёта по данной ссылке необходимо передать заголовок Authorization: Bearer <your_access_key> |
| info.url.value | string | no | The string value. |

## Response: OK

### Example

```json
{
  "info": {
    "report_id": "string",
    "status": 0,
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
    "account_id": 0,
    "url": {
      "value": "string"
    }
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
  -d '{
  "report_id": "string"
}' \
  api.finam.ru:443 grpc.tradeapi.v1.reports.ReportsService/SubscribeAccountReportInfo
```