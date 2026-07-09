"use client";

import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { Gap } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const SEVERITY_COLORS = {
  critical: "#EF4444",
  high: "#F97316",
  medium: "#EAB308",
  low: "#22C55E",
} as const;

// ── Styles ────────────────────────────────────────────────

const styles = {
  grid: "grid grid-cols-1 md:grid-cols-2 gap-6",
  panel: "flex flex-col gap-3",
  panelTitle: "text-xs font-semibold text-[#64748B] uppercase tracking-wider",
  donutWrapper: "relative",
  donutCenter: "absolute inset-0 flex flex-col items-center justify-center pointer-events-none",
  donutTotal: "text-2xl font-bold text-[#0F172A]",
  donutSub: "text-xs text-[#94A3B8]",
  empty: "h-[220px] flex items-center justify-center text-sm text-[#94A3B8]",
};

// ── Constants ─────────────────────────────────────────────

const REG_DISPLAY: Record<string, string> = {
  GDPR: "GDPR",
  NIS2: "NIS2",
  EU_AI_ACT: "AI Act",
};

// ── Types ──────────────────────────────────────────────────

interface Props {
  gapsByRegulation: Record<string, Gap[]>;
}

// ── Helpers ────────────────────────────────────────────────

const isOpen = (g: Gap) =>
  g.status === "not_met" || g.status === "partial" || g.status === "unknown";

// ── Sub-components ────────────────────────────────────────

const SeverityDonut = ({ gaps }: { gaps: Gap[] }) => {
  const open = gaps.filter(isOpen);
  const counts = {
    critical: open.filter((g) => g.severity === "critical").length,
    high: open.filter((g) => g.severity === "high").length,
    medium: open.filter((g) => g.severity === "medium").length,
    low: open.filter((g) => g.severity === "low").length,
  };

  const data = (
    Object.entries(counts) as [keyof typeof SEVERITY_COLORS, number][]
  )
    .filter(([, v]) => v > 0)
    .map(([k, v]) => ({
      name: k.charAt(0).toUpperCase() + k.slice(1),
      value: v,
      color: SEVERITY_COLORS[k],
    }));

  if (data.length === 0) {
    return <div className={styles.empty}>No open gaps</div>;
  }

  return (
    <div className={styles.donutWrapper}>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={85}
            dataKey="value"
            paddingAngle={2}
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              borderRadius: "8px",
              border: "1px solid #E2E8F0",
              fontSize: "12px",
            }}
          />
          <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
        </PieChart>
      </ResponsiveContainer>
      <div className={styles.donutCenter}>
        <span className={styles.donutTotal}>{open.length}</span>
        <span className={styles.donutSub}>open</span>
      </div>
    </div>
  );
};

const RegBarChart = ({ gapsByRegulation }: { gapsByRegulation: Record<string, Gap[]> }) => {
  const byReg = Object.entries(gapsByRegulation).map(([regKey, regGaps]) => {
    const open = regGaps.filter(isOpen);
    return {
      name: REG_DISPLAY[regKey] ?? regKey,
      Critical: open.filter((g) => g.severity === "critical").length,
      High: open.filter((g) => g.severity === "high").length,
      Medium: open.filter((g) => g.severity === "medium").length,
    };
  });

  const hasData = byReg.some((r) => r.Critical + r.High + r.Medium > 0);

  if (!hasData) {
    return <div className={styles.empty}>Run assessments to see data</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={byReg} margin={{ top: 5, right: 5, bottom: 5, left: -15 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
        <XAxis
          dataKey="name"
          tick={{ fontSize: 11, fill: "#94A3B8" }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 11, fill: "#94A3B8" }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={{ borderRadius: "8px", border: "1px solid #E2E8F0", fontSize: "12px" }}
        />
        <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
        <Bar dataKey="Critical" fill={SEVERITY_COLORS.critical} radius={[2, 2, 0, 0]} />
        <Bar dataKey="High" fill={SEVERITY_COLORS.high} radius={[2, 2, 0, 0]} />
        <Bar dataKey="Medium" fill={SEVERITY_COLORS.medium} radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
};

// ── Component ─────────────────────────────────────────────

export const GapChartsRow = ({ gapsByRegulation }: Props) => {
  const allGaps = Object.values(gapsByRegulation).flat();
  return (
    <div className={styles.grid}>
      <div className={styles.panel}>
        <p className={styles.panelTitle}>Gap Severity Distribution</p>
        <SeverityDonut gaps={allGaps} />
      </div>
      <div className={styles.panel}>
        <p className={styles.panelTitle}>Open Gaps by Regulation</p>
        <RegBarChart gapsByRegulation={gapsByRegulation} />
      </div>
    </div>
  );
};
