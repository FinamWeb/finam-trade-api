"""Unit tests for the metadata auth plugins."""

from __future__ import annotations

from unittest.mock import MagicMock

import grpc

from finam_trade_api._metadata import (
    _AsyncAuthPlugin,
    _SyncAuthPlugin,
    async_call_credentials,
    sync_call_credentials,
)


def test_sync_plugin_injects_authorization_metadata() -> None:
    token_manager = MagicMock()
    token_manager.get_token.return_value = "jwt-abc"
    plugin = _SyncAuthPlugin(token_manager)

    captured: list[tuple[tuple[tuple[str, str], ...], Exception | None]] = []

    def callback(metadata, error):  # noqa: ANN001
        captured.append((tuple(metadata), error))

    plugin(MagicMock(spec=grpc.AuthMetadataContext), callback)

    assert captured == [((("authorization", "jwt-abc"),), None)]
    token_manager.get_token.assert_called_once()


def test_async_plugin_injects_authorization_when_token_present() -> None:
    token_manager = MagicMock()
    token_manager._token = "jwt-xyz"
    plugin = _AsyncAuthPlugin(token_manager)

    captured: list[tuple[tuple[tuple[str, str], ...], Exception | None]] = []
    plugin(MagicMock(spec=grpc.AuthMetadataContext), lambda md, err: captured.append((tuple(md), err)))

    assert captured == [((("authorization", "jwt-xyz"),), None)]


def test_async_plugin_emits_empty_metadata_when_no_token() -> None:
    token_manager = MagicMock()
    token_manager._token = None
    plugin = _AsyncAuthPlugin(token_manager)

    captured: list[tuple[tuple[tuple[str, str], ...], Exception | None]] = []
    plugin(MagicMock(spec=grpc.AuthMetadataContext), lambda md, err: captured.append((tuple(md), err)))

    assert captured == [((), None)]


def test_factory_helpers_return_grpc_call_credentials() -> None:
    sync_token_manager = MagicMock()
    sync_token_manager.get_token.return_value = "t"
    creds = sync_call_credentials(sync_token_manager)
    assert isinstance(creds, grpc.CallCredentials)

    async_token_manager = MagicMock()
    async_token_manager._token = "t"
    creds = async_call_credentials(async_token_manager)
    assert isinstance(creds, grpc.CallCredentials)
