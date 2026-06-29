import { updateBillingCustomer } from "../clients/billing-client";

export type CustomerSyncInput = {
  customerId: string;
  plan: "free" | "pro";
  valid?: boolean;
};

export async function syncCustomerToBilling(input: CustomerSyncInput): Promise<void> {
  await updateBillingCustomer({
    customerId: input.customerId,
    plan: input.plan,
    valid: input.valid,
  });
}
