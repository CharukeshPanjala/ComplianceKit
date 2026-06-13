// WHAT: Generate Policy modal | CHANGE: new file | WHY: COM-176 — pick a policy type and gaps (across GDPR/NIS2/AI Act) to draft a policy
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Modal } from "@/components/ui/Modal";
import { useLatestAssessments } from "@/lib/hooks/useLatestAssessments";
import { useGaps } from "@/lib/hooks/useGaps";
import { useGeneratePolicy } from "@/lib/hooks/usePolicies";
import { POLICY_TYPE_LABELS, type PolicyType } from "@/lib/policiesApi";
import type { RegulationName } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────────────────────────

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

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  body: "space-y-5",
  field: "space-y-1.5",
  label: "text-xs font-semibold text-gray-500 uppercase tracking-wider",
  select:
    "w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0F2044]/20 focus:border-[#0F2044] bg-white",
  tabs: "flex gap-2 border-b border-gray-100 pb-2",
  tab: (active: boolean) =>
    `px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
      active ? "bg-[#0F2044] text-white" : "text-gray-500 hover:bg-gray-50"
    }`,
  gapList: "space-y-1 max-h-64 overflow-y-auto border border-gray-100 rounded-xl p-2",
  gapRow: "flex items-start gap-2.5 px-2 py-1.5 rounded-lg hover:bg-gray-50 cursor-pointer",
  gapCheck: "w-4 h-4 mt-0.5 text-[#0F2044] rounded flex-shrink-0",
  severityDot: "w-2 h-2 rounded-full mt-1.5 flex-shrink-0",
  gapText: "text-xs",
  gapArticle: "font-semibold text-gray-700",
  gapTitle: "text-gray-500",
  placeholder: "text-sm text-gray-400 text-center py-6",
  footer: "flex items-center justify-between pt-4 border-t border-gray-100 mt-5",
  summary: "text-xs text-gray-500",
  errorText: "text-xs text-red-500 ml-2",
  rightActions: "flex gap-2",
  cancelBtn: "px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors",
  generateBtn:
    "px-5 py-2 bg-[#0F2044] text-white text-sm font-semibold rounded-xl hover:bg-[#1a3366] transition-colors disabled:opacity-50",
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface GeneratePolicyModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialGapId?: string | null;
  initialRegulation?: RegulationName | null;
}

// ── Component ─────────────────────────────────────────────────────────────────

export const GeneratePolicyModal = ({
  isOpen,
  onClose,
  initialGapId,
  initialRegulation,
}: GeneratePolicyModalProps) => {
  const router = useRouter();

  // ── State ─────────────────────────────────────────────

  const [policyType, setPolicyType] = useState<PolicyType | "">("");
  const [activeTab, setActiveTab] = useState<RegulationName>("GDPR");
  const [selectedGapIds, setSelectedGapIds] = useState<Set<string>>(new Set());

  const { data: latestAssessments } = useLatestAssessments();
  const activeAssessment = latestAssessments?.find((a) => a.regulation === activeTab) ?? null;
  const { data: gapsData, isLoading: gapsLoading } = useGaps(activeAssessment?.assessment_id ?? null, {
    resolved: false,
    limit: 100,
  });

  const generatePolicy = useGeneratePolicy();

  // ── Effects ───────────────────────────────────────────

  useEffect(() => {
    if (!isOpen) return;
    if (initialRegulation) setActiveTab(initialRegulation);
    if (initialGapId) setSelectedGapIds((prev) => new Set(prev).add(initialGapId));
  }, [isOpen, initialGapId, initialRegulation]);

  // ── Handlers ──────────────────────────────────────────

  const handleToggleGap = (gapId: string) => {
    setSelectedGapIds((prev) => {
      const next = new Set(prev);
      if (next.has(gapId)) next.delete(gapId);
      else next.add(gapId);
      return next;
    });
  };

  const handleClose = () => {
    setPolicyType("");
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

  // ── Render helpers ────────────────────────────────────

  const renderPolicyTypeSelect = () => (
    <div className={styles.field}>
      <label className={styles.label}>Policy type</label>
      <select className={styles.select} value={policyType} onChange={(e) => setPolicyType(e.target.value as PolicyType)}>
        <option value="">Select a policy type…</option>
        {Object.entries(POLICY_TYPE_LABELS).map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>
    </div>
  );

  const renderTabs = () => (
    <div className={styles.tabs}>
      {REGULATION_TABS.map((tab) => (
        <button key={tab.value} className={styles.tab(activeTab === tab.value)} onClick={() => setActiveTab(tab.value)}>
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
      return <p className={styles.placeholder}>Loading gaps…</p>;
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
              {gap.title && <span className={styles.gapTitle}> — {gap.title}</span>}
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
          <span className={styles.errorText}>{generatePolicy.error?.message ?? "Failed to generate"}</span>
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
          {generatePolicy.isPending ? "Generating…" : "Generate"}
        </button>
      </div>
    </div>
  );

  // ── Render ────────────────────────────────────────────

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Generate Policy" size="lg">
      <div className={styles.body}>
        {renderPolicyTypeSelect()}
        <div className={styles.field}>
          <label className={styles.label}>Select gaps to address</label>
          {renderTabs()}
          {renderGapList()}
        </div>
      </div>
      {renderFooter()}
    </Modal>
  );
};
