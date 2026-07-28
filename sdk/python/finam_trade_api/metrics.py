"""Usage-metrics-service message types.

Re-exports the proto request/response messages used with
``client.metrics.*`` RPCs.

    from finam_trade_api.metrics import GetUsageMetricsRequest
"""

from .proto.grpc.tradeapi.v1.metrics.usage_metrics_service_pb2 import (
    GetUsageMetricsRequest,
    GetUsageMetricsResponse,
)

__all__ = ["GetUsageMetricsRequest", "GetUsageMetricsResponse"]
