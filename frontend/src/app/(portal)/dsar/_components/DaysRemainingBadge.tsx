"use client";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  badge: {
    base: "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold tabular-nums",
    critical: "bg-red-100 text-red-700",
    warning: "bg-amber-100 text-amber-700",
    ok: "bg-green-100 text-green-700",
    done: "bg-gray-100 text-gray-500",
  },
  dot: {
    base: "w-1.5 h-1.5 rounded-full",
    critical: "bg-red-500 animate-pulse",
    warning: "bg-amber-500",
    ok: "bg-green-500",
    done: "bg-gray-400",
  },
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface Props {
  daysRemaining: number;
  isOverdue: boolean;
  isTerminal: boolean;
}

// ── Component ─────────────────────────────────────────────────────────────────

export const DaysRemainingBadge = ({ daysRemaining, isOverdue, isTerminal }: Props) => {
  if (isTerminal) {
    return (
      <span className={`${styles.badge.base} ${styles.badge.done}`}>
        <span className={`${styles.dot.base} ${styles.dot.done}`} />
        Done
      </span>
    );
  }

  if (isOverdue) {
    return (
      <span className={`${styles.badge.base} ${styles.badge.critical}`}>
        <span className={`${styles.dot.base} ${styles.dot.critical}`} />
        {Math.abs(daysRemaining)}d overdue
      </span>
    );
  }

  const variant = daysRemaining <= 5 ? "critical" : daysRemaining <= 14 ? "warning" : "ok";
  const label = daysRemaining === 0 ? "Due today" : `${daysRemaining}d left`;

  return (
    <span className={`${styles.badge.base} ${styles.badge[variant]}`}>
      <span className={`${styles.dot.base} ${styles.dot[variant]}`} />
      {label}
    </span>
  );
};
