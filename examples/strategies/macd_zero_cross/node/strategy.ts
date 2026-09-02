export const FAST_WINDOW = 12;
export const SLOW_WINDOW = 26;
export const SIGNAL_WINDOW = 9;

export type Signal = "entry" | "exit" | null;

export type Evaluation = Readonly<{
  macd: number;
  signalLine: number;
  histogram: number;
  signal: Signal;
}>;

/**
 * Closes needed for a signal line and for three MACD values.
 *
 * The first MACD value needs `slowWindow` closes. The signal line adds
 * `signalWindow - 1` more, and the two-declining-bars rule compares three MACD
 * values.
 */
export const requiredCloses = (slowWindow = SLOW_WINDOW, signalWindow = SIGNAL_WINDOW): number =>
  Math.max(slowWindow + signalWindow - 1, slowWindow + 2);

/**
 * Closes kept while streaming. Ten slow windows make the EMA seed irrelevant to
 * the newest value, so a restart converges on the same MACD.
 */
export const HISTORY_CLOSES = SLOW_WINDOW * 10;
export const MINIMUM_CLOSES = requiredCloses();

const itemAt = (values: readonly number[], index: number): number => {
  const item = values.at(index);
  if (item === undefined) throw new RangeError(`missing value at index ${index}`);
  return item;
};

/** The EMA series, seeded with the average of the first window. */
const emaSeries = (values: readonly number[], window: number): number[] => {
  const multiplier = 2 / (window + 1);
  let current = values.slice(0, window).reduce((total, item) => total + item, 0) / window;
  const series = [current];
  for (const item of values.slice(window)) {
    current = (item - current) * multiplier + current;
    series.push(current);
  }
  return series;
};

/** MACD values, one per close that both EMAs cover. */
export const macdSeries = (
  closes: readonly number[],
  fastWindow = FAST_WINDOW,
  slowWindow = SLOW_WINDOW,
): number[] => {
  const fast = emaSeries(closes, fastWindow);
  const slow = emaSeries(closes, slowWindow);
  const offset = fast.length - slow.length;
  return slow.map((slowValue, index) => itemAt(fast, index + offset) - slowValue);
};

/**
 * Pure MACD calculation and zero-cross rule, independent from the SDK.
 *
 * Entry is the MACD line crossing zero upwards while flat. Exit is two
 * consecutive declining MACD values while holding a position. The signal line
 * and histogram are reported for context; neither rule reads them.
 */
export const evaluate = (
  closes: readonly number[],
  inPosition = false,
  fastWindow = FAST_WINDOW,
  slowWindow = SLOW_WINDOW,
  signalWindow = SIGNAL_WINDOW,
): Evaluation => {
  if (fastWindow <= 0 || slowWindow <= fastWindow) {
    throw new RangeError("windows must satisfy 0 < fastWindow < slowWindow");
  }
  if (signalWindow <= 0) throw new RangeError("signalWindow must be positive");
  const minimum = requiredCloses(slowWindow, signalWindow);
  if (closes.length < minimum) {
    throw new RangeError(`at least ${minimum} closes are required`);
  }

  const macd = macdSeries(closes, fastWindow, slowWindow);
  const signalLine = itemAt(emaSeries(macd, signalWindow), -1);
  const older = itemAt(macd, -3);
  const previous = itemAt(macd, -2);
  const current = itemAt(macd, -1);

  let signal: Signal = null;
  if (inPosition) {
    if (current < previous && previous < older) signal = "exit";
  } else if (previous <= 0 && current > 0) {
    signal = "entry";
  }

  return { macd: current, signalLine, histogram: current - signalLine, signal };
};
