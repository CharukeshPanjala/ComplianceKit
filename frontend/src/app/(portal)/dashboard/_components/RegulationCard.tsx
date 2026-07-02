"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { useQueryClient } from "@tanstack/react-query";
import { ScoreGauge } from "./ScoreGauge";
import { assessmentKeys } from "@/lib/hooks/useTriggerAssessment";
import { getAssessment } from "@/lib/assessmentApi";
import type { LatestAssessment, RiskLevel } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const REG_CONFIG = {
  GDPR: {
    label: "GDPR",
    fullName: "General Data Protection Regulation",
    initial: "G",
    iconBg: "bg-blue-100",
    iconText: "text-blue-700",
    border: "border-blue-200",
  },
  NIS2: {
    label: "NIS2",
    fullName: "Network & Information Security Directive",
    initial: "N",
    iconBg: "bg-purple-100",
    iconText: "text-purple-700",
    border: "border-purple-200",
  },
  EU_AI_ACT: {
    label: "EU AI Act",
    fullName: "Artificial Intelligence Act",
    initial: "A",
    iconBg: "bg-amber-100",
    iconText: "text-amber-700",
    border: "border-amber-200",
  },
};

const POLL_INTERVAL_MS = 3000;
const TIMEOUT_WARNING_S = 60;
const TIMEOUT_ERROR_S = 300;

// ── Types ─────────────────────────────────────────────────

interface RegulationCardProps {
  data: LatestAssessment;
  onViewGaps: (assessmentId: string) => void;
  onReAssess: () => void;
  isTriggering: boolean;
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  card: "bg-white rounded-2xl border-2 shadow-sm p-6 flex flex-col gap-4",
  header: "flex items-center justify-between",
  iconWrapper: "flex items-center gap-2.5",
  icon: "w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold",
  label: "text-sm font-semibold text-gray-900",
  fullName: "text-xs text-gray-400 leading-tight",
  date: "text-xs font-medium text-gray-500",
  body: "flex-1 flex flex-col items-center justify-center py-2",
  loadingSpinner: "w-16 h-16 rounded-full border-4 border-gray-100 border-t-amber-500 animate-spin",
  loadingText: "text-sm text-gray-500 text-center",
  timeoutWarning: "text-xs text-amber-600 text-center",
  timeoutError: "text-xs text-red-500 text-center",
  stateIcon: "w-12 h-12 rounded-full flex items-center justify-center",
  stateTitle: "text-sm text-gray-600",
  stateSubtitle: "text-xs text-gray-400",
  stateWrapper: "flex flex-col items-center gap-2 text-center",
  breakdown: "grid grid-cols-3 gap-2 text-center border-t border-gray-50 pt-3",
  breakdownLabel: "text-xs text-gray-400",
  actions: "flex gap-2",
  viewBtn:
    "flex-1 py-2 text-sm font-medium text-navy border border-navy/20 rounded-lg hover:bg-navy/5 transition-colors",
  reassessBtn:
    "flex-1 py-2 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50",
};

// ── Sub-components ────────────────────────────────────────

const LoadingState = ({ elapsed }: { elapsed: number }) => (
  <div className={styles.stateWrapper}>
    <div className={styles.loadingSpinner} />
    <p className={styles.loadingText}>Running assessment...</p>
    {elapsed > TIMEOUT_ERROR_S && (
      <p className={styles.timeoutError}>Something went wrong. Please refresh.</p>
    )}
    {elapsed > TIMEOUT_WARNING_S && elapsed <= TIMEOUT_ERROR_S && (
      <p className={styles.timeoutWarning}>Taking longer than expected...</p>
    )}
  </div>
);

const FailedState = () => (
  <div className={styles.stateWrapper}>
    <div className={`${styles.stateIcon} bg-red-50`}>
      <svg className="w-6 h-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
    </div>
    <p className={styles.stateTitle}>Assessment failed</p>
    <p className={styles.stateSubtitle}>Please try again</p>
  </div>
);

const NeverRunState = () => (
  <div className={styles.stateWrapper}>
    <div className={`${styles.stateIcon} bg-gray-50`}>
      <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        />
      </svg>
    </div>
    <p className={styles.stateTitle}>Not assessed yet</p>
    <p className={styles.stateSubtitle}>Starting automatically...</p>
  </div>
);

const NotApplicableState = () => (
  <div className={styles.stateWrapper}>
    <div className={`${styles.stateIcon} bg-gray-50`}>
      <svg className="w-6 h-6 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
        />
      </svg>
    </div>
    <p className={`${styles.stateTitle} text-gray-400`}>Not applicable</p>
    <p className={styles.stateSubtitle}>Based on your company profile</p>
  </div>
);

