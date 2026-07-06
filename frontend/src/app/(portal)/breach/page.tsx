"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useBreachList, useCreateBreach, useUpdateBreach, useDeleteBreach, useDraftNotification } from "@/lib/hooks/useBreaches";
import type { BreachCreateRequest, BreachUpdateRequest } from "@/lib/breachApi";
import { BreachTable } from "./_components/BreachTable";
import { BreachFormModal } from "./_components/BreachFormModal";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  page: "p-6 lg:p-8 max-w-7xl mx-auto",
  header: "flex items-start justify-between mb-6",
  heading: "text-2xl font-bold text-gray-900",
  subheading: "text-sm text-gray-500 mt-0.5",
  reportBtn: "flex items-center gap-2 px-4 py-2 bg-[#D97706] hover:bg-[#B45309] text-white text-sm font-medium rounded-lg transition-colors",
  statsRow: "grid grid-cols-4 gap-4 mb-6",
  statCard: "bg-white rounded-xl border border-gray-100 shadow-sm p-4",
  statValue: "text-2xl font-bold text-gray-900",
  statLabel: "text-xs text-gray-500 mt-0.5",
  loading: "flex items-center justify-center py-24 text-gray-400 text-sm",
  error: "p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 mb-4",
  emptyState: "flex flex-col items-center justify-center py-24 text-center",
  emptyTitle: "text-lg font-semibold text-gray-800 mb-2",
  emptyText: "text-sm text-gray-500 max-w-sm mb-6",
  emptyCta: "flex items-center gap-2 px-5 py-2.5 bg-[#D97706] hover:bg-[#B45309] text-white text-sm font-medium rounded-lg transition-colors",
};

// ── Sub-components ────────────────────────────────────────────────────────────

const AlertIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
  </svg>
);

// ── Component ─────────────────────────────────────────────────────────────────

export default function BreachPage() {
  // ── State ─────────────────────────────────────────────────────────────────
  const [showForm, setShowForm] = useState(false);

  // ── Hooks ─────────────────────────────────────────────────────────────────
  const { data, isLoading, error } = useBreachList();
  const create = useCreateBreach();
  const update = useUpdateBreach();
  const remove = useDeleteBreach();
  const draft = useDraftNotification();

  const breaches = data?.breaches ?? [];

  // ── Stats ─────────────────────────────────────────────────────────────────
  const openCount = breaches.filter((b) => b.status !== "closed").length;
  const overdueCount = breaches.filter((b) => b.deadline_passed).length;
  const criticalCount = breaches.filter((b) => b.severity === "critical" || b.severity === "high").length;
  const closedCount = breaches.filter((b) => b.status === "closed").length;

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleCreate = async (body: BreachCreateRequest) => {
    await create.mutateAsync(body);
    toast.success("Breach incident reported");
  };

  const handleUpdate = async (breachId: string, body: BreachUpdateRequest) => {
    await update.mutateAsync({ breachId, body });
  };

  const handleDelete = async (breachId: string) => {
    try {
      await remove.mutateAsync(breachId);
      toast.success("Incident deleted");
    } catch {
      toast.error("Failed to delete incident");
    }
  };

  const handleDraft = async (breachId: string) => {
    return draft.mutateAsync(breachId);
  };

  // ── Render helpers ────────────────────────────────────────────────────────

  const renderStats = () => (
    <div className={styles.statsRow}>
      <div className={styles.statCard}>
        <div className={styles.statValue}>{openCount}</div>
        <div className={styles.statLabel}>Total Incidents</div>
      </div>
      <div className={styles.statCard}>
        <div className={`${styles.statValue} ${overdueCount > 0 ? "text-red-600" : ""}`}>{overdueCount}</div>
        <div className={styles.statLabel}>Open</div>
      </div>
      <div className={styles.statCard}>
        <div className={`${styles.statValue} ${criticalCount > 0 ? "text-orange-600" : ""}`}>{criticalCount}</div>
        <div className={styles.statLabel}>Under Investigation</div>
      </div>
      <div className={styles.statCard}>
        <div className={styles.statValue}>{closedCount}</div>
        <div className={styles.statLabel}>Resolved</div>
      </div>
    </div>
  );

  const renderEmpty = () => (
    <div className={styles.emptyState}>
      <svg className="w-12 h-12 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
      <div className={styles.emptyTitle}>No breach incidents</div>
      <div className={styles.emptyText}>
        When a data breach occurs, report it here immediately. GDPR requires notification within 72 hours.
      </div>
      <button className={styles.emptyCta} onClick={() => setShowForm(true)}>
        <AlertIcon />
        Report breach incident
      </button>
    </div>
  );

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.heading}>Breach Tracker</h1>
          <p className={styles.subheading}>GDPR Art. 33 (72h) · NIS2 Art. 23 (24h) notification deadlines</p>
        </div>
        <button className={styles.reportBtn} onClick={() => setShowForm(true)}>
          <AlertIcon />
          Report incident
        </button>
      </div>

      {isLoading && <div className={styles.loading}>Loading incidents...</div>}
      {error && <div className={styles.error}>{error instanceof Error ? error.message : "Failed to load incidents"}</div>}

      {!isLoading && !error && (
        <>
          {breaches.length > 0 && renderStats()}
          {breaches.length === 0 ? renderEmpty() : (
            <BreachTable
              breaches={breaches}
              onUpdate={handleUpdate}
              onDelete={handleDelete}
              onDraft={handleDraft}
            />
          )}
        </>
      )}

      {showForm && (
        <BreachFormModal onClose={() => setShowForm(false)} onSubmit={handleCreate} />
      )}
    </div>
  );
}
