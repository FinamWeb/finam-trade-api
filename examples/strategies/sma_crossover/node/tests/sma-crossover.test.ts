import type { Bar } from "@finam/trade-api/market-data";
import { describe, expect, it, vi } from "vitest";

import type { Config } from "../config.js";
import type { StrategyApi } from "../runner.js";
import { orderedBars, placeOrder, resolveAccountId, run } from "../runner.js";
import { evaluate } from "../strategy.js";

const bar = (seconds: number, close = "0") =>
  ({
    timestamp: new Date(seconds * 1_000),
    open: undefined,
    high: undefined,
    low: undefined,
    close: { value: close },
    volume: undefined,
  }) as Bar;

const config = (overrides: Partial<Config> = {}): Config => ({
  secret: "secret",
  symbol: "SBER@MISX",
  timeframe: "M5",
  quantity: 2,
  execute: false,
  check: false,
  logLevel: "ERROR",
  ...overrides,
});

const fakeApi = (
  bars = Array.from({ length: 32 }, (_, index) => bar(index + 1, `${index}`)),
  accountIds = ["A1"],
) => {
  let accountCalls = 0;
  let tokenDetailsCalls = 0;
  const placed: Array<{ side?: number; quantity?: { value?: string } }> = [];
  let positionValue = "0";

  const api = {
    getToken: () => "jwt",
    auth: {
      tokenDetails: async () => {
        tokenDetailsCalls += 1;
        return { accountIds };
      },
    },
    marketData: {
      bars: async () => ({ symbol: "SBER@MISX", bars }),
      subscribeBars: async function* () {},
    },
    accounts: {
      getAccount: async () => {
        accountCalls += 1;
        return {
          positions:
            positionValue === "0"
              ? []
              : [{ symbol: "SBER@MISX", quantity: { value: positionValue } }],
        };
      },
    },
    orders: {
      placeOrder: async (order: { side?: number; quantity?: { value?: string } }) => {
        placed.push(order);
        return { orderId: "order-1", status: 1 };
      },
    },
  } as unknown as StrategyApi;

  return {
    api,
    placed,
    accountCalls: () => accountCalls,
    tokenDetailsCalls: () => tokenDetailsCalls,
    setPosition: (value: string) => {
      positionValue = value;
    },
  };
};

describe("SMA 9/30 strategy", () => {
  it("detects one entry and one exit", () => {
    const closes = Array.from({ length: 92 }, (_, index) => {
      const base =
        index < 32
          ? 121 - index * 0.42
          : index < 62
            ? 107.56 + (index - 32) * 0.72
            : 129.16 - (index - 62) * 0.82;
      return base + Math.sin(index * 0.7) * 0.65 + Math.sin(index * 0.19) * 0.35;
    });

    const signals = closes
      .slice(29)
      .map((_, index) => evaluate(closes.slice(0, index + 30)).signal);
    expect(signals.filter((signal) => signal === "entry")).toHaveLength(1);
    expect(signals.filter((signal) => signal === "exit")).toHaveLength(1);
  });

  it("requires the slow window", () => {
    expect(() => evaluate(Array(29).fill(1))).toThrow("30 closes");
  });

  it("sorts bars and keeps the newest update", () => {
    const bars = orderedBars([bar(2, "old"), bar(1), bar(2, "new")]);
    expect(bars.map((item) => item.timestamp?.getTime())).toEqual([1_000, 2_000]);
    expect(bars.at(-1)?.close?.value).toBe("new");
  });

  it("keeps history check read-only", async () => {
    const fake = fakeApi();
    const output = vi.spyOn(console, "log").mockImplementation(() => undefined);
    try {
      await run(fake.api, config({ check: true }));
      expect(output).toHaveBeenCalledWith(expect.stringContaining("History check passed"));
      expect(fake.tokenDetailsCalls()).toBe(0);
      expect(fake.accountCalls()).toBe(0);
      expect(fake.placed).toEqual([]);
    } finally {
      output.mockRestore();
    }
  });

  it("does not read the account or place an order in dry-run", async () => {
    const fake = fakeApi();
    await placeOrder(fake.api, config(), undefined, "entry", bar(1));
    expect(fake.tokenDetailsCalls()).toBe(0);
    expect(fake.accountCalls()).toBe(0);
    expect(fake.placed).toEqual([]);
  });

  it("buys only when flat", async () => {
    const fake = fakeApi();
    await placeOrder(fake.api, config({ execute: true }), "A1", "entry", bar(1));
    expect(fake.placed[0]).toMatchObject({ side: 1, quantity: { value: "2" } });
  });

  it("caps an exit at the current long position", async () => {
    const fake = fakeApi();
    fake.setPosition("0.5");
    await placeOrder(fake.api, config({ execute: true }), "A1", "exit", bar(1));
    expect(fake.placed[0]).toMatchObject({ side: 2, quantity: { value: "0.5" } });
  });

  it("resolves the sole account from token details", async () => {
    const fake = fakeApi();
    await expect(resolveAccountId(fake.api)).resolves.toBe("A1");
    expect(fake.tokenDetailsCalls()).toBe(1);
  });

  it("rejects ambiguous account access", async () => {
    const fake = fakeApi(undefined, ["A1", "A2"]);
    await expect(resolveAccountId(fake.api)).rejects.toThrow(
      "Expected exactly one available account; received 2",
    );
  });
});
