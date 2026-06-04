# Changelog

All notable changes to the Finam Trade API Python SDK are documented in this
file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The PyPI distribution is `finam-sdk`; the Python import name is
`finam_trade_api`.

## [Unreleased]

## [0.1.0] — 2026-05-26

Initial public release.

### Added

- `FinamClient` — synchronous client with automatic JWT issuance, background
  refresh via `AuthService.SubscribeJwtRenewal`, and exponential-backoff
  retries on transient gRPC failures (`UNAVAILABLE`, `RESOURCE_EXHAUSTED`).
- `AsyncFinamClient` — asyncio counterpart, mirroring the sync surface 1:1
  using `grpc.aio`. Streaming RPCs return async iterators.
- Service stubs exposed as attributes: `auth`, `accounts`, `assets`,
  `market_data`, `orders`, `reports`, `metrics`. The full proto surface is
  available without a translation layer.
- Per-service message re-export modules for short imports —
  `finam_trade_api.accounts`, `.assets`, `.market_data`, `.orders`,
  `.reports`, `.metrics`, `.auth_messages`. `Side` is re-exported alongside
  `Order` in `finam_trade_api.orders`.
- Typed exception hierarchy mapped from gRPC status codes
  (`AuthError`, `PermissionDeniedError`, `InvalidArgumentError`,
  `NotFoundError`, `RateLimitError`, `DeadlineExceededError`,
  `InternalError`, `ServiceUnavailableError`), with `from_rpc_error()` to
  convert raw `grpc.RpcError` to a typed `FinamError`.
- `RetryPolicy` — configurable exponential backoff with jitter for unary
  RPCs. Streaming RPCs are not retried; callers handle reconnection at a
  meaningful boundary.
- Generated proto stubs ship pre-compiled in the wheel — end users never
  need protoc. Type stubs (`.pyi`) generated via `mypy-protobuf` are
  included, so RPC methods are visible to Pyright/Pylance/mypy.
- `py.typed` marker — full static-typing support.
- Examples for auth + accounts, placing/cancelling orders, and async quote
  subscription.

### Notes

- Distribution name on PyPI is `finam-sdk` because the
  `finam-trade-api` name is held by an unrelated third-party REST client.
  Import name stays `finam_trade_api`.

[Unreleased]: https://github.com/FinamWeb/finam-trade-api/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/FinamWeb/finam-trade-api/releases/tag/v0.1.0
