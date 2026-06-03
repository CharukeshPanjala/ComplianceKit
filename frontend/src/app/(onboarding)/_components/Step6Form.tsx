"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/ui/FormField";
import { CheckboxCard } from "@/components/ui/CheckboxCard";
import { Tooltip } from "@/components/ui/Tooltip";
import { clientApiFetch } from "@/lib/clientApi";
import { getFirstIncompleteStep } from "@/lib/validateOnboarding";
import type { Profile } from "@/types/profile";

// ── Schema ────────────────────────────────────────────────

const schema = z.object({
  // GDPR
  lawful_bases: z.array(z.string()).min(1, "Select at least one lawful basis"),
  processes_children_data: z.boolean({ error: "Please answer this question" }),
  transfers_outside_eea: z.boolean({ error: "Please answer this question" }),
  transfer_mechanisms: z.array(z.string()).optional(),
  uses_data_processors: z.boolean({ error: "Please answer this question" }),
  has_breach_procedure: z.boolean({ error: "Please answer this question" }),
  has_dpia: z.boolean({ error: "Please answer this question" }),
  // NIS2
  nis2_sectors: z.array(z.string()).optional(),
  nis2_entity_type: z.string().optional(),
  has_mfa: z.boolean().optional(),
  has_incident_response_plan: z.boolean().optional(),
  has_business_continuity_plan: z.boolean().optional(),
  assesses_supply_chain: z.boolean().optional(),
  // EU AI Act
  uses_ai: z.boolean({ error: "Please answer this question" }),
  ai_role: z.string().optional(),
  high_risk_ai_categories: z.array(z.string()).optional(),
  uses_gpai: z.boolean().optional(),
  has_ai_governance_policy: z.boolean().optional(),
});

type FormData = z.infer<typeof schema>;

// ── Constants ─────────────────────────────────────────────

const LAWFUL_BASIS_OPTIONS = [
  { value: "consent", label: "Consent — Art. 6(1)(a)" },
  { value: "contract", label: "Contract — Art. 6(1)(b)" },
  { value: "legal_obligation", label: "Legal obligation — Art. 6(1)(c)" },
  { value: "vital_interests", label: "Vital interests — Art. 6(1)(d)" },
  { value: "public_task", label: "Public task — Art. 6(1)(e)" },
  { value: "legitimate_interest", label: "Legitimate interest — Art. 6(1)(f)" },
];

const TRANSFER_MECHANISM_OPTIONS = [
  { value: "adequacy_decision", label: "Adequacy decision" },
  { value: "sccs", label: "Standard Contractual Clauses (SCCs)" },
  { value: "bcrs", label: "Binding Corporate Rules (BCRs)" },
  { value: "derogations", label: "Specific derogations (Art. 49)" },
];

const NIS2_SECTOR_OPTIONS = [
  { value: "energy", label: "Energy" },
  { value: "transport", label: "Transport" },
  { value: "banking", label: "Banking" },
  { value: "financial_markets", label: "Financial markets" },
  { value: "health", label: "Health" },
  { value: "water", label: "Drinking water / Waste water" },
  { value: "digital_infrastructure", label: "Digital infrastructure" },
  { value: "managed_services", label: "Managed IT/security services" },
  { value: "public_administration", label: "Public administration" },
  { value: "space", label: "Space" },
  { value: "not_applicable", label: "Not applicable" },
];

const NIS2_ENTITY_OPTIONS = [
  { value: "essential", label: "Essential entity" },
  { value: "important", label: "Important entity" },
  { value: "unsure", label: "Unsure" },
  { value: "not_applicable", label: "Not applicable" },
];

const HIGH_RISK_AI_OPTIONS = [
  { value: "biometrics", label: "Biometrics & facial recognition" },
  { value: "critical_infrastructure", label: "Critical infrastructure management" },
  { value: "education", label: "Education & vocational training" },
  { value: "employment", label: "Employment & HR management" },
  { value: "essential_services", label: "Credit, insurance & essential services" },
  { value: "law_enforcement", label: "Law enforcement" },
  { value: "migration", label: "Migration & border control" },
  { value: "justice", label: "Administration of justice" },
  { value: "none", label: "None of the above" },
];

