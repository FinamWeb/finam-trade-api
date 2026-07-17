# PlaceSLTPOrder

> Выставление SL/TP заявки
Пример HTTP запроса:
POST /v1/accounts/A12345/sltp-orders
Content-Type: application/json
Authorization: <token>

**Protocol:** rest | **Type:** post
**Path:** /v1/accounts/{account_id}/sltp-orders

{
  "symbol": "SBER@MISX",
  "side": "SIDE_BUY",
  "quantity_sl": {
    "value": "10"
  },
  "sl_price": {
    "value": "270.00"
  },
  "limit_price": {
    "value": "269.50"
  },
  "quantity_tp": {
    "value": "10"
  },
  "tp_price": {
    "value": "295.50"
  },
  "tp_guard_spread": {
    "value": "0.5"  },
  "tp_spread_measure": "TP_SPREAD_MEASURE_VALUE",
  "valid_before": "VALID_BEFORE_GOOD_TILL_DATE",
  "valid_expiry_time": "2026-12-31T23:59:59Z",
  "comment": "my SL/TP order"
 }

 Поле account_id берется из URL-пути, остальные поля передаются в теле запроса

## Path Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| account_id | string | yes | Идентификатор аккаунта |

## Request Body

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| symbol | string | no |  |
| side | enum | no | - SIDE_UNSPECIFIED: Сторона сделки не указана
 - SIDE_BUY: Покупка
 - SIDE_SELL: Продажа — SIDE_UNSPECIFIED, SIDE_BUY, SIDE_SELL |
| quantity_sl | object | no | A representation of a decimal value, such as 2.5. Clients may convert values
into language-native decimal formats, such as Java's [BigDecimal][] or
Python's [decimal.Decimal][].

[BigDecimal]:
https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/math/BigDecimal.html
[decimal.Decimal]: https://docs.python.org/3/library/decimal.html |
| quantity_sl.value | string | no | The decimal value, as a string.

The string representation consists of an optional sign, `+` (`U+002B`)
or `-` (`U+002D`), followed by a sequence of zero or more decimal digits
("the integer"), optionally followed by a fraction, optionally followed
by an exponent.

The fraction consists of a decimal point followed by zero or more decimal
digits. The string must contain at least one digit in either the integer
or the fraction. The number formed by the sign, the integer and the
fraction is referred to as the significand.

The exponent consists of the character `e` (`U+0065`) or `E` (`U+0045`)
followed by one or more decimal digits.

Services **should** normalize decimal values before storing them by:

  - Removing an explicitly-provided `+` sign (`+2.5` -> `2.5`).
  - Replacing a zero-length integer value with `0` (`.5` -> `0.5`).
  - Coercing the exponent character to lower-case (`2.5E8` -> `2.5e8`).
  - Removing an explicitly-provided zero exponent (`2.5e0` -> `2.5`).

Services **may** perform additional normalization based on its own needs
and the internal decimal implementation selected, such as shifting the
decimal point and exponent value together (example: `2.5e-1` <-> `0.25`).
Additionally, services **may** preserve trailing zeroes in the fraction
to indicate increased precision, but are not required to do so.

Note that only the `.` character is supported to divide the integer
and the fraction; `,` **should not** be supported regardless of locale.
Additionally, thousand separators **should not** be supported. If a
service does support them, values **must** be normalized.

The ENBF grammar is:

    DecimalString =
      [Sign] Significand [Exponent];

    Sign = '+' | '-';

    Significand =
      Digits ['.'] [Digits] | [Digits] '.' Digits;

    Exponent = ('e' | 'E') [Sign] Digits;

    Digits = { '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' };

Services **should** clearly document the range of supported values, the
maximum supported precision (total number of digits), and, if applicable,
the scale (number of digits after the decimal point), as well as how it
behaves when receiving out-of-bounds values.

Services **may** choose to accept values passed as input even when the
value has a higher precision or scale than the service supports, and
**should** round the value to fit the supported scale. Alternatively, the
service **may** error with `400 Bad Request` (`INVALID_ARGUMENT` in gRPC)
if precision would be lost.

