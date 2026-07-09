// ── Types ──────────────────────────────────────────────
type Regulation = "GDPR" | "NIS2" | "EU_AI_ACT";
type Size = "sm" | "md";

interface RegulationBadgeProps {
  regulation: Regulation;
  size?: Size;
}

// ── Constants ──────────────────────────────────────────
const LABELS: Record<Regulation, string> = {
  GDPR: "GDPR",
  NIS2: "NIS2",
  EU_AI_ACT: "AI Act",
};

const VARIANT_CLASSES: Record<Regulation, string> = {
  GDPR: "bg-purple-100 text-purple-700 border-purple-200",
  NIS2: "bg-cyan-100 text-cyan-700 border-cyan-200",
  EU_AI_ACT: "bg-pink-100 text-pink-700 border-pink-200",
};

const SIZE_CLASSES: Record<Size, string> = {
  sm: "text-xs px-2 py-0.5",
  md: "text-sm px-2.5 py-1",
};

// ── Styles ─────────────────────────────────────────────
const styles = {
  base: "font-medium rounded-full border inline-flex items-center",
};

// ── Component ──────────────────────────────────────────
export const RegulationBadge = ({ regulation, size = "sm" }: RegulationBadgeProps) => (
  <span className={`${styles.base} ${VARIANT_CLASSES[regulation]} ${SIZE_CLASSES[size]}`}>
    {LABELS[regulation]}
  </span>
);
