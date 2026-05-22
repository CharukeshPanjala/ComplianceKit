"use client";

import { useState } from "react";

// ── Styles ─────────────────────────────────────────────────

const styles = {
  wrapper: "relative inline-flex items-center cursor-pointer group",
  icon: "w-4 h-4 text-gray-400",
  box: "absolute left-0 top-6 z-10 w-64 bg-gray-900 text-white text-xs rounded-lg px-3 py-2 shadow-lg hidden group-hover:block",
};

// ── Types ──────────────────────────────────────────────────

interface TooltipProps {
  text: string;
}

// ── Component ─────────────────────────────────────────────

export function Tooltip({ text }: TooltipProps) {
  const [open, setOpen] = useState(false);

  return (
    <span className={styles.wrapper} onClick={() => setOpen((o) => !o)}>
      <svg className={styles.icon} fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
          clipRule="evenodd"
        />
      </svg>
      <span className={`${styles.box} ${open ? "!block" : ""}`}>{text}</span>
    </span>
  );
}
