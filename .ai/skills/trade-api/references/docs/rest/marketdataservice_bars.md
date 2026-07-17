# Bars

> Получение исторических данных по инструменту (агрегированные свечи)
Пример HTTP запроса:
GET /v1/instruments/SBER@MISX/bars?timeframe=TIME_FRAME_D&interval.start_time=2023-01-01T00:00:00Z&interval.end_time=2023-01-31T23:59:59Z
Authorization: <token>

**Protocol:** rest | **Type:** get
**Path:** /v1/instruments/{symbol}/bars

Параметры:
- symbol - передается в URL пути
- timeframe и interval - передаются как query-параметры

## Path Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| symbol | string | yes | Символ инструмента |

## Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| timeframe | string | no | Необходимый таймфрейм

 - TIME_FRAME_UNSPECIFIED: Таймфрейм не указан
 - TIME_FRAME_M1: 1 минута. Глубина данных 7 дней.
 - TIME_FRAME_M5: 5 минут. Глубина данных 30 дней.
 - TIME_FRAME_M15: 15 минут. Глубина данных 30 дней.
 - TIME_FRAME_M30: 30 минут. Глубина данных 30 дней.
 - TIME_FRAME_H1: 1 час. Глубина данных 30 дней.
 - TIME_FRAME_H2: 2 часа. Глубина данных 30 дней.
 - TIME_FRAME_H4: 4 часа. Глубина данных 30 дней.
 - TIME_FRAME_H8: 8 часов. Глубина данных 30 дней.
 - TIME_FRAME_D: День. Глубина данных 365 дней.
 - TIME_FRAME_W: Неделя. Глубина данных 365*5 дней.
 - TIME_FRAME_MN: Месяц. Глубина данных 365*5 дней.
 - TIME_FRAME_QR: Квартал. Глубина данных 365*5 дней. — TIME_FRAME_UNSPECIFIED, TIME_FRAME_M1, TIME_FRAME_M5, TIME_FRAME_M15, TIME_FRAME_M30, TIME_FRAME_H1, TIME_FRAME_H2, TIME_FRAME_H4, TIME_FRAME_H8, TIME_FRAME_D, TIME_FRAME_W, TIME_FRAME_MN, TIME_FRAME_QR |
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
  "symbol": "string",
  "bars": [
    {
      "timestamp": "string",
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
      "volume": {
        "value": "string"
      }
    }
  ]
}
```

## Response: 400

Неверно передан символ или интервал. Символ должен быть в виде ticker@mic. Где ticker - это, например, SBER. А mic, например, MISX

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
  timeframe: 'YOUR_TIMEFRAME',
  interval.start_time: 'YOUR_INTERVAL.START_TIME',
  interval.end_time: 'YOUR_INTERVAL.END_TIME'
});

const response = await fetch(`https://api.finam.ru/v1/instruments/YOUR_SYMBOL/bars?${params}`, {
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
    "https://api.finam.ru/v1/instruments/YOUR_SYMBOL/bars",
    headers={
        "Authorization": f"Bearer {token}"
    },
    params={
        "timeframe": "YOUR_TIMEFRAME",
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
    params.Set("timeframe", "YOUR_TIMEFRAME")
    params.Set("interval.start_time", "YOUR_INTERVAL.START_TIME")
    params.Set("interval.end_time", "YOUR_INTERVAL.END_TIME")
    req, _ := http.NewRequest("GET", "https://api.finam.ru/v1/instruments/YOUR_SYMBOL/bars?"+params.Encode(), nil)
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

$ch = curl_init('https://api.finam.ru/v1/instruments/YOUR_SYMBOL/bars?' . http_build_query(['timeframe' => 'YOUR_TIMEFRAME', 'interval.start_time' => 'YOUR_INTERVAL.START_TIME', 'interval.end_time' => 'YOUR_INTERVAL.END_TIME']));
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
        .get("https://api.finam.ru/v1/instruments/YOUR_SYMBOL/bars")
        .bearer_auth(token)
        .query(&[("timeframe", "YOUR_TIMEFRAME"), ("interval.start_time", "YOUR_INTERVAL.START_TIME"), ("interval.end_time", "YOUR_INTERVAL.END_TIME")])
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

curl -X GET 'https://api.finam.ru/v1/instruments/YOUR_SYMBOL/bars?timeframe=YOUR_TIMEFRAME&interval.start_time=YOUR_INTERVAL.START_TIME&interval.end_time=YOUR_INTERVAL.END_TIME' \
  -H "Authorization: Bearer $TOKEN"
```