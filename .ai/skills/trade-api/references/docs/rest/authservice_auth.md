# Auth

> Получение JWT токена из API токена
Пример HTTP запроса:
POST /v1/sessions
Content-Type: application/json

**Protocol:** rest | **Type:** post
**Path:** /v1/sessions

{
  "secret": "your-api-secret-key"
}

Все поля передаются в теле запроса

## Request Body

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| secret | string | no |  |
| source_app_id | string | no |  |

## Response: 200

A successful response.

### Example

```json
{
  "token": "string"
}
```

## Response: 401

Срок действия токена истек или токен недействителен

## Response: 404

Счёт не был найден в токене

## Response: 429

Слишком много запросов. Доступный лимит - 200 запросов в минуту

## Response: 500

Внутренняя ошибка сервиса. Попробуйте позже

## Response: 503

Сервис на данный момент не доступен. Попробуйте позже

## Response: 504

Крайний срок истек до завершения операции

## Response: default

An unexpected error response.

### Example

```json
{
  "code": 0,
  "message": "string",
  "details": [
    {
      "@type": "string"
    }
  ]
}
```

## Code Examples

### JavaScript

```javascript
const response = await fetch('https://api.finam.ru/v1/sessions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    "secret": "string",
    "source_app_id": "string"
  })
});
const data = await response.json();
```

### Python

```python
import requests

response = requests.post(
    "https://api.finam.ru/v1/sessions",
    headers={
        "Content-Type": "application/json"
    },
    json={
    "secret": "string",
    "source_app_id": "string"
}
)
data = response.json()
```

### Go

```go
package main

import (
    "bytes"
    "fmt"
    "io"
    "net/http"
)

func main() {
    body := []byte(`{
  "secret": "string",
  "source_app_id": "string"
}`)
    req, _ := http.NewRequest("POST", "https://api.finam.ru/v1/sessions", bytes.NewBuffer(body))
    req.Header.Set("Content-Type", "application/json")
    resp, _ := http.DefaultClient.Do(req)
    defer resp.Body.Close()
    respBody, _ := io.ReadAll(resp.Body)
    fmt.Println(string(respBody))
}
```

### PHP

```php
<?php

$ch = curl_init('https://api.finam.ru/v1/sessions');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'POST');
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['secret' => 'string', 'source_app_id' => 'string']));
$response = curl_exec($ch);
curl_close($ch);
$data = json_decode($response, true);
```

### Rust

```rust
use reqwest;
use serde_json::json;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();

    let response = client
        .post("https://api.finam.ru/v1/sessions")
        .json(&json!({
          "secret": "string",
          "source_app_id": "string"
        }))
        .send().await?;

    let data: serde_json::Value = response.json().await?;
    println!("{:#?}", data);
    Ok(())
}
```

### cURL

```shell
curl -X POST 'https://api.finam.ru/v1/sessions' \
  -H 'Content-Type: application/json' \
  -d '{
  "secret": "string",
  "source_app_id": "string"
}'
```