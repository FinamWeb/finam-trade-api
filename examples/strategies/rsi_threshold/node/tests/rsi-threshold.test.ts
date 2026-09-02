import type { Bar } from "@finam/trade-api/market-data";
import { describe, expect, it, vi } from "vitest";

import type { Config } from "../config.js";
import type { StrategyApi } from "../runner.js";
import { orderedBars, placeOrder, resolveAccountId, run } from "../runner.js";
import { evaluate, MINIMUM_CLOSES, NEUTRAL } from "../strategy.js";

// One oversold entry and one overbought exit; see the walk-forward test.
const ENTRY_INDEX = 24;
const EXIT_INDEX = 71;

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

/** Sideways, then a sell-off into oversold, then a rally into overbought. */
const sampleCloses = (count = 95): number[] =>
  Array.from({ length: count }, (_, index) => {
    const base = index < 20 ? 100 : index < 50 ? 100 - (index - 20) * 0.8 : 76 + (index - 50) * 0.8;
    return base + Math.sin(index * 0.7) * 0.45 + Math.sin(index * 0.19) * 0.3;
  });

/** A warm-up window whose closes all move by the same step. */
const ramp = (step: number): number[] =>
  Array.from({ length: MINIMUM_CLOSES }, (_, index) => 50 + index * step);

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

describe("RSI 14 threshold strategy", () => {
  it("enters when oversold and exits when overbought", () => {
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

  it("enters on the first close below the entry level", () => {
    const closes = sampleCloses();
    const before = evaluate(closes.slice(0, ENTRY_INDEX));
    expect(before.rsi).toBeGreaterThanOrEqual(0.2);
    expect(before.signal).toBeNull();
    expect(evaluate(closes.slice(0, ENTRY_INDEX + 1)).rsi).toBeLessThan(0.2);
  });

  it("exits on the first close above the exit level", () => {
    const closes = sampleCloses();
    expect(evaluate(closes.slice(0, EXIT_INDEX), true).rsi).toBeLessThanOrEqual(0.8);
    expect(evaluate(closes.slice(0, EXIT_INDEX + 1), true).rsi).toBeGreaterThan(0.8);
  });

  it("ignores an oversold reading while in position", () => {
    // The candle after the entry is still oversold; the position flag, not the
    // level, is what stops a second entry.
    const closes = sampleCloses().slice(0, ENTRY_INDEX + 2);
    expect(evaluate(closes, true).signal).toBeNull();
    expect(evaluate(closes, false).signal).toBe("entry");
  });

  it("ignores an overbought reading while flat", () => {
    const closes = sampleCloses().slice(0, EXIT_INDEX + 2);
    expect(evaluate(closes, false).signal).toBeNull();
    expect(evaluate(closes, true).signal).toBe("exit");
  });

  // A steady ramp puts every change on one side of the ratio, and a flat
  // series has no change at all.
  it.each([
    { market: "only gains", step: 1, inPosition: true, rsi: 1, signal: "exit" },
    { market: "only losses", step: -1, inPosition: false, rsi: 0, signal: "entry" },
    { market: "no change", step: 0, inPosition: false, rsi: NEUTRAL, signal: null },
  ])("reads $market as rsi $rsi", ({ step, inPosition, rsi, signal }) => {
    const result = evaluate(ramp(step), inPosition);
    expect(result.rsi).toBe(rsi);
    expect(result.signal).toBe(signal);
  });

  it("reports Wilder's averages alongside the ratio", () => {
    const result = evaluate(ramp(1));
    expect(result.averageGain).toBeCloseTo(1, 10);
    expect(result.averageLoss).toBe(0);
  });

  it("requires the warm-up window", () => {
    expect(() => evaluate(Array(MINIMUM_CLOSES - 1).fill(1))).toThrow("15 closes");
  });

  it("rejects levels out of order", () => {
    expect(() => evaluate(sampleCloses(), false, 14, 0.8, 0.2)).toThrow("entryLevel < exitLevel");
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
      "at least 16 historical bars are required",
    );
  });

  it("alternates entry and exit across a dry-run stream", async () => {
    const bars = sampleCloses().map((close, index) => bar(index + 1, `${close}`));
    const fake = fakeApi(bars.slice(0, 20), ["A1"], [bars.slice(20)]);
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
      clientOrderId: "rsi14-b-0000000001",
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
