# Клиент к Finam Trade API для Go

Клиентский пакет для Finam Trade API, сгенерированные из .proto.

## Установка

Команда установки последней версии:

```sh
go get github.com/FinamWeb/finam-trade-api/go@latest
```

## Быстрый старт

Ниже — минимальный пример подключения к gRPC‑эндпоинту и вызова метода через сгенерированный клиент. Конкретные методы и сообщения берите из импортируемых пакетов.

```go
package main

import (
    "context"
    "log"
    "time"

    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
    "google.golang.org/grpc/metadata"

    "github.com/FinamWeb/finam-trade-api/go/grpc/tradeapi/v1/accounts"
)

func main() {
    // Адрес gRPC‑сервера Finam Trade API
    grpcAddr := "api.finam.ru:443" // замените на актуальный

    // Создаем соединение (используйте TLS cred'ы вместо insecure при реальной работе)
    conn, err := grpc.NewClient(
        grpcAddr,
        grpc.WithTransportCredentials(insecure.NewCredentials()),
    )
    if err != nil {
        log.Fatalf("dial failed: %v", err)
    }
    defer conn.Close()

    // Токен авторизации (например, Bearer)
    token := "YOUR_TOKEN"

    // Контекст с метаданными авторизации
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    ctx = metadata.AppendToOutgoingContext(ctx, "Authorization", token)

    // Создаем клиент нужного сервиса, например AccountsService
    accClient := accounts.NewAccountsServiceClient(conn)

    // Пример вызова метода (заполните запрос своими данными)
    // req := &accounts.GetAccountRequest{AccountId: "A12345"}
    // resp, err := accClient.GetAccount(ctx, req)
    // if err != nil {
    //     log.Fatalf("GetAccount error: %v", err)
    // }
    // log.Printf("Account: %+v", resp)
}
```

Подключайте и используйте другие сервисы аналогично, импортируя соответствующие пакеты из каталога `grpc/tradeapi/v1`.
