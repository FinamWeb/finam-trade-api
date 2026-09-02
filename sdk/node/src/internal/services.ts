import type { Channel, ClientFactory } from "nice-grpc";
import type { RetryOptions } from "nice-grpc-client-middleware-retry";
import type { AccountsServiceClient } from "../generated/grpc/tradeapi/v1/accounts/accounts_service.js";
import { AccountsServiceDefinition } from "../generated/grpc/tradeapi/v1/accounts/accounts_service.js";
import type { AssetsServiceClient } from "../generated/grpc/tradeapi/v1/assets/assets_service.js";
import { AssetsServiceDefinition } from "../generated/grpc/tradeapi/v1/assets/assets_service.js";
import type { AuthServiceClient } from "../generated/grpc/tradeapi/v1/auth/auth_service.js";
import { AuthServiceDefinition } from "../generated/grpc/tradeapi/v1/auth/auth_service.js";
import type { CorporateActionsServiceClient } from "../generated/grpc/tradeapi/v1/corporateactions/corporate_actions_service.js";
import { CorporateActionsServiceDefinition } from "../generated/grpc/tradeapi/v1/corporateactions/corporate_actions_service.js";
import type { MarketDataServiceClient } from "../generated/grpc/tradeapi/v1/marketdata/marketdata_service.js";
import { MarketDataServiceDefinition } from "../generated/grpc/tradeapi/v1/marketdata/marketdata_service.js";
import type { UsageMetricsServiceClient } from "../generated/grpc/tradeapi/v1/metrics/usage_metrics_service.js";
import { UsageMetricsServiceDefinition } from "../generated/grpc/tradeapi/v1/metrics/usage_metrics_service.js";
import type { OrdersServiceClient } from "../generated/grpc/tradeapi/v1/orders/orders_service.js";
import { OrdersServiceDefinition } from "../generated/grpc/tradeapi/v1/orders/orders_service.js";
import type { ReportsServiceClient } from "../generated/grpc/tradeapi/v1/reports/reports_service.js";
import { ReportsServiceDefinition } from "../generated/grpc/tradeapi/v1/reports/reports_service.js";

/**
 * The two client factories a Trade API client needs.
 *
 * `AuthService` must be reached without an Authorization header, so it cannot
 * share the factory that every other service uses.
 */
export type ServiceClientFactories = Readonly<{
  authorized: ClientFactory<RetryOptions>;
  unauthenticated: ClientFactory<RetryOptions>;
}>;

export type ServiceClients = Readonly<{
  auth: AuthServiceClient<RetryOptions>;
  accounts: AccountsServiceClient<RetryOptions>;
  assets: AssetsServiceClient<RetryOptions>;
  corporateActions: CorporateActionsServiceClient<RetryOptions>;
  marketData: MarketDataServiceClient<RetryOptions>;
  orders: OrdersServiceClient<RetryOptions>;
  reports: ReportsServiceClient<RetryOptions>;
  metrics: UsageMetricsServiceClient<RetryOptions>;
}>;

export const createServiceClients = (
  factories: ServiceClientFactories,
  channel: Channel,
  retry: RetryOptions,
): ServiceClients => {
  const defaults = { "*": retry } as const;
  const { authorized, unauthenticated } = factories;

  return {
    // AuthService authenticates with the secret or with a token carried in the
    // request body, never with an Authorization header. TokenDetails is
    // rejected outright when one is present, so this client must not add it.
    auth: unauthenticated.create(AuthServiceDefinition, channel, defaults),
    accounts: authorized.create(AccountsServiceDefinition, channel, defaults),
    assets: authorized.create(AssetsServiceDefinition, channel, defaults),
    corporateActions: authorized.create(CorporateActionsServiceDefinition, channel, defaults),
    marketData: authorized.create(MarketDataServiceDefinition, channel, defaults),
    orders: authorized.create(OrdersServiceDefinition, channel, defaults),
    reports: authorized.create(ReportsServiceDefinition, channel, defaults),
    metrics: authorized.create(UsageMetricsServiceDefinition, channel, defaults),
  };
};
