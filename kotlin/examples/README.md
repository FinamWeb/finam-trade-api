# Finam Trade API Kotlin Examples

## Обзор

Этот репозиторий содержит примеры использования Finam Trade API на языке Kotlin.

## Получение секретного ключа

Для аутентификации в API и запуска тестов вам потребуется секретный ключ. 

1.  Перейдите на портал [Finam Trade API](https://tradeapi.finam.ru/docs/tokens/).
2.  Следуйте инструкциям для создания нового ключа API (secret key).
3.  Скопируйте полученный ключ. Он понадобится вам для запуска примеров.

## Тестирование

В качестве примера предоставляется базовый тест, который демонстрирует основной цикл работы с API: аутентификация и получение данных.

### `GetAccount`

Этот тест выполняет следующие шаги:

1.  **Аутентификация:** Используя предоставленный секретный ключ (`secret`), тест отправляет запрос на эндпоинт `/v1/auth` для получения JWT-токена.
2.  **Запрос данных:** Полученный токен используется для аутентификации запроса на эндпоинт `/v1/accounts/{account_id}` для получения информации о счете.
3.  **Проверка:** Тест проверяет, что ответ успешен и содержит ожидаемые данные.

### Запуск

Для запуска вам необходимо:
1. выбрать пример для запуска.
2. передать ваш секретный ключ, созданный ранее, в качестве переменной окружения.

**macOS/Linux:**
```bash
export FINAM_SECRET_KEY="your-secret-key"
export APP_MAIN_CLASS=example.GetAccount
./gradlew :example:run
```

**Windows (Command Prompt):**
```cmd
set FINAM_SECRET_KEY="your-secret-key"
set APP_MAIN_CLASS="example.GetAccount"
gradlew.bat :example:run
```

**Windows (PowerShell):**
```powershell
$env:FINAM_SECRET_KEY="your-secret-key"
$env:APP_MAIN_CLASS="example.GetAccount"
./gradlew :example:run
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
1. Получение jwt токена на основании секретного ключа из переменной окружения `FINAM_SECRET_KEY`
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
2. Перед запуском метода `main` нажмите `Modify run configuration..`, в поле `Environment variables` добавить переменную окружения `FINAM_SECRET_KEY="your-secret-key"`
3. Запустите метод `main`

#### Терминал
Аналогично примеру выше для `GetAccount` (с учетом OS) задайте переменные окружения `FINAM_SECRET_KEY`, `APP_MAIN_CLASS` и запустите пример
```bash
export FINAM_SECRET_KEY="your-secret-key"
export APP_MAIN_CLASS="example.ws.SubscribeBars"
./gradlew run
```