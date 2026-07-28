"""Retry policy and interceptors for transient gRPC failures.

Applies exponential backoff to unary calls that fail with UNAVAILABLE.

``RESOURCE_EXHAUSTED`` (429) is **not** retried by default — a 429 means the
server is throttling us, and blind retries amplify the throttle. We retry it
only when the server explicitly invites a retry via the
``grpc-retry-pushback-ms`` trailing metadata, in which case the pushback
delay overrides the configured backoff for that attempt.

Streaming calls are not retried automatically — the caller drives the
iteration and can re-subscribe at a meaningful point (e.g. resuming from
the last received bar).
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from typing import Optional

import grpc
import grpc.aio

logger = logging.getLogger(__name__)

_RETRY_PUSHBACK_KEY = "grpc-retry-pushback-ms"

# Status codes that are always retried (with backoff). RESOURCE_EXHAUSTED is
# handled separately — see _retry_delay_for().
_ALWAYS_RETRYABLE = frozenset({grpc.StatusCode.UNAVAILABLE})


@dataclass(frozen=True)
class RetryPolicy:
    """Exponential-backoff retry settings.

    ``max_attempts`` includes the initial attempt — 1 disables retries.
    Delay between attempts: ``min(max_backoff, initial_backoff * multiplier^(n-1))``
    plus uniform jitter in ``[0, 0.25 * delay]``.

    A ``grpc-retry-pushback-ms`` trailing metadata value from the server always
    overrides the computed delay (this is how Trade API tells clients when it's
    safe to retry after a 429).
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


def _pushback_seconds(trailing_metadata) -> Optional[float]:  # type: ignore[no-untyped-def]
    """Parse ``grpc-retry-pushback-ms`` from trailing metadata, if present."""
    if not trailing_metadata:
        return None
    for key, value in trailing_metadata:
        if key.lower() != _RETRY_PUSHBACK_KEY:
            continue
        try:
            ms = int(value)
        except (TypeError, ValueError):
            logger.warning("Malformed %s value: %r — ignoring", _RETRY_PUSHBACK_KEY, value)
            return None
        # Negative pushback is documented to mean "don't retry."
        if ms < 0:
            return None
        return ms / 1000.0
    return None


def _retry_delay_for(
    code: grpc.StatusCode,
    trailing_metadata,  # type: ignore[no-untyped-def]
    policy: RetryPolicy,
    attempt: int,
) -> Optional[float]:
    """Return the delay (seconds) to wait before retrying, or None to give up."""
    if code in _ALWAYS_RETRYABLE:
        return policy.backoff(attempt)
    if code == grpc.StatusCode.RESOURCE_EXHAUSTED:
        pushback = _pushback_seconds(trailing_metadata)
        if pushback is not None:
            return pushback
        # No pushback: do not retry. Hammering a throttled server only makes
        # things worse.
        return None
    return None


class _RetryInterceptor(
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
):
    """Sync interceptor — retries unary-unary calls on transient codes."""

    def __init__(self, policy: RetryPolicy) -> None:
        self._policy = policy

    def intercept_unary_unary(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        for attempt in range(1, self._policy.max_attempts + 1):
            call = continuation(client_call_details, request)
            try:
                call.result()
                return call
            except grpc.RpcError as exc:
                if attempt == self._policy.max_attempts:
                    raise
                delay = _retry_delay_for(
                    exc.code(), call.trailing_metadata(), self._policy, attempt
                )
                if delay is None:
                    raise
                time.sleep(delay)
        # Unreachable — the loop either returns on success or raises.
        raise RuntimeError("retry loop exited without returning or raising")  # pragma: no cover

    def intercept_unary_stream(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        # Streams are not retried — the caller drives the iteration and can
        # re-subscribe at a meaningful point (e.g. resuming from last bar).
        return continuation(client_call_details, request)


class _AsyncRetryUnaryInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    """Async unary-unary retry.

    grpc.aio.Channel dispatches each interceptor into exactly one bucket based
    on the first matching ``isinstance`` check, so an interceptor that inherits
    from multiple ClientInterceptor subtypes silently loses its registrations
    for all but the first match. Split into two classes — see also the auth
    interceptor split in ``finam_trade_api.aio``.
    """

    def __init__(self, policy: RetryPolicy) -> None:
        self._policy = policy

    async def intercept_unary_unary(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        call = await continuation(client_call_details, request)
        for attempt in range(1, self._policy.max_attempts + 1):
            code = await call.code()
            if code == grpc.StatusCode.OK:
                return call
            if attempt == self._policy.max_attempts:
                return call
            trailing = await call.trailing_metadata()
            delay = _retry_delay_for(code, trailing, self._policy, attempt)
            if delay is None:
                return call
            # Cancel the prior call so its underlying RPC and pending tasks
            # are released. Without this, retries leak ``UnaryUnaryCall``
            # objects under load and grpc.aio emits
            # "Task was destroyed but it is pending!" warnings.
            try:
                call.cancel()
            except Exception:  # noqa: BLE001 — best-effort cleanup
                pass
            await asyncio.sleep(delay)
            call = await continuation(client_call_details, request)
        return call  # pragma: no cover — loop always returns


class _AsyncRetryStreamInterceptor(grpc.aio.UnaryStreamClientInterceptor):
    """Pass-through for server-streaming RPCs — see module docstring on
    why streams are not auto-retried. Registered as a separate object so
    grpc.aio actually attaches it to the streaming bucket (see the comment
    on ``_AsyncRetryUnaryInterceptor``)."""

    def __init__(self, policy: RetryPolicy) -> None:
        self._policy = policy

    async def intercept_unary_stream(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        return await continuation(client_call_details, request)


def build_sync_interceptor(policy: RetryPolicy = DEFAULT_POLICY) -> _RetryInterceptor:
    return _RetryInterceptor(policy)


def build_async_interceptors(
    policy: RetryPolicy = DEFAULT_POLICY,
) -> tuple[_AsyncRetryUnaryInterceptor, _AsyncRetryStreamInterceptor]:
    """Return the pair of async interceptors that together cover unary + stream."""
    return _AsyncRetryUnaryInterceptor(policy), _AsyncRetryStreamInterceptor(policy)


__all__ = [
    "RetryPolicy",
    "DEFAULT_POLICY",
    "build_sync_interceptor",
    "build_async_interceptors",
]
