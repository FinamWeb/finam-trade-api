"""News-service message types.

Re-exports the proto request/response messages used with
``client.news.*`` RPCs.

    from finam_trade_api.news import GetNewsHistoryRequest
"""

from .proto.grpc.tradeapi.v1.news.news_service_pb2 import (
    GetNewsHistoryRequest,
    GetNewsHistoryResponse,
    GetNewsRequest,
    GetNewsResponse,
    GetNewsSourcesRequest,
    GetNewsSourcesResponse,
    NewsFilter,
    NewsItem,
    NewsSource,
    NewsTimeRange,
    SubscribeNewsRequest,
    SubscribeNewsResponse,
)

__all__ = [
    "GetNewsHistoryRequest",
    "GetNewsHistoryResponse",
    "GetNewsRequest",
    "GetNewsResponse",
    "GetNewsSourcesRequest",
    "GetNewsSourcesResponse",
    "NewsFilter",
    "NewsItem",
    "NewsSource",
    "NewsTimeRange",
    "SubscribeNewsRequest",
    "SubscribeNewsResponse",
]
