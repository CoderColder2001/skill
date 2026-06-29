import type { CustomerSyncInput } from "../../src/services/customer-sync-service";

export function buildCustomerSyncInput(overrides: Partial<CustomerSyncInput> = {}): CustomerSyncInput {
  return {
    customerId: "cus_001",
    plan: "free",
    ...overrides,
  };
}
