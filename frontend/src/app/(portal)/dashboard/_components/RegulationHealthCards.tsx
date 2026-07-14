"use client";

import { GaugeRing } from "@/components/ui/GaugeRing";
import { useTriggerAssessment } from "@/lib/hooks/useTriggerAssessment";
import type { LatestAssessment, Gap, RegulationName } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const REG_CONFIG: Record<RegulationName, { label: string; color: string }> = {
  GDPR: { label: "GDPR", color: "#7C3AED" },
  NIS2: { label: "NIS2", color: "#0891B2" },
  EU_AI_ACT: { label: "AI Act", color: "#BE185D" },
};

const REGS: RegulationName[] = ["GDPR", "NIS2", "EU_AI_ACT"];

// ── Styles ────────────────────────────────────────────────

const styles = {
  grid: "grid grid-cols-1 md:grid-cols-3 gap-4",
  card: "bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-5 flex flex-col gap-4",
  cardHeader: "flex items-center justify-between",
  regLabel: "text-sm font-bold text-[#0F172A]",
  regBadge: "text-[10px] font-bold px-2 py-0.5 rounded-full text-white uppercase tracking-wide",
  statusChip: "text-[10px] font-semibold px-2 py-0.5 rounded-full border",
  gaugeRow: "flex justify-center",
  statsRow: "grid grid-cols-4 gap-1 text-center",
  statBox: "flex flex-col",
  statVal: "text-sm font-bold",
  statLabel: "text-[10px] text-[#94A3B8]",
  deadlineText: "text-xs text-[#64748B]",
  actions: "flex gap-2 mt-auto pt-2 border-t border-[#F1F5F9]",
  viewBtn: "flex-1 text-xs font-medium py-1.5 rounded-lg border border-[#E2E8F0] text-[#334155] hover:bg-gray-50 transition-colors",
  reassessBtn: "flex-1 text-xs font-medium py-1.5 rounded-lg border border-[#E2E8F0] text-[#334155] hover:bg-gray-50 transition-colors disabled:opacity-40",
  skeletonPulse: "bg-[#F1F5F9] rounded animate-pulse",
  notRunText: "text-sm text-[#94A3B8] text-center py-4",
};

// ── Types ──────────────────────────────────────────────────

interface Props {
  assessments: LatestAssessment[];
  gapsByRegulation: Record<string, Gap[]>;
  onViewGaps: (assessmentId: string, regulation: RegulationName) => void;
}

// ── Helpers ────────────────────────────────────────────────

const getStatusChip = (score: number | null) => {
  if (score === null)
    return { label: "Pending", cls: "border-gray-200 text-gray-400 bg-gray-50" };
  if (score < 40) return { label: "At Risk", cls: "border-red-200 text-red-600 bg-red-50" };
  if (score < 70) return { label: "Improving", cls: "border-amber-200 text-amber-700 bg-amber-50" };
  return { label: "On Track", cls: "border-green-200 text-green-700 bg-green-50" };
};

const isOpen = (g: Gap) => g.status === "not_met" || g.status === "partial" || g.status === "unknown";

// ── Sub-components ────────────────────────────────────────

const NotApplicableCard = ({
  reg,
  reason,
}: {
  reg: RegulationName;
  reason?: string | null;
}) => {
  const cfg = REG_CONFIG[reg];
  return (
    <div className={`${styles.card} border-dashed bg-gray-50`}>
      <div className={styles.cardHeader}>
        <span className={styles.regLabel}>{cfg.label}</span>
        <span
          className={styles.regBadge}
          style={{ backgroundColor: cfg.color, opacity: 0.4 }}
        >
          {cfg.label}
        </span>
      </div>
      <div className="flex flex-col items-center gap-2 py-2">
        <span className="text-2xl">🛈</span>
        <p className="text-xs font-semibold text-[#64748B] uppercase tracking-wide">
          Not applicable
        </p>
      </div>
      {reason && (
        <p className="text-xs text-[#64748B] leading-relaxed bg-white border border-[#E2E8F0] rounded-lg px-3 py-2.5">
          {reason}
        </p>
      )}
    </div>
  );
};

const InsufficientDataCard = ({
  reg,
  unknownRules,
  totalRules,
  onReassess,
  isTriggering,
}: {
  reg: RegulationName;
  unknownRules: number;
  totalRules: number;
  onReassess: () => void;
  isTriggering: boolean;
}) => {
  const cfg = REG_CONFIG[reg];
  return (
    <div className={`${styles.card} border-amber-200 bg-amber-50`}>
      <div className={styles.cardHeader}>
        <span className={styles.regLabel}>{cfg.label}</span>
        <span className={styles.regBadge} style={{ backgroundColor: cfg.color }}>{cfg.label}</span>
      </div>
      <div className="flex flex-col items-center gap-2 py-2 text-center">
        <span className="text-2xl">📋</span>
        <p className="text-xs font-semibold text-amber-800 uppercase tracking-wide">
          No scoreable articles yet
        </p>
        <p className="text-xs text-amber-700 leading-relaxed px-1">
          {unknownRules} of {totalRules} articles require documentation uploads before a score can be calculated.
        </p>
      </div>
      <div className={styles.actions}>
        <button
          onClick={onReassess}
          disabled={isTriggering}
          className={styles.reassessBtn}
        >
          {isTriggering ? "Starting..." : "Re-assess"}
        </button>
      </div>
    </div>
  );
};

