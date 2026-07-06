// ── Types ──────────────────────────────────────────────
interface ChipProps {
  label: string;
  removable?: boolean;
  onRemove?: () => void;
  onClick?: () => void;
  selected?: boolean;
}

// ── Styles ─────────────────────────────────────────────
const styles = {
  base: "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium border transition-colors",
  selected: "bg-amber-50 border-[#D97706] text-[#D97706]",
  unselected: "bg-white border-gray-300 text-gray-700 hover:border-gray-400",
  removeBtn: "flex items-center justify-center w-4 h-4 rounded-full hover:bg-black/10 transition-colors flex-shrink-0",
};

// ── Sub-components ─────────────────────────────────────
const XIcon = () => (
  <svg className="w-2.5 h-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

// ── Component ──────────────────────────────────────────
export const Chip = ({ label, removable, onRemove, onClick, selected }: ChipProps) => {
  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    onRemove?.();
  };

  return (
    <span
      onClick={onClick}
      className={`${styles.base} ${selected ? styles.selected : styles.unselected} ${onClick ? "cursor-pointer" : "cursor-default"}`}
    >
      {label}
      {removable && (
        <button type="button" onClick={handleRemove} className={styles.removeBtn}>
          <XIcon />
        </button>
      )}
    </span>
  );
};
