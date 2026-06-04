"""Unit + small-integration tests for the JWT lifecycle.

Runs against a real in-process AuthService implementation (``tests.fakes``)
so we exercise gRPC plumbing (channel, stub, stream cancellation) rather than
just mocking method calls.
"""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import grpc
import grpc.aio
import pytest

from finam_trade_api.auth import AsyncTokenManager, TokenManager
from finam_trade_api.exceptions import AuthError

from .fakes import FakeAuthService, await_for, fake_server, wait_for


# ---------------------------------------------------------------------------
# Sync TokenManager
# ---------------------------------------------------------------------------


def test_start_blocks_until_initial_token_available() -> None:
    auth = FakeAuthService(initial_token="initial")
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.insecure_channel(endpoint)
        mgr = TokenManager(channel, secret="s3cret")
        try:
            mgr.start()
            assert mgr.get_token() == "initial"
            assert auth.auth_calls == 1
        finally:
            mgr.stop()
            auth.close_stream()
            channel.close()


def test_start_is_idempotent() -> None:
    """Calling start() twice must NOT spawn a second daemon thread or
    re-call Auth — both would race on the same token state."""
    auth = FakeAuthService(initial_token="t0")
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.insecure_channel(endpoint)
        mgr = TokenManager(channel, secret="s")
        try:
            mgr.start()
            first_thread = mgr._thread
            mgr.start()  # second call: must be a no-op
            assert mgr._thread is first_thread
            assert auth.auth_calls == 1
        finally:
            mgr.stop()
            auth.close_stream()
            channel.close()


def test_renewal_stream_updates_token() -> None:
    auth = FakeAuthService(initial_token="t0")
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.insecure_channel(endpoint)
        mgr = TokenManager(channel, secret="s")
        try:
            mgr.start()
            wait_for(lambda: auth.subscribe_calls >= 1)
            auth.push_token("t1")
            wait_for(lambda: mgr.get_token() == "t1")
            auth.push_token("t2")
            wait_for(lambda: mgr.get_token() == "t2")
        finally:
            mgr.stop()
            auth.close_stream()
            channel.close()


def test_renewal_stream_reconnects_after_drop() -> None:
    auth = FakeAuthService(initial_token="t0")
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.insecure_channel(endpoint)
        mgr = TokenManager(channel, secret="s")
        try:
            mgr.start()
            wait_for(lambda: auth.subscribe_calls >= 1)
            auth.close_stream()  # server-side: end the current stream
            # The manager should re-subscribe; observe via the subscribe counter.
            wait_for(lambda: auth.subscribe_calls >= 2)
            # And it should still propagate tokens on the new stream.
            auth.push_token("after-reconnect")
            wait_for(lambda: mgr.get_token() == "after-reconnect")
        finally:
            mgr.stop()
            auth.close_stream()
            channel.close()


def test_initial_auth_failure_raises_typed_error() -> None:
    """If the very first Auth call fails, callers should see a typed AuthError."""

    class FailingAuth(FakeAuthService):
        def Auth(self, request, context):  # type: ignore[override]
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "bad secret")

    auth = FailingAuth()
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.insecure_channel(endpoint)
        mgr = TokenManager(channel, secret="wrong")
        try:
            with pytest.raises(AuthError) as exc_info:
                mgr.start()
            assert exc_info.value.code is grpc.StatusCode.UNAUTHENTICATED
        finally:
            channel.close()


def test_renewal_stream_reconnects_after_rpc_error() -> None:
    """Exercises the `except grpc.RpcError` reconnect branch (not just clean stream end)."""
    auth = FakeAuthService(initial_token="t0")
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.insecure_channel(endpoint)
        mgr = TokenManager(
            channel,
            secret="s",
            reconnect_initial_backoff=0.01,
            reconnect_max_backoff=0.02,
        )
        try:
            mgr.start()
            wait_for(lambda: auth.subscribe_calls >= 1)
            auth.abort_stream()  # server aborts the stream with UNAVAILABLE
            wait_for(lambda: auth.subscribe_calls >= 2)
            auth.push_token("after-error")
            wait_for(lambda: mgr.get_token() == "after-error")
        finally:
            mgr.stop()
            auth.close_stream()
            channel.close()


