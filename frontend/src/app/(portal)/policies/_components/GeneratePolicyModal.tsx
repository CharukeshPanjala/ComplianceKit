"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Modal } from "@/components/ui/Modal";
import { useLatestAssessments } from "@/lib/hooks/useLatestAssessments";
import { useGaps } from "@/lib/hooks/useGaps";
import { useGeneratePolicy } from "@/lib/hooks/usePolicies";
import { type PolicyType } from "@/lib/policiesApi";
import type { RegulationName } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const REGULATION_TABS: { value: RegulationName; label: string }[] = [
  { value: "GDPR", label: "GDPR" },
  { value: "NIS2", label: "NIS2" },
  { value: "EU_AI_ACT", label: "EU AI Act" },
];

const SEVERITY_DOT: Record<string, string> = {
  critical: "bg-red-500",
  high: "bg-orange-500",
  medium: "bg-amber-500",
  low: "bg-blue-500",
};

interface PolicyTypeMeta {
  label: string;
  description: string;
  recommendedFor: RegulationName[];
}

const POLICY_TYPE_META: Record<PolicyType, PolicyTypeMeta> = {
  privacy_notice: {
    label: "Privacy Notice",
    description: "Tells users what personal data you collect, why, and their rights.",
    recommendedFor: ["GDPR"],
  },
  data_retention: {
    label: "Data Retention Policy",
    description: "Documents how long you keep each category of data and why.",
    recommendedFor: ["GDPR"],
  },
  dpa: {
    label: "Data Processing Agreement",
    description: "Contract with vendors who process personal data on your behalf.",
    recommendedFor: ["GDPR"],
  },
  cookie_policy: {
    label: "Cookie Policy",
    description: "Discloses tracking technologies used on your website and consent options.",
    recommendedFor: ["GDPR"],
  },
  incident_response: {
    label: "Incident Response Plan",
    description: "Your procedure for detecting, containing, and reporting security breaches.",
    recommendedFor: ["NIS2"],
  },
  ai_governance: {
    label: "AI Governance Policy",
    description: "Oversight, risk management, and accountability for AI systems you operate.",
    recommendedFor: ["EU_AI_ACT"],
  },
  ropa: {
    label: "Record of Processing Activities",
    description: "Comprehensive register of all personal data processing in your organisation.",
    recommendedFor: ["GDPR"],
  },
  other: {
    label: "General Compliance Policy",
    description: "A flexible policy document for compliance requirements not covered above.",
    recommendedFor: [],
  },
};

const DEFAULT_BY_REGULATION: Record<RegulationName, PolicyType> = {
  GDPR: "privacy_notice",
  NIS2: "incident_response",
  EU_AI_ACT: "ai_governance",
};

// ── Styles ────────────────────────────────────────────────

const styles = {
  body: "space-y-5",
  fieldLabel: "text-xs font-semibold text-[#64748B] uppercase tracking-wider mb-2",
  typeGrid: "grid grid-cols-2 gap-2",
  typeCard: (selected: boolean, recommended: boolean) =>
    `relative p-3 rounded-xl border cursor-pointer transition-all text-left ${
      selected
        ? "border-[#D97706] bg-amber-50 ring-1 ring-[#D97706]"
        : recommended
        ? "border-[#E2E8F0] bg-[#FAFBFC] hover:border-[#D97706]/40"
        : "border-[#E2E8F0] bg-white hover:border-gray-300"
    }`,
  typeCardLabel: (selected: boolean) =>
    `text-[13px] font-medium leading-tight ${selected ? "text-[#92400E]" : "text-[#0F172A]"}`,
  typeCardDesc: "text-[11px] text-[#64748B] leading-relaxed mt-1",
  recommendedBadge:
    "absolute top-2 right-2 text-[9px] font-semibold px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-700 uppercase tracking-wide",
  selectedCheck:
    "absolute top-2 right-2 w-4 h-4 rounded-full bg-[#D97706] flex items-center justify-center",
  tabs: "flex gap-2 border-b border-[#E2E8F0] pb-2",
  tab: (active: boolean) =>
    `px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
      active ? "bg-[#D97706] text-white" : "text-gray-500 hover:bg-gray-50"
    }`,
  gapList: "space-y-1 max-h-52 overflow-y-auto border border-[#E2E8F0] rounded-xl p-2",
  gapRow: "flex items-start gap-2.5 px-2 py-1.5 rounded-lg hover:bg-gray-50 cursor-pointer",
  gapCheck: "w-4 h-4 mt-0.5 text-[#0F2044] rounded flex-shrink-0",
  severityDot: "w-2 h-2 rounded-full mt-1.5 flex-shrink-0",
  gapText: "text-xs",
  gapArticle: "font-semibold text-gray-700",
  gapTitle: "text-gray-500",
  placeholder: "text-sm text-[#64748B] text-center py-6",
  footer: "flex items-center justify-between pt-4 border-t border-[#E2E8F0] mt-5",
  summary: "text-xs text-gray-500",
  errorText: "text-xs text-red-500 ml-2",
  rightActions: "flex gap-2",
  cancelBtn:
    "px-4 py-2 text-sm border border-[#E2E8F0] bg-white text-[#334155] rounded-xl transition-colors hover:bg-gray-50",
  generateBtn:
    "px-5 py-2 bg-[#D97706] text-white text-sm font-semibold rounded-xl hover:bg-[#B45309] transition-colors disabled:opacity-50",
};

// ── Types ─────────────────────────────────────────────────

interface GeneratePolicyModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialGapId?: string | null;
  initialRegulation?: RegulationName | null;
}

// ── Component ─────────────────────────────────────────────