Services **should** error with `400 Bad Request` (`INVALID_ARGUMENT` in
gRPC) if the service receives a value outside of the supported range. |
| sl_price | object | no | A representation of a decimal value, such as 2.5. Clients may convert values
into language-native decimal formats, such as Java's [BigDecimal][] or
Python's [decimal.Decimal][].

[BigDecimal]:
https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/math/BigDecimal.html
[decimal.Decimal]: https://docs.python.org/3/library/decimal.html |
| sl_price.value | string | no | The decimal value, as a string.

The string representation consists of an optional sign, `+` (`U+002B`)
or `-` (`U+002D`), followed by a sequence of zero or more decimal digits
("the integer"), optionally followed by a fraction, optionally followed
by an exponent.

The fraction consists of a decimal point followed by zero or more decimal
digits. The string must contain at least one digit in either the integer
or the fraction. The number formed by the sign, the integer and the
fraction is referred to as the significand.

The exponent consists of the character `e` (`U+0065`) or `E` (`U+0045`)
followed by one or more decimal digits.

Services **should** normalize decimal values before storing them by:

  - Removing an explicitly-provided `+` sign (`+2.5` -> `2.5`).
  - Replacing a zero-length integer value with `0` (`.5` -> `0.5`).
  - Coercing the exponent character to lower-case (`2.5E8` -> `2.5e8`).
  - Removing an explicitly-provided zero exponent (`2.5e0` -> `2.5`).

Services **may** perform additional normalization based on its own needs
and the internal decimal implementation selected, such as shifting the
decimal point and exponent value together (example: `2.5e-1` <-> `0.25`).
Additionally, services **may** preserve trailing zeroes in the fraction
to indicate increased precision, but are not required to do so.

Note that only the `.` character is supported to divide the integer
and the fraction; `,` **should not** be supported regardless of locale.
Additionally, thousand separators **should not** be supported. If a
service does support them, values **must** be normalized.

The ENBF grammar is:

    DecimalString =
      [Sign] Significand [Exponent];

    Sign = '+' | '-';

    Significand =
      Digits ['.'] [Digits] | [Digits] '.' Digits;

    Exponent = ('e' | 'E') [Sign] Digits;

    Digits = { '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' };

Services **should** clearly document the range of supported values, the
maximum supported precision (total number of digits), and, if applicable,
the scale (number of digits after the decimal point), as well as how it
behaves when receiving out-of-bounds values.

Services **may** choose to accept values passed as input even when the
value has a higher precision or scale than the service supports, and
**should** round the value to fit the supported scale. Alternatively, the
service **may** error with `400 Bad Request` (`INVALID_ARGUMENT` in gRPC)
if precision would be lost.

Services **should** error with `400 Bad Request` (`INVALID_ARGUMENT` in
gRPC) if the service receives a value outside of the supported range. |
| limit_price | object | no | A representation of a decimal value, such as 2.5. Clients may convert values
into language-native decimal formats, such as Java's [BigDecimal][] or
Python's [decimal.Decimal][].

[BigDecimal]:
https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/math/BigDecimal.html
[decimal.Decimal]: https://docs.python.org/3/library/decimal.html |
| limit_price.value | string | no | The decimal value, as a string.

The string representation consists of an optional sign, `+` (`U+002B`)
or `-` (`U+002D`), followed by a sequence of zero or more decimal digits
("the integer"), optionally followed by a fraction, optionally followed
by an exponent.

The fraction consists of a decimal point followed by zero or more decimal
digits. The string must contain at least one digit in either the integer
or the fraction. The number formed by the sign, the integer and the
fraction is referred to as the significand.

The exponent consists of the character `e` (`U+0065`) or `E` (`U+0045`)
followed by one or more decimal digits.

Services **should** normalize decimal values before storing them by:

  - Removing an explicitly-provided `+` sign (`+2.5` -> `2.5`).
  - Replacing a zero-length integer value with `0` (`.5` -> `0.5`).
  - Coercing the exponent character to lower-case (`2.5E8` -> `2.5e8`).
  - Removing an explicitly-provided zero exponent (`2.5e0` -> `2.5`).

