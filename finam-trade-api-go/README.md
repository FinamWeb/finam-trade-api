<h1>Finam trade api GO</h1>

### О проекте
Сборка GO и OpenApiSwagger для Finam Trade API.

### Как собрать локально

Предполагается, что Go установлен и прописана переменная окружения $GOPATH. Документация по GO:  [Go Wiki](https://go.dev/wiki/#getting-started-with-go)
* Запустить команду. 
    ```sh
    go install tool
    ```
    Это поместит четыре двоичных файла в ваш `$GOBIN`;
    
    - `protoc-gen-grpc-gateway`
    - `protoc-gen-openapiv2`
    - `protoc-gen-go`
    - `protoc-gen-go-grpc`
  
    Убедитесь, что ваш `$GOBIN` файл находится в вашем $PATH
* Удостоверится, что установлен protobuf-compiler [Protocol Buffer Compiler Installation](https://grpc.io/docs/protoc-installation)
    Это можно сделать на linux простой командой
    ```shell
    sudo apt update
    sudo apt install protobuf-compiler
    ```   
* Запустить команду 
    ```sh
    ./gradlew generateGoPackage
    ```
    Эта команда запустит сборку Go прото-фалов в директории `../proto`. Все файлы сгенерируются в `/go`.

### Как вносить изменения

1) Внести изменения в `proto`
2) Установить зависимости локально и запустить `./gradlew generateGoPackage`
3) Сделать commit с изменениями

