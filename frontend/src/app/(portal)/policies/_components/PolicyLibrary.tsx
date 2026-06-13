// WHAT: Policy library grid | CHANGE: new file | WHY: COM-176 — list generated policies with status badges + empty state
"use client";

import Link from "next/link";
import { POLICY_TYPE_LABELS, type Policy, type PolicyStatus } from "@/lib/policiesApi";

// ── Constants ─────────────────────────────────────────────────────────────────

const STATUS_BADGE: Record<PolicyStatus, string> = {
  draft: "bg-amber-50 text-amber-700 border border-amber-100",
  under_review: "bg-blue-50 text-blue-700 border border-blue-100",
  active: "bg-green-50 text-green-700 border border-green-100",
  archived: "bg-gray-100 text-gray-500 border border-gray-200",
};

const STATUS_LABEL: Record<PolicyStatus, string> = {
  draft: "Draft",
  under_review: "Under Review",
  active: "Active",
  archived: "Archived",
};

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  grid: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4",
  card: "block bg-white border border-gray-100 rounded-2xl p-5 hover:border-[#0F2044]/30 hover:shadow-sm transition-all",
  cardHeader: "flex items-start justify-between gap-2 mb-2",
  cardTitle: "text-sm font-semibold text-gray-900",
  cardType: "text-xs text-gray-400 mt-0.5",
  badge: "text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0",
  cardFooter: "flex items-center justify-between mt-4 pt-3 border-t border-gray-50",
  version: "text-xs text-gray-400",
  aiTag: "text-xs text-blue-500",
  empty: "text-center py-16",
  emptyTitle: "text-base font-semibold text-gray-700 mb-1",
  emptySubtitle: "text-sm text-gray-400 mb-4",
  emptyBtn: "px-4 py-2 bg-[#0F2044] text-white text-sm font-semibold rounded-xl hover:bg-[#1a3366] transition-colors",
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface PolicyLibraryProps {
  policies: Policy[];
  onGenerateClick: () => void;
}

// ── Component ─────────────────────────────────────────────────────────────────

export const PolicyLibrary = ({ policies, onGenerateClick }: PolicyLibraryProps) => {
  if (policies.length === 0) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyTitle}>No policies yet</p>
        <p className={styles.emptySubtitle}>Generate your first policy from a compliance gap.</p>
        <button className={styles.emptyBtn} onClick={onGenerateClick}>
          Generate Policy
        </button>
      </div>
    );
  }

  return (
    <div className={styles.grid}>
      {policies.map((policy) => (
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        <Link key={policy.policy_id} href={`/policies/${policy.policy_id}` as any} className={styles.card}>
          <div className={styles.cardHeader}>
            <div>
              <p className={styles.cardTitle}>{policy.title}</p>
              <p className={styles.cardType}>{policy.type ? POLICY_TYPE_LABELS[policy.type] : "Policy"}</p>
            </div>
            {policy.status && (
              <span className={`${styles.badge} ${STATUS_BADGE[policy.status]}`}>{STATUS_LABEL[policy.status]}</span>
            )}
          </div>
          <div className={styles.cardFooter}>
            <span className={styles.version}>Version {policy.current_version}</span>
            {policy.is_ai_enhanced && <span className={styles.aiTag}>✨ AI-enhanced</span>}
          </div>
        </Link>
      ))}
    </div>
  );
};
