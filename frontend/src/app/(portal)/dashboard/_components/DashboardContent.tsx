"use client";

import { useState } from "react";
import { AssessmentSection } from "./AssessmentSection";
import { GapList } from "./GapList";
import { GapDetailModal } from "./GapDetailModal";
import { ScoreTrendChart } from "./ScoreTrendChart";
import { DeadlinesWidget } from "./DeadlinesWidget";
import { QuickWinsWidget } from "./QuickWinsWidget";
import { RemediationRoadmap } from "./RemediationRoadmap";
import { ProfileCompletenessWidget } from "./ProfileCompletenessWidget";
import { useGaps } from "@/lib/hooks/useGaps";
import { useAssessmentStats } from "@/lib/hooks/useAssessmentStats";
import type { Profile } from "@/types/profile";
import type { RegulationName } from "@/types/assessment";

// ── Types ─────────────────────────────────────────────────

interface DashboardContentProps {
  profile: Profile;
}

interface SelectedAssessment {
  id: string;
  regulation: RegulationName;
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "flex-1 overflow-y-auto",
  inner: "max-w-7xl mx-auto px-6 py-8 space-y-8",
  gapSection: "space-y-4",
  gapHeader: "flex items-center justify-between",
  gapTitle: "text-lg font-bold text-gray-900",
  backBtn: "text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1.5 transition-colors",
  widgetGrid: "grid grid-cols-1 lg:grid-cols-3 gap-6",
  widgetLeft: "lg:col-span-2 space-y-6",
  widgetRight: "space-y-6",
};

// ── Sub-components ────────────────────────────────────────

const BackIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
  </svg>
);

// ── Gap section wrapper ───────────────────────────────────

const GapSection = ({
  assessment,
  onBack,
  onGapClick,
}: {
  assessment: SelectedAssessment;
  onBack: () => void;
  onGapClick: (gapId: string) => void;
}) => {
  const { data: gapData } = useGaps(assessment.id);
  const { data: stats } = useAssessmentStats(assessment.id);

  const gaps = gapData?.gaps ?? [];

  return (
    <div className={styles.gapSection}>
      <div className={styles.gapHeader}>
        <h2 className={styles.gapTitle}>{assessment.regulation} Gap Analysis</h2>
        <button onClick={onBack} className={styles.backBtn}>
          <BackIcon />
          Back to overview
        </button>
      </div>

      <div className={styles.widgetGrid}>
        <div className={styles.widgetLeft}>
          <GapList
            assessmentId={assessment.id}
            regulation={assessment.regulation}
            onGapClick={onGapClick}
          />
        </div>
        <div className={styles.widgetRight}>
          <QuickWinsWidget stats={stats ?? null} assessmentId={assessment.id} />
          <ScoreTrendChart regulation={assessment.regulation} />
          <DeadlinesWidget gaps={gaps} regulation={assessment.regulation} />
          <RemediationRoadmap gaps={gaps} onGapClick={onGapClick} />
        </div>
      </div>
    </div>
  );
};

// ── Component ─────────────────────────────────────────────

export const DashboardContent = ({ profile }: DashboardContentProps) => {
  // ── State ─────────────────────────────────────────────

  const [selectedAssessment, setSelectedAssessment] = useState<SelectedAssessment | null>(null);
  const [selectedGapId, setSelectedGapId] = useState<string | null>(null);

  // ── Handlers ─────────────────────────────────────────

  const handleViewGaps = (assessmentId: string, regulation: RegulationName) => {
    setSelectedAssessment({ id: assessmentId, regulation });
  };

  const handleBack = () => {
    setSelectedAssessment(null);
    setSelectedGapId(null);
  };

  const handleGapClick = (gapId: string) => {
    setSelectedGapId(gapId);
  };

  const handleModalClose = () => {
    setSelectedGapId(null);
  };

  // ── Render helpers ────────────────────────────────────

  const renderOverview = () => (
    <>
      <AssessmentSection
        profile={{
          nis2_data: profile.nis2_data,
          ai_act_data: profile.ai_act_data,
        }}
        onViewGaps={handleViewGaps}
      />
      <div className={styles.widgetGrid}>
        <div className={styles.widgetLeft}>
          <ProfileCompletenessWidget profile={profile} />
        </div>
        <div className={styles.widgetRight}>
          <ScoreTrendChart regulation="GDPR" />
        </div>
      </div>
    </>
  );

  const renderGapView = () => {
    if (!selectedAssessment) return null;
    return (
      <GapSection assessment={selectedAssessment} onBack={handleBack} onGapClick={handleGapClick} />
    );
  };

  const renderModal = () => {
    if (!selectedAssessment) return null;
    return (
      <GapDetailModal
        gapId={selectedGapId}
        assessmentId={selectedAssessment.id}
        regulation={selectedAssessment.regulation}
        isOpen={!!selectedGapId}
        onClose={handleModalClose}
      />
    );
  };

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.wrapper}>
      <div className={styles.inner}>{selectedAssessment ? renderGapView() : renderOverview()}</div>
      {renderModal()}
    </div>
  );
};