export const GeneratePolicyModal = ({
  isOpen,
  onClose,
  initialGapId,
  initialRegulation,
}: GeneratePolicyModalProps) => {
  const router = useRouter();

  // ── State ──────────────────────────────────────────────

  const [policyType, setPolicyType] = useState<PolicyType>("privacy_notice");
  const [activeTab, setActiveTab] = useState<RegulationName>("GDPR");
  const [selectedGapIds, setSelectedGapIds] = useState<Set<string>>(new Set());

  const { data: latestAssessments } = useLatestAssessments();
  const activeAssessment = latestAssessments?.find((a) => a.regulation === activeTab) ?? null;
  const { data: gapsData, isLoading: gapsLoading } = useGaps(
    activeAssessment?.assessment_id ?? null,
    { resolved: false, limit: 100 }
  );

  const generatePolicy = useGeneratePolicy();

  // ── Effects ────────────────────────────────────────────

  useEffect(() => {
    if (!isOpen) return;
    if (initialRegulation) {
      setActiveTab(initialRegulation);
      setPolicyType(DEFAULT_BY_REGULATION[initialRegulation]);
    }
    if (initialGapId) setSelectedGapIds((prev) => new Set(prev).add(initialGapId));
  }, [isOpen, initialGapId, initialRegulation]);

  // auto-suggest policy type when tab changes (only if user hasn't explicitly chosen)
  const handleTabChange = (reg: RegulationName) => {
    setActiveTab(reg);
    setPolicyType(DEFAULT_BY_REGULATION[reg]);
  };

  // ── Handlers ───────────────────────────────────────────

  const handleToggleGap = (gapId: string) => {
    setSelectedGapIds((prev) => {
      const next = new Set(prev);
      if (next.has(gapId)) next.delete(gapId);
      else next.add(gapId);
      return next;
    });
  };

  const handleClose = () => {
    setPolicyType("privacy_notice");
    setSelectedGapIds(new Set());
    setActiveTab("GDPR");
    generatePolicy.reset();
    onClose();
  };

  const handleGenerate = () => {
    if (!policyType || selectedGapIds.size === 0) return;
    generatePolicy.mutate(
      { policy_type: policyType, gap_ids: Array.from(selectedGapIds) },
      {
        onSuccess: (policy) => {
          handleClose();
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          router.push(`/policies/${policy.policy_id}` as any);
        },
      }
    );
  };

  // ── Render helpers ─────────────────────────────────────

  const renderPolicyTypeCards = () => (
    <div>
      <p className={styles.fieldLabel}>What do you want to create?</p>
      <div className={styles.typeGrid}>
        {(Object.entries(POLICY_TYPE_META) as [PolicyType, PolicyTypeMeta][]).map(([type, meta]) => {
          const selected = policyType === type;
          const recommended = meta.recommendedFor.includes(activeTab);
          return (
            <button
              key={type}
              className={styles.typeCard(selected, recommended)}
              onClick={() => setPolicyType(type)}
            >
              {selected ? (
                <span className={styles.selectedCheck}>
                  <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </span>
              ) : recommended ? (
                <span className={styles.recommendedBadge}>Recommended</span>
              ) : null}
              <p className={styles.typeCardLabel(selected)}>{meta.label}</p>
              <p className={styles.typeCardDesc}>{meta.description}</p>
            </button>
          );
        })}
      </div>
    </div>
  );

  const renderTabs = () => (
    <div className={styles.tabs}>
      {REGULATION_TABS.map((tab) => (
        <button
          key={tab.value}
          className={styles.tab(activeTab === tab.value)}
          onClick={() => handleTabChange(tab.value)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );

  const renderGapList = () => {
    if (!activeAssessment?.assessment_id) {
      return <p className={styles.placeholder}>No assessment run yet for this regulation.</p>;
    }
    if (gapsLoading) {
      return <p className={styles.placeholder}>Loading gaps...</p>;
    }
    const gaps = gapsData?.gaps ?? [];
    if (gaps.length === 0) {
      return <p className={styles.placeholder}>No open gaps for this regulation.</p>;
    }
    return (
      <div className={styles.gapList}>
        {gaps.map((gap) => (
          <label key={gap.gap_id} className={styles.gapRow}>
            <input
              type="checkbox"
              className={styles.gapCheck}
              checked={selectedGapIds.has(gap.gap_id)}
              onChange={() => handleToggleGap(gap.gap_id)}
            />
            <span className={`${styles.severityDot} ${SEVERITY_DOT[gap.severity ?? "low"]}`} />
            <span className={styles.gapText}>
              <span className={styles.gapArticle}>{gap.article}</span>
              {gap.title && <span className={styles.gapTitle}>: {gap.title}</span>}
            </span>
          </label>
        ))}
      </div>
    );
  };

  const renderFooter = () => (
    <div className={styles.footer}>
      <p className={styles.summary}>
        {selectedGapIds.size} gap{selectedGapIds.size === 1 ? "" : "s"} selected
        {generatePolicy.isError && (
          <span className={styles.errorText}>
            {generatePolicy.error?.message ?? "Failed to generate"}
          </span>
        )}
      </p>
      <div className={styles.rightActions}>
        <button className={styles.cancelBtn} onClick={handleClose}>
          Cancel
        </button>
        <button
          className={styles.generateBtn}
          onClick={handleGenerate}
          disabled={!policyType || selectedGapIds.size === 0 || generatePolicy.isPending}
        >
          {generatePolicy.isPending ? "Generating..." : "Generate"}
        </button>
      </div>
    </div>
  );

  // ── Render ─────────────────────────────────────────────

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Generate policy" size="lg">
      <div className={styles.body}>
        {renderPolicyTypeCards()}
        <div>
          <p className={styles.fieldLabel}>Which gaps does this policy address?</p>
          {renderTabs()}
          {renderGapList()}
        </div>
      </div>
      {renderFooter()}
    </Modal>
  );
};
