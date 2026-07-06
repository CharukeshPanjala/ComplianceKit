import type { ReactNode } from "react";

// ── Types ──────────────────────────────────────────────
interface FilterBarProps {
  children: ReactNode;
  rightSlot?: ReactNode;
}

// ── Styles ─────────────────────────────────────────────
const styles = {
  wrapper: "bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-4",
  inner: "flex items-center gap-3 flex-wrap",
  left: "flex items-center gap-3 flex-wrap flex-1",
  right: "flex items-center gap-3 flex-shrink-0",
};

// ── Component ──────────────────────────────────────────
export const FilterBar = ({ children, rightSlot }: FilterBarProps) => (
  <div className={styles.wrapper}>
    <div className={styles.inner}>
      <div className={styles.left}>{children}</div>
      {rightSlot && <div className={styles.right}>{rightSlot}</div>}
    </div>
  </div>
);
