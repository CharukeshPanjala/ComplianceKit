"use client";

import { useState } from "react";
import { GapList } from "../../dashboard/_components/GapList";
import { GapDetailModal } from "../../dashboard/_components/GapDetailModal";
import { useLatestAssessments } from "@/lib/hooks/useLatestAssessments";
import type { RegulationName } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const REGULATIONS: { value: RegulationName; label: string }[] = [
  { value: "GDPR", label: "GDPR" },
  { value: "NIS2", label: "NIS2" },
  { value: "EU_AI_ACT", label: "EU AI Act" },
];

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "flex-1 overflow-y-auto",
  inner: "max-w-7xl mx-auto px-6 py-8 space-y-6",
  tabs: "flex gap-2 border-b border-gray-100",
  tab: {
    base: "px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px",
    active: "border-navy text-navy",
    inactive: "border-transparent text-gray-500 hover:text-gray-700",
  },
  emptyWrapper: "text-center py-16",
  emptyTitle: "text-sm font-medium text-gray-500",
  emptySubtitle: "text-xs text-gray-400 mt-1",
};

// ── Component ─────────────────────────────────────────────

export const GapsPageContent = () => {
  // ── State ────────────────────────────────────────────

  const [activeRegulation, setActiveRegulation] = useState<RegulationName>("GDPR");
  const [selectedGapId, setSelectedGapId] = useState<string | null>(null);

  const { data: assessments = [], isLoading } = useLatestAssessments();

  const activeAssessment = assessments.find((a) => a.regulation === activeRegulation) ?? null;

  // ── Handlers ─────────────────────────────────────────

  const handleTabClick = (regulation: RegulationName) => {
    setActiveRegulation(regulation);
    setSelectedGapId(null);
  };

  const handleGapClick = (gapId: string) => setSelectedGapId(gapId);
  const handleModalClose = () => setSelectedGapId(null);

  // ── Render helpers ────────────────────────────────────

  const renderTabs = () => (
    <div className={styles.tabs}>
      {REGULATIONS.map((reg) => (
        <button
          key={reg.value}
          onClick={() => handleTabClick(reg.value)}
          className={`${styles.tab.base} ${
            activeRegulation === reg.value ? styles.tab.active : styles.tab.inactive
          }`}
        >
          {reg.label}
        </button>
      ))}
    </div>
  );

  const renderEmptyState = (title: string, subtitle: string) => (
    <div className={styles.emptyWrapper}>
      <p className={styles.emptyTitle}>{title}</p>
      <p className={styles.emptySubtitle}>{subtitle}</p>
    </div>
  );

  const renderContent = () => {
    if (isLoading) return null;

    if (!activeAssessment?.assessment_id) {
      return renderEmptyState(
        "No assessment yet for this regulation",
        "Run an assessment from the dashboard first"
      );
    }

    if (activeAssessment.status !== "completed") {
      return renderEmptyState(
        "Assessment is still running",
        "Check back in a moment, or view progress on the dashboard"
      );
    }

    return (
      <GapList
        assessmentId={activeAssessment.assessment_id}
        regulation={activeRegulation}
        onGapClick={handleGapClick}
      />
    );
  };

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.wrapper}>
      <div className={styles.inner}>
        {renderTabs()}
        {renderContent()}
      </div>
      {activeAssessment?.assessment_id && (
        <GapDetailModal
          gapId={selectedGapId}
          assessmentId={activeAssessment.assessment_id}
          regulation={activeRegulation}
          isOpen={!!selectedGapId}
          onClose={handleModalClose}
        />
      )}
    </div>
  );
};
