# envelopeListener

> Клиент получает информацию в рамках своих подписок, а также служебные события и ошибки

**Protocol:** asyncapi | **Type:** subscribe
**Path:** /ws

## WsEnvelope

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| type | enum | yes | Тип сообщения — DATA, ERROR, EVENT |
| subscription_key | string | no | Опциональный идентификатор подписки (если применяется) |
| subscription_type | enum | no | Тип подписки — ORDERS, TRADES, QUOTES, ORDER_BOOK, BARS, INSTRUMENT_TRADES |
| timestamp | integer | yes | Метка времени в формате unix timestamp |
| payload | oneOf | no | Полезная нагрузка (тип зависит от subscriptionType) |
| payload (SubscribeQuoteResponse) |  |  |  |
| payload.quote | Quote[] | no |  |
| payload.quote.symbol | string | no |  |
| payload.quote.timestamp | string | no | RFC3339 timestamp |
| payload.quote.ask | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.ask_size | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.bid | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.bid_size | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.last | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.last_size | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.volume | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.turnover | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.open | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.high | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.low | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.close | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.change | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.option | object | no |  |
| payload.quote.option.open_interest | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.option.implied_volatility | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.option.theoretical_price | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.option.delta | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.option.gamma | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.option.theta | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.option.vega | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.quote.option.rho | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.error | object | no |  |
| payload.error.code | integer | no |  |
| payload.error.description | string | no |  |
| payload (SubscribeOrderBookResponse) |  |  |  |
| payload.order_book | StreamOrderBook[] | no |  |
| payload.order_book.symbol | string | no |  |
| payload.order_book.rows | object[] | no |  |
| payload.order_book.rows.price | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.order_book.rows.sell_size | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.order_book.rows.buy_size | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.order_book.rows.action | enum | no | ACTION_UNSPECIFIED, ACTION_REMOVE, ACTION_ADD, ACTION_UPDATE |
| payload.order_book.rows.mpid | string | no |  |
| payload.order_book.rows.timestamp | string | no | RFC3339 timestamp |
| payload (SubscribeLatestTradesResponse) |  |  |  |
| payload.symbol | string | no |  |
| payload.trades | Trade[] | no |  |
| payload.trades.trade_id | string | no |  |
| payload.trades.mpid | string | no |  |
| payload.trades.timestamp | string | no | RFC3339 timestamp |
| payload.trades.price | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.trades.size | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.trades.side | enum | no | SIDE_UNSPECIFIED, SIDE_BUY, SIDE_SELL |
| payload (SubscribeBarsResponse) |  |  |  |
| payload.symbol | string | no |  |
| payload.bars | Bar[] | no |  |
| payload.bars.timestamp | string | no | RFC3339 timestamp |
| payload.bars.open | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.bars.high | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.bars.low | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.bars.close | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.bars.volume | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload (SubscribeOrdersResponse) |  |  |  |
| payload.orders | OrderState[] | no |  |
| payload.orders.order_id | string | no |  |
| payload.orders.exec_id | string | no |  |
| payload.orders.status | enum | no | ORDER_STATUS_UNSPECIFIED, ORDER_STATUS_NEW, ORDER_STATUS_PARTIALLY_FILLED, ORDER_STATUS_FILLED, ORDER_STATUS_DONE_FOR_DAY, ORDER_STATUS_CANCELED, ORDER_STATUS_REPLACED, ORDER_STATUS_PENDING_CANCEL, ORDER_STATUS_REJECTED, ORDER_STATUS_SUSPENDED, ORDER_STATUS_PENDING_NEW, ORDER_STATUS_EXPIRED, ORDER_STATUS_FAILED, ORDER_STATUS_FORWARDING, ORDER_STATUS_WAIT, ORDER_STATUS_DENIED_BY_BROKER, ORDER_STATUS_REJECTED_BY_EXCHANGE, ORDER_STATUS_WATCHING, ORDER_STATUS_EXECUTED, ORDER_STATUS_DISABLED, ORDER_STATUS_LINK_WAIT, ORDER_STATUS_SL_GUARD_TIME, ORDER_STATUS_SL_EXECUTED, ORDER_STATUS_SL_FORWARDING, ORDER_STATUS_TP_GUARD_TIME, ORDER_STATUS_TP_EXECUTED, ORDER_STATUS_TP_CORRECTION, ORDER_STATUS_TP_FORWARDING, ORDER_STATUS_TP_CORR_GUARD_TIME |
| payload.orders.order | object | no |  |
| payload.orders.order.account_id | string | no |  |
| payload.orders.order.symbol | string | no |  |
| payload.orders.order.quantity | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.orders.order.side | enum | no | SIDE_UNSPECIFIED, SIDE_BUY, SIDE_SELL |
| payload.orders.order.type | enum | no | ORDER_TYPE_UNSPECIFIED, ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT, ORDER_TYPE_STOP, ORDER_TYPE_STOP_LIMIT, ORDER_TYPE_MULTI_LEG |
| payload.orders.order.time_in_force | enum | no | TIME_IN_FORCE_UNSPECIFIED, TIME_IN_FORCE_DAY, TIME_IN_FORCE_GOOD_TILL_CANCEL, TIME_IN_FORCE_GOOD_TILL_CROSSING, TIME_IN_FORCE_EXT, TIME_IN_FORCE_ON_OPEN, TIME_IN_FORCE_ON_CLOSE, TIME_IN_FORCE_IOC, TIME_IN_FORCE_FOK |
| payload.orders.order.limit_price | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.orders.order.stop_price | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.orders.order.stop_condition | enum | no | STOP_CONDITION_UNSPECIFIED, STOP_CONDITION_LAST_UP, STOP_CONDITION_LAST_DOWN |
| payload.orders.order.legs | Leg[] | no |  |
| payload.orders.order.legs.symbol | string | no |  |
| payload.orders.order.legs.quantity | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.orders.order.legs.side | enum | no | SIDE_UNSPECIFIED, SIDE_BUY, SIDE_SELL |
| payload.orders.order.client_order_id | string | no |  |
| payload.orders.order.valid_before | enum | no | VALID_BEFORE_UNSPECIFIED, VALID_BEFORE_END_OF_DAY, VALID_BEFORE_GOOD_TILL_CANCEL, VALID_BEFORE_GOOD_TILL_DATE |
| payload.orders.order.comment | string | no |  |
| payload.orders.transact_at | string | no | RFC3339 timestamp |
| payload.orders.accept_at | string | no | RFC3339 timestamp |
| payload.orders.withdraw_at | string | no | RFC3339 timestamp |
| payload (SubscribeTradesResponse) |  |  |  |
| payload.trades | AccountTrade[] | no |  |
| payload.trades.trade_id | string | no |  |
| payload.trades.symbol | string | no |  |
| payload.trades.price | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.trades.size | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.trades.side | enum | no | SIDE_UNSPECIFIED, SIDE_BUY, SIDE_SELL |
| payload.trades.timestamp | string | no | RFC3339 timestamp |
| payload.trades.order_id | string | no |  |
| payload.trades.account_id | string | no |  |
| payload.trades.comment | string | no |  |
| payload (SubscribeAccountResponse) |  |  |  |
| payload.account_id | string | no |  |
| payload.type | string | no |  |
| payload.status | string | no |  |
| payload.equity | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.unrealized_profit | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.positions | Position[] | no |  |
| payload.positions.symbol | string | no |  |
| payload.positions.quantity | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.positions.average_price | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.positions.current_price | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.positions.maintenance_margin | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.positions.daily_pnl | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.positions.unrealized_pnl | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.cash | Money[] | no |  |
| payload.cash.currencyCode | string | no |  |
| payload.cash.units | string | no |  |
| payload.cash.nanos | integer | no |  |
| payload.portfolio | oneOf | no |  |
| payload.portfolio (MC) |  |  |  |
| payload.portfolio.available_cash | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.portfolio.initial_margin | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.portfolio.maintenance_margin | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.portfolio (FORTS) |  |  |  |
| payload.portfolio.available_cash | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.portfolio.money_reserved | string | no | Decimal encoded as string (protobuf google.type.Decimal). Use string to avoid precision loss. |
| payload.open_account_date | string | no | RFC3339 timestamp |
| payload.first_trade_date | string | no | RFC3339 timestamp |
| payload.first_non_trade_date | string | no | RFC3339 timestamp |
| error_info | object | no |  |
| error_info.code | integer | yes | Код ошибки |
| error_info.type | string | yes | Тип ошибки (например INVALID_REQUEST, UNAUTHENTICATED) |
| error_info.message | string | no | Подробное сообщение об ошибке (опционально) |
| event_info | object | no |  |
| event_info.event | string | yes | Идентификатор события (например HANDSHAKE_SUCCESS, CONNECTION_CLOSED) |
| event_info.code | integer | yes | Числовой код события |
| event_info.reason | string | yes | Описание события |