def test_renewal_loop_recovers_from_unexpected_exception(caplog) -> None:  # noqa: ANN001
    """A non-gRPC exception in the renewal loop (e.g. a decoder bug) must NOT
    silently kill the daemon thread — that would freeze the JWT until expiry
    and surface as cryptic 401s on every subsequent RPC.

    We provoke a RuntimeError inside the loop via a one-shot patch on
    ``_set_token``, then verify (a) the loop logged the error and (b) the
    daemon thread is still alive afterwards (so token refreshes will continue
    on subsequent renewals)."""
    import logging

    auth = FakeAuthService(initial_token="t0")
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.insecure_channel(endpoint)
        mgr = TokenManager(
            channel,
            secret="s",
            reconnect_initial_backoff=0.01,
            reconnect_max_backoff=0.02,
        )
        try:
            mgr.start()
            wait_for(lambda: auth.subscribe_calls >= 1)

            calls = {"n": 0}
            original = mgr._set_token

            def flaky_set(token: str) -> None:
                calls["n"] += 1
                if calls["n"] == 1:
                    raise RuntimeError("simulated decoder bug")
                original(token)

            with caplog.at_level(logging.ERROR, logger="finam_trade_api.auth"):
                with patch.object(mgr, "_set_token", side_effect=flaky_set):
                    auth.push_token("triggers-exception")
                    # Wait until the loop has logged the unexpected exception.
                    wait_for(
                        lambda: any(
                            "Unexpected error in JWT renewal loop" in r.message
                            for r in caplog.records
                        )
                    )

            # Crucial: the daemon thread must still be alive — that's how we
            # know the exception was caught instead of killing the loop.
            assert mgr._thread is not None and mgr._thread.is_alive()
        finally:
            mgr.stop()
            auth.close_stream()
            channel.close()


def test_stop_is_idempotent_and_safe_after_partial_start() -> None:
    auth = FakeAuthService()
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.insecure_channel(endpoint)
        mgr = TokenManager(channel, secret="s")
        mgr.start()
        mgr.stop()
        mgr.stop()  # second call must not raise
        auth.close_stream()
        channel.close()


# ---------------------------------------------------------------------------
# Async TokenManager
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_start_returns_with_initial_token() -> None:
    auth = FakeAuthService(initial_token="async-initial")
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.aio.insecure_channel(endpoint)
        mgr = AsyncTokenManager(channel, secret="s")
        try:
            await mgr.start()
            assert await mgr.get_token() == "async-initial"
            assert auth.auth_calls == 1
        finally:
            await mgr.stop()
            auth.close_stream()
            await channel.close()


@pytest.mark.asyncio
async def test_async_start_is_idempotent() -> None:
    auth = FakeAuthService()
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.aio.insecure_channel(endpoint)
        mgr = AsyncTokenManager(channel, secret="s")
        try:
            await mgr.start()
            first_task = mgr._task
            await mgr.start()  # must be a no-op
            assert mgr._task is first_task
            assert auth.auth_calls == 1
        finally:
            await mgr.stop()
            auth.close_stream()
            await channel.close()


@pytest.mark.asyncio
async def test_async_renewal_stream_updates_token() -> None:
    auth = FakeAuthService(initial_token="t0")
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.aio.insecure_channel(endpoint)
        mgr = AsyncTokenManager(channel, secret="s")
        try:
            await mgr.start()
            await await_for(lambda: auth.subscribe_calls >= 1)
            auth.push_token("t1")
            await await_for(lambda: mgr._token == "t1")
            assert await mgr.get_token() == "t1"
        finally:
            await mgr.stop()
            auth.close_stream()
            await channel.close()


@pytest.mark.asyncio
async def test_async_renewal_stream_reconnects_after_rpc_error() -> None:
    auth = FakeAuthService(initial_token="t0")
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.aio.insecure_channel(endpoint)
        mgr = AsyncTokenManager(
            channel,
            secret="s",
            reconnect_initial_backoff=0.01,
            reconnect_max_backoff=0.02,
        )
        try:
            await mgr.start()
            await await_for(lambda: auth.subscribe_calls >= 1)
            auth.abort_stream()
            await await_for(lambda: auth.subscribe_calls >= 2)
            auth.push_token("after-error")
            await await_for(lambda: mgr._token == "after-error")
            assert await mgr.get_token() == "after-error"
        finally:
            await mgr.stop()
            auth.close_stream()
            await channel.close()


