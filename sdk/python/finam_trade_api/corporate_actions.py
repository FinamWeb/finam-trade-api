"""Corporate-actions-service message types.

Re-exports the proto request/response messages used with
``client.corporate_actions.*`` RPCs.

    from finam_trade_api.corporate_actions import GetFutureDividendsRequest
"""

from .proto.grpc.tradeapi.v1.corporateactions.corporate_actions_service_pb2 import (
    AmortizationEventDetails,
    BondEvent,
    BondEventType,
    ConvertationType,
    CouponEventDetails,
    Dividend,
    GetFutureBondsEventsRequest,
    GetFutureBondsEventsResponse,
    GetFutureDividendsRequest,
    GetFutureDividendsResponse,
    GetFutureSplitsRequest,
    GetFutureSplitsResponse,
    GetPastBondsEventsRequest,
    GetPastBondsEventsResponse,
    GetPastDividendsRequest,
    GetPastDividendsResponse,
    GetPastSplitsRequest,
    GetPastSplitsResponse,
    OfferEventDetails,
    Pagination,
    SortDirection,
    SplitInfo,
)

__all__ = [
    "AmortizationEventDetails",
    "BondEvent",
    "BondEventType",
    "ConvertationType",
    "CouponEventDetails",
    "Dividend",
    "GetFutureBondsEventsRequest",
    "GetFutureBondsEventsResponse",
    "GetFutureDividendsRequest",
    "GetFutureDividendsResponse",
    "GetFutureSplitsRequest",
    "GetFutureSplitsResponse",
    "GetPastBondsEventsRequest",
    "GetPastBondsEventsResponse",
    "GetPastDividendsRequest",
    "GetPastDividendsResponse",
    "GetPastSplitsRequest",
    "GetPastSplitsResponse",
    "OfferEventDetails",
    "Pagination",
    "SortDirection",
    "SplitInfo",
]
