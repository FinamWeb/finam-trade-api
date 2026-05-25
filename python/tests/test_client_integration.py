"""End-to-end integration tests against an in-process fake gRPC server.

These exercise the real FinamClient / AsyncFinamClient against actual gRPC
plumbing — channel construction, the Authorization metadata injection path,
retry interceptor wiring, stream iteration — without hitting the network.
"""

from __future__ import annotations

import asyncio

import grpc
import pytest

from finam_trade_api import (
    AsyncFinamClient,
    AuthError,
    FinamClient,
    InvalidArgumentError,
    RateLimitError,
    RetryPolicy,
    from_rpc_error,
)
from finam_trade_api.proto.grpc.tradeapi.v1.accounts.accounts_service_pb2 import (
    GetAccountRequest,
)
from finam_trade_api.proto.grpc.tradeapi.v1.marketdata.marketdata_service_pb2 import (
    SubscribeQuoteRequest,
)
from finam_trade_api.proto.grpc.tradeapi.v1.orders.orders_service_pb2 import (
    CancelOrderRequest,
    Order,
)

from .fakes import (
    FakeAccountsService,
    FakeAuthService,
    FakeMarketDataService,
    FakeOrdersService,
    fake_server,
)


# ---------------------------------------------------------------------------
# Sync FinamClient
# ---------------------------------------------------------------------------


def _fast_retry() -> RetryPolicy:
    return RetryPolicy(max_attempts=3, initial_backoff=0.001, max_backoff=0.002)


def test_unary_call_succeeds_and_carries_authorization_header() -> None:
    auth = FakeAuthService(initial_token="my-jwt")
    accounts = FakeAccountsService()
    with fake_server(auth=auth, accounts=accounts) as (endpoint, _):
        with FinamClient(secret="s", endpoint=endpoint, insecure=True) as client:
            resp = client.accounts.GetAccount(GetAccountRequest(account_id="A12345"))
            assert resp.account_id == "A12345"
            md = dict(accounts.last_metadata)
            assert md.get("authorization") == "my-jwt"
        auth.close_stream()


def test_unary_call_retries_on_unavailable_then_succeeds() -> None:
    auth = FakeAuthService()
    orders = FakeOrdersService()
    orders.fail_next(grpc.StatusCode.UNAVAILABLE, times=2)
    with fake_server(auth=auth, orders=orders) as (endpoint, _):
        with FinamClient(
            secret="s", endpoint=endpoint, insecure=True, retry_policy=_fast_retry()
        ) as client:
            state = client.orders.PlaceOrder(Order(account_id="A1", symbol="SBER@MISX"))
            assert state.order_id == "ord-1"
            assert len(orders.placed) == 1
        auth.close_stream()


def test_unary_call_surfaces_typed_error_after_giving_up() -> None:
    auth = FakeAuthService()
    orders = FakeOrdersService()
    orders.fail_next(grpc.StatusCode.UNAVAILABLE, times=10)
    with fake_server(auth=auth, orders=orders) as (endpoint, _):
        with FinamClient(
            secret="s", endpoint=endpoint, insecure=True, retry_policy=_fast_retry()
        ) as client:
            with pytest.raises(grpc.RpcError) as exc_info:
                client.orders.PlaceOrder(Order(account_id="A1", symbol="SBER@MISX"))
            typed = from_rpc_error(exc_info.value)
            assert typed.code is grpc.StatusCode.UNAVAILABLE
        auth.close_stream()


def test_invalid_argument_is_not_retried_and_maps_cleanly() -> None:
    auth = FakeAuthService()
    orders = FakeOrdersService()
    orders.fail_next(grpc.StatusCode.INVALID_ARGUMENT, times=1)
    with fake_server(auth=auth, orders=orders) as (endpoint, _):
        with FinamClient(
            secret="s", endpoint=endpoint, insecure=True, retry_policy=_fast_retry()
        ) as client:
            with pytest.raises(grpc.RpcError) as exc_info:
                client.orders.PlaceOrder(Order(account_id="A1", symbol="SBER@MISX"))
            typed = from_rpc_error(exc_info.value)
            assert isinstance(typed, InvalidArgumentError)
        # No retries — failure consumed exactly once.
        assert orders.fail_remaining == 0
        auth.close_stream()


