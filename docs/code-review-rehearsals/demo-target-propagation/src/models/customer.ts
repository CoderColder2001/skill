export interface CustomerRecord {
  id: string;
  email: string;
  plan: "free" | "pro";
  valid?: boolean;
}

export interface CustomerPayload {
  id: string;
  email: string;
  plan: "free" | "pro";
  valid?: boolean;
}
