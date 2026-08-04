"""Account-service message types.

Re-exports the proto request/response messages used with
``client.accounts.*`` RPCs so callers don't need to import them from the
deeply nested generated module path.

    from finam_trade_api.accounts import GetAccountRequest
    client.accounts.GetAccount(GetAccountRequest(account_id="A12345"))
"""

from .proto.grpc.tradeapi.v1.accounts.accounts_service_pb2 import (
    FORTS,
    MC,
    MCT,
    GetAccountRequest,
    GetAccountResponse,
    Position,
    TradesRequest,
    TradesResponse,
    Transaction,
    TransactionsRequest,
    TransactionsResponse,
)

__all__ = [
    "GetAccountRequest",
    "GetAccountResponse",
    "TradesRequest",
    "TradesResponse",
    "TransactionsRequest",
    "TransactionsResponse",
    "Position",
    "Transaction",
    "FORTS",
    "MC",
    "MCT",
]