Services **may** perform additional normalization based on its own needs
and the internal decimal implementation selected, such as shifting the
decimal point and exponent value together (example: `2.5e-1` <-> `0.25`).
Additionally, services **may** preserve trailing zeroes in the fraction
to indicate increased precision, but are not required to do so.

Note that only the `.` character is supported to divide the integer
and the fraction; `,` **should not** be supported regardless of locale.
Additionally, thousand separators **should not** be supported. If a
service does support them, values **must** be normalized.

The ENBF grammar is:

    DecimalString =
      [Sign] Significand [Exponent];

    Sign = '+' | '-';

    Significand =
      Digits ['.'] [Digits] | [Digits] '.' Digits;

    Exponent = ('e' | 'E') [Sign] Digits;

    Digits = { '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' };

Services **should** clearly document the range of supported values, the
maximum supported precision (total number of digits), and, if applicable,
the scale (number of digits after the decimal point), as well as how it
behaves when receiving out-of-bounds values.

Services **may** choose to accept values passed as input even when the
value has a higher precision or scale than the service supports, and
**should** round the value to fit the supported scale. Alternatively, the
service **may** error with `400 Bad Request` (`INVALID_ARGUMENT` in gRPC)
if precision would be lost.

Services **should** error with `400 Bad Request` (`INVALID_ARGUMENT` in
gRPC) if the service receives a value outside of the supported range. |
| quantity_tp | object | no | A representation of a decimal value, such as 2.5. Clients may convert values
into language-native decimal formats, such as Java's [BigDecimal][] or
Python's [decimal.Decimal][].

[BigDecimal]:
https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/math/BigDecimal.html
[decimal.Decimal]: https://docs.python.org/3/library/decimal.html |
| quantity_tp.value | string | no | The decimal value, as a string.

The string representation consists of an optional sign, `+` (`U+002B`)
or `-` (`U+002D`), followed by a sequence of zero or more decimal digits
("the integer"), optionally followed by a fraction, optionally followed
by an exponent.

The fraction consists of a decimal point followed by zero or more decimal
digits. The string must contain at least one digit in either the integer
or the fraction. The number formed by the sign, the integer and the
fraction is referred to as the significand.

The exponent consists of the character `e` (`U+0065`) or `E` (`U+0045`)
followed by one or more decimal digits.

Services **should** normalize decimal values before storing them by:

  - Removing an explicitly-provided `+` sign (`+2.5` -> `2.5`).
  - Replacing a zero-length integer value with `0` (`.5` -> `0.5`).
  - Coercing the exponent character to lower-case (`2.5E8` -> `2.5e8`).
  - Removing an explicitly-provided zero exponent (`2.5e0` -> `2.5`).

Services **may** perform additional normalization based on its own needs
and the internal decimal implementation selected, such as shifting the
decimal point and exponent value together (example: `2.5e-1` <-> `0.25`).
Additionally, services **may** preserve trailing zeroes in the fraction
to indicate increased precision, but are not required to do so.

Note that only the `.` character is supported to divide the integer
and the fraction; `,` **should not** be supported regardless of locale.
Additionally, thousand separators **should not** be supported. If a
service does support them, values **must** be normalized.

The ENBF grammar is:

    DecimalString =
      [Sign] Significand [Exponent];

    Sign = '+' | '-';

    Significand =
      Digits ['.'] [Digits] | [Digits] '.' Digits;

    Exponent = ('e' | 'E') [Sign] Digits;

    Digits = { '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' };

Services **should** clearly document the range of supported values, the
maximum supported precision (total number of digits), and, if applicable,
the scale (number of digits after the decimal point), as well as how it
behaves when receiving out-of-bounds values.

Services **may** choose to accept values passed as input even when the
value has a higher precision or scale than the service supports, and
**should** round the value to fit the supported scale. Alternatively, the
service **may** error with `400 Bad Request` (`INVALID_ARGUMENT` in gRPC)
if precision would be lost.

