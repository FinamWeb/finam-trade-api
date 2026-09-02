"""Synchronous Finam Trade API client.

Single entry point that owns the gRPC channel, the JWT lifecycle, and the
typed service stubs. Service stubs are exposed as attributes so callers can
invoke generated methods directly with proto messages — the wrapper only
takes care of channel setup, authentication, retries, and error mapping.

    with FinamClient(secret="...") as client:
        accounts = client.accounts.GetAccount(GetAccountRequest(account_id="A12345"))
        for tick in client.market_data.SubscribeQuote(SubscribeQuoteRequest(symbol="SBER@MISX")):
            ...
"""

from __future__ import annotations

import logging
from types import TracebackType
from typing import TYPE_CHECKING

import grpc

from ._insecure_auth import InsecureAuthInterceptor
from ._metadata import sync_call_credentials
from ._services import service_stubs
from .auth import TokenManager
from .retry import DEFAULT_POLICY, RetryPolicy, build_sync_interceptor

if TYPE_CHECKING:
    # Imported only for type checking so the package still imports cleanly
    # before scripts/generate_proto.sh has been run. At runtime the service
    # stubs are instantiated via _service_stubs() below.
    from .proto.grpc.tradeapi.v1.accounts.accounts_service_pb2_grpc import (
        AccountsServiceStub,
    )
    from .proto.grpc.tradeapi.v1.assets.assets_service_pb2_grpc import (
        AssetsServiceStub,
    )
    from .proto.grpc.tradeapi.v1.auth.auth_service_pb2_grpc import AuthServiceStub
    from .proto.grpc.tradeapi.v1.corporateactions.corporate_actions_service_pb2_grpc import (
        CorporateActionsServiceStub,
    )
    from .proto.grpc.tradeapi.v1.marketdata.marketdata_service_pb2_grpc import (
        MarketDataServiceStub,
    )
    from .proto.grpc.tradeapi.v1.metrics.usage_metrics_service_pb2_grpc import (
        UsageMetricsServiceStub,
    )
    from .proto.grpc.tradeapi.v1.orders.orders_service_pb2_grpc import (
        OrdersServiceStub,
    )
    from .proto.grpc.tradeapi.v1.reports.reports_service_pb2_grpc import (
        ReportsServiceStub,
    )

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = "api.finam.ru:443"