## Response: WsEnvelope

### SubscribeQuoteResponse

```json
{
  "type": "DATA",
  "subscription_key": "string",
  "subscription_type": "ORDERS",
  "timestamp": 0,
  "payload": {
    "quote": [
      {
        "symbol": "string",
        "timestamp": "string",
        "ask": "string",
        "ask_size": "string",
        "bid": "string",
        "bid_size": "string",
        "last": "string",
        "last_size": "string",
        "volume": "string",
        "turnover": "string",
        "open": "string",
        "high": "string",
        "low": "string",
        "close": "string",
        "change": "string",
        "option": {
          "open_interest": "string",
          "implied_volatility": "string",
          "theoretical_price": "string",
          "delta": "string",
          "gamma": "string",
          "theta": "string",
          "vega": "string",
          "rho": "string"
        }
      }
    ],
    "error": {
      "code": 0,
      "description": "string"
    }
  },
  "error_info": {
    "code": 0,
    "type": "string",
    "message": "string"
  },
  "event_info": {
    "event": "string",
    "code": 0,
    "reason": "string"
  }
}
```

### SubscribeOrderBookResponse

```json
{
  "type": "DATA",
  "subscription_key": "string",
  "subscription_type": "ORDERS",
  "timestamp": 0,
  "payload": {
    "order_book": [
      {
        "symbol": "string",
        "rows": [
          {
            "price": "string",
            "sell_size": "string",
            "buy_size": "string",
            "action": "ACTION_UNSPECIFIED",
            "mpid": "string",
            "timestamp": "string"
          }
        ]
      }
    ]
  },
  "error_info": {
    "code": 0,
    "type": "string",
    "message": "string"
  },
  "event_info": {
    "event": "string",
    "code": 0,
    "reason": "string"
  }
}
```