def test_rate_limit_is_retried_then_propagates_if_persistent() -> None:
    auth = FakeAuthService()
    orders = FakeOrdersService()
    orders.fail_next(grpc.StatusCode.RESOURCE_EXHAUSTED, times=5)
    with fake_server(auth=auth, orders=orders) as (endpoint, _):
        with FinamClient(
            secret="s", endpoint=endpoint, insecure=True, retry_policy=_fast_retry()
        ) as client:
            with pytest.raises(grpc.RpcError) as exc_info:
                client.orders.PlaceOrder(Order(account_id="A1", symbol="SBER@MISX"))
            typed = from_rpc_error(exc_info.value)
            assert isinstance(typed, RateLimitError)
        auth.close_stream()


def test_streaming_subscription_yields_events_and_carries_auth() -> None:
    auth = FakeAuthService(initial_token="stream-jwt")
    market_data = FakeMarketDataService(events=4, require_auth=True)
    with fake_server(auth=auth, market_data=market_data) as (endpoint, _):
        with FinamClient(secret="s", endpoint=endpoint, insecure=True) as client:
            events = list(
                client.market_data.SubscribeQuote(SubscribeQuoteRequest(symbols=["X"]))
            )
            assert len(events) == 4
            md = dict(market_data.last_metadata)
            assert md.get("authorization") == "stream-jwt"
        auth.close_stream()


def test_place_and_cancel_order_round_trip() -> None:
    auth = FakeAuthService()
    orders = FakeOrdersService()
    with fake_server(auth=auth, orders=orders) as (endpoint, _):
        with FinamClient(secret="s", endpoint=endpoint, insecure=True) as client:
            state = client.orders.PlaceOrder(Order(account_id="A1", symbol="SBER@MISX"))
            assert state.order_id == "ord-1"
            cancelled = client.orders.CancelOrder(
                CancelOrderRequest(account_id="A1", order_id=state.order_id)
            )
            assert cancelled.order_id == "ord-1"
            assert orders.cancelled == ["ord-1"]
        auth.close_stream()


def test_client_token_property_returns_current_jwt() -> None:
    auth = FakeAuthService(initial_token="abc")
    with fake_server(auth=auth) as (endpoint, _):
        with FinamClient(secret="s", endpoint=endpoint, insecure=True) as client:
            assert client.token == "abc"
        auth.close_stream()


def test_client_rejects_call_when_auth_fails_upfront() -> None:
    class BadAuth(FakeAuthService):
        def Auth(self, request, context):  # type: ignore[override]
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "no")

    with fake_server(auth=BadAuth()) as (endpoint, _):
        with pytest.raises(AuthError):
            FinamClient(secret="bad", endpoint=endpoint, insecure=True)


# ---------------------------------------------------------------------------
# AsyncFinamClient
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_unary_call_carries_authorization() -> None:
    auth = FakeAuthService(initial_token="async-jwt")
    accounts = FakeAccountsService()
    with fake_server(auth=auth, accounts=accounts) as (endpoint, _):
        async with AsyncFinamClient(
            secret="s", endpoint=endpoint, insecure=True
        ) as client:
            resp = await client.accounts.GetAccount(GetAccountRequest(account_id="A99"))
            assert resp.account_id == "A99"
            md = dict(accounts.last_metadata)
            assert md.get("authorization") == "async-jwt"
        auth.close_stream()


@pytest.mark.asyncio
async def test_async_streaming_subscription_yields_events_and_carries_auth() -> None:
    auth = FakeAuthService(initial_token="async-stream-jwt")
    market_data = FakeMarketDataService(events=3, require_auth=True)
    with fake_server(auth=auth, market_data=market_data) as (endpoint, _):
        async with AsyncFinamClient(
            secret="s", endpoint=endpoint, insecure=True
        ) as client:
            received = []
            async for event in client.market_data.SubscribeQuote(
                SubscribeQuoteRequest(symbols=["X"])
            ):
                received.append(event)
            assert len(received) == 3
            md = dict(market_data.last_metadata)
            assert md.get("authorization") == "async-stream-jwt"
        auth.close_stream()


@pytest.mark.asyncio
async def test_async_start_is_idempotent() -> None:
    auth = FakeAuthService()
    with fake_server(auth=auth) as (endpoint, _):
        client = AsyncFinamClient(secret="s", endpoint=endpoint, insecure=True)
        await client.start()
        await client.start()  # must be a no-op, no double-subscribe
        try:
            assert await client.token == "jwt-1"
        finally:
            await client.close()
            auth.close_stream()
