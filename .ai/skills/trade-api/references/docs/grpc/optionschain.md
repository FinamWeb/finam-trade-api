# OptionsChain

> Получение цепочки опционов для базового актива

**Protocol:** grpc | **Type:** unary
**Path:** /grpc.tradeapi.v1.assets.AssetsService/OptionsChain

Получение цепочки опционов для базового актива
 Пример HTTP запроса:
 GET /v1/assets/SBER@MISX/options
 Authorization: <token>

## Request

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| underlying_symbol | string | no | Символ базового актива опциона |
| root | string | no | Опциональный параметр. Актуален для опционов на фьючерсы, по типу (недельные, месячные).
 Если параметр не указан, будут возвращены опционы с ближайшей датой экспирации. |
| expiration_date | Date | no | Опциональный фильтр по дате экспирации опционов.
 Если параметр не указан, будут возвращены опционы с ближайшей датой экспирации. |
| expiration_date.year | int32 | no | Year of the date. Must be from 1 to 9999, or 0 to specify a date without
 a year. |
| expiration_date.month | int32 | no | Month of a year. Must be from 1 to 12, or 0 to specify a year without a
 month and day. |
| expiration_date.day | int32 | no | Day of a month. Must be from 1 to 31 and valid for the year and month, or 0
 to specify a year by itself or a year and month where the day isn't
 significant. |

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| symbol | string | no | Символ базового актива опциона |
| options | Option[] | yes | Информация об опционе |
| options.symbol | string | no | Символ инструмента |
| options.type | Type | no | Тип инструмента — TYPE_UNSPECIFIED, TYPE_CALL, TYPE_PUT |
| options.contract_size | Decimal | no | Лот, количество базового актива в инструменте |
| options.contract_size.value | string | no | The decimal value, as a string.

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
| options.trade_first_day | Date | no | Дата старта торговли |
| options.trade_first_day.year | int32 | no | Year of the date. Must be from 1 to 9999, or 0 to specify a date without
 a year. |
| options.trade_first_day.month | int32 | no | Month of a year. Must be from 1 to 12, or 0 to specify a year without a
 month and day. |
| options.trade_first_day.day | int32 | no | Day of a month. Must be from 1 to 31 and valid for the year and month, or 0
 to specify a year by itself or a year and month where the day isn't
 significant. |
| options.trade_last_day | Date | no | Дата окончания торговли |
| options.trade_last_day.year | int32 | no | Year of the date. Must be from 1 to 9999, or 0 to specify a date without
 a year. |
| options.trade_last_day.month | int32 | no | Month of a year. Must be from 1 to 12, or 0 to specify a year without a
 month and day. |
| options.trade_last_day.day | int32 | no | Day of a month. Must be from 1 to 31 and valid for the year and month, or 0
 to specify a year by itself or a year and month where the day isn't
 significant. |
| options.strike | Decimal | no | Цена исполнения опциона |
| options.strike.value | string | no | The decimal value, as a string.

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
| options.multiplier | Decimal | no | Множитель опциона |
| options.multiplier.value | string | no | The decimal value, as a string.

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
| options.expiration_first_day | Date | no | Дата начала экспирации |
| options.expiration_first_day.year | int32 | no | Year of the date. Must be from 1 to 9999, or 0 to specify a date without
 a year. |
| options.expiration_first_day.month | int32 | no | Month of a year. Must be from 1 to 12, or 0 to specify a year without a
 month and day. |
| options.expiration_first_day.day | int32 | no | Day of a month. Must be from 1 to 31 and valid for the year and month, or 0
 to specify a year by itself or a year and month where the day isn't
 significant. |
| options.expiration_last_day | Date | no | Дата окончания экспирации |
| options.expiration_last_day.year | int32 | no | Year of the date. Must be from 1 to 9999, or 0 to specify a date without
 a year. |
| options.expiration_last_day.month | int32 | no | Month of a year. Must be from 1 to 12, or 0 to specify a year without a
 month and day. |
| options.expiration_last_day.day | int32 | no | Day of a month. Must be from 1 to 31 and valid for the year and month, or 0
 to specify a year by itself or a year and month where the day isn't
 significant. |

## Response: OK

### Example

```json
{
  "symbol": "string",
  "options": [
    {
      "symbol": "string",
      "type": 0,
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
  "underlying_symbol": "string",
  "root": "string",
  "expiration_date": {
    "year": 0,
    "month": 0,
    "day": 0
  }
}' \
  api.finam.ru:443 grpc.tradeapi.v1.assets.AssetsService/OptionsChain
```