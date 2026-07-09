// ── Types ──────────────────────────────────────────────
interface CountdownBadgeProps {
  hours: number;
  label?: string;
}

// ── Styles ─────────────────────────────────────────────
const styles = {
  base: "text-xs font-medium px-2.5 py-0.5 rounded-full border inline-flex items-center gap-1.5",
  urgent: "bg-red-100 text-red-700 border-red-200",
  warning: "bg-amber-100 text-amber-700 border-amber-200",
  ok: "bg-green-100 text-green-700 border-green-200",
  icon: "w-3 h-3 flex-shrink-0",
};

// ── Sub-components ─────────────────────────────────────
const ClockIcon = ({ className }: { className: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
    />
  </svg>
);

// ── Helpers ────────────────────────────────────────────
const formatTime = (hours: number): string => {
  if (hours < 24) return `${Math.max(0, Math.round(hours))}h remaining`;
  const days = Math.floor(hours / 24);
  const remainingHours = Math.round(hours % 24);
  return remainingHours > 0 ? `${days}d ${remainingHours}h remaining` : `${days}d remaining`;
};

// ── Component ──────────────────────────────────────────
export const CountdownBadge = ({ hours, label }: CountdownBadgeProps) => {
  const variantClass =
    hours <= 24 ? styles.urgent : hours <= 168 ? styles.warning : styles.ok;

  return (
    <span className={`${styles.base} ${variantClass}`}>
      <ClockIcon className={styles.icon} />
      {label ?? formatTime(hours)}
    </span>
  );
};
