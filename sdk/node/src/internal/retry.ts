import { Status } from "nice-grpc";
import type { RetryOptions } from "nice-grpc-client-middleware-retry";

export type RetryPolicy = Readonly<{
  /** Total attempts including the initial call. */
  maxAttempts: number;
  initialBackoffMs: number;
  maxBackoffMs: number;
}>;

export const DEFAULT_RETRY_POLICY: RetryPolicy = Object.freeze({
  maxAttempts: 4,
  initialBackoffMs: 200,
  maxBackoffMs: 5_000,
});

export const resolveRetry = (policy: Partial<RetryPolicy> | false | undefined): RetryOptions => {
  if (policy === false) return { retry: false };

  const resolved = { ...DEFAULT_RETRY_POLICY, ...policy };
  if (!Number.isInteger(resolved.maxAttempts) || resolved.maxAttempts < 1) {
    throw new RangeError("retry.maxAttempts must be a positive integer");
  }

  return {
    retry: true,
    retryMaxAttempts: resolved.maxAttempts - 1,
    retryBaseDelayMs: resolved.initialBackoffMs,
    retryMaxDelayMs: resolved.maxBackoffMs,
    retryableStatuses: [Status.UNAVAILABLE],
  };
};
