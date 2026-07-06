// ── Types ──────────────────────────────────────────────
interface ProgressBarProps {
  value: number;
  height?: number;
  color?: string;
  animated?: boolean;
  label?: string;
}

// ── Styles ─────────────────────────────────────────────
const styles = {
  wrapper: "w-full",
  header: "flex items-center justify-between mb-1",
  labelText: "text-sm text-[#64748B]",
  pctText: "text-sm font-medium text-[#334155]",
  track: "w-full bg-gray-200 rounded-full overflow-hidden",
  fill: "rounded-full transition-all duration-500 ease-out",
};

// ── Component ──────────────────────────────────────────
export const ProgressBar = ({
  value,
  height = 8,
  color = "#D97706",
  animated = false,
  label,
}: ProgressBarProps) => {
  const clampedValue = Math.min(100, Math.max(0, value));

  return (
    <div className={styles.wrapper}>
      {label && (
        <div className={styles.header}>
          <span className={styles.labelText}>{label}</span>
          <span className={styles.pctText}>{clampedValue}%</span>
        </div>
      )}
      <div className={styles.track} style={{ height }}>
        <div
          className={`${styles.fill} ${animated ? "animate-pulse" : ""}`}
          style={{ width: `${clampedValue}%`, backgroundColor: color, height: "100%" }}
        />
      </div>
    </div>
  );
};
