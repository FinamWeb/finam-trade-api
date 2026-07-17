# GetConstituents

> Получить состав биржевого индекса по его символу

**Protocol:** grpc | **Type:** unary
**Path:** /grpc.tradeapi.v1.assets.AssetsService/GetConstituents

## Request

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| symbol | string | no | Символьный код индекса (например, "SPX@_SP", "NDX@_SCI") |
| cursor | int64 | no | Курсор для пагинации. Указывает sec_id инструмента, с которого должен начинаться список.
 Для первого запроса оставьте поле пустым (значение 0).
 Для последующих запросов используйте значение next_cursor из предыдущего ответа. |

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| constituents | Constituents[] | yes | Список компонентов (ценных бумаг), входящих в базу расчета запрошенного индекса |
| constituents.symbol | string | no | Символьный код инструмента |
| constituents.name | string | no | Полное наименование компании-эмитента |
| constituents.sector | string | no | Глобальный сектор экономики, к которому относится компания (например, "Technology", "Healthcare") |
| constituents.sub_sector | string | no | Отрасль (подотрасль) деятельности компании (например, "Software - Application") |
| constituents.cik | string | no | Уникальный идентификатор компании в базе данных SEC США (Central Index Key) |
| constituents.index_inclusion_date | Date | no | Дата добавления бумаги в индекс |
| constituents.index_inclusion_date.year | int32 | no | Year of the date. Must be from 1 to 9999, or 0 to specify a date without
 a year. |
| constituents.index_inclusion_date.month | int32 | no | Month of a year. Must be from 1 to 12, or 0 to specify a year without a
 month and day. |
| constituents.index_inclusion_date.day | int32 | no | Day of a month. Must be from 1 to 31 and valid for the year and month, or 0
 to specify a year by itself or a year and month where the day isn't
 significant. |
| next_cursor | int64 | no | Курсор для получения следующей страницы. Содержит sec_id последнего инструмента в текущем списке.
 Передайте это значение в поле cursor следующего запроса, чтобы получить следующую часть данных.
 Если значение 0 или отсутствует — это последняя страница |

## Response: OK

### Example

```json
{
  "constituents": [
    {
      "symbol": "string",
      "name": "string",
      "sector": "string",
      "sub_sector": "string",
      "cik": "string",
      "index_inclusion_date": {
        "year": 0,
        "month": 0,
        "day": 0
      }
    }
  ],
  "next_cursor": 0
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
  "symbol": "string",
  "cursor": 0
}' \
  api.finam.ru:443 grpc.tradeapi.v1.assets.AssetsService/GetConstituents
```