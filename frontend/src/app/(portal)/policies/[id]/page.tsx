// WHAT: /policies/[id] portal page | CHANGE: new file | WHY: COM-176 — policy viewer with status workflow, version history, PDF/DOCX downloads
"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { usePolicy, useUpdatePolicyStatus, useExportPolicyPdf, useExportPolicyDocx } from "@/lib/hooks/usePolicies";
import { POLICY_TYPE_LABELS, type PolicyStatus } from "@/lib/policiesApi";
import { PolicyMarkdown } from "./_components/PolicyMarkdown";

// ── Constants ─────────────────────────────────────────────────────────────────

const STATUS_OPTIONS: { value: PolicyStatus; label: string; activeClass: string }[] = [
  { value: "draft", label: "Draft", activeClass: "bg-amber-50 border-amber-200 text-amber-700" },
  { value: "under_review", label: "Under Review", activeClass: "bg-blue-50 border-blue-200 text-blue-700" },
  { value: "active", label: "Active", activeClass: "bg-green-50 border-green-200 text-green-700" },
  { value: "archived", label: "Archived", activeClass: "bg-gray-100 border-gray-300 text-gray-600" },
];

const CHANGE_TYPE_LABEL: Record<string, string> = {
  created: "Created",
  edited: "Edited",
  ai_enhanced: "AI Enhanced",
  approved: "Approved",
  archived: "Archived",
};

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  page: "p-6 max-w-5xl mx-auto space-y-5",
  back: "text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1.5 transition-colors",
  header: "flex items-start justify-between gap-4",
  title: "text-xl font-bold text-gray-900",
  subtitle: "text-sm text-gray-400 mt-0.5 flex items-center gap-2",
  aiTag: "text-xs text-blue-500 bg-blue-50 border border-blue-100 px-2 py-0.5 rounded-full",
  actions: "flex items-center gap-2 flex-shrink-0",
  exportBtn:
    "px-3 py-2 text-sm font-medium border border-gray-200 rounded-xl text-gray-700 hover:border-[#0F2044] transition-colors disabled:opacity-50",
  statusRow: "flex items-center gap-2",
  statusBtn: (active: boolean, activeClass: string) =>
    `px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors disabled:opacity-50 ${
      active ? activeClass : "border-gray-200 text-gray-400 hover:border-gray-300"
    }`,
  layout: "grid grid-cols-1 lg:grid-cols-[1fr_240px] gap-6",
  content: "bg-white border border-gray-100 rounded-2xl p-8",
  sidebar: "space-y-4",
  sectionTitle: "text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2",
  versionList: "space-y-2",
  versionRow: "flex items-center justify-between text-xs text-gray-500 py-1.5 border-b border-gray-50 last:border-0",
  versionNum: "font-medium text-gray-700",
  loading: "text-sm text-gray-400 text-center py-16",
  error: "text-sm text-red-500 text-center py-16",
};

// ── Sub-components ────────────────────────────────────────────────────────────

const BackIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
  </svg>
);

// ── Component ─────────────────────────────────────────────────────────────────

export default function PolicyDetailPage() {
  const params = useParams<{ id: string }>();
  const policyId = params.id;

  const { data: policy, isLoading, isError } = usePolicy(policyId);
  const updateStatus = useUpdatePolicyStatus();
  const exportPdf = useExportPolicyPdf();
  const exportDocx = useExportPolicyDocx();

  // ── Handlers ──────────────────────────────────────────

  const handleStatusChange = (status: PolicyStatus) => {
    if (!policy || policy.status === status) return;
    updateStatus.mutate({ policyId: policy.policy_id, status });
  };

  const handleExportPdf = () => {
    if (!policy?.type) return;
    exportPdf.mutate({ policyId: policy.policy_id, policyType: policy.type });
  };

  const handleExportDocx = () => {
    if (!policy?.type) return;
    exportDocx.mutate({ policyId: policy.policy_id, policyType: policy.type });
  };

  // ── Render helpers ────────────────────────────────────

  const renderBack = () => (
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    <Link href={"/policies" as any} className={styles.back}>
      <BackIcon />
      Back to library
    </Link>
  );

  const renderHeader = () => {
    if (!policy) return null;
    return (
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>{policy.title}</h1>
          <p className={styles.subtitle}>
            <span>
              {policy.type ? POLICY_TYPE_LABELS[policy.type] : "Policy"} · Version {policy.current_version}
            </span>
            {policy.is_ai_enhanced && <span className={styles.aiTag}>✨ AI-enhanced</span>}
          </p>
        </div>
        <div className={styles.actions}>
          <button className={styles.exportBtn} onClick={handleExportPdf} disabled={exportPdf.isPending}>
            {exportPdf.isPending ? "Exporting…" : "Export PDF"}
          </button>
          <button className={styles.exportBtn} onClick={handleExportDocx} disabled={exportDocx.isPending}>
            {exportDocx.isPending ? "Exporting…" : "Export DOCX"}
          </button>
        </div>
      </div>
    );
  };

  const renderStatus = () => {
    if (!policy) return null;
    return (
      <div className={styles.statusRow}>
        {STATUS_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            className={styles.statusBtn(policy.status === opt.value, opt.activeClass)}
            onClick={() => handleStatusChange(opt.value)}
            disabled={updateStatus.isPending}
          >
            {opt.label}
          </button>
        ))}
      </div>
    );
  };

  const renderVersions = () => {
    if (!policy?.versions?.length) return null;
    return (
      <div>
        <p className={styles.sectionTitle}>Version History</p>
        <div className={styles.versionList}>
          {policy.versions.map((v) => (
            <div key={v.version_id} className={styles.versionRow}>
              <span className={styles.versionNum}>v{v.version_number}</span>
              <span>{v.change_type ? CHANGE_TYPE_LABEL[v.change_type] ?? v.change_type : "-"}</span>
              <span>{new Date(v.created_at).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderBody = () => {
    if (isLoading) return <p className={styles.loading}>Loading policy…</p>;
    if (isError || !policy) return <p className={styles.error}>Failed to load policy.</p>;
    return (
      <>
        {renderHeader()}
        {renderStatus()}
        <div className={styles.layout}>
          <div className={styles.content}>
            <PolicyMarkdown content={policy.content ?? ""} />
          </div>
          <div className={styles.sidebar}>{renderVersions()}</div>
        </div>
      </>
    );
  };

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.page}>
      {renderBack()}
      {renderBody()}
    </div>
  );
}
