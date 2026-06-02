"use client";

import { useAuth } from "@clerk/nextjs";
import { useQueryClient } from "@tanstack/react-query";
import { showToast } from "@/components/ui/Toast";
import { updateGap } from "@/lib/assessmentApi";
import { assessmentKeys } from "@/lib/hooks/useTriggerAssessment";
import type { AssessmentStats } from "@/types/assessment";

// ── Types ─────────────────────────────────────────────────

interface QuickWinsWidgetProps {
  stats: AssessmentStats | null;
  assessmentId: string;
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "bg-white rounded-2xl border border-gray-100 shadow-sm p-6",
  header: "flex items-center justify-between mb-4",
  title: "text-sm font-semibold text-gray-900",
  subtitle: "text-xs text-gray-400 mt-0.5",
  headerIcon: "w-5 h-5 text-amber-500",
  list: "space-y-3",
  item: "flex items-start gap-3 p-3 rounded-xl bg-amber-50 border border-amber-100",
  itemBody: "flex-1 min-w-0",
  itemArticle: "text-sm font-medium text-gray-900",
  itemCategory: "text-xs text-gray-400 mt-0.5",
  itemHint: "text-xs text-gray-600 mt-1 leading-relaxed",
  resolveBtn:
    "flex-shrink-0 text-xs font-medium text-amber-700 border border-amber-300 bg-white px-2.5 py-1.5 rounded-lg hover:bg-amber-50 transition-colors",
  emptyWrapper: "text-center py-8",
  emptyIcon: "w-10 h-10 text-gray-200 mx-auto mb-2",
  emptyTitle: "text-sm font-medium text-gray-500",
  emptySubtitle: "text-xs text-gray-400 mt-1",
  scoreBoost: "text-xs text-amber-600 font-medium mt-3 text-center",
};

// ── Sub-components ────────────────────────────────────────

const LightningIcon = () => (
  <svg className={styles.headerIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={1.5}
      d="M13 10V3L4 14h7v7l9-11h-7z"
    />
  </svg>
);

const EmptyState = () => (
  <div className={styles.emptyWrapper}>
    <svg className={styles.emptyIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1}
        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
    <p className={styles.emptyTitle}>No quick wins available</p>
    <p className={styles.emptySubtitle}>All easy gaps are resolved</p>
  </div>
);

// ── Component ─────────────────────────────────────────────

export const QuickWinsWidget = ({ stats, assessmentId }: QuickWinsWidgetProps) => {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  const wins = stats?.quick_wins ?? [];

  // ── Handlers ─────────────────────────────────────────

  const handleResolve = async (gapId: string) => {
    try {
      const token = await getToken();
      if (!token) return;
      await updateGap(token, assessmentId, gapId, { resolved: true });
      queryClient.invalidateQueries({ queryKey: assessmentKeys.gaps(assessmentId) });
      queryClient.invalidateQueries({ queryKey: assessmentKeys.stats(assessmentId) });
      showToast.success("Gap marked as resolved");
    } catch {
      showToast.error("Failed to resolve gap. Please try again.");
    }
  };

  // ── Render helpers ────────────────────────────────────

  const renderHeader = () => (
    <div className={styles.header}>
      <div>
        <h3 className={styles.title}>Quick Wins</h3>
        <p className={styles.subtitle}>Low-effort fixes for a higher score</p>
      </div>
      <LightningIcon />
    </div>
  );

  const renderItem = (win: AssessmentStats["quick_wins"][0]) => (
    <div key={win.gap_id} className={styles.item}>
      <div className={styles.itemBody}>
        <p className={styles.itemArticle}>{win.article}</p>
        <p className={styles.itemCategory}>{win.category ?? "General"}</p>
        {win.remediation_hint && <p className={styles.itemHint}>{win.remediation_hint}</p>}
      </div>
      <button onClick={() => handleResolve(win.gap_id)} className={styles.resolveBtn}>
        Resolve
      </button>
    </div>
  );

  const renderScoreBoost = () => {
    if (wins.length === 0) return null;
    return (
      <p className={styles.scoreBoost}>
        ⚡ Resolving these {wins.length} gaps could improve your score
      </p>
    );
  };

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.wrapper}>
      {renderHeader()}
      {wins.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          <div className={styles.list}>{wins.map(renderItem)}</div>
          {renderScoreBoost()}
        </>
      )}
    </div>
  );
};
