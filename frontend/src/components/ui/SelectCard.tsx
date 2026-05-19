const styles = {
  base: "w-full px-4 py-3 border rounded-lg text-left transition-colors",
  active: "border-blue-600 bg-blue-50",
  inactive: "border-gray-300 hover:border-gray-400 hover:bg-gray-50",
  label: {
    active: "text-sm font-medium text-blue-700",
    inactive: "text-sm font-medium text-gray-700",
  },
  description: "text-sm text-gray-500 ml-2",
};

interface SelectCardProps {
  label: string;
  description?: string;
  selected: boolean;
  onClick: () => void;
}

export function SelectCard({ label, description, selected, onClick }: SelectCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`${styles.base} ${selected ? styles.active : styles.inactive}`}
    >
      <span className={selected ? styles.label.active : styles.label.inactive}>{label}</span>
      {description && <span className={styles.description}>{description}</span>}
    </button>
  );
}
