import { pushBillingProfile } from "../clients/billing-client";
import { pushCustomerRecord } from "../clients/crm-client";

export async function syncCustomer(customerId: string) {
  const crmResult = await pushCustomerRecord(customerId);
  const billingResult = await pushBillingProfile(customerId);

  return {
    ok: crmResult.ok && billingResult.ok,
    crmRemoteId: crmResult.remoteId,
    billingRemoteId: billingResult.remoteId,
  };
}
