"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Modal } from "@/components/ui/Modal";
import { GapResolveButton } from "./GapResolveButton";
import { useGaps } from "@/lib/hooks/useGaps";
import type { Gap, RegulationName } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const SEVERITY_CONFIG = {
  critical: { label: "Critical severity", bg: "bg-red-50", text: "text-red-800", border: "border-red-200" },
  high: { label: "High severity", bg: "bg-orange-50", text: "text-orange-800", border: "border-orange-200" },
  medium: { label: "Medium severity", bg: "bg-amber-50", text: "text-amber-800", border: "border-amber-200" },
  low: { label: "Low severity", bg: "bg-blue-50", text: "text-blue-800", border: "border-blue-200" },
};

const STATUS_DOT: Record<string, string> = {
  unknown: "bg-gray-400",
  not_met: "bg-red-500",
  partial: "bg-amber-500",
  met: "bg-green-500",
  not_applicable: "bg-gray-300",
};

const STATUS_LABEL: Record<string, string> = {
  unknown: "Needs review",
  not_met: "Not met",
  partial: "Partially addressed",
  met: "Requirement met",
  not_applicable: "Not applicable",
};

const COUNTRY_NAMES: Record<string, string> = {
  DE: "Germany", FR: "France", NL: "Netherlands", IE: "Ireland",
  ES: "Spain", IT: "Italy", PL: "Poland", SE: "Sweden", AT: "Austria",
  BE: "Belgium", DK: "Denmark", FI: "Finland", PT: "Portugal",
  GB: "United Kingdom", US: "United States", CA: "Canada",
};

const UNKNOWN_REASON_MAP: Record<string, string> = {
  // Generic check-type reasons
  cannot_evaluate_policy_required_without_additional_data:
    "This article requires a written policy or documented process. We can't verify that automatically. Work through the steps below and mark it resolved once your documentation is in place.",
  cannot_evaluate_document_required_without_additional_data:
    "This article requires specific documentation (such as a technical file or assessment report) that we can't verify from your profile alone. Complete the steps below and mark it resolved.",
  cannot_evaluate_technical_without_additional_data:
    "This article requires specific technical measures that we can't verify from your profile. Review the steps below to confirm you have them in place.",
  // GDPR-specific reasons
  consent_mechanism_requires_verification:
    "Your profile indicates you rely on consent as a lawful basis, but we can't automatically verify your consent mechanism meets GDPR Art. 7 requirements. Check your consent flows and mark resolved once confirmed.",
  age_verification_requires_technical_check:
    "Processing data of children requires age verification or parental consent mechanisms that need a technical audit to verify. Review your sign-up and data collection flows.",
  explicit_consent_or_exemption_requires_verification:
    "Processing special-category data requires explicit consent or another Art. 9(2) exemption that we can't automatically verify. Confirm you have the correct legal basis documented.",
  legal_authority_requires_verification:
    "Processing under legal obligation or official authority requires verification of the specific legal basis. Confirm and document the applicable law or regulatory mandate.",
  portability_mechanism_requires_technical_verification:
    "Providing data portability (Art. 20) requires a technical export mechanism that we can't verify from your profile. Confirm you can export personal data in a machine-readable format.",
  human_oversight_mechanism_requires_verification:
    "Automated decision-making requires a human oversight or review mechanism that needs a technical review to verify. Confirm your process for allowing individuals to contest automated decisions.",
  joint_controller_arrangement_requires_verification:
    "Joint controller arrangements require a written agreement defining responsibilities that we can't verify automatically. Confirm your joint controller agreement is in place and accessible to data subjects.",
  dpa_existence_requires_verification:
    "Data processing agreements with processors must exist but can't be automatically verified. Confirm your DPAs are signed and cover all required Art. 28 clauses.",
  dpo_mandatory_assessment_requires_verification:
    "Whether a DPO is mandatory depends on your specific processing activities and requires a detailed assessment. Review the Art. 37 criteria and confirm your determination is documented.",
  eu_representative_appointment_requires_verification:
    "Appointing an EU representative (Art. 27) or authorised representative under the AI Act requires confirmation that we can't automate. Verify your representative appointment is documented.",
  third_party_register_requires_verification:
    "Maintaining a register of third-party disclosures and legal authority requests requires verification that the register exists and is current.",
  national_employment_law_obligations_require_verification:
    "Employee data processing under Art. 88 is governed by national employment law that varies by country. Confirm your employee data processing complies with the applicable national rules.",
  research_safeguards_require_verification:
    "Research and statistical processing requires specific safeguards (pseudonymisation, access controls, etc.) that need a technical review to verify.",
  // NIS2-specific reasons
  insufficient_data_to_evaluate:
    "Not enough information in your profile to evaluate this requirement. Complete the relevant sections of your company profile and re-run the assessment.",
  nis2_registration_requires_verification:
    "NIS2 Art. 27 requires entities to register with their national authority. We can't verify registration automatically. Confirm your registration status with the relevant authority.",
  // AI Act-specific reasons
  prohibited_practices_require_ai_system_audit:
    "Verifying compliance with prohibited AI practices requires a detailed review of your AI systems that we can't automate. Review each prohibited practice in the steps below.",
  gpai_usage_not_answered:
    "You haven't indicated whether you use or provide general-purpose AI models. Update your profile under AI Act data to enable accurate assessment.",
  public_body_high_risk_obligations_require_verification:
    "Public bodies deploying high-risk AI systems have specific obligations that require a detailed review of each system's use case and impact assessment.",
  deployer_obligations_require_verification:
    "AI deployer obligations for high-risk systems require verification of your human oversight, record-keeping, and incident monitoring processes.",
  transparency_disclosure_implementation_requires_verification:
    "AI transparency obligations (chatbots, synthetic content, emotion recognition) require technical verification of your disclosure mechanisms.",
  gpai_systemic_risk_requires_compute_verification:
    "Determining whether your GPAI model poses systemic risk requires verification of training compute above the 10^25 FLOPs threshold.",
  gpai_eu_representative_not_answered:
    "You haven't confirmed whether you have an EU representative for your GPAI model. Update your AI Act profile data to enable accurate assessment.",
  // Fallback
  evaluation_logic_not_yet_implemented:
    "Assessment logic for this article is not yet implemented. Work through the remediation steps below and mark it resolved once you've confirmed compliance.",
};

