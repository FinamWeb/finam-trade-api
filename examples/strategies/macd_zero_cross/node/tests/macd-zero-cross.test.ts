import type { Bar } from "@finam/trade-api/market-data";
import { describe, expect, it, vi } from "vitest";

import type { Config } from "../config.js";
import type { StrategyApi } from "../runner.js";
import { orderedBars, placeOrder, resolveAccountId, run } from "../runner.js";
import { evaluate, MINIMUM_CLOSES } from "../strategy.js";

// One entry cross and one two-declining-bars exit; see the walk-forward test.
const ENTRY_INDEX = 57;
const EXIT_INDEX = 82;

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

/** A fall, then a rally through zero, then a decline. */
const sampleCloses = (count = 110): number[] =>
  Array.from({ length: count }, (_, index) => {
    const base =
      index < 45
        ? 121 - index * 0.42
        : index < 80
          ? 102.1 + (index - 45) * 0.72
          : 127.3 - (index - 80) * 0.82;
    return base + Math.sin(index * 0.7) * 0.65 + Math.sin(index * 0.19) * 0.35;
  });

const historyBars = (count = MINIMUM_CLOSES + 1) =>
  Array.from({ length: count }, (_, index) => bar(index + 1, `${index + 1}`));

type PlacedOrder = { side?: number; quantity?: { value?: string }; clientOrderId?: string };

const fakeApi = (bars = historyBars(), accountIds = ["A1"], updates: Bar[][] = []) => {
  let accountCalls = 0;
  let tokenDetailsCalls = 0;
  const placed: PlacedOrder[] = [];
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
      subscribeBars: async function* () {
        for (const update of updates) yield { bars: update };
      },
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
      placeOrder: async (order: PlacedOrder) => {
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

describe("MACD 12/26/9 zero-cross strategy", () => {
  it("enters on the zero cross and exits after two declines", () => {
    const closes = sampleCloses();
    const events: Array<[number, string]> = [];
    let inPosition = false;

    for (let index = MINIMUM_CLOSES; index <= closes.length; index += 1) {
      const { signal } = evaluate(closes.slice(0, index), inPosition);
      if (signal) {
        events.push([index - 1, signal]);
        inPosition = signal === "entry";
      }
    }

    expect(events).toEqual([
      [ENTRY_INDEX, "entry"],
      [EXIT_INDEX, "exit"],
    ]);
  });

  it("crosses zero upwards on the entry bar", () => {
    const closes = sampleCloses();
    const previous = evaluate(closes.slice(0, ENTRY_INDEX)).macd;
    const current = evaluate(closes.slice(0, ENTRY_INDEX + 1)).macd;
    expect(previous).toBeLessThanOrEqual(0);
    expect(current).toBeGreaterThan(0);
  });

  it("exits after two declining values", () => {
    const closes = sampleCloses();
    const [older, previous, current] = [2, 1, 0].map(
      (offset) => evaluate(closes.slice(0, EXIT_INDEX + 1 - offset), true).macd,
    );
    expect(current).toBeLessThan(previous as number);
    expect(previous).toBeLessThan(older as number);
  });

  it("ignores a zero cross while in position", () => {
    expect(evaluate(sampleCloses().slice(0, ENTRY_INDEX + 1), true).signal).toBeNull();
  });

  it("ignores declining values while flat", () => {
    expect(evaluate(sampleCloses().slice(0, EXIT_INDEX + 1), false).signal).toBeNull();
  });

  it("reports the signal line and histogram", () => {
    // A unit-slope ramp holds every EMA exactly (window - 1) / 2 behind price,
    // so the MACD line settles on (slowWindow - fastWindow) / 2.
    const result = evaluate(Array.from({ length: MINIMUM_CLOSES }, (_, index) => index + 1));
    expect(result.macd).toBeCloseTo(7, 10);
    expect(result.signalLine).toBeCloseTo(7, 10);
    expect(result.histogram).toBeCloseTo(0, 10);
    expect(result.signal).toBeNull();
  });

  it("requires the warm-up window", () => {
    expect(() => evaluate(Array(MINIMUM_CLOSES - 1).fill(1))).toThrow("34 closes");
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

  it("requires a warmed-up history", async () => {
    const fake = fakeApi(historyBars(MINIMUM_CLOSES));
    await expect(run(fake.api, config({ check: true }))).rejects.toThrow(
      "at least 35 historical bars are required",
    );
  });

  it("alternates entry and exit across a dry-run stream", async () => {
    const bars = sampleCloses().map((close, index) => bar(index + 1, `${close}`));
    const fake = fakeApi(bars.slice(0, 40), ["A1"], [bars.slice(40)]);
    const warn = vi.spyOn(console, "warn").mockImplementation(() => undefined);
    try {
      await run(fake.api, config({ logLevel: "WARNING" }));
      const signals = warn.mock.calls
        .map(([message]) => String(message))
        .filter((message) => message.includes("DRY RUN"));
      expect(signals).toHaveLength(2);
      expect(signals[0]).toContain("DRY RUN: entry");
      expect(signals[1]).toContain("DRY RUN: exit");
    } finally {
      warn.mockRestore();
    }
  });

  it("does not read the account or place an order in dry-run", async () => {
    const fake = fakeApi();
    await expect(placeOrder(fake.api, config(), undefined, "entry", bar(1))).resolves.toBe(true);
    expect(fake.tokenDetailsCalls()).toBe(0);
    expect(fake.accountCalls()).toBe(0);
    expect(fake.placed).toEqual([]);
  });

  it("leaves the position unchanged without a signal", async () => {
    const fake = fakeApi();
    await expect(placeOrder(fake.api, config({ execute: true }), "A1", null, bar(1))).resolves.toBe(
      false,
    );
    expect(fake.accountCalls()).toBe(0);
    expect(fake.placed).toEqual([]);
  });

  it("buys only when flat", async () => {
    const fake = fakeApi();
    await placeOrder(fake.api, config({ execute: true }), "A1", "entry", bar(1));
    expect(fake.placed[0]).toMatchObject({
      side: 1,
      quantity: { value: "2" },
      clientOrderId: "macd0-b-0000000001",
    });
  });

  it("skips an entry when a position exists", async () => {
    const fake = fakeApi();
    fake.setPosition("3");
    await expect(
      placeOrder(fake.api, config({ execute: true }), "A1", "entry", bar(1)),
    ).resolves.toBe(false);
    expect(fake.placed).toEqual([]);
  });

  it("returns to flat when an exit finds no position", async () => {
    const fake = fakeApi();
    await expect(
      placeOrder(fake.api, config({ execute: true }), "A1", "exit", bar(1)),
    ).resolves.toBe(true);
    expect(fake.placed).toEqual([]);
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
