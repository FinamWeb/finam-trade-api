"""Brand-neutral facade used by the strategy examples.

The underlying SDK remains fully available through its original public
namespace. This facade intentionally exposes only the small, stable subset used
by examples that should be portable across compatible white-label APIs.
"""

from finam_trade_api import FinamClient as Client
from finam_trade_api import from_rpc_error
from finam_trade_api.accounts import GetAccountRequest, GetAccountResponse, Position
from finam_trade_api.market_data import (
    Bar,
    BarsRequest,
    BarsResponse,
    SubscribeBarsRequest,
    SubscribeBarsResponse,
    TimeFrame,
)
from finam_trade_api.orders import (
    Order,
    OrderState,
    OrderStatus,
    OrderType,
    Side,
    TimeInForce,
)

__all__ = [
    "Bar",
    "BarsRequest",
    "BarsResponse",
    "Client",
    "GetAccountRequest",
    "GetAccountResponse",
    "Order",
    "OrderState",
    "OrderStatus",
    "OrderType",
    "Position",
    "Side",
    "SubscribeBarsRequest",
    "SubscribeBarsResponse",
    "TimeFrame",
    "TimeInForce",
    "from_rpc_error",
]
