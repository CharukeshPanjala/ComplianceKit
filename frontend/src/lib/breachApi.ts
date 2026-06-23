const POLICY_BASE = process.env.NEXT_PUBLIC_POLICY_URL ?? "http://localhost:8001";

// ── Types ─────────────────────────────────────────────────────────────────────

export type BreachType = "confidentiality" | "integrity" | "availability" | "combined";
export type BreachSeverity = "low" | "medium" | "high" | "critical";
export type BreachStatus =
  | "draft"
  | "under_investigation"
  | "reported_to_dpa"
  | "reported_to_individuals"
  | "closed";
export type BreachRegulation = "gdpr" | "nis2" | "both";

export interface BreachIncident {
  breach_id: string;
  title: string;
  description: string | null;
  breach_type: BreachType | null;
  severity: BreachSeverity | null;
  regulation: BreachRegulation | null;
  discovered_at: string | null;
  occurred_at: string | null;
  reported_at: string | null;
  affected_individual_count: number | null;
  data_categories_affected: string[] | null;
  status: BreachStatus | null;
  notification_required: boolean;
  dpa_notified: boolean;
  dpa_notification_date: string | null;
  individuals_notified: boolean;
  individuals_notification_date: string | null;
  containment_measures: string | null;
  root_cause: string | null;
  remediation_steps: string | null;
  ai_notification_draft: { subject: string; body: string } | null;
  created_at: string | null;
  updated_at: string | null;
  // computed by API
  deadline_hours: number;
  deadline_at: string;
  hours_remaining: number;
  deadline_passed: boolean;
}

export interface BreachListResponse {
  total: number;
  breaches: BreachIncident[];
}

export interface BreachCreateRequest {
  title: string;
  description?: string;
  breach_type?: BreachType;
  severity?: BreachSeverity;
  regulation?: BreachRegulation;
  discovered_at: string;
  occurred_at?: string;
  affected_individual_count?: number;
  data_categories_affected?: string[];
  notification_required?: boolean;
  containment_measures?: string;
  root_cause?: string;
  remediation_steps?: string;
}

export type BreachUpdateRequest = Partial<
  Omit<BreachIncident, "breach_id" | "created_at" | "updated_at" | "deadline_hours" | "deadline_at" | "hours_remaining" | "deadline_passed" | "ai_notification_draft">
>;

// ── Helpers ───────────────────────────────────────────────────────────────────

async function request<T>(path: string, token: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${POLICY_BASE}${path}`, {
    ...init,
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ── API functions ─────────────────────────────────────────────────────────────

export const listBreaches = (token: string): Promise<BreachListResponse> =>
  request("/api/v1/breach", token);

export const createBreach = (token: string, body: BreachCreateRequest): Promise<BreachIncident> =>
  request("/api/v1/breach", token, { method: "POST", body: JSON.stringify(body) });

export const getBreach = (token: string, breachId: string): Promise<BreachIncident> =>
  request(`/api/v1/breach/${breachId}`, token);

export const updateBreach = (
  token: string,
  breachId: string,
  body: BreachUpdateRequest,
): Promise<BreachIncident> =>
  request(`/api/v1/breach/${breachId}`, token, { method: "PATCH", body: JSON.stringify(body) });

export const deleteBreach = (token: string, breachId: string): Promise<void> =>
  fetch(`${POLICY_BASE}/api/v1/breach/${breachId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  }).then(() => undefined);

export const draftNotification = (
  token: string,
  breachId: string,
): Promise<{ breach_id: string; draft: { subject: string; body: string } }> =>
  request(`/api/v1/breach/${breachId}/draft-notification`, token, { method: "POST" });