Services **should** error with `400 Bad Request` (`INVALID_ARGUMENT` in
gRPC) if the service receives a value outside of the supported range. |
| tp_price | object | no | A representation of a decimal value, such as 2.5. Clients may convert values
into language-native decimal formats, such as Java's [BigDecimal][] or
Python's [decimal.Decimal][].

[BigDecimal]:
https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/math/BigDecimal.html
[decimal.Decimal]: https://docs.python.org/3/library/decimal.html |
| tp_price.value | string | no | The decimal value, as a string.

The string representation consists of an optional sign, `+` (`U+002B`)
or `-` (`U+002D`), followed by a sequence of zero or more decimal digits
("the integer"), optionally followed by a fraction, optionally followed
by an exponent.

The fraction consists of a decimal point followed by zero or more decimal
digits. The string must contain at least one digit in either the integer
or the fraction. The number formed by the sign, the integer and the
fraction is referred to as the significand.

The exponent consists of the character `e` (`U+0065`) or `E` (`U+0045`)
followed by one or more decimal digits.

Services **should** normalize decimal values before storing them by:

  - Removing an explicitly-provided `+` sign (`+2.5` -> `2.5`).
  - Replacing a zero-length integer value with `0` (`.5` -> `0.5`).
  - Coercing the exponent character to lower-case (`2.5E8` -> `2.5e8`).
  - Removing an explicitly-provided zero exponent (`2.5e0` -> `2.5`).

Services **may** perform additional normalization based on its own needs
and the internal decimal implementation selected, such as shifting the
decimal point and exponent value together (example: `2.5e-1` <-> `0.25`).
Additionally, services **may** preserve trailing zeroes in the fraction
to indicate increased precision, but are not required to do so.

Note that only the `.` character is supported to divide the integer
and the fraction; `,` **should not** be supported regardless of locale.
Additionally, thousand separators **should not** be supported. If a
service does support them, values **must** be normalized.

The ENBF grammar is:

    DecimalString =
      [Sign] Significand [Exponent];

    Sign = '+' | '-';

    Significand =
      Digits ['.'] [Digits] | [Digits] '.' Digits;

    Exponent = ('e' | 'E') [Sign] Digits;

    Digits = { '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' };

Services **should** clearly document the range of supported values, the
maximum supported precision (total number of digits), and, if applicable,
the scale (number of digits after the decimal point), as well as how it
behaves when receiving out-of-bounds values.

Services **may** choose to accept values passed as input even when the
value has a higher precision or scale than the service supports, and
**should** round the value to fit the supported scale. Alternatively, the
service **may** error with `400 Bad Request` (`INVALID_ARGUMENT` in gRPC)
if precision would be lost.

Services **should** error with `400 Bad Request` (`INVALID_ARGUMENT` in
gRPC) if the service receives a value outside of the supported range. |
| tp_guard_spread | object | no | A representation of a decimal value, such as 2.5. Clients may convert values
into language-native decimal formats, such as Java's [BigDecimal][] or
Python's [decimal.Decimal][].

[BigDecimal]:
https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/math/BigDecimal.html
[decimal.Decimal]: https://docs.python.org/3/library/decimal.html |
| tp_guard_spread.value | string | no | The decimal value, as a string.

The string representation consists of an optional sign, `+` (`U+002B`)
or `-` (`U+002D`), followed by a sequence of zero or more decimal digits
("the integer"), optionally followed by a fraction, optionally followed
by an exponent.

The fraction consists of a decimal point followed by zero or more decimal
digits. The string must contain at least one digit in either the integer
or the fraction. The number formed by the sign, the integer and the
fraction is referred to as the significand.

The exponent consists of the character `e` (`U+0065`) or `E` (`U+0045`)
followed by one or more decimal digits.

Services **should** normalize decimal values before storing them by:

  - Removing an explicitly-provided `+` sign (`+2.5` -> `2.5`).
  - Replacing a zero-length integer value with `0` (`.5` -> `0.5`).
  - Coercing the exponent character to lower-case (`2.5E8` -> `2.5e8`).
  - Removing an explicitly-provided zero exponent (`2.5e0` -> `2.5`).

