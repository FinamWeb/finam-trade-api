"""Reports-service message types.

Re-exports the proto request/response messages used with
``client.reports.*`` RPCs.

    from finam_trade_api.reports import CreateAccountReportRequest
"""

from .proto.grpc.tradeapi.v1.reports.reports_service_pb2 import (
    AccountReportInfo,
    CreateAccountReportRequest,
    CreateAccountReportResponse,
    DateRange,
    GetAccountReportInfoRequest,
    GetAccountReportInfoResponse,
    ReportCreationStatus,
    ReportForm,
    SubscribeAccountReportInfoRequest,
    SubscribeAccountReportInfoResponse,
)

__all__ = [
    "AccountReportInfo",
    "CreateAccountReportRequest",
    "CreateAccountReportResponse",
    "DateRange",
    "GetAccountReportInfoRequest",
    "GetAccountReportInfoResponse",
    "ReportCreationStatus",
    "ReportForm",
    "SubscribeAccountReportInfoRequest",
    "SubscribeAccountReportInfoResponse",
]
