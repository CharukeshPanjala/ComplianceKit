// ── Styles ─────────────────────────────────────────────────

const styles = {
  base: "px-3 py-2.5 border rounded-lg text-left flex items-center gap-2 transition-colors",
  active: "border-navy bg-navy/10",
  inactive: "border-gray-300 hover:border-gray-400",
  icon: {
    active: "text-navy w-4 flex-shrink-0 font-bold",
    inactive: "text-transparent w-4 flex-shrink-0",
  },
  label: {
    active: "text-sm font-medium text-navy",
    inactive: "text-sm text-gray-600",
  },
};

// ── Types ──────────────────────────────────────────────────

interface CheckboxCardProps {
  label: string;
  checked: boolean;
  onChange: () => void;
  className?: string;
}

// ── Component ─────────────────────────────────────────────

export function CheckboxCard({ label, checked, onChange, className = "" }: CheckboxCardProps) {
  return (
    <button
      type="button"
      onClick={onChange}
      className={`${styles.base} ${checked ? styles.active : styles.inactive} ${className}`}
    >
      <span className={checked ? styles.icon.active : styles.icon.inactive}>✓</span>
      <span className={checked ? styles.label.active : styles.label.inactive}>{label}</span>
    </button>
  );
}
