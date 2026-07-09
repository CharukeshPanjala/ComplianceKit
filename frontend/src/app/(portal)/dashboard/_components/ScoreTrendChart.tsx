"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useAssessmentHistory } from "@/lib/hooks/useAssessmentHistory";
import type { RegulationName } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const REG_LABELS: Record<RegulationName, string> = {
  GDPR: "GDPR",
  NIS2: "NIS2",
  EU_AI_ACT: "EU AI Act",
};

const REG_COLORS: Record<string, string> = {
  GDPR: "#7C3AED",
  NIS2: "#0891B2",
  EU_AI_ACT: "#BE185D",
};

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "bg-white rounded-2xl border border-gray-100 shadow-sm p-6",
  header: "flex items-center justify-between mb-4",
  title: "text-sm font-semibold text-gray-900",
  regBadge:
    "text-xs text-gray-400 font-medium px-2 py-1 bg-gray-100 rounded-full",
  loadingWrapper: "h-[220px] flex items-center justify-center",
  loadingBar: "w-full h-2 bg-gray-100 rounded-full overflow-hidden",
  loadingPulse: "h-full w-1/2 bg-gray-200 animate-pulse rounded-full",
  tooltipWrapper:
    "bg-white border border-[#E2E8F0] shadow-lg rounded-xl px-3 py-2",
  tooltipDate: "text-xs text-[#94A3B8] mb-1",
  tooltipScore: "text-sm font-bold text-[#0F172A]",
};

// ── Types ──────────────────────────────────────────────────

interface Props {
  regulation?: RegulationName;
}

// ── Sub-components ────────────────────────────────────────

const LoadingState = () => (
  <div className={styles.loadingWrapper}>
    <div className={styles.loadingBar}>
      <div className={styles.loadingPulse} />
    </div>
  </div>
);

const SingleTooltip = ({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { value: number }[];
  label?: string;
}) => {
  if (!active || !payload?.length) return null;
  return (
    <div className={styles.tooltipWrapper}>
      <p className={styles.tooltipDate}>{label}</p>
      <p className={styles.tooltipScore}>{payload[0].value}/100</p>
    </div>
  );
};

// ── Component ─────────────────────────────────────────────

export const ScoreTrendChart = ({ regulation }: Props) => {
  const { data: allHistory = [], isLoading } = useAssessmentHistory(undefined, 30);

  // ── Render helpers ────────────────────────────────────

  const renderEmptyState = () => (
    <div className={styles.loadingWrapper}>
      <p className="text-sm text-[#94A3B8]">Run more assessments to see your trend</p>
    </div>
  );

  const renderSingleLine = () => {
    if (isLoading) return <LoadingState />;

    const filtered = allHistory.filter((h) => h.regulation === regulation);
    const chartData = [...filtered].reverse().map((h) => ({
      date: new Date(h.completed_at).toLocaleDateString("en-GB", {
        day: "numeric",
        month: "short",
      }),
      score: h.score,
    }));

    if (chartData.length < 2) return renderEmptyState();

    return (
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#94A3B8" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 11, fill: "#94A3B8" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<SingleTooltip />} />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#D97706"
            strokeWidth={2.5}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    );
  };

  const renderMultiLine = () => {
    if (isLoading) return <LoadingState />;

    if (allHistory.length < 2) return renderEmptyState();

    const sorted = [...allHistory].sort(
      (a, b) => new Date(a.completed_at).getTime() - new Date(b.completed_at).getTime()
    );

    const running: Record<string, number | null> = { GDPR: null, NIS2: null, EU_AI_ACT: null };
    const chartData = sorted.map((h) => {
      running[h.regulation] = h.score;
      return {
        date: new Date(h.completed_at).toLocaleDateString("en-GB", { day: "numeric", month: "short" }),
        GDPR: running.GDPR,
        NIS2: running.NIS2,
        EU_AI_ACT: running.EU_AI_ACT,
      };
    });

    const regsPresent = (["GDPR", "NIS2", "EU_AI_ACT"] as const).filter(
      (r) => allHistory.some((h) => h.regulation === r)
    );

    return (
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#94A3B8" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 11, fill: "#94A3B8" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{
              borderRadius: "8px",
              border: "1px solid #E2E8F0",
              boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.07)",
            }}
          />
          <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "12px" }} />
          {regsPresent.map((r) => (
            <Line
              key={r}
              type="monotone"
              dataKey={r}
              name={REG_LABELS[r]}
              stroke={REG_COLORS[r]}
              strokeWidth={2}
              dot={false}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    );
  };

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <h3 className={styles.title}>Score Trend</h3>
        {regulation && (
          <span className={styles.regBadge}>{REG_LABELS[regulation]}</span>
        )}
      </div>
      {regulation ? renderSingleLine() : renderMultiLine()}
    </div>
  );
};
