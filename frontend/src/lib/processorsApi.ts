const POLICY_BASE = process.env.NEXT_PUBLIC_POLICY_URL ?? "http://localhost:8001";

// ── Types ─────────────────────────────────────────────────────────────────────

export type ProcessorStatus = "active" | "inactive" | "under_review";
export type ProcessorRisk = "low" | "medium" | "high";
export type ProcessorSource = "manual" | "auto_generated";
export type ProcessorTransferMechanism = "scc" | "bcr" | "adequacy_decision" | "derogation" | "none";

export interface Processor {
  processor_id: string;
  name: string;
  category: string | null;
  service_description: string | null;
  website: string | null;
  data_categories: string[] | null;
  data_subject_categories: string[] | null;
  processing_locations: string[] | null;
  transfer_mechanism: ProcessorTransferMechanism | null;
  dpa_signed: boolean;
  dpa_date: string | null;
  contract_review_date: string | null;
  risk_level: ProcessorRisk | null;
  status: ProcessorStatus | null;
  source: ProcessorSource | null;
  sub_processors: Record<string, unknown> | null;
  notes: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface ProcessorListResponse {
  total: number;
  processors: Processor[];
}

export interface GenerateProcessorsResponse {
  generated: number;
  processors: Processor[];
}

export interface ProcessorUpdateRequest {
  dpa_signed?: boolean;
  dpa_date?: string | null;
  contract_review_date?: string | null;
  status?: ProcessorStatus;
  risk_level?: ProcessorRisk;
  transfer_mechanism?: ProcessorTransferMechanism;
  processing_locations?: string[];
  data_categories?: string[];
  notes?: string | null;
  service_description?: string | null;
  website?: string | null;
}

export interface ProcessorListFilters {
  status?: ProcessorStatus;
  category?: string;
  risk_level?: ProcessorRisk;
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

export const generateProcessors = (token: string): Promise<GenerateProcessorsResponse> =>
  request("/api/v1/processors/generate", token, { method: "POST" });

export const listProcessors = (token: string, filters?: ProcessorListFilters): Promise<ProcessorListResponse> => {
  const params = new URLSearchParams();
  if (filters?.status) params.set("status", filters.status);
  if (filters?.category) params.set("category", filters.category);
  if (filters?.risk_level) params.set("risk_level", filters.risk_level);
  const qs = params.toString();
  return request(`/api/v1/processors${qs ? `?${qs}` : ""}`, token);
};

export const updateProcessor = (
  token: string,
  processorId: string,
  body: ProcessorUpdateRequest,
): Promise<Processor> =>
  request(`/api/v1/processors/${processorId}`, token, { method: "PATCH", body: JSON.stringify(body) });

export const deleteProcessor = (token: string, processorId: string): Promise<void> =>
  fetch(`${POLICY_BASE}/api/v1/processors/${processorId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  }).then(() => undefined);