const buildStatusSentence = (gap: Gap): string => {
  const ev = gap.evidence ?? {};
  const status = gap.status;

  if (status === "met") {
    const parts: string[] = [];
    if (ev.primary_jurisdiction) {
      const country = COUNTRY_NAMES[ev.primary_jurisdiction as string] ?? ev.primary_jurisdiction;
      parts.push(`your primary jurisdiction is set to ${country}`);
    }
    if (Array.isArray(ev.lawful_bases) && ev.lawful_bases.length > 0) {
      const bases = (ev.lawful_bases as string[]).map((b) => b.replace(/_/g, " ")).join(", ");
      parts.push(`your company has identified ${bases} as lawful basis for processing`);
    }
    if (ev.uses_ai === true && ev.ai_role) {
      parts.push(`your company is registered as an AI ${ev.ai_role} and confirmed it uses AI systems`);
    }
    if (Array.isArray(ev.high_risk_ai_categories) && ev.high_risk_ai_categories.length > 0) {
      const cats = (ev.high_risk_ai_categories as string[]).map((c) => c.replace(/_/g, " ")).join(", ");
      parts.push(`your company uses AI in high-risk categories: ${cats}`);
    }
    if (ev.has_dpo === true) parts.push("your company has appointed a Data Protection Officer");
    if (ev.has_ropa === true) parts.push("your company maintains a Record of Processing Activities");
    if (ev.transfers_outside_eea === false) parts.push("your company does not transfer personal data outside the EEA");

    return parts.length > 0
      ? `Requirement met because ${parts.join(", and ")}.`
      : "This requirement is satisfied based on your current company profile.";
  }

  if (status === "not_met") {
    if (ev.has_breach_procedure === false)
      return "Your profile indicates you don't have a breach notification procedure in place yet. This is required under GDPR Art. 33/34.";
    if (ev.has_dpia === false)
      return "Your profile indicates you haven't completed a Data Protection Impact Assessment (DPIA) yet. This is required for high-risk processing activities.";
    if (ev.has_ropa === false)
      return "Your profile indicates you don't maintain a Record of Processing Activities (RoPA) yet. All organisations processing personal data must keep one.";
    if (ev.has_dpo === false)
      return "Based on your profile, your organisation may require a Data Protection Officer but hasn't appointed one.";
    return gap.remediation_hint ?? "Based on your company profile, this requirement is not currently in place.";
  }

  if (status === "partial") {
    return gap.remediation_hint ?? "You've partially addressed this requirement but gaps remain. Review the steps below to complete it.";
  }

  if (status === "unknown") {
    const reason = (ev.reason as string) ?? "";
    return UNKNOWN_REASON_MAP[reason] ?? "We can't automatically verify this from your profile alone. Work through the steps below and mark it resolved once done.";
  }

  return "This article does not apply to your organisation based on your profile.";
};

