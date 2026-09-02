"""Lazy access to generated gRPC service stubs."""

from typing import Any


def service_stubs() -> dict[str, type[Any]]:
    """Load generated stubs only when a client is constructed."""

    from .proto.grpc.tradeapi.v1.accounts import accounts_service_pb2_grpc
    from .proto.grpc.tradeapi.v1.assets import assets_service_pb2_grpc
    from .proto.grpc.tradeapi.v1.auth import auth_service_pb2_grpc
    from .proto.grpc.tradeapi.v1.marketdata import marketdata_service_pb2_grpc
    from .proto.grpc.tradeapi.v1.metrics import usage_metrics_service_pb2_grpc
    from .proto.grpc.tradeapi.v1.orders import orders_service_pb2_grpc
    from .proto.grpc.tradeapi.v1.reports import reports_service_pb2_grpc

    return {
        "auth": auth_service_pb2_grpc.AuthServiceStub,
        "accounts": accounts_service_pb2_grpc.AccountsServiceStub,
        "assets": assets_service_pb2_grpc.AssetsServiceStub,
        "market_data": marketdata_service_pb2_grpc.MarketDataServiceStub,
        "orders": orders_service_pb2_grpc.OrdersServiceStub,
        "reports": reports_service_pb2_grpc.ReportsServiceStub,
        "metrics": usage_metrics_service_pb2_grpc.UsageMetricsServiceStub,
    }
