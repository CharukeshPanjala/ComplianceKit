// ── Types ──────────────────────────────────────────────
interface GaugeRingProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
}

// ── Helpers ────────────────────────────────────────────
const getColor = (score: number): string => {
  if (score < 40) return "#DC2626";
  if (score < 70) return "#D97706";
  return "#16A34A";
};

// ── Component ──────────────────────────────────────────
export const GaugeRing = ({ score, size = 120, strokeWidth = 10, label }: GaugeRingProps) => {
  const clampedScore = Math.min(100, Math.max(0, score));
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (clampedScore / 100) * circumference;
  const color = getColor(clampedScore);
  const center = size / 2;

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="#E2E8F0"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: "stroke-dashoffset 0.6s ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center rotate-0">
          <span className="text-2xl font-bold text-[#0F172A]">{clampedScore}</span>
        </div>
      </div>
      {label && <span className="text-xs text-[#64748B]">{label}</span>}
    </div>
  );
};
