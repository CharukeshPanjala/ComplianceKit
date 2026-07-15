// WHAT: Policies API client | CHANGE: new file | WHY: COM-176 — typed fetch calls to policy-engine /api/v1/policies

const POLICY_BASE = process.env.NEXT_PUBLIC_POLICY_URL ?? "http://localhost:8001";

// ── Types ─────────────────────────────────────────────────────────────────────

export type PolicyType =
  | "privacy_notice" | "ropa" | "dpa" | "cookie_policy"
  | "data_retention" | "incident_response" | "ai_governance" | "other";

export type PolicyStatus = "draft" | "active" | "under_review" | "archived";
export type PolicyContentFormat = "markdown" | "plain_text";
export type PolicyChangeType = "created" | "edited" | "ai_enhanced" | "approved" | "archived";

export interface Policy {
  policy_id: string;
  title: string;
  type: PolicyType | null;
  status: PolicyStatus | null;
  language: string;
  content_format: PolicyContentFormat | null;
  current_version: number;
  content: string | null;
  tags: string[] | null;
  is_ai_enhanced: boolean;
  related_article: string | null;
  next_review_date: string | null;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PolicyVersionSummary {
  version_id: string;
  version_number: number;
  is_ai_enhanced: boolean;
  change_type: PolicyChangeType | null;
  created_at: string;
}

export interface PolicyDetail extends Policy {
  versions: PolicyVersionSummary[];
}

export interface PolicyListResponse {
  total: number;
  policies: Policy[];
}

export interface PolicyGenerateRequest {
  policy_type: PolicyType;
  gap_ids: string[];
}

// ── Display labels ────────────────────────────────────────────────────────────

export const POLICY_TYPE_LABELS: Record<PolicyType, string> = {
  privacy_notice: "Privacy Notice",
  ropa: "Records of Processing Activities",
  dpa: "Data Processing Agreement",
  cookie_policy: "Cookie Policy",
  data_retention: "Data Retention Policy",
  incident_response: "Incident Response Policy",
  ai_governance: "AI Governance Policy",
  other: "Compliance Policy",
};

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

async function downloadFile(path: string, token: string, filename: string): Promise<void> {
  const res = await fetch(`${POLICY_BASE}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Download failed");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ── API functions ─────────────────────────────────────────────────────────────

export const listPolicies = (token: string): Promise<PolicyListResponse> =>
  request("/api/v1/policies", token);

export const getPolicy = (token: string, policyId: string): Promise<PolicyDetail> =>
  request(`/api/v1/policies/${policyId}`, token);

export const generatePolicy = (token: string, body: PolicyGenerateRequest): Promise<Policy> =>
  request("/api/v1/policies/generate", token, { method: "POST", body: JSON.stringify(body) });

export const updatePolicyStatus = (token: string, policyId: string, status: PolicyStatus): Promise<Policy> =>
  request(`/api/v1/policies/${policyId}/status`, token, { method: "PATCH", body: JSON.stringify({ status }) });

export const updatePolicyContent = (token: string, policyId: string, content: string): Promise<Policy> =>
  request(`/api/v1/policies/${policyId}/content`, token, { method: "PATCH", body: JSON.stringify({ content }) });

export const exportPolicyPdf = (token: string, policyId: string, policyType: PolicyType): Promise<void> =>
  downloadFile(`/api/v1/policies/${policyId}/export/pdf`, token, `${policyType}.pdf`);

export const exportPolicyDocx = (token: string, policyId: string, policyType: PolicyType): Promise<void> =>
  downloadFile(`/api/v1/policies/${policyId}/export/docx`, token, `${policyType}.docx`);
