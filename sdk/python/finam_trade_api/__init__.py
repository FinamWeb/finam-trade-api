"""Finam Trade API — Python SDK.

Thin ergonomic wrapper over the generated gRPC stubs. Handles channel
construction, JWT issuance + auto-refresh, retries on transient failures,
and error mapping. Service methods are invoked directly on the generated
stubs (e.g. ``client.orders.PlaceOrder(...)``) using proto request/response
messages.

Public surface:

- :class:`FinamClient` — synchronous client.
- :class:`AsyncFinamClient` — asyncio client.
- :class:`RetryPolicy` — exponential-backoff configuration.
- :mod:`finam_trade_api.exceptions` — typed errors mapped from gRPC status codes.
- :func:`from_rpc_error` — convert a raw ``grpc.RpcError`` into a typed :class:`FinamError`.
"""

from importlib.metadata import version

from .aio import AsyncFinamClient
from .client import DEFAULT_ENDPOINT, FinamClient
from .exceptions import (
    AuthError,
    DeadlineExceededError,
    FinamError,
    InternalError,
    InvalidArgumentError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServiceUnavailableError,
    from_rpc_error,
)
from .retry import DEFAULT_POLICY, RetryPolicy

__version__ = version("finam-sdk")

__all__ = [
    "DEFAULT_ENDPOINT",
    "DEFAULT_POLICY",
    "AsyncFinamClient",
    "AuthError",
    "DeadlineExceededError",
    "FinamClient",
    "FinamError",
    "InternalError",
    "InvalidArgumentError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "RetryPolicy",
    "ServiceUnavailableError",
    "__version__",
    "from_rpc_error",
]
