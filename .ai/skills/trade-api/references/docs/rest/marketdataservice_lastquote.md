# LastQuote

> Получение последней котировки по инструменту
Пример HTTP запроса:
GET /v1/instruments/SBER@MISX/quotes/latest
Authorization: <token>

**Protocol:** rest | **Type:** get
**Path:** /v1/instruments/{symbol}/quotes/latest

## Path Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| symbol | string | yes | Символ инструмента |

## Response: 200

A successful response.

### Example

```json
{
  "symbol": "string",
  "quote": {
    "symbol": "string",
    "timestamp": "string",
    "ask": {
      "value": "string"
    },
    "ask_size": {
      "value": "string"
    },
    "bid": {
      "value": "string"
    },
    "bid_size": {
      "value": "string"
    },
    "last": {
      "value": "string"
    },
    "last_size": {
      "value": "string"
    },
    "volume": {
      "value": "string"
    },
    "turnover": {
      "value": "string"
    },
    "open": {
      "value": "string"
    },
    "high": {
      "value": "string"
    },
    "low": {
      "value": "string"
    },
    "close": {
      "value": "string"
    },
    "change": {
      "value": "string"
    },
    "open_interest": {
      "value": "string"
    },
    "option": {
      "open_interest": {
        "value": "string"
      },
      "implied_volatility": {
        "value": "string"
      },
      "theoretical_price": {
        "value": "string"
      },
      "delta": {
        "value": "string"
      },
      "gamma": {
        "value": "string"
      },
      "theta": {
        "value": "string"
      },
      "vega": {
        "value": "string"
      },
      "rho": {
        "value": "string"
      }
    }
  }
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

const response = await fetch('https://api.finam.ru/v1/instruments/YOUR_SYMBOL/quotes/latest', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`
  },
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

response = requests.get(
    "https://api.finam.ru/v1/instruments/YOUR_SYMBOL/quotes/latest",
    headers={
        "Authorization": f"Bearer {token}"
    },
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

    req, _ := http.NewRequest("GET", "https://api.finam.ru/v1/instruments/YOUR_SYMBOL/quotes/latest", nil)
    req.Header.Set("Authorization", "Bearer "+token)
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

$ch = curl_init('https://api.finam.ru/v1/instruments/YOUR_SYMBOL/quotes/latest');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'GET');
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Authorization: Bearer ' . $token]);
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
        .get("https://api.finam.ru/v1/instruments/YOUR_SYMBOL/quotes/latest")
        .bearer_auth(token)
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

curl -X GET 'https://api.finam.ru/v1/instruments/YOUR_SYMBOL/quotes/latest' \
  -H "Authorization: Bearer $TOKEN"
```