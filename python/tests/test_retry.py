"""Unit tests for finam_trade_api.retry.

These exercise the backoff math and the interceptor's retry decisions without
spinning up a real gRPC channel — we feed a fake ``continuation`` callable
into ``intercept_unary_unary`` directly.
"""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import grpc
import pytest

from finam_trade_api.retry import (
    DEFAULT_POLICY,
    RetryPolicy,
    build_async_interceptors,
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


def _make_call(
    success: bool,
    code: grpc.StatusCode | None = None,
    trailing_metadata: tuple = (),
) -> MagicMock:
    call = MagicMock()
    call.trailing_metadata.return_value = trailing_metadata
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


def test_sync_retry_does_NOT_retry_resource_exhausted_without_pushback() -> None:
    """RESOURCE_EXHAUSTED (429) means 'you are being throttled' — blind retries
    just amplify the throttle, so the default behaviour is to give up
    immediately. See finam_trade_api/retry.py module docstring."""
    interceptor = build_sync_interceptor(_fast_policy(max_attempts=4))
    cont = MagicMock(side_effect=[_make_call(False, grpc.StatusCode.RESOURCE_EXHAUSTED)])
    with pytest.raises(grpc.RpcError):
        interceptor.intercept_unary_unary(cont, MagicMock(), "req")
    assert cont.call_count == 1


def test_sync_retry_DOES_retry_resource_exhausted_when_pushback_present() -> None:
    """If the server attaches grpc-retry-pushback-ms it is explicitly inviting
    a retry after the given delay."""
    interceptor = build_sync_interceptor(_fast_policy(max_attempts=3))
    calls = [
        _make_call(
            False,
            grpc.StatusCode.RESOURCE_EXHAUSTED,
            trailing_metadata=(("grpc-retry-pushback-ms", "5"),),
        ),
        _make_call(True),
    ]
    cont = MagicMock(side_effect=calls)
    result = interceptor.intercept_unary_unary(cont, MagicMock(), "req")
    assert result is calls[1]
    assert cont.call_count == 2


def test_sync_retry_respects_negative_pushback_as_do_not_retry() -> None:
    """A negative pushback value documented to mean 'do not retry'."""
    interceptor = build_sync_interceptor(_fast_policy(max_attempts=4))
    cont = MagicMock(
        side_effect=[
            _make_call(
                False,
                grpc.StatusCode.RESOURCE_EXHAUSTED,
                trailing_metadata=(("grpc-retry-pushback-ms", "-1"),),
            )
        ]
    )
    with pytest.raises(grpc.RpcError):
        interceptor.intercept_unary_unary(cont, MagicMock(), "req")
    assert cont.call_count == 1


def test_sync_retry_ignores_malformed_pushback() -> None:
    """A malformed grpc-retry-pushback-ms value should be ignored (logged)
    and the default policy applied — which for RESOURCE_EXHAUSTED means
    'give up'."""
    interceptor = build_sync_interceptor(_fast_policy(max_attempts=4))
    cont = MagicMock(
        side_effect=[
            _make_call(
                False,
                grpc.StatusCode.RESOURCE_EXHAUSTED,
                trailing_metadata=(("grpc-retry-pushback-ms", "not-a-number"),),
            )
        ]
    )
    with pytest.raises(grpc.RpcError):
        interceptor.intercept_unary_unary(cont, MagicMock(), "req")
    assert cont.call_count == 1


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


def _make_async_call(
    code: grpc.StatusCode, trailing_metadata: tuple = ()
) -> Any:
    """Build a fake grpc.aio call. ``code()`` and ``trailing_metadata()`` are
    coroutines on real grpc.aio calls — we model them with AsyncMock so the
    interceptor's ``await`` works unchanged. ``cancel()`` is plain sync."""
    call = MagicMock()
    call.code = AsyncMock(return_value=code)
    call.trailing_metadata = AsyncMock(return_value=trailing_metadata)
    return call


def test_async_build_returns_pair_of_interceptors() -> None:
    """The async builder must return two distinct objects (one per interface),
    otherwise grpc.aio's first-match dispatch silently drops the stream side."""
    unary, stream = build_async_interceptors(_fast_policy())
    assert isinstance(unary, grpc.aio.UnaryUnaryClientInterceptor)
    assert isinstance(stream, grpc.aio.UnaryStreamClientInterceptor)
    # And NOT cross-registered, which is exactly the bug we're guarding against.
    assert not isinstance(unary, grpc.aio.UnaryStreamClientInterceptor)
    assert not isinstance(stream, grpc.aio.UnaryUnaryClientInterceptor)


@pytest.mark.asyncio
async def test_async_retry_succeeds_after_transient_unavailable() -> None:
    unary, _ = build_async_interceptors(_fast_policy(max_attempts=3))
    bad = _make_async_call(grpc.StatusCode.UNAVAILABLE)
    good = _make_async_call(grpc.StatusCode.OK)
    cont = AsyncMock(side_effect=[bad, good])

    result = await unary.intercept_unary_unary(cont, MagicMock(), "req")
    assert result is good
    assert cont.call_count == 2
    # Critical: the failed first call must be cancelled so it doesn't leak.
    bad.cancel.assert_called_once()


@pytest.mark.asyncio
async def test_async_retry_gives_up_after_max_attempts() -> None:
    unary, _ = build_async_interceptors(_fast_policy(max_attempts=2))
    calls = [
        _make_async_call(grpc.StatusCode.UNAVAILABLE),
        _make_async_call(grpc.StatusCode.UNAVAILABLE),
    ]
    cont = AsyncMock(side_effect=calls)
    result = await unary.intercept_unary_unary(cont, MagicMock(), "req")
    assert await result.code() is grpc.StatusCode.UNAVAILABLE
    assert cont.call_count == 2


@pytest.mark.asyncio
async def test_async_retry_skips_non_retryable_code() -> None:
    unary, _ = build_async_interceptors(_fast_policy(max_attempts=4))
    call = _make_async_call(grpc.StatusCode.INVALID_ARGUMENT)
    cont = AsyncMock(return_value=call)
    result = await unary.intercept_unary_unary(cont, MagicMock(), "req")
    assert await result.code() is grpc.StatusCode.INVALID_ARGUMENT
    assert cont.call_count == 1


@pytest.mark.asyncio
async def test_async_retry_does_NOT_retry_resource_exhausted_without_pushback() -> None:
    unary, _ = build_async_interceptors(_fast_policy(max_attempts=4))
    call = _make_async_call(grpc.StatusCode.RESOURCE_EXHAUSTED)
    cont = AsyncMock(return_value=call)
    result = await unary.intercept_unary_unary(cont, MagicMock(), "req")
    assert await result.code() is grpc.StatusCode.RESOURCE_EXHAUSTED
    assert cont.call_count == 1


@pytest.mark.asyncio
async def test_async_retry_honors_pushback_metadata() -> None:
    unary, _ = build_async_interceptors(_fast_policy(max_attempts=3))
    bad = _make_async_call(
        grpc.StatusCode.RESOURCE_EXHAUSTED,
        trailing_metadata=(("grpc-retry-pushback-ms", "5"),),
    )
    good = _make_async_call(grpc.StatusCode.OK)
    cont = AsyncMock(side_effect=[bad, good])
    result = await unary.intercept_unary_unary(cont, MagicMock(), "req")
    assert result is good
    assert cont.call_count == 2


@pytest.mark.asyncio
async def test_async_stream_interceptor_passes_through_unchanged() -> None:
    _, stream = build_async_interceptors(_fast_policy())
    sentinel = object()
    cont = AsyncMock(return_value=sentinel)
    assert (
        await stream.intercept_unary_stream(cont, MagicMock(), "req") is sentinel
    )


@pytest.mark.asyncio
async def test_async_retry_tolerates_cancel_raising_on_old_call() -> None:
    """If ``call.cancel()`` raises (e.g. on a call that already completed), the
    retry must continue anyway — cancellation is best-effort cleanup."""
    unary, _ = build_async_interceptors(_fast_policy(max_attempts=3))
    bad = _make_async_call(grpc.StatusCode.UNAVAILABLE)
    # Force cancel() to raise. The retry should still move on to the next call.
    bad.cancel = MagicMock(side_effect=RuntimeError("cancel exploded"))
    good = _make_async_call(grpc.StatusCode.OK)
    cont = AsyncMock(side_effect=[bad, good])

    result = await unary.intercept_unary_unary(cont, MagicMock(), "req")
    assert result is good


# ---------------------------------------------------------------------------
# _pushback_seconds helper — covers parsing edge cases not reached via the
# integration paths.
# ---------------------------------------------------------------------------


def test_pushback_parsing_handles_no_trailing_metadata() -> None:
    from finam_trade_api.retry import _pushback_seconds

    assert _pushback_seconds(None) is None
    assert _pushback_seconds(()) is None


def test_pushback_parsing_ignores_unrelated_metadata_keys() -> None:
    from finam_trade_api.retry import _pushback_seconds

    assert _pushback_seconds((("content-type", "application/grpc"),)) is None
