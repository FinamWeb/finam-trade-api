# Finam Trade API Kotlin Examples

## Обзор

Gradle-модуль `examples` содержит примеры использования Kotlin SDK Finam Trade API
(модуль `sdk`, артефакт `ru.finam.tradeapi:finam-trade-api-kotlin`).

## Подключение SDK в свой проект

SDK публикуется в Maven Central. Версия совпадает с версией остальных SDK
репозитория (`kotlin/gradle.properties`):

```kotlin
// build.gradle.kts
repositories {
    mavenCentral()
}

dependencies {
    implementation("ru.finam.tradeapi:finam-trade-api-kotlin:2.24.0")
}
```

## Получение секретного ключа

Для аутентификации в API и запуска примеров вам потребуется секретный ключ. 

1.  Перейдите на портал [Finam Trade API](https://tradeapi.finam.ru/docs/tokens/).
2.  Следуйте инструкциям для создания нового ключа API (secret key).
3.  Скопируйте полученный ключ. Он понадобится вам для запуска примеров.

## Тестирование

В качестве примера предоставляется базовый тест, который демонстрирует основной цикл работы с API: аутентификация и получение данных.

### `GetAccount`

Этот тест выполняет следующие шаги:

1.  **Аутентификация:** клиент SDK (`tradeAPIClient`) обменивает секретный ключ (`secret`) на JWT через gRPC-метод `AuthService.Auth` и затем продлевает его через `SubscribeJwtRenewal`; REST-эндпоинт `/v1/auth` не используется.
2.  **Запрос данных:** для каждого счёта из `TokenDetails` вызывается gRPC-метод `AccountsService.GetAccount` с JWT в заголовке `Authorization`.
3.  **Проверка:** Тест проверяет, что ответ успешен и содержит ожидаемые данные.

### Запуск

Команды ниже выполняются из каталога `kotlin/`. Для запуска вам необходимо:
1. выбрать пример для запуска.
2. передать ваш секретный ключ, созданный ранее, в переменной окружения `TRADE_API_SECRET` —
   как и во всех остальных SDK репозитория. Старое имя `FINAM_SECRET_KEY` пока
   поддерживается как запасной вариант.

**macOS/Linux:**
```bash
export TRADE_API_SECRET="your-secret-key"
export APP_MAIN_CLASS=example.GetAccount
./gradlew :examples:run
```

**Windows (Command Prompt):**
```cmd
set TRADE_API_SECRET="your-secret-key"
set APP_MAIN_CLASS="example.GetAccount"
gradlew.bat :examples:run
```

**Windows (PowerShell):**
```powershell
$env:TRADE_API_SECRET="your-secret-key"
$env:APP_MAIN_CLASS="example.GetAccount"
./gradlew :examples:run
```

Замените `"your-secret-key"` на ваш реальный ключ API.

## WebSocket
Примеры websocket подписок расположены в `example.ws`:
- [SubscribeBars.kt](src/main/kotlin/example/ws/SubscribeBars.kt) - подписка на агрегированные свечи по инструменту
- [SubscribeLatestTrades.kt](src/main/kotlin/example/ws/SubscribeLatestTrades.kt) - подписка на сделки по инструменту
- [SubscribeOrderBook.kt](src/main/kotlin/example/ws/SubscribeOrderBook.kt) - подписка на стакан по инструменту
- [SubscribeQuotes.kt](src/main/kotlin/example/ws/SubscribeQuotes.kt) - подписка на котировки по инструменту
- [SubscribeOrders.kt](src/main/kotlin/example/ws/SubscribeOrders.kt) - подписка на собственные заявки
- [SubscribeTrades.kt](src/main/kotlin/example/ws/SubscribeTrades.kt) - подписка на собственные сделки
- [SubscribeAccount.kt](src/main/kotlin/example/ws/SubscribeAccount.kt) - подписка на информацию по аккаунту
- [SubscribeBarsWithoutAuthorizationHeader.kt](src/main/kotlin/example/ws/SubscribeBarsWithoutAuthorizationHeader.kt) - пример подписки без передачи токена в Authorization header

Сценарий каждого примера состоит из следующих шагов:
1. Получение jwt токена на основании секретного ключа из переменной окружения `TRADE_API_SECRET`
2. Создание вебсокет соединения
3. Ожидание хэндшейка
4. Оформление подписки
5. Логировние данных, на которые была подписка
6. Отмена подписки
7. Закрытие соединения

### Запуск
На примере [SubscribeBars.kt](src/main/kotlin/example/ws/SubscribeBars.kt).

Предполагается, что секретный ключ (далее `your-secret-key`) уже выпущен в соответствии с инструкцией выше.

#### IntelliJ IDEA
1. Выберите класс [SubscribeBars.kt](src/main/kotlin/example/ws/SubscribeBars.kt)
2. Перед запуском метода `main` нажмите `Modify run configuration..`, в поле `Environment variables` добавить переменную окружения `TRADE_API_SECRET="your-secret-key"`
3. Запустите метод `main`

#### Терминал
Аналогично примеру выше для `GetAccount` (с учетом OS) задайте переменные окружения `TRADE_API_SECRET`, `APP_MAIN_CLASS` и запустите пример
```bash
export TRADE_API_SECRET="your-secret-key"
export APP_MAIN_CLASS="example.ws.SubscribeBars"
./gradlew :examples:run
```