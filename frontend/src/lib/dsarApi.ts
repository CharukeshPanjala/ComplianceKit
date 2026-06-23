const POLICY_BASE = process.env.NEXT_PUBLIC_POLICY_URL ?? "http://localhost:8001";

// ── Types ─────────────────────────────────────────────────────────────────────

export type DsarRequestType =
  | "access" | "rectification" | "erasure" | "portability"
  | "restriction" | "objection" | "withdraw_consent";

export type DsarStatus =
  | "pending" | "in_progress" | "awaiting_info"
  | "completed" | "rejected" | "withdrawn";

export interface DsarRequest {
  dsar_id: string;
  request_type: DsarRequestType | null;
  request_type_label: string;
  description: string | null;
  requester_email: string;
  requester_name: string | null;
  identity_verified: boolean;
  identity_verification_method: string | null;
  status: DsarStatus | null;
  assigned_to: string | null;
  rejection_reason: string | null;
  internal_notes: string | null;
  received_at: string | null;
  due_date: string | null;
  completed_at: string | null;
  created_at: string | null;
  updated_at: string | null;
  // computed by API
  days_remaining: number;
  is_overdue: boolean;
}

export interface DsarListResponse {
  total: number;
  dsars: DsarRequest[];
}

export interface DsarCreateRequest {
  request_type: DsarRequestType;
  requester_email: string;
  requester_name?: string;
  description?: string;
  received_at?: string;
}

export interface DsarUpdateRequest {
  status?: DsarStatus;
  identity_verified?: boolean;
  identity_verification_method?: string;
  assigned_to?: string;
  rejection_reason?: string;
  internal_notes?: string;
}

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

export const listDsars = (token: string): Promise<DsarListResponse> =>
  request("/api/v1/dsar", token);

export const createDsar = (token: string, body: DsarCreateRequest): Promise<DsarRequest> =>
  request("/api/v1/dsar", token, { method: "POST", body: JSON.stringify(body) });

export const getDsar = (token: string, dsarId: string): Promise<DsarRequest> =>
  request(`/api/v1/dsar/${dsarId}`, token);

export const updateDsar = (
  token: string,
  dsarId: string,
  body: DsarUpdateRequest,
): Promise<DsarRequest> =>
  request(`/api/v1/dsar/${dsarId}`, token, { method: "PATCH", body: JSON.stringify(body) });

export const deleteDsar = (token: string, dsarId: string): Promise<void> =>
  fetch(`${POLICY_BASE}/api/v1/dsar/${dsarId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  }).then(() => undefined);