const FINE_EXPOSURE = {
  tier_2: "Up to €20M or 4% of global annual turnover",
  tier_1: "Up to €10M or 2% of global annual turnover",
};

const POLICY_TYPE_LABEL: Record<string, string> = {
  GDPR: "Data Processing Policy",
  NIS2: "Information Security Policy",
  EU_AI_ACT: "AI Governance Policy",
};

// ── Types ─────────────────────────────────────────────────

interface GapDetailModalProps {
  gapId: string | null;
  assessmentId: string;
  regulation: RegulationName;
  isOpen: boolean;
  onClose: () => void;
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  artLabel: "text-[11px] font-medium text-[#94A3B8] uppercase tracking-[0.06em] mb-1",
  title: "text-[17px] font-medium text-[#0F172A] leading-snug",
  badges: "flex gap-2 flex-wrap",
  badge: "text-[11px] font-medium px-2.5 py-0.5 rounded-full border",
  sectionLabel: "text-[11px] font-medium text-[#94A3B8] uppercase tracking-[0.06em] mb-2",
  plainBox: "bg-[#EFF6FF] border border-[#BFDBFE] rounded-[10px] px-3.5 py-3 text-sm text-[#1E3A5F] leading-relaxed",
  statusBox: "bg-[#F8FAFC] border border-[#E2E8F0] rounded-[10px] px-4 py-3.5",
  statusRow: "flex items-center gap-2 mb-2",
  statusDot: "w-2 h-2 rounded-full flex-shrink-0",
  statusLabel: "text-xs font-medium text-[#475569]",
  statusBody: "text-[13px] text-[#64748B] leading-relaxed",
  fineBox: "bg-[#FEF2F2] border border-[#FECACA] rounded-[10px] px-3.5 py-3 flex items-center gap-2.5",
  fineIcon: "text-[#DC2626] flex-shrink-0",
  fineInner: "",
  fineLabel: "text-[11px] font-medium text-[#DC2626] uppercase tracking-[0.06em] mb-0.5",
  fineText: "text-[13px] text-[#DC2626]",
  steps: "flex flex-col gap-2.5",
  step: "flex gap-3 items-start",
  stepNum: "w-[22px] h-[22px] rounded-full bg-[#0F2044] text-white text-[11px] font-medium flex items-center justify-center flex-shrink-0 mt-0.5",
  stepText: "text-[13px] text-[#334155] leading-[1.55]",
  policyBox: "bg-[#F8FAFC] border border-[#E2E8F0] rounded-[10px] px-4 py-3.5 flex gap-3 items-start",
  policyIcon: "w-[34px] h-[34px] rounded-lg bg-[#EFF6FF] flex items-center justify-center flex-shrink-0",
  policyTitle: "text-[13px] font-medium text-[#0F172A] mb-0.5",
  policyBody: "text-xs text-[#64748B] leading-relaxed mb-2.5",
  policyBtn: "text-xs font-medium text-[#1D4ED8] border border-[#BFDBFE] rounded-md px-3 py-1.5 bg-transparent hover:bg-[#EFF6FF] transition-colors cursor-pointer",
  resolveSection: "border-t border-[#F1F5F9] pt-4 flex flex-col gap-2.5",
  loadingWrapper: "py-8 text-center text-sm text-[#94A3B8]",
  notFoundWrapper: "py-8 text-center text-sm text-[#94A3B8]",
};

// ── Component ─────────────────────────────────────────────

