import { randomUUID } from "node:crypto";

import { withTradeApi } from "@finam/trade-api";
import { OrderType, Side, TimeInForce } from "@finam/trade-api/orders";

const secret = process.env.TRADE_API_SECRET;
const symbol = process.env.TRADE_API_SYMBOL ?? "SBER@MISX";
const quantity = process.env.TRADE_API_QUANTITY ?? "1";
const limitPrice = process.env.TRADE_API_LIMIT_PRICE;

if (!secret) {
  throw new Error("Set TRADE_API_SECRET");
}
if (process.env.TRADE_API_EXECUTE !== "1") {
  throw new Error("Set TRADE_API_EXECUTE=1 to acknowledge that this example places a real order");
}
if (!limitPrice) {
  throw new Error("Set TRADE_API_LIMIT_PRICE to the limit price you intend to submit");
}

await withTradeApi({ secret }, async (api) => {
  const details = await api.auth.tokenDetails({ token: api.getToken() });
  const [accountId] = details.accountIds;
  if (details.accountIds.length !== 1 || !accountId) {
    throw new Error(
      `Expected exactly one available account; received ${details.accountIds.length}`,
    );
  }
  const order = await api.orders.placeOrder({
    accountId,
    symbol,
    quantity: { value: quantity },
    side: Side.SIDE_BUY,
    type: OrderType.ORDER_TYPE_LIMIT,
    timeInForce: TimeInForce.TIME_IN_FORCE_DAY,
    limitPrice: { value: limitPrice },
    clientOrderId: randomUUID().replaceAll("-", "").slice(0, 20),
  });

  console.log("Placed order:", order.orderId);
});
