# Changelog

All notable changes to the Finam Trade API Python SDK are documented in this
file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The PyPI distribution is `finam-sdk`; the Python import name is
`finam_trade_api`.

## [Unreleased]

## [2.19.1] — 2026-09-02

Repository layout and tooling are aligned with `limeint/tradingapi`: a
hand-written Node.js SDK (`@finam/trade-api`) ships alongside this package,
examples moved to `examples/sdk/` and `examples/strategies/`, and a root
`justfile` drives every check. Both SDKs now share one version line.

### Added

- `client.corporate_actions` sub-client for `CorporateActionsService`
  (`GetFutureSplits`, `GetPastSplits`, `GetFutureDividends`,
  `GetPastDividends`, `GetFutureBondsEvents`, `GetPastBondsEvents`) on both
  the sync and asyncio clients, and the `finam_trade_api.corporate_actions`
  message re-export module.

### Fixed

- `AuthService` is now reached without an `Authorization` header. `TokenDetails`
  carries its token in the request body, and the server rejects the call with
  `INVALID_ARGUMENT` when a header is also present, which made
  `client.auth.TokenDetails` fail for every caller. The public auth stub now
  sits on the credential-free channel that already served `Auth` and
  `SubscribeJwtRenewal`. Every other service is unchanged and still sends the
  header.

### Changed

- The asynchronous auth channel now carries the retry interceptors, so a
  transient `UNAVAILABLE` on the initial `Auth` call is retried instead of
  surfacing immediately. Streaming RPCs, including `SubscribeJwtRenewal`, are
  unaffected — the stream interceptor is a pass-through.
- `finam_trade_api.__version__` now reports the installed distribution version
  instead of a hardcoded string.
- Python 3.10 is the minimum supported version. The shipped stubs are generated
  with protobuf 7 gencode, which already required 3.10 at runtime; the metadata
  now says so. `grpcio>=1.83` and `protobuf>=7.35.1` are the new floors.
- Development dependencies moved from the `dev` extra to a `uv` dependency
  group with a committed `uv.lock`; `ruff` and `mypy` run in CI as hard gates.
- The insecure test-channel interceptors moved to `finam_trade_api._insecure_auth`
  and the lazy stub registry to `finam_trade_api._services`. Neither is public
  API.

### Removed

- `sdk/python/examples/` and `sdk/python/.env.example`. The examples live in
  `examples/sdk/python/` as a standalone consumer project; the single
  `.env.example` is at the repository root.

## [2.19.0] — 2026-08-13

### Added

- `Bar.is_data_snapshot`, `Quote.is_data_snapshot`, `Trade.is_data_snapshot`, and
  `StreamOrderBook.is_data_snapshot` — flag indicating the data is a snapshot.

## [2.18.1] — 2026-08-03

### Added

- `GetAssetParamsResponse.trade_lot_size` — lot size of the instrument for trading operations;
  0 if the value is not available.

## [2.18.0] — 2026-07-20

### Added

- `Constituents.weight` — weight of the instrument within the index.

## [2.17.0] — 2026-06-25

### Added

- New `CorporateActionsService` proto with two RPCs: `GetFutureBondsEvents` and `GetPastBondsEvents` —
  bond event calendars (coupons, amortisations, offers) with date-range filtering, sorting, and
  pagination.
- `OrderState.triggered_order_id` — ID of the exchange order generated when a stop condition or
  stop-price is triggered.

## [2.16.0] — 2026-06-05

Version unified with the other Finam Trade API SDKs (JS, Kotlin) so a single
release tag publishes every SDK at the same version. No API changes since
`0.1.0`.

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

[Unreleased]: https://github.com/FinamWeb/finam-trade-api/compare/2.19.0...HEAD
[2.19.0]: https://github.com/FinamWeb/finam-trade-api/releases/tag/2.19.0
[2.18.1]: https://github.com/FinamWeb/finam-trade-api/releases/tag/2.18.1
[2.18.0]: https://github.com/FinamWeb/finam-trade-api/releases/tag/2.18.0
[2.17.0]: https://github.com/FinamWeb/finam-trade-api/releases/tag/2.17.0
[2.16.0]: https://github.com/FinamWeb/finam-trade-api/releases/tag/2.16.0
[0.1.0]: https://github.com/FinamWeb/finam-trade-api/releases/tag/v0.1.0
