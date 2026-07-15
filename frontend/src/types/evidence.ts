export type DocumentType =
  | "privacy_notice"
  | "security_policy"
  | "breach_response_plan"
  | "dpia_template";

export type EvaluationStatus = "pending" | "evaluating" | "completed" | "failed";
export type ClauseStatus = "met" | "partial" | "not_met";
export type OverallStatus = "compliant" | "partial" | "non_compliant";

export interface ClauseResult {
  article: number;
  clause_id: string;
  label: string;
  status: ClauseStatus;
  note: string;
}

export interface EvaluationResults {
  overall_status: OverallStatus;
  clauses: ClauseResult[];
}

export interface EvidenceDocument {
  evidence_id: string;
  document_type: DocumentType;
  file_name: string;
  status: EvaluationStatus;
  evaluation_results: EvaluationResults | null;
  articles_covered: number[] | null;
  evaluated_at: string | null;
  created_at: string;
}

export const DOCUMENT_TYPE_META: Record<
  DocumentType,
  { label: string; articles: number[]; description: string }
> = {
  privacy_notice: {
    label: "Privacy Notice",
    articles: [12, 13, 14],
    description: "Transparency obligations and information provided to data subjects",
  },
  security_policy: {
    label: "Security Policy",
    articles: [32],
    description: "Technical and organisational measures to ensure security of processing",
  },
  breach_response_plan: {
    label: "Breach Response Plan",
    articles: [33, 34],
    description: "Procedures for notifying supervisory authorities and affected individuals",
  },
  dpia_template: {
    label: "DPIA Template",
    articles: [35, 36],
    description: "Data Protection Impact Assessment for high-risk processing activities",
  },
};
