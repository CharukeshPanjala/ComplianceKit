import type { ReactNode } from "react";

// ── Types ──────────────────────────────────────────────
interface StatCardProps {
  value: string | number;
  label: string;
  change?: { value: number; positive: boolean };
  icon?: ReactNode;
}

// ── Styles ─────────────────────────────────────────────
const styles = {
  card: "bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-6 relative",
  iconWrapper: "absolute top-4 right-4 w-10 h-10 rounded-full bg-[#FEF3C7] flex items-center justify-center text-[#D97706]",
  value: "text-3xl font-bold text-[#0F172A]",
  label: "text-sm text-[#64748B] mt-1",
  changeWrapper: "flex items-center gap-1 mt-2 text-sm font-medium",
  changeUp: "text-green-600",
  changeDown: "text-red-600",
};

// ── Sub-components ─────────────────────────────────────
const ArrowUp = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
  </svg>
);

const ArrowDown = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
  </svg>
);

// ── Component ──────────────────────────────────────────
export const StatCard = ({ value, label, change, icon }: StatCardProps) => (
  <div className={styles.card}>
    {icon && <div className={styles.iconWrapper}>{icon}</div>}
    <div className={styles.value}>{value}</div>
    <div className={styles.label}>{label}</div>
    {change && (
      <div className={`${styles.changeWrapper} ${change.positive ? styles.changeUp : styles.changeDown}`}>
        {change.positive ? <ArrowUp /> : <ArrowDown />}
        <span>{Math.abs(change.value)}%</span>
      </div>
    )}
  </div>
);
