export type BillingPayload = {
  customerId: string;
  plan: "free" | "pro";
  valid?: boolean;
};

export async function updateBillingCustomer(payload: BillingPayload): Promise<void> {
  void payload;
}
