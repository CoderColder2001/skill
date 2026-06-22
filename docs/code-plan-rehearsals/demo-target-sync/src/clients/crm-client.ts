export async function pushCustomerRecord(customerId: string) {
  return {
    ok: true,
    remoteId: `crm:${customerId}`,
  };
}