const AI_ROLE_OPTIONS = [
  { value: "provider", label: "Provider (we build AI systems)" },
  { value: "deployer", label: "Deployer (we use AI in our products/services)" },
  { value: "importer", label: "Importer (we import AI systems)" },
  { value: "distributor", label: "Distributor (we distribute AI systems)" },
  { value: "multiple", label: "Multiple roles" },
];

// ── Styles ────────────────────────────────────────────────

const styles = {
  section: "space-y-6",
  sectionTitle: "text-base font-semibold text-navy border-b border-gray-100 pb-2 mb-4",
  yesNoGroup: "flex gap-3",
  yesNoBtn: {
    base: "flex-1 py-3 border rounded-lg text-sm text-center transition-colors",
    active: "border-navy bg-navy/10 text-navy font-medium",
    inactive: "border-gray-300 text-gray-600 hover:border-navy hover:bg-gray-50",
  },
  grid: "grid grid-cols-1 sm:grid-cols-2 gap-2",
  labelRow: "flex items-center gap-1.5 mb-2",
  nav: "flex justify-between mt-8",
  divider: "border-t border-gray-100 my-6",
};

// ── Props ─────────────────────────────────────────────────

interface Props {
  initialData: Profile | null;
}

// ── Component ─────────────────────────────────────────────

