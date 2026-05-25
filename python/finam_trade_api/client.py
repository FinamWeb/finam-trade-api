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
from typing import Optional

import grpc

from ._metadata import sync_call_credentials
from .auth import TokenManager
from .retry import DEFAULT_POLICY, RetryPolicy, build_sync_interceptor

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = "api.finam.ru:443"


class _InsecureAuthInterceptor(
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
    grpc.StreamUnaryClientInterceptor,
    grpc.StreamStreamClientInterceptor,
):
    """Attaches the current JWT as Authorization metadata on every call.

    Used only when the client is constructed via :meth:`FinamClient.for_testing`
    — gRPC forbids attaching ``CallCredentials`` to insecure channels, so we
    cannot use the normal ``metadata_call_credentials`` path in that mode.
    """

    def __init__(self, token_manager: TokenManager) -> None:
        self._token_manager = token_manager

    def _details_with_token(self, client_call_details):  # type: ignore[no-untyped-def]
        token = self._token_manager.get_token()
        existing = tuple(client_call_details.metadata or ())
        metadata = existing + (("authorization", token),)
        # client_call_details is an immutable namedtuple-ish; rebuild it.
        return client_call_details._replace(metadata=metadata)

    def intercept_unary_unary(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        return continuation(self._details_with_token(client_call_details), request)

    def intercept_unary_stream(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        return continuation(self._details_with_token(client_call_details), request)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):  # type: ignore[no-untyped-def]
        return continuation(self._details_with_token(client_call_details), request_iterator)

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):  # type: ignore[no-untyped-def]
        return continuation(self._details_with_token(client_call_details), request_iterator)


def _service_stubs():  # noqa: ANN202
    """Import the generated stubs lazily so the package imports cleanly
    before scripts/generate_proto.sh has been run."""
    from .proto.grpc.tradeapi.v1.accounts import accounts_service_pb2_grpc  # type: ignore[import-not-found]
    from .proto.grpc.tradeapi.v1.assets import assets_service_pb2_grpc  # type: ignore[import-not-found]
    from .proto.grpc.tradeapi.v1.auth import auth_service_pb2_grpc  # type: ignore[import-not-found]
    from .proto.grpc.tradeapi.v1.marketdata import marketdata_service_pb2_grpc  # type: ignore[import-not-found]
    from .proto.grpc.tradeapi.v1.metrics import usage_metrics_service_pb2_grpc  # type: ignore[import-not-found]
    from .proto.grpc.tradeapi.v1.orders import orders_service_pb2_grpc  # type: ignore[import-not-found]
    from .proto.grpc.tradeapi.v1.reports import reports_service_pb2_grpc  # type: ignore[import-not-found]

    return {
        "auth": auth_service_pb2_grpc.AuthServiceStub,
        "accounts": accounts_service_pb2_grpc.AccountsServiceStub,
        "assets": assets_service_pb2_grpc.AssetsServiceStub,
        "market_data": marketdata_service_pb2_grpc.MarketDataServiceStub,
        "orders": orders_service_pb2_grpc.OrdersServiceStub,
        "reports": reports_service_pb2_grpc.ReportsServiceStub,
        "metrics": usage_metrics_service_pb2_grpc.UsageMetricsServiceStub,
    }


class FinamClient:
    """Synchronous client for the Finam Trade API.

    Args:
        secret: API secret (long-lived token) issued by Finam.
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
        channel_options: Optional[list[tuple[str, object]]] = None,
        _insecure: bool = False,
    ) -> None:
        self._endpoint = endpoint
        self._secret = secret
        self._retry_policy = retry_policy
        self._auth_channel: Optional[grpc.Channel] = None
        self._channel: Optional[grpc.Channel] = None
        self._token_manager: Optional[TokenManager] = None

        try:
            if _insecure:
                self._auth_channel = grpc.insecure_channel(endpoint, options=channel_options)
                self._token_manager = TokenManager(self._auth_channel, secret)
                self._token_manager.start()
                app_channel = grpc.insecure_channel(endpoint, options=channel_options)
                self._channel = grpc.intercept_channel(
                    app_channel,
                    _InsecureAuthInterceptor(self._token_manager),
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

                # Application channel layers the call credentials (Authorization
                # header) on top of TLS and installs the retry interceptor.
                call_creds = sync_call_credentials(self._token_manager)
                composite = grpc.composite_channel_credentials(transport, call_creds)
                app_channel = grpc.secure_channel(endpoint, composite, options=channel_options)
                self._channel = grpc.intercept_channel(
                    app_channel, build_sync_interceptor(retry_policy)
                )

            stubs = _service_stubs()
            self.auth = stubs["auth"](self._channel)
            self.accounts = stubs["accounts"](self._channel)
            self.assets = stubs["assets"](self._channel)
            self.market_data = stubs["market_data"](self._channel)
            self.orders = stubs["orders"](self._channel)
            self.reports = stubs["reports"](self._channel)
            self.metrics = stubs["metrics"](self._channel)
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
        channel_options: Optional[list[tuple[str, object]]] = None,
    ) -> "FinamClient":
        """Construct an insecure (no-TLS) client for testing against an in-process
        fake server. Never use against ``api.finam.ru`` or any production endpoint."""
        return cls(
            secret,
            endpoint=endpoint,
            retry_policy=retry_policy,
            channel_options=channel_options,
            _insecure=True,
        )

    def get_token(self) -> Optional[str]:
        """Return the current JWT, or ``None`` if construction has not completed.

        The token is refreshed in the background; callers typically don't need
        to read it because the SDK injects it on every RPC automatically. Use
        this when you need to forward the JWT to a non-SDK component (e.g. a
        WebSocket bridge).
        """
        if self._token_manager is None:
            return None
        return self._token_manager._token  # noqa: SLF001 — intentional snapshot read

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

    def __enter__(self) -> "FinamClient":
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self.close()


__all__ = ["FinamClient", "DEFAULT_ENDPOINT"]
