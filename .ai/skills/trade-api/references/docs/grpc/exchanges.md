# Exchanges

> Получение списка доступных бирж, названия и mic коды

**Protocol:** grpc | **Type:** unary
**Path:** /grpc.tradeapi.v1.assets.AssetsService/Exchanges

Получение списка доступных бирж, названия и mic коды
 Пример HTTP запроса:
 GET /v1/exchanges
 Authorization: <token>

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| exchanges | Exchange[] | yes | Информация о бирже |
| exchanges.mic | string | no | Идентификатор биржи mic |
| exchanges.name | string | no | Наименование биржи |

## Response: OK

### Example

```json
{
  "exchanges": [
    {
      "mic": "string",
      "name": "string"
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
  api.finam.ru:443 grpc.tradeapi.v1.assets.AssetsService/Exchanges
```