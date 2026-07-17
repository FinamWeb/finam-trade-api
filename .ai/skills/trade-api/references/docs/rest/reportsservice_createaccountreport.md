# CreateAccountReport

> Запустить генерацию отчета по счету за период
Пример HTTP запроса:
POST /v1/report
Authorization: <token>

**Protocol:** rest | **Type:** post
**Path:** /v1/report

## Request Body

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| date_range | object | no |  |
| date_range.date_begin | string | no |  |
| date_range.date_end | string | no |  |
| report_form | enum | no | - REPORT_FORM_UNKNOWN: Не указана
 - REPORT_FORM_SHORT: Краткая
 - REPORT_FORM_LONG: Полная — REPORT_FORM_UNKNOWN, REPORT_FORM_SHORT, REPORT_FORM_LONG |
| account_id | string | no |  |

## Response: 200

A successful response.

### Example

```json
{
  "report_id": "string"
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
const authResponse = await fetch('https://api.finam.ru/v1/sessions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({"secret":"YOUR_API_TOKEN"})
});
const { token } = await authResponse.json();

const response = await fetch('https://api.finam.ru/v1/report', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    "date_range": {
      "date_begin": "string",
      "date_end": "string"
    },
    "report_form": "REPORT_FORM_UNKNOWN",
    "account_id": "string"
  })
});
const data = await response.json();
```

### Python

```python
import requests

auth_response = requests.post(
    "https://api.finam.ru/v1/sessions",
    json={
    "secret": "YOUR_API_TOKEN"
}
)
token = auth_response.json()["token"]

response = requests.post(
    "https://api.finam.ru/v1/report",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={
    "date_range": {
        "date_begin": "string",
        "date_end": "string"
    },
    "report_form": "REPORT_FORM_UNKNOWN",
    "account_id": "string"
}
)
data = response.json()
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
)

func main() {
    authBody := []byte(`{"secret":"YOUR_API_TOKEN"}`)
    authReq, _ := http.NewRequest("POST", "https://api.finam.ru/v1/sessions", bytes.NewBuffer(authBody))
    authReq.Header.Set("Content-Type", "application/json")
    authResp, _ := http.DefaultClient.Do(authReq)
    defer authResp.Body.Close()
    var authResult map[string]interface{}
    json.NewDecoder(authResp.Body).Decode(&authResult)
    token := authResult["token"].(string)

    body := []byte(`{
  "date_range": {
    "date_begin": "string",
    "date_end": "string"
  },
  "report_form": "REPORT_FORM_UNKNOWN",
  "account_id": "string"
}`)
    req, _ := http.NewRequest("POST", "https://api.finam.ru/v1/report", bytes.NewBuffer(body))
    req.Header.Set("Authorization", "Bearer "+token)
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

$authCh = curl_init('https://api.finam.ru/v1/sessions');
curl_setopt($authCh, CURLOPT_RETURNTRANSFER, true);
curl_setopt($authCh, CURLOPT_POST, true);
curl_setopt($authCh, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($authCh, CURLOPT_POSTFIELDS, json_encode(['secret' => 'YOUR_API_TOKEN']));
$authResponse = json_decode(curl_exec($authCh), true);
curl_close($authCh);
$token = $authResponse['token'];

$ch = curl_init('https://api.finam.ru/v1/report');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'POST');
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Authorization: Bearer ' . $token, 'Content-Type: application/json']);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['date_range' => ['date_begin' => 'string', 'date_end' => 'string'], 'report_form' => 'REPORT_FORM_UNKNOWN', 'account_id' => 'string']));
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

    let auth_response: serde_json::Value = client
        .post("https://api.finam.ru/v1/sessions")
        .json(&json!({"secret":"YOUR_API_TOKEN"}))
        .send().await?
        .json().await?;
    let token = auth_response["token"].as_str().unwrap();

    let response = client
        .post("https://api.finam.ru/v1/report")
        .bearer_auth(token)
        .json(&json!({
          "date_range": {
            "date_begin": "string",
            "date_end": "string"
          },
          "report_form": "REPORT_FORM_UNKNOWN",
          "account_id": "string"
        }))
        .send().await?;

    let data: serde_json::Value = response.json().await?;
    println!("{:#?}", data);
    Ok(())
}
```

### cURL

```shell
TOKEN=$(curl -s -X POST 'https://api.finam.ru/v1/sessions' \
  -H 'Content-Type: application/json' \
  -d '{"secret":"YOUR_API_TOKEN"}' | jq -r '.token')

curl -X POST 'https://api.finam.ru/v1/report' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
  "date_range": {
    "date_begin": "string",
    "date_end": "string"
  },
  "report_form": "REPORT_FORM_UNKNOWN",
  "account_id": "string"
}'
```