"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useProcessorList, useGenerateProcessors, useUpdateProcessor, useDeleteProcessor } from "@/lib/hooks/useProcessors";
import type { ProcessorUpdateRequest } from "@/lib/processorsApi";
import { VendorTable } from "./_components/VendorTable";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  page: "p-6 lg:p-8 max-w-7xl mx-auto",
  header: "flex items-start justify-between mb-6",
  heading: "text-2xl font-bold text-gray-900",
  subheading: "text-sm text-gray-500 mt-0.5",
  actions: "flex items-center gap-3",
  generateBtn:
    "flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50",
  statsRow: "grid grid-cols-4 gap-4 mb-6",
  statCard: "bg-white rounded-xl border border-gray-100 shadow-sm p-4",
  statValue: "text-2xl font-bold text-gray-900",
  statLabel: "text-xs text-gray-500 mt-0.5",
  filterRow: "flex items-center gap-3 mb-4",
  filterSelect: "px-3 py-1.5 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500",
  clearFilter: "text-xs text-gray-500 hover:text-gray-700 underline cursor-pointer",
  error: "p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 mb-4",
  loading: "flex items-center justify-center py-24 text-gray-400 text-sm",
  emptyState: "flex flex-col items-center justify-center py-24 text-center",
  emptyTitle: "text-lg font-semibold text-gray-800 mb-2",
  emptyText: "text-sm text-gray-500 max-w-sm mb-6",
  emptyCta:
    "flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50",
};

// ── Sub-components ────────────────────────────────────────────────────────────

const GenerateIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
  </svg>
);

// ── Component ─────────────────────────────────────────────────────────────────

export default function VendorsPage() {
  // ── State ─────────────────────────────────────────────────────────────────
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [riskFilter, setRiskFilter] = useState<string>("");

  // ── Hooks ─────────────────────────────────────────────────────────────────
  const { data, isLoading, error } = useProcessorList(
    statusFilter || riskFilter
      ? {
          status: (statusFilter as "active" | "inactive" | "under_review") || undefined,
          risk_level: (riskFilter as "low" | "medium" | "high") || undefined,
        }
      : undefined
  );
  const generate = useGenerateProcessors();
  const update = useUpdateProcessor();
  const remove = useDeleteProcessor();

  const processors = data?.processors ?? [];

  // ── Stats ─────────────────────────────────────────────────────────────────
  const allProcessors = data?.processors ?? [];
  const totalCount = allProcessors.length;
  const highRiskCount = allProcessors.filter((p) => p.risk_level === "high").length;
  const dpaMissingCount = allProcessors.filter((p) => !p.dpa_signed).length;
  const reviewDueCount = allProcessors.filter((p) => {
    if (!p.contract_review_date) return false;
    return new Date(p.contract_review_date) <= new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
  }).length;

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleGenerate = async () => {
    try {
      const res = await generate.mutateAsync();
      toast.success(`Generated ${res.generated} vendors from your tech stack`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to generate vendors");
    }
  };

  const handleUpdate = async (processorId: string, body: ProcessorUpdateRequest) => {
    await update.mutateAsync({ processorId, body });
    toast.success("Vendor updated");
  };

  const handleDelete = async (processorId: string) => {
    try {
      await remove.mutateAsync(processorId);
      toast.success("Vendor removed");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to remove vendor");
    }
  };

  const handleClearFilters = () => {
    setStatusFilter("");
    setRiskFilter("");
  };

  // ── Render helpers ────────────────────────────────────────────────────────

  const renderStats = () => (
    <div className={styles.statsRow}>
      <div className={styles.statCard}>
        <div className={styles.statValue}>{totalCount}</div>
        <div className={styles.statLabel}>Total vendors</div>
      </div>
      <div className={styles.statCard}>
        <div className={`${styles.statValue} ${highRiskCount > 0 ? "text-red-600" : ""}`}>{highRiskCount}</div>
        <div className={styles.statLabel}>High risk</div>
      </div>
      <div className={styles.statCard}>
        <div className={`${styles.statValue} ${dpaMissingCount > 0 ? "text-amber-600" : ""}`}>{dpaMissingCount}</div>
        <div className={styles.statLabel}>DPA missing</div>
      </div>
      <div className={styles.statCard}>
        <div className={`${styles.statValue} ${reviewDueCount > 0 ? "text-amber-600" : ""}`}>{reviewDueCount}</div>
        <div className={styles.statLabel}>Review due (30d)</div>
      </div>
    </div>
  );

  const renderFilters = () => (
    <div className={styles.filterRow}>
      <select
        className={styles.filterSelect}
        value={statusFilter}
        onChange={(e) => setStatusFilter(e.target.value)}
      >
        <option value="">All statuses</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
        <option value="under_review">Under review</option>
      </select>
      <select
        className={styles.filterSelect}
        value={riskFilter}
        onChange={(e) => setRiskFilter(e.target.value)}
      >
        <option value="">All risk levels</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
        <option value="low">Low</option>
      </select>
      {(statusFilter || riskFilter) && (
        <span className={styles.clearFilter} onClick={handleClearFilters}>
          Clear filters
        </span>
      )}
    </div>
  );

  const renderEmpty = () => (
    <div className={styles.emptyState}>
      <svg className="w-12 h-12 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
      </svg>
      <div className={styles.emptyTitle}>No vendors yet</div>
      <div className={styles.emptyText}>
        Auto-populate your vendor register from your tech stack, or add vendors manually.
      </div>
      <button
        className={styles.emptyCta}
        onClick={handleGenerate}
        disabled={generate.isPending}
      >
        <GenerateIcon />
        {generate.isPending ? "Generating..." : "Generate from tech stack"}
      </button>
    </div>
  );

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.heading}>Vendor Register</h1>
          <p className={styles.subheading}>Track data processors and GDPR Article 28 compliance</p>
        </div>
        <div className={styles.actions}>
          <button
            className={styles.generateBtn}
            onClick={handleGenerate}
            disabled={generate.isPending}
          >
            <GenerateIcon />
            {generate.isPending ? "Generating..." : "Regenerate from tech stack"}
          </button>
        </div>
      </div>

      {isLoading && <div className={styles.loading}>Loading vendors...</div>}

      {error && (
        <div className={styles.error}>
          {error instanceof Error ? error.message : "Failed to load vendors"}
        </div>
      )}

      {!isLoading && !error && (
        <>
          {renderStats()}
          {processors.length > 0 && renderFilters()}
          {processors.length === 0 && !statusFilter && !riskFilter ? (
            renderEmpty()
          ) : (
            <VendorTable processors={processors} onUpdate={handleUpdate} onDelete={handleDelete} />
          )}
        </>
      )}
    </div>
  );
}
