import type { CustomerPayload } from "../../src/models/customer";

export function buildCustomerPayload(overrides: Partial<CustomerPayload> = {}): CustomerPayload {
  return {
    id: "cus_123",
    email: "customer@example.com",
    plan: "free",
    ...overrides,
  };
}
