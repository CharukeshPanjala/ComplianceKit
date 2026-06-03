"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useAssessmentHistory } from "@/lib/hooks/useAssessmentHistory";
import type { RegulationName } from "@/types/assessment";

// ── Types ─────────────────────────────────────────────────

interface ScoreTrendChartProps {
  regulation: RegulationName;
}

interface ChartPoint {
  date: string;
  score: number;
  risk: string;
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "bg-white rounded-2xl border border-gray-100 shadow-sm p-6",
  header: "flex items-center justify-between mb-6",
  title: "text-sm font-semibold text-gray-900",
  regulation: "text-xs text-gray-400 font-medium px-2 py-1 bg-gray-100 rounded-full",
  chartWrapper: "h-48",
  emptyWrapper: "h-48 flex flex-col items-center justify-center text-center",
  emptyIcon: "w-10 h-10 text-gray-200 mb-2",
  emptyText: "text-sm text-gray-400",
  emptySubtext: "text-xs text-gray-300 mt-1",
  loadingWrapper: "h-48 flex items-center justify-center",
  loadingBar: "w-full h-2 bg-gray-100 rounded-full overflow-hidden",
  loadingPulse: "h-full w-1/2 bg-gray-200 animate-pulse rounded-full",
  tooltipWrapper: "bg-white border border-gray-100 shadow-lg rounded-xl px-3 py-2",
  tooltipDate: "text-xs text-gray-400 mb-1",
  tooltipScore: "text-sm font-bold text-navy",
};

const REG_LABELS: Record<RegulationName, string> = {
  GDPR: "GDPR",
  NIS2: "NIS2",
  EU_AI_ACT: "EU AI Act",
};

// ── Helpers ───────────────────────────────────────────────

const formatDate = (dateStr: string) =>
  new Date(dateStr).toLocaleDateString("en-GB", { day: "numeric", month: "short" });

const buildChartData = (
  history: { score: number; risk_level: string; completed_at: string }[]
): ChartPoint[] =>
  [...history].reverse().map((h) => ({
    date: formatDate(h.completed_at),
    score: h.score,
    risk: h.risk_level,
  }));

// ── Sub-components ────────────────────────────────────────

const CustomTooltip = ({
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

const EmptyState = () => (
  <div className={styles.emptyWrapper}>
    <svg className={styles.emptyIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1}
        d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"
      />
    </svg>
    <p className={styles.emptyText}>No history yet</p>
    <p className={styles.emptySubtext}>Run assessments to see your score trend</p>
  </div>
);

const LoadingState = () => (
  <div className={styles.loadingWrapper}>
    <div className={styles.loadingBar}>
      <div className={styles.loadingPulse} />
    </div>
  </div>
);

// ── Component ─────────────────────────────────────────────

export const ScoreTrendChart = ({ regulation }: ScoreTrendChartProps) => {
  const { data: history = [], isLoading } = useAssessmentHistory(regulation, 10);

  const chartData = buildChartData(history);
  const hasData = chartData.length > 1;

  // ── Render helpers ────────────────────────────────────

  const renderHeader = () => (
    <div className={styles.header}>
      <h3 className={styles.title}>Score History</h3>
      <span className={styles.regulation}>{REG_LABELS[regulation]}</span>
    </div>
  );

  const renderChart = () => (
    <div className={styles.chartWrapper}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#9ca3af" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 11, fill: "#9ca3af" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#1e3a5f"
            strokeWidth={2.5}
            dot={{ fill: "#1e3a5f", strokeWidth: 0, r: 4 }}
            activeDot={{ r: 6, fill: "#f59e0b" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.wrapper}>
      {renderHeader()}
      {isLoading && <LoadingState />}
      {!isLoading && !hasData && <EmptyState />}
      {!isLoading && hasData && renderChart()}
    </div>
  );
};
