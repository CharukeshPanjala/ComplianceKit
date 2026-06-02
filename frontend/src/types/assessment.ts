// ── Assessment types ──────────────────────────────────────────────────────────

export type AssessmentStatus = "pending" | "running" | "completed" | "failed" | "never_run";
export type RiskLevel = "low" | "medium" | "high" | "critical";
export type GapStatus = "met" | "partial" | "not_met" | "unknown" | "not_applicable";
export type RemediationPriority = "critical" | "high" | "medium" | "low";
export type RegulationName = "GDPR" | "NIS2" | "EU_AI_ACT";

export interface Assessment {
  assessment_id: string;
  status: AssessmentStatus;
  score: number | null;
  risk_level: RiskLevel | null;
  total_rules: number;
  applicable_rules: number;
  met_rules: number;
  partial_rules: number;
  not_met_rules: number;
  unknown_rules: number;
  triggered_by: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface LatestAssessment {
  regulation: RegulationName;
  assessment_id: string | null;
  score: number | null;
  risk_level: RiskLevel | null;
  met_rules: number | null;
  not_met_rules: number | null;
  unknown_rules: number | null;
  completed_at: string | null;
  status: AssessmentStatus | "never_run";
}

export interface Gap {
  gap_id: string;
  article: string;
  article_number: number;
  title: string | null;
  plain_english: string | null;
  chapter: string | null;
  category: string | null;
  severity: "critical" | "high" | "medium" | "low" | null;
  fine_tier: "tier_1" | "tier_2" | null;
  status: GapStatus;
  score: number | null;
  remediation_priority: RemediationPriority | null;
  remediation_hint: string | null;
  remediation_steps: { steps: string[] } | null;
  evidence: Record<string, unknown> | null;
  assigned_to: string | null;
  due_date: string | null;
  resolved: boolean;
  resolved_at: string | null;
  notes: string | null;
}

export interface GapsResponse {
  assessment_id: string;
  total: number;
  gaps: Gap[];
}

export interface AssessmentHistoryItem {
  assessment_id: string;
  regulation_id: string;
  score: number;
  risk_level: RiskLevel;
  met_rules: number;
  not_met_rules: number;
  unknown_rules: number;
  completed_at: string;
}

export interface AssessmentStats {
  assessment_id: string;
  by_severity: Record<string, Record<string, number>>;
  by_category: { category: string; gaps: number }[];
  quick_wins: {
    gap_id: string;
    article: string;
    category: string;
    severity: string;
    remediation_hint: string | null;
  }[];
}

export interface TriggerAssessmentResponse {
  assessment_id: string;
  status: AssessmentStatus;
  regulation: RegulationName;
  message: string;
}

export interface UpdateGapRequest {
  resolved?: boolean;
  notes?: string;
  assigned_to?: string;
  due_date?: string;
}
