import assert from "node:assert/strict";
import test from "node:test";

import { runNightlySync } from "../../src/jobs/nightly-sync-job";
import { syncCustomer } from "../../src/services/customer-sync-service";

test("syncCustomer pushes data to both external systems", async () => {
  const result = await syncCustomer("cust-1");

  assert.equal(result.ok, true);
  assert.equal(result.crmRemoteId, "crm:cust-1");
  assert.equal(result.billingRemoteId, "billing:cust-1");
});

test("runNightlySync loops through customers and delegates to service", async () => {
  const results = await runNightlySync();

  assert.equal(results.length, 3);
});
