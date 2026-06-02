"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";

// ── Constants ─────────────────────────────────────────────

const STEPS = [
  { number: 1, label: "Company Basics" },
  { number: 2, label: "Jurisdiction & Data" },
  { number: 3, label: "Tech Stack" },
  { number: 4, label: "Infrastructure" },
  { number: 5, label: "Regulations & Contacts" },
  { number: 6, label: "Regulatory Details" },
];

// ── Styles ────────────────────────────────────────────────

const styles = {
  aside: "hidden md:flex md:w-64 lg:w-72 bg-navy flex-col h-screen flex-shrink-0 overflow-y-auto",
  logo: {
    wrapper: "px-6 py-8 border-b border-white/10",
    inner: "flex items-center gap-2.5",
    icon: "w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center flex-shrink-0",
    iconText: "text-white font-bold text-sm",
    name: "text-white font-bold text-lg tracking-tight",
    sub: "text-blue-200 text-xs mt-2 leading-relaxed",
  },
  nav: "flex-1 px-4 py-6 space-y-1",
  step: {
    row: "flex items-center gap-3 px-3 py-3 rounded-lg transition-colors",
    active: "bg-white/10",
    future: "opacity-40",
    dot: {
      base: "w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold transition-colors",
      complete: "bg-amber-500 text-white",
      current: "bg-white text-navy",
      future: "bg-white/20 text-white",
    },
    label: {
      active: "text-sm font-medium text-white",
      inactive: "text-sm font-medium text-blue-100",
    },
  },
  footer: "px-6 py-6 border-t border-white/10",
  footerText: "text-blue-300 text-xs leading-relaxed",
  backLink: "mt-3 block text-xs text-blue-300 hover:text-white transition-colors",
};

// ── Component ─────────────────────────────────────────────

export const StepSidebar = () => {
  const pathname = usePathname();
  const match = pathname.match(/\/step\/(\d+)/);
  const current = match ? Number(match[1]) : 1;

  // ── Helpers ──────────────────────────────────────────

  const getRowClass = (isActive: boolean, isComplete: boolean) =>
    `${styles.step.row} ${isActive ? styles.step.active : ""} ${
      !isActive && !isComplete ? styles.step.future : ""
    }`;

  const getDotClass = (isActive: boolean, isComplete: boolean) =>
    `${styles.step.dot.base} ${
      isComplete
        ? styles.step.dot.complete
        : isActive
          ? styles.step.dot.current
          : styles.step.dot.future
    }`;

  // ── Render helpers ────────────────────────────────────

  const renderLogo = () => (
    <div className={styles.logo.wrapper}>
      <div className={styles.logo.inner}>
        <div className={styles.logo.icon}>
          <span className={styles.logo.iconText}>C</span>
        </div>
        <span className={styles.logo.name}>ComplianceKit</span>
      </div>
      <p className={styles.logo.sub}>Complete your compliance profile</p>
    </div>
  );

  const renderStepDot = (step: (typeof STEPS)[0], isActive: boolean, isComplete: boolean) => (
    <div className={getDotClass(isActive, isComplete)}>{isComplete ? "✓" : step.number}</div>
  );

  const renderStepLabel = (step: (typeof STEPS)[0], isActive: boolean) => (
    <p className={isActive ? styles.step.label.active : styles.step.label.inactive}>{step.label}</p>
  );

  const renderStep = (step: (typeof STEPS)[0]) => {
    const isComplete = step.number < current;
    const isActive = step.number === current;
    const rowClass = getRowClass(isActive, isComplete);

    const inner = (
      <>
        {renderStepDot(step, isActive, isComplete)}
        {renderStepLabel(step, isActive)}
      </>
    );

    if (isComplete) {
      return (
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        <Link
          key={step.number}
          href={`/onboarding/step/${step.number}` as any}
          className={rowClass}
        >
          {inner}
        </Link>
      );
    }

    return (
      <div key={step.number} className={rowClass}>
        {inner}
      </div>
    );
  };

  const renderNav = () => <nav className={styles.nav}>{STEPS.map(renderStep)}</nav>;

  const renderFooter = () => (
    <div className={styles.footer}>
      <p className={styles.footerText}>Progress is saved automatically at each step.</p>
    </div>
  );

  // ── Render ────────────────────────────────────────────

  return (
    <aside className={styles.aside}>
      {renderLogo()}
      {renderNav()}
      {renderFooter()}
    </aside>
  );
};
