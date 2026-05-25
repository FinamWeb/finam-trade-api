"""Unit + small-integration tests for the JWT lifecycle.

Runs against a real in-process AuthService implementation (``tests.fakes``)
so we exercise gRPC plumbing (channel, stub, stream cancellation) rather than
just mocking method calls.
"""

from __future__ import annotations

import asyncio

import grpc
import grpc.aio
import pytest

from finam_trade_api.auth import AsyncTokenManager, TokenManager
from finam_trade_api.exceptions import AuthError

from .fakes import FakeAuthService, fake_server, wait_for


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
            wait_for(lambda: auth.subscribe_calls >= 2, timeout=5.0)
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
            wait_for(lambda: auth.subscribe_calls >= 2, timeout=5.0)
            auth.push_token("after-error")
            wait_for(lambda: mgr.get_token() == "after-error")
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
async def test_async_renewal_stream_updates_token() -> None:
    auth = FakeAuthService(initial_token="t0")
    with fake_server(auth=auth) as (endpoint, _):
        channel = grpc.aio.insecure_channel(endpoint)
        mgr = AsyncTokenManager(channel, secret="s")
        try:
            await mgr.start()
            # Give the background task a chance to subscribe.
            for _ in range(200):
                if auth.subscribe_calls >= 1:
                    break
                await asyncio.sleep(0.01)
            auth.push_token("t1")
            for _ in range(200):
                if await mgr.get_token() == "t1":
                    break
                await asyncio.sleep(0.01)
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
            for _ in range(200):
                if auth.subscribe_calls >= 1:
                    break
                await asyncio.sleep(0.01)
            auth.abort_stream()
            for _ in range(500):
                if auth.subscribe_calls >= 2:
                    break
                await asyncio.sleep(0.01)
            assert auth.subscribe_calls >= 2
            auth.push_token("after-error")
            for _ in range(200):
                if await mgr.get_token() == "after-error":
                    break
                await asyncio.sleep(0.01)
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
