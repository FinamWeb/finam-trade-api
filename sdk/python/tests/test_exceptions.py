"""Unit tests for finam_trade_api.exceptions."""

from __future__ import annotations

import grpc
import pytest

from finam_trade_api.exceptions import (
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


class _FakeRpcError(grpc.RpcError):
    def __init__(self, code: grpc.StatusCode, details: str) -> None:
        self._code = code
        self._details = details

    def code(self) -> grpc.StatusCode:
        return self._code

    def details(self) -> str:
        return self._details


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (grpc.StatusCode.UNAUTHENTICATED, AuthError),
        (grpc.StatusCode.PERMISSION_DENIED, PermissionDeniedError),
        (grpc.StatusCode.RESOURCE_EXHAUSTED, RateLimitError),
        (grpc.StatusCode.INVALID_ARGUMENT, InvalidArgumentError),
        (grpc.StatusCode.NOT_FOUND, NotFoundError),
        (grpc.StatusCode.UNAVAILABLE, ServiceUnavailableError),
        (grpc.StatusCode.DEADLINE_EXCEEDED, DeadlineExceededError),
        (grpc.StatusCode.INTERNAL, InternalError),
    ],
)
def test_known_status_codes_map_to_typed_errors(
    code: grpc.StatusCode, expected: type[FinamError]
) -> None:
    raw = _FakeRpcError(code, "boom")
    err = from_rpc_error(raw)
    assert isinstance(err, expected)
    assert err.code is code
    assert err.details == "boom"
    assert str(err) == "boom"


def test_unknown_status_code_falls_back_to_base_finam_error() -> None:
    raw = _FakeRpcError(grpc.StatusCode.ABORTED, "weird")
    err = from_rpc_error(raw)
    assert type(err) is FinamError
    assert err.code is grpc.StatusCode.ABORTED


def test_rpc_error_without_code_or_details_still_converts() -> None:
    class _BareError(grpc.RpcError):
        pass  # no code() / details() attrs

    err = from_rpc_error(_BareError("just a string"))
    assert isinstance(err, FinamError)
    assert err.code is None


def test_repr_includes_message_and_code() -> None:
    raw = _FakeRpcError(grpc.StatusCode.UNAUTHENTICATED, "expired")
    err = from_rpc_error(raw)
    assert "AuthError" in repr(err)
    assert "expired" in repr(err)
    assert "UNAUTHENTICATED" in repr(err)


def test_all_typed_errors_inherit_from_finam_error() -> None:
    for cls in (
        AuthError,
        PermissionDeniedError,
        RateLimitError,
        InvalidArgumentError,
        NotFoundError,
        ServiceUnavailableError,
        DeadlineExceededError,
        InternalError,
    ):
        assert issubclass(cls, FinamError)
