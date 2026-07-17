# GetPastSplits

> Получить историю сплитов по инструменту

**Protocol:** grpc | **Type:** unary
**Path:** /grpc.tradeapi.v1.corporateactions.CorporateActionsService/GetPastSplits

## Request

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| symbol | string | no | Символ инструмента |
| date_from | Date | no | Начало временного интервала |
| date_from.year | int32 | no | Year of the date. Must be from 1 to 9999, or 0 to specify a date without
 a year. |
| date_from.month | int32 | no | Month of a year. Must be from 1 to 12, or 0 to specify a year without a
 month and day. |
| date_from.day | int32 | no | Day of a month. Must be from 1 to 31 and valid for the year and month, or 0
 to specify a year by itself or a year and month where the day isn't
 significant. |
| date_to | Date | no | Конец временного интервала |
| date_to.year | int32 | no | Year of the date. Must be from 1 to 9999, or 0 to specify a date without
 a year. |
| date_to.month | int32 | no | Month of a year. Must be from 1 to 12, or 0 to specify a year without a
 month and day. |
| date_to.day | int32 | no | Day of a month. Must be from 1 to 31 and valid for the year and month, or 0
 to specify a year by itself or a year and month where the day isn't
 significant. |
| sort_direction | SortDirection | no | Направление сортировки по дате: asc — от старых к новым, desc — от новых к старым — ASC, DESC |
| limit | int32 | no | Лимит. Ограничивает количество возвращаемых сплитов в списке |
| offset | int32 | no | Смещение. Указывает количество сплитов, которые нужно пропустить перед тем, как начать возвращать результат |

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| symbol | string | no | Символ инструмента |
| pagination | Pagination | no | Параметры пагинации |
| pagination.total | int32 | no | Общее количество элементов |
| pagination.limit | int32 | no | Лимит. Ограничивает количество возвращаемых элементов |
| pagination.offset | int32 | no | Смещение. Указывает количество элементов, которые нужно пропустить перед тем, как начать возвращать результат |
| pagination.has_next | bool | no | Флаг следующей страницы. Указывает, существует ли следующая страница данных |
| splits | SplitInfo[] | yes | Информация о сплитах |
| splits.exec_date | Date | no | Дата вступления в силу корпоративного действия (дата исполнения) |
| splits.exec_date.year | int32 | no | Year of the date. Must be from 1 to 9999, or 0 to specify a date without
 a year. |
| splits.exec_date.month | int32 | no | Month of a year. Must be from 1 to 12, or 0 to specify a year without a
 month and day. |
| splits.exec_date.day | int32 | no | Day of a month. Must be from 1 to 31 and valid for the year and month, or 0
 to specify a year by itself or a year and month where the day isn't
 significant. |
| splits.old_ratio | Decimal | no | Количество ценных бумаг до проведения конвертации (числитель коэффициента) |
| splits.old_ratio.value | string | no | The decimal value, as a string.

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
| splits.new_ratio | Decimal | no | Количество ценных бумаг после проведения конвертации (знаменатель коэффициента) |
| splits.new_ratio.value | string | no | The decimal value, as a string.

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
| splits.new_lot | Int32Value | no | Новый размер лота инструмента после исполнения корпоративного действия |
| splits.new_lot.value | int32 | no | The int32 value. |
| splits.convertation_type | ConvertationType | no | Тип события (сплит / консолидация и т.д.) — CONVTYPE_UNKNOWN, BUYBACK, CALL_OPTION_EXERCISED, DRAWINGS, DRAWINGS_BY_LOTTERY, EARLY_CONVERSION, MATURITY, ORDINARY, PUT_OPTION_EXERCISED, TENDER_OFFER |

## Response: OK

### Example

```json
{
  "symbol": "string",
  "pagination": {
    "total": 0,
    "limit": 0,
    "offset": 0,
    "has_next": false
  },
  "splits": [
    {
      "exec_date": {
        "year": 0,
        "month": 0,
        "day": 0
      },
      "old_ratio": {
        "value": "string"
      },
      "new_ratio": {
        "value": "string"
      },
      "new_lot": {
        "value": 0
      },
      "convertation_type": 0
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
  "symbol": "string",
  "date_from": {
    "year": 0,
    "month": 0,
    "day": 0
  },
  "date_to": {
    "year": 0,
    "month": 0,
    "day": 0
  },
  "sort_direction": 0,
  "limit": 0,
  "offset": 0
}' \
  api.finam.ru:443 grpc.tradeapi.v1.corporateactions.CorporateActionsService/GetPastSplits
```