# SubscribeOrderTrade

> Подписка на собственные заявки и сделки. Стрим метод

**Protocol:** grpc | **Type:** bidi-stream
**Path:** /grpc.tradeapi.v1.orders.OrdersService/SubscribeOrderTrade

## Request

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| action | Action | no | Изменение статуса подписки: подписка/отписка — ACTION_SUBSCRIBE, ACTION_UNSUBSCRIBE |
| data_type | DataType | no | Подписка только на заявки/ордера или на все сразу — DATA_TYPE_ALL, DATA_TYPE_ORDERS, DATA_TYPE_TRADES |
| account_id | string | no | Идентификатор аккаунта |

## Response

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| orders | OrderState[] | yes | Заявки |
| orders.order_id | string | no | Идентификатор заявки |
| orders.exec_id | string | no | Идентификатор исполнения |
| orders.status | OrderStatus | no | Статус заявки — ORDER_STATUS_UNSPECIFIED, ORDER_STATUS_NEW, ORDER_STATUS_PARTIALLY_FILLED, ORDER_STATUS_FILLED, ORDER_STATUS_DONE_FOR_DAY, ORDER_STATUS_CANCELED, ORDER_STATUS_REPLACED, ORDER_STATUS_PENDING_CANCEL, ORDER_STATUS_REJECTED, ORDER_STATUS_SUSPENDED, ORDER_STATUS_PENDING_NEW, ORDER_STATUS_EXPIRED, ORDER_STATUS_FAILED, ORDER_STATUS_FORWARDING, ORDER_STATUS_WAIT, ORDER_STATUS_DENIED_BY_BROKER, ORDER_STATUS_REJECTED_BY_EXCHANGE, ORDER_STATUS_WATCHING, ORDER_STATUS_EXECUTED, ORDER_STATUS_DISABLED, ORDER_STATUS_LINK_WAIT, ORDER_STATUS_SL_GUARD_TIME, ORDER_STATUS_SL_EXECUTED, ORDER_STATUS_SL_FORWARDING, ORDER_STATUS_TP_GUARD_TIME, ORDER_STATUS_TP_EXECUTED, ORDER_STATUS_TP_CORRECTION, ORDER_STATUS_TP_FORWARDING, ORDER_STATUS_TP_CORR_GUARD_TIME |
| orders.order | Order | no | Заявка |
| orders.order.account_id | string | no | Идентификатор аккаунта |
| orders.order.symbol | string | no | Символ инструмента |
| orders.order.quantity | Decimal | no | Количество в шт. |
| orders.order.quantity.value | string | no | The decimal value, as a string.

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
| orders.order.side | Side | no | Сторона (long или short) — SIDE_UNSPECIFIED, SIDE_BUY, SIDE_SELL |
| orders.order.type | OrderType | no | Тип заявки — ORDER_TYPE_UNSPECIFIED, ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT, ORDER_TYPE_STOP, ORDER_TYPE_STOP_LIMIT, ORDER_TYPE_MULTI_LEG |
| orders.order.time_in_force | TimeInForce | no | Срок действия заявки — TIME_IN_FORCE_UNSPECIFIED, TIME_IN_FORCE_DAY, TIME_IN_FORCE_GOOD_TILL_CANCEL, TIME_IN_FORCE_GOOD_TILL_CROSSING, TIME_IN_FORCE_EXT, TIME_IN_FORCE_ON_OPEN, TIME_IN_FORCE_ON_CLOSE, TIME_IN_FORCE_IOC, TIME_IN_FORCE_FOK |
| orders.order.limit_price | Decimal | no | Необходимо для лимитной и стоп лимитной заявки |
| orders.order.limit_price.value | string | no | The decimal value, as a string.

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
| orders.order.stop_price | Decimal | no | Необходимо для стоп рыночной и стоп лимитной заявки |
| orders.order.stop_price.value | string | no | The decimal value, as a string.

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
| orders.order.stop_condition | StopCondition | no | Необходимо для стоп рыночной и стоп лимитной заявки — STOP_CONDITION_UNSPECIFIED, STOP_CONDITION_LAST_UP, STOP_CONDITION_LAST_DOWN |
| orders.order.legs | Leg[] | yes | Необходимо для мульти лег заявки |
| orders.order.legs.symbol | string | no | Символ инструмента |
| orders.order.legs.quantity | Decimal | no | Количество |
| orders.order.legs.quantity.value | string | no | The decimal value, as a string.

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
| orders.order.legs.side | Side | no | Сторона — SIDE_UNSPECIFIED, SIDE_BUY, SIDE_SELL |
| orders.order.client_order_id | string | no | Уникальный идентификатор заявки. Автоматически генерируется, если не отправлен. (максимум 20 символов) |
| orders.order.valid_before | ValidBefore | no | Срок действия условной заявки. Заполняется для заявок с типом ORDER_TYPE_STOP, ORDER_TYPE_STOP_LIMIT — VALID_BEFORE_UNSPECIFIED, VALID_BEFORE_END_OF_DAY, VALID_BEFORE_GOOD_TILL_CANCEL, VALID_BEFORE_GOOD_TILL_DATE |
| orders.order.comment | string | no | Метка заявки. (максимум 128 символов) |
| orders.transact_at | Timestamp | no | Дата и время выставления заявки |
| orders.transact_at.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| orders.transact_at.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |
| orders.accept_at | Timestamp | no | Дата и время принятия заявки |
| orders.accept_at.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| orders.accept_at.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |
| orders.withdraw_at | Timestamp | no | Дата и время  отмены заявки |
| orders.withdraw_at.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| orders.withdraw_at.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |
| orders.initial_quantity | Decimal | no | Начальный объем (заполняется только для биржевой заявки) |
| orders.initial_quantity.value | string | no | The decimal value, as a string.

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
| orders.executed_quantity | Decimal | no | Исполненный объем (заполняется только для биржевой заявки) |
| orders.executed_quantity.value | string | no | The decimal value, as a string.

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
| orders.remaining_quantity | Decimal | no | Оставшийся объем (заполняется только для биржевой заявки) |
| orders.remaining_quantity.value | string | no | The decimal value, as a string.

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
| orders.sltp_order | SLTPOrder | no | Информация о SL/TP заявке |
| orders.sltp_order.account_id | string | no | Идентификатор аккаунта |
| orders.sltp_order.symbol | string | no | Символ инструмента |
| orders.sltp_order.side | Side | no | Сторона для обеих заявок — SIDE_UNSPECIFIED, SIDE_BUY, SIDE_SELL |
| orders.sltp_order.quantity_sl | Decimal | no | Количество в шт для SL |
| orders.sltp_order.quantity_sl.value | string | no | The decimal value, as a string.

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
| orders.sltp_order.sl_price | Decimal | no | Параметр условия цены для SL части |
| orders.sltp_order.sl_price.value | string | no | The decimal value, as a string.

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
| orders.sltp_order.limit_price | Decimal | no | Если указано, после активации SL будет выставлена лимитная заявка с этой ценой |
| orders.sltp_order.limit_price.value | string | no | The decimal value, as a string.

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
| orders.sltp_order.quantity_tp | Decimal | no | Количество в шт для TP |
| orders.sltp_order.quantity_tp.value | string | no | The decimal value, as a string.

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
| orders.sltp_order.tp_price | Decimal | no | Параметр условия цены для TP части |
| orders.sltp_order.tp_price.value | string | no | The decimal value, as a string.

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
| orders.sltp_order.tp_guard_spread | Decimal | no | Если указано, после активации TP будет выставлена лимитная заявка с учетом защитного спрэда |
| orders.sltp_order.tp_guard_spread.value | string | no | The decimal value, as a string.

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
| orders.sltp_order.tp_spread_measure | TPSpreadMeasure | no | Единица измерения величины защитного спреда — TP_SPREAD_MEASURE_UNDEFINED, TP_SPREAD_MEASURE_VALUE, TP_SPREAD_MEASURE_PERCENT |
| orders.sltp_order.client_order_id | string | no | Уникальный идентификатор заявки. Автоматически генерируется, если не отправлен. (максимум 20 символов) |
| orders.sltp_order.valid_before | ValidBefore | no | Срок действия условной заявки. Если не заполнено, то по умолчанию выставляется VALID_BEFORE_GOOD_TILL_CANCEL — VALID_BEFORE_UNSPECIFIED, VALID_BEFORE_END_OF_DAY, VALID_BEFORE_GOOD_TILL_CANCEL, VALID_BEFORE_GOOD_TILL_DATE |
| orders.sltp_order.valid_expiry_time | Timestamp | no | Временная метка прекращения действия SL/TP заявки |
| orders.sltp_order.valid_expiry_time.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| orders.sltp_order.valid_expiry_time.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |
| orders.sltp_order.comment | string | no | Метка заявки. (максимум 128 символов) |
| orders.triggered_order_id | string | no | Идентификатор биржевой заявки, порожденной в результате срабатывания условия или достижения стоп-цены. |
| trades | AccountTrade[] | yes | Сделки |
| trades.trade_id | string | no | Идентификатор сделки |
| trades.symbol | string | no | Символ инструмента |
| trades.price | Decimal | no | Цена исполнения |
| trades.price.value | string | no | The decimal value, as a string.

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
| trades.size | Decimal | no | Размер в шт. |
| trades.size.value | string | no | The decimal value, as a string.

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
| trades.side | Side | no | Сторона сделки (long или short) — SIDE_UNSPECIFIED, SIDE_BUY, SIDE_SELL |
| trades.timestamp | Timestamp | no | Метка времени |
| trades.timestamp.seconds | int64 | no | Represents seconds of UTC time since Unix epoch
 1970-01-01T00:00:00Z. Must be from 0001-01-01T00:00:00Z to
 9999-12-31T23:59:59Z inclusive. |
