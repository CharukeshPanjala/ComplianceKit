import type { Profile } from "@/types/profile";

// Returns the step number of the first incomplete step, or null if all complete
export const getFirstIncompleteStep = (profile: Profile | null): number | null => {
  if (!profile) return 1;

  // ── Step 1 ────────────────────────────────────────────────
  if (!profile.tenant_name || !profile.industry || !profile.company_size || !profile.b2b_or_b2c)
    return 1;

  // ── Step 2 ────────────────────────────────────────────────
  if (
    !profile.primary_jurisdiction ||
    !profile.data_role ||
    !profile.number_of_data_subjects ||
    !profile.data_categories_processed?.length ||
    !profile.data_subject_categories?.length ||
    !profile.processing_purposes?.length
  )
    return 2;

  // ── Step 3 — no required fields ───────────────────────────

  // ── Step 4 ────────────────────────────────────────────────
  if (profile.uses_cloud_services == null || profile.has_on_premise_servers == null) return 4;

  if (
    profile.uses_cloud_services === true &&
    (!profile.cloud_providers?.length || !profile.primary_cloud_region)
  )
    return 4;

  // ── Step 5 ────────────────────────────────────────────────
  if (profile.has_compliance_officer == null || profile.previous_regulatory_action == null)
    return 5;

  // ── Step 6 ────────────────────────────────────────────────
  const gdpr = profile.gdpr_data ?? {};
  if (
    !Array.isArray(gdpr.lawful_bases) ||
    (gdpr.lawful_bases as string[]).length === 0 ||
    gdpr.processes_children_data == null ||
    gdpr.transfers_outside_eea == null ||
    gdpr.uses_data_processors == null ||
    gdpr.has_breach_procedure == null ||
    gdpr.has_dpia == null
  )
    return 6;

  const ai = profile.ai_act_data ?? {};
  if (ai.uses_ai == null) return 6;

  return null;
};
