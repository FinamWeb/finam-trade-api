import type { CallContext } from "nice-grpc";
import { createServer, ServerError, Status } from "nice-grpc";
import { describe, expect, it } from "vitest";
import type { AccountsServiceImplementation } from "../src/generated/grpc/tradeapi/v1/accounts/accounts_service.js";
import { AccountsServiceDefinition } from "../src/generated/grpc/tradeapi/v1/accounts/accounts_service.js";
import type { AuthServiceImplementation } from "../src/generated/grpc/tradeapi/v1/auth/auth_service.js";
import { AuthServiceDefinition } from "../src/generated/grpc/tradeapi/v1/auth/auth_service.js";
import { AuthError, createTradeApi, ServiceUnavailableError, withTradeApi } from "../src/index.js";

type FakeOptions = {
  initialToken?: string;
  failAuth?: boolean;
  unavailableCalls?: number;
};

const waitUntil = async (predicate: () => boolean, timeoutMs = 2_000): Promise<void> => {
  const deadline = Date.now() + timeoutMs;
  while (!predicate()) {
    if (Date.now() >= deadline) throw new Error("Timed out waiting for condition");
    await new Promise((resolve) => setTimeout(resolve, 5));
  }
};

const fakeServer = async (options: FakeOptions = {}) => {
  const server = createServer();
  let accountCalls = 0;
  let unavailableCalls = options.unavailableCalls ?? 0;
  let releaseRenewal: (() => void) | undefined;
  let renewalStarted = false;
  let renewalCancelled = false;
  const authorization: Array<string | Uint8Array | undefined> = [];
  const tokenDetailsAuthorization: Array<string | Uint8Array | undefined> = [];
  const renewalReady = new Promise<void>((resolve) => {
    releaseRenewal = resolve;
  });

  const auth = {
    async auth() {
      if (options.failAuth) {
        throw new ServerError(Status.UNAUTHENTICATED, "bad secret");
      }
      return { token: options.initialToken ?? "jwt-1" };
    },
    async tokenDetails(_request: unknown, context: CallContext) {
      tokenDetailsAuthorization.push(context.metadata.get("authorization"));
      return { accountIds: ["A1"], readonly: false };
    },
    async *subscribeJwtRenewal(_request: unknown, context: CallContext) {
      renewalStarted = true;
      await Promise.race([
        renewalReady,
        new Promise<void>((resolve) => {
          context.signal.addEventListener("abort", () => resolve(), {
            once: true,
          });
        }),
      ]);
      if (context.signal.aborted) {
        renewalCancelled = true;
        return;
      }
      yield { token: "jwt-2" };
      await new Promise<void>((resolve) => {
        context.signal.addEventListener(
          "abort",
          () => {
            renewalCancelled = true;
            resolve();
          },
          { once: true },
        );
      });
    },
  } satisfies AuthServiceImplementation;

  const accounts = {
    async getAccount(request, context) {
      accountCalls += 1;
      authorization.push(context.metadata.get("authorization"));
      if (unavailableCalls > 0) {
        unavailableCalls -= 1;
        throw new ServerError(Status.UNAVAILABLE, "try again");
      }
      return { accountId: request.accountId };
    },
    async trades() {
      return { trades: [] };
    },
    async transactions() {
      return { transactions: [] };
    },
    async *subscribeAccount(request) {
      yield { accountId: request.accountId };
    },
  } satisfies AccountsServiceImplementation;

  server.add(AuthServiceDefinition, auth);
  server.add(AccountsServiceDefinition, accounts);
  const port = await server.listen("127.0.0.1:0");

  return {
    endpoint: `127.0.0.1:${port}`,
    pushRenewal: () => releaseRenewal?.(),
    accountCalls: () => accountCalls,
    authorization,
    tokenDetailsAuthorization,
    renewalStarted: () => renewalStarted,
    renewalCancelled: () => renewalCancelled,
    close: () => server.shutdown(),
  };
};

describe("createTradeApi", () => {
  it("authenticates, injects metadata, and uses renewed JWTs", async () => {
    const fake = await fakeServer();
    const client = await createTradeApi({
      secret: "secret",
      endpoint: fake.endpoint,
      insecure: true,
    });

    try {
      await expect(client.accounts.getAccount({ accountId: "A1" })).resolves.toMatchObject({
        accountId: "A1",
      });
      expect(fake.authorization.at(-1)).toBe("jwt-1");

      fake.pushRenewal();
      await waitUntil(() => client.getToken() === "jwt-2");
      await client.accounts.getAccount({ accountId: "A2" });
      expect(fake.authorization.at(-1)).toBe("jwt-2");
    } finally {
      await client.close();
      await fake.close();
    }
  });

  it("reaches AuthService without an Authorization header", async () => {
    const fake = await fakeServer();
    const client = await createTradeApi({
      secret: "secret",
      endpoint: fake.endpoint,
      insecure: true,
    });

    try {
      // AuthService takes its token in the request body. The server rejects
      // TokenDetails outright when an Authorization header is also present.
      await expect(client.auth.tokenDetails({ token: client.getToken() })).resolves.toMatchObject({
        accountIds: ["A1"],
      });
      expect(fake.tokenDetailsAuthorization).toEqual([undefined]);

      // Every other service still receives the header.
      await client.accounts.getAccount({ accountId: "A1" });
      expect(fake.authorization.at(-1)).toBe("jwt-1");
    } finally {
      await client.close();
      await fake.close();
    }
  });

  it("retries unavailable unary calls with the configured policy", async () => {
    const fake = await fakeServer({ unavailableCalls: 2 });
    const client = await createTradeApi({
      secret: "secret",
      endpoint: fake.endpoint,
      insecure: true,
      retry: {
        maxAttempts: 3,
        initialBackoffMs: 1,
        maxBackoffMs: 2,
      },
    });

    try {
      await expect(client.accounts.getAccount({ accountId: "A1" })).resolves.toMatchObject({
        accountId: "A1",
      });
      expect(fake.accountCalls()).toBe(3);
    } finally {
      await client.close();
      await fake.close();
    }
  });

  it("maps initial authentication failures to AuthError", async () => {
    const fake = await fakeServer({ failAuth: true });
    try {
      await expect(
        createTradeApi({
          secret: "bad",
          endpoint: fake.endpoint,
          insecure: true,
        }),
      ).rejects.toBeInstanceOf(AuthError);
    } finally {
      await fake.close();
    }
  });

  it("maps service failures to typed SDK errors", async () => {
    const fake = await fakeServer({ unavailableCalls: 1 });
    const client = await createTradeApi({
      secret: "secret",
      endpoint: fake.endpoint,
      insecure: true,
      retry: false,
    });

    try {
      await expect(client.accounts.getAccount({ accountId: "A1" })).rejects.toBeInstanceOf(
        ServiceUnavailableError,
      );
    } finally {
      await client.close();
      await fake.close();
    }
  });

  it("withTradeApi closes the renewal stream when work throws", async () => {
    const fake = await fakeServer();
    try {
      await expect(
        withTradeApi(
          {
            secret: "secret",
            endpoint: fake.endpoint,
            insecure: true,
          },
          async () => {
            await waitUntil(fake.renewalStarted);
            throw new Error("work failed");
          },
        ),
      ).rejects.toThrow("work failed");
      await waitUntil(fake.renewalCancelled);
    } finally {
      await fake.close();
    }
  });
});
