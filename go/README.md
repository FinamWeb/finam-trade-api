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

## Как собрать локально

Ниже — шаги, чтобы локально сгенерировать Go-клиента и OpenAPI-спецификацию из `.proto`.

1) Подготовка окружения
- Установите Go и настройте рабочее окружение: см. [Go Wiki](https://go.dev/wiki/#getting-started-with-go).
- Установите `protoc` (Protocol Buffers compiler): см. официальную инструкцию — [Protocol Buffer Compiler Installation](https://grpc.io/docs/protoc-installation).
- Убедитесь, что `$GOBIN` (или `%GOBIN%` на Windows) добавлен в `PATH`. По умолчанию, если `GOBIN` не задан, бинарники ставятся в `$(go env GOPATH)/bin` — добавьте и его в `PATH`.

2) Установка генераторов
- В проекте используется блок `tool` в `go.mod`. Для установки всех требуемых генераторов выполните:
```sh
go install tool
```
В результате в `$GOBIN` появятся бинарники:
- `protoc-gen-grpc-gateway`
- `protoc-gen-openapiv2`
- `protoc-gen-go`
- `protoc-gen-go-grpc`

Проверьте, что утилиты доступны: например, `protoc-gen-go --version` и `protoc --version` выполняются без ошибок.

3) Генерация кода и спецификации
- Запустите следующую команду ИЗ КОРНЯ репозитория:
```sh
protoc \
  --proto_path=proto \
  --go_out=go --go_opt=paths=source_relative \
  --go-grpc_out=go --go-grpc_opt=paths=source_relative \
  --openapiv2_out=docs/swagger \
  --openapiv2_opt=logtostderr=true,allow_merge=true,merge_file_name=api \
  ./proto/grpc/tradeapi/v1/*.proto \
  ./proto/grpc/tradeapi/v1/accounts/*.proto \
  ./proto/grpc/tradeapi/v1/assets/*.proto \
  ./proto/grpc/tradeapi/v1/auth/*.proto \
  ./proto/grpc/tradeapi/v1/marketdata/*.proto \
  ./proto/grpc/tradeapi/v1/orders/*.proto
```

Что получится
- Go-код будет сгенерирован в каталоге `go/grpc/tradeapi/v1/...` (относительно корня репозитория).
- OpenAPI-спецификация будет обновлена/собрана в `docs/swagger/api.swagger.json`.

## Автогенерация

После слияния кода в `main` Go‑код клиента и Swagger автоматически генерируются, есть изменения в `proto`. 