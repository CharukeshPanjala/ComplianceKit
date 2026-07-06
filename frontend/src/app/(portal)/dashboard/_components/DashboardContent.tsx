"use client";

import { useState, useEffect, useRef } from "react";
import { useUser } from "@clerk/nextjs";
import { GapList } from "./GapList";
import { GapDetailModal } from "./GapDetailModal";
import { ScoreTrendChart } from "./ScoreTrendChart";
import { DeadlinesWidget } from "./DeadlinesWidget";
import { QuickWinsWidget } from "./QuickWinsWidget";
import { RemediationRoadmap } from "./RemediationRoadmap";
import { ProfileCompletenessWidget } from "./ProfileCompletenessWidget";
import { ExecutiveSummaryBar } from "./ExecutiveSummaryBar";
import { CriticalAlertsPanel } from "./CriticalAlertsPanel";
import { RegulationHealthCards } from "./RegulationHealthCards";
import { GapChartsRow } from "./GapChartsRow";
import { RiskExposurePanel } from "./RiskExposurePanel";
import { ComplianceMiniWidgets } from "./ComplianceMiniWidgets";
import { RecentActivityFeed } from "./RecentActivityFeed";
import { useGaps } from "@/lib/hooks/useGaps";
import { useAssessmentStats } from "@/lib/hooks/useAssessmentStats";
import { useTriggerAssessment } from "@/lib/hooks/useTriggerAssessment";
import { useDownloadComplianceReport } from "@/lib/hooks/useReports";
import { useLatestAssessments } from "@/lib/hooks/useLatestAssessments";
import { useDsarList } from "@/lib/hooks/useDsar";
import { useBreachList } from "@/lib/hooks/useBreaches";
import { useProcessorList } from "@/lib/hooks/useProcessors";
import type { Gap } from "@/types/assessment";
import type { ReportFormat } from "@/lib/reportsApi";
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
  backBtn:
    "text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1.5 transition-colors",
  widgetGrid: "grid grid-cols-1 lg:grid-cols-3 gap-6",
  widgetLeft: "lg:col-span-2 space-y-6",
  widgetRight: "space-y-6",
  pageHeader: "flex items-start justify-between gap-4 flex-wrap",
  pageTitle: "text-2xl font-bold text-[#0F172A]",
  pageSubtitle: "text-sm text-[#64748B] mt-0.5",
  maturityBadge:
    "inline-block mt-1 text-xs font-semibold px-2 py-0.5 rounded-full",
  headerActions: "flex items-center gap-2 flex-shrink-0",
  btnPrimary:
    "px-4 py-2 text-sm font-medium bg-[#D97706] hover:bg-[#B45309] text-white rounded-lg transition-colors disabled:opacity-50",
  btnSecondary:
    "px-4 py-2 text-sm font-medium border border-[#E2E8F0] rounded-lg text-[#334155] hover:bg-gray-50 transition-colors disabled:opacity-50",
  sectionLabel:
    "text-xs font-semibold tracking-widest text-[#64748B] uppercase mb-3",
  section:
    "bg-white rounded-xl shadow-sm p-6 border border-gray-100 space-y-4",
  row23: "grid grid-cols-1 lg:grid-cols-3 gap-6",
  row23Left: "lg:col-span-2",
  row23Right: "",
  row56: "grid grid-cols-1 lg:grid-cols-3 gap-6",
  row56Left: "lg:col-span-2",
  row56Right: "",
  errorText: "text-sm text-red-500 mt-2",
};

// ── Sub-components ────────────────────────────────────────

const BackIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
  </svg>
);

