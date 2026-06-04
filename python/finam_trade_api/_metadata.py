"""Per-call metadata plumbing for injecting the JWT into every RPC.

We use `grpc.metadata_call_credentials` so the Authorization header is attached
at call time, picking up whichever JWT the TokenManager currently holds. This
avoids the rebuild-the-channel-on-refresh dance.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import grpc

if TYPE_CHECKING:  # pragma: no cover
    from .auth import AsyncTokenManager, TokenManager


class _SyncAuthPlugin(grpc.AuthMetadataPlugin):
    def __init__(self, token_manager: "TokenManager") -> None:
        self._token_manager = token_manager

    def __call__(
        self,
        context: grpc.AuthMetadataContext,
        callback: grpc.AuthMetadataPluginCallback,
    ) -> None:
        token = self._token_manager.get_token()
        callback((("authorization", token),), None)


class _AsyncAuthPlugin(grpc.AuthMetadataPlugin):
    """Async variant — grpc.aio still drives the plugin synchronously, so we
    rely on the AsyncTokenManager exposing the current token without awaiting."""

    def __init__(self, token_manager: "AsyncTokenManager") -> None:
        self._token_manager = token_manager

    def __call__(
        self,
        context: grpc.AuthMetadataContext,
        callback: grpc.AuthMetadataPluginCallback,
    ) -> None:
        token = self._token_manager._token  # noqa: SLF001 — intentional fast-path read
        if token is None:
            # AsyncFinamClient.start() awaits the initial Auth before building
            # the application channel, so the token is always set before any
            # RPC reaches this plugin. A None here means the SDK was used
            # without start() — surface as a clear error instead of an empty
            # Authorization header that the server would reject as 401.
            callback(
                (),
                RuntimeError(
                    "AsyncFinamClient JWT is not available — "
                    "did you call await client.start()?"
                ),
            )
            return
        callback((("authorization", token),), None)


def sync_call_credentials(token_manager: "TokenManager") -> grpc.CallCredentials:
    return grpc.metadata_call_credentials(_SyncAuthPlugin(token_manager))


def async_call_credentials(token_manager: "AsyncTokenManager") -> grpc.CallCredentials:
    return grpc.metadata_call_credentials(_AsyncAuthPlugin(token_manager))


__all__ = ["sync_call_credentials", "async_call_credentials"]
