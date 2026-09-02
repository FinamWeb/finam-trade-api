import { setTimeout as delay } from "node:timers/promises";
import type { ClientMiddleware } from "nice-grpc";
import { ClientError, Metadata } from "nice-grpc";
import { toTradeApiError } from "../errors.js";
import type { AuthServiceClient } from "../generated/grpc/tradeapi/v1/auth/auth_service.js";

export type RenewalErrorHandler = (error: unknown, retryInMs: number) => void;

export const authorization = (getToken: () => string): ClientMiddleware =>
  async function* (call, options) {
    const metadata = Metadata(options.metadata);
    metadata.set("authorization", getToken());
    return yield* call.next(call.request, { ...options, metadata });
  };

export const mapErrors: ClientMiddleware = async function* (call, options) {
  try {
    return yield* call.next(call.request, options);
  } catch (error) {
    if (error instanceof ClientError) throw toTradeApiError(error);
    throw error;
  }
};

const reportRenewalError = (
  onError: RenewalErrorHandler | undefined,
  error: unknown,
  retryInMs: number,
): void => {
  try {
    onError?.(error, retryInMs);
  } catch {
    // An observer must not stop authentication renewal.
  }
};

const waitForRetry = async (delayMs: number, signal: AbortSignal): Promise<boolean> => {
  try {
    await delay(delayMs, undefined, { signal });
    return true;
  } catch {
    return false;
  }
};

const receiveTokenUpdates = async (
  auth: AuthServiceClient,
  request: { secret: string; sourceAppId: string },
  signal: AbortSignal,
  setToken: (token: string) => void,
  onError: RenewalErrorHandler | undefined,
  retryInMs: number,
): Promise<boolean> => {
  let receivedUpdate = false;
  try {
    for await (const update of auth.subscribeJwtRenewal(request, { signal })) {
      setToken(update.token);
      receivedUpdate = true;
    }
  } catch (error) {
    if (!signal.aborted) reportRenewalError(onError, error, retryInMs);
  }
  return receivedUpdate;
};

export const renewToken = async (
  auth: AuthServiceClient,
  request: { secret: string; sourceAppId: string },
  signal: AbortSignal,
  setToken: (token: string) => void,
  onError?: RenewalErrorHandler,
): Promise<void> => {
  let backoffMs = 1_000;

  while (!signal.aborted) {
    const receivedUpdate = await receiveTokenUpdates(
      auth,
      request,
      signal,
      setToken,
      onError,
      backoffMs,
    );
    if (receivedUpdate) backoffMs = 1_000;
    if (signal.aborted) break;
    if (!(await waitForRetry(backoffMs, signal))) break;
    backoffMs = Math.min(backoffMs * 2, 30_000);
  }
};
