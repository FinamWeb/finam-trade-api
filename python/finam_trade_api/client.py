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


class _InsecureAuthInterceptor(
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
    grpc.StreamUnaryClientInterceptor,
    grpc.StreamStreamClientInterceptor,
):
    """Attaches the current JWT as Authorization metadata on every call.

    Used only when the client is constructed with ``insecure=True`` — gRPC
    forbids attaching ``CallCredentials`` to insecure channels, so we cannot
    use the normal ``metadata_call_credentials`` path in that mode.
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

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = "api.finam.ru:443"


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
        insecure: Use a plaintext channel and inject Authorization via interceptor.
            Intended for local testing against an in-process fake server. Never
            enable this for production traffic.
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

        if insecure:
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
            self._auth_channel = grpc.secure_channel(endpoint, transport, options=channel_options)
            self._token_manager = TokenManager(self._auth_channel, secret)
            self._token_manager.start()

            # Application channel layers the call credentials (Authorization header)
            # on top of TLS and installs the retry interceptor.
            call_creds = sync_call_credentials(self._token_manager)
            composite = grpc.composite_channel_credentials(transport, call_creds)
            app_channel = grpc.secure_channel(endpoint, composite, options=channel_options)
            self._channel = grpc.intercept_channel(app_channel, build_sync_interceptor(retry_policy))

        stubs = _service_stubs()
        self.auth = stubs["auth"](self._channel)
        self.accounts = stubs["accounts"](self._channel)
        self.assets = stubs["assets"](self._channel)
        self.market_data = stubs["market_data"](self._channel)
        self.orders = stubs["orders"](self._channel)
        self.reports = stubs["reports"](self._channel)
        self.metrics = stubs["metrics"](self._channel)

    @property
    def token(self) -> str:
        """Current JWT — useful for debugging or for callers that need to
        forward it to a non-SDK component (e.g. a websocket bridge)."""
        return self._token_manager.get_token()

    def close(self) -> None:
        self._token_manager.stop()
        self._channel.close()
        self._auth_channel.close()

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
