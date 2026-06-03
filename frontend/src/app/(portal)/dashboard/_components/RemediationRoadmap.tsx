"use client";

import type { Gap } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const PRIORITY_CONFIG = {
  critical: {
    bg: "bg-red-500",
    text: "text-red-700",
    light: "bg-red-50",
    border: "border-red-100",
    label: "Critical",
  },
  high: {
    bg: "bg-orange-500",
    text: "text-orange-700",
    light: "bg-orange-50",
    border: "border-orange-100",
    label: "High",
  },
  medium: {
    bg: "bg-amber-500",
    text: "text-amber-700",
    light: "bg-amber-50",
    border: "border-amber-100",
    label: "Medium",
  },
  low: {
    bg: "bg-blue-400",
    text: "text-blue-700",
    light: "bg-blue-50",
    border: "border-blue-100",
    label: "Low",
  },
};

const PRIORITY_ORDER = ["critical", "high", "medium", "low"] as const;
type Priority = (typeof PRIORITY_ORDER)[number];

// ── Types ─────────────────────────────────────────────────

interface RemediationRoadmapProps {
  gaps: Gap[];
  onGapClick: (gapId: string) => void;
}

interface GroupedGaps {
  priority: Priority;
  gaps: Gap[];
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "bg-white rounded-2xl border border-gray-100 shadow-sm p-6",
  header: "flex items-center justify-between mb-5",
  title: "text-sm font-semibold text-gray-900",
  subtitle: "text-xs text-gray-400 mt-0.5",
  counts: "flex gap-3",
  countBadge: "text-xs font-semibold px-2 py-1 rounded-full",
  groups: "space-y-5",
  groupHeader: "flex items-center gap-2 mb-2",
  groupDot: "w-2.5 h-2.5 rounded-full",
  groupLabel: "text-xs font-semibold uppercase tracking-wide",
  groupCount: "text-xs text-gray-400 ml-auto",
  groupItems: "space-y-1.5 ml-4",
  item: "flex items-center gap-3 p-2.5 rounded-lg border cursor-pointer hover:shadow-sm transition-all",
  itemArticle: "text-sm font-medium text-gray-800 flex-1 truncate",
  itemStatus: "text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0",
  emptyWrapper: "text-center py-10",
  emptyIcon: "w-10 h-10 text-green-200 mx-auto mb-2",
  emptyTitle: "text-sm font-medium text-green-600",
  emptySubtitle: "text-xs text-gray-400 mt-1",
};

// ── Helpers ───────────────────────────────────────────────

const groupGapsByPriority = (gaps: Gap[]): GroupedGaps[] => {
  const actionableGaps = gaps.filter(
    (g) =>
      !g.resolved && g.remediation_priority && g.status !== "met" && g.status !== "not_applicable"
  );

  return PRIORITY_ORDER.map((priority) => ({
    priority,
    gaps: actionableGaps.filter((g) => g.remediation_priority === priority),
  })).filter((g) => g.gaps.length > 0);
};

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    not_met: "Not Met",
    partial: "Partial",
    unknown: "Unknown",
  };
  return labels[status] ?? status;
};

const getStatusColors = (status: string) => {
  const colors: Record<string, string> = {
    not_met: "bg-red-50 text-red-600",
    partial: "bg-amber-50 text-amber-600",
    unknown: "bg-gray-100 text-gray-500",
  };
  return colors[status] ?? "bg-gray-100 text-gray-500";
};

// ── Sub-components ────────────────────────────────────────

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
    <p className={styles.emptyTitle}>No action items</p>
    <p className={styles.emptySubtitle}>All gaps are resolved or met</p>
  </div>
);

// ── Component ─────────────────────────────────────────────

export const RemediationRoadmap = ({ gaps, onGapClick }: RemediationRoadmapProps) => {
  const groups = groupGapsByPriority(gaps);
  const totalActionItems = groups.reduce((sum, g) => sum + g.gaps.length, 0);
  const criticalCount = groups.find((g) => g.priority === "critical")?.gaps.length ?? 0;

  // ── Render helpers ────────────────────────────────────

  const renderHeader = () => (
    <div className={styles.header}>
      <div>
        <h3 className={styles.title}>Remediation Roadmap</h3>
        <p className={styles.subtitle}>{totalActionItems} items need attention</p>
      </div>
      {criticalCount > 0 && (
        <div className={styles.counts}>
          <span className={`${styles.countBadge} bg-red-50 text-red-700`}>
            {criticalCount} critical
          </span>
        </div>
      )}
    </div>
  );

  const renderGapItem = (gap: Gap) => (
    <div
      key={gap.gap_id}
      onClick={() => onGapClick(gap.gap_id)}
      className={`${styles.item} ${
        PRIORITY_CONFIG[gap.remediation_priority as Priority]?.border ?? "border-gray-100"
      } ${PRIORITY_CONFIG[gap.remediation_priority as Priority]?.light ?? "bg-gray-50"}`}
    >
      <p className={styles.itemArticle}>{gap.article}</p>
      <span className={`${styles.itemStatus} ${getStatusColors(gap.status)}`}>
        {getStatusLabel(gap.status)}
      </span>
    </div>
  );

  const renderGroup = (group: GroupedGaps) => {
    const config = PRIORITY_CONFIG[group.priority];
    return (
      <div key={group.priority}>
        <div className={styles.groupHeader}>
          <div className={`${styles.groupDot} ${config.bg}`} />
          <span className={`${styles.groupLabel} ${config.text}`}>{config.label}</span>
          <span className={styles.groupCount}>{group.gaps.length} gaps</span>
        </div>
        <div className={styles.groupItems}>{group.gaps.map(renderGapItem)}</div>
      </div>
    );
  };

  const renderGroups = () => <div className={styles.groups}>{groups.map(renderGroup)}</div>;

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.wrapper}>
      {renderHeader()}
      {groups.length === 0 ? <EmptyState /> : renderGroups()}
    </div>
  );
};
