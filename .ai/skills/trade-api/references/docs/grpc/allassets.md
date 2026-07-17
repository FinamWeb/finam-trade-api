# AllAssets

> Получение списка всех инструментов, в том числе индикативных и архивных, их описание

**Protocol:** grpc | **Type:** unary
**Path:** /grpc.tradeapi.v1.assets.AssetsService/AllAssets

Получение списка всех инструментов, в том числе индикативных и архивных, их описание
 Пример HTTP запроса:
 GET /v1/assets/all?cursor=56658&only_disabled=true
 Authorization: <token>

## Request

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| cursor | int64 | no | Курсор для пагинации. Указывает sec_id инструмента, с которого должен начинаться список.
 Для первого запроса оставьте поле пустым (значение 0).
 Для последующих запросов используйте значение next_cursor из предыдущего ответа. |
| only_active | bool | no | Фильтрация по статусу инструмента: выбираются только активные(неархивные) инструменты
 По умолчанию: false. |
| only_disabled | bool | no | Фильтрация по статусу инструмента: выбираются только неактивные(архивные) инструменты
 По умолчанию: false. |

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| assets | Asset[] | yes | Часть списка инструментов |
| assets.symbol | string | no | Символ инструмента ticker@mic |
| assets.id | string | no | Идентификатор инструмента |
| assets.ticker | string | no | Тикер инструмента |
| assets.mic | string | no | mic идентификатор биржи |
| assets.isin | string | no | Isin идентификатор инструмента |
| assets.type | string | no | Тип инструмента |
| assets.name | string | no | Наименование инструмента |
| assets.is_archived | bool | no | Архивный инструмент или нет |
| next_cursor | int64 | no | Курсор для получения следующей страницы. Содержит sec_id последнего инструмента в текущем списке.
 Передайте это значение в поле cursor следующего запроса, чтобы получить следующую часть данных.
 Если значение 0 или отсутствует — это последняя страница. |

## Response: OK

### Example

```json
{
  "assets": [
    {
      "symbol": "string",
      "id": "string",
      "ticker": "string",
      "mic": "string",
      "isin": "string",
      "type": "string",
      "name": "string",
      "is_archived": false
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
  "cursor": 0,
  "only_active": false,
  "only_disabled": false
}' \
  api.finam.ru:443 grpc.tradeapi.v1.assets.AssetsService/AllAssets
```