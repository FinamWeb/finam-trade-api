import type { TradeApi } from "@finam/trade-api";
import type { Bar } from "@finam/trade-api/market-data";
import { OrderType, orderStatusToJSON, Side, TimeInForce } from "@finam/trade-api/orders";
import type { Config, LogLevel } from "./config.js";
import { TIMEFRAMES } from "./config.js";
import type { Signal } from "./strategy.js";
import { evaluate } from "./strategy.js";

export type StrategyApi = Readonly<{
  auth: Pick<TradeApi["auth"], "tokenDetails">;
  getToken: TradeApi["getToken"];
  marketData: Pick<TradeApi["marketData"], "bars" | "subscribeBars">;
  accounts: Pick<TradeApi["accounts"], "getAccount">;
  orders: Pick<TradeApi["orders"], "placeOrder">;
}>;

const LOG_PRIORITY: Record<LogLevel, number> = {
  DEBUG: 10,
  INFO: 20,
  WARNING: 30,
  ERROR: 40,
};

export const log = (config: Config, level: LogLevel, message: string): void => {
  if (LOG_PRIORITY[level] < LOG_PRIORITY[config.logLevel]) return;
  if (level === "ERROR") console.error(message);
  else if (level === "WARNING") console.warn(message);
  else console.info(message);
};

const barKey = (bar: Pick<Bar, "timestamp">): number => {
  if (!bar.timestamp) throw new Error("bar timestamp is missing");
  return bar.timestamp.getTime();
};

export const orderedBars = (bars: readonly Bar[]): Bar[] => {
  const byTimestamp = new Map<number, Bar>();
  for (const bar of bars) byTimestamp.set(barKey(bar), bar);
  return [...byTimestamp.entries()].sort(([left], [right]) => left - right).map(([, bar]) => bar);
};

const decimal = (value: { value: string } | undefined): number => {
  const parsed = Number(value?.value ?? "0");
  if (!Number.isFinite(parsed)) throw new Error(`invalid decimal: ${value?.value}`);
  return parsed;
};

const history = async (
  api: StrategyApi,
  config: Config,
  now = new Date(),
): Promise<{ closes: number[]; pending: Bar }> => {
  const [timeframe, lookbackDays] = TIMEFRAMES[config.timeframe];
  const response = await api.marketData.bars({
    symbol: config.symbol,
    timeframe,
    interval: {
      startTime: new Date(now.getTime() - lookbackDays * 86_400_000),
      endTime: now,
    },
  });
  const bars = orderedBars(response.bars);
  if (bars.length < 31) {
    throw new Error(`at least 31 historical bars are required; received ${bars.length}`);
  }
  const pending = bars.at(-1);
  if (!pending) throw new Error("historical response did not contain a pending bar");

  return {
    closes: bars.slice(0, -1).map((bar) => decimal(bar.close)),
    pending,
  };
};

const position = async (api: StrategyApi, accountId: string, symbol: string): Promise<number> => {
  const account = await api.accounts.getAccount({ accountId });
  return decimal(account.positions.find((item) => item.symbol === symbol)?.quantity);
};

export const resolveAccountId = async (api: StrategyApi): Promise<string> => {
  const details = await api.auth.tokenDetails({ token: api.getToken() });
  const [accountId] = details.accountIds;
  if (details.accountIds.length !== 1 || !accountId) {
    throw new Error(
      `Expected exactly one available account; received ${details.accountIds.length}`,
    );
  }
  return accountId;
};

export const placeOrder = async (
  api: StrategyApi,
  config: Config,
  accountId: string | undefined,
  signal: Signal,
  bar: Bar,
): Promise<void> => {
  if (!signal) return;
  if (!config.execute) {
    log(config, "WARNING", `DRY RUN: ${signal} ${config.quantity} units of ${config.symbol}`);
    return;
  }

  if (!accountId) throw new Error("account ID is required in execute mode");

  const current = await position(api, accountId, config.symbol);
  if (signal === "entry" && current !== 0) {
    log(config, "WARNING", `Skipping entry: current position is ${current}, expected zero`);
    return;
  }
  if (signal === "exit" && current <= 0) {
    log(config, "WARNING", "Skipping exit: there is no long position");
    return;
  }

  const side = signal === "entry" ? Side.SIDE_BUY : Side.SIDE_SELL;
  const quantity = signal === "entry" ? config.quantity : Math.min(current, config.quantity);
  const seconds = Math.floor(barKey(bar) / 1_000)
    .toString()
    .slice(-10)
    .padStart(10, "0");
  const state = await api.orders.placeOrder(
    {
      accountId,
      symbol: config.symbol,
      quantity: { value: String(quantity) },
      side,
      type: OrderType.ORDER_TYPE_MARKET,
      timeInForce: TimeInForce.TIME_IN_FORCE_DAY,
      clientOrderId: `sma9x30-${signal === "entry" ? "b" : "s"}-${seconds}`,
      comment: "SMA 9/30 crossover",
    },
    { retry: false },
  );
  log(config, "WARNING", `Submitted order ${state.orderId}: ${orderStatusToJSON(state.status)}`);
};

type MarketState = {
  closes: number[];
  pending: Bar;
};

const processBar = async (
  api: StrategyApi,
  config: Config,
  state: MarketState,
  bar: Bar,
  accountId: string | undefined,
): Promise<MarketState> => {
  if (barKey(bar) < barKey(state.pending)) return state;
  if (barKey(bar) === barKey(state.pending)) return { ...state, pending: bar };

  const closes = [...state.closes, decimal(state.pending.close)].slice(-31);
  const result = evaluate(closes);
  log(
    config,
    "INFO",
    `Closed bar: close=${closes.at(-1)} sma9=${result.fast} ` +
      `sma30=${result.slow} signal=${result.signal ?? "none"}`,
  );
  await placeOrder(api, config, accountId, result.signal, state.pending);
  return { closes, pending: bar };
};

export const run = async (api: StrategyApi, config: Config): Promise<void> => {
  const accountId = config.execute ? await resolveAccountId(api) : undefined;
  let state = await history(api, config);
  const result = evaluate(state.closes);
  log(
    config,
    "INFO",
    `History ready: close=${state.closes.at(-1)} sma9=${result.fast} sma30=${result.slow}`,
  );

  if (config.check) {
    console.log(
      `History check passed: close=${state.closes.at(-1)} sma9=${result.fast} ` +
        `sma30=${result.slow} signal=${result.signal ?? "none"}`,
    );
    return;
  }

  const [timeframe] = TIMEFRAMES[config.timeframe];
  for await (const response of api.marketData.subscribeBars({
    symbol: config.symbol,
    timeframe,
  })) {
    for (const bar of orderedBars(response.bars)) {
      state = await processBar(api, config, state, bar, accountId);
    }
  }
};
