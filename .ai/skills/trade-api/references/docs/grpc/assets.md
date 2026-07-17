# Assets

> Получение списка доступных для торговли инструментов, их описание

**Protocol:** grpc | **Type:** unary
**Path:** /grpc.tradeapi.v1.assets.AssetsService/Assets

Получение списка доступных для торговли инструментов, их описание
 Пример HTTP запроса:
 GET /v1/assets
 Authorization: <token>

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| assets | Asset[] | yes | Информация об инструменте |
| assets.symbol | string | no | Символ инструмента ticker@mic |
| assets.id | string | no | Идентификатор инструмента |
| assets.ticker | string | no | Тикер инструмента |
| assets.mic | string | no | mic идентификатор биржи |
| assets.isin | string | no | Isin идентификатор инструмента |
| assets.type | string | no | Тип инструмента |
| assets.name | string | no | Наименование инструмента |
| assets.is_archived | bool | no | Архивный инструмент или нет |

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
  api.finam.ru:443 grpc.tradeapi.v1.assets.AssetsService/Assets
```