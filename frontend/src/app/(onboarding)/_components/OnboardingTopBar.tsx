"use client";

import { usePathname } from "next/navigation";

// ── Constants ─────────────────────────────────────────────
const PHASES = [
  { label: "Company Basics", steps: [1, 2, 3] },
  { label: "Regulations", steps: [4] },
  { label: "Configure", steps: [5, 6] },
];

const TOTAL_STEPS = 6;

// ── Styles ─────────────────────────────────────────────────
const styles = {
  topBar: "bg-white border-b border-gray-100 px-6 py-4",
  topBarInner: "flex items-center justify-between max-w-4xl mx-auto",
  logo: "flex items-center gap-2.5",
  logoIcon: "w-8 h-8 bg-[#D97706] rounded-lg flex items-center justify-center",
  logoIconText: "text-white font-bold text-sm",
  logoName: "text-[#0F172A] font-bold text-lg",
  stepIndicator: "text-sm text-[#64748B] font-medium",
  stepperWrapper: "border-b border-gray-100 px-6 py-4 bg-white",
  stepperInner: "flex items-start max-w-4xl mx-auto",
  phaseWrapper: "flex items-center",
  phaseContent: "flex flex-col items-center",
  circleBase: "w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0",
  circleDone: "bg-green-500 text-white",
  circleCurrent: "bg-[#D97706] text-white",
  circlePending: "bg-gray-200 text-gray-400",
  phaseLabel: "text-xs mt-1.5 font-medium whitespace-nowrap",
  labelDone: "text-green-600",
  labelCurrent: "text-[#D97706] font-bold",
  labelPending: "text-gray-400",
  connector: "h-0.5 flex-1 mx-3 mt-3.5",
  connectorDone: "bg-green-300",
  connectorPending: "bg-gray-200",
};

// ── Sub-components ──────────────────────────────────────────
const CheckIcon = () => (
  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
  </svg>
);

// ── Component ───────────────────────────────────────────────
export const OnboardingTopBar = () => {
  const pathname = usePathname();
  const match = pathname.match(/\/onboarding\/step\/(\d+)/);
  const currentStep = match ? parseInt(match[1], 10) : 1;

  const getCurrentPhase = (stepNum: number) =>
    PHASES.findIndex((p) => p.steps.includes(stepNum));

  const currentPhaseIndex = getCurrentPhase(currentStep);

  // ── Render helpers ───────────────────────────────────────
  const renderPhase = (phase: (typeof PHASES)[0], index: number) => {
    const isDone = index < currentPhaseIndex;
    const isCurrent = index === currentPhaseIndex;
    const isLast = index === PHASES.length - 1;

    return (
      <div key={phase.label} className={`${styles.phaseWrapper} ${!isLast ? "flex-1" : ""}`}>
        <div className={styles.phaseContent}>
          <div
            className={`${styles.circleBase} ${
              isDone ? styles.circleDone : isCurrent ? styles.circleCurrent : styles.circlePending
            }`}
          >
            {isDone ? <CheckIcon /> : index + 1}
          </div>
          <span
            className={`${styles.phaseLabel} ${
              isDone ? styles.labelDone : isCurrent ? styles.labelCurrent : styles.labelPending
            }`}
          >
            {phase.label}
          </span>
        </div>
        {!isLast && (
          <div className={`${styles.connector} ${isDone ? styles.connectorDone : styles.connectorPending}`} />
        )}
      </div>
    );
  };

  // ── Render ───────────────────────────────────────────────
  return (
    <>
      <div className={styles.topBar}>
        <div className={styles.topBarInner}>
          <div className={styles.logo}>
            <div className={styles.logoIcon}>
              <span className={styles.logoIconText}>C</span>
            </div>
            <span className={styles.logoName}>ComplianceKit</span>
          </div>
          <span className={styles.stepIndicator}>
            Step {currentStep} of {TOTAL_STEPS}
          </span>
        </div>
      </div>
      <div className={styles.stepperWrapper}>
        <div className={styles.stepperInner}>{PHASES.map(renderPhase)}</div>
      </div>
    </>
  );
};
