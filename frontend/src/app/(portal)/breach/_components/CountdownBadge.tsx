"use client";

import { useEffect, useState } from "react";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  badge: {
    base: "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold tabular-nums",
    critical: "bg-red-100 text-red-700 border border-red-200",
    warning: "bg-amber-100 text-amber-700 border border-amber-200",
    ok: "bg-green-100 text-green-700 border border-green-200",
    done: "bg-gray-100 text-gray-500 border border-gray-200",
  },
  dot: {
    base: "w-1.5 h-1.5 rounded-full",
    critical: "bg-red-500 animate-pulse",
    warning: "bg-amber-500",
    ok: "bg-green-500",
    done: "bg-gray-400",
  },
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface Props {
  deadlineAt: string;
  hoursWindow: number;
  dpaNotified: boolean;
}

// ── Component ─────────────────────────────────────────────────────────────────

export const CountdownBadge = ({ deadlineAt, hoursWindow, dpaNotified }: Props) => {
  const [hoursLeft, setHoursLeft] = useState<number | null>(null);

  useEffect(() => {
    const calc = () => {
      const diff = (new Date(deadlineAt).getTime() - Date.now()) / 3_600_000;
      setHoursLeft(Math.max(0, diff));
    };
    calc();
    const id = setInterval(calc, 60_000);
    return () => clearInterval(id);
  }, [deadlineAt]);

  if (dpaNotified) {
    return (
      <span className={`${styles.badge.base} ${styles.badge.done}`}>
        <span className={`${styles.dot.base} ${styles.dot.done}`} />
        Notified
      </span>
    );
  }

  if (hoursLeft === null) return null;

  const passed = hoursLeft <= 0;
  const variant = passed || hoursLeft < 6
    ? "critical"
    : hoursLeft < 24
    ? "warning"
    : "ok";

  const label = passed
    ? "OVERDUE"
    : hoursLeft < 1
    ? `${Math.round(hoursLeft * 60)}m left`
    : `${Math.round(hoursLeft)}h / ${hoursWindow}h`;

  return (
    <span className={`${styles.badge.base} ${styles.badge[variant]}`}>
      <span className={`${styles.dot.base} ${styles.dot[variant]}`} />
      {label}
    </span>
  );
};