// ── Gaps loader for a single assessment ──────────────────
const GapsForAssessment = ({
  assessmentId,
  onGaps,
}: {
  assessmentId: string;
  onGaps: (id: string, gaps: Gap[]) => void;
}) => {
  const { data: gapData } = useGaps(assessmentId);
  const gaps = gapData?.gaps ?? [];
  useEffect(() => {
    if (gaps.length > 0) onGaps(assessmentId, gaps);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assessmentId, gaps.length]);
  return null;
};

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

  const [selectedAssessment, setSelectedAssessment] =
    useState<SelectedAssessment | null>(null);
  const [selectedGapId, setSelectedGapId] = useState<string | null>(null);
  const [gapsByRegulation, setGapsByRegulation] = useState<Record<string, Gap[]>>({});

  // ── Hooks ─────────────────────────────────────────────

  const { user } = useUser();
  const downloadReport = useDownloadComplianceReport();
  const { data: latestAssessments = [] } = useLatestAssessments();
  const { data: dsarData } = useDsarList();
  const { data: breachData } = useBreachList();
  const { data: vendorData } = useProcessorList();

  const primaryAssessmentId =
    latestAssessments.find((a) => a.status === "completed" && a.assessment_id)
      ?.assessment_id ?? null;
  const { data: primaryStats } = useAssessmentStats(primaryAssessmentId ?? "");

  const triggerAssessment = useTriggerAssessment();
  const autoTriggered = useRef(false);

  useEffect(() => {
    if (autoTriggered.current || latestAssessments.length === 0) return;
    const neverRun = latestAssessments.filter((a) => a.status === "never_run");
    if (neverRun.length === 0) return;
    autoTriggered.current = true;
    neverRun.forEach((a) => triggerAssessment.mutate(a.regulation));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [latestAssessments]);

  const dsarRequests = dsarData?.dsars ?? [];
  const breachIncidents = breachData?.breaches ?? [];
  const vendors = vendorData?.processors ?? [];

  // ── Handlers ─────────────────────────────────────────

  const handleGapsLoaded = (assessmentId: string, gaps: Gap[]) => {
    const regulation = latestAssessments.find(
      (a) => a.assessment_id === assessmentId
    )?.regulation;
    if (!regulation) return;
    setGapsByRegulation((prev) => {
      if (prev[regulation]?.length === gaps.length) return prev;
      return { ...prev, [regulation]: gaps };
    });
  };

  const allGaps = Object.values(gapsByRegulation).flat();

  const handleDownloadReport = (format: ReportFormat) => {
    downloadReport.mutate(format);
  };

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

  const renderMaturityBadge = () => {
    const completed = latestAssessments.filter(
      (a) => a.status === "completed" && a.score !== null
    );
    const avg =
      completed.length > 0
        ? Math.round(
            completed.reduce((s, a) => s + (a.score ?? 0), 0) / completed.length
          )
        : 0;

    if (avg < 40)
      return (
        <span className={`${styles.maturityBadge} bg-red-100 text-red-700`}>
          Developing
        </span>
      );
    if (avg < 70)
      return (
        <span className={`${styles.maturityBadge} bg-amber-100 text-amber-700`}>
          Established
        </span>
      );
    return (
      <span className={`${styles.maturityBadge} bg-green-100 text-green-700`}>
        Advanced
      </span>
    );
  };

  const renderOverview = () => {
    const hour = new Date().getHours();
    const greeting =
      hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
    const firstName = user?.firstName ?? "there";

    return (
      <div className="space-y-6">
        {/* Page header */}
        <div className={styles.pageHeader}>
          <div>
            <h1 className={styles.pageTitle}>
              {greeting}, {firstName}
            </h1>
            <p className={styles.pageSubtitle}>
              Your compliance posture across all regulations
            </p>
            {renderMaturityBadge()}
          </div>
          <div className={styles.headerActions}>
            <button
              className={styles.btnPrimary}
              onClick={() => handleDownloadReport("pdf")}
              disabled={downloadReport.isPending}
            >
              {downloadReport.isPending && downloadReport.variables === "pdf"
                ? "Generating..."
                : "Export PDF"}
            </button>
            <button
              className={styles.btnSecondary}
              onClick={() => handleDownloadReport("docx")}
              disabled={downloadReport.isPending}
            >
              {downloadReport.isPending && downloadReport.variables === "docx"
                ? "Generating..."
                : "Export DOCX"}
            </button>
          </div>
        </div>

        {/* Hidden gap loaders — fetch gaps for all completed assessments */}
        {latestAssessments
          .filter((a) => a.status === "completed" && a.assessment_id)
          .map((a) => (
            <GapsForAssessment
              key={a.assessment_id!}
              assessmentId={a.assessment_id!}
              onGaps={handleGapsLoaded}
            />
          ))}

        {downloadReport.isError && (
          <p className={styles.errorText}>
            {downloadReport.error?.message ?? "Failed to generate report."}
          </p>
        )}

        {/* Row 1 — Executive summary bar */}
        <div className={styles.section}>
          <p className={styles.sectionLabel}>Summary</p>
          <ExecutiveSummaryBar assessments={latestAssessments} gaps={allGaps} />
        </div>

        {/* Row 3 — Critical alerts */}
        <div className={styles.section}>
          <p className={styles.sectionLabel}>Needs Your Attention</p>
          <CriticalAlertsPanel
            assessments={latestAssessments}
            gaps={allGaps}
            dsarRequests={dsarRequests}
            breachIncidents={breachIncidents}
          />
        </div>

        {/* Row 3 — Regulation health cards */}
        <div className={styles.section}>
          <p className={styles.sectionLabel}>Regulation Health</p>
          <RegulationHealthCards
            assessments={latestAssessments}
            gapsByRegulation={gapsByRegulation}
            onViewGaps={handleViewGaps}
          />
        </div>

        {/* Row 5 — Score trend (2/3) + Mini widgets (1/3) */}
        <div className={styles.row23}>
          <div className={`${styles.section} ${styles.row23Left}`}>
            <p className={styles.sectionLabel}>Score Trend</p>
            <ScoreTrendChart />
          </div>
          <div className={`${styles.section} ${styles.row23Right}`}>
            <p className={styles.sectionLabel}>Compliance Status</p>
            <ComplianceMiniWidgets
              dsarRequests={dsarRequests}
              vendors={vendors}
            />
          </div>
        </div>

        {/* Row 6 — Gap charts */}
        {allGaps.length > 0 && (
          <div className={styles.section}>
            <p className={styles.sectionLabel}>Gap Breakdown</p>
            <GapChartsRow gapsByRegulation={gapsByRegulation} />
          </div>
        )}

        {/* Row 7 — Risk exposure (2/3) + Recent activity (1/3) */}
        <div className={styles.row56}>
          <div className={`${styles.section} ${styles.row56Left}`}>
            <p className={styles.sectionLabel}>Risk Exposure</p>
            <RiskExposurePanel assessments={latestAssessments} gapsByRegulation={gapsByRegulation} />
          </div>
          <div className={`${styles.section} ${styles.row56Right}`}>
            <p className={styles.sectionLabel}>Recent Activity</p>
            <RecentActivityFeed
              assessments={latestAssessments}
              gaps={allGaps}
              dsarRequests={dsarRequests}
              breachIncidents={breachIncidents}
            />
          </div>
        </div>

        {/* Bottom widgets */}
        <div className={styles.widgetGrid}>
          <div className={styles.widgetLeft}>
            <QuickWinsWidget stats={primaryStats ?? null} assessmentId={primaryAssessmentId ?? ""} />
          </div>
          <div className={styles.widgetRight}>
            <ProfileCompletenessWidget profile={profile} />
            {Object.entries(gapsByRegulation).map(([reg, regGaps]) =>
              regGaps.some((g) => g.due_date && !g.resolved) ? (
                <DeadlinesWidget key={reg} gaps={regGaps} regulation={reg} />
              ) : null
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderGapView = () => {
    if (!selectedAssessment) return null;
    return (
      <GapSection
        assessment={selectedAssessment}
        onBack={handleBack}
        onGapClick={handleGapClick}
      />
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
      <div className={styles.inner}>
        {selectedAssessment ? renderGapView() : renderOverview()}
      </div>
      {renderModal()}
    </div>
  );
};
