import { syncCustomer } from "../services/customer-sync-service";

const customerIds = ["cust-1", "cust-2", "cust-3"];

export async function runNightlySync() {
  const results = [];

  for (const customerId of customerIds) {
    results.push(await syncCustomer(customerId));
  }

  return results;
}