Services **may** perform additional normalization based on its own needs
and the internal decimal implementation selected, such as shifting the
decimal point and exponent value together (example: `2.5e-1` <-> `0.25`).
Additionally, services **may** preserve trailing zeroes in the fraction
to indicate increased precision, but are not required to do so.

Note that only the `.` character is supported to divide the integer
and the fraction; `,` **should not** be supported regardless of locale.
Additionally, thousand separators **should not** be supported. If a
service does support them, values **must** be normalized.

The ENBF grammar is:

    DecimalString =
      [Sign] Significand [Exponent];

    Sign = '+' | '-';

    Significand =
      Digits ['.'] [Digits] | [Digits] '.' Digits;

    Exponent = ('e' | 'E') [Sign] Digits;

    Digits = { '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' };

Services **should** clearly document the range of supported values, the
maximum supported precision (total number of digits), and, if applicable,
the scale (number of digits after the decimal point), as well as how it
behaves when receiving out-of-bounds values.

Services **may** choose to accept values passed as input even when the
value has a higher precision or scale than the service supports, and
**should** round the value to fit the supported scale. Alternatively, the
service **may** error with `400 Bad Request` (`INVALID_ARGUMENT` in gRPC)
if precision would be lost.

Services **should** error with `400 Bad Request` (`INVALID_ARGUMENT` in
gRPC) if the service receives a value outside of the supported range. |
| tp_spread_measure | enum | no | - TP_SPREAD_MEASURE_UNDEFINED: Значение не указано
 - TP_SPREAD_MEASURE_VALUE: в единицах цены
 - TP_SPREAD_MEASURE_PERCENT: в процентах, с максимальной точностью до сотых процента — TP_SPREAD_MEASURE_UNDEFINED, TP_SPREAD_MEASURE_VALUE, TP_SPREAD_MEASURE_PERCENT |
| client_order_id | string | no |  |
| valid_before | enum | no | - VALID_BEFORE_UNSPECIFIED: Значение не указано
 - VALID_BEFORE_END_OF_DAY: До конца торгового дня
 - VALID_BEFORE_GOOD_TILL_CANCEL: До отмены
 - VALID_BEFORE_GOOD_TILL_DATE: До указанной даты-времени. Данный тип поддерживается только при выставлении SL/TP заявок — VALID_BEFORE_UNSPECIFIED, VALID_BEFORE_END_OF_DAY, VALID_BEFORE_GOOD_TILL_CANCEL, VALID_BEFORE_GOOD_TILL_DATE |
| valid_expiry_time | string | no |  |
| comment | string | no |  |

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

## Response: 400

Неверно переданы торговые параметры

## Response: 401

Срок действия токена истек или токен недействителен

## Response: 404

Счёт или инструмент не были найдены

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

const response = await fetch('https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/sltp-orders', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
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
    "https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/sltp-orders",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={
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
}`)
    req, _ := http.NewRequest("POST", "https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/sltp-orders", bytes.NewBuffer(body))
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

$ch = curl_init('https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/sltp-orders');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'POST');
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Authorization: Bearer ' . $token, 'Content-Type: application/json']);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['symbol' => 'string', 'side' => 'SIDE_UNSPECIFIED', 'quantity_sl' => ['value' => 'string'], 'sl_price' => ['value' => 'string'], 'limit_price' => ['value' => 'string'], 'quantity_tp' => ['value' => 'string'], 'tp_price' => ['value' => 'string'], 'tp_guard_spread' => ['value' => 'string'], 'tp_spread_measure' => 'TP_SPREAD_MEASURE_UNDEFINED', 'client_order_id' => 'string', 'valid_before' => 'VALID_BEFORE_UNSPECIFIED', 'valid_expiry_time' => 'string', 'comment' => 'string']));
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
        .post("https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/sltp-orders")
        .bearer_auth(token)
        .json(&json!({
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

curl -X POST 'https://api.finam.ru/v1/accounts/YOUR_ACCOUNT_ID/sltp-orders' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
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
}'
```