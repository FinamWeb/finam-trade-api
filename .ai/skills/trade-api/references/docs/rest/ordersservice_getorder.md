# GetOrder

> Получение информации о конкретном ордере
Пример HTTP запроса:
GET /v1/accounts/A12345/orders/ORD789012
Authorization: <token>

**Protocol:** rest | **Type:** get
**Path:** /v1/accounts/{account_id}/orders/{order_id}

## Path Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| account_id | string | yes | Идентификатор аккаунта |
| order_id | string | yes | Идентификатор заявки |

## Response: 200

A successful response.

### Example

```json
{
  "order_id": "string",
  "exec_id": "string",
  "status": "ORDER_STATUS_UNSPECIFIED",
  "order": {
    "account_id": "string",
    "symbol": "string",
    "quantity": {
      "value": "string"
    },
    "side": "SIDE_UNSPECIFIED",
    "type": "ORDER_TYPE_UNSPECIFIED",
    "time_in_force": "TIME_IN_FORCE_UNSPECIFIED",
    "limit_price": {
      "value": "string"
    },
    "stop_price": {
      "value": "string"
    },
    "stop_condition": "STOP_CONDITION_UNSPECIFIED",
    "legs": [
      {
        "symbol": "string",
        "quantity": {
          "value": "string"
        },
        "side": "SIDE_UNSPECIFIED"
      }
    ],
    "client_order_id": "string",
    "valid_before": "VALID_BEFORE_UNSPECIFIED",
    "comment": "string"
  },
  "transact_at": "string",
  "accept_at": "string",
  "withdraw_at": "string",
  "initial_quantity": {
    "value": "string"
  },
  "executed_quantity": {
    "value": "string"
  },
  "remaining_quantity": {
    "value": "string"
  },
  "sltp_order": {
    "account_id": "string",
    "symbol": "string",
    "side": "SIDE_UNSPECIFIED",
    "quantity_sl": {
      "value": "string"
    },
    "sl_price": {
      "value": "string"
    },
    "limit_price": {
      "value": "string"
    },
    "quantity_tp": {
      "value": "string"
    },
    "tp_price": {
      "value": "string"
    },
    "tp_guard_spread": {
      "value": "string"
    },
    "tp_spread_measure": "TP_SPREAD_MEASURE_UNDEFINED",
    "client_order_id": "string",
    "valid_before": "VALID_BEFORE_UNSPECIFIED",
    "valid_expiry_time": "string",
    "comment": "string"
  },
  "triggered_order_id": "string"
}
```

## Response: 401

Срок действия токена истек или токен недействителен

## Response: 404

Счёт или заявка не были найдены

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

const response = await fetch('https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/orders/YOUR_ORDER_ID', {
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
    "https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/orders/YOUR_ORDER_ID",
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

    req, _ := http.NewRequest("GET", "https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/orders/YOUR_ORDER_ID", nil)
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

$ch = curl_init('https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/orders/YOUR_ORDER_ID');
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
        .get("https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/orders/YOUR_ORDER_ID")
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

curl -X GET 'https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/orders/YOUR_ORDER_ID' \
  -H "Authorization: Bearer $TOKEN"
```