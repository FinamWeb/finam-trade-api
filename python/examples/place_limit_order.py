"""Place a limit order, then cancel it.

This example sends a far-from-market limit order so it will not be filled
immediately, allowing the cancel to demonstrate cleanly. Do not run against
a real account without changing the symbol/price/quantity.

Usage:
    FINAM_SECRET=... FINAM_ACCOUNT_ID=... python examples/place_limit_order.py
"""

from __future__ import annotations

import os

from google.type.decimal_pb2 import Decimal  # type: ignore[import-not-found]

from finam_trade_api import FinamClient
from finam_trade_api.proto.grpc.tradeapi.v1.orders.orders_service_pb2 import (
    CancelOrderRequest,
    Order,
    OrderType,
    TimeInForce,
)
from finam_trade_api.proto.grpc.tradeapi.v1.side_pb2 import Side  # type: ignore[import-not-found]


def main() -> None:
    secret = os.environ["FINAM_SECRET"]
    account_id = os.environ["FINAM_ACCOUNT_ID"]

    with FinamClient(secret=secret) as client:
        order = Order(
            account_id=account_id,
            symbol="SBER@MISX",
            quantity=Decimal(value="1"),
            side=Side.SIDE_BUY,
            type=OrderType.ORDER_TYPE_LIMIT,
            time_in_force=TimeInForce.TIME_IN_FORCE_DAY,
            limit_price=Decimal(value="100.00"),  # far below market
            client_order_id="example-001",
        )
        state = client.orders.PlaceOrder(order)
        print(f"Placed: {state.order_id} status={state.status}")

        cancelled = client.orders.CancelOrder(
            CancelOrderRequest(account_id=account_id, order_id=state.order_id)
        )
        print(f"Cancelled: {cancelled.order_id} status={cancelled.status}")


if __name__ == "__main__":
    main()
