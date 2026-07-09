"use client";

import { useState, useEffect } from "react";
import { useGaps } from "@/lib/hooks/useGaps";
import { GapItem } from "./GapItem";
import { GapListSkeleton } from "@/components/ui/Skeleton";
import type { RegulationName } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const SEVERITY_OPTIONS = ["all", "critical", "high", "medium", "low"];
const STATUS_OPTIONS = ["all", "not_met", "unknown", "partial", "met"];
const PRIORITY_OPTIONS = ["all", "critical", "high", "medium", "low"];
const PAGE_SIZE = 20;

// ── Types ─────────────────────────────────────────────────

interface GapListProps {
  assessmentId: string;
  regulation: RegulationName;
  onGapClick: (gapId: string) => void;
  externalSearch?: string;
  externalSeverity?: string;
  externalStatus?: string;
  onTotalChange?: (total: number) => void;
  hideInternalFilters?: boolean;
}

interface Filters {
  severity: string;
  status: string;
  priority: string;
  resolved: string;
  search: string;
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "space-y-4",
  header: "flex flex-col sm:flex-row sm:items-center justify-between gap-3",
  title: "text-lg font-bold text-gray-900",
  count: "text-sm text-gray-400 font-normal",
  filters: "flex flex-wrap items-center gap-2",
  searchWrapper: "relative flex-1 min-w-48",
  searchIcon: "absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400",
  searchInput:
    "w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-navy/20 focus:border-navy",
  select:
    "text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-navy/20 focus:border-navy bg-white text-gray-700",
  resolvedBtn: {
    base: "text-sm px-3 py-2 rounded-lg border transition-colors",
    active: "border-navy bg-navy text-white",
    inactive: "border-gray-200 text-gray-600 hover:border-navy",
  },
  list: "space-y-2",
  emptyWrapper: "text-center py-16",
  emptyIcon: "w-12 h-12 text-gray-200 mx-auto mb-3",
  emptyTitle: "text-sm font-medium text-gray-500",
  emptySubtitle: "text-xs text-gray-400 mt-1",
  errorWrapper: "text-center py-8",
  errorText: "text-sm text-red-500",
  retryBtn: "text-sm text-navy underline mt-2",
  pagination: "flex items-center justify-between pt-4 border-t border-gray-100",
  pageInfo: "text-sm text-gray-500",
  pageButtons: "flex gap-2",
  pageBtn: {
    base: "px-3 py-1.5 text-sm rounded-lg border transition-colors",
    active: "border-navy bg-navy text-white",
    inactive:
      "border-gray-200 text-gray-600 hover:border-navy disabled:opacity-40 disabled:cursor-not-allowed",
  },
};

// ── Sub-components ────────────────────────────────────────