const SkeletonCard = ({ reg }: { reg: RegulationName }) => {
  const cfg = REG_CONFIG[reg];
  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <span className={styles.regLabel}>{cfg.label}</span>
        <span className={styles.regBadge} style={{ backgroundColor: cfg.color }}>{cfg.label}</span>
      </div>
      <div className={`${styles.skeletonPulse} h-16 w-16 mx-auto rounded-full`} />
      <div className={`${styles.skeletonPulse} h-4 w-full`} />
      <p className="text-xs text-center text-[#94A3B8]">Recalculating...</p>
    </div>
  );
};

// ── Component ─────────────────────────────────────────────

export const RegulationHealthCards = ({ assessments, gapsByRegulation, onViewGaps }: Props) => {
  const {
    mutate: triggerOne,
    isPending: isTriggering,
    variables: triggeringReg,
  } = useTriggerAssessment();

  const renderCard = (reg: RegulationName) => {
    const cfg = REG_CONFIG[reg];
    const assessment = assessments.find((a) => a.regulation === reg);

    if (!assessment) {
      return (
        <div key={reg} className={styles.card}>
          <div className={styles.cardHeader}>
            <span className={styles.regLabel}>{cfg.label}</span>
            <span className={styles.regBadge} style={{ backgroundColor: cfg.color }}>{cfg.label}</span>
          </div>
          <p className={styles.notRunText}>Not assessed yet</p>
          <div className={styles.actions}>
            <button
              onClick={() => triggerOne(reg)}
              disabled={isTriggering && triggeringReg === reg}
              className={styles.reassessBtn}
            >
              {isTriggering && triggeringReg === reg ? "Starting..." : "Assess"}
            </button>
          </div>
        </div>
      );
    }

    if (assessment.status === "pending" || assessment.status === "running") {
      return <SkeletonCard key={reg} reg={reg} />;
    }

    if (assessment.insufficient_data) {
      return (
        <InsufficientDataCard
          key={reg}
          reg={reg}
          unknownRules={assessment.unknown_rules ?? 0}
          totalRules={(assessment.met_rules ?? 0) + (assessment.partial_rules ?? 0) + (assessment.not_met_rules ?? 0) + (assessment.unknown_rules ?? 0)}
          onReassess={() => triggerOne(reg)}
          isTriggering={isTriggering && triggeringReg === reg}
        />
      );
    }

    if ((assessment.status as string) === "not_applicable") {
      return (
        <NotApplicableCard
          key={reg}
          reg={reg}
          reason={assessment.not_applicable_reason}
        />
      );
    }

    const score = assessment.score ?? 0;
    const chip = getStatusChip(assessment.score);
    const coveragePct = assessment.coverage_pct ?? 100;
    const isPartial = assessment.score !== null && coveragePct < 80;
    const regGaps = gapsByRegulation[reg] ?? [];
    const openGaps = regGaps.filter(isOpen);

    const counts = {
      critical: openGaps.filter((g) => g.severity === "critical").length,
      high: openGaps.filter((g) => g.severity === "high").length,
      medium: openGaps.filter((g) => g.severity === "medium").length,
      low: openGaps.filter((g) => g.severity === "low").length,
    };

    const upcoming = regGaps
      .filter((g) => g.due_date && isOpen(g))
      .map((g) => new Date(g.due_date!).getTime())
      .filter((t) => t > Date.now())
      .sort((a, b) => a - b);

    const nextDeadline =
      upcoming.length > 0
        ? `Next deadline: ${Math.ceil((upcoming[0] - Date.now()) / 86_400_000)}d`
        : "No deadlines";

    const handleViewGaps = () => {
      if (assessment.assessment_id) onViewGaps(assessment.assessment_id, reg);
    };

    return (
      <div key={reg} className={styles.card}>
        <div className={styles.cardHeader}>
          <span className={styles.regLabel}>{cfg.label}</span>
          <div className="flex items-center gap-1.5">
            <span className={styles.regBadge} style={{ backgroundColor: cfg.color }}>{cfg.label}</span>
            <span className={`${styles.statusChip} ${chip.cls}`}>{chip.label}</span>
            {isPartial && (
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full border border-amber-300 text-amber-700 bg-amber-50">
                Partial
              </span>
            )}
          </div>
        </div>

        <div className={styles.gaugeRow}>
          <GaugeRing score={score} size={80} strokeWidth={7} />
        </div>
        {isPartial && (
          <p className="text-[11px] text-center text-amber-600">
            Based on {coveragePct}% of articles
          </p>
        )}

        <div className={styles.statsRow}>
          {[
            { label: "Critical", val: counts.critical, color: "text-red-500" },
            { label: "High", val: counts.high, color: "text-orange-500" },
            { label: "Medium", val: counts.medium, color: "text-amber-500" },
            { label: "Low", val: counts.low, color: "text-green-600" },
          ].map(({ label, val, color }) => (
            <div key={label} className={styles.statBox}>
              <span className={`${styles.statVal} ${color}`}>{val}</span>
              <span className={styles.statLabel}>{label}</span>
            </div>
          ))}
        </div>

        <p className={styles.deadlineText}>{nextDeadline}</p>

        <div className={styles.actions}>
          {assessment.assessment_id && (
            <button onClick={handleViewGaps} className={styles.viewBtn}>
              View {openGaps.length} gaps
            </button>
          )}
          <button
            onClick={() => triggerOne(reg)}
            disabled={isTriggering && triggeringReg === reg}
            className={styles.reassessBtn}
          >
            {isTriggering && triggeringReg === reg ? "Starting..." : "Re-assess"}
          </button>
        </div>
      </div>
    );
  };

  return <div className={styles.grid}>{REGS.map(renderCard)}</div>;
};
