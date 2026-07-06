"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { LatestAssessment, Gap, RegulationName } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const REG_COLORS: Record<RegulationName, string> = {
  GDPR: "#7C3AED",
  NIS2: "#0891B2",
  EU_AI_ACT: "#BE185D",
};

const REG_LABELS: Record<RegulationName, string> = {
  GDPR: "GDPR",
  NIS2: "NIS2",
  EU_AI_ACT: "AI Act",
};

const EXPOSURE_WEIGHTS: Record<string, number> = {
  critical: 500_000,
  high: 100_000,
  medium: 20_000,
  low: 5_000,
};

const REGS: RegulationName[] = ["GDPR", "NIS2", "EU_AI_ACT"];

// ── Styles ────────────────────────────────────────────────

const styles = {
  grid: "grid grid-cols-1 md:grid-cols-2 gap-6 items-start",
  table: "w-full rounded-lg border border-[#E2E8F0] overflow-hidden text-sm",
  thead: "bg-[#F8FAFC]",
  th: "px-4 py-2.5 text-left text-[10px] font-semibold text-[#94A3B8] uppercase tracking-wider",
  tbody: "divide-y divide-[#F1F5F9]",
  trBase: "border-l-[3px]",
  td: "px-4 py-3 text-sm text-[#64748B]",
  tdLabel: "px-4 py-3 text-sm font-semibold text-[#0F172A]",
  tdAlt: "px-4 py-3 text-sm text-[#64748B] bg-[#F8FAFC]",
  footer: "mt-3 text-xs text-[#94A3B8]",
  empty: "h-[200px] flex items-center justify-center text-sm text-[#94A3B8]",
};

// ── Types ──────────────────────────────────────────────────

interface Props {
  assessments: LatestAssessment[];
  gapsByRegulation: Record<string, Gap[]>;
}

interface RegExposure {
  reg: RegulationName;
  amount: number;
  openCount: number;
}

// ── Helpers ────────────────────────────────────────────────

const formatExposure = (amount: number): string => {
  if (amount >= 1_000_000) return `€${(amount / 1_000_000).toFixed(1)}M`;
  if (amount >= 1_000) return `€${(amount / 1_000).toFixed(0)}k`;
  return `€${amount}`;
};

const isOpen = (g: Gap) =>
  g.status === "not_met" || g.status === "partial" || g.status === "unknown";

const computeExposures = (
  assessments: LatestAssessment[],
  gapsByRegulation: Record<string, Gap[]>
): RegExposure[] => {
  if (Object.keys(gapsByRegulation).length > 0) {
    return REGS.map((reg) => {
      const regGaps = (gapsByRegulation[reg] ?? []).filter(isOpen);
      const amount = regGaps.reduce(
        (sum, g) => sum + (EXPOSURE_WEIGHTS[g.severity ?? "low"] ?? 0),
        0
      );
      return { reg, amount, openCount: regGaps.length };
    });
  }

  // Fall back to LatestAssessment approximation when gaps not yet loaded
  return assessments
    .filter((a) => a.status === "completed")
    .map((a) => ({
      reg: a.regulation,
      amount: (a.not_met_rules ?? 0) * 100_000,
      openCount: a.not_met_rules ?? 0,
    }));
};

// ── Sub-components ────────────────────────────────────────

const ExposureDonut = ({ exposures }: { exposures: RegExposure[] }) => {
  const total = exposures.reduce((s, e) => s + e.amount, 0);
  if (total === 0) {
    return <div className={styles.empty}>No exposure data yet</div>;
  }

  const data = exposures
    .filter((e) => e.amount > 0)
    .map((e) => ({
      name: REG_LABELS[e.reg],
      value: e.amount,
      color: REG_COLORS[e.reg],
    }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={55}
          outerRadius={90}
          dataKey="value"
          paddingAngle={3}
        >
          {data.map((entry) => (
            <Cell key={entry.name} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value) => [formatExposure(Number(value)), "Exposure"]}
          contentStyle={{
            borderRadius: "8px",
            border: "1px solid #E2E8F0",
            fontSize: "12px",
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
};

const ExposureTable = ({
  exposures,
  total,
}: {
  exposures: RegExposure[];
  total: number;
}) => (
  <table className={styles.table}>
    <thead className={styles.thead}>
      <tr>
        <th className={styles.th}>Regulation</th>
        <th className={styles.th}>Exposure</th>
        <th className={styles.th}>% of Total</th>
        <th className={styles.th}>Open Gaps</th>
      </tr>
    </thead>
    <tbody className={styles.tbody}>
      {exposures.map((e, i) => {
        const isEven = i % 2 === 1;
        return (
          <tr
            key={e.reg}
            className={styles.trBase}
            style={{ borderLeftColor: REG_COLORS[e.reg] }}
          >
            <td className={styles.tdLabel}>{REG_LABELS[e.reg]}</td>
            <td className={isEven ? styles.tdAlt : styles.td}>
              {formatExposure(e.amount)}
            </td>
            <td className={isEven ? styles.tdAlt : styles.td}>
              {total > 0 ? `${Math.round((e.amount / total) * 100)}%` : "—"}
            </td>
            <td className={isEven ? styles.tdAlt : styles.td}>{e.openCount}</td>
          </tr>
        );
      })}
      {exposures.length === 0 && (
        <tr>
          <td
            colSpan={4}
            className="px-4 py-6 text-center text-sm text-[#94A3B8]"
          >
            No completed assessments
          </td>
        </tr>
      )}
    </tbody>
  </table>
);

// ── Component ─────────────────────────────────────────────

export const RiskExposurePanel = ({ assessments, gapsByRegulation }: Props) => {
  const exposures = computeExposures(assessments, gapsByRegulation);
  const totalAmount = exposures.reduce((s, e) => s + e.amount, 0);
  const totalGaps = exposures.reduce((s, e) => s + e.openCount, 0);

  return (
    <div>
      <div className={styles.grid}>
        <ExposureDonut exposures={exposures} />
        <ExposureTable exposures={exposures} total={totalAmount} />
      </div>
      <p className={styles.footer}>
        Based on {totalGaps} open gaps · Max exposure excludes already-met
        controls
      </p>
    </div>
  );
};
