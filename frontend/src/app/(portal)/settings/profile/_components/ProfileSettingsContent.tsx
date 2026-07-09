"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { clientApiFetch } from "@/lib/clientApi";

// ── Constants ─────────────────────────────────────────────

const GDPR_LAWFUL_BASES = [
  { value: "consent", label: "Consent" },
  { value: "contract", label: "Contract" },
  { value: "legal_obligation", label: "Legal Obligation" },
  { value: "vital_interests", label: "Vital Interests" },
  { value: "public_task", label: "Public Task" },
  { value: "legitimate_interests", label: "Legitimate Interest" },
];

const GDPR_TRANSFER_MECHANISMS = [
  { value: "adequacy_decision", label: "Adequacy Decision" },
  { value: "sccs", label: "Standard Contractual Clauses (SCCs)" },
  { value: "bcrs", label: "Binding Corporate Rules (BCRs)" },
  { value: "derogations", label: "Derogations (Art. 49)" },
];

const NIS2_SECTORS = [
  { value: "energy", label: "Energy" },
  { value: "transport", label: "Transport" },
  { value: "banking", label: "Banking" },
  { value: "financial_markets", label: "Financial Markets" },
  { value: "health", label: "Health" },
  { value: "water", label: "Water" },
  { value: "digital_infrastructure", label: "Digital Infrastructure" },
  { value: "managed_services", label: "Managed Services (ICT)" },
  { value: "public_administration", label: "Public Administration" },
  { value: "space", label: "Space" },
  { value: "not_applicable", label: "Not in scope" },
];

const NIS2_ENTITY_TYPES = [
  { value: "essential", label: "Essential Entity" },
  { value: "important", label: "Important Entity" },
  { value: "unsure", label: "Unsure" },
  { value: "not_applicable", label: "Not applicable" },
];

const AI_ROLES = [
  { value: "provider", label: "Provider (places AI on market)" },
  { value: "deployer", label: "Deployer (uses AI in operations)" },
  { value: "both", label: "Both provider and deployer" },
  { value: "neither", label: "Neither" },
];

const HIGH_RISK_CATEGORIES = [
  { value: "biometric", label: "Biometric identification" },
  { value: "critical_infrastructure", label: "Critical infrastructure" },
  { value: "education", label: "Education / vocational training" },
  { value: "employment", label: "Employment / HR management" },
  { value: "essential_services", label: "Essential private/public services" },
  { value: "law_enforcement", label: "Law enforcement" },
  { value: "migration", label: "Migration / asylum / border control" },
  { value: "justice", label: "Administration of justice" },
  { value: "none", label: "None of the above" },
];

// ── Styles ────────────────────────────────────────────────

