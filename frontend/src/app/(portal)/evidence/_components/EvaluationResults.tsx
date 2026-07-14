"use client";

import type { EvaluationResults as EvaluationResultsData, ClauseStatus } from "@/types/evidence";

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "space-y-3",
  summary: "flex items-center justify-between text-sm font-medium text-[#0F172A]",
  summaryCount: "text-xs text-[#64748B]",
  clauseList: "space-y-2",
  clause: "flex items-start gap-2.5 text-sm",
  clauseIcon: "mt-0.5 w-4 h-4 flex-shrink-0",
  clauseLabel: "text-[#334155] leading-snug",
  clauseNote: "text-xs text-[#94A3B8] mt-0.5",
  overallBadge: "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold",
};

// ── Sub-components ────────────────────────────────────────

const MetIcon = () => (
  <svg className={`${styles.clauseIcon} text-green-500`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const PartialIcon = () => (
  <svg className={`${styles.clauseIcon} text-amber-500`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M12 3a9 9 0 100 18A9 9 0 0012 3z" />
  </svg>
);

const NotMetIcon = () => (
  <svg className={`${styles.clauseIcon} text-red-400`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const clauseIcon = (status: ClauseStatus) => {
  if (status === "met") return <MetIcon />;
  if (status === "partial") return <PartialIcon />;
  return <NotMetIcon />;
};

const overallBadgeCls = (status: string) => {
  if (status === "compliant") return "bg-green-50 text-green-700 border border-green-200";
  if (status === "partial") return "bg-amber-50 text-amber-700 border border-amber-200";
  return "bg-red-50 text-red-600 border border-red-200";
};

const overallLabel = (status: string) => {
  if (status === "compliant") return "Compliant";
  if (status === "partial") return "Partially compliant";
  return "Non-compliant";
};

// ── Component ─────────────────────────────────────────────

interface Props {
  results: EvaluationResultsData;
}

export const EvaluationResults = ({ results }: Props) => {
  const metCount = results.clauses.filter((c) => c.status === "met").length;
  const total = results.clauses.length;

  return (
    <div className={styles.wrapper}>
      <div className={styles.summary}>
        <span className={`${styles.overallBadge} ${overallBadgeCls(results.overall_status)}`}>
          {overallLabel(results.overall_status)}
        </span>
        <span className={styles.summaryCount}>{metCount} of {total} clauses met</span>
      </div>

      <ul className={styles.clauseList}>
        {results.clauses.map((clause) => (
          <li key={clause.clause_id} className={styles.clause}>
            {clauseIcon(clause.status)}
            <div>
              <p className={styles.clauseLabel}>Art. {clause.article} — {clause.label}</p>
              {clause.note && <p className={styles.clauseNote}>{clause.note}</p>}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};
