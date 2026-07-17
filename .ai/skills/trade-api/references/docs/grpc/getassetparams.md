# GetAssetParams

> Получение торговых параметров по инструменту

**Protocol:** grpc | **Type:** unary
**Path:** /grpc.tradeapi.v1.assets.AssetsService/GetAssetParams

Получение торговых параметров по инструменту
 Пример HTTP запроса:
 GET /v1/assets/SBER@MISX/params?account_id=1440399
 Authorization: <token>

 Параметры:
 - symbol - передается в URL пути
 - account_id - передаётся как query-параметр

## Request

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| symbol | string | no | Символ инструмента |
| account_id | string | no | ID аккаунта для которого будут подбираться торговые параметры |

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| symbol | string | no | Символ инструмента |
| account_id | string | no | ID аккаунта для которого подбираются торговые параметры |
| tradeable | bool | no | Доступны ли торговые операции
 Старое поле, помечено как устаревшее.
 Клиентам следует перейти на is_tradeable. |
| longable | Longable | no | Доступны ли операции в Лонг |
| longable.value | Status | no | Статус инструмента — NOT_AVAILABLE, AVAILABLE, ACCOUNT_NOT_APPROVED |
| longable.halted_days | int32 | no | Сколько дней действует запрет на операции в Лонг (если есть) |
| shortable | Shortable | no | Доступны ли операции в Шорт |
| shortable.value | Status | no | Статус инструмента — NOT_AVAILABLE, AVAILABLE, HTB, ACCOUNT_NOT_APPROVED, AVAILABLE_STRATEGY |
| shortable.halted_days | int32 | no | Сколько дней действует запрет на операции в Шорт (если есть) |
| long_risk_rate | Decimal | no | Ставка риска для операции в Лонг |
| long_risk_rate.value | string | no | The decimal value, as a string.

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
| long_collateral | Money | no | Сумма обеспечения для поддержания позиции Лонг |
| long_collateral.currency_code | string | no | The three-letter currency code defined in ISO 4217. |
| long_collateral.units | int64 | no | The whole units of the amount.
 For example if `currencyCode` is `"USD"`, then 1 unit is one US dollar. |
| long_collateral.nanos | int32 | no | Number of nano (10^-9) units of the amount.
 The value must be between -999,999,999 and +999,999,999 inclusive.
 If `units` is positive, `nanos` must be positive or zero.
 If `units` is zero, `nanos` can be positive, zero, or negative.
 If `units` is negative, `nanos` must be negative or zero.
 For example $-1.75 is represented as `units`=-1 and `nanos`=-750,000,000. |
| short_risk_rate | Decimal | no | Ставка риска для операции в Шорт |
| short_risk_rate.value | string | no | The decimal value, as a string.

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
| short_collateral | Money | no | Сумма обеспечения для поддержания позиции Шорт |
| short_collateral.currency_code | string | no | The three-letter currency code defined in ISO 4217. |
| short_collateral.units | int64 | no | The whole units of the amount.
 For example if `currencyCode` is `"USD"`, then 1 unit is one US dollar. |
| short_collateral.nanos | int32 | no | Number of nano (10^-9) units of the amount.
 The value must be between -999,999,999 and +999,999,999 inclusive.
 If `units` is positive, `nanos` must be positive or zero.
 If `units` is zero, `nanos` can be positive, zero, or negative.
 If `units` is negative, `nanos` must be negative or zero.
 For example $-1.75 is represented as `units`=-1 and `nanos`=-750,000,000. |
| long_initial_margin | Money | no | Начальные требования, сколько на счету должно быть свободных денежных средств, чтобы открыть лонг позицию, для FORTS счетов равен биржевому ГО |
| long_initial_margin.currency_code | string | no | The three-letter currency code defined in ISO 4217. |
| long_initial_margin.units | int64 | no | The whole units of the amount.
 For example if `currencyCode` is `"USD"`, then 1 unit is one US dollar. |
| long_initial_margin.nanos | int32 | no | Number of nano (10^-9) units of the amount.
 The value must be between -999,999,999 and +999,999,999 inclusive.
 If `units` is positive, `nanos` must be positive or zero.
 If `units` is zero, `nanos` can be positive, zero, or negative.
 If `units` is negative, `nanos` must be negative or zero.
 For example $-1.75 is represented as `units`=-1 and `nanos`=-750,000,000. |
| short_initial_margin | Money | no | Начальные требования, сколько на счету должно быть свободных денежных средств, чтобы открыть шорт позицию, для FORTS счетов равен биржевому ГО |
| short_initial_margin.currency_code | string | no | The three-letter currency code defined in ISO 4217. |
| short_initial_margin.units | int64 | no | The whole units of the amount.
 For example if `currencyCode` is `"USD"`, then 1 unit is one US dollar. |
| short_initial_margin.nanos | int32 | no | Number of nano (10^-9) units of the amount.
 The value must be between -999,999,999 and +999,999,999 inclusive.
 If `units` is positive, `nanos` must be positive or zero.
 If `units` is zero, `nanos` can be positive, zero, or negative.
 If `units` is negative, `nanos` must be negative or zero.
 For example $-1.75 is represented as `units`=-1 and `nanos`=-750,000,000. |
| is_tradable | BoolValue | no | Доступны ли торговые операции
 Новое поле. Позволяет различать false и "не установлено". |
| is_tradable.value | bool | no | The bool value. |
| price_type | PriceType | no | Допустимая цена. Помогает определить можно ли выставлять ордера с отрицательной ценой для финансового инструмента — UNKNOWN, POSITIVE, NON_NEGATIVE, ANY |

## Response: OK

### Example

```json
{
  "symbol": "string",
  "account_id": "string",
  "tradeable": false,
  "longable": {
    "value": 0,
    "halted_days": 0
  },
  "shortable": {
    "value": 0,
    "halted_days": 0
  },
  "long_risk_rate": {
    "value": "string"
  },
  "long_collateral": {
    "currency_code": "string",
    "units": 0,
    "nanos": 0
  },
  "short_risk_rate": {
    "value": "string"
  },
  "short_collateral": {
    "currency_code": "string",
    "units": 0,
    "nanos": 0
  },
  "long_initial_margin": {
    "currency_code": "string",
    "units": 0,
    "nanos": 0
  },
  "short_initial_margin": {
    "currency_code": "string",
    "units": 0,
    "nanos": 0
  },
  "is_tradable": {
    "value": false
  },
  "price_type": 0
}
```

## Code Examples

### grpcurl

```shell
TOKEN=$(grpcurl \
  -d '{
  "secret": "YOUR_API_TOKEN"
}' \
  api.finam.ru:443 grpc.tradeapi.v1.auth.AuthService/Auth | jq -r '.token')

grpcurl \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
  "symbol": "string",
  "account_id": "string"
}' \
  api.finam.ru:443 grpc.tradeapi.v1.assets.AssetsService/GetAssetParams
```