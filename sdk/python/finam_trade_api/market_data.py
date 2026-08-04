"""Market-data-service message types.

Re-exports the proto request/response messages used with
``client.market_data.*`` RPCs.

    from finam_trade_api.market_data import SubscribeQuoteRequest
    for tick in client.market_data.SubscribeQuote(
        SubscribeQuoteRequest(symbol="SBER@MISX")
    ):
        ...
"""

from .proto.grpc.tradeapi.v1.marketdata.marketdata_service_pb2 import (
    Bar,
    BarsRequest,
    BarsResponse,
    LatestTradesRequest,
    LatestTradesResponse,
    OrderBook,
    OrderBookRequest,
    OrderBookResponse,
    Quote,
    QuoteRequest,
    QuoteResponse,
    StreamError,
    StreamOrderBook,
    SubscribeBarsRequest,
    SubscribeBarsResponse,
    SubscribeLatestTradesRequest,
    SubscribeLatestTradesResponse,
    SubscribeOrderBookRequest,
    SubscribeOrderBookResponse,
    SubscribeQuoteRequest,
    SubscribeQuoteResponse,
    TimeFrame,
    Trade,
)

__all__ = [
    "Bar",
    "BarsRequest",
    "BarsResponse",
    "LatestTradesRequest",
    "LatestTradesResponse",
    "OrderBook",
    "OrderBookRequest",
    "OrderBookResponse",
    "Quote",
    "QuoteRequest",
    "QuoteResponse",
    "StreamError",
    "StreamOrderBook",
    "SubscribeBarsRequest",
    "SubscribeBarsResponse",
    "SubscribeLatestTradesRequest",
    "SubscribeLatestTradesResponse",
    "SubscribeOrderBookRequest",
    "SubscribeOrderBookResponse",
    "SubscribeQuoteRequest",
    "SubscribeQuoteResponse",
    "TimeFrame",
    "Trade",
]