export default function Step6Form({ initialData }: Props) {
  const { getToken } = useAuth();
  const router = useRouter();

  const [serverError, setServerError] = useState<string | null>(null);

  const gdpr = (initialData?.gdpr_data ?? {}) as Record<string, unknown>;
  const nis2 = (initialData?.nis2_data ?? {}) as Record<string, unknown>;
  const ai = (initialData?.ai_act_data ?? {}) as Record<string, unknown>;

  // ── Form ─────────────────────────────────────────────────

  const {
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      lawful_bases: (gdpr.lawful_bases as string[]) ?? [],
      processes_children_data: (gdpr.processes_children_data as boolean) ?? undefined,
      transfers_outside_eea: (gdpr.transfers_outside_eea as boolean) ?? undefined,
      transfer_mechanisms: (gdpr.transfer_mechanisms as string[]) ?? [],
      uses_data_processors: (gdpr.uses_data_processors as boolean) ?? undefined,
      has_breach_procedure: (gdpr.has_breach_procedure as boolean) ?? undefined,
      has_dpia: (gdpr.has_dpia as boolean) ?? undefined,
      nis2_sectors: (nis2.sectors as string[]) ?? [],
      nis2_entity_type: (nis2.entity_type as string) ?? "",
      has_mfa: (nis2.has_mfa as boolean) ?? undefined,
      has_incident_response_plan: (nis2.has_incident_response_plan as boolean) ?? undefined,
      has_business_continuity_plan: (nis2.has_business_continuity_plan as boolean) ?? undefined,
      assesses_supply_chain: (nis2.assesses_supply_chain as boolean) ?? undefined,
      uses_ai: (ai.uses_ai as boolean) ?? undefined,
      ai_role: (ai.ai_role as string) ?? "",
      high_risk_ai_categories: (ai.high_risk_ai_categories as string[]) ?? [],
      uses_gpai: (ai.uses_gpai as boolean) ?? undefined,
      has_ai_governance_policy: (ai.has_ai_governance_policy as boolean) ?? undefined,
    },
  });

  const lawfulBases = watch("lawful_bases") ?? [];
  const transfersOutsideEea = watch("transfers_outside_eea");
  const transferMechanisms = watch("transfer_mechanisms") ?? [];
  const nis2Sectors = watch("nis2_sectors") ?? [];
  const nis2EntityType = watch("nis2_entity_type");
  const usesAi = watch("uses_ai");
  const highRiskCategories = watch("high_risk_ai_categories") ?? [];
  const aiRole = watch("ai_role");

  const nis2InScope = nis2Sectors.length > 0 && !nis2Sectors.includes("not_applicable");

  // ── Handlers ──────────────────────────────────────────────

  const toggleLawfulBasis = (value: string) => {
    const updated = lawfulBases.includes(value)
      ? lawfulBases.filter((v) => v !== value)
      : [...lawfulBases, value];
    setValue("lawful_bases", updated, { shouldValidate: true });
  };

  const toggleTransferMechanism = (value: string) => {
    const updated = transferMechanisms.includes(value)
      ? transferMechanisms.filter((v) => v !== value)
      : [...transferMechanisms, value];
    setValue("transfer_mechanisms", updated);
  };

  const toggleNis2Sector = (value: string) => {
    if (value === "not_applicable") {
      setValue("nis2_sectors", nis2Sectors.includes("not_applicable") ? [] : ["not_applicable"]);
      return;
    }
    const without = nis2Sectors.filter((v) => v !== "not_applicable");
    const updated = without.includes(value)
      ? without.filter((v) => v !== value)
      : [...without, value];
    setValue("nis2_sectors", updated);
  };

  const toggleHighRiskCategory = (value: string) => {
    if (value === "none") {
      setValue("high_risk_ai_categories", highRiskCategories.includes("none") ? [] : ["none"]);
      return;
    }
    const without = highRiskCategories.filter((v) => v !== "none");
    const updated = without.includes(value)
      ? without.filter((v) => v !== value)
      : [...without, value];
    setValue("high_risk_ai_categories", updated);
  };

  // ── Render helpers ────────────────────────────────────────

  const renderYesNo = (value: boolean | undefined, onYes: () => void, onNo: () => void) => (
    <div className={styles.yesNoGroup}>
      <button
        type="button"
        onClick={onYes}
        className={`${styles.yesNoBtn.base} ${value === true ? styles.yesNoBtn.active : styles.yesNoBtn.inactive}`}
      >
        Yes
      </button>
      <button
        type="button"
        onClick={onNo}
        className={`${styles.yesNoBtn.base} ${value === false ? styles.yesNoBtn.active : styles.yesNoBtn.inactive}`}
      >
        No
      </button>
    </div>
  );

  const renderGdprSection = () => (
    <div className={styles.section}>
      <p className={styles.sectionTitle}>GDPR — Lawful basis & obligations</p>

      <FormField
        label="What is your lawful basis for processing personal data?"
        required
        error={errors.lawful_bases?.message}
      >
        <div className={styles.labelRow}>
          <Tooltip text="Under GDPR Art. 6, every processing activity must have at least one lawful basis. Select all that apply to your organisation." />
        </div>
        <div className={styles.grid}>
          {LAWFUL_BASIS_OPTIONS.map((opt) => (
            <CheckboxCard
              key={opt.value}
              label={opt.label}
              checked={lawfulBases.includes(opt.value)}
              onChange={() => toggleLawfulBasis(opt.value)}
            />
          ))}
        </div>
      </FormField>

      <FormField
        label="Do you process personal data of children (under 16)?"
        required
        error={errors.processes_children_data?.message}
      >
        <div className={styles.labelRow}>
          <Tooltip text="Processing children's data triggers additional consent requirements under GDPR Art. 8." />
        </div>
        {renderYesNo(
          watch("processes_children_data"),
          () => setValue("processes_children_data", true, { shouldValidate: true }),
          () => setValue("processes_children_data", false, { shouldValidate: true })
        )}
      </FormField>

      <FormField
        label="Do you transfer personal data outside the EU/EEA?"
        required
        error={errors.transfers_outside_eea?.message}
      >
        <div className={styles.labelRow}>
          <Tooltip text="Transfers outside the EU/EEA are subject to additional requirements under GDPR Chapter V (Art. 44–49)." />
        </div>
        {renderYesNo(
          transfersOutsideEea,
          () => setValue("transfers_outside_eea", true, { shouldValidate: true }),
          () => {
            setValue("transfers_outside_eea", false, { shouldValidate: true });
            setValue("transfer_mechanisms", []);
          }
        )}
      </FormField>

      {transfersOutsideEea === true && (
        <FormField label="What transfer mechanism do you rely on?" hint="select all that apply">
          <div className={styles.grid}>
            {TRANSFER_MECHANISM_OPTIONS.map((opt) => (
              <CheckboxCard
                key={opt.value}
                label={opt.label}
                checked={transferMechanisms.includes(opt.value)}
                onChange={() => toggleTransferMechanism(opt.value)}
              />
            ))}
          </div>
        </FormField>
      )}

      <FormField
        label="Do you use third-party data processors (e.g. cloud vendors, CRMs, payroll providers)?"
        required
        error={errors.uses_data_processors?.message}
      >
        <div className={styles.labelRow}>
          <Tooltip text="Using processors triggers GDPR Art. 28 — you must have a Data Processing Agreement (DPA) in place with each one." />
        </div>
        {renderYesNo(
          watch("uses_data_processors"),
          () => setValue("uses_data_processors", true, { shouldValidate: true }),
          () => setValue("uses_data_processors", false, { shouldValidate: true })
        )}
      </FormField>

      <FormField
        label="Do you have a documented data breach response procedure?"
        required
        error={errors.has_breach_procedure?.message}
      >
        <div className={styles.labelRow}>
          <Tooltip text="GDPR Art. 33 requires reporting breaches to your supervisory authority within 72 hours. A documented procedure is required." />
        </div>
        {renderYesNo(
          watch("has_breach_procedure"),
          () => setValue("has_breach_procedure", true, { shouldValidate: true }),
          () => setValue("has_breach_procedure", false, { shouldValidate: true })
        )}
      </FormField>

      <FormField
        label="Have you conducted a Data Protection Impact Assessment (DPIA)?"
        required
        error={errors.has_dpia?.message}
      >
        <div className={styles.labelRow}>
          <Tooltip text="GDPR Art. 35 requires a DPIA for high-risk processing activities — e.g. large-scale profiling, systematic monitoring, processing special category data." />
        </div>
        {renderYesNo(
          watch("has_dpia"),
          () => setValue("has_dpia", true, { shouldValidate: true }),
          () => setValue("has_dpia", false, { shouldValidate: true })
        )}
      </FormField>
    </div>
  );

  const renderNis2Section = () => (
    <div className={styles.section}>
      <p className={styles.sectionTitle}>NIS2 — Cybersecurity</p>

      <FormField
        label="Does your organisation operate in any NIS2-regulated sector?"
        hint="select all that apply"
      >
        <div className={styles.labelRow}>
          <Tooltip text="NIS2 Directive Art. 2–3 applies to organisations in critical sectors. Select 'Not applicable' if your sector is not listed." />
        </div>
        <div className={styles.grid}>
          {NIS2_SECTOR_OPTIONS.map((opt) => (
            <CheckboxCard
              key={opt.value}
              label={opt.label}
              checked={nis2Sectors.includes(opt.value)}
              onChange={() => toggleNis2Sector(opt.value)}
            />
          ))}
        </div>
      </FormField>

      {nis2InScope && (
        <>
          <FormField label="How do you classify your organisation under NIS2?">
            <div className={styles.grid}>
              {NIS2_ENTITY_OPTIONS.map((opt) => (
                <CheckboxCard
                  key={opt.value}
                  label={opt.label}
                  checked={nis2EntityType === opt.value}
                  onChange={() =>
                    setValue("nis2_entity_type", nis2EntityType === opt.value ? "" : opt.value)
                  }
                />
              ))}
            </div>
          </FormField>

          <FormField label="Do you have multi-factor authentication (MFA) on critical systems?">
            {renderYesNo(
              watch("has_mfa"),
              () => setValue("has_mfa", true),
              () => setValue("has_mfa", false)
            )}
          </FormField>

          <FormField label="Do you have a documented incident response plan?">
            {renderYesNo(
              watch("has_incident_response_plan"),
              () => setValue("has_incident_response_plan", true),
              () => setValue("has_incident_response_plan", false)
            )}
          </FormField>

          <FormField label="Do you have a business continuity plan (BCP)?">
            {renderYesNo(
              watch("has_business_continuity_plan"),
              () => setValue("has_business_continuity_plan", true),
              () => setValue("has_business_continuity_plan", false)
            )}
          </FormField>

          <FormField label="Do you assess security risks in your supply chain?">
            {renderYesNo(
              watch("assesses_supply_chain"),
              () => setValue("assesses_supply_chain", true),
              () => setValue("assesses_supply_chain", false)
            )}
          </FormField>
        </>
      )}
    </div>
  );

  const renderAiActSection = () => (
    <div className={styles.section}>
      <p className={styles.sectionTitle}>EU AI Act — Artificial Intelligence</p>

      <FormField
        label="Does your organisation develop, deploy, or use AI systems?"
        required
        error={errors.uses_ai?.message}
      >
        <div className={styles.labelRow}>
          <Tooltip text="The EU AI Act applies to providers, deployers, importers, and distributors of AI systems placed on the EU market or affecting EU residents." />
        </div>
        {renderYesNo(
          usesAi,
          () => setValue("uses_ai", true, { shouldValidate: true }),
          () => {
            setValue("uses_ai", false, { shouldValidate: true });
            setValue("ai_role", "");
            setValue("high_risk_ai_categories", []);
          }
        )}
      </FormField>

      {usesAi === true && (
        <>
          <FormField label="What is your role under the EU AI Act?">
            <div className={styles.grid}>
              {AI_ROLE_OPTIONS.map((opt) => (
                <CheckboxCard
                  key={opt.value}
                  label={opt.label}
                  checked={aiRole === opt.value}
                  onChange={() => setValue("ai_role", aiRole === opt.value ? "" : opt.value)}
                />
              ))}
            </div>
          </FormField>

          <FormField
            label="Do your AI systems fall into any high-risk categories (Annex III)?"
            hint="select all that apply"
          >
            <div className={styles.labelRow}>
              <Tooltip text="High-risk AI systems under EU AI Act Art. 6 and Annex III face stricter obligations including conformity assessments and registration." />
            </div>
            <div className={styles.grid}>
              {HIGH_RISK_AI_OPTIONS.map((opt) => (
                <CheckboxCard
                  key={opt.value}
                  label={opt.label}
                  checked={highRiskCategories.includes(opt.value)}
                  onChange={() => toggleHighRiskCategory(opt.value)}
                />
              ))}
            </div>
          </FormField>
        </>
      )}

      <FormField label="Do you use general-purpose AI models (e.g. GPT-4, Claude, Gemini) in your products or operations?">
        <div className={styles.labelRow}>
          <Tooltip text="Use of GPAI models may trigger obligations under EU AI Act Art. 53–55 depending on your role and the model's systemic risk classification." />
        </div>
        {renderYesNo(
          watch("uses_gpai"),
          () => setValue("uses_gpai", true),
          () => setValue("uses_gpai", false)
        )}
      </FormField>

      {usesAi === true && (
        <FormField label="Do you have an AI governance or ethics policy?">
          <div className={styles.labelRow}>
            <Tooltip text="EU AI Act Art. 17 requires providers of high-risk AI systems to implement a quality management system including governance documentation." />
          </div>
          {renderYesNo(
            watch("has_ai_governance_policy"),
            () => setValue("has_ai_governance_policy", true),
            () => setValue("has_ai_governance_policy", false)
          )}
        </FormField>
      )}
    </div>
  );

  const renderNavigation = () => (
    <div className={styles.nav}>
      <Button type="button" variant="secondary" onClick={() => onBack()}>
        ← Back
      </Button>
      <Button type="submit" variant="success" loading={isSubmitting} loadingText="Submitting...">
        Finish & Submit ✓
      </Button>
    </div>
  );

  // ── Back ──────────────────────────────────────────────────

  const onBack = async () => {
    try {
      const token = await getToken();
      const data = watch();
      await clientApiFetch("/api/v1/profile", token!, {
        method: "PATCH",
        body: JSON.stringify({
          gdpr_data: {
            lawful_bases: data.lawful_bases ?? [],
            processes_children_data: data.processes_children_data ?? null,
            transfers_outside_eea: data.transfers_outside_eea ?? null,
            transfer_mechanisms: data.transfer_mechanisms ?? [],
            uses_data_processors: data.uses_data_processors ?? null,
            has_breach_procedure: data.has_breach_procedure ?? null,
            has_dpia: data.has_dpia ?? null,
          },
          nis2_data: {
            sectors: data.nis2_sectors ?? [],
            entity_type: data.nis2_entity_type || null,
            has_mfa: data.has_mfa ?? null,
            has_incident_response_plan: data.has_incident_response_plan ?? null,
            has_business_continuity_plan: data.has_business_continuity_plan ?? null,
            assesses_supply_chain: data.assesses_supply_chain ?? null,
          },
          ai_act_data: {
            uses_ai: data.uses_ai ?? null,
            ai_role: data.ai_role || null,
            high_risk_ai_categories: data.high_risk_ai_categories ?? [],
            uses_gpai: data.uses_gpai ?? null,
            has_ai_governance_policy: data.has_ai_governance_policy ?? null,
          },
        }),
      });
    } catch {}
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    router.push("/onboarding/step/5" as any);
  };

  // ── Submit ─────────────────────────────────────────────────

  const onSubmit = async (data: FormData) => {
    setServerError(null);
    try {
      const token = await getToken();

      const saveRes = await clientApiFetch("/api/v1/profile", token!, {
        method: "PATCH",
        body: JSON.stringify({
          gdpr_data: {
            lawful_bases: data.lawful_bases,
            processes_children_data: data.processes_children_data,
            transfers_outside_eea: data.transfers_outside_eea,
            transfer_mechanisms: data.transfer_mechanisms ?? [],
            uses_data_processors: data.uses_data_processors,
            has_breach_procedure: data.has_breach_procedure,
            has_dpia: data.has_dpia,
          },
          nis2_data: {
            sectors: data.nis2_sectors ?? [],
            entity_type: data.nis2_entity_type || null,
            has_mfa: data.has_mfa ?? null,
            has_incident_response_plan: data.has_incident_response_plan ?? null,
            has_business_continuity_plan: data.has_business_continuity_plan ?? null,
            assesses_supply_chain: data.assesses_supply_chain ?? null,
          },
          ai_act_data: {
            uses_ai: data.uses_ai,
            ai_role: data.ai_role || null,
            high_risk_ai_categories: data.high_risk_ai_categories ?? [],
            uses_gpai: data.uses_gpai ?? null,
            has_ai_governance_policy: data.has_ai_governance_policy ?? null,
          },
          is_complete: true,
        }),
      });

      if (!saveRes.ok) {
        const body = await saveRes.json().catch(() => ({}));
        throw new Error(body?.detail ?? "Failed to save. Please try again.");
      }

      // If profile was already complete — just go back to dashboard
      if (initialData?.is_complete) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        router.push("/dashboard" as any);
        return;
      }

      // First time completing — validate all steps
      const profileRes = await clientApiFetch("/api/v1/profile", token!, { method: "GET" });
      const profile = profileRes.ok ? await profileRes.json() : null;
      const incompleteStep = getFirstIncompleteStep(profile);

      if (incompleteStep) {
        setServerError(
          `Step ${incompleteStep} has required fields missing — taking you back to complete it.`
        );
        setTimeout(() => {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          router.push(`/onboarding/step/${incompleteStep}` as any);
        }, 1500);
        return;
      }

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      router.push("/dashboard" as any);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Something went wrong.");
    }
  };

  // ── Render ─────────────────────────────────────────────────

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div className={styles.section}>
        {renderGdprSection()}
        <div className={styles.divider} />
        {renderNis2Section()}
        <div className={styles.divider} />
        {renderAiActSection()}
      </div>
      {serverError && <p className="mt-4 text-sm text-red-600">{serverError}</p>}
      {renderNavigation()}
    </form>
  );
}
