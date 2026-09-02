"""Asyncio variant of FinamClient.

Mirrors the sync client one-to-one, using grpc.aio under the hood. Streaming
RPCs return async iterators that can be consumed with ``async for``.

    async with AsyncFinamClient(secret="...") as client:
        accounts = await client.accounts.GetAccount(GetAccountRequest(account_id="A12345"))
        async for tick in client.market_data.SubscribeQuote(SubscribeQuoteRequest(symbol="SBER@MISX")):
            ...
"""

from __future__ import annotations

import logging
from types import TracebackType
from typing import TYPE_CHECKING

import grpc
import grpc.aio

from ._insecure_auth import (
    InsecureAsyncAuthStreamInterceptor,
    InsecureAsyncAuthUnaryInterceptor,
)
from ._metadata import async_call_credentials
from ._services import service_stubs
from .auth import AsyncTokenManager
from .client import DEFAULT_ENDPOINT
from .retry import DEFAULT_POLICY, RetryPolicy, build_async_interceptors

if TYPE_CHECKING:
    # The *AsyncStub classes are @type_check_only in the generated .pyi files
    # — they exist only for static analysis. At runtime the same stub class
    # handles both sync and async channels; the AsyncStub annotation tells
    # the type checker that RPCs return awaitables / async iterators.
    from .proto.grpc.tradeapi.v1.accounts.accounts_service_pb2_grpc import (
        AccountsServiceAsyncStub,
    )
    from .proto.grpc.tradeapi.v1.assets.assets_service_pb2_grpc import (
        AssetsServiceAsyncStub,
    )
    from .proto.grpc.tradeapi.v1.auth.auth_service_pb2_grpc import (
        AuthServiceAsyncStub,
    )
    from .proto.grpc.tradeapi.v1.corporateactions.corporate_actions_service_pb2_grpc import (
        CorporateActionsServiceAsyncStub,
    )
    from .proto.grpc.tradeapi.v1.marketdata.marketdata_service_pb2_grpc import (
        MarketDataServiceAsyncStub,
    )
    from .proto.grpc.tradeapi.v1.metrics.usage_metrics_service_pb2_grpc import (
        UsageMetricsServiceAsyncStub,
    )
    from .proto.grpc.tradeapi.v1.orders.orders_service_pb2_grpc import (
        OrdersServiceAsyncStub,
    )
    from .proto.grpc.tradeapi.v1.reports.reports_service_pb2_grpc import (
        ReportsServiceAsyncStub,
    )

logger = logging.getLogger(__name__)