const styles = {
  page: "min-h-screen bg-[#F8FAFC]",
  stickyBar:
    "sticky top-0 z-10 bg-white border-b border-[#E2E8F0] px-6 py-3 flex items-center justify-between",
  pageTitle: "text-base font-bold text-[#0F172A]",
  saveBtn:
    "px-4 py-2 text-sm font-semibold bg-[#D97706] hover:bg-[#B45309] text-white rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2",
  saveBtnSaving: "opacity-70 cursor-not-allowed",
  spinner: "w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin",
  content: "max-w-3xl mx-auto px-6 py-8 space-y-4",
  errorBox: "bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-700",
  successBox: "bg-green-50 border border-green-200 rounded-xl px-4 py-3 text-sm text-green-700",
  accordion: "bg-white rounded-xl border border-[#E2E8F0] shadow-sm overflow-hidden",
  accordionHeader:
    "w-full flex items-center justify-between px-5 py-4 text-left hover:bg-gray-50 transition-colors",
  accordionTitle: "text-sm font-bold text-[#0F172A] flex items-center gap-2",
  accordionDot: "w-3 h-3 rounded-full flex-shrink-0",
  chevron: "w-4 h-4 text-[#94A3B8] transition-transform",
  chevronOpen: "rotate-180",
  accordionBody: "px-5 pb-5 pt-1 space-y-5 border-t border-[#F1F5F9]",
  fieldGroup: "space-y-2",
  fieldLabel: "text-xs font-semibold text-[#334155] uppercase tracking-wide",
  fieldSub: "text-xs text-[#94A3B8] mt-0.5",
  toggleRow: "flex gap-2",
  toggleBtn:
    "px-4 py-2 text-sm font-medium rounded-lg border transition-colors flex-1 text-center",
  toggleActive: "bg-[#D97706] border-[#D97706] text-white",
  toggleInactive: "bg-white border-[#E2E8F0] text-[#334155] hover:border-[#D97706]",
  checkGrid: "grid grid-cols-2 gap-2",
  checkCard:
    "flex items-center gap-2.5 px-3 py-2.5 rounded-lg border cursor-pointer transition-colors text-sm",
  checkCardActive: "border-[#D97706] bg-amber-50 text-[#0F172A]",
  checkCardInactive: "border-[#E2E8F0] bg-white text-[#334155] hover:border-[#D97706]",
  checkBox:
    "w-4 h-4 rounded border-2 flex-shrink-0 flex items-center justify-center",
  checkBoxActive: "bg-[#D97706] border-[#D97706]",
  checkBoxInactive: "border-[#CBD5E1]",
  radioGrid: "grid grid-cols-2 gap-2",
  radioCard:
    "flex items-center gap-2.5 px-3 py-2.5 rounded-lg border cursor-pointer transition-colors text-sm",
  radioCardActive: "border-[#D97706] bg-amber-50 text-[#0F172A]",
  radioCardInactive: "border-[#E2E8F0] bg-white text-[#334155] hover:border-[#D97706]",
  radioCircle: "w-4 h-4 rounded-full border-2 flex-shrink-0",
  radioCircleActive: "border-[#D97706] bg-[#D97706]",
  radioCircleInactive: "border-[#CBD5E1]",
  indent: "pl-4 border-l-2 border-[#F1F5F9] space-y-4 mt-2",
  skeleton: "bg-[#F1F5F9] rounded animate-pulse",
  skeletonLine: "h-4 rounded",
  loadingWrapper: "max-w-3xl mx-auto px-6 py-8 space-y-4",
};

// ── Types ──────────────────────────────────────────────────

type SectionKey = "gdpr" | "nis2" | "ai_act";

interface ProfileData {
  gdpr_data: Record<string, unknown>;
  nis2_data: Record<string, unknown>;
  ai_act_data: Record<string, unknown>;
}

// ── Helpers ────────────────────────────────────────────────

const getTimeOfDay = (): string => {
  const h = new Date().getHours();
  return h < 12 ? "morning" : h < 17 ? "afternoon" : "evening";
};

const getBool = (data: Record<string, unknown>, key: string): boolean =>
  data[key] === true;

const getArr = (data: Record<string, unknown>, key: string): string[] => {
  const v = data[key];
  return Array.isArray(v) ? (v as string[]) : [];
};

const getString = (data: Record<string, unknown>, key: string): string => {
  const v = data[key];
  return typeof v === "string" ? v : "";
};

// ── Sub-components ────────────────────────────────────────

const YesNoToggle = ({
  value,
  onChange,
}: {
  value: boolean;
  onChange: (v: boolean) => void;
}) => (
  <div className={styles.toggleRow}>
    <button
      type="button"
      className={`${styles.toggleBtn} ${value ? styles.toggleActive : styles.toggleInactive}`}
      onClick={() => onChange(true)}
    >
      Yes
    </button>
    <button
      type="button"
      className={`${styles.toggleBtn} ${!value ? styles.toggleActive : styles.toggleInactive}`}
      onClick={() => onChange(false)}
    >
      No
    </button>
  </div>
);

const CheckboxGroup = ({
  options,
  values,
  onChange,
}: {
  options: { value: string; label: string }[];
  values: string[];
  onChange: (v: string[]) => void;
}) => {
  const handleToggle = (val: string) => {
    if (values.includes(val)) {
      onChange(values.filter((v) => v !== val));
    } else {
      onChange([...values, val]);
    }
  };

  return (
    <div className={styles.checkGrid}>
      {options.map((opt) => {
        const checked = values.includes(opt.value);
        return (
          <button
            key={opt.value}
            type="button"
            className={`${styles.checkCard} ${checked ? styles.checkCardActive : styles.checkCardInactive}`}
            onClick={() => handleToggle(opt.value)}
          >
            <div
              className={`${styles.checkBox} ${checked ? styles.checkBoxActive : styles.checkBoxInactive}`}
            >
              {checked && (
                <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 12 12">
                  <path d="M10 3L5 8.5 2 5.5" stroke="white" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              )}
            </div>
            <span>{opt.label}</span>
          </button>
        );
      })}
    </div>
  );
};