| trades.timestamp.nanos | int32 | no | Non-negative fractions of a second at nanosecond resolution. Negative
 second values with fractions must still have non-negative nanos values
 that count forward in time. Must be from 0 to 999,999,999
 inclusive. |
| trades.order_id | string | no | Идентификатор заявки |
| trades.account_id | string | no | Идентификатор аккаунта |
| trades.comment | string | no | Метка заявки. (максимум 128 символов) |
| trades.accrued_interest | Decimal | no | НКД (заполняется на следующий день после даты совершения сделки) |
| trades.accrued_interest.value | string | no | The decimal value, as a string.

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
| trades.currency | string | no | Валюта цены (например, RUB, USD, EUR)
 Примечание: поле заполняется только при использовании метода Trades
 Для SubscribeTrades данное поле может быть пустым в связи с различиями в источниках данных. При обработке сделок из подписки рекомендуется учитывать возможность пустого значения. |

## Response: OK

### Example

```json
{
  "orders": [
    {
      "order_id": "string",
      "exec_id": "string",
      "status": 0,
      "order": {
        "account_id": "string",
        "symbol": "string",
        "quantity": {
          "value": "string"
        },
        "side": 0,
        "type": 0,
        "time_in_force": 0,
        "limit_price": {
          "value": "string"
        },
        "stop_price": {
          "value": "string"
        },
        "stop_condition": 0,
        "legs": [
          {
            "symbol": "string",
            "quantity": {
              "value": "string"
            },
            "side": 0
          }
        ],
        "client_order_id": "string",
        "valid_before": 0,
        "comment": "string"
      },
      "transact_at": {
        "seconds": 0,
        "nanos": 0
      },
      "accept_at": {
        "seconds": 0,
        "nanos": 0
      },
      "withdraw_at": {
        "seconds": 0,
        "nanos": 0
      },
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
        "side": 0,
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
        "tp_spread_measure": 0,
        "client_order_id": "string",
        "valid_before": 0,
        "valid_expiry_time": {
          "seconds": 0,
          "nanos": 0
        },
        "comment": "string"
      },
      "triggered_order_id": "string"
    }
  ],
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
      "side": 0,
      "timestamp": {
        "seconds": 0,
        "nanos": 0
      },
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
  -d @ \
  api.finam.ru:443 grpc.tradeapi.v1.orders.OrdersService/SubscribeOrderTrade

# Pass data via stdin for streaming:
# echo '{
  "action": 0,
  "data_type": 0,
  "account_id": "string"
}' | grpcurl -d @ \
#   -H "Authorization: Bearer $TOKEN" \
#   api.finam.ru:443 grpc.tradeapi.v1.orders.OrdersService/SubscribeOrderTrade
```