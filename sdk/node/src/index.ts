export { Status as GrpcStatus } from "nice-grpc";
export {
  createTradeApi,
  DEFAULT_ENDPOINT,
  DEFAULT_RETRY_POLICY,
  type RetryPolicy,
  type TradeApi,
  type TradeApiOptions,
  withTradeApi,
} from "./client.js";
export {
  AuthError,
  DeadlineExceededError,
  InternalError,
  InvalidArgumentError,
  NotFoundError,
  PermissionDeniedError,
  RateLimitError,
  ServiceUnavailableError,
  TradeApiError,
  toTradeApiError,
} from "./errors.js";
