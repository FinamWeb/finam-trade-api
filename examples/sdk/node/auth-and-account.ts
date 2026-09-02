import { withTradeApi } from "@finam/trade-api";

const secret = process.env.TRADE_API_SECRET;

if (!secret) {
  throw new Error("Set TRADE_API_SECRET");
}

await withTradeApi({ secret }, async (api) => {
  const details = await api.auth.tokenDetails({ token: api.getToken() });
  console.log("Available account IDs:", details.accountIds);

  const [accountId] = details.accountIds;
  if (!accountId) {
    console.log("Authentication succeeded; this secret exposes no trading accounts.");
    return;
  }

  const account = await api.accounts.getAccount({ accountId });
  console.log("First account:", account);
});
