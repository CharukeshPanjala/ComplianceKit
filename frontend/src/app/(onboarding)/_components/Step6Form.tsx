"use client";

import { useState, useEffect } from "react";
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
  // GDPR — Tier A new fields
  has_erasure_process: z.boolean().optional(),
  has_restriction_process: z.boolean().optional(),
  has_portability_process: z.boolean().optional(),
  has_marketing_objection_process: z.boolean().optional(),
  uses_automated_decisions: z.boolean().optional(),
  has_joint_controllers: z.boolean().optional(),
  is_public_authority: z.boolean().optional(),
  processes_employee_data: z.boolean().optional(),
  processes_for_research: z.boolean().optional(),
  special_category_condition: z.string().optional(),
  transfer_destination_countries: z.array(z.string()).optional(),
  derogation_types: z.array(z.string()).optional(),
  has_bcr: z.boolean().optional(),
  has_public_incident_notification_gdpr: z.boolean().optional(),
  // NIS2
  nis2_sectors: z.array(z.string()).optional(),
  nis2_entity_type: z.string().optional(),
  has_mfa: z.boolean().optional(),
  has_incident_response_plan: z.boolean().optional(),
  has_business_continuity_plan: z.boolean().optional(),
  assesses_supply_chain: z.boolean().optional(),
  // NIS2 — Tier A new fields
  has_vulnerability_disclosure_policy: z.boolean().optional(),
  management_approved_security_measures: z.boolean().optional(),
  has_cyber_awareness_training: z.boolean().optional(),
  uses_encryption: z.boolean().optional(),
  has_asset_inventory: z.boolean().optional(),
  participates_in_info_sharing: z.boolean().optional(),
  uses_certified_products: z.boolean().optional(),
  nis2_registration_complete: z.boolean().optional(),
  has_public_incident_notification_nis2: z.boolean().optional(),
  // EU AI Act
  uses_ai: z.boolean({ error: "Please answer this question" }),
  ai_role: z.string().optional(),
  high_risk_ai_categories: z.array(z.string()).optional(),
  uses_gpai: z.boolean().optional(),
  has_ai_governance_policy: z.boolean().optional(),
  // EU AI Act — Tier A new fields
  has_ai_literacy_training: z.boolean().optional(),
  is_public_body: z.boolean().optional(),
  uses_chatbot: z.boolean().optional(),
  uses_synthetic_content: z.boolean().optional(),
  uses_emotion_recognition: z.boolean().optional(),
  has_ai_complaint_process: z.boolean().optional(),
  has_ai_explanation_process: z.boolean().optional(),
  prohibited_practice_flags: z.array(z.string()).optional(),
  gpai_flops_above_threshold: z.boolean().optional(),
  has_gpai_eu_representative: z.boolean().optional(),
});

type FormData = z.infer<typeof schema>;

// ── Constants ─────────────────────────────────────────────