// ── Polling hook ──────────────────────────────────────────

const useAssessmentPolling = (assessmentId: string | null, initialStatus: string) => {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const [status, setStatus] = useState(initialStatus);
  const [elapsed, setElapsed] = useState(0);

  // Reset whenever a new assessment starts (e.g. re-assess) — initialStatus only
  // applies on mount otherwise, leaving stale "completed" state from the prior run.
  useEffect(() => {
    setStatus(initialStatus);
    setElapsed(0);
  }, [assessmentId, initialStatus]);

  const isPolling = !!assessmentId && (status === "pending" || status === "running");

  useEffect(() => {
    if (!isPolling) return;
    const interval = setInterval(async () => {
      setElapsed((e) => e + 3);
      try {
        const token = await getToken();
        if (!token) return;
        const result = await getAssessment(token, assessmentId!);
        if (!result) return;
        setStatus(result.status);
        if (result.status === "completed" || result.status === "failed") {
          queryClient.invalidateQueries({ queryKey: assessmentKeys.latest() });
          clearInterval(interval);
        }
      } catch {
        // silent — keep polling
      }
    }, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [isPolling, assessmentId, getToken, queryClient]);

  return { status, elapsed };
};

// ── Component ─────────────────────────────────────────────

export const RegulationCard = ({
  data,
  onViewGaps,
  onReAssess,
  isTriggering,
}: RegulationCardProps) => {
  const config = REG_CONFIG[data.regulation];
  const { status, elapsed } = useAssessmentPolling(data.assessment_id, data.status);

  const isLoading = isTriggering || status === "pending" || status === "running";
  const isCompleted = status === "completed";
  const isFailed = status === "failed";
  const isNeverRun = status === "never_run";
  const isNotApplicable = (status as string) === "not_applicable";

  const completedDate = data.completed_at ? new Date(data.completed_at).toLocaleDateString() : "";

  // ── Handlers ─────────────────────────────────────────

  const handleViewGaps = () => {
    if (data.assessment_id) onViewGaps(data.assessment_id);
  };

  // ── Render helpers ────────────────────────────────────

  const renderHeader = () => (
    <div className={styles.header}>
      <div className={styles.iconWrapper}>
        <div className={`${styles.icon} ${config.iconBg} ${config.iconText}`}>{config.initial}</div>
        <div>
          <p className={styles.label}>{config.label}</p>
          <p className={styles.fullName}>{config.fullName}</p>
        </div>
      </div>
      {isCompleted && <span className={styles.date}>{completedDate}</span>}
    </div>
  );

  const renderBody = () => (
    <div className={styles.body}>
      {isLoading && <LoadingState elapsed={elapsed} />}
      {isCompleted && data.score !== null && data.risk_level && (
        <ScoreGauge score={data.score} riskLevel={data.risk_level as RiskLevel} size="md" animate />
      )}
      {isFailed && <FailedState />}
      {isNeverRun && <NeverRunState />}
      {isNotApplicable && <NotApplicableState />}
    </div>
  );

  const renderBreakdown = () => {
    if (!isCompleted) return null;
    return (
      <div className={styles.breakdown}>
        <div>
          <p className={styles.breakdownLabel}>Met</p>
          <p className="text-sm font-semibold text-green-600">{data.met_rules ?? 0}</p>
        </div>
        <div>
          <p className={styles.breakdownLabel}>Not Met</p>
          <p className="text-sm font-semibold text-red-500">{data.not_met_rules ?? 0}</p>
        </div>
        <div>
          <p className={styles.breakdownLabel}>Unknown</p>
          <p className="text-sm font-semibold text-gray-400">{data.unknown_rules ?? 0}</p>
        </div>
      </div>
    );
  };

  const renderActions = () => {
    if (isNeverRun || isNotApplicable || isLoading) return null;
    return (
      <div className={styles.actions}>
        {isCompleted && data.assessment_id && (
          <button onClick={handleViewGaps} className={styles.viewBtn}>
            View Gaps
          </button>
        )}
        {(isCompleted || isFailed) && (
          <button onClick={onReAssess} disabled={isTriggering} className={styles.reassessBtn}>
            Re-assess
          </button>
        )}
      </div>
    );
  };

  // ── Render ────────────────────────────────────────────

  return (
    <div className={`${styles.card} ${config.border}`}>
      {renderHeader()}
      {renderBody()}
      {renderBreakdown()}
      {renderActions()}
    </div>
  );
};
