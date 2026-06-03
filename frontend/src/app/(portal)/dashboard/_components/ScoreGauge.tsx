"use client";

import { useEffect, useState } from "react";
import type { RiskLevel } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const RISK_COLORS: Record<RiskLevel, { stroke: string; text: string; bg: string }> = {
  low: { stroke: "#22c55e", text: "text-green-600", bg: "bg-green-50" },
  medium: { stroke: "#f59e0b", text: "text-amber-600", bg: "bg-amber-50" },
  high: { stroke: "#f97316", text: "text-orange-600", bg: "bg-orange-50" },
  critical: { stroke: "#ef4444", text: "text-red-600", bg: "bg-red-50" },
};

const RISK_LABELS: Record<RiskLevel, string> = {
  low: "Low Risk",
  medium: "Medium Risk",
  high: "High Risk",
  critical: "Critical Risk",
};

const SIZES = {
  sm: { size: 100, strokeWidth: 8, fontSize: "text-xl" },
  md: { size: 140, strokeWidth: 10, fontSize: "text-3xl" },
  lg: { size: 180, strokeWidth: 12, fontSize: "text-4xl" },
};

// ── Types ─────────────────────────────────────────────────

interface ScoreGaugeProps {
  score: number;
  riskLevel: RiskLevel;
  size?: "sm" | "md" | "lg";
  animate?: boolean;
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "flex flex-col items-center gap-2",
  scoreWrapper: "relative",
  scoreText: "absolute inset-0 flex flex-col items-center justify-center",
  scoreLabel: "text-xs text-gray-400 font-medium",
  badge: "text-xs font-semibold px-2.5 py-1 rounded-full",
};

// ── Component ─────────────────────────────────────────────

export const ScoreGauge = ({ score, riskLevel, size = "md", animate = true }: ScoreGaugeProps) => {
  // ── State ────────────────────────────────────────────

  const [displayScore, setDisplayScore] = useState(animate ? 0 : score);

  const { size: svgSize, strokeWidth, fontSize } = SIZES[size];
  const colors = RISK_COLORS[riskLevel];
  const radius = (svgSize - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const center = svgSize / 2;
  const progress = displayScore / 100;
  const strokeDashoffset = circumference - progress * circumference;

  // ── Handlers ─────────────────────────────────────────

  useEffect(() => {
    if (!animate) return;
    const duration = 1000;
    const steps = 60;
    const increment = score / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= score) {
        setDisplayScore(score);
        clearInterval(timer);
      } else {
        setDisplayScore(Math.round(current));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [score, animate]);

  // ── Render helpers ────────────────────────────────────

  const renderCircle = () => (
    <svg width={svgSize} height={svgSize} className="-rotate-90">
      <circle
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        stroke="#f3f4f6"
        strokeWidth={strokeWidth}
      />
      <circle
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        stroke={colors.stroke}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={strokeDashoffset}
        style={{ transition: animate ? "stroke-dashoffset 0.05s ease" : "none" }}
      />
    </svg>
  );

  const renderScore = () => (
    <div className={styles.scoreText}>
      <span className={`${fontSize} font-bold text-gray-900`}>{displayScore}</span>
      <span className={styles.scoreLabel}>/ 100</span>
    </div>
  );

  const renderBadge = () => (
    <span className={`${styles.badge} ${colors.bg} ${colors.text}`}>{RISK_LABELS[riskLevel]}</span>
  );

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.wrapper}>
      <div className={styles.scoreWrapper}>
        {renderCircle()}
        {renderScore()}
      </div>
      {renderBadge()}
    </div>
  );
};
