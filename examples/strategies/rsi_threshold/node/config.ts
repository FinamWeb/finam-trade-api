import { parseArgs } from "node:util";

import { TimeFrame } from "@finam/trade-api/market-data";

export const TIMEFRAMES = {
  M1: [TimeFrame.TIME_FRAME_M1, 7],
  M5: [TimeFrame.TIME_FRAME_M5, 14],
  M15: [TimeFrame.TIME_FRAME_M15, 30],
  M30: [TimeFrame.TIME_FRAME_M30, 30],
  H1: [TimeFrame.TIME_FRAME_H1, 30],
  H2: [TimeFrame.TIME_FRAME_H2, 30],
  H4: [TimeFrame.TIME_FRAME_H4, 30],
  H8: [TimeFrame.TIME_FRAME_H8, 30],
  D: [TimeFrame.TIME_FRAME_D, 180],
  W: [TimeFrame.TIME_FRAME_W, 365 * 2],
  MN: [TimeFrame.TIME_FRAME_MN, 365 * 5],
  QR: [TimeFrame.TIME_FRAME_QR, 365 * 5],
} as const;

export type TimeframeName = keyof typeof TIMEFRAMES;
export type LogLevel = "DEBUG" | "INFO" | "WARNING" | "ERROR";

export type Config = Readonly<{
  secret: string;
  symbol: string;
  timeframe: TimeframeName;
  quantity: number;
  execute: boolean;
  check: boolean;
  logLevel: LogLevel;
}>;

const LOG_LEVELS = new Set<LogLevel>(["DEBUG", "INFO", "WARNING", "ERROR"]);

const isTimeframe = (value: string): value is TimeframeName => value in TIMEFRAMES;
const isLogLevel = (value: string): value is LogLevel => LOG_LEVELS.has(value as LogLevel);

const requiredSecret = (value: string | undefined): string => {
  if (!value) throw new Error("--secret or TRADE_API_SECRET is required");
  return value;
};

const validSymbol = (value: string | undefined): string => {
  if (!value?.includes("@")) {
    throw new Error("--symbol must use ticker@mic format, for example SBER@MISX");
  }
  return value;
};

const validTimeframe = (value: string): TimeframeName => {
  if (!isTimeframe(value)) throw new Error(`unsupported timeframe: ${value}`);
  return value;
};

const positiveQuantity = (value: string): number => {
  const quantity = Number(value);
  if (!Number.isFinite(quantity) || quantity <= 0) {
    throw new Error("--quantity must be a positive number");
  }
  return quantity;
};

const validLogLevel = (value: string): LogLevel => {
  if (!isLogLevel(value)) throw new Error(`unsupported log level: ${value}`);
  return value;
};

const validateMode = (execute: boolean, check: boolean): void => {
  if (check && execute) throw new Error("--check and --execute cannot be combined");
};

export const parseConfig = (
  argv: readonly string[],
  env: Readonly<Record<string, string | undefined>> = process.env,
): Config => {
  const { values } = parseArgs({
    args: [...argv],
    options: {
      secret: { type: "string" },
      symbol: { type: "string" },
      timeframe: { type: "string" },
      quantity: { type: "string" },
      execute: { type: "boolean", default: false },
      check: { type: "boolean", default: false },
      "log-level": { type: "string" },
    },
    strict: true,
  });

  const secret = requiredSecret(values.secret ?? env.TRADE_API_SECRET);
  const symbol = validSymbol(values.symbol ?? env.TRADE_API_SYMBOL);
  const timeframe = validTimeframe(
    (values.timeframe ?? env.TRADE_API_TIMEFRAME ?? "M5").toUpperCase(),
  );
  const quantity = positiveQuantity(values.quantity ?? env.TRADE_API_QUANTITY ?? "1");
  const logLevel = validLogLevel(
    (values["log-level"] ?? env.TRADE_API_LOG_LEVEL ?? "INFO").toUpperCase(),
  );
  validateMode(values.execute, values.check);

  return {
    secret,
    symbol,
    timeframe,
    quantity,
    execute: values.execute,
    check: values.check,
    logLevel,
  };
};

export const USAGE = `Usage:
  npm start -- --symbol SBER@MISX [--timeframe M5] [--quantity 1]
  npm start -- --symbol SBER@MISX --check
  npm start -- --symbol SBER@MISX --execute

TRADE_API_SECRET is required. Dry-run is the default.`;
