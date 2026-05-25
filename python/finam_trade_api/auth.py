"""JWT lifecycle management for the Finam Trade API.

The Trade API issues short-lived JWTs in exchange for a long-lived API secret.
`AuthService.SubscribeJwtRenewal` is a server-streaming RPC that emits a fresh
JWT whenever the previous one is about to expire — this module consumes that
stream in the background and exposes the current token through a thread-safe /
asyncio-safe accessor used by the per-call metadata callback.

If the renewal stream drops, the manager falls back to calling `AuthService.Auth`
directly and reconnects to the stream.
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from typing import Optional

import grpc
import grpc.aio

from .exceptions import AuthError, from_rpc_error

logger = logging.getLogger(__name__)

# Imported lazily so that the package is importable even before the proto stubs
# have been generated. The generation script populates finam_trade_api.proto.
def _auth_stubs():  # noqa: ANN202
    from .proto.grpc.tradeapi.v1.auth import (  # type: ignore[import-not-found]
        auth_service_pb2,
        auth_service_pb2_grpc,
    )

    return auth_service_pb2, auth_service_pb2_grpc


class TokenManager:
    """Sync token manager — runs the renewal stream in a daemon thread."""

    def __init__(
        self,
        channel: grpc.Channel,
        secret: str,
        *,
        reconnect_initial_backoff: float = 1.0,
        reconnect_max_backoff: float = 30.0,
    ) -> None:
        self._channel = channel
        self._secret = secret
        self._token: Optional[str] = None
        self._lock = threading.Lock()
        self._ready = threading.Event()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._reconnect_initial_backoff = reconnect_initial_backoff
        self._reconnect_max_backoff = reconnect_max_backoff

    def start(self) -> None:
        """Block until the first token is available, then keep refreshing in the background."""
        pb2, pb2_grpc = _auth_stubs()
        stub = pb2_grpc.AuthServiceStub(self._channel)

        # Fetch the initial token synchronously so callers can use the client
        # immediately after start() returns.
        try:
            resp = stub.Auth(pb2.AuthRequest(secret=self._secret))
        except grpc.RpcError as exc:
            raise from_rpc_error(exc) from exc
        self._set_token(resp.token)

        self._thread = threading.Thread(
            target=self._run_renewal_loop,
            name="finam-jwt-renewal",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def get_token(self) -> str:
        self._ready.wait()
        with self._lock:
            assert self._token is not None
            return self._token

    def _set_token(self, token: str) -> None:
        with self._lock:
            self._token = token
        self._ready.set()

    def _run_renewal_loop(self) -> None:
        pb2, pb2_grpc = _auth_stubs()
        stub = pb2_grpc.AuthServiceStub(self._channel)
        backoff = self._reconnect_initial_backoff
        while not self._stop.is_set():
            try:
                stream = stub.SubscribeJwtRenewal(
                    pb2.SubscribeJwtRenewalRequest(secret=self._secret)
                )
                for msg in stream:
                    if self._stop.is_set():
                        return
                    self._set_token(msg.token)
                    backoff = self._reconnect_initial_backoff
            except grpc.RpcError as exc:
                if self._stop.is_set():
                    return
                logger.warning("JWT renewal stream dropped: %s; reconnecting in %.1fs", exc, backoff)
                time.sleep(backoff)
                backoff = min(backoff * 2, self._reconnect_max_backoff)


class AsyncTokenManager:
    """Async token manager — runs the renewal stream as an asyncio task."""

    def __init__(
        self,
        channel: grpc.aio.Channel,
        secret: str,
        *,
        reconnect_initial_backoff: float = 1.0,
        reconnect_max_backoff: float = 30.0,
    ) -> None:
        self._channel = channel
        self._secret = secret
        self._token: Optional[str] = None
        self._ready = asyncio.Event()
        self._stop = asyncio.Event()
        self._task: Optional[asyncio.Task[None]] = None
        self._reconnect_initial_backoff = reconnect_initial_backoff
        self._reconnect_max_backoff = reconnect_max_backoff

    async def start(self) -> None:
        pb2, pb2_grpc = _auth_stubs()
        stub = pb2_grpc.AuthServiceStub(self._channel)
        try:
            resp = await stub.Auth(pb2.AuthRequest(secret=self._secret))
        except grpc.aio.AioRpcError as exc:
            raise from_rpc_error(exc) from exc
        self._set_token(resp.token)
        self._task = asyncio.create_task(self._run_renewal_loop(), name="finam-jwt-renewal")

    async def stop(self) -> None:
        self._stop.set()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass

    async def get_token(self) -> str:
        await self._ready.wait()
        assert self._token is not None
        return self._token

    def _set_token(self, token: str) -> None:
        self._token = token
        self._ready.set()

    async def _run_renewal_loop(self) -> None:
        pb2, pb2_grpc = _auth_stubs()
        stub = pb2_grpc.AuthServiceStub(self._channel)
        backoff = self._reconnect_initial_backoff
        while not self._stop.is_set():
            try:
                async for msg in stub.SubscribeJwtRenewal(
                    pb2.SubscribeJwtRenewalRequest(secret=self._secret)
                ):
                    if self._stop.is_set():
                        return
                    self._set_token(msg.token)
                    backoff = self._reconnect_initial_backoff
            except grpc.aio.AioRpcError as exc:
                if self._stop.is_set():
                    return
                logger.warning(
                    "JWT renewal stream dropped: %s; reconnecting in %.1fs", exc, backoff
                )
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, self._reconnect_max_backoff)


__all__ = ["TokenManager", "AsyncTokenManager", "AuthError"]
