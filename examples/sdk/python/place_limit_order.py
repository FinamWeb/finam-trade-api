"""Place a real limit order, then attempt to cancel it.

The order can fill before cancellation. Run the read-only auth example first,
use a dedicated account, and review every value before opting in.
"""

from __future__ import annotations

import os
from uuid import uuid4

from finam_trade_api import FinamClient
from finam_trade_api.auth_messages import TokenDetailsRequest
from finam_trade_api.orders import (
    CancelOrderRequest,
    Order,
    OrderType,
    Side,
    TimeInForce,
)
from google.type.decimal_pb2 import Decimal


def main() -> None:
    secret = os.environ["TRADE_API_SECRET"]
    if os.environ.get("TRADE_API_EXECUTE") != "1":
        raise RuntimeError(
            "set TRADE_API_EXECUTE=1 to acknowledge that this example places a real order"
        )
    try:
        limit_price = os.environ["TRADE_API_LIMIT_PRICE"]
    except KeyError as exc:
        raise RuntimeError("set TRADE_API_LIMIT_PRICE to the intended limit price") from exc

    symbol = os.environ.get("TRADE_API_SYMBOL", "SBER@MISX")
    quantity = os.environ.get("TRADE_API_QUANTITY", "1")

    with FinamClient(secret=secret) as client:
        token = client.get_token()
        if token is None:
            raise RuntimeError("authentication did not return a token")

        details = client.auth.TokenDetails(TokenDetailsRequest(token=token))
        if len(details.account_ids) != 1:
            raise RuntimeError(
                f"expected exactly one available account; received {len(details.account_ids)}"
            )
        account_id = details.account_ids[0]
        order = Order(
            account_id=account_id,
            symbol=symbol,
            quantity=Decimal(value=quantity),
            side=Side.SIDE_BUY,
            type=OrderType.ORDER_TYPE_LIMIT,
            time_in_force=TimeInForce.TIME_IN_FORCE_DAY,
            limit_price=Decimal(value=limit_price),
            client_order_id=uuid4().hex[:20],
        )
        state = client.orders.PlaceOrder(order)
        print(f"Placed: {state.order_id} status={state.status}")

        cancelled = client.orders.CancelOrder(
            CancelOrderRequest(account_id=account_id, order_id=state.order_id)
        )
        print(f"Cancelled: {cancelled.order_id} status={cancelled.status}")


if __name__ == "__main__":
    main()
