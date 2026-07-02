import type {
  Assessment,
  LatestAssessment,
  GapsResponse,
  AssessmentHistoryItem,
  AssessmentStats,
  TriggerAssessmentResponse,
  UpdateGapRequest,
  RegulationName,
} from "@/types/assessment";

const POLICY_BASE = process.env.NEXT_PUBLIC_POLICY_URL ?? "http://localhost:8001";

// ── Custom error types ────────────────────────────────────────────────────────

export class AssessmentApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message);
    this.name = "AssessmentApiError";
  }
}

export class NetworkError extends AssessmentApiError {
  constructor() {
    super("Unable to connect to compliance engine. Please try again.", undefined, "network_error");
  }
}

// ── Helper ────────────────────────────────────────────────────────────────────

async function policyFetch(
  path: string,
  token: string,
  options: RequestInit = {}
): Promise<Response> {
  try {
    const res = await fetch(`${POLICY_BASE}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...(options.headers ?? {}),
      },
    });
    return res;
  } catch {
    throw new NetworkError();
  }
}

async function parseJson<T>(res: Response): Promise<T> {
  try {
    return await res.json();
  } catch {
    throw new AssessmentApiError("Invalid response from server", res.status, "parse_error");
  }
}

// ── Trigger assessment ────────────────────────────────────────────────────────

export async function triggerAssessment(
  token: string,
  regulation: RegulationName
): Promise<TriggerAssessmentResponse> {
  const res = await policyFetch("/api/v1/assessments", token, {
    method: "POST",
    body: JSON.stringify({ regulation_name: regulation }),
  });

  const data = await parseJson<TriggerAssessmentResponse>(res);

  if (!res.ok) {
    throw new AssessmentApiError(
      `Failed to trigger ${regulation} assessment`,
      res.status,
      "trigger_failed"
    );
  }

  return data;
}

// ── Poll assessment status ────────────────────────────────────────────────────

export async function getAssessment(
  token: string,
  assessmentId: string
): Promise<Assessment | null> {
  const res = await policyFetch(`/api/v1/assessments/${assessmentId}`, token);
  if (res.status === 404) return null;
  if (!res.ok) throw new AssessmentApiError("Failed to fetch assessment", res.status);
  return parseJson<Assessment>(res);
}

// ── Latest assessments ────────────────────────────────────────────────────────

export async function getLatestAssessments(token: string): Promise<LatestAssessment[]> {
  const res = await policyFetch("/api/v1/assessments/latest", token);
  if (!res.ok) return [];
  const data = await parseJson<{ assessments: LatestAssessment[] }>(res);
  return data.assessments ?? [];
}

// ── Gaps ──────────────────────────────────────────────────────────────────────

export async function getGaps(
  token: string,
  assessmentId: string,
  params?: {
    status?: string;
    severity?: string;
    category?: string;
    remediation_priority?: string;
    resolved?: boolean;
    limit?: number;
    offset?: number;
  }
): Promise<GapsResponse> {
  const query = new URLSearchParams();
  if (params?.status) query.set("status", params.status);
  if (params?.severity) query.set("severity", params.severity);
  if (params?.category) query.set("category", params.category);
  if (params?.remediation_priority) query.set("remediation_priority", params.remediation_priority);
  if (params?.resolved !== undefined) query.set("resolved", String(params.resolved));
  if (params?.limit !== undefined) query.set("limit", String(params.limit));
  if (params?.offset !== undefined) query.set("offset", String(params.offset));

  const qs = query.toString();
  const res = await policyFetch(
    `/api/v1/assessments/${assessmentId}/gaps${qs ? `?${qs}` : ""}`,
    token
  );

  if (res.status === 404) return { assessment_id: assessmentId, total: 0, gaps: [] };
  if (!res.ok) throw new AssessmentApiError("Failed to fetch gaps", res.status);
  return parseJson<GapsResponse>(res);
}

// ── Update gap ────────────────────────────────────────────────────────────────

export async function updateGap(
  token: string,
  assessmentId: string,
  gapId: string,
  body: UpdateGapRequest
): Promise<boolean> {
  const res = await policyFetch(`/api/v1/assessments/${assessmentId}/gaps/${gapId}`, token, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
  if (res.status === 404) return false;
  if (!res.ok) throw new AssessmentApiError("Failed to update gap", res.status);
  return true;
}

// ── Score history ─────────────────────────────────────────────────────────────

export async function getAssessmentHistory(
  token: string,
  regulation?: RegulationName,
  limit = 10
): Promise<AssessmentHistoryItem[]> {
  const query = new URLSearchParams();
  if (regulation) query.set("regulation", regulation);
  query.set("limit", String(limit));

  const res = await policyFetch(`/api/v1/assessments/history?${query.toString()}`, token);

  if (!res.ok) return [];
  const data = await parseJson<{ history: AssessmentHistoryItem[] }>(res);
  return data.history ?? [];
}

// ── Stats ─────────────────────────────────────────────────────────────────────

export async function getAssessmentStats(
  token: string,
  assessmentId: string
): Promise<AssessmentStats | null> {
  const res = await policyFetch(`/api/v1/assessments/${assessmentId}/stats`, token);
  if (res.status === 404) return null;
  if (!res.ok) return null;
  return parseJson<AssessmentStats>(res);
}

// ── Trigger all applicable regulations ───────────────────────────────────────

export async function triggerAllApplicableAssessments(
  token: string,
  profile: {
    nis2_data: Record<string, unknown> | null;
    ai_act_data: Record<string, unknown> | null;
  }
): Promise<TriggerAssessmentResponse[]> {
  const regulations: RegulationName[] = ["GDPR"];

  const nis2Sectors = (profile.nis2_data?.sectors as string[] | undefined) ?? [];
  const nis2Applicable = nis2Sectors.length > 0 && nis2Sectors[0] !== "not_applicable";
  if (nis2Applicable) regulations.push("NIS2");

  if (profile.ai_act_data?.uses_ai === true) regulations.push("EU_AI_ACT");

  const results = await Promise.allSettled(regulations.map((reg) => triggerAssessment(token, reg)));

  return results
    .filter((r): r is PromiseFulfilledResult<TriggerAssessmentResponse> => r.status === "fulfilled")
    .map((r) => r.value);
}
