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
