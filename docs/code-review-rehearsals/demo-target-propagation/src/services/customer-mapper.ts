import type { CustomerPayload, CustomerRecord } from "../models/customer";

export function buildCustomerRecord(payload: CustomerPayload): CustomerRecord {
  return {
    id: payload.id,
    email: payload.email,
    plan: payload.plan,
  };
}

export function serializeCustomer(record: CustomerRecord): CustomerPayload {
  return {
    id: record.id,
    email: record.email,
    plan: record.plan,
  };
}
