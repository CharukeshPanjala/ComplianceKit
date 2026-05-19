export type Industry =
  | "technology"
  | "healthcare"
  | "finance"
  | "legal"
  | "retail"
  | "education"
  | "manufacturing"
  | "other";

export type CompanySize = "1-10" | "11-50" | "51-200" | "201-1000" | "1000+";

export type B2BOrB2C = "b2b" | "b2c" | "both";

export type NumberOfDataSubjects = "under_1k" | "under_10k" | "under_100k" | "over_100k";

export type DataRole = "controller" | "processor" | "both";

export interface Profile {
  profile_id: string;
  tenant_id: string;
  tenant_name: string | null;
  industry: Industry | null;
  company_size: CompanySize | null;
  b2b_or_b2c: B2BOrB2C | null;
  data_role: DataRole | null;
  number_of_data_subjects: NumberOfDataSubjects | null;
  website_url: string | null;
  primary_jurisdiction: string | null;
  uses_cloud_services: boolean | null;
  cloud_providers: string[] | null;
  primary_cloud_region: string | null;
  has_on_premise_servers: boolean | null;
  certifications: string[] | null;
  has_compliance_officer: boolean | null;
  dpo_name: string | null;
  dpo_email: string | null;
  legal_contact_email: string | null;
  previous_regulatory_action: boolean | null;
  data_categories_processed: string[] | null;
  processing_purposes: string[] | null;
  data_subject_categories: string[] | null;
  tech_stack: string[] | null;
  gdpr_data: Record<string, unknown> | null;
  nis2_data: Record<string, unknown> | null;
  ai_act_data: Record<string, unknown> | null;
  is_complete: boolean;
}
