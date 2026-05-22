// ── Styles ─────────────────────────────────────────────────

const styles = {
  base: "w-full px-4 py-3 border rounded-lg text-left transition-colors",
  active: "border-navy bg-navy/10",
  inactive: "border-gray-300 hover:border-gray-400 hover:bg-gray-50",
  label: {
    active: "text-sm font-medium text-navy",
    inactive: "text-sm font-medium text-gray-700",
  },
  description: "text-xs text-gray-400 mt-0.5",
};

// ── Types ──────────────────────────────────────────────────

interface SelectCardProps {
  label: string;
  description?: string;
  selected: boolean;
  onClick: () => void;
}

// ── Component ─────────────────────────────────────────────

export function SelectCard({ label, description, selected, onClick }: SelectCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`${styles.base} ${selected ? styles.active : styles.inactive}`}
    >
      <div className="flex flex-col items-start">
        <span className={selected ? styles.label.active : styles.label.inactive}>{label}</span>
        {description && <span className={styles.description}>{description}</span>}
      </div>
    </button>
  );
}
