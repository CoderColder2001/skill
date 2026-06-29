import { syncCustomerToBilling, type CustomerSyncInput } from "../services/customer-sync-service";

type NightlyCustomer = CustomerSyncInput & {
  source: "crm" | "billing";
};

export async function runNightlySync(customers: NightlyCustomer[]): Promise<void> {
  for (const customer of customers) {
    await syncCustomerToBilling({
      customerId: customer.customerId,
      plan: customer.plan,
    });
  }
}
