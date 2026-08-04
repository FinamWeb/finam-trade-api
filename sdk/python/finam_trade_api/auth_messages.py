"""Auth-service message types.

Re-exports the proto request/response messages used with
``client.auth.*`` RPCs. Named ``auth_messages`` (not ``auth``) because
:mod:`finam_trade_api.auth` already exposes the JWT lifecycle manager.

Most callers never need these directly — :class:`~finam_trade_api.FinamClient`
fetches and refreshes the token transparently. They are exposed here only
for advanced use cases (custom token inspection, manual re-auth flows).

    from finam_trade_api.auth_messages import TokenDetailsRequest
"""

from .proto.grpc.tradeapi.v1.auth.auth_service_pb2 import (
    AuthRequest,
    AuthResponse,
    MDPermission,
    SubscribeJwtRenewalRequest,
    SubscribeJwtRenewalResponse,
    TokenDetailsRequest,
    TokenDetailsResponse,
)

__all__ = [
    "AuthRequest",
    "AuthResponse",
    "MDPermission",
    "SubscribeJwtRenewalRequest",
    "SubscribeJwtRenewalResponse",
    "TokenDetailsRequest",
    "TokenDetailsResponse",
]
