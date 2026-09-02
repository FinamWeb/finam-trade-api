import type { ChannelOptions } from "nice-grpc";
import { ChannelCredentials, createChannel, createClient, createClientFactory } from "nice-grpc";
import { retryMiddleware } from "nice-grpc-client-middleware-retry";
import { toTradeApiError } from "./errors.js";
import { AuthServiceDefinition } from "./generated/grpc/tradeapi/v1/auth/auth_service.js";
import type { RenewalErrorHandler } from "./internal/auth.js";
import { authorization, mapErrors, renewToken } from "./internal/auth.js";
import type { RetryPolicy } from "./internal/retry.js";
import { DEFAULT_RETRY_POLICY, resolveRetry } from "./internal/retry.js";
import type { ServiceClients } from "./internal/services.js";
import { createServiceClients } from "./internal/services.js";

export const DEFAULT_ENDPOINT = "api.finam.ru:443";
export type { RetryPolicy };
export { DEFAULT_RETRY_POLICY };

export type TradeApiOptions = Readonly<{
  secret: string;
  endpoint?: string;
  sourceAppId?: string;
  retry?: Partial<RetryPolicy> | false;
  channelOptions?: ChannelOptions;
  /**
   * Use plaintext transport for a local test server.
   * Never enable this for a production endpoint.
   */
  insecure?: boolean;
  onRenewalError?: RenewalErrorHandler;
}>;

export type TradeApi = ServiceClients &
  Readonly<{
    getToken: () => string;
    close: () => Promise<void>;
  }>;

/**
 * Create a ready-to-use Trade API client.
 *
 * The initial JWT is fetched before this promise resolves. Every service call
 * receives the latest token automatically; server streams are AsyncIterables.
 */
export const createTradeApi = async (options: TradeApiOptions): Promise<TradeApi> => {
  const credentials = options.insecure
    ? ChannelCredentials.createInsecure()
    : ChannelCredentials.createSsl();
  const channel = createChannel(
    options.endpoint ?? DEFAULT_ENDPOINT,
    credentials,
    options.channelOptions,
  );
  const rawAuth = createClient(AuthServiceDefinition, channel);
  const request = {
    secret: options.secret,
    sourceAppId: options.sourceAppId ?? "",
  };

  let token: string;
  try {
    token = (await rawAuth.auth(request)).token;
  } catch (error) {
    channel.close();
    throw toTradeApiError(error);
  }

  const authorized = createClientFactory()
    .use(authorization(() => token))
    .use(retryMiddleware)
    .use(mapErrors);
  // AuthService takes its credential in the request body, so it is reached
  // without the Authorization header that every other service requires.
  const unauthenticated = createClientFactory().use(retryMiddleware).use(mapErrors);
  const services = createServiceClients(
    { authorized, unauthenticated },
    channel,
    resolveRetry(options.retry),
  );
  const abort = new AbortController();
  const renewal = renewToken(
    rawAuth,
    request,
    abort.signal,
    (nextToken) => {
      token = nextToken;
    },
    options.onRenewalError,
  );
  let closed = false;

  return {
    ...services,
    getToken: () => token,
    close: async () => {
      if (closed) return;
      closed = true;
      abort.abort();
      channel.close();
      await renewal;
    },
  };
};

/** Run work with a client and always close its channel and renewal stream. */
export const withTradeApi = async <Result>(
  options: TradeApiOptions,
  run: (client: TradeApi) => Result | Promise<Result>,
): Promise<Result> => {
  const client = await createTradeApi(options);
  try {
    return await run(client);
  } finally {
    await client.close();
  }
};