### SubscribeLatestTradesResponse

```json
{
  "type": "DATA",
  "subscription_key": "string",
  "subscription_type": "ORDERS",
  "timestamp": 0,
  "payload": {
    "symbol": "string",
    "trades": [
      {
        "trade_id": "string",
        "mpid": "string",
        "timestamp": "string",
        "price": "string",
        "size": "string",
        "side": "SIDE_UNSPECIFIED"
      }
    ]
  },
  "error_info": {
    "code": 0,
    "type": "string",
    "message": "string"
  },
  "event_info": {
    "event": "string",
    "code": 0,
    "reason": "string"
  }
}
```

### SubscribeBarsResponse

```json
{
  "type": "DATA",
  "subscription_key": "string",
  "subscription_type": "ORDERS",
  "timestamp": 0,
  "payload": {
    "symbol": "string",
    "bars": [
      {
        "timestamp": "string",
        "open": "string",
        "high": "string",
        "low": "string",
        "close": "string",
        "volume": "string"
      }
    ]
  },
  "error_info": {
    "code": 0,
    "type": "string",
    "message": "string"
  },
  "event_info": {
    "event": "string",
    "code": 0,
    "reason": "string"
  }
}
```

### SubscribeOrdersResponse

```json
{
  "type": "DATA",
  "subscription_key": "string",
  "subscription_type": "ORDERS",
  "timestamp": 0,
  "payload": {
    "orders": [
      {
        "order_id": "string",
        "exec_id": "string",
        "status": "ORDER_STATUS_UNSPECIFIED",
        "order": {
          "account_id": "string",
          "symbol": "string",
          "quantity": "string",
          "side": "SIDE_UNSPECIFIED",
          "type": "ORDER_TYPE_UNSPECIFIED",
          "time_in_force": "TIME_IN_FORCE_UNSPECIFIED",
          "limit_price": "string",
          "stop_price": "string",
          "stop_condition": "STOP_CONDITION_UNSPECIFIED",
          "legs": [
            {
              "symbol": "string",
              "quantity": "string",
              "side": "SIDE_UNSPECIFIED"
            }
          ],
          "client_order_id": "string",
          "valid_before": "VALID_BEFORE_UNSPECIFIED",
          "comment": "string"
        },
        "transact_at": "string",
        "accept_at": "string",
        "withdraw_at": "string"
      }
    ]
  },
  "error_info": {
    "code": 0,
    "type": "string",
    "message": "string"
  },
  "event_info": {
    "event": "string",
    "code": 0,
    "reason": "string"
  }
}
```

### SubscribeTradesResponse

```json
{
  "type": "DATA",
  "subscription_key": "string",
  "subscription_type": "ORDERS",
  "timestamp": 0,
  "payload": {
    "trades": [
      {
        "trade_id": "string",
        "symbol": "string",
        "price": "string",
        "size": "string",
        "side": "SIDE_UNSPECIFIED",
        "timestamp": "string",
        "order_id": "string",
        "account_id": "string",
        "comment": "string"
      }
    ]
  },
  "error_info": {
    "code": 0,
    "type": "string",
    "message": "string"
  },
  "event_info": {
    "event": "string",
    "code": 0,
    "reason": "string"
  }
}
```

### SubscribeAccountResponse

```json
{
  "type": "DATA",
  "subscription_key": "string",
  "subscription_type": "ORDERS",
  "timestamp": 0,
  "payload": {
    "account_id": "string",
    "type": "string",
    "status": "string",
    "equity": "string",
    "unrealized_profit": "string",
    "positions": [
      {
        "symbol": "string",
        "quantity": "string",
        "average_price": "string",
        "current_price": "string",
        "maintenance_margin": "string",
        "daily_pnl": "string",
        "unrealized_pnl": "string"
      }
    ],
    "cash": [
      {
        "currencyCode": "string",
        "units": "string",
        "nanos": 0
      }
    ],
    "portfolio": {
      "available_cash": "string",
      "initial_margin": "string",
      "maintenance_margin": "string"
    },
    "open_account_date": "string",
    "first_trade_date": "string",
    "first_non_trade_date": "string"
  },
  "error_info": {
    "code": 0,
    "type": "string",
    "message": "string"
  },
  "event_info": {
    "event": "string",
    "code": 0,
    "reason": "string"
  }
}
```