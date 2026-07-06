import type { ReactNode } from "react";

// ── Types ──────────────────────────────────────────────
type BadgeVariant =
  | "success"
  | "warning"
  | "danger"
  | "info"
  | "gdpr"
  | "nis2"
  | "ai-act"
  | "soon"
  | "outline"
  | "grey";

interface BadgeProps {
  variant: BadgeVariant;
  children: ReactNode;
  dot?: boolean;
}

// ── Styles ─────────────────────────────────────────────
const VARIANT_CLASSES: Record<BadgeVariant, string> = {
  success: "bg-green-100 text-green-700 border-green-200",
  warning: "bg-amber-100 text-amber-700 border-amber-200",
  danger: "bg-red-100 text-red-700 border-red-200",
  info: "bg-cyan-100 text-cyan-700 border-cyan-200",
  gdpr: "bg-purple-100 text-purple-700 border-purple-200",
  nis2: "bg-cyan-100 text-cyan-700 border-cyan-200",
  "ai-act": "bg-pink-100 text-pink-700 border-pink-200",
  soon: "bg-gray-100 text-gray-500 border-gray-200",
  outline: "bg-white text-gray-700 border-gray-300",
  grey: "bg-gray-100 text-gray-600 border-gray-200",
};

const DOT_CLASSES: Record<BadgeVariant, string> = {
  success: "bg-green-500",
  warning: "bg-amber-500",
  danger: "bg-red-500",
  info: "bg-cyan-500",
  gdpr: "bg-purple-500",
  nis2: "bg-cyan-500",
  "ai-act": "bg-pink-500",
  soon: "bg-gray-400",
  outline: "bg-gray-500",
  grey: "bg-gray-400",
};

const styles = {
  base: "text-xs font-medium px-2 py-0.5 rounded-full border inline-flex items-center gap-1",
  dot: "w-1.5 h-1.5 rounded-full flex-shrink-0",
};

// ── Component ──────────────────────────────────────────
export const Badge = ({ variant, children, dot }: BadgeProps) => (
  <span className={`${styles.base} ${VARIANT_CLASSES[variant]}`}>
    {dot && <span className={`${styles.dot} ${DOT_CLASSES[variant]}`} />}
    {children}
  </span>
);
