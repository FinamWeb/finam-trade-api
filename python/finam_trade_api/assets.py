"""Assets-service message types.

Re-exports the proto request/response messages used with
``client.assets.*`` RPCs.

    from finam_trade_api.assets import GetAssetRequest
    client.assets.GetAsset(GetAssetRequest(symbol="SBER@MISX"))
"""

from .proto.grpc.tradeapi.v1.assets.assets_service_pb2 import (
    AllAssetsRequest,
    AllAssetsResponse,
    Asset,
    AssetsRequest,
    AssetsResponse,
    ClockRequest,
    ClockResponse,
    Constituents,
    Exchange,
    ExchangesRequest,
    ExchangesResponse,
    GetAssetParamsRequest,
    GetAssetParamsResponse,
    GetAssetRequest,
    GetAssetResponse,
    GetConstituentsRequest,
    GetConstituentsResponse,
    Longable,
    Option,
    OptionsChainRequest,
    OptionsChainResponse,
    PriceType,
    ScheduleRequest,
    ScheduleResponse,
    Shortable,
)

__all__ = [
    "AllAssetsRequest",
    "AllAssetsResponse",
    "Asset",
    "AssetsRequest",
    "AssetsResponse",
    "ClockRequest",
    "ClockResponse",
    "Constituents",
    "Exchange",
    "ExchangesRequest",
    "ExchangesResponse",
    "GetAssetParamsRequest",
    "GetAssetParamsResponse",
    "GetAssetRequest",
    "GetAssetResponse",
    "GetConstituentsRequest",
    "GetConstituentsResponse",
    "Longable",
    "Option",
    "OptionsChainRequest",
    "OptionsChainResponse",
    "PriceType",
    "ScheduleRequest",
    "ScheduleResponse",
    "Shortable",
]
