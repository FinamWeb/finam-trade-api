"""Typed exceptions for the Finam Trade API SDK.

Maps gRPC status codes (and the HTTP responses documented in the proto annotations)
to language-native exception types so callers can catch specific failure modes
without inspecting raw status codes.
"""

from __future__ import annotations

from typing import Optional

import grpc


class FinamError(Exception):
    """Base class for all SDK-raised errors."""

    def __init__(
        self,
        message: str,
        *,
        code: Optional[grpc.StatusCode] = None,
        details: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.details = details

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.args[0]!r}, code={self.code!r})"


class AuthError(FinamError):
    """Token is missing, expired, or otherwise invalid (gRPC UNAUTHENTICATED / HTTP 401)."""


class PermissionDeniedError(FinamError):
    """Caller is authenticated but not permitted (gRPC PERMISSION_DENIED / HTTP 403)."""


class RateLimitError(FinamError):
    """Rate limit hit (gRPC RESOURCE_EXHAUSTED / HTTP 429).

    The Trade API documents a default limit of 200 requests/minute.
    """


class InvalidArgumentError(FinamError):
    """Request was malformed (gRPC INVALID_ARGUMENT / HTTP 400)."""


class NotFoundError(FinamError):
    """Requested resource does not exist (gRPC NOT_FOUND / HTTP 404)."""


class ServiceUnavailableError(FinamError):
    """Service is temporarily unavailable (gRPC UNAVAILABLE / HTTP 503)."""


class DeadlineExceededError(FinamError):
    """Deadline elapsed before the operation completed (gRPC DEADLINE_EXCEEDED / HTTP 504)."""


class InternalError(FinamError):
    """Server-side error (gRPC INTERNAL / HTTP 500)."""


_STATUS_MAP: dict[grpc.StatusCode, type[FinamError]] = {
    grpc.StatusCode.UNAUTHENTICATED: AuthError,
    grpc.StatusCode.PERMISSION_DENIED: PermissionDeniedError,
    grpc.StatusCode.RESOURCE_EXHAUSTED: RateLimitError,
    grpc.StatusCode.INVALID_ARGUMENT: InvalidArgumentError,
    grpc.StatusCode.NOT_FOUND: NotFoundError,
    grpc.StatusCode.UNAVAILABLE: ServiceUnavailableError,
    grpc.StatusCode.DEADLINE_EXCEEDED: DeadlineExceededError,
    grpc.StatusCode.INTERNAL: InternalError,
}


def from_rpc_error(err: grpc.RpcError) -> FinamError:
    """Convert a grpc.RpcError into the matching typed FinamError."""
    code = err.code() if hasattr(err, "code") else None
    details = err.details() if hasattr(err, "details") else None
    exc_type = _STATUS_MAP.get(code, FinamError) if code is not None else FinamError
    return exc_type(details or str(err), code=code, details=details)


__all__ = [
    "FinamError",
    "AuthError",
    "PermissionDeniedError",
    "RateLimitError",
    "InvalidArgumentError",
    "NotFoundError",
    "ServiceUnavailableError",
    "DeadlineExceededError",
    "InternalError",
    "from_rpc_error",
]
