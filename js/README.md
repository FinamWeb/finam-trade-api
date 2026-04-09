# Клиент к Finam Trade API для JavaScript

Клиентский пакет для Finam Trade API, сгенерированный из .proto на основе [buf](https://buf.build)

## Установка

```sh
npm install @finam/grpc-tradeapi @connectrpc/connect @connectrpc/connect-web
```

## Быстрый старт

```javascript
import { createGrpcWebTransport } from '@connectrpc/connect-web';
import { createClient } from '@connectrpc/connect';
import { AuthService } from '@finam/grpc-tradeapi/grpc/tradeapi/v1/auth/auth_service_pb';
import { AccountsService } from '@finam/grpc-tradeapi/grpc/tradeapi/v1/accounts/accounts_service_pb';

const transport = createGrpcWebTransport({
  baseUrl: 'https://api.finam.ru',
});

// Создаем клиент AuthService
const authClient = createClient(AuthService, transport);

// Выполняем аутентификацию
const authResponse = await authClient.auth({ secret: 'YOUR_TOKEN' });
const token = authResponse.token;

// Используем токен для дальнейших запросов
const headers = { authorization: token };

// Теперь можно использовать другие сервисы, например AccountsService
const accountsClient = createClient(AccountsService, transport);

const accountResponse = await accountsClient.getAccount({ accountId: 'A12345' }, { headers });

console.log(accountResponse);
```

Подключайте и используйте другие сервисы аналогично, импортируя их из `@finam/grpc-tradeapi`.
