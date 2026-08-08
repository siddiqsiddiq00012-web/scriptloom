import { api } from "./client";

export function getPlans() {
  return api.get("/billing/plans");
}

export function getProviderStatus() {
  return api.get("/billing/provider-status");
}

export function getSubscription() {
  return api.get("/billing/subscription");
}

export function getUsage() {
  return api.get("/billing/usage");
}

export function createCheckoutSession({ plan_key, billing_cycle = "monthly", success_url, cancel_url }) {
  return api.post("/billing/checkout", { plan_key, billing_cycle, success_url, cancel_url });
}

export function cancelSubscription({ immediately = false } = {}) {
  return api.post("/billing/cancel-subscription", { immediately });
}

export function getInvoices(limit = 10) {
  return api.get(`/billing/invoices?limit=${limit}`);
}

export function formatPrice(cents, currency = "USD") {
  if (cents === 0) return "$0";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency || "USD",
    minimumFractionDigits: 0,
  }).format(cents / 100);
}

export function formatStorage(bytes) {
  if (bytes === -1 || bytes === undefined || bytes === null) return "Unlimited";
  if (bytes <= 0) return "0 GB";
  const gb = bytes / (1024 * 1024 * 1024);
  if (gb >= 1) return `${gb.toFixed(0)} GB`;
  const mb = bytes / (1024 * 1024);
  if (mb >= 1) return `${mb.toFixed(0)} MB`;
  return `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

export function formatMinutes(minutes) {
  if (minutes === -1) return "Unlimited";
  if (minutes >= 60) {
    const hours = (minutes / 60).toFixed(1);
    return `${hours} hr${hours === "1.0" ? "" : "s"}`;
  }
  return `${minutes} min`;
}
