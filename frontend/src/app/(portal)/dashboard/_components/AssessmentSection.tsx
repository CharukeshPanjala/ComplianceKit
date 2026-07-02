"use client";

import { useEffect } from "react";
import { RegulationCard } from "./RegulationCard";
import { RegulationCardSkeleton } from "@/components/ui/Skeleton";
import { useLatestAssessments } from "@/lib/hooks/useLatestAssessments";
import { useTriggerAllAssessments, useTriggerAssessment } from "@/lib/hooks/useTriggerAssessment";
import type { LatestAssessment, RegulationName } from "@/types/assessment";

// ── Types ─────────────────────────────────────────────────

interface AssessmentSectionProps {
  profile: {
    nis2_data: Record<string, unknown> | null;
    ai_act_data: Record<string, unknown> | null;
  };
  onViewGaps: (assessmentId: string, regulation: RegulationName) => void;
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  section: "space-y-6",
  heading: "text-xl font-bold text-gray-900",
  subheading: "text-sm text-gray-500 mt-0.5",
  grid: "grid grid-cols-1 md:grid-cols-3 gap-6",
  emptyState: "text-center py-12 text-gray-400 text-sm",
};

// ── Helpers ───────────────────────────────────────────────

const hasNeverRunAssessment = (assessments: LatestAssessment[]) =>
  assessments.some((a) => a.status === "never_run");

const getRegulationFromId = (
  assessments: LatestAssessment[],
  assessmentId: string
): RegulationName | null =>
  assessments.find((a) => a.assessment_id === assessmentId)?.regulation ?? null;

// ── Component ─────────────────────────────────────────────

export const AssessmentSection = ({ profile, onViewGaps }: AssessmentSectionProps) => {
  const { data: assessments = [], isLoading } = useLatestAssessments();
  const { mutate: triggerAll } = useTriggerAllAssessments();
  const {
    mutate: triggerOne,
    isPending: isTriggering,
    variables: triggeringRegulation,
  } = useTriggerAssessment();

  // ── Handlers ─────────────────────────────────────────

  const handleReAssess = (regulation: RegulationName) => {
    triggerOne(regulation);
  };

  const handleViewGaps = (assessmentId: string) => {
    const regulation = getRegulationFromId(assessments, assessmentId);
    if (regulation) onViewGaps(assessmentId, regulation);
  };

  // ── Auto-trigger on first visit ───────────────────────

  useEffect(() => {
    if (isLoading) return;
    if (!hasNeverRunAssessment(assessments)) return;
    triggerAll(profile);
  }, [isLoading, assessments, profile, triggerAll]);

  // ── Render helpers ────────────────────────────────────

  const renderHeader = () => (
    <div>
      <h2 className={styles.heading}>Compliance Score</h2>
      <p className={styles.subheading}>
        Based on your company profile, last assessed{" "}
        {assessments.find((a) => a.completed_at)
          ? new Date(assessments.find((a) => a.completed_at)!.completed_at!).toLocaleDateString()
          : "never"}
      </p>
    </div>
  );

  const renderSkeletons = () => (
    <div className={styles.grid}>
      <RegulationCardSkeleton />
      <RegulationCardSkeleton />
      <RegulationCardSkeleton />
    </div>
  );

  const renderCards = () => (
    <div className={styles.grid}>
      {assessments.map((assessment) => (
        <RegulationCard
          key={assessment.regulation}
          data={assessment}
          onViewGaps={handleViewGaps}
          onReAssess={() => handleReAssess(assessment.regulation)}
          isTriggering={isTriggering && triggeringRegulation === assessment.regulation}
        />
      ))}
      {assessments.length === 0 && (
        <p className={styles.emptyState}>No regulations found. Please complete onboarding.</p>
      )}
    </div>
  );

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.section}>
      {renderHeader()}
      {isLoading ? renderSkeletons() : renderCards()}
    </div>
  );
};
