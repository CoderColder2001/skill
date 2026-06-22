export async function pushBillingProfile(customerId: string) {
  return {
    ok: true,
    remoteId: `billing:${customerId}`,
  };
}
