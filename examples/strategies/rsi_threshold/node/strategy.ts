export const PERIOD = 14;
export const ENTRY_LEVEL = 0.2;
export const EXIT_LEVEL = 0.8;

/**
 * A flat market has no gains and no losses, which leaves the ratio undefined.
 * The midpoint is the conventional reading and sits between both levels, so a
 * gap in the data cannot by itself trigger a trade.
 */
export const NEUTRAL = 0.5;

export type Signal = "entry" | "exit" | null;

export type Evaluation = Readonly<{
  rsi: number;
  averageGain: number;
  averageLoss: number;
  signal: Signal;
}>;

/**
 * Closes needed for one RSI value.
 *
 * Wilder's averages cover `period` price changes, and the first change also
 * needs the close before it.
 */
export const requiredCloses = (period = PERIOD): number => period + 1;

/**
 * Closes kept while streaming. Ten periods make the seed irrelevant to the
 * newest value, so a restart converges on the same RSI.
 */
export const HISTORY_CLOSES = PERIOD * 10;
export const MINIMUM_CLOSES = requiredCloses();

const itemAt = (values: readonly number[], index: number): number => {
  const item = values.at(index);
  if (item === undefined) throw new RangeError(`missing value at index ${index}`);
  return item;
};

/**
 * Consecutive close-to-close changes split into gains and losses.
 *
 * Both are reported as non-negative magnitudes, and an unchanged close
 * contributes zero to each.
 */
const changes = (closes: readonly number[]): { gains: number[]; losses: number[] } => {
  const gains: number[] = [];
  const losses: number[] = [];
  for (let index = 1; index < closes.length; index += 1) {
    const change = itemAt(closes, index) - itemAt(closes, index - 1);
    gains.push(Math.max(change, 0));
    losses.push(Math.max(-change, 0));
  }
  return { gains, losses };
};

/**
 * Wilder's smoothed average gain and loss for the newest close.
 *
 * The averages are seeded with the simple mean of the first `period` changes
 * and then smoothed with weight `1 / period`, which is Wilder's original
 * formulation rather than a standard EMA.
 */
export const wilderAverages = (
  closes: readonly number[],
  period = PERIOD,
): { averageGain: number; averageLoss: number } => {
  const { gains, losses } = changes(closes);
  const mean = (values: readonly number[]): number =>
    values.slice(0, period).reduce((total, item) => total + item, 0) / period;

  let averageGain = mean(gains);
  let averageLoss = mean(losses);
  for (let index = period; index < gains.length; index += 1) {
    averageGain = (averageGain * (period - 1) + itemAt(gains, index)) / period;
    averageLoss = (averageLoss * (period - 1) + itemAt(losses, index)) / period;
  }
  return { averageGain, averageLoss };
};

/**
 * The RSI on a 0..1 scale; multiply by 100 for the 0..100 form.
 *
 * This is the usual `100 - 100 / (1 + gain / loss)` rearranged into
 * `gain / (gain + loss)`. The two agree everywhere, but this form needs no
 * special case for a period without losses.
 */
export const relativeStrengthIndex = (averageGain: number, averageLoss: number): number => {
  const total = averageGain + averageLoss;
  return total === 0 ? NEUTRAL : averageGain / total;
};

/**
 * Pure RSI calculation and threshold rule, independent from the SDK.
 *
 * Entry is an RSI below `entryLevel` while flat. Exit is an RSI above
 * `exitLevel` while holding a position. Both are levels rather than crossings,
 * so the caller's position state is what stops a signal from repeating on every
 * candle that stays beyond its level.
 */
export const evaluate = (
  closes: readonly number[],
  inPosition = false,
  period = PERIOD,
  entryLevel = ENTRY_LEVEL,
  exitLevel = EXIT_LEVEL,
): Evaluation => {
  if (period <= 0) throw new RangeError("period must be positive");
  if (!(entryLevel >= 0 && entryLevel < exitLevel && exitLevel <= 1)) {
    throw new RangeError("levels must satisfy 0 <= entryLevel < exitLevel <= 1");
  }
  const minimum = requiredCloses(period);
  if (closes.length < minimum) {
    throw new RangeError(`at least ${minimum} closes are required`);
  }

  const { averageGain, averageLoss } = wilderAverages(closes, period);
  const rsi = relativeStrengthIndex(averageGain, averageLoss);

  let signal: Signal = null;
  if (inPosition) {
    if (rsi > exitLevel) signal = "exit";
  } else if (rsi < entryLevel) {
    signal = "entry";
  }

  return { rsi, averageGain, averageLoss, signal };
};
