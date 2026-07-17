# GetAsset

> Получение информации по конкретному инструменту
Пример HTTP запроса:
GET /v1/assets/SBER@MISX?account_id=1440399
Authorization: <token>

**Protocol:** rest | **Type:** get
**Path:** /v1/assets/{symbol}

Параметры:
- symbol - передается в URL пути
- account_id - передаётся как query-параметр

## Path Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| symbol | string | yes | Символ инструмента |

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| account_id | string | no | ID аккаунта для которого будет подбираться информация по инструменту |

## Response: 200

A successful response.

### Example

```json
{
  "board": "string",
  "id": "string",
  "ticker": "string",
  "mic": "string",
  "isin": "string",
  "type": "string",
  "name": "string",
  "decimals": 0,
  "min_step": "string",
  "lot_size": {
    "value": "string"
  },
  "expiration_date": {
    "year": 0,
    "month": 0,
    "day": 0
  },
  "quote_currency": "string",
  "future_details": {
    "expiration_date": "string",
    "contract_size": {
      "value": "string"
    }
  },
  "option_details": {
    "expiration_date": "string",
    "contract_size": {
      "value": "string"
    },
    "strike": {
      "value": "string"
    }
  },
  "bond_details": {
    "bond_face_value": {
      "value": "string"
    },
    "currency": "string"
  }
}
```

## Response: 400

Неверно передан символ или счет. Символ должен быть в виде ticker@mic. Где ticker - это, например, SBER. А mic, например, MISX

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

const params = new URLSearchParams({
  account_id: 'YOUR_ACCOUNT_ID'
});

const response = await fetch(`https://api.finam.ru/v1/assets/YOUR_SYMBOL?${params}`, {
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
    "https://api.finam.ru/v1/assets/YOUR_SYMBOL",
    headers={
        "Authorization": f"Bearer {token}"
    },
    params={
        "account_id": "YOUR_ACCOUNT_ID"
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
    "net/url"
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

    params := url.Values{}
    params.Set("account_id", "YOUR_ACCOUNT_ID")
    req, _ := http.NewRequest("GET", "https://api.finam.ru/v1/assets/YOUR_SYMBOL?"+params.Encode(), nil)
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

$ch = curl_init('https://api.finam.ru/v1/assets/YOUR_SYMBOL?' . http_build_query(['account_id' => 'YOUR_ACCOUNT_ID']));
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
        .get("https://api.finam.ru/v1/assets/YOUR_SYMBOL")
        .bearer_auth(token)
        .query(&[("account_id", "YOUR_ACCOUNT_ID")])
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

curl -X GET 'https://api.finam.ru/v1/assets/YOUR_SYMBOL?account_id=YOUR_ACCOUNT_ID' \
  -H "Authorization: Bearer $TOKEN"
```