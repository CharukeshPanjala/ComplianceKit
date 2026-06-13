// WHAT: ROPA API client | CHANGE: new file | WHY: COM-173 — typed fetch calls to policy-engine /api/v1/ropa
const POLICY_BASE = process.env.NEXT_PUBLIC_POLICY_URL ?? "http://localhost:8001";

// ── Types ─────────────────────────────────────────────────────────────────────

export type RopaStatus = "draft" | "active" | "archived";
export type RopaSource = "manual" | "auto_generated";
export type RopaLegalBasis =
  | "consent" | "contract" | "legal_obligation"
  | "vital_interests" | "public_task" | "legitimate_interests";
export type TransferMechanism = "scc" | "bcr" | "adequacy_decision" | "derogation" | "none";

export interface RopaEntry {
  ropa_id: string;
  activity_name: string;
  purpose: string;
  category: string | null;
  data_role: string | null;
  legal_basis: RopaLegalBasis | null;
  legal_obligation_reference: string | null;
  legitimate_interest_description: string | null;
  data_categories: string[] | null;
  data_subject_categories: string[] | null;
  has_special_category_data: boolean;
  special_category_types: string[] | null;
  special_category_condition: string | null;
  has_automated_decision_making: boolean;
  automated_decision_description: string | null;
  processing_locations: string[] | null;
  third_party_transfers: Record<string, unknown> | null;
  transfer_mechanism: TransferMechanism | null;
  processors: Record<string, unknown> | null;
  retention_period: string | null;
  security_measures: string | null;
  requires_dpia: boolean;
  dpia_completed: boolean | null;
  status: RopaStatus;
  source: RopaSource;
  last_reviewed_at: string | null;
  next_review_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface RopaListResponse {
  total: number;
  entries: RopaEntry[];
}

export interface GenerateRopaResponse {
  generated: number;
  entries: RopaEntry[];
}

export type RopaUpdateRequest = Partial<Omit<RopaEntry, "ropa_id" | "source" | "created_at" | "updated_at">>;

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

export const listRopa = (token: string): Promise<RopaListResponse> =>
  request("/api/v1/ropa", token);

export const generateRopa = (token: string): Promise<GenerateRopaResponse> =>
  request("/api/v1/ropa/generate", token, { method: "POST" });

export const getRopa = (token: string, ropaId: string): Promise<RopaEntry> =>
  request(`/api/v1/ropa/${ropaId}`, token);

export const createRopa = (token: string, body: Partial<RopaEntry>): Promise<RopaEntry> =>
  request("/api/v1/ropa", token, { method: "POST", body: JSON.stringify(body) });

export const updateRopa = (token: string, ropaId: string, body: RopaUpdateRequest): Promise<RopaEntry> =>
  request(`/api/v1/ropa/${ropaId}`, token, { method: "PATCH", body: JSON.stringify(body) });

export const updateRopaStatus = (token: string, ropaId: string, status: RopaStatus): Promise<{ ropa_id: string; status: RopaStatus }> =>
  request(`/api/v1/ropa/${ropaId}/status`, token, { method: "PATCH", body: JSON.stringify({ status }) });

export const deleteRopa = (token: string, ropaId: string): Promise<void> =>
  fetch(`${POLICY_BASE}/api/v1/ropa/${ropaId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  }).then(() => undefined);

export const exportRopaPdf = async (token: string): Promise<void> => {
  const res = await fetch(`${POLICY_BASE}/api/v1/ropa/export/pdf`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("PDF export failed");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "ropa-register.pdf";
  a.click();
  URL.revokeObjectURL(url);
};