@pytest.mark.asyncio
async def test_async_initial_auth_failure_raises_typed_error() -> None:
    class FailingAuth(FakeAuthService):
        def Auth(self, request, context):  # type: ignore[override]
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "bad secret")

    auth = FailingAuth()
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.aio.insecure_channel(endpoint)
        mgr = AsyncTokenManager(channel, secret="wrong")
        try:
            with pytest.raises(AuthError):
                await mgr.start()
        finally:
            await channel.close()


@pytest.mark.asyncio
async def test_async_stop_logs_but_does_not_propagate_unexpected_failure() -> None:
    """If the renewal task happens to raise on shutdown, stop() must log
    and return cleanly — teardown callers expect close() to succeed."""
    auth = FakeAuthService()
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.aio.insecure_channel(endpoint)
        mgr = AsyncTokenManager(channel, secret="s")
        try:
            await mgr.start()
            await await_for(lambda: auth.subscribe_calls >= 1)
            # No assertion failure here — we just want stop() to be safe.
            await mgr.stop()
            await mgr.stop()  # also idempotent on the async side
        finally:
            auth.close_stream()
            await channel.close()


@pytest.mark.asyncio
async def test_async_renewal_loop_recovers_from_unexpected_exception(caplog) -> None:  # noqa: ANN001
    """Async equivalent of the sync ``test_renewal_loop_recovers_*`` test —
    a non-gRPC exception inside the async loop must be caught, logged, and
    NOT cancel the renewal task."""
    import logging

    auth = FakeAuthService(initial_token="t0")
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.aio.insecure_channel(endpoint)
        mgr = AsyncTokenManager(
            channel,
            secret="s",
            reconnect_initial_backoff=0.01,
            reconnect_max_backoff=0.02,
        )
        try:
            await mgr.start()
            await await_for(lambda: auth.subscribe_calls >= 1)

            calls = {"n": 0}
            original = mgr._set_token

            def flaky_set(token: str) -> None:
                calls["n"] += 1
                if calls["n"] == 1:
                    raise RuntimeError("simulated async decoder bug")
                original(token)

            with caplog.at_level(logging.ERROR, logger="finam_trade_api.auth"):
                with patch.object(mgr, "_set_token", side_effect=flaky_set):
                    auth.push_token("triggers-exception")
                    await await_for(
                        lambda: any(
                            "Unexpected error in JWT renewal loop" in r.message
                            for r in caplog.records
                        )
                    )

            # Task is still running — it didn't die from the exception.
            assert mgr._task is not None and not mgr._task.done()
        finally:
            await mgr.stop()
            auth.close_stream()
            await channel.close()


@pytest.mark.asyncio
async def test_async_stop_logs_unexpected_task_failure_without_propagating(
    caplog,  # noqa: ANN001
) -> None:
    """The renewal task's unexpected-exception arm should never normally raise,
    but if a future code change introduces a bug, ``stop()`` must still
    return cleanly so the surrounding ``close()`` call doesn't propagate."""
    import logging

    auth = FakeAuthService()
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.aio.insecure_channel(endpoint)
        mgr = AsyncTokenManager(channel, secret="s")
        try:
            await mgr.start()

            # Replace the task with one that raises a non-Cancelled exception
            # on await — simulates a hypothetical bug surfacing only at shutdown.
            real_task = mgr._task

            async def boom() -> None:
                raise RuntimeError("simulated shutdown failure")

            mgr._task = asyncio.create_task(boom())
            # Let it actually run so the exception is raised before stop().
            await asyncio.sleep(0)

            with caplog.at_level(logging.ERROR, logger="finam_trade_api.auth"):
                # Must not raise even though the underlying task did.
                await mgr.stop()

            assert any(
                "JWT renewal task raised on shutdown" in r.message
                for r in caplog.records
            )

            # Tidy up the real renewal task we displaced so it doesn't leak.
            real_task.cancel()
            try:
                await real_task
            except (asyncio.CancelledError, Exception):
                pass
        finally:
            auth.close_stream()
            await channel.close()
