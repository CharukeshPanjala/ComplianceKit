"use client";

import type { Profile } from "@/types/profile";

// ── Constants ─────────────────────────────────────────────

const PROFILE_SECTIONS = [
  {
    label: "Company basics",
    step: 1,
    isComplete: (p: Profile) => !!(p.tenant_name && p.industry && p.company_size && p.b2b_or_b2c),
  },
  {
    label: "Jurisdiction & data",
    step: 2,
    isComplete: (p: Profile) =>
      !!(p.primary_jurisdiction && p.data_role && p.data_categories_processed?.length),
  },
  {
    label: "Tech stack",
    step: 3,
    isComplete: (p: Profile) => !!p.tech_stack?.length,
  },
  {
    label: "Infrastructure",
    step: 4,
    isComplete: (p: Profile) => p.uses_cloud_services !== null && p.has_on_premise_servers !== null,
  },
  {
    label: "Compliance contacts",
    step: 5,
    isComplete: (p: Profile) =>
      p.has_compliance_officer !== null && p.previous_regulatory_action !== null,
  },
  {
    label: "Regulatory details",
    step: 6,
    isComplete: (p: Profile) => {
      const gdpr = (p.gdpr_data as { lawful_bases?: string[] } | null) ?? {};
      if (!Array.isArray(gdpr.lawful_bases) || gdpr.lawful_bases.length === 0) return false;
      return true;
    },
  },
];

// ── Types ─────────────────────────────────────────────────

interface ProfileCompletenessWidgetProps {
  profile: Profile;
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "bg-white rounded-2xl border border-gray-100 shadow-sm p-6",
  header: "flex items-center justify-between mb-4",
  title: "text-sm font-semibold text-gray-900",
  percent: "text-sm font-bold text-navy",
  barWrapper: "w-full bg-gray-100 rounded-full h-2 mb-4",
  bar: "h-2 rounded-full bg-amber-500 transition-all duration-500",
  sections: "space-y-2",
  row: "flex items-center gap-2.5 text-sm",
  checkDone: "w-4 h-4 text-green-500 flex-shrink-0",
  checkPending: "w-4 h-4 text-gray-300 flex-shrink-0",
  labelDone: "text-gray-600",
  labelPending: "text-gray-400",
  link: "ml-auto text-xs text-navy hover:underline",
  allDone: "text-xs text-green-600 font-medium mt-3 text-center",
};

// ── Sub-components ────────────────────────────────────────

const CheckIcon = ({ done }: { done: boolean }) => (
  <svg
    className={done ? styles.checkDone : styles.checkPending}
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
  >
    {done ? (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    ) : (
      <circle cx="12" cy="12" r="9" strokeWidth={1.5} />
    )}
  </svg>
);

// ── Component ─────────────────────────────────────────────

export const ProfileCompletenessWidget = ({ profile }: ProfileCompletenessWidgetProps) => {
  const results = PROFILE_SECTIONS.map((s) => ({
    ...s,
    done: s.isComplete(profile),
  }));

  const completedCount = results.filter((r) => r.done).length;
  const percent = Math.round((completedCount / results.length) * 100);
  const allDone = completedCount === results.length;

  // ── Render helpers ────────────────────────────────────

  const renderHeader = () => (
    <div className={styles.header}>
      <h3 className={styles.title}>Profile Completeness</h3>
      <span className={styles.percent}>{percent}%</span>
    </div>
  );

  const renderBar = () => (
    <div className={styles.barWrapper}>
      <div className={styles.bar} style={{ width: `${percent}%` }} />
    </div>
  );

  const renderSections = () => (
    <div className={styles.sections}>
      {results.map((section) => (
        <div key={section.step} className={styles.row}>
          <CheckIcon done={section.done} />
          <span className={section.done ? styles.labelDone : styles.labelPending}>
            {section.label}
          </span>
          {!section.done && (
            /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
            <a href={`/onboarding/step/${section.step}` as any} className={styles.link}>
              Complete →
            </a>
          )}
        </div>
      ))}
      {allDone && (
        <p className={styles.allDone}>✓ Profile complete — assessments are fully optimised</p>
      )}
    </div>
  );

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.wrapper}>
      {renderHeader()}
      {renderBar()}
      {renderSections()}
    </div>
  );
};
