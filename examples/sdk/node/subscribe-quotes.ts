import { withTradeApi } from "@finam/trade-api";

const secret = process.env.TRADE_API_SECRET;
const symbol = process.env.TRADE_API_SYMBOL ?? "SBER@MISX";

if (!secret) throw new Error("Set TRADE_API_SECRET");

const abort = new AbortController();
process.once("SIGINT", () => abort.abort());

await withTradeApi({ secret }, async (api) => {
  for await (const update of api.marketData.subscribeQuote(
    { symbols: [symbol] },
    { signal: abort.signal },
  )) {
    console.log(update);
  }
});
