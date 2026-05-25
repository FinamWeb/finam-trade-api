"""In-process fake implementations of the Trade API gRPC services.

Used by both the auth-focused unit tests (which need a working AuthService
with a controllable renewal stream) and the broader integration tests (which
need stubs for accounts/orders/market data).

Everything lives in this single module so individual tests can compose just
the servicers they care about.
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from queue import Queue
from typing import Any, Iterable, Iterator, Optional

import grpc

from finam_trade_api.proto.grpc.tradeapi.v1.accounts import (
    accounts_service_pb2,
    accounts_service_pb2_grpc,
)
from finam_trade_api.proto.grpc.tradeapi.v1.assets import (
    assets_service_pb2,
    assets_service_pb2_grpc,
)
from finam_trade_api.proto.grpc.tradeapi.v1.auth import (
    auth_service_pb2,
    auth_service_pb2_grpc,
)
from finam_trade_api.proto.grpc.tradeapi.v1.marketdata import (
    marketdata_service_pb2,
    marketdata_service_pb2_grpc,
)
from finam_trade_api.proto.grpc.tradeapi.v1.orders import (
    orders_service_pb2,
    orders_service_pb2_grpc,
)


class FakeAuthService(auth_service_pb2_grpc.AuthServiceServicer):
    """Controllable AuthService.

    - ``Auth`` returns ``initial_token`` (and increments a counter).
    - ``TokenDetails`` returns a fixed payload.
    - ``SubscribeJwtRenewal`` yields whatever tokens are pushed via
      :meth:`push_token`. ``close_stream`` ends the current stream so the
      manager exercises its reconnect path. ``fail_next_subscribe`` makes
      the next ``SubscribeJwtRenewal`` call raise UNAVAILABLE.
    """

    # Sentinel pushed to the queue to abort the current stream with UNAVAILABLE
    # (as opposed to ending it cleanly, which is what ``close_stream`` does).
    _ABORT = "__abort__"

    def __init__(self, initial_token: str = "jwt-1") -> None:
        self._initial_token = initial_token
        self.auth_calls = 0
        self._subscribe_calls = 0
        self._fail_subscribes = 0
        self._queue: Queue[Optional[str]] = Queue()
        self._lock = threading.Lock()

    # --- gRPC handlers ----------------------------------------------------

    def Auth(self, request: auth_service_pb2.AuthRequest, context: grpc.ServicerContext) -> Any:
        with self._lock:
            self.auth_calls += 1
        return auth_service_pb2.AuthResponse(token=self._initial_token)

    def TokenDetails(
        self,
        request: auth_service_pb2.TokenDetailsRequest,
        context: grpc.ServicerContext,
    ) -> Any:
        return auth_service_pb2.TokenDetailsResponse(account_ids=["A12345"], readonly=False)

    def SubscribeJwtRenewal(
        self,
        request: auth_service_pb2.SubscribeJwtRenewalRequest,
        context: grpc.ServicerContext,
    ) -> Iterator[auth_service_pb2.SubscribeJwtRenewalResponse]:
        with self._lock:
            self._subscribe_calls += 1
            if self._fail_subscribes > 0:
                self._fail_subscribes -= 1
                context.abort(grpc.StatusCode.UNAVAILABLE, "fake transient failure")
        # Block on the queue; ``None`` ends the stream cleanly,
        # ``_ABORT`` ends it with UNAVAILABLE so the client treats it as
        # a transient failure and exercises the reconnect-on-error path.
        while True:
            token = self._queue.get()
            if token is None:
                return
            if token == self._ABORT:
                context.abort(grpc.StatusCode.UNAVAILABLE, "fake stream abort")
            yield auth_service_pb2.SubscribeJwtRenewalResponse(token=token)

    # --- test controls ----------------------------------------------------

    def push_token(self, token: str) -> None:
        self._queue.put(token)

    def close_stream(self) -> None:
        self._queue.put(None)

    def abort_stream(self) -> None:
        self._queue.put(self._ABORT)

    def fail_next_subscribe(self, n: int = 1) -> None:
        with self._lock:
            self._fail_subscribes += n

    @property
    def subscribe_calls(self) -> int:
        with self._lock:
            return self._subscribe_calls


class FakeAccountsService(accounts_service_pb2_grpc.AccountsServiceServicer):
    """Echoes the requested account id back so tests can assert end-to-end wiring."""

    def __init__(self, require_auth: bool = True) -> None:
        self.require_auth = require_auth
        self.last_metadata: tuple[tuple[str, str], ...] = ()

    def _check_auth(self, context: grpc.ServicerContext) -> None:
        self.last_metadata = tuple(context.invocation_metadata())
        if not self.require_auth:
            return
        for key, value in self.last_metadata:
            if key.lower() == "authorization" and value:
                return
        context.abort(grpc.StatusCode.UNAUTHENTICATED, "missing authorization")

    def GetAccount(
        self,
        request: accounts_service_pb2.GetAccountRequest,
        context: grpc.ServicerContext,
    ) -> Any:
        self._check_auth(context)
        return accounts_service_pb2.GetAccountResponse(account_id=request.account_id)


class FakeOrdersService(orders_service_pb2_grpc.OrdersServiceServicer):
    """Returns a successful OrderState for any placed order, supports cancellation
    and an order-trade stream that emits a configurable number of events."""

    def __init__(self) -> None:
        self.placed: list[orders_service_pb2.Order] = []
        self.cancelled: list[str] = []
        self.fail_with: Optional[grpc.StatusCode] = None
        self.fail_remaining = 0

    def fail_next(self, code: grpc.StatusCode, times: int = 1) -> None:
        self.fail_with = code
        self.fail_remaining = times

    def _maybe_fail(self, context: grpc.ServicerContext) -> None:
        if self.fail_with is not None and self.fail_remaining > 0:
            self.fail_remaining -= 1
            code = self.fail_with
            if self.fail_remaining == 0:
                self.fail_with = None
            context.abort(code, f"fake {code.name}")

    def PlaceOrder(self, request: orders_service_pb2.Order, context: grpc.ServicerContext) -> Any:
        self._maybe_fail(context)
        self.placed.append(request)
        return orders_service_pb2.OrderState(
            order_id=f"ord-{len(self.placed)}",
            order=request,
        )

    def CancelOrder(
        self,
        request: orders_service_pb2.CancelOrderRequest,
        context: grpc.ServicerContext,
    ) -> Any:
        self.cancelled.append(request.order_id)
        return orders_service_pb2.OrderState(order_id=request.order_id)


class FakeMarketDataService(marketdata_service_pb2_grpc.MarketDataServiceServicer):
    """Emits a configurable number of quote events from SubscribeQuote.

    Records the metadata of the last incoming call so streaming-auth tests
    can verify the Authorization header was actually attached.
    """

    def __init__(self, events: int = 3, require_auth: bool = False) -> None:
        self.events = events
        self.require_auth = require_auth
        self.last_metadata: tuple[tuple[str, str], ...] = ()

    def SubscribeQuote(
        self,
        request: marketdata_service_pb2.SubscribeQuoteRequest,
        context: grpc.ServicerContext,
    ) -> Iterator[marketdata_service_pb2.SubscribeQuoteResponse]:
        self.last_metadata = tuple(context.invocation_metadata())
        if self.require_auth and not any(
            k.lower() == "authorization" and v for k, v in self.last_metadata
        ):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "missing authorization on stream")
        for _ in range(self.events):
            yield marketdata_service_pb2.SubscribeQuoteResponse()


class FakeAssetsService(assets_service_pb2_grpc.AssetsServiceServicer):
    """Returns a tiny canned asset list."""

    def Assets(
        self,
        request: assets_service_pb2.AssetsRequest,
        context: grpc.ServicerContext,
    ) -> Any:
        return assets_service_pb2.AssetsResponse()


# ---------------------------------------------------------------------------
# Server harness
# ---------------------------------------------------------------------------


@contextmanager
def fake_server(
    *,
    auth: Optional[FakeAuthService] = None,
    accounts: Optional[FakeAccountsService] = None,
    orders: Optional[FakeOrdersService] = None,
    market_data: Optional[FakeMarketDataService] = None,
    assets: Optional[FakeAssetsService] = None,
) -> Iterator[tuple[str, dict[str, Any]]]:
    """Spin up a real gRPC server on localhost:<random> with the requested
    servicers attached. Yields (endpoint, registry-of-installed-services)."""
    server = grpc.server(ThreadPoolExecutor(max_workers=4))
    installed: dict[str, Any] = {}

    if auth is not None:
        auth_service_pb2_grpc.add_AuthServiceServicer_to_server(auth, server)
        installed["auth"] = auth
    if accounts is not None:
        accounts_service_pb2_grpc.add_AccountsServiceServicer_to_server(accounts, server)
        installed["accounts"] = accounts
    if orders is not None:
        orders_service_pb2_grpc.add_OrdersServiceServicer_to_server(orders, server)
        installed["orders"] = orders
    if market_data is not None:
        marketdata_service_pb2_grpc.add_MarketDataServiceServicer_to_server(market_data, server)
        installed["market_data"] = market_data
    if assets is not None:
        assets_service_pb2_grpc.add_AssetsServiceServicer_to_server(assets, server)
        installed["assets"] = assets

    port = server.add_insecure_port("localhost:0")
    server.start()
    endpoint = f"localhost:{port}"
    try:
        yield endpoint, installed
    finally:
        server.stop(grace=0).wait()


def wait_for(predicate, timeout: float = 5.0, interval: float = 0.01) -> None:  # noqa: ANN001
    """Spin-wait helper for tests that need to observe a background thread's effect.

    Default timeout is 5s — cold GitHub-hosted runners under load routinely take
    >1s to start a daemon thread and complete the first RPC.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(interval)
    raise AssertionError("timed out waiting for predicate")


async def await_for(  # noqa: ANN001
    predicate,
    timeout: float = 5.0,
    interval: float = 0.01,
) -> None:
    """Asyncio counterpart of ``wait_for``.

    ``predicate`` may be sync or async. Replaces the open-coded
    ``for _ in range(N): await asyncio.sleep(...)`` loops that were
    duplicated across the async test files.
    """
    import asyncio
    import inspect

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = predicate()
        if inspect.isawaitable(result):
            result = await result
        if result:
            return
        await asyncio.sleep(interval)
    raise AssertionError("timed out waiting for predicate")