const SearchIcon = () => (
  <svg className={styles.searchIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
    />
  </svg>
);

const EmptyState = ({ hasFilters }: { hasFilters: boolean }) => (
  <div className={styles.emptyWrapper}>
    <svg className={styles.emptyIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1}
        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
    <p className={styles.emptyTitle}>
      {hasFilters ? "No gaps match your filters" : "All clear, no gaps found!"}
    </p>
    <p className={styles.emptySubtitle}>
      {hasFilters ? "Try adjusting or clearing your filters" : "Your compliance is looking great"}
    </p>
  </div>
);

// ── Component ─────────────────────────────────────────────

export const GapList = ({
  assessmentId,
  regulation,
  onGapClick,
  externalSearch,
  externalSeverity,
  externalStatus,
  onTotalChange,
  hideInternalFilters = false,
}: GapListProps) => {
  // ── State ────────────────────────────────────────────

  const [page, setPage] = useState(0);
  const [filters, setFilters] = useState<Filters>({
    severity: "all",
    status: "all",
    priority: "all",
    resolved: "false",
    search: "",
  });

  const offset = page * PAGE_SIZE;

  const effectiveSeverity = externalSeverity !== undefined ? externalSeverity : filters.severity;
  const effectiveStatus = externalStatus !== undefined ? externalStatus : filters.status;
  const effectiveSearch = externalSearch !== undefined ? externalSearch : filters.search;

  const { data, isLoading, isError, refetch } = useGaps(assessmentId, {
    severity: effectiveSeverity !== "all" && effectiveSeverity !== "" ? effectiveSeverity : undefined,
    status: effectiveStatus !== "all" && effectiveStatus !== "" ? effectiveStatus : undefined,
    remediation_priority: filters.priority !== "all" ? filters.priority : undefined,
    resolved: filters.resolved === "all" ? undefined : filters.resolved === "true",
    limit: PAGE_SIZE,
    offset,
  });

  const gaps = data?.gaps ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.ceil(total / PAGE_SIZE);

  const hasFilters =
    effectiveSeverity !== "all" && effectiveSeverity !== "" ||
    effectiveStatus !== "all" && effectiveStatus !== "" ||
    filters.priority !== "all" ||
    filters.resolved !== "false" ||
    effectiveSearch !== "";

  // Filter by search client-side (article name/category)
  const visibleGaps = effectiveSearch
    ? gaps.filter(
        (g) =>
          g.article.toLowerCase().includes(effectiveSearch.toLowerCase()) ||
          (g.category ?? "").toLowerCase().includes(effectiveSearch.toLowerCase())
      )
    : gaps;

  // ── Handlers ─────────────────────────────────────────

  const handleFilterChange = (key: keyof Filters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(0);
  };

  const handlePrev = () => setPage((p) => Math.max(0, p - 1));
  const handleNext = () => setPage((p) => Math.min(totalPages - 1, p + 1));
  const handleRetry = () => refetch();

  useEffect(() => {
    onTotalChange?.(total);
  }, [total, onTotalChange]);

  // ── Render helpers ────────────────────────────────────

  const renderHeader = () => (
    <div className={styles.header}>
      <h3 className={styles.title}>
        {regulation} Gaps <span className={styles.count}>({total} total)</span>
      </h3>
    </div>
  );

  const renderFilters = () => (
    <div className={styles.filters}>
      {/* Search */}
      <div className={styles.searchWrapper}>
        <SearchIcon />
        <input
          type="text"
          placeholder="Search by article or category..."
          value={filters.search}
          onChange={(e) => handleFilterChange("search", e.target.value)}
          className={styles.searchInput}
        />
      </div>

      {/* Severity */}
      <select
        value={filters.severity}
        onChange={(e) => handleFilterChange("severity", e.target.value)}
        className={styles.select}
      >
        {SEVERITY_OPTIONS.map((o) => (
          <option key={o} value={o}>
            {o === "all" ? "All severities" : o.charAt(0).toUpperCase() + o.slice(1)}
          </option>
        ))}
      </select>

      {/* Status */}
      <select
        value={filters.status}
        onChange={(e) => handleFilterChange("status", e.target.value)}
        className={styles.select}
      >
        {STATUS_OPTIONS.map((o) => (
          <option key={o} value={o}>
            {o === "all" ? "All statuses" : o.replace("_", " ")}
          </option>
        ))}
      </select>

      {/* Priority */}
      <select
        value={filters.priority}
        onChange={(e) => handleFilterChange("priority", e.target.value)}
        className={styles.select}
      >
        {PRIORITY_OPTIONS.map((o) => (
          <option key={o} value={o}>
            {o === "all" ? "All priorities" : o.charAt(0).toUpperCase() + o.slice(1)}
          </option>
        ))}
      </select>

      {/* Resolved toggle */}
      <button
        onClick={() =>
          handleFilterChange("resolved", filters.resolved === "true" ? "false" : "true")
        }
        className={`${styles.resolvedBtn.base} ${
          filters.resolved === "true" ? styles.resolvedBtn.active : styles.resolvedBtn.inactive
        }`}
      >
        {filters.resolved === "true" ? "✓ Resolved" : "Show resolved"}
      </button>
    </div>
  );

  const renderList = () => {
    if (isLoading) return <GapListSkeleton />;

    if (isError)
      return (
        <div className={styles.errorWrapper}>
          <p className={styles.errorText}>Failed to load gaps</p>
          <button onClick={handleRetry} className={styles.retryBtn}>
            Try again
          </button>
        </div>
      );

    if (visibleGaps.length === 0) return <EmptyState hasFilters={hasFilters} />;

    return (
      <div className={styles.list}>
        {visibleGaps.map((gap) => (
          <GapItem
            key={gap.gap_id}
            gap={gap}
            assessmentId={assessmentId}
            onClick={() => onGapClick(gap.gap_id)}
          />
        ))}
      </div>
    );
  };

  const renderPagination = () => {
    if (totalPages <= 1) return null;
    return (
      <div className={styles.pagination}>
        <p className={styles.pageInfo}>
          Showing {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} of {total}
        </p>
        <div className={styles.pageButtons}>
          <button
            onClick={handlePrev}
            disabled={page === 0}
            className={`${styles.pageBtn.base} ${styles.pageBtn.inactive}`}
          >
            ← Prev
          </button>
          <button
            onClick={handleNext}
            disabled={page >= totalPages - 1}
            className={`${styles.pageBtn.base} ${styles.pageBtn.inactive}`}
          >
            Next →
          </button>
        </div>
      </div>
    );
  };

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.wrapper}>
      {renderHeader()}
      {!hideInternalFilters && renderFilters()}
      {renderList()}
      {renderPagination()}
    </div>
  );
};
