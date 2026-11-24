import { createServer, ServerError, Status } from "nice-grpc";
import { describe, expect, it } from "vitest";
import type { AuthServiceImplementation } from "../src/generated/grpc/tradeapi/v1/auth/auth_service.js";
import { AuthServiceDefinition } from "../src/generated/grpc/tradeapi/v1/auth/auth_service.js";
import type { NewsServiceImplementation } from "../src/generated/grpc/tradeapi/v1/news/news_service.js";
import { NewsServiceDefinition } from "../src/generated/grpc/tradeapi/v1/news/news_service.js";
import type { OrdersServiceImplementation } from "../src/generated/grpc/tradeapi/v1/orders/orders_service.js";
import { OrdersServiceDefinition } from "../src/generated/grpc/tradeapi/v1/orders/orders_service.js";
import { createTradeApi, ServiceUnavailableError } from "../src/index.js";

const unavailable = (): never => {
  throw new ServerError(Status.UNAVAILABLE, "try again");
};

const fakeServer = async () => {
  const server = createServer();
  const orderCalls = { placeOrder: 0, placeSLTPOrder: 0, cancelOrder: 0, getOrder: 0 };
  const newsAuthorization: Array<string | Uint8Array | undefined> = [];

  const auth = {
    async auth() {
      return { token: "jwt-1" };
    },
    async tokenDetails() {
      return { accountIds: ["A1"], readonly: false };
    },
    async *subscribeJwtRenewal() {},
  } satisfies AuthServiceImplementation;

  const orders = {
    async placeOrder() {
      orderCalls.placeOrder += 1;
      return unavailable();
    },
    async placeSLTPOrder() {
      orderCalls.placeSLTPOrder += 1;
      return unavailable();
    },
    async cancelOrder() {
      orderCalls.cancelOrder += 1;
      return unavailable();
    },
    async getOrder() {
      orderCalls.getOrder += 1;
      return unavailable();
    },
    async getOrders() {
      return { orders: [] };
    },
    async *subscribeOrderTrade() {},
    async *subscribeOrders() {},
    async *subscribeTrades() {},
  } satisfies OrdersServiceImplementation;

  const news = {
    async *subscribeNews() {},
    async getNewsHistory() {
      return { items: [] };
    },
    async getNews(request) {
      return { item: { id: request.newsId } };
    },
    async getNewsSources(_request, context) {
      newsAuthorization.push(context.metadata.get("authorization"));
      return { sources: [{ id: "src-1", name: "Source" }] };
    },
  } satisfies NewsServiceImplementation;

  server.add(AuthServiceDefinition, auth);
  server.add(OrdersServiceDefinition, orders);
  server.add(NewsServiceDefinition, news);
  const port = await server.listen("127.0.0.1:0");

  return {
    endpoint: `127.0.0.1:${port}`,
    orderCalls: () => ({ ...orderCalls }),
    newsAuthorization,
    close: () => server.shutdown(),
  };
};

describe("service wiring", () => {
  it("does not retry non-idempotent order mutations by default", async () => {
    const fake = await fakeServer();
    const client = await createTradeApi({
      secret: "secret",
      endpoint: fake.endpoint,
      insecure: true,
      retry: { maxAttempts: 3, initialBackoffMs: 1, maxBackoffMs: 2 },
    });

    try {
      await expect(
        client.orders.placeOrder({ accountId: "A1", symbol: "SBER@MISX" }),
      ).rejects.toBeInstanceOf(ServiceUnavailableError);
      await expect(
        client.orders.placeSLTPOrder({ accountId: "A1", symbol: "SBER@MISX" }),
      ).rejects.toBeInstanceOf(ServiceUnavailableError);
      await expect(
        client.orders.cancelOrder({ accountId: "A1", orderId: "1" }),
      ).rejects.toBeInstanceOf(ServiceUnavailableError);
      await expect(
        client.orders.getOrder({ accountId: "A1", orderId: "1" }),
      ).rejects.toBeInstanceOf(ServiceUnavailableError);
      expect(fake.orderCalls()).toEqual({
        placeOrder: 1,
        placeSLTPOrder: 1,
        cancelOrder: 1,
        getOrder: 3,
      });
    } finally {
      await client.close();
      await fake.close();
    }
  });

  it("exposes NewsService on the authorized channel", async () => {
    const fake = await fakeServer();
    const client = await createTradeApi({
      secret: "secret",
      endpoint: fake.endpoint,
      insecure: true,
    });

    try {
      await expect(client.news.getNewsSources({})).resolves.toMatchObject({
        sources: [{ id: "src-1", name: "Source" }],
      });
      expect(fake.newsAuthorization).toEqual(["jwt-1"]);
    } finally {
      await client.close();
      await fake.close();
    }
  });
});
