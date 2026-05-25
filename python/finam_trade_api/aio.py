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
from typing import Optional

import grpc
import grpc.aio

from ._metadata import async_call_credentials
from .auth import AsyncTokenManager
from .client import DEFAULT_ENDPOINT
from .retry import DEFAULT_POLICY, RetryPolicy, build_async_interceptor


async def _details_with_token_async(token_manager: AsyncTokenManager, details):  # type: ignore[no-untyped-def]
    token = await token_manager.get_token()
    existing = tuple(details.metadata or ())
    return details._replace(metadata=existing + (("authorization", token),))


# grpc.aio.Channel registers each interceptor into exactly one bucket based on
# the first matching isinstance() check (see grpc.aio._channel.Channel.__init__).
# That means an interceptor inheriting from multiple ClientInterceptor subtypes
# is silently ignored for all but the first matching type. To get Authorization
# headers on both unary and server-streaming calls, we register two separate
# objects — one per interface.


class _InsecureAsyncAuthUnaryInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    """Insecure-mode auth header injector for unary-unary calls."""

    def __init__(self, token_manager: AsyncTokenManager) -> None:
        self._token_manager = token_manager

    async def intercept_unary_unary(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        details = await _details_with_token_async(self._token_manager, client_call_details)
        return await continuation(details, request)


class _InsecureAsyncAuthStreamInterceptor(grpc.aio.UnaryStreamClientInterceptor):
    """Insecure-mode auth header injector for server-streaming calls."""

    def __init__(self, token_manager: AsyncTokenManager) -> None:
        self._token_manager = token_manager

    async def intercept_unary_stream(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        details = await _details_with_token_async(self._token_manager, client_call_details)
        return await continuation(details, request)

logger = logging.getLogger(__name__)


def _async_service_stubs():  # noqa: ANN202
    from .proto.grpc.tradeapi.v1.accounts import accounts_service_pb2_grpc  # type: ignore[import-not-found]
    from .proto.grpc.tradeapi.v1.assets import assets_service_pb2_grpc  # type: ignore[import-not-found]
    from .proto.grpc.tradeapi.v1.auth import auth_service_pb2_grpc  # type: ignore[import-not-found]
    from .proto.grpc.tradeapi.v1.marketdata import marketdata_service_pb2_grpc  # type: ignore[import-not-found]
    from .proto.grpc.tradeapi.v1.metrics import usage_metrics_service_pb2_grpc  # type: ignore[import-not-found]
    from .proto.grpc.tradeapi.v1.orders import orders_service_pb2_grpc  # type: ignore[import-not-found]
    from .proto.grpc.tradeapi.v1.reports import reports_service_pb2_grpc  # type: ignore[import-not-found]

    # The grpc-python generated stubs are channel-agnostic — the same stub
    # classes work for grpc.aio.Channel.
    return {
        "auth": auth_service_pb2_grpc.AuthServiceStub,
        "accounts": accounts_service_pb2_grpc.AccountsServiceStub,
        "assets": assets_service_pb2_grpc.AssetsServiceStub,
        "market_data": marketdata_service_pb2_grpc.MarketDataServiceStub,
        "orders": orders_service_pb2_grpc.OrdersServiceStub,
        "reports": reports_service_pb2_grpc.ReportsServiceStub,
        "metrics": usage_metrics_service_pb2_grpc.UsageMetricsServiceStub,
    }


class AsyncFinamClient:
    """Asyncio client for the Finam Trade API.

    Construct, then ``await client.start()`` — or use as an async context
    manager — before issuing RPCs, so the initial JWT is in hand.
    """

    def __init__(
        self,
        secret: str,
        *,
        endpoint: str = DEFAULT_ENDPOINT,
        retry_policy: RetryPolicy = DEFAULT_POLICY,
        channel_options: Optional[list[tuple[str, object]]] = None,
        insecure: bool = False,
    ) -> None:
        self._endpoint = endpoint
        self._secret = secret
        self._retry_policy = retry_policy
        self._channel_options = channel_options
        self._insecure = insecure

        self._auth_channel: Optional[grpc.aio.Channel] = None
        self._channel: Optional[grpc.aio.Channel] = None
        self._token_manager: Optional[AsyncTokenManager] = None
        self._started = False

    async def start(self) -> None:
        if self._started:
            return
        if self._insecure:
            self._auth_channel = grpc.aio.insecure_channel(
                self._endpoint, options=self._channel_options
            )
            self._token_manager = AsyncTokenManager(self._auth_channel, self._secret)
            await self._token_manager.start()
            self._channel = grpc.aio.insecure_channel(
                self._endpoint,
                options=self._channel_options,
                interceptors=[
                    _InsecureAsyncAuthUnaryInterceptor(self._token_manager),
                    _InsecureAsyncAuthStreamInterceptor(self._token_manager),
                    build_async_interceptor(self._retry_policy),
                ],
            )
        else:  # pragma: no cover - exercised against the real TLS endpoint
            transport = grpc.ssl_channel_credentials()
            self._auth_channel = grpc.aio.secure_channel(
                self._endpoint, transport, options=self._channel_options
            )
            self._token_manager = AsyncTokenManager(self._auth_channel, self._secret)
            await self._token_manager.start()

            call_creds = async_call_credentials(self._token_manager)
            composite = grpc.composite_channel_credentials(transport, call_creds)
            self._channel = grpc.aio.secure_channel(
                self._endpoint,
                composite,
                options=self._channel_options,
                interceptors=[build_async_interceptor(self._retry_policy)],
            )

        stubs = _async_service_stubs()
        self.auth = stubs["auth"](self._channel)
        self.accounts = stubs["accounts"](self._channel)
        self.assets = stubs["assets"](self._channel)
        self.market_data = stubs["market_data"](self._channel)
        self.orders = stubs["orders"](self._channel)
        self.reports = stubs["reports"](self._channel)
        self.metrics = stubs["metrics"](self._channel)
        self._started = True

    @property
    async def token(self) -> str:
        assert self._token_manager is not None, "call start() first"
        return await self._token_manager.get_token()

    async def close(self) -> None:
        if self._token_manager is not None:
            await self._token_manager.stop()
        if self._channel is not None:
            await self._channel.close()
        if self._auth_channel is not None:
            await self._auth_channel.close()

    async def __aenter__(self) -> "AsyncFinamClient":
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        await self.close()


__all__ = ["AsyncFinamClient"]
