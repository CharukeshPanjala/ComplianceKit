"use client";

import { GaugeRing } from "@/components/ui/GaugeRing";
import type { LatestAssessment, Gap } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const EXPOSURE_WEIGHTS: Record<string, number> = {
  critical: 500_000,
  high: 100_000,
  medium: 20_000,
  low: 5_000,
};

// ── Styles ────────────────────────────────────────────────

const styles = {
  grid: "grid grid-cols-2 lg:grid-cols-4 gap-4",
  card: "bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-5 flex flex-col items-center gap-1 text-center",
  label: "text-xs font-semibold text-[#64748B] tracking-widest uppercase mt-1",
  sub: "text-xs text-[#94A3B8]",
  valueAmber: "text-3xl font-bold text-[#D97706]",
  valueRed: "text-3xl font-bold text-red-600",
  valueGreen: "text-3xl font-bold text-[#16A34A]",
  valueGray: "text-3xl font-bold text-[#94A3B8]",
};

// ── Types ──────────────────────────────────────────────────

interface Props {
  assessments: LatestAssessment[];
  gaps: Gap[];
}

// ── Helpers ────────────────────────────────────────────────

const formatExposure = (amount: number): string => {
  if (amount >= 1_000_000) return `€${(amount / 1_000_000).toFixed(1)}M`;
  if (amount >= 1_000) return `€${(amount / 1_000).toFixed(0)}k`;
  return `€${amount}`;
};

const isOpen = (gap: Gap) =>
  gap.status === "not_met" || gap.status === "partial" || gap.status === "unknown";

// ── Component ─────────────────────────────────────────────

export const ExecutiveSummaryBar = ({ assessments, gaps }: Props) => {
  // ── Render helpers ─────────────────────────────────────

  const renderOverallScore = () => {
    const completed = assessments.filter(
      (a) => a.status === "completed" && a.score !== null
    );
    const score =
      completed.length > 0
        ? Math.round(
            completed.reduce((sum, a) => sum + (a.score ?? 0), 0) /
              completed.length
          )
        : 0;
    return (
      <div className={styles.card}>
        <GaugeRing score={score} size={72} strokeWidth={7} />
        <span className={styles.label}>Overall Score</span>
      </div>
    );
  };

  const renderExposure = () => {
    let total = 0;
    try {
      gaps.filter(isOpen).forEach((g) => {
        total += EXPOSURE_WEIGHTS[g.severity ?? "low"] ?? 0;
      });
    } catch {
      total = 0;
    }
    return (
      <div className={styles.card}>
        <span className={styles.valueAmber}>{formatExposure(total)}</span>
        <span className={styles.label}>Risk Exposure</span>
        <span className={styles.sub}>Maximum fine exposure</span>
      </div>
    );
  };

  const renderCritical = () => {
    const count = gaps.filter(
      (g) => g.severity === "critical" && g.status !== "met"
    ).length;
    const cls = count > 0 ? styles.valueRed : styles.valueGreen;
    return (
      <div className={styles.card}>
        <span className={cls}>{count}</span>
        <span className={styles.label}>Critical Items</span>
        <span className={styles.sub}>Unresolved critical gaps</span>
      </div>
    );
  };

  const renderDeadline = () => {
    const withDeadlines = gaps
      .filter((g) => g.due_date && isOpen(g))
      .map((g) => ({
        days: Math.ceil(
          (new Date(g.due_date!).getTime() - Date.now()) / 86_400_000
        ),
      }))
      .filter((d) => d.days >= 0)
      .sort((a, b) => a.days - b.days);

    if (withDeadlines.length === 0) {
      return (
        <div className={styles.card}>
          <span className={styles.valueGray}>None</span>
          <span className={styles.label}>Next Deadline</span>
          <span className={styles.sub}>No upcoming deadlines</span>
        </div>
      );
    }

    const days = withDeadlines[0].days;
    const cls =
      days < 7
        ? styles.valueRed
        : days < 30
          ? styles.valueAmber
          : styles.valueGreen;

    return (
      <div className={styles.card}>
        <span className={cls}>{days}d</span>
        <span className={styles.label}>Next Deadline</span>
        <span className={styles.sub}>days remaining</span>
      </div>
    );
  };

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.grid}>
      {renderOverallScore()}
      {renderExposure()}
      {renderCritical()}
      {renderDeadline()}
    </div>
  );
};
