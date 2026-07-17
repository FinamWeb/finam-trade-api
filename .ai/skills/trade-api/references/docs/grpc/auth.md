# Auth

> Получение JWT токена из API токена

**Protocol:** grpc | **Type:** unary
**Path:** /grpc.tradeapi.v1.auth.AuthService/Auth

Получение JWT токена из API токена
 Пример HTTP запроса:
 POST /v1/sessions
 Content-Type: application/json

 {
   "secret": "your-api-secret-key"
 }

 Все поля передаются в теле запроса

## Request

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| secret | string | no | API токен (secret key) |
| source_app_id | string | no | Идентификатор приложения-источника запроса |

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| token | string | no | Полученный JWT-токен |

## Response: OK

### Example

```json
{
  "token": "string"
}
```

## Code Examples

### grpcurl

```shell
grpcurl \
  -d '{
  "secret": "string",
  "source_app_id": "string"
}' \
  api.finam.ru:443 grpc.tradeapi.v1.auth.AuthService/Auth
```