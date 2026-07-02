"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useDsarList, useCreateDsar, useUpdateDsar, useDeleteDsar } from "@/lib/hooks/useDsar";
import type { DsarCreateRequest, DsarUpdateRequest } from "@/lib/dsarApi";
import { DsarTable } from "./_components/DsarTable";
import { DsarFormModal } from "./_components/DsarFormModal";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  page: "p-6 lg:p-8 max-w-7xl mx-auto",
  header: "flex items-start justify-between mb-6",
  heading: "text-2xl font-bold text-gray-900",
  subheading: "text-sm text-gray-500 mt-0.5",
  logBtn: "flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors",
  statsRow: "grid grid-cols-4 gap-4 mb-6",
  statCard: "bg-white rounded-xl border border-gray-100 shadow-sm p-4",
  statValue: "text-2xl font-bold text-gray-900",
  statLabel: "text-xs text-gray-500 mt-0.5",
  loading: "flex items-center justify-center py-24 text-gray-400 text-sm",
  error: "p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 mb-4",
  emptyState: "flex flex-col items-center justify-center py-24 text-center",
  emptyTitle: "text-lg font-semibold text-gray-800 mb-2",
  emptyText: "text-sm text-gray-500 max-w-sm mb-6",
  emptyCta: "flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors",
};

// ── Sub-components ────────────────────────────────────────────────────────────

const PlusIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
);

// ── Component ─────────────────────────────────────────────────────────────────

export default function DsarPage() {
  // ── State ─────────────────────────────────────────────────────────────────
  const [showForm, setShowForm] = useState(false);

  // ── Hooks ─────────────────────────────────────────────────────────────────
  const { data, isLoading, error } = useDsarList();
  const create = useCreateDsar();
  const update = useUpdateDsar();
  const remove = useDeleteDsar();

  const dsars = data?.dsars ?? [];

  // ── Stats ─────────────────────────────────────────────────────────────────
  const pendingCount = dsars.filter((d) => d.status === "pending" || d.status === "in_progress").length;
  const overdueCount = dsars.filter((d) => d.is_overdue).length;
  const unverifiedCount = dsars.filter((d) => !d.identity_verified && d.status !== "completed" && d.status !== "rejected" && d.status !== "withdrawn").length;
  const completedCount = dsars.filter((d) => d.status === "completed").length;

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleCreate = async (body: DsarCreateRequest) => {
    await create.mutateAsync(body);
    toast.success("DSAR request logged, 30-day clock started");
  };

  const handleUpdate = async (dsarId: string, body: DsarUpdateRequest) => {
    await update.mutateAsync({ dsarId, body });
    toast.success("Request updated");
  };

  const handleDelete = async (dsarId: string) => {
    try {
      await remove.mutateAsync(dsarId);
      toast.success("Request deleted");
    } catch {
      toast.error("Failed to delete request");
    }
  };

  // ── Render helpers ────────────────────────────────────────────────────────

  const renderStats = () => (
    <div className={styles.statsRow}>
      <div className={styles.statCard}>
        <div className={styles.statValue}>{pendingCount}</div>
        <div className={styles.statLabel}>Open requests</div>
      </div>
      <div className={styles.statCard}>
        <div className={`${styles.statValue} ${overdueCount > 0 ? "text-red-600" : ""}`}>{overdueCount}</div>
        <div className={styles.statLabel}>Overdue (30d)</div>
      </div>
      <div className={styles.statCard}>
        <div className={`${styles.statValue} ${unverifiedCount > 0 ? "text-amber-600" : ""}`}>{unverifiedCount}</div>
        <div className={styles.statLabel}>Identity unverified</div>
      </div>
      <div className={styles.statCard}>
        <div className={styles.statValue}>{completedCount}</div>
        <div className={styles.statLabel}>Completed</div>
      </div>
    </div>
  );

  const renderEmpty = () => (
    <div className={styles.emptyState}>
      <svg className="w-12 h-12 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
      <div className={styles.emptyTitle}>No DSAR requests</div>
      <div className={styles.emptyText}>
        Log data subject access requests here. GDPR Art. 12 requires you to respond within 30 days.
      </div>
      <button className={styles.emptyCta} onClick={() => setShowForm(true)}>
        <PlusIcon />
        Log DSAR request
      </button>
    </div>
  );

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.heading}>DSAR Requests</h1>
          <p className={styles.subheading}>Data Subject Access Requests · 30-day GDPR response deadline</p>
        </div>
        <button className={styles.logBtn} onClick={() => setShowForm(true)}>
          <PlusIcon />
          Log request
        </button>
      </div>

      {isLoading && <div className={styles.loading}>Loading requests...</div>}
      {error && <div className={styles.error}>{error instanceof Error ? error.message : "Failed to load requests"}</div>}

      {!isLoading && !error && (
        <>
          {dsars.length > 0 && renderStats()}
          {dsars.length === 0 ? renderEmpty() : (
            <DsarTable dsars={dsars} onUpdate={handleUpdate} onDelete={handleDelete} />
          )}
        </>
      )}

      {showForm && (
        <DsarFormModal onClose={() => setShowForm(false)} onSubmit={handleCreate} />
      )}
    </div>
  );
}
