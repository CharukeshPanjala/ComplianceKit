import type { ReactNode } from "react";

// ── Types ──────────────────────────────────────────────
interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  action?: { label: string; onClick: () => void };
}

// ── Styles ─────────────────────────────────────────────
const styles = {
  wrapper: "flex flex-col items-center justify-center py-16 px-4 text-center",
  iconWrapper: "w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 mb-4",
  title: "text-lg font-semibold text-[#0F172A] mb-2",
  description: "text-sm text-gray-500 max-w-sm",
  button: "mt-6 px-4 py-2 bg-[#D97706] hover:bg-[#B45309] text-white text-sm font-medium rounded-lg transition-colors",
};

// ── Component ──────────────────────────────────────────
export const EmptyState = ({ icon, title, description, action }: EmptyStateProps) => (
  <div className={styles.wrapper}>
    <div className={styles.iconWrapper}>{icon}</div>
    <h3 className={styles.title}>{title}</h3>
    <p className={styles.description}>{description}</p>
    {action && (
      <button onClick={action.onClick} className={styles.button}>
        {action.label}
      </button>
    )}
  </div>
);
