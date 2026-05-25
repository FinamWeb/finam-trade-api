"""Unit tests for finam_trade_api.retry.

These exercise the backoff math and the interceptor's retry decisions without
spinning up a real gRPC channel — we feed a fake `continuation` callable into
``intercept_unary_unary`` directly.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any
from unittest.mock import MagicMock

import grpc
import pytest

from finam_trade_api.retry import (
    DEFAULT_POLICY,
    RetryPolicy,
    build_async_interceptor,
    build_sync_interceptor,
)


# ---------------------------------------------------------------------------
# RetryPolicy.backoff
# ---------------------------------------------------------------------------


def test_backoff_grows_exponentially_until_cap() -> None:
    policy = RetryPolicy(initial_backoff=1.0, max_backoff=8.0, multiplier=2.0)
    # base delays (without jitter): 1, 2, 4, 8, 8, 8...
    samples = [policy.backoff(n) for n in range(1, 7)]
    # account for up to 25% jitter
    for actual, base in zip(samples, [1.0, 2.0, 4.0, 8.0, 8.0, 8.0]):
        assert base <= actual <= base * 1.25 + 1e-9


def test_backoff_attempt_zero_is_clamped_to_initial() -> None:
    policy = RetryPolicy(initial_backoff=0.5, max_backoff=5.0, multiplier=2.0)
    delay = policy.backoff(0)
    assert 0.5 <= delay <= 0.5 * 1.25 + 1e-9


def test_default_policy_is_sensible() -> None:
    assert DEFAULT_POLICY.max_attempts >= 2
    assert DEFAULT_POLICY.initial_backoff > 0
    assert DEFAULT_POLICY.max_backoff >= DEFAULT_POLICY.initial_backoff
    assert DEFAULT_POLICY.multiplier > 1


# ---------------------------------------------------------------------------
# Sync interceptor
# ---------------------------------------------------------------------------


class _StubRpcError(grpc.RpcError):
    def __init__(self, code: grpc.StatusCode) -> None:
        self._code = code

    def code(self) -> grpc.StatusCode:
        return self._code

    def details(self) -> str:
        return f"stubbed {self._code.name}"


def _fast_policy(max_attempts: int = 3) -> RetryPolicy:
    return RetryPolicy(
        max_attempts=max_attempts,
        initial_backoff=0.001,
        max_backoff=0.002,
        multiplier=2.0,
    )


def _make_call(success: bool, code: grpc.StatusCode | None = None) -> MagicMock:
    call = MagicMock()
    if success:
        call.result.return_value = "ok"
    else:
        assert code is not None
        call.result.side_effect = _StubRpcError(code)
    return call


def test_sync_retry_succeeds_after_transient_unavailable() -> None:
    interceptor = build_sync_interceptor(_fast_policy(max_attempts=3))
    calls = [
        _make_call(False, grpc.StatusCode.UNAVAILABLE),
        _make_call(True),
    ]
    cont = MagicMock(side_effect=calls)
    result = interceptor.intercept_unary_unary(cont, MagicMock(), "req")
    assert result is calls[1]
    assert cont.call_count == 2


def test_sync_retry_gives_up_after_max_attempts() -> None:
    interceptor = build_sync_interceptor(_fast_policy(max_attempts=3))
    cont = MagicMock(
        side_effect=[_make_call(False, grpc.StatusCode.UNAVAILABLE) for _ in range(3)]
    )
    with pytest.raises(grpc.RpcError) as exc_info:
        interceptor.intercept_unary_unary(cont, MagicMock(), "req")
    assert exc_info.value.code() is grpc.StatusCode.UNAVAILABLE
    assert cont.call_count == 3


def test_sync_retry_does_not_retry_non_retryable_code() -> None:
    interceptor = build_sync_interceptor(_fast_policy(max_attempts=4))
    cont = MagicMock(side_effect=[_make_call(False, grpc.StatusCode.INVALID_ARGUMENT)])
    with pytest.raises(grpc.RpcError):
        interceptor.intercept_unary_unary(cont, MagicMock(), "req")
    assert cont.call_count == 1


def test_sync_retry_handles_resource_exhausted() -> None:
    interceptor = build_sync_interceptor(_fast_policy(max_attempts=2))
    calls = [
        _make_call(False, grpc.StatusCode.RESOURCE_EXHAUSTED),
        _make_call(True),
    ]
    cont = MagicMock(side_effect=calls)
    result = interceptor.intercept_unary_unary(cont, MagicMock(), "req")
    assert result is calls[1]


def test_sync_retry_sleeps_between_attempts() -> None:
    interceptor = build_sync_interceptor(
        RetryPolicy(max_attempts=2, initial_backoff=0.05, max_backoff=0.05, multiplier=1.0)
    )
    calls = [
        _make_call(False, grpc.StatusCode.UNAVAILABLE),
        _make_call(True),
    ]
    cont = MagicMock(side_effect=calls)
    started = time.monotonic()
    interceptor.intercept_unary_unary(cont, MagicMock(), "req")
    elapsed = time.monotonic() - started
    assert elapsed >= 0.05  # at least the configured backoff


def test_sync_interceptor_passes_streams_through_unchanged() -> None:
    interceptor = build_sync_interceptor(_fast_policy())
    sentinel = object()
    cont = MagicMock(return_value=sentinel)
    assert interceptor.intercept_unary_stream(cont, MagicMock(), "req") is sentinel
    cont.assert_called_once()


# ---------------------------------------------------------------------------
# Async interceptor
# ---------------------------------------------------------------------------


def _make_async_call(code: grpc.StatusCode) -> Any:
    call = MagicMock()

    async def _code() -> grpc.StatusCode:
        return code

    call.code = _code
    return call


@pytest.mark.asyncio
async def test_async_retry_succeeds_after_transient_unavailable() -> None:
    interceptor = build_async_interceptor(_fast_policy(max_attempts=3))
    bad = _make_async_call(grpc.StatusCode.UNAVAILABLE)
    good = _make_async_call(grpc.StatusCode.OK)

    async def cont(details: Any, request: Any) -> Any:
        return bad if cont.calls == 0 else good  # type: ignore[attr-defined]

    cont.calls = 0  # type: ignore[attr-defined]

    async def cont_tracker(details: Any, request: Any) -> Any:
        result = await cont(details, request)
        cont_tracker.count += 1  # type: ignore[attr-defined]
        cont.calls += 1  # type: ignore[attr-defined]
        return result

    cont_tracker.count = 0  # type: ignore[attr-defined]
    result = await interceptor.intercept_unary_unary(cont_tracker, MagicMock(), "req")
    assert result is good
    assert cont_tracker.count == 2  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_async_retry_gives_up_after_max_attempts() -> None:
    interceptor = build_async_interceptor(_fast_policy(max_attempts=2))

    async def cont(details: Any, request: Any) -> Any:
        cont.count += 1  # type: ignore[attr-defined]
        return _make_async_call(grpc.StatusCode.UNAVAILABLE)

    cont.count = 0  # type: ignore[attr-defined]
    result = await interceptor.intercept_unary_unary(cont, MagicMock(), "req")
    assert await result.code() is grpc.StatusCode.UNAVAILABLE
    assert cont.count == 2  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_async_retry_skips_non_retryable_code() -> None:
    interceptor = build_async_interceptor(_fast_policy(max_attempts=4))

    async def cont(details: Any, request: Any) -> Any:
        cont.count += 1  # type: ignore[attr-defined]
        return _make_async_call(grpc.StatusCode.INVALID_ARGUMENT)

    cont.count = 0  # type: ignore[attr-defined]
    result = await interceptor.intercept_unary_unary(cont, MagicMock(), "req")
    assert await result.code() is grpc.StatusCode.INVALID_ARGUMENT
    assert cont.count == 1  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_async_interceptor_passes_streams_through_unchanged() -> None:
    interceptor = build_async_interceptor(_fast_policy())
    sentinel = object()

    async def cont(details: Any, request: Any) -> Any:
        return sentinel

    assert await interceptor.intercept_unary_stream(cont, MagicMock(), "req") is sentinel
