"use client";

import type { Gap } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const URGENCY_CONFIG = {
  overdue: { text: "text-red-700", bg: "bg-red-50", border: "border-red-200", label: "Overdue" },
  soon: {
    text: "text-amber-700",
    bg: "bg-amber-50",
    border: "border-amber-200",
    label: "Due soon",
  },
  upcoming: {
    text: "text-blue-700",
    bg: "bg-blue-50",
    border: "border-blue-200",
    label: "Upcoming",
  },
};

// ── Types ─────────────────────────────────────────────────

interface DeadlineItem {
  gap_id: string;
  article: string;
  category: string | null;
  due_date: string;
  severity: string | null;
  regulation: string;
}

interface DeadlinesWidgetProps {
  gaps: Gap[];
  regulation: string;
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "bg-white rounded-2xl border border-gray-100 shadow-sm p-6",
  header: "flex items-center justify-between mb-4",
  title: "text-sm font-semibold text-gray-900",
  headerIcon: "w-4 h-4 text-amber-500",
  list: "space-y-3",
  item: "flex items-center gap-3 p-3 rounded-xl border",
  itemLeft: "flex-1 min-w-0",
  itemArticle: "text-sm font-medium text-gray-900 truncate",
  itemMeta: "text-xs text-gray-400 mt-0.5",
  itemRight: "flex-shrink-0 text-right",
  itemDate: "text-xs font-semibold",
  itemBadge: "text-xs px-2 py-0.5 rounded-full font-medium mt-0.5",
  emptyWrapper: "text-center py-8",
  emptyIcon: "w-10 h-10 text-gray-200 mx-auto mb-2",
  emptyText: "text-sm text-gray-400",
};

// ── Helpers ───────────────────────────────────────────────

const getUrgency = (dueDate: string) => {
  const now = new Date();
  const due = new Date(dueDate);
  const daysUntil = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  if (daysUntil < 0) return { key: "overdue" as const, daysUntil };
  if (daysUntil <= 14) return { key: "soon" as const, daysUntil };
  return { key: "upcoming" as const, daysUntil };
};

const formatDaysLabel = (daysUntil: number) => {
  if (daysUntil < 0) return `${Math.abs(daysUntil)}d overdue`;
  if (daysUntil === 0) return "Due today";
  if (daysUntil === 1) return "Due tomorrow";
  return `${daysUntil}d remaining`;
};

const getDeadlines = (gaps: Gap[], regulation: string): DeadlineItem[] =>
  gaps
    .filter((g) => g.due_date && !g.resolved)
    .map((g) => ({
      gap_id: g.gap_id,
      article: g.article,
      category: g.category,
      due_date: g.due_date!,
      severity: g.severity,
      regulation,
    }))
    .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
    .slice(0, 5);

// ── Sub-components ────────────────────────────────────────

const CalendarIcon = () => (
  <svg className={styles.headerIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={1.5}
      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
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
        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
      />
    </svg>
    <p className={styles.emptyText}>No upcoming deadlines</p>
  </div>
);

// ── Component ─────────────────────────────────────────────

export const DeadlinesWidget = ({ gaps, regulation }: DeadlinesWidgetProps) => {
  const deadlines = getDeadlines(gaps, regulation);

  // ── Render helpers ────────────────────────────────────

  const renderHeader = () => (
    <div className={styles.header}>
      <h3 className={styles.title}>Upcoming Deadlines</h3>
      <CalendarIcon />
    </div>
  );

  const renderItem = (item: DeadlineItem) => {
    const { key, daysUntil } = getUrgency(item.due_date);
    const urgency = URGENCY_CONFIG[key];
    const dateLabel = formatDaysLabel(daysUntil);

    return (
      <div key={item.gap_id} className={`${styles.item} ${urgency.border} ${urgency.bg}`}>
        <div className={styles.itemLeft}>
          <p className={styles.itemArticle}>{item.article}</p>
          <p className={styles.itemMeta}>
            {item.regulation} · {item.category ?? "General"}
          </p>
        </div>
        <div className={styles.itemRight}>
          <p className={`${styles.itemDate} ${urgency.text}`}>{dateLabel}</p>
          <p className={`${styles.itemBadge} ${urgency.bg} ${urgency.text}`}>{urgency.label}</p>
        </div>
      </div>
    );
  };

  const renderList = () => <div className={styles.list}>{deadlines.map(renderItem)}</div>;

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.wrapper}>
      {renderHeader()}
      {deadlines.length === 0 ? <EmptyState /> : renderList()}
    </div>
  );
};
