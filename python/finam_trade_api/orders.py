"""Orders-service message types.

Re-exports the proto request/response messages used with
``client.orders.*`` RPCs. Includes :class:`Side` (from the shared ``side``
proto) since it's the primary type users reach for when placing orders.

    from finam_trade_api.orders import Order, OrderType, Side, TimeInForce
    client.orders.PlaceOrder(
        Order(symbol="SBER@MISX", side=Side.SIDE_BUY, type=OrderType.ORDER_TYPE_LIMIT, ...)
    )
"""

from .proto.grpc.tradeapi.v1.orders.orders_service_pb2 import (
    CancelOrderRequest,
    GetOrderRequest,
    Leg,
    Order,
    OrdersRequest,
    OrdersResponse,
    OrderState,
    OrderStatus,
    OrderTradeRequest,
    OrderTradeResponse,
    OrderType,
    SLTPOrder,
    StopCondition,
    SubscribeOrdersRequest,
    SubscribeOrdersResponse,
    SubscribeTradesRequest,
    SubscribeTradesResponse,
    TimeInForce,
    TPSpreadMeasure,
    ValidBefore,
)
from .proto.grpc.tradeapi.v1.side_pb2 import Side

__all__ = [
    "CancelOrderRequest",
    "GetOrderRequest",
    "Leg",
    "Order",
    "OrderState",
    "OrderStatus",
    "OrderTradeRequest",
    "OrderTradeResponse",
    "OrderType",
    "OrdersRequest",
    "OrdersResponse",
    "SLTPOrder",
    "Side",
    "StopCondition",
    "SubscribeOrdersRequest",
    "SubscribeOrdersResponse",
    "SubscribeTradesRequest",
    "SubscribeTradesResponse",
    "TimeInForce",
    "TPSpreadMeasure",
    "ValidBefore",
]
