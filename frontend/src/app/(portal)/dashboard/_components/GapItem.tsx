"use client";

import type { Gap } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const SEVERITY_CONFIG = {
  critical: { dot: "bg-red-500", text: "text-red-700", bg: "bg-red-50", label: "Critical" },
  high: { dot: "bg-orange-500", text: "text-orange-700", bg: "bg-orange-50", label: "High" },
  medium: { dot: "bg-amber-500", text: "text-amber-700", bg: "bg-amber-50", label: "Medium" },
  low: { dot: "bg-blue-400", text: "text-blue-700", bg: "bg-blue-50", label: "Low" },
};

const STATUS_CONFIG = {
  not_met: { text: "text-red-600", bg: "bg-red-50", label: "Not Met" },
  partial: { text: "text-amber-600", bg: "bg-amber-50", label: "Partial" },
  unknown: { text: "text-gray-500", bg: "bg-gray-100", label: "Unknown" },
  met: { text: "text-green-600", bg: "bg-green-50", label: "Met" },
  not_applicable: { text: "text-gray-400", bg: "bg-gray-50", label: "Not Applicable" },
};

const FINE_LABELS = {
  tier_2: "€20M / 4%",
  tier_1: "€10M / 2%",
};

// ── Types ─────────────────────────────────────────────────

interface GapItemProps {
  gap: Gap;
  assessmentId: string;
  onClick: () => void;
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper:
    "bg-white rounded-xl border border-gray-100 p-4 flex items-center gap-4 hover:border-gray-200 hover:shadow-sm transition-all cursor-pointer group",
  wrapperResolved: "opacity-60",
  left: "flex-shrink-0",
  dot: "w-2.5 h-2.5 rounded-full",
  body: "flex-1 min-w-0",
  article: "text-sm font-semibold text-gray-900 group-hover:text-navy transition-colors truncate",
  category: "text-xs text-gray-400 mt-0.5 truncate",
  right: "flex items-center gap-2 flex-shrink-0",
  statusBadge: "text-xs font-medium px-2 py-0.5 rounded-full",
  fineBadge: "text-xs font-medium px-2 py-0.5 rounded-full bg-red-50 text-red-600 hidden sm:block",
  resolvedBadge: "text-xs text-green-600 font-medium hidden sm:block",
  chevron: "w-4 h-4 text-gray-300 group-hover:text-gray-500 transition-colors",
};

// ── Sub-components ────────────────────────────────────────

const ChevronIcon = () => (
  <svg className={styles.chevron} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
);

// ── Component ─────────────────────────────────────────────

export const GapItem = ({ gap, onClick }: GapItemProps) => {
  const severity = SEVERITY_CONFIG[gap.severity ?? "medium"] ?? SEVERITY_CONFIG.medium;
  const status = STATUS_CONFIG[gap.status] ?? STATUS_CONFIG.unknown;
  const fineLabel = gap.fine_tier ? FINE_LABELS[gap.fine_tier] : null;

  // ── Render helpers ────────────────────────────────────

  const renderLeft = () => (
    <div className={styles.left}>
      <div className={`${styles.dot} ${severity.dot}`} />
    </div>
  );

  const renderBody = () => (
    <div className={styles.body}>
      <p className={styles.article}>{gap.article}</p>
      <p className={styles.category}>{gap.category ?? "General"}</p>
    </div>
  );

  const renderRight = () => (
    <div className={styles.right}>
      {gap.resolved && <span className={styles.resolvedBadge}>✓ Resolved</span>}
      {fineLabel && !gap.resolved && <span className={styles.fineBadge}>{fineLabel}</span>}
      <span className={`${styles.statusBadge} ${status.bg} ${status.text}`}>{status.label}</span>
      <ChevronIcon />
    </div>
  );

  // ── Render ────────────────────────────────────────────

  return (
    <div
      onClick={onClick}
      className={`${styles.wrapper} ${gap.resolved ? styles.wrapperResolved : ""}`}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onClick()}
      aria-label={`${gap.article}: ${status.label}`}
    >
      {renderLeft()}
      {renderBody()}
      {renderRight()}
    </div>
  );
};
