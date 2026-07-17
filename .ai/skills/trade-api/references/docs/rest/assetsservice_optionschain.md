# OptionsChain

> Получение цепочки опционов для базового актива
Пример HTTP запроса:
GET /v1/assets/SBER@MISX/options
Authorization: <token>

**Protocol:** rest | **Type:** get
**Path:** /v1/assets/{underlying_symbol}/options

## Path Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| underlying_symbol | string | yes | Символ базового актива опциона |

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| root | string | no | Опциональный параметр. Актуален для опционов на фьючерсы, по типу (недельные, месячные).
Если параметр не указан, будут возвращены опционы с ближайшей датой экспирации. |
| expiration_date.year | integer | no | Year of the date. Must be from 1 to 9999, or 0 to specify a date without
a year. |
| expiration_date.month | integer | no | Month of a year. Must be from 1 to 12, or 0 to specify a year without a
month and day. |
| expiration_date.day | integer | no | Day of a month. Must be from 1 to 31 and valid for the year and month, or 0
to specify a year by itself or a year and month where the day isn't
significant. |

## Response: 200

A successful response.

### Example

```json
{
  "symbol": "string",
  "options": [
    {
      "symbol": "string",
      "type": "TYPE_UNSPECIFIED",
      "contract_size": {
        "value": "string"
      },
      "trade_first_day": {
        "year": 0,
        "month": 0,
        "day": 0
      },
      "trade_last_day": {
        "year": 0,
        "month": 0,
        "day": 0
      },
      "strike": {
        "value": "string"
      },
      "multiplier": {
        "value": "string"
      },
      "expiration_first_day": {
        "year": 0,
        "month": 0,
        "day": 0
      },
      "expiration_last_day": {
        "year": 0,
        "month": 0,
        "day": 0
      }
    }
  ]
}
```

## Response: 400

Неверно передан символ. Символ должен быть в виде ticker@mic. Где ticker - это, например, SBER. А mic, например, MISX

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
  root: 'YOUR_ROOT',
  expiration_date.year: 'YOUR_EXPIRATION_DATE.YEAR',
  expiration_date.month: 'YOUR_EXPIRATION_DATE.MONTH',
  expiration_date.day: 'YOUR_EXPIRATION_DATE.DAY'
});

const response = await fetch(`https://api.finam.ru/v1/assets/YOUR_UNDERLYING_SYMBOL/options?${params}`, {
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
    "https://api.finam.ru/v1/assets/YOUR_UNDERLYING_SYMBOL/options",
    headers={
        "Authorization": f"Bearer {token}"
    },
    params={
        "root": "YOUR_ROOT",
        "expiration_date.year": "YOUR_EXPIRATION_DATE.YEAR",
        "expiration_date.month": "YOUR_EXPIRATION_DATE.MONTH",
        "expiration_date.day": "YOUR_EXPIRATION_DATE.DAY"
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
    params.Set("root", "YOUR_ROOT")
    params.Set("expiration_date.year", "YOUR_EXPIRATION_DATE.YEAR")
    params.Set("expiration_date.month", "YOUR_EXPIRATION_DATE.MONTH")
    params.Set("expiration_date.day", "YOUR_EXPIRATION_DATE.DAY")
    req, _ := http.NewRequest("GET", "https://api.finam.ru/v1/assets/YOUR_UNDERLYING_SYMBOL/options?"+params.Encode(), nil)
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

$ch = curl_init('https://api.finam.ru/v1/assets/YOUR_UNDERLYING_SYMBOL/options?' . http_build_query(['root' => 'YOUR_ROOT', 'expiration_date.year' => 'YOUR_EXPIRATION_DATE.YEAR', 'expiration_date.month' => 'YOUR_EXPIRATION_DATE.MONTH', 'expiration_date.day' => 'YOUR_EXPIRATION_DATE.DAY']));
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
        .get("https://api.finam.ru/v1/assets/YOUR_UNDERLYING_SYMBOL/options")
        .bearer_auth(token)
        .query(&[("root", "YOUR_ROOT"), ("expiration_date.year", "YOUR_EXPIRATION_DATE.YEAR"), ("expiration_date.month", "YOUR_EXPIRATION_DATE.MONTH"), ("expiration_date.day", "YOUR_EXPIRATION_DATE.DAY")])
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

curl -X GET 'https://api.finam.ru/v1/assets/YOUR_UNDERLYING_SYMBOL/options?root=YOUR_ROOT&expiration_date.year=YOUR_EXPIRATION_DATE.YEAR&expiration_date.month=YOUR_EXPIRATION_DATE.MONTH&expiration_date.day=YOUR_EXPIRATION_DATE.DAY' \
  -H "Authorization: Bearer $TOKEN"
```