export type Signal = "entry" | "exit" | null;

export type Evaluation = Readonly<{
  fast: number;
  slow: number;
  signal: Signal;
}>;

const mean = (values: readonly number[]): number =>
  values.reduce((total, value) => total + value, 0) / values.length;

/** Pure SMA calculation and crossover rule, independent from the SDK. */
export const evaluate = (
  closes: readonly number[],
  fastWindow = 9,
  slowWindow = 30,
): Evaluation => {
  if (fastWindow <= 0 || slowWindow <= fastWindow) {
    throw new RangeError("windows must satisfy 0 < fastWindow < slowWindow");
  }
  if (closes.length < slowWindow) {
    throw new RangeError(`at least ${slowWindow} closes are required`);
  }

  const fast = mean(closes.slice(-fastWindow));
  const slow = mean(closes.slice(-slowWindow));
  if (closes.length === slowWindow) return { fast, slow, signal: null };

  const previous = closes.slice(0, -1);
  const previousFast = mean(previous.slice(-fastWindow));
  const previousSlow = mean(previous.slice(-slowWindow));
  const signal =
    previousFast <= previousSlow && fast > slow
      ? "entry"
      : previousFast >= previousSlow && fast < slow
        ? "exit"
        : null;

  return { fast, slow, signal };
};
