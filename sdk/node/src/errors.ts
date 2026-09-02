import { ClientError, Status } from "nice-grpc";

export class TradeApiError extends Error {
  readonly code?: Status;
  readonly path?: string;
  readonly details?: string;

  constructor(
    message: string,
    options: {
      code?: Status;
      path?: string;
      details?: string;
      cause?: unknown;
    } = {},
  ) {
    super(message, { cause: options.cause });
    this.name = new.target.name;
    this.code = options.code;
    this.path = options.path;
    this.details = options.details;
  }
}

export class AuthError extends TradeApiError {}
export class PermissionDeniedError extends TradeApiError {}
export class RateLimitError extends TradeApiError {}
export class InvalidArgumentError extends TradeApiError {}
export class NotFoundError extends TradeApiError {}
export class ServiceUnavailableError extends TradeApiError {}
export class DeadlineExceededError extends TradeApiError {}
export class InternalError extends TradeApiError {}

const errorsByStatus = new Map<Status, typeof TradeApiError>([
  [Status.UNAUTHENTICATED, AuthError],
  [Status.PERMISSION_DENIED, PermissionDeniedError],
  [Status.RESOURCE_EXHAUSTED, RateLimitError],
  [Status.INVALID_ARGUMENT, InvalidArgumentError],
  [Status.NOT_FOUND, NotFoundError],
  [Status.UNAVAILABLE, ServiceUnavailableError],
  [Status.DEADLINE_EXCEEDED, DeadlineExceededError],
  [Status.INTERNAL, InternalError],
]);

/** Convert a gRPC error into an SDK-specific error that is easy to catch. */
export const toTradeApiError = (error: unknown): TradeApiError => {
  if (error instanceof TradeApiError) return error;
  if (!(error instanceof ClientError)) {
    return new TradeApiError(error instanceof Error ? error.message : String(error), {
      cause: error,
    });
  }

  const ErrorType = errorsByStatus.get(error.code) ?? TradeApiError;
  return new ErrorType(error.details || error.message, {
    code: error.code,
    path: error.path,
    details: error.details,
    cause: error,
  });
};