const LAWFUL_BASIS_OPTIONS = [
  { value: "consent", label: "Consent - Art. 6(1)(a)" },
  { value: "contract", label: "Contract - Art. 6(1)(b)" },
  { value: "legal_obligation", label: "Legal obligation - Art. 6(1)(c)" },
  { value: "vital_interests", label: "Vital interests - Art. 6(1)(d)" },
  { value: "public_task", label: "Public task - Art. 6(1)(e)" },
  { value: "legitimate_interests", label: "Legitimate interest - Art. 6(1)(f)" },
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

const SPECIAL_CATEGORY_CONDITION_OPTIONS = [
  { value: "explicit_consent", label: "Explicit consent (Art. 9(2)(a))" },
  { value: "employment_law", label: "Employment/social security law (Art. 9(2)(b))" },
  { value: "vital_interests", label: "Vital interests (Art. 9(2)(c))" },
  { value: "legitimate_activities", label: "Legitimate activities of non-profit (Art. 9(2)(d))" },
  { value: "public_data", label: "Manifestly made public (Art. 9(2)(e))" },
  { value: "legal_claims", label: "Legal claims (Art. 9(2)(f))" },
  { value: "substantial_public_interest", label: "Substantial public interest (Art. 9(2)(g))" },
  { value: "medical", label: "Medical purposes (Art. 9(2)(h))" },
  { value: "public_health", label: "Public health (Art. 9(2)(i))" },
  { value: "research", label: "Research/statistics/archiving (Art. 9(2)(j))" },
];

const DEROGATION_TYPE_OPTIONS = [
  { value: "consent", label: "Explicit consent of the data subject" },
  { value: "contract", label: "Necessary for contract performance" },
  { value: "legal_claims", label: "Establishment or defence of legal claims" },
  { value: "vital_interests", label: "Vital interests" },
  { value: "public_register", label: "Transfer from a public register" },
  { value: "compelling_legitimate_interests", label: "Compelling legitimate interests" },
];

const PROHIBITED_PRACTICE_OPTIONS = [
  { value: "subliminal_manipulation", label: "Subliminal or manipulative techniques to distort behaviour" },
  { value: "vulnerability_exploitation", label: "Exploiting vulnerabilities of specific groups (age, disability, etc.)" },
  { value: "social_scoring", label: "Social scoring by public authorities" },
  { value: "real_time_biometric", label: "Real-time remote biometric identification in public spaces (law enforcement)" },
  { value: "facial_scraping", label: "Untargeted facial image scraping from internet or CCTV" },
  { value: "emotion_inference_workplace", label: "Inferring emotions in workplace or education" },
  { value: "criminal_prediction", label: "AI profiling to predict criminal offences" },
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
  textarea: "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-navy focus:outline-none",
  error: "mt-4 text-sm text-red-600",
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
      has_erasure_process: (gdpr.has_erasure_process as boolean) ?? undefined,
      has_restriction_process: (gdpr.has_restriction_process as boolean) ?? undefined,
      has_portability_process: (gdpr.has_portability_process as boolean) ?? undefined,
      has_marketing_objection_process: (gdpr.has_marketing_objection_process as boolean) ?? undefined,
      uses_automated_decisions: (gdpr.uses_automated_decisions as boolean) ?? undefined,
      has_joint_controllers: (gdpr.has_joint_controllers as boolean) ?? undefined,
      is_public_authority: (gdpr.is_public_authority as boolean) ?? undefined,
      processes_employee_data: (gdpr.processes_employee_data as boolean) ?? undefined,
      processes_for_research: (gdpr.processes_for_research as boolean) ?? undefined,
      special_category_condition: (gdpr.special_category_condition as string) ?? "",
      transfer_destination_countries: (gdpr.transfer_destination_countries as string[]) ?? [],
      derogation_types: (gdpr.derogation_types as string[]) ?? [],
      has_bcr: (gdpr.has_bcr as boolean) ?? undefined,
      has_public_incident_notification_gdpr: (gdpr.has_public_incident_notification as boolean) ?? undefined,
      nis2_sectors: (nis2.sectors as string[]) ?? [],
      nis2_entity_type: (nis2.entity_type as string) ?? "",
      has_mfa: (nis2.has_mfa as boolean) ?? undefined,
      has_incident_response_plan: (nis2.has_incident_response_plan as boolean) ?? undefined,
      has_business_continuity_plan: (nis2.has_business_continuity_plan as boolean) ?? undefined,
      assesses_supply_chain: (nis2.assesses_supply_chain as boolean) ?? undefined,
      has_vulnerability_disclosure_policy: (nis2.has_vulnerability_disclosure_policy as boolean) ?? undefined,
      management_approved_security_measures: (nis2.management_approved_security_measures as boolean) ?? undefined,
      has_cyber_awareness_training: (nis2.has_cyber_awareness_training as boolean) ?? undefined,
      uses_encryption: (nis2.uses_encryption as boolean) ?? undefined,
      has_asset_inventory: (nis2.has_asset_inventory as boolean) ?? undefined,
      participates_in_info_sharing: (nis2.participates_in_info_sharing as boolean) ?? undefined,
      uses_certified_products: (nis2.uses_certified_products as boolean) ?? undefined,
      nis2_registration_complete: (nis2.nis2_registration_complete as boolean) ?? undefined,
      has_public_incident_notification_nis2: (nis2.has_public_incident_notification as boolean) ?? undefined,
      uses_ai: (ai.uses_ai as boolean) ?? undefined,
      ai_role: (ai.ai_role as string) ?? "",
      high_risk_ai_categories: (ai.high_risk_ai_categories as string[]) ?? [],
      uses_gpai: (ai.uses_gpai as boolean) ?? undefined,
      has_ai_governance_policy: (ai.has_ai_governance_policy as boolean) ?? undefined,
      has_ai_literacy_training: (ai.has_ai_literacy_training as boolean) ?? undefined,
      is_public_body: (ai.is_public_body as boolean) ?? undefined,
      uses_chatbot: (ai.uses_chatbot as boolean) ?? undefined,
      uses_synthetic_content: (ai.uses_synthetic_content as boolean) ?? undefined,
      uses_emotion_recognition: (ai.uses_emotion_recognition as boolean) ?? undefined,
      has_ai_complaint_process: (ai.has_ai_complaint_process as boolean) ?? undefined,
      has_ai_explanation_process: (ai.has_ai_explanation_process as boolean) ?? undefined,
      prohibited_practice_flags: (ai.prohibited_practice_flags as string[]) ?? [],
      gpai_flops_above_threshold: (ai.gpai_flops_above_threshold as boolean) ?? undefined,
      has_gpai_eu_representative: (ai.has_gpai_eu_representative as boolean) ?? undefined,
    },
  });

  const lawfulBases = watch("lawful_bases") ?? [];
  const transfersOutsideEea = watch("transfers_outside_eea");
  const transferMechanisms = watch("transfer_mechanisms") ?? [];
  const derogationTypes = watch("derogation_types") ?? [];
  const transferDestinationCountries = watch("transfer_destination_countries") ?? [];
  const nis2Sectors = watch("nis2_sectors") ?? [];
  const nis2EntityType = watch("nis2_entity_type");
  const usesAi = watch("uses_ai");
  const highRiskCategories = watch("high_risk_ai_categories") ?? [];
  const aiRole = watch("ai_role");
  const usesGpai = watch("uses_gpai");
  const prohibitedPracticeFlags = watch("prohibited_practice_flags") ?? [];

  const nis2InScope = nis2Sectors.length > 0 && !nis2Sectors.includes("not_applicable");

  const specialCategoryDataCategories = new Set(
    (initialData?.data_categories_processed ?? []) as string[]
  );
  const hasSpecialCategoryData = [
    "health", "biometric", "genetic", "racial_ethnic",
    "political", "religious", "trade_union", "sexual_orientation",
  ].some((c) => specialCategoryDataCategories.has(c));

  // ── Live rules panel sync ──────────────────────────────────
  useEffect(() => {
    const gdprRules: string[] = ["Art.5", "Art.6"];
    if (lawfulBases.includes("consent")) gdprRules.push("Art.7");
    if (hasSpecialCategoryData) gdprRules.push("Art.9");
    gdprRules.push("Art.17", "Art.18", "Art.20", "Art.21");
    if (watch("uses_automated_decisions")) gdprRules.push("Art.22");
    gdprRules.push("Art.30", "Art.32", "Art.33", "Art.34", "Art.35");
    if (watch("is_public_authority")) gdprRules.push("Art.37", "Art.38", "Art.39");
    if (transfersOutsideEea) gdprRules.push("Art.44", "Art.45", "Art.46");
    if (transferMechanisms.includes("bcrs") || watch("has_bcr")) gdprRules.push("Art.47");
    if (derogationTypes.length > 0) gdprRules.push("Art.49");

    const nis2Rules: string[] = [];
    if (nis2InScope) {
      nis2Rules.push("Art.18", "Art.20", "Art.21", "Art.23");
      if (watch("uses_certified_products")) nis2Rules.push("Art.24");
      if (watch("has_vulnerability_disclosure_policy")) nis2Rules.push("Art.12");
      if (watch("participates_in_info_sharing")) nis2Rules.push("Art.29");
      if (watch("nis2_registration_complete")) nis2Rules.push("Art.27");
    }

    const aiRules: string[] = [];
    if (usesAi) {
      aiRules.push("Art.6", "Art.13", "Art.14");
      if (highRiskCategories.length > 0 && !highRiskCategories.includes("none")) {
        aiRules.push("Art.9", "Art.10", "Art.11", "Art.12", "Art.15", "Art.17", "Art.43");
        if (aiRole === "deployer" || aiRole === "both") aiRules.push("Art.26");
      }
      if (watch("uses_chatbot") || watch("uses_synthetic_content") || watch("uses_emotion_recognition")) {
        aiRules.push("Art.50");
      }
      if (watch("has_ai_explanation_process")) aiRules.push("Art.86");
      if (usesGpai) {
        aiRules.push("Art.51", "Art.52", "Art.53");
        if (aiRole === "provider" || aiRole === "both") aiRules.push("Art.54", "Art.55");
      }
    }

    const gdprCount = Math.min(gdprRules.length, 5);
    const nis2Count = Math.min(nis2Rules.length, 5);
    const aiCount = Math.min(aiRules.length, 4);

    const allActive = [...new Set([...gdprRules, ...nis2Rules, ...aiRules])];
    const reg = nis2InScope && nis2Rules.length >= gdprRules.length
      ? "NIS2"
      : usesAi && aiRules.length >= gdprRules.length
      ? "AI_ACT"
      : "GDPR";

    const payload = {
      activeRuleIds: allActive,
      regulation: reg,
      trackProgress: { gdpr: gdprCount, nis2: nis2Count, aiAct: aiCount },
    };

    try {
      sessionStorage.setItem("ck_live_rules", JSON.stringify(payload));
      window.dispatchEvent(new Event("ck:rules-update"));
    } catch {
      // ignore
    }
  }, [
    lawfulBases, transfersOutsideEea, transferMechanisms, derogationTypes,
    nis2Sectors, usesAi, highRiskCategories, aiRole, usesGpai,
    nis2InScope, hasSpecialCategoryData,
  ]);

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

  const toggleDerogationType = (value: string) => {
    const updated = derogationTypes.includes(value)
      ? derogationTypes.filter((v) => v !== value)
      : [...derogationTypes, value];
    setValue("derogation_types", updated);
  };

  const toggleProhibitedPracticeFlag = (value: string) => {
    if (value === "none") {
      setValue("prohibited_practice_flags", prohibitedPracticeFlags.includes("none") ? [] : ["none"]);
      return;
    }
    const without = prohibitedPracticeFlags.filter((v) => v !== "none");
    const updated = without.includes(value)
      ? without.filter((v) => v !== value)
      : [...without, value];
    setValue("prohibited_practice_flags", updated);
  };

  const handleTransferCountriesChange = (raw: string) => {
    const arr = raw
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    setValue("transfer_destination_countries", arr);
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
      <p className={styles.sectionTitle}>GDPR - Lawful basis & obligations</p>

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
          <Tooltip text="Using processors triggers GDPR Art. 28. You must have a Data Processing Agreement (DPA) in place with each one." />
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
          <Tooltip text="GDPR Art. 35 requires a DPIA for high-risk processing activities, e.g. large-scale profiling, systematic monitoring, processing special category data." />
        </div>
        {renderYesNo(
          watch("has_dpia"),
          () => setValue("has_dpia", true, { shouldValidate: true }),
          () => setValue("has_dpia", false, { shouldValidate: true })
        )}
      </FormField>

      <FormField label="Do you have a process to handle erasure requests (right to be forgotten)?">
        <div className={styles.labelRow}>
          <Tooltip text="GDPR Art. 17 requires you to erase personal data on request unless a legitimate ground for retention applies." />
        </div>
        {renderYesNo(
          watch("has_erasure_process"),
          () => setValue("has_erasure_process", true),
          () => setValue("has_erasure_process", false)
        )}
      </FormField>

      <FormField label="Can you restrict processing of personal data on request?">
        <div className={styles.labelRow}>
          <Tooltip text="GDPR Art. 18 gives individuals the right to restrict how their data is processed in certain circumstances." />
        </div>
        {renderYesNo(
          watch("has_restriction_process"),
          () => setValue("has_restriction_process", true),
          () => setValue("has_restriction_process", false)
        )}
      </FormField>

      <FormField label="Can you export personal data in a machine-readable format on request?">
        <div className={styles.labelRow}>
          <Tooltip text="GDPR Art. 20 grants data portability rights when processing is based on consent or contract and is automated." />
        </div>
        {renderYesNo(
          watch("has_portability_process"),
          () => setValue("has_portability_process", true),
          () => setValue("has_portability_process", false)
        )}
      </FormField>

      <FormField label="Do you have a process for individuals to object to direct marketing?">
        <div className={styles.labelRow}>
          <Tooltip text="GDPR Art. 21 gives individuals an absolute right to object to processing for direct marketing." />
        </div>
        {renderYesNo(
          watch("has_marketing_objection_process"),
          () => setValue("has_marketing_objection_process", true),
          () => setValue("has_marketing_objection_process", false)
        )}
      </FormField>

      <FormField label="Do you make automated decisions that significantly affect individuals (e.g. credit scoring, profiling)?">
        <div className={styles.labelRow}>
          <Tooltip text="GDPR Art. 22 covers solely automated decisions with significant effects, distinct from general AI use." />
        </div>
        {renderYesNo(
          watch("uses_automated_decisions"),
          () => setValue("uses_automated_decisions", true),
          () => setValue("uses_automated_decisions", false)
        )}
      </FormField>

      <FormField label="Do you jointly determine the purposes and means of processing with another organisation (joint controllers)?">
        <div className={styles.labelRow}>
          <Tooltip text="GDPR Art. 26 requires a documented arrangement between joint controllers setting out their respective responsibilities." />
        </div>
        {renderYesNo(
          watch("has_joint_controllers"),
          () => setValue("has_joint_controllers", true),
          () => setValue("has_joint_controllers", false)
        )}
      </FormField>

      <FormField label="Is your organisation a public authority or body?">
        <div className={styles.labelRow}>
          <Tooltip text="Public authorities are required to appoint a DPO under GDPR Art. 37(1)(a) regardless of processing scale." />
        </div>
        {renderYesNo(
          watch("is_public_authority"),
          () => setValue("is_public_authority", true),
          () => setValue("is_public_authority", false)
        )}
      </FormField>

      <FormField label="Do you process personal data of your own employees?">
        <div className={styles.labelRow}>
          <Tooltip text="GDPR Art. 88 allows Member States to set specific rules for employee data. Your obligations may vary by jurisdiction." />
        </div>
        {renderYesNo(
          watch("processes_employee_data"),
          () => setValue("processes_employee_data", true),
          () => setValue("processes_employee_data", false)
        )}
      </FormField>

      <FormField label="Do you process personal data for scientific research, statistics, or archiving in the public interest?">
        <div className={styles.labelRow}>
          <Tooltip text="GDPR Art. 89 provides derogations for research/statistics but requires appropriate safeguards such as anonymisation." />
        </div>
        {renderYesNo(
          watch("processes_for_research"),
          () => setValue("processes_for_research", true),
          () => setValue("processes_for_research", false)
        )}
      </FormField>

      <FormField label="Do you have a process to notify affected individuals of a personal data breach?">
        <div className={styles.labelRow}>
          <Tooltip text="GDPR Art. 34 requires notifying data subjects without undue delay when a breach is likely to cause high risk." />
        </div>
        {renderYesNo(
          watch("has_public_incident_notification_gdpr"),
          () => setValue("has_public_incident_notification_gdpr", true),
          () => setValue("has_public_incident_notification_gdpr", false)
        )}
      </FormField>

      {hasSpecialCategoryData && (
        <FormField label="What is your legal condition for processing special category data (Art. 9(2))?">
          <div className={styles.labelRow}>
            <Tooltip text="GDPR Art. 9(2) lists the exhaustive conditions permitting special category data processing. Explicit consent is most common." />
          </div>
          <div className={styles.grid}>
            {SPECIAL_CATEGORY_CONDITION_OPTIONS.map((opt) => (
              <CheckboxCard
                key={opt.value}
                label={opt.label}
                checked={watch("special_category_condition") === opt.value}
                onChange={() =>
                  setValue(
                    "special_category_condition",
                    watch("special_category_condition") === opt.value ? "" : opt.value
                  )
                }
              />
            ))}
          </div>
        </FormField>
      )}

      {transfersOutsideEea === true && (
        <>
          <FormField label="Which countries do you transfer personal data to?" hint="comma-separated">
            <div className={styles.labelRow}>
              <Tooltip text="GDPR Art. 45 provides an adequacy list. Transfers to non-adequate countries require additional safeguards." />
            </div>
            <input
              type="text"
              className={styles.textarea}
              defaultValue={transferDestinationCountries.join(", ")}
              onChange={(e) => handleTransferCountriesChange(e.target.value)}
              placeholder="e.g. United States, India, Singapore"
            />
          </FormField>

          <FormField label="Do you rely on any Art. 49 derogations for transfers?" hint="select all that apply">
            <div className={styles.labelRow}>
              <Tooltip text="Art. 49 derogations (e.g. explicit consent, vital interests, legal claims) apply only in specific, limited circumstances." />
            </div>
            <div className={styles.grid}>
              {DEROGATION_TYPE_OPTIONS.map((opt) => (
                <CheckboxCard
                  key={opt.value}
                  label={opt.label}
                  checked={derogationTypes.includes(opt.value)}
                  onChange={() => toggleDerogationType(opt.value)}
                />
              ))}
            </div>
          </FormField>

          <FormField label="Has your organisation adopted Binding Corporate Rules (BCRs)?">
            <div className={styles.labelRow}>
              <Tooltip text="BCRs under GDPR Art. 47 allow intra-group international transfers without per-country SCCs." />
            </div>
            {renderYesNo(
              watch("has_bcr"),
              () => setValue("has_bcr", true),
              () => setValue("has_bcr", false)
            )}
          </FormField>
        </>
      )}
    </div>
  );

  const renderNis2Section = () => (
    <div className={styles.section}>
      <p className={styles.sectionTitle}>NIS2: Cybersecurity</p>

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

          <FormField label="Do you have a coordinated vulnerability disclosure policy?">
            <div className={styles.labelRow}>
              <Tooltip text="NIS2 Art. 12 requires Member State entities to have a policy allowing security researchers to disclose vulnerabilities responsibly." />
            </div>
            {renderYesNo(
              watch("has_vulnerability_disclosure_policy"),
              () => setValue("has_vulnerability_disclosure_policy", true),
              () => setValue("has_vulnerability_disclosure_policy", false)
            )}
          </FormField>

          <FormField label="Has management/the board formally approved your cybersecurity risk-management measures?">
            <div className={styles.labelRow}>
              <Tooltip text="NIS2 Art. 20 makes management bodies personally liable for cybersecurity measures. Formal approval is required." />
            </div>
            {renderYesNo(
              watch("management_approved_security_measures"),
              () => setValue("management_approved_security_measures", true),
              () => setValue("management_approved_security_measures", false)
            )}
          </FormField>

          <FormField label="Do you provide regular cybersecurity awareness training to all staff?">
            <div className={styles.labelRow}>
              <Tooltip text="NIS2 Art. 21(g) requires entities to implement cybersecurity hygiene policies and awareness training programmes." />
            </div>
            {renderYesNo(
              watch("has_cyber_awareness_training"),
              () => setValue("has_cyber_awareness_training", true),
              () => setValue("has_cyber_awareness_training", false)
            )}
          </FormField>

          <FormField label="Do you use encryption to protect data in transit and at rest?">
            <div className={styles.labelRow}>
              <Tooltip text="NIS2 Art. 21(h) explicitly lists use of cryptography and encryption as a required security measure." />
            </div>
            {renderYesNo(
              watch("uses_encryption"),
              () => setValue("uses_encryption", true),
              () => setValue("uses_encryption", false)
            )}
          </FormField>

          <FormField label="Do you maintain an inventory of your IT assets?">
            <div className={styles.labelRow}>
              <Tooltip text="NIS2 Art. 21(i) requires policies and procedures for ICT asset management as part of security risk management." />
            </div>
            {renderYesNo(
              watch("has_asset_inventory"),
              () => setValue("has_asset_inventory", true),
              () => setValue("has_asset_inventory", false)
            )}
          </FormField>

          <FormField label="Does your organisation participate in any cybersecurity information-sharing arrangements?">
            <div className={styles.labelRow}>
              <Tooltip text="NIS2 Art. 29 enables voluntary participation in information-sharing arrangements to improve collective security." />
            </div>
            {renderYesNo(
              watch("participates_in_info_sharing"),
              () => setValue("participates_in_info_sharing", true),
              () => setValue("participates_in_info_sharing", false)
            )}
          </FormField>

          <FormField label="Do you use ICT products or services that are certified under EU cybersecurity certification schemes?">
            <div className={styles.labelRow}>
              <Tooltip text="NIS2 Art. 24 encourages use of certified products. Art. 19 allows the Commission to mandate certification for certain categories." />
            </div>
            {renderYesNo(
              watch("uses_certified_products"),
              () => setValue("uses_certified_products", true),
              () => setValue("uses_certified_products", false)
            )}
          </FormField>

          <FormField label="Has your organisation completed NIS2 registration with the relevant national authority?">
            <div className={styles.labelRow}>
              <Tooltip text="NIS2 Art. 27 requires essential and important entities to register with the national competent authority, providing contact and sector details." />
            </div>
            {renderYesNo(
              watch("nis2_registration_complete"),
              () => setValue("nis2_registration_complete", true),
              () => setValue("nis2_registration_complete", false)
            )}
          </FormField>

          <FormField label="Can you notify your customers or the public of significant cybersecurity incidents?">
            <div className={styles.labelRow}>
              <Tooltip text="NIS2 Art. 23 requires notifying recipients of services and the public when an incident may affect them." />
            </div>
            {renderYesNo(
              watch("has_public_incident_notification_nis2"),
              () => setValue("has_public_incident_notification_nis2", true),
              () => setValue("has_public_incident_notification_nis2", false)
            )}
          </FormField>
        </>
      )}
    </div>
  );

  const renderAiActSection = () => (
    <div className={styles.section}>
      <p className={styles.sectionTitle}>EU AI Act: Artificial Intelligence</p>

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

      <FormField label="Do you provide AI literacy training to staff who work with AI systems?">
        <div className={styles.labelRow}>
          <Tooltip text="EU AI Act Art. 4 requires providers and deployers to ensure staff have sufficient AI literacy for their role." />
        </div>
        {renderYesNo(
          watch("has_ai_literacy_training"),
          () => setValue("has_ai_literacy_training", true),
          () => setValue("has_ai_literacy_training", false)
        )}
      </FormField>

      <FormField label="Is your organisation a public body or providing services in the public interest?">
        <div className={styles.labelRow}>
          <Tooltip text="EU AI Act Art. 27 imposes specific obligations on deployers that are public bodies using high-risk AI systems." />
        </div>
        {renderYesNo(
          watch("is_public_body"),
          () => setValue("is_public_body", true),
          () => setValue("is_public_body", false)
        )}
      </FormField>

      {usesAi === true && (
        <>
          <FormField label="Do you use or deploy AI-powered chatbots or virtual assistants?">
            <div className={styles.labelRow}>
              <Tooltip text="EU AI Act Art. 50 requires chatbots to disclose that users are interacting with an AI system." />
            </div>
            {renderYesNo(
              watch("uses_chatbot"),
              () => setValue("uses_chatbot", true),
              () => setValue("uses_chatbot", false)
            )}
          </FormField>

          <FormField label="Do you generate or distribute AI-generated synthetic content (images, audio, video, text)?">
            <div className={styles.labelRow}>
              <Tooltip text="EU AI Act Art. 50 requires synthetic content to be labelled as AI-generated using machine-readable markers." />
            </div>
            {renderYesNo(
              watch("uses_synthetic_content"),
              () => setValue("uses_synthetic_content", true),
              () => setValue("uses_synthetic_content", false)
            )}
          </FormField>

          <FormField label="Do you use emotion recognition or biometric categorisation systems?">
            <div className={styles.labelRow}>
              <Tooltip text="EU AI Act Art. 50 requires transparency disclosures when using emotion recognition or biometric categorisation on individuals." />
            </div>
            {renderYesNo(
              watch("uses_emotion_recognition"),
              () => setValue("uses_emotion_recognition", true),
              () => setValue("uses_emotion_recognition", false)
            )}
          </FormField>

          <FormField label="Do you have a complaint-handling process for issues related to your AI systems?">
            <div className={styles.labelRow}>
              <Tooltip text="EU AI Act Art. 26(8) and Art. 86 require deployers to provide a mechanism for affected persons to raise concerns about AI decisions." />
            </div>
            {renderYesNo(
              watch("has_ai_complaint_process"),
              () => setValue("has_ai_complaint_process", true),
              () => setValue("has_ai_complaint_process", false)
            )}
          </FormField>

          <FormField label="Can you explain AI-based decisions to individuals who request an explanation?">
            <div className={styles.labelRow}>
              <Tooltip text="EU AI Act Art. 86 gives individuals the right to request an explanation of high-risk AI system outputs that affect them." />
            </div>
            {renderYesNo(
              watch("has_ai_explanation_process"),
              () => setValue("has_ai_explanation_process", true),
              () => setValue("has_ai_explanation_process", false)
            )}
          </FormField>

          <FormField
            label="Does your organisation use any of the following AI practices? (select all that apply)"
            hint="select all that apply"
          >
            <div className={styles.labelRow}>
              <Tooltip text="EU AI Act Art. 5 prohibits these practices outright. If any apply, immediate remediation is required." />
            </div>
            <div className={styles.grid}>
              {PROHIBITED_PRACTICE_OPTIONS.map((opt) => (
                <CheckboxCard
                  key={opt.value}
                  label={opt.label}
                  checked={prohibitedPracticeFlags.includes(opt.value)}
                  onChange={() => toggleProhibitedPracticeFlag(opt.value)}
                />
              ))}
            </div>
          </FormField>
        </>
      )}

      {usesGpai === true && (
        <>
          <FormField label="Does the GPAI model you use exceed 10^25 FLOPs training compute (systemic risk threshold)?">
            <div className={styles.labelRow}>
              <Tooltip text="EU AI Act Art. 51 classifies GPAI models trained above 10^25 FLOPs as having systemic risk, triggering additional obligations under Arts. 53-55." />
            </div>
            {renderYesNo(
              watch("gpai_flops_above_threshold"),
              () => setValue("gpai_flops_above_threshold", true),
              () => setValue("gpai_flops_above_threshold", false)
            )}
          </FormField>

          {(aiRole === "provider" || aiRole === "multiple") && (
            <FormField label="Do you have an authorised EU representative for your GPAI model?">
              <div className={styles.labelRow}>
                <Tooltip text="EU AI Act Art. 54 requires non-EU providers of GPAI models to designate an authorised representative established in the EU." />
              </div>
              {renderYesNo(
                watch("has_gpai_eu_representative"),
                () => setValue("has_gpai_eu_representative", true),
                () => setValue("has_gpai_eu_representative", false)
              )}
            </FormField>
          )}
        </>
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
            has_erasure_process: data.has_erasure_process ?? null,
            has_restriction_process: data.has_restriction_process ?? null,
            has_portability_process: data.has_portability_process ?? null,
            has_marketing_objection_process: data.has_marketing_objection_process ?? null,
            uses_automated_decisions: data.uses_automated_decisions ?? null,
            has_joint_controllers: data.has_joint_controllers ?? null,
            is_public_authority: data.is_public_authority ?? null,
            processes_employee_data: data.processes_employee_data ?? null,
            processes_for_research: data.processes_for_research ?? null,
            special_category_condition: data.special_category_condition || null,
            transfer_destination_countries: data.transfer_destination_countries ?? [],
            derogation_types: data.derogation_types ?? [],
            has_bcr: data.has_bcr ?? null,
            has_public_incident_notification: data.has_public_incident_notification_gdpr ?? null,
          },
          nis2_data: {
            sectors: data.nis2_sectors ?? [],
            entity_type: data.nis2_entity_type || null,
            has_mfa: data.has_mfa ?? null,
            has_incident_response_plan: data.has_incident_response_plan ?? null,
            has_business_continuity_plan: data.has_business_continuity_plan ?? null,
            assesses_supply_chain: data.assesses_supply_chain ?? null,
            has_vulnerability_disclosure_policy: data.has_vulnerability_disclosure_policy ?? null,
            management_approved_security_measures: data.management_approved_security_measures ?? null,
            has_cyber_awareness_training: data.has_cyber_awareness_training ?? null,
            uses_encryption: data.uses_encryption ?? null,
            has_asset_inventory: data.has_asset_inventory ?? null,
            participates_in_info_sharing: data.participates_in_info_sharing ?? null,
            uses_certified_products: data.uses_certified_products ?? null,
            nis2_registration_complete: data.nis2_registration_complete ?? null,
            has_public_incident_notification: data.has_public_incident_notification_nis2 ?? null,
          },
          ai_act_data: {
            uses_ai: data.uses_ai ?? null,
            ai_role: data.ai_role || null,
            high_risk_ai_categories: data.high_risk_ai_categories ?? [],
            uses_gpai: data.uses_gpai ?? null,
            has_ai_governance_policy: data.has_ai_governance_policy ?? null,
            has_ai_literacy_training: data.has_ai_literacy_training ?? null,
            is_public_body: data.is_public_body ?? null,
            uses_chatbot: data.uses_chatbot ?? null,
            uses_synthetic_content: data.uses_synthetic_content ?? null,
            uses_emotion_recognition: data.uses_emotion_recognition ?? null,
            has_ai_complaint_process: data.has_ai_complaint_process ?? null,
            has_ai_explanation_process: data.has_ai_explanation_process ?? null,
            prohibited_practice_flags: data.prohibited_practice_flags ?? [],
            gpai_flops_above_threshold: data.gpai_flops_above_threshold ?? null,
            has_gpai_eu_representative: data.has_gpai_eu_representative ?? null,
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
            has_erasure_process: data.has_erasure_process ?? null,
            has_restriction_process: data.has_restriction_process ?? null,
            has_portability_process: data.has_portability_process ?? null,
            has_marketing_objection_process: data.has_marketing_objection_process ?? null,
            uses_automated_decisions: data.uses_automated_decisions ?? null,
            has_joint_controllers: data.has_joint_controllers ?? null,
            is_public_authority: data.is_public_authority ?? null,
            processes_employee_data: data.processes_employee_data ?? null,
            processes_for_research: data.processes_for_research ?? null,
            special_category_condition: data.special_category_condition || null,
            transfer_destination_countries: data.transfer_destination_countries ?? [],
            derogation_types: data.derogation_types ?? [],
            has_bcr: data.has_bcr ?? null,
            has_public_incident_notification: data.has_public_incident_notification_gdpr ?? null,
          },
          nis2_data: {
            sectors: data.nis2_sectors ?? [],
            entity_type: data.nis2_entity_type || null,
            has_mfa: data.has_mfa ?? null,
            has_incident_response_plan: data.has_incident_response_plan ?? null,
            has_business_continuity_plan: data.has_business_continuity_plan ?? null,
            assesses_supply_chain: data.assesses_supply_chain ?? null,
            has_vulnerability_disclosure_policy: data.has_vulnerability_disclosure_policy ?? null,
            management_approved_security_measures: data.management_approved_security_measures ?? null,
            has_cyber_awareness_training: data.has_cyber_awareness_training ?? null,
            uses_encryption: data.uses_encryption ?? null,
            has_asset_inventory: data.has_asset_inventory ?? null,
            participates_in_info_sharing: data.participates_in_info_sharing ?? null,
            uses_certified_products: data.uses_certified_products ?? null,
            nis2_registration_complete: data.nis2_registration_complete ?? null,
            has_public_incident_notification: data.has_public_incident_notification_nis2 ?? null,
          },
          ai_act_data: {
            uses_ai: data.uses_ai,
            ai_role: data.ai_role || null,
            high_risk_ai_categories: data.high_risk_ai_categories ?? [],
            uses_gpai: data.uses_gpai ?? null,
            has_ai_governance_policy: data.has_ai_governance_policy ?? null,
            has_ai_literacy_training: data.has_ai_literacy_training ?? null,
            is_public_body: data.is_public_body ?? null,
            uses_chatbot: data.uses_chatbot ?? null,
            uses_synthetic_content: data.uses_synthetic_content ?? null,
            uses_emotion_recognition: data.uses_emotion_recognition ?? null,
            has_ai_complaint_process: data.has_ai_complaint_process ?? null,
            has_ai_explanation_process: data.has_ai_explanation_process ?? null,
            prohibited_practice_flags: data.prohibited_practice_flags ?? [],
            gpai_flops_above_threshold: data.gpai_flops_above_threshold ?? null,
            has_gpai_eu_representative: data.has_gpai_eu_representative ?? null,
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
          `Step ${incompleteStep} has required fields missing. Taking you back to complete it.`
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
      {serverError && <p className={styles.error}>{serverError}</p>}
      {renderNavigation()}
    </form>
  );
}