export const GapDetailModal = ({ gapId, assessmentId, regulation, isOpen, onClose }: GapDetailModalProps) => {
  const router = useRouter();
  const [notes, setNotes] = useState("");

  const { data, isLoading } = useGaps(isOpen ? assessmentId : null);
  const gap: Gap | null = data?.gaps.find((g) => g.gap_id === gapId) ?? null;

  const severityCfg = SEVERITY_CONFIG[gap?.severity ?? "medium"] ?? SEVERITY_CONFIG.medium;
  const fineText = gap?.fine_tier ? FINE_EXPOSURE[gap.fine_tier] : null;
  const steps = gap?.remediation_steps?.steps ?? [];
  const policyLabel = POLICY_TYPE_LABEL[regulation] ?? "Compliance Policy";

  // ── Handlers ──────────────────────────────────────────

  const handleGeneratePolicy = () => {
    if (!gap) return;
    onClose();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    router.push(`/policies?gap_id=${gap.gap_id}&regulation=${regulation}` as any);
  };

  // ── Render helpers ────────────────────────────────────

  const renderLoading = () => <div className={styles.loadingWrapper}>Loading gap details...</div>;
  const renderNotFound = () => <div className={styles.notFoundWrapper}>Gap not found.</div>;

  const renderBadges = () => (
    <div className={styles.badges}>
      {gap?.article && (
        <span className={`${styles.badge} bg-[#0F2044] text-white border-[#0F2044]`}>
          {regulation.replace("_", " ")} · {gap.article}
        </span>
      )}
      <span className={`${styles.badge} ${severityCfg.bg} ${severityCfg.text} ${severityCfg.border}`}>
        {severityCfg.label}
      </span>
      {gap?.chapter && (
        <span className={`${styles.badge} bg-gray-100 text-gray-600 border-gray-200`}>{gap.chapter}</span>
      )}
    </div>
  );

  const renderPlainEnglish = () => {
    if (!gap?.plain_english) return null;
    return (
      <div>
        <p className={styles.sectionLabel}>What this rule requires</p>
        <div className={styles.plainBox}>{gap.plain_english}</div>
      </div>
    );
  };

  const renderStatus = () => {
    if (!gap) return null;
    const statusKey = gap.status ?? "unknown";
    return (
      <div className={styles.statusBox}>
        <div className={styles.statusRow}>
          <span className={`${styles.statusDot} ${STATUS_DOT[statusKey] ?? "bg-gray-400"}`} />
          <span className={styles.statusLabel}>Your status: {STATUS_LABEL[statusKey] ?? statusKey}</span>
        </div>
        <p className={styles.statusBody}>{buildStatusSentence(gap)}</p>
      </div>
    );
  };

  const renderFineExposure = () => {
    if (!fineText) return null;
    return (
      <div className={styles.fineBox}>
        <svg className={`w-4 h-4 ${styles.fineIcon}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
        </svg>
        <div>
          <p className={styles.fineLabel}>Fine exposure</p>
          <p className={styles.fineText}>{fineText}</p>
        </div>
      </div>
    );
  };

  const renderSteps = () => {
    if (steps.length === 0) return null;
    return (
      <div>
        <p className={styles.sectionLabel}>How to fix it</p>
        <div className={styles.steps}>
          {steps.map((step, i) => (
            <div key={i} className={styles.step}>
              <div className={styles.stepNum}>{i + 1}</div>
              <p className={styles.stepText}>{step}</p>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderPolicyCallout = () => {
    if (!gap || gap.status === "met" || gap.status === "not_applicable") return null;
    return (
      <div className={styles.policyBox}>
        <div className={styles.policyIcon}>
          <svg className="w-4 h-4 text-[#1D4ED8]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div>
          <p className={styles.policyTitle}>Generate a policy document</p>
          <p className={styles.policyBody}>
            ComplianceKit will draft a {policyLabel} tailored to close this gap. Takes about 30 seconds. You can review and edit it before publishing.
          </p>
          <button className={styles.policyBtn} onClick={handleGeneratePolicy}>
            Generate policy
          </button>
        </div>
      </div>
    );
  };

  const renderResolve = () => {
    if (!gap) return null;
    return (
      <div className={styles.resolveSection}>
        <GapResolveButton
          gap={gap}
          assessmentId={assessmentId}
          notes={notes}
          onNotesChange={setNotes}
        />
      </div>
    );
  };

  const renderContent = () => {
    if (isLoading) return renderLoading();
    if (!gap) return renderNotFound();
    return (
      <div className="flex flex-col gap-5">
        {renderBadges()}
        {renderPlainEnglish()}
        {renderStatus()}
        {renderFineExposure()}
        {renderSteps()}
        {renderPolicyCallout()}
        {renderResolve()}
      </div>
    );
  };

  // ── Render ────────────────────────────────────────────

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={gap?.title ?? gap?.article ?? "Gap details"}
      size="lg"
    >
      {renderContent()}
    </Modal>
  );
};
