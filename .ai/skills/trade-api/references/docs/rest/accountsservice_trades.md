# Trades

> Получение истории по сделкам аккаунта
Пример HTTP запроса:
GET /v1/accounts/A12345/trades?limit=50&interval.start_time=2023-01-01T00:00:00Z&interval.end_time=2023-01-31T23:59:59Z
Authorization: <token>

**Protocol:** rest | **Type:** get
**Path:** /v1/accounts/{account_id}/trades

Параметры:
- account_id - передается в URL пути
- limit и interval - передаются как query-параметры

## Path Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| account_id | string | yes | Идентификатор аккаунта |

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| limit | integer | no | Лимит количества сделок |
| interval.start_time | string | no | Optional. Inclusive start of the interval.

If specified, a Timestamp matching this interval will have to be the same
or after the start. |
| interval.end_time | string | no | Optional. Exclusive end of the interval.

If specified, a Timestamp matching this interval will have to be before the
end. |

## Response: 200

A successful response.

### Example

```json
{
  "trades": [
    {
      "trade_id": "string",
      "symbol": "string",
      "price": {
        "value": "string"
      },
      "size": {
        "value": "string"
      },
      "side": "SIDE_UNSPECIFIED",
      "timestamp": "string",
      "order_id": "string",
      "account_id": "string",
      "comment": "string",
      "accrued_interest": {
        "value": "string"
      },
      "currency": "string"
    }
  ]
}
```

## Response: 400

Неверно передан интервал

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
  limit: 'YOUR_LIMIT',
  interval.start_time: 'YOUR_INTERVAL.START_TIME',
  interval.end_time: 'YOUR_INTERVAL.END_TIME'
});

const response = await fetch(`https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/trades?${params}`, {
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
    "https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/trades",
    headers={
        "Authorization": f"Bearer {token}"
    },
    params={
        "limit": "YOUR_LIMIT",
        "interval.start_time": "YOUR_INTERVAL.START_TIME",
        "interval.end_time": "YOUR_INTERVAL.END_TIME"
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
    params.Set("limit", "YOUR_LIMIT")
    params.Set("interval.start_time", "YOUR_INTERVAL.START_TIME")
    params.Set("interval.end_time", "YOUR_INTERVAL.END_TIME")
    req, _ := http.NewRequest("GET", "https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/trades?"+params.Encode(), nil)
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

$ch = curl_init('https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/trades?' . http_build_query(['limit' => 'YOUR_LIMIT', 'interval.start_time' => 'YOUR_INTERVAL.START_TIME', 'interval.end_time' => 'YOUR_INTERVAL.END_TIME']));
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
        .get("https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/trades")
        .bearer_auth(token)
        .query(&[("limit", "YOUR_LIMIT"), ("interval.start_time", "YOUR_INTERVAL.START_TIME"), ("interval.end_time", "YOUR_INTERVAL.END_TIME")])
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

curl -X GET 'https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/trades?limit=YOUR_LIMIT&interval.start_time=YOUR_INTERVAL.START_TIME&interval.end_time=YOUR_INTERVAL.END_TIME' \
  -H "Authorization: Bearer $TOKEN"
```