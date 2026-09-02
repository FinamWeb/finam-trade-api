"""Authorization interceptors used only by local plaintext test clients."""

from __future__ import annotations

from typing import Any

import grpc
import grpc.aio

from .auth import AsyncTokenManager, TokenManager


class InsecureAuthInterceptor(
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
    grpc.StreamUnaryClientInterceptor,
    grpc.StreamStreamClientInterceptor,
):
    """Attach the current JWT to every synchronous call."""

    def __init__(self, token_manager: TokenManager) -> None:
        self._token_manager = token_manager

    def _details_with_token(self, details: Any) -> Any:
        token = self._token_manager.get_token()
        metadata = (*tuple(details.metadata or ()), ("authorization", token))
        return details._replace(metadata=metadata)

    def intercept_unary_unary(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        return continuation(self._details_with_token(client_call_details), request)

    def intercept_unary_stream(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        return continuation(self._details_with_token(client_call_details), request)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):  # type: ignore[no-untyped-def]
        return continuation(self._details_with_token(client_call_details), request_iterator)

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):  # type: ignore[no-untyped-def]
        return continuation(self._details_with_token(client_call_details), request_iterator)


async def _details_with_token(token_manager: AsyncTokenManager, details: Any) -> Any:
    token = await token_manager.get_token()
    metadata = (*tuple(details.metadata or ()), ("authorization", token))
    return details._replace(metadata=metadata)


class InsecureAsyncAuthUnaryInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    """Attach the current JWT to asynchronous unary calls."""

    def __init__(self, token_manager: AsyncTokenManager) -> None:
        self._token_manager = token_manager

    async def intercept_unary_unary(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        details = await _details_with_token(self._token_manager, client_call_details)
        return await continuation(details, request)


class InsecureAsyncAuthStreamInterceptor(grpc.aio.UnaryStreamClientInterceptor):
    """Attach the current JWT to asynchronous server streams."""

    def __init__(self, token_manager: AsyncTokenManager) -> None:
        self._token_manager = token_manager

    async def intercept_unary_stream(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        details = await _details_with_token(self._token_manager, client_call_details)
        return await continuation(details, request)
