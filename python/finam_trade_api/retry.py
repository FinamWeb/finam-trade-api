"""Retry policy and interceptors for transient gRPC failures.

Applies exponential backoff to unary calls that fail with UNAVAILABLE (503)
or RESOURCE_EXHAUSTED (429). Streaming calls are not retried automatically —
the caller is expected to handle reconnection at the iteration boundary.
"""

from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass

import grpc
import grpc.aio

_RETRYABLE = frozenset(
    {
        grpc.StatusCode.UNAVAILABLE,
        grpc.StatusCode.RESOURCE_EXHAUSTED,
    }
)


@dataclass(frozen=True)
class RetryPolicy:
    """Exponential-backoff retry settings.

    `max_attempts` includes the initial attempt — 1 disables retries.
    Delay between attempts: min(max_backoff, initial_backoff * multiplier^(n-1))
    plus uniform jitter in [0, 0.25 * delay].
    """

    max_attempts: int = 4
    initial_backoff: float = 0.2
    max_backoff: float = 5.0
    multiplier: float = 2.0

    def backoff(self, attempt: int) -> float:
        delay = min(
            self.max_backoff,
            self.initial_backoff * (self.multiplier ** max(0, attempt - 1)),
        )
        return delay + random.uniform(0, 0.25 * delay)


DEFAULT_POLICY = RetryPolicy()


class _RetryInterceptor(
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
):
    """Sync interceptor — retries unary-unary calls on transient codes."""

    def __init__(self, policy: RetryPolicy) -> None:
        self._policy = policy

    def intercept_unary_unary(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        last_exc: grpc.RpcError | None = None
        for attempt in range(1, self._policy.max_attempts + 1):
            call = continuation(client_call_details, request)
            try:
                # Force materialization to surface RpcError synchronously.
                call.result()
                return call
            except grpc.RpcError as exc:
                last_exc = exc
                if exc.code() not in _RETRYABLE or attempt == self._policy.max_attempts:
                    raise
                time.sleep(self._policy.backoff(attempt))
        assert last_exc is not None
        raise last_exc

    def intercept_unary_stream(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        # Streams are not retried — the caller drives the iteration and can
        # re-subscribe at a meaningful point (e.g. resuming from last bar).
        return continuation(client_call_details, request)


class _AsyncRetryInterceptor(
    grpc.aio.UnaryUnaryClientInterceptor,
    grpc.aio.UnaryStreamClientInterceptor,
):
    """Async interceptor — same policy, asyncio-friendly sleep."""

    def __init__(self, policy: RetryPolicy) -> None:
        self._policy = policy

    async def intercept_unary_unary(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        for attempt in range(1, self._policy.max_attempts + 1):
            call = await continuation(client_call_details, request)
            code = await call.code()
            if code == grpc.StatusCode.OK:
                return call
            if code not in _RETRYABLE or attempt == self._policy.max_attempts:
                return call
            await asyncio.sleep(self._policy.backoff(attempt))
        return call  # pragma: no cover — loop always returns

    async def intercept_unary_stream(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        return await continuation(client_call_details, request)


def build_sync_interceptor(policy: RetryPolicy = DEFAULT_POLICY) -> _RetryInterceptor:
    return _RetryInterceptor(policy)


def build_async_interceptor(policy: RetryPolicy = DEFAULT_POLICY) -> _AsyncRetryInterceptor:
    return _AsyncRetryInterceptor(policy)


__all__ = ["RetryPolicy", "DEFAULT_POLICY", "build_sync_interceptor", "build_async_interceptor"]
