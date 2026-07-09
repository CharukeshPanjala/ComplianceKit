"use client";

import { useEffect, useState } from "react";

// ── Constants ─────────────────────────────────────────
const RING_CIRCUMFERENCE = 138.2;
const SCORE_PERCENT = 87;

// ── Styles ────────────────────────────────────────────
const styles = {
  page: "flex min-h-screen",
  leftPanel: "hidden lg:flex lg:w-1/2 bg-navy flex-col justify-between p-12",
  logo: "text-white font-bold text-xl tracking-tight",
  cardWrapper: "relative h-[130px] w-[92%] mb-6",
  cardBack: "absolute top-3.5 left-3.5 -right-2.5 h-[100px] bg-[#e7d9c4] rounded-lg shadow-md",
  cardMid: "absolute top-1.5 left-1.5 -right-0.5 h-[106px] bg-[#bcd1e8] rounded-lg shadow-md",
  cardFront: "absolute top-0 left-0 right-1.5 bg-warm-white rounded-lg p-4 shadow-lg",
  cardHeader: "flex items-center justify-between mb-2.5",
  cardTitle: "text-xs font-medium text-navy",
  previewBadge: "text-[10px] text-gray-400 border border-gray-200 rounded px-1.5 py-0.5",
  cardBody: "flex items-center gap-3",
  cardStats: "text-[11px] leading-5",
  statMet: "text-green-700",
  statPartial: "text-amber-700",
  headline: "text-4xl font-bold text-white leading-snug mb-4",
  subtext: "text-blue-200 text-lg leading-relaxed max-w-sm",
  footerNote: "text-blue-300 text-sm",
  rightPanel: "flex flex-1 items-center justify-center bg-warm-white p-8",
};

// ── Component ─────────────────────────────────────────
const AuthLayout = ({ children }: { children: React.ReactNode }) => {
  // ── State ───────────────────────────────────────────
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const dashOffset = mounted
    ? RING_CIRCUMFERENCE - (RING_CIRCUMFERENCE * SCORE_PERCENT) / 100
    : RING_CIRCUMFERENCE;

  // ── Render ──────────────────────────────────────────
  return (
    <div className={styles.page}>
      {/* Left — Navy brand panel */}
      <div className={styles.leftPanel}>
        <span className={styles.logo}>ComplianceKit</span>

        <div>
          {/* Stacked compliance score card */}
          <div className={styles.cardWrapper}>
            <div className={styles.cardBack} />
            <div className={styles.cardMid} />
            <div className={styles.cardFront}>
              <div className={styles.cardHeader}>
                <span className={styles.cardTitle}>GDPR readiness</span>
                <span className={styles.previewBadge}>Preview</span>
              </div>
              <div className={styles.cardBody}>
                <svg width="56" height="56" viewBox="0 0 56 56">
                  <circle cx="28" cy="28" r="22" fill="none" stroke="#f3f4f6" strokeWidth="7" />
                  <circle
                    cx="28"
                    cy="28"
                    r="22"
                    fill="none"
                    stroke="#22c55e"
                    strokeWidth="7"
                    strokeLinecap="round"
                    strokeDasharray={RING_CIRCUMFERENCE}
                    strokeDashoffset={dashOffset}
                    transform="rotate(-90 28 28)"
                    style={{ transition: "stroke-dashoffset 1s ease-out" }}
                  />
                  <text x="28" y="32" textAnchor="middle" fontSize="13" fontWeight="500" fill="#1e3a5f">
                    {SCORE_PERCENT}%
                  </text>
                </svg>
                <div className={styles.cardStats}>
                  <div className={styles.statMet}>● 12 requirements met</div>
                  <div className={styles.statPartial}>● 4 partially met</div>
                </div>
              </div>
            </div>
          </div>

          <h1 className={styles.headline}>
            Find the gaps
            <br />
            before the regulator does.
          </h1>
          <p className={styles.subtext}>AI-powered compliance scoring, fully automated.</p>
        </div>

        <p className={styles.footerNote}>Built for GDPR, NIS2 & EU AI Act deadlines</p>
      </div>

      {/* Right — Clerk form */}
      <div className={styles.rightPanel}>{children}</div>
    </div>
  );
};

export default AuthLayout;