const RadioGroup = ({
  options,
  value,
  onChange,
}: {
  options: { value: string; label: string }[];
  value: string;
  onChange: (v: string) => void;
}) => (
  <div className={styles.radioGrid}>
    {options.map((opt) => {
      const selected = value === opt.value;
      return (
        <button
          key={opt.value}
          type="button"
          className={`${styles.radioCard} ${selected ? styles.radioCardActive : styles.radioCardInactive}`}
          onClick={() => onChange(opt.value)}
        >
          <div
            className={`${styles.radioCircle} ${selected ? styles.radioCircleActive : styles.radioCircleInactive}`}
          />
          <span>{opt.label}</span>
        </button>
      );
    })}
  </div>
);

const SkeletonLoader = () => (
  <div className={styles.loadingWrapper}>
    {[1, 2, 3].map((i) => (
      <div key={i} className={`${styles.accordion}`}>
        <div className={styles.accordionHeader}>
          <div className={`${styles.skeleton} ${styles.skeletonLine} w-32`} />
        </div>
      </div>
    ))}
  </div>
);

// ── Component ─────────────────────────────────────────────

export const ProfileSettingsContent = () => {
  // ── State ─────────────────────────────────────────────

  const [profileData, setProfileData] = useState<ProfileData>({
    gdpr_data: {},
    nis2_data: {},
    ai_act_data: {},
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [openSection, setOpenSection] = useState<SectionKey | null>("gdpr");

  const { getToken } = useAuth();
  const router = useRouter();

  // ── Hooks ─────────────────────────────────────────────

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = await getToken();
        if (!token) return;
        const res = await clientApiFetch("/api/v1/profile", token);
        if (!res.ok) throw new Error("Failed to load profile");
        const data = await res.json();
        setProfileData({
          gdpr_data: (data.gdpr_data as Record<string, unknown>) ?? {},
          nis2_data: (data.nis2_data as Record<string, unknown>) ?? {},
          ai_act_data: (data.ai_act_data as Record<string, unknown>) ?? {},
        });
      } catch {
        setError("Could not load your profile. Try refreshing.");
      } finally {
        setLoading(false);
      }
    };
    void fetchProfile();
  }, [getToken]);

  // ── Handlers ─────────────────────────────────────────

  const handleToggleSection = (key: SectionKey) => {
    setOpenSection((prev) => (prev === key ? null : key));
  };

  const handleGdprField = (field: string, value: unknown) => {
    setProfileData((prev) => ({
      ...prev,
      gdpr_data: { ...prev.gdpr_data, [field]: value },
    }));
  };

  const handleNis2Field = (field: string, value: unknown) => {
    setProfileData((prev) => ({
      ...prev,
      nis2_data: { ...prev.nis2_data, [field]: value },
    }));
  };

  const handleAiField = (field: string, value: unknown) => {
    setProfileData((prev) => ({
      ...prev,
      ai_act_data: { ...prev.ai_act_data, [field]: value },
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");

      const patchRes = await clientApiFetch("/api/v1/profile", token, {
        method: "PATCH",
        body: JSON.stringify({
          gdpr_data: profileData.gdpr_data,
          nis2_data: profileData.nis2_data,
          ai_act_data: profileData.ai_act_data,
        }),
      });
      if (!patchRes.ok) throw new Error("Failed to save profile");

      await Promise.allSettled([
        clientApiFetch("/api/v1/assessments", token, {
          method: "POST",
          body: JSON.stringify({ regulation: "GDPR" }),
        }),
        clientApiFetch("/api/v1/assessments", token, {
          method: "POST",
          body: JSON.stringify({ regulation: "NIS2" }),
        }),
        clientApiFetch("/api/v1/assessments", token, {
          method: "POST",
          body: JSON.stringify({ regulation: "EU_AI_ACT" }),
        }),
      ]);

      setSuccess(true);
      setTimeout(() => router.push("/dashboard"), 2000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  // ── Render helpers ────────────────────────────────────

  const renderAccordionHeader = (
    key: SectionKey,
    label: string,
    color: string
  ) => (
    <button
      type="button"
      className={styles.accordionHeader}
      onClick={() => handleToggleSection(key)}
    >
      <span className={styles.accordionTitle}>
        <span
          className={styles.accordionDot}
          style={{ backgroundColor: color }}
        />
        {label}
      </span>
      <svg
        className={`${styles.chevron} ${openSection === key ? styles.chevronOpen : ""}`}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    </button>
  );

  const renderGdprSection = () => {
    const g = profileData.gdpr_data;
    const transfersEea = getBool(g, "transfers_outside_eea");
    const usesAutomated = getBool(g, "uses_automated_decisions");

    return (
      <div className={styles.accordion}>
        {renderAccordionHeader("gdpr", "GDPR Data Protection", "#7C3AED")}
        {openSection === "gdpr" && (
          <div className={styles.accordionBody}>
            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Lawful Bases for Processing</p>
              <p className={styles.fieldSub}>Select all that apply to your organisation</p>
              <CheckboxGroup
                options={GDPR_LAWFUL_BASES}
                values={getArr(g, "lawful_bases")}
                onChange={(v) => handleGdprField("lawful_bases", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Processes Children&apos;s Data</p>
              <YesNoToggle
                value={getBool(g, "processes_children_data")}
                onChange={(v) => handleGdprField("processes_children_data", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Transfers Data Outside the EEA</p>
              <YesNoToggle
                value={transfersEea}
                onChange={(v) => handleGdprField("transfers_outside_eea", v)}
              />
              {transfersEea && (
                <div className={styles.indent}>
                  <p className={styles.fieldLabel}>Transfer Mechanisms Used</p>
                  <CheckboxGroup
                    options={GDPR_TRANSFER_MECHANISMS}
                    values={getArr(g, "transfer_mechanisms")}
                    onChange={(v) => handleGdprField("transfer_mechanisms", v)}
                  />
                </div>
              )}
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Uses Data Processors</p>
              <YesNoToggle
                value={getBool(g, "uses_data_processors")}
                onChange={(v) => handleGdprField("uses_data_processors", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Has Breach Notification Procedure</p>
              <YesNoToggle
                value={getBool(g, "has_breach_procedure")}
                onChange={(v) => handleGdprField("has_breach_procedure", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Has DPIA Process</p>
              <YesNoToggle
                value={getBool(g, "has_dpia")}
                onChange={(v) => handleGdprField("has_dpia", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Uses Automated Decision-Making</p>
              <YesNoToggle
                value={usesAutomated}
                onChange={(v) => handleGdprField("uses_automated_decisions", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Has Erasure (Right to be Forgotten) Process</p>
              <YesNoToggle
                value={getBool(g, "has_erasure_process")}
                onChange={(v) => handleGdprField("has_erasure_process", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Has Data Portability Process</p>
              <YesNoToggle
                value={getBool(g, "has_portability_process")}
                onChange={(v) => handleGdprField("has_portability_process", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Has Marketing Objection Process</p>
              <YesNoToggle
                value={getBool(g, "has_marketing_objection_process")}
                onChange={(v) => handleGdprField("has_marketing_objection_process", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Has Joint Controllers Arrangement</p>
              <YesNoToggle
                value={getBool(g, "has_joint_controllers")}
                onChange={(v) => handleGdprField("has_joint_controllers", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Is a Public Authority or Body</p>
              <YesNoToggle
                value={getBool(g, "is_public_authority")}
                onChange={(v) => handleGdprField("is_public_authority", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Processes Employee / HR Data</p>
              <YesNoToggle
                value={getBool(g, "processes_employee_data")}
                onChange={(v) => handleGdprField("processes_employee_data", v)}
              />
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderNis2Section = () => {
    const n = profileData.nis2_data;

    return (
      <div className={styles.accordion}>
        {renderAccordionHeader("nis2", "NIS2 Network & Information Security", "#0891B2")}
        {openSection === "nis2" && (
          <div className={styles.accordionBody}>
            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Applicable Sectors</p>
              <p className={styles.fieldSub}>Select all sectors your organisation operates in</p>
              <CheckboxGroup
                options={NIS2_SECTORS}
                values={getArr(n, "sectors")}
                onChange={(v) => handleNis2Field("sectors", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Entity Type</p>
              <RadioGroup
                options={NIS2_ENTITY_TYPES}
                value={getString(n, "entity_type")}
                onChange={(v) => handleNis2Field("entity_type", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Has Multi-Factor Authentication (MFA)</p>
              <YesNoToggle
                value={getBool(n, "has_mfa")}
                onChange={(v) => handleNis2Field("has_mfa", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Has Incident Response Plan</p>
              <YesNoToggle
                value={getBool(n, "has_incident_response_plan")}
                onChange={(v) => handleNis2Field("has_incident_response_plan", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Has Business Continuity Plan</p>
              <YesNoToggle
                value={getBool(n, "has_business_continuity_plan")}
                onChange={(v) => handleNis2Field("has_business_continuity_plan", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Assesses Supply Chain Risks</p>
              <YesNoToggle
                value={getBool(n, "assesses_supply_chain")}
                onChange={(v) => handleNis2Field("assesses_supply_chain", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Has Vulnerability Disclosure Policy</p>
              <YesNoToggle
                value={getBool(n, "has_vulnerability_disclosure_policy")}
                onChange={(v) => handleNis2Field("has_vulnerability_disclosure_policy", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Management Has Approved Security Measures</p>
              <YesNoToggle
                value={getBool(n, "management_approved_security_measures")}
                onChange={(v) => handleNis2Field("management_approved_security_measures", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Has Cyber Awareness Training</p>
              <YesNoToggle
                value={getBool(n, "has_cyber_awareness_training")}
                onChange={(v) => handleNis2Field("has_cyber_awareness_training", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Uses Encryption</p>
              <YesNoToggle
                value={getBool(n, "uses_encryption")}
                onChange={(v) => handleNis2Field("uses_encryption", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Has Asset Inventory</p>
              <YesNoToggle
                value={getBool(n, "has_asset_inventory")}
                onChange={(v) => handleNis2Field("has_asset_inventory", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Participates in Information Sharing Arrangements</p>
              <YesNoToggle
                value={getBool(n, "participates_in_info_sharing")}
                onChange={(v) => handleNis2Field("participates_in_info_sharing", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Uses Certified Products / Services</p>
              <YesNoToggle
                value={getBool(n, "uses_certified_products")}
                onChange={(v) => handleNis2Field("uses_certified_products", v)}
              />
            </div>

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>NIS2 Registration Complete</p>
              <YesNoToggle
                value={getBool(n, "nis2_registration_complete")}
                onChange={(v) => handleNis2Field("nis2_registration_complete", v)}
              />
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderAiSection = () => {
    const a = profileData.ai_act_data;
    const usesAi = getBool(a, "uses_ai");
    const usesGpai = getBool(a, "uses_gpai");
    const gpaiFlops = getBool(a, "gpai_flops_above_threshold");
    const aiRole = getString(a, "ai_role");

    return (
      <div className={styles.accordion}>
        {renderAccordionHeader("ai_act", "EU AI Act", "#BE185D")}
        {openSection === "ai_act" && (
          <div className={styles.accordionBody}>
            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Uses AI Systems</p>
              <YesNoToggle
                value={usesAi}
                onChange={(v) => handleAiField("uses_ai", v)}
              />
            </div>

            {usesAi && (
              <>
                <div className={styles.fieldGroup}>
                  <p className={styles.fieldLabel}>AI Role</p>
                  <RadioGroup
                    options={AI_ROLES}
                    value={aiRole}
                    onChange={(v) => handleAiField("ai_role", v)}
                  />
                </div>

                <div className={styles.fieldGroup}>
                  <p className={styles.fieldLabel}>High-Risk AI Categories</p>
                  <p className={styles.fieldSub}>Select all that apply</p>
                  <CheckboxGroup
                    options={HIGH_RISK_CATEGORIES}
                    values={getArr(a, "high_risk_ai_categories")}
                    onChange={(v) => handleAiField("high_risk_ai_categories", v)}
                  />
                </div>

                <div className={styles.fieldGroup}>
                  <p className={styles.fieldLabel}>Uses General Purpose AI (GPAI) Models</p>
                  <YesNoToggle
                    value={usesGpai}
                    onChange={(v) => handleAiField("uses_gpai", v)}
                  />
                  {usesGpai && (
                    <div className={styles.indent}>
                      <div className={styles.fieldGroup}>
                        <p className={styles.fieldLabel}>GPAI FLOPs Above 10^25 Threshold</p>
                        <YesNoToggle
                          value={gpaiFlops}
                          onChange={(v) => handleAiField("gpai_flops_above_threshold", v)}
                        />
                      </div>
                      {gpaiFlops && aiRole === "provider" && (
                        <div className={styles.fieldGroup}>
                          <p className={styles.fieldLabel}>Has EU Representative for GPAI</p>
                          <YesNoToggle
                            value={getBool(a, "has_gpai_eu_representative")}
                            onChange={(v) => handleAiField("has_gpai_eu_representative", v)}
                          />
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className={styles.fieldGroup}>
                  <p className={styles.fieldLabel}>Has AI Governance Policy</p>
                  <YesNoToggle
                    value={getBool(a, "has_ai_governance_policy")}
                    onChange={(v) => handleAiField("has_ai_governance_policy", v)}
                  />
                </div>

                <div className={styles.fieldGroup}>
                  <p className={styles.fieldLabel}>Has AI Literacy Training Program</p>
                  <YesNoToggle
                    value={getBool(a, "has_ai_literacy_training")}
                    onChange={(v) => handleAiField("has_ai_literacy_training", v)}
                  />
                </div>

                <div className={styles.fieldGroup}>
                  <p className={styles.fieldLabel}>Uses Chatbot / Conversational AI</p>
                  <YesNoToggle
                    value={getBool(a, "uses_chatbot")}
                    onChange={(v) => handleAiField("uses_chatbot", v)}
                  />
                </div>

                <div className={styles.fieldGroup}>
                  <p className={styles.fieldLabel}>Uses Synthetic Content Generation</p>
                  <YesNoToggle
                    value={getBool(a, "uses_synthetic_content")}
                    onChange={(v) => handleAiField("uses_synthetic_content", v)}
                  />
                </div>

                <div className={styles.fieldGroup}>
                  <p className={styles.fieldLabel}>Uses Emotion Recognition</p>
                  <YesNoToggle
                    value={getBool(a, "uses_emotion_recognition")}
                    onChange={(v) => handleAiField("uses_emotion_recognition", v)}
                  />
                </div>

                <div className={styles.fieldGroup}>
                  <p className={styles.fieldLabel}>Has AI Complaint Handling Process</p>
                  <YesNoToggle
                    value={getBool(a, "has_ai_complaint_process")}
                    onChange={(v) => handleAiField("has_ai_complaint_process", v)}
                  />
                </div>

                <div className={styles.fieldGroup}>
                  <p className={styles.fieldLabel}>Has AI Explanation Process for Affected Persons</p>
                  <YesNoToggle
                    value={getBool(a, "has_ai_explanation_process")}
                    onChange={(v) => handleAiField("has_ai_explanation_process", v)}
                  />
                </div>
              </>
            )}

            <div className={styles.fieldGroup}>
              <p className={styles.fieldLabel}>Is a Public Body Providing Public Services</p>
              <YesNoToggle
                value={getBool(a, "is_public_body")}
                onChange={(v) => handleAiField("is_public_body", v)}
              />
            </div>
          </div>
        )}
      </div>
    );
  };

  // ── Render ────────────────────────────────────────────

  if (loading) {
    return (
      <div className={styles.page}>
        <div className={styles.stickyBar}>
          <span className={styles.pageTitle}>Profile Settings</span>
        </div>
        <SkeletonLoader />
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.stickyBar}>
        <span className={styles.pageTitle}>
          Good {getTimeOfDay()} — update your compliance profile
        </span>
        <button
          type="button"
          className={`${styles.saveBtn} ${saving ? styles.saveBtnSaving : ""}`}
          onClick={handleSave}
          disabled={saving}
        >
          {saving && <span className={styles.spinner} />}
          {saving ? "Saving..." : "Save & Recalculate"}
        </button>
      </div>

      <div className={styles.content}>
        {error && <div className={styles.errorBox}>{error}</div>}
        {success && (
          <div className={styles.successBox}>
            Saved. Your compliance scores are recalculating. Redirecting to dashboard...
          </div>
        )}

        {renderGdprSection()}
        {renderNis2Section()}
        {renderAiSection()}
      </div>
    </div>
  );
};
