# Finam Trade API (WebSocket)

> WebSocket подписки на котировки/сделки/стакан/свечи/заявки.
Клиент шлёт запросы (subscribe/unsubscribe/unsubscribe_all) в виде JSON, сервер отвечает envelope-ами:
- DATA — payload с данными для разных подписок (варианты для BARS, ORDER_BOOK, QUOTES, TRADES, ORDERS)
- ERROR — ошибка (валидация, аутентификация,недоступность upstream и т.п.)
- EVENT — служебные события (HANDSHAKE_SUCCESS, CONNECTION_CLOSED и т.п.)


**Version:** 1.0.0
**Protocol:** asyncapi
**Spec version:** 3.0.0

## Servers

| URL | Protocol | Description |
| --- | --- | --- |
| api.finam.ru:443 | wss | Production WebSocket host |

## Authentication

**AuthorizationHeader** (httpApiKey)
JWT напрямую передается в Authorization HTTP header. Пример - Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ
In: header

**TokenInPayload** (plain)
JWT передаётся в теле сообщения на подписку. См. пример `SubscribeBars`

## tradingInfo

- [sendRequest](/docs/async-api/sendrequest.md): Клиент отправляет команды SUBSCRIBE/UNSUBSCRIBE/UNSUBSCRIBE_ALL
- [envelopeListener](/docs/async-api/envelopelistener.md): Клиент получает информацию в рамках своих подписок, а также служебные события и ошибки

## See also

- [Tokens](/tokens.md): API token management