class AsyncFinamClient:
    """Asyncio client for the Finam Trade API.

    Construct, then ``await client.start()`` — or use as an async context
    manager — before issuing RPCs, so the initial JWT is in hand.

    For local testing against an in-process fake server, construct via
    :meth:`for_testing` rather than passing ``_insecure`` directly.
    """

    def __init__(
        self,
        secret: str,
        *,
        endpoint: str = DEFAULT_ENDPOINT,
        retry_policy: RetryPolicy = DEFAULT_POLICY,
        channel_options: list[tuple[str, object]] | None = None,
        _insecure: bool = False,
    ) -> None:
        self._endpoint = endpoint
        self._secret = secret
        self._retry_policy = retry_policy
        self._channel_options = channel_options
        self._insecure = _insecure

        self._auth_channel: grpc.aio.Channel | None = None
        self._channel: grpc.aio.Channel | None = None
        self._token_manager: AsyncTokenManager | None = None
        self._started = False

    @classmethod
    def for_testing(
        cls,
        secret: str,
        *,
        endpoint: str,
        retry_policy: RetryPolicy = DEFAULT_POLICY,
        channel_options: list[tuple[str, object]] | None = None,
    ) -> AsyncFinamClient:
        """Construct an insecure (no-TLS) client for testing against an in-process
        fake server. Never use against ``api.finam.ru`` or any production endpoint."""
        return cls(
            secret,
            endpoint=endpoint,
            retry_policy=retry_policy,
            channel_options=channel_options,
            _insecure=True,
        )

    async def start(self) -> None:
        """Open channels, fetch the initial JWT, and wire up service stubs.

        If any step fails the partial state is rolled back so ``start()`` is
        safe to call again after fixing the underlying issue.
        """
        if self._started:
            return
        try:
            if self._insecure:
                await self._start_insecure()
            else:
                await self._start_secure()

            # See client.py for why the per-attribute annotations are needed.
            # The generated stub classes have an overloaded __new__ that
            # returns the AsyncStub variant when given a grpc.aio.Channel, so
            # these annotations match runtime behavior — RPC methods are typed
            # as returning awaitables / async iterators.
            stubs = service_stubs()
            # AuthService authenticates with the secret or with a token carried
            # in the request body, never with an Authorization header.
            # TokenDetails is rejected outright when one is present, so this
            # stub must not sit on the credentialed application channel.
            self.auth: AuthServiceAsyncStub = stubs["auth"](self._auth_channel)
            self.accounts: AccountsServiceAsyncStub = stubs["accounts"](self._channel)
            self.assets: AssetsServiceAsyncStub = stubs["assets"](self._channel)
            self.corporate_actions: CorporateActionsServiceAsyncStub = stubs["corporate_actions"](
                self._channel
            )
            self.market_data: MarketDataServiceAsyncStub = stubs["market_data"](self._channel)
            self.orders: OrdersServiceAsyncStub = stubs["orders"](self._channel)
            self.reports: ReportsServiceAsyncStub = stubs["reports"](self._channel)
            self.metrics: UsageMetricsServiceAsyncStub = stubs["metrics"](self._channel)
            self._started = True
        except BaseException:
            # Roll back any channels / background tasks we opened so the
            # caller doesn't leak resources on a failed start.
            await self._safe_teardown()
            raise

    async def _start_insecure(self) -> None:
        # grpc.aio takes interceptors at construction time, so the auth channel
        # is built with retries up front. It stays free of call credentials —
        # AuthService must not receive an Authorization header.
        auth_retry_unary, auth_retry_stream = build_async_interceptors(self._retry_policy)
        self._auth_channel = grpc.aio.insecure_channel(
            self._endpoint,
            options=self._channel_options,
            interceptors=[auth_retry_unary, auth_retry_stream],
        )
        self._token_manager = AsyncTokenManager(self._auth_channel, self._secret)
        await self._token_manager.start()
        retry_unary, retry_stream = build_async_interceptors(self._retry_policy)
        self._channel = grpc.aio.insecure_channel(
            self._endpoint,
            options=self._channel_options,
            interceptors=[
                InsecureAsyncAuthUnaryInterceptor(self._token_manager),
                InsecureAsyncAuthStreamInterceptor(self._token_manager),
                retry_unary,
                retry_stream,
            ],
        )

    async def _start_secure(self) -> None:  # pragma: no cover - real TLS endpoint
        transport = grpc.ssl_channel_credentials()
        # Transport credentials only, plus retries: this channel carries both
        # the JWT lifecycle RPCs and the public AuthService stub, neither of
        # which may send an Authorization header.
        auth_retry_unary, auth_retry_stream = build_async_interceptors(self._retry_policy)
        self._auth_channel = grpc.aio.secure_channel(
            self._endpoint,
            transport,
            options=self._channel_options,
            interceptors=[auth_retry_unary, auth_retry_stream],
        )
        self._token_manager = AsyncTokenManager(self._auth_channel, self._secret)
        await self._token_manager.start()

        call_creds = async_call_credentials(self._token_manager)
        composite = grpc.composite_channel_credentials(transport, call_creds)
        retry_unary, retry_stream = build_async_interceptors(self._retry_policy)
        self._channel = grpc.aio.secure_channel(
            self._endpoint,
            composite,
            options=self._channel_options,
            interceptors=[retry_unary, retry_stream],
        )

    async def _safe_teardown(self) -> None:
        """Best-effort cleanup used by both ``start()`` failure paths and
        ``close()``. Swallows errors — we are already in a teardown path."""
        if self._token_manager is not None:
            try:
                await self._token_manager.stop()
            except Exception:  # pragma: no cover - defensive log on teardown
                logger.exception("Error stopping token manager during teardown")
        if self._channel is not None:
            try:
                await self._channel.close()
            except Exception:  # pragma: no cover - defensive log on teardown
                logger.exception("Error closing application channel during teardown")
        if self._auth_channel is not None:
            try:
                await self._auth_channel.close()
            except Exception:  # pragma: no cover - defensive log on teardown
                logger.exception("Error closing auth channel during teardown")

    def get_token(self) -> str | None:
        """Return the current JWT, or ``None`` if ``start()`` has not completed.

        Sync read (no ``await``) — exposes the cached token snapshot. The token
        is refreshed in the background; callers typically don't need to read it
        at all because the SDK injects it on every RPC automatically.
        """
        if self._token_manager is None:
            return None
        return self._token_manager._token

    async def close(self) -> None:
        await self._safe_teardown()

    async def __aenter__(self) -> AsyncFinamClient:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()


__all__ = ["AsyncFinamClient"]