class FinamClient:
    """Synchronous client for the Finam Trade API.

    Args:
        secret: API secret (long-lived token) issued by the Trade API provider.
        endpoint: gRPC endpoint, e.g. ``api.finam.ru:443``.
        retry_policy: Optional retry policy override.
        channel_options: Extra gRPC channel options forwarded to ``grpc.secure_channel``.

    For local testing against an in-process fake server, construct via
    :meth:`for_testing` rather than instantiating directly.
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
        self._auth_channel: grpc.Channel | None = None
        self._auth_stub_channel: grpc.Channel | None = None
        self._channel: grpc.Channel | None = None
        self._token_manager: TokenManager | None = None

        try:
            if _insecure:
                self._auth_channel = grpc.insecure_channel(endpoint, options=channel_options)
                self._token_manager = TokenManager(self._auth_channel, secret)
                self._token_manager.start()
                self._auth_stub_channel = grpc.intercept_channel(
                    self._auth_channel, build_sync_interceptor(retry_policy)
                )
                app_channel = grpc.insecure_channel(endpoint, options=channel_options)
                self._channel = grpc.intercept_channel(
                    app_channel,
                    InsecureAuthInterceptor(self._token_manager),
                    build_sync_interceptor(retry_policy),
                )
            else:  # pragma: no cover - exercised against the real TLS endpoint
                # Auth channel uses transport credentials only; the renewal stream
                # cannot depend on a JWT it has not fetched yet.
                transport = grpc.ssl_channel_credentials()
                self._auth_channel = grpc.secure_channel(
                    endpoint, transport, options=channel_options
                )
                self._token_manager = TokenManager(self._auth_channel, secret)
                self._token_manager.start()

                # Public AuthService stub. It shares the auth channel's socket
                # but adds retries, and deliberately carries no call
                # credentials — see the self.auth assignment below.
                self._auth_stub_channel = grpc.intercept_channel(
                    self._auth_channel, build_sync_interceptor(retry_policy)
                )

                # Application channel layers the call credentials (Authorization
                # header) on top of TLS and installs the retry interceptor.
                call_creds = sync_call_credentials(self._token_manager)
                composite = grpc.composite_channel_credentials(transport, call_creds)
                app_channel = grpc.secure_channel(endpoint, composite, options=channel_options)
                self._channel = grpc.intercept_channel(
                    app_channel, build_sync_interceptor(retry_policy)
                )

            # Type annotations let Pyright/Pylance see the per-service stub
            # methods (GetAccount, Trades, …) which are otherwise assigned
            # dynamically in the generated __init__ and invisible to static
            # analysis. The stub classes' overloaded __new__ also lets a
            # checker discriminate sync vs. async based on the channel type.
            stubs = service_stubs()
            # AuthService authenticates with the secret or with a token carried
            # in the request body, never with an Authorization header.
            # TokenDetails is rejected outright when one is present, so this
            # stub must not sit on the credentialed application channel.
            self.auth: AuthServiceStub = stubs["auth"](self._auth_stub_channel)
            self.accounts: AccountsServiceStub = stubs["accounts"](self._channel)
            self.assets: AssetsServiceStub = stubs["assets"](self._channel)
            self.corporate_actions: CorporateActionsServiceStub = stubs["corporate_actions"](
                self._channel
            )
            self.market_data: MarketDataServiceStub = stubs["market_data"](self._channel)
            self.orders: OrdersServiceStub = stubs["orders"](self._channel)
            self.reports: ReportsServiceStub = stubs["reports"](self._channel)
            self.metrics: UsageMetricsServiceStub = stubs["metrics"](self._channel)
        except BaseException:
            # Roll back any channels / background threads we opened so the
            # caller doesn't leak resources on a failed construction.
            self._safe_teardown()
            raise

    @classmethod
    def for_testing(
        cls,
        secret: str,
        *,
        endpoint: str,
        retry_policy: RetryPolicy = DEFAULT_POLICY,
        channel_options: list[tuple[str, object]] | None = None,
    ) -> FinamClient:
        """Construct an insecure (no-TLS) client for testing against an in-process
        fake server. Never use against ``api.finam.ru`` or any production endpoint."""
        return cls(
            secret,
            endpoint=endpoint,
            retry_policy=retry_policy,
            channel_options=channel_options,
            _insecure=True,
        )

    def get_token(self) -> str | None:
        """Return the current JWT, or ``None`` if construction has not completed.

        The token is refreshed in the background; callers typically don't need
        to read it because the SDK injects it on every RPC automatically. Use
        this when you need to forward the JWT to a non-SDK component (e.g. a
        WebSocket bridge).
        """
        if self._token_manager is None:
            return None
        return self._token_manager._token

    def _safe_teardown(self) -> None:
        if self._token_manager is not None:
            try:
                self._token_manager.stop()
            except Exception:  # pragma: no cover - defensive log on teardown
                logger.exception("Error stopping token manager during teardown")
        if self._channel is not None:
            try:
                self._channel.close()
            except Exception:  # pragma: no cover - defensive log on teardown
                logger.exception("Error closing application channel during teardown")
        if self._auth_channel is not None:
            try:
                self._auth_channel.close()
            except Exception:  # pragma: no cover - defensive log on teardown
                logger.exception("Error closing auth channel during teardown")

    def close(self) -> None:
        self._safe_teardown()

    def __enter__(self) -> FinamClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()


__all__ = ["DEFAULT_ENDPOINT", "FinamClient"]
