"use client";

import { useState } from "react";
import type { ChangeEvent } from "react";
import { useRouter } from "next/navigation";
import { GapDetailModal } from "../../dashboard/_components/GapDetailModal";
import { useLatestAssessments } from "@/lib/hooks/useLatestAssessments";
import { useGaps } from "@/lib/hooks/useGaps";
import type { Gap, RegulationName } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const REGULATIONS: { value: RegulationName; label: string }[] = [
  { value: "GDPR", label: "GDPR" },
  { value: "NIS2", label: "NIS2" },
  { value: "EU_AI_ACT", label: "EU AI Act" },
];

const REGULATION_LABELS: Record<RegulationName, string> = {
  GDPR: "GDPR",
  NIS2: "NIS2",
  EU_AI_ACT: "AI Act",
};

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "flex-1 overflow-y-auto",
  inner: "max-w-7xl mx-auto px-6 py-8 space-y-4",
  filterBar:
    "bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-4 flex items-center gap-3 flex-wrap",
  filterSearch:
    "flex-1 min-w-[200px] px-3 py-2 text-sm border border-[#E2E8F0] rounded-lg focus:outline-none focus:border-[#D97706]",
  filterSelect:
    "px-3 py-2 text-sm border border-[#E2E8F0] rounded-lg focus:outline-none focus:border-[#D97706] bg-white text-[#334155]",
  filterCount: "text-sm text-[#64748B] ml-auto",
  filterExport:
    "px-3 py-2 text-sm border border-[#E2E8F0] rounded-lg text-[#334155] hover:bg-gray-50",
  tabs: "flex gap-2 border-b border-gray-100",
  tab: {
    base: "px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px",
    active: "border-navy text-navy",
    inactive: "border-transparent text-gray-500 hover:text-gray-700",
  },
  bulkBar: "bg-amber-50 border border-amber-200 rounded-xl p-3 flex items-center gap-3",
  table: "bg-white rounded-xl border border-[#E2E8F0] shadow-sm overflow-hidden",
  tableHeader:
    "grid grid-cols-[40px_1fr_100px_90px_100px_110px_40px] gap-3 px-4 py-3 bg-[#F8FAFC] border-b border-[#E2E8F0] text-xs font-medium text-[#64748B] uppercase tracking-wide",
  tableRow:
    "grid grid-cols-[40px_1fr_100px_90px_100px_110px_40px] gap-3 px-4 py-3 border-b border-[#E2E8F0] items-center hover:bg-[#F8FAFC] cursor-pointer last:border-b-0",
  expandedSection: "px-4 py-4 border-b border-[#E2E8F0] bg-[#FAFBFC] last:border-b-0",
  emptyWrapper: "text-center py-16",
  emptyTitle: "text-sm font-medium text-gray-500",
  emptySubtitle: "text-xs text-gray-400 mt-1",
};

// ── Sub-components ─────────────────────────────────────────

const ChevronDownIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className="h-4 w-4 text-[#64748B]"
    viewBox="0 0 20 20"
    fill="currentColor"
  >
    <path
      fillRule="evenodd"
      d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
      clipRule="evenodd"
    />
  </svg>
);

const ChevronUpIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className="h-4 w-4 text-[#64748B]"
    viewBox="0 0 20 20"
    fill="currentColor"
  >
    <path
      fillRule="evenodd"
      d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z"
      clipRule="evenodd"
    />
  </svg>
);

// ── Helpers ────────────────────────────────────────────────

const getSeverityColor = (severity: string | null) => {
  switch (severity) {
    case "critical":
      return "text-red-600";
    case "high":
      return "text-orange-500";
    case "medium":
      return "text-amber-500";
    case "low":
      return "text-gray-500";
    default:
      return "text-gray-400";
  }
};

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case "met":
      return "bg-green-100 text-green-700";
    case "partial":
      return "bg-amber-100 text-amber-700";
    case "not_met":
      return "bg-red-100 text-red-700";
    default:
      return "bg-gray-100 text-gray-600";
  }
};

const formatDate = (date: string | null) => {
  if (!date) return "N/A";
  return new Date(date).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
};

// ── Component ─────────────────────────────────────────────

export const GapsPageContent = () => {
  // ── State ────────────────────────────────────────────

  const [activeRegulation, setActiveRegulation] = useState<RegulationName>("GDPR");
  const [selectedGapId, setSelectedGapId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [regulationFilter, setRegulationFilter] = useState("");
  const [severityFilter, setSeverityFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [expandedRowId, setExpandedRowId] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(1);

  const router = useRouter();
  const { data: assessments = [], isLoading } = useLatestAssessments();
  const activeAssessment = assessments.find((a) => a.regulation === activeRegulation) ?? null;

  const { data: gapsData, isError: gapsError } = useGaps(activeAssessment?.assessment_id ?? null, {
    severity: severityFilter || undefined,
    status: statusFilter || undefined,
  });

  const allGaps = gapsData?.gaps ?? [];
  const filteredGaps = allGaps.filter((gap) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      gap.article.toLowerCase().includes(q) ||
      (gap.title ?? "").toLowerCase().includes(q) ||
      (gap.plain_english ?? "").toLowerCase().includes(q)
    );
  });

  // ── Handlers ─────────────────────────────────────────

  const handleTabClick = (regulation: RegulationName) => {
    setActiveRegulation(regulation);
    setRegulationFilter(regulation);
    setSelectedGapId(null);
    setExpandedRowId(null);
    setSelectedIds([]);
    setCurrentPage(1);
  };

  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);
  };

  const handleRegulationFilter = (e: ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setRegulationFilter(val);
    if (val) setActiveRegulation(val as RegulationName);
    setCurrentPage(1);
  };

  const handleSeverityFilter = (e: ChangeEvent<HTMLSelectElement>) => {
    setSeverityFilter(e.target.value);
    setCurrentPage(1);
  };

  const handleStatusFilter = (e: ChangeEvent<HTMLSelectElement>) => {
    setStatusFilter(e.target.value);
    setCurrentPage(1);
  };

  const handleModalClose = () => setSelectedGapId(null);

  const handleRowExpand = (id: string) =>
    setExpandedRowId((prev) => (prev === id ? null : id));

  const handleSelectRow = (id: string) =>
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );

  const handleSelectAll = () => {
    const allIds = filteredGaps.map((g) => g.gap_id);
    if (selectedIds.length === allIds.length && allIds.length > 0) {
      setSelectedIds([]);
    } else {
      setSelectedIds(allIds);
    }
  };

  const handleMarkResolved = () => {
    // stub — bulk resolve wired in a future ticket
  };

  const handleArchive = () => {
    // stub — bulk archive wired in a future ticket
  };

  const handlePrevPage = () => setCurrentPage((p) => Math.max(1, p - 1));
  const handleNextPage = () => setCurrentPage((p) => p + 1);
  const handleGoToPage = (page: number) => setCurrentPage(page);

  // ── Render helpers ────────────────────────────────────

  const renderFilterBar = () => (
    <div className={styles.filterBar}>
      <input
        type="text"
        placeholder="Search gaps..."
        className={styles.filterSearch}
        value={searchQuery}
        onChange={handleSearchChange}
      />
      <select className={styles.filterSelect} value={regulationFilter} onChange={handleRegulationFilter}>
        <option value="">All Regulations</option>
        <option value="GDPR">GDPR</option>
        <option value="NIS2">NIS2</option>
        <option value="EU_AI_ACT">AI Act</option>
      </select>
      <select className={styles.filterSelect} value={severityFilter} onChange={handleSeverityFilter}>
        <option value="">All Severities</option>
        <option value="critical">critical</option>
        <option value="high">high</option>
        <option value="medium">medium</option>
        <option value="low">low</option>
      </select>
      <select className={styles.filterSelect} value={statusFilter} onChange={handleStatusFilter}>
        <option value="">All Statuses</option>
        <option value="not_met">Not met</option>
        <option value="partial">Partial</option>
        <option value="met">Met</option>
        <option value="unknown">Unknown</option>
        <option value="not_applicable">Not applicable</option>
      </select>
      <span className={styles.filterCount}>{filteredGaps.length} gaps found</span>
      <button className={styles.filterExport}>Export CSV</button>
    </div>
  );

  const renderTabs = () => (
    <div className={styles.tabs}>
      {REGULATIONS.map((reg) => (
        <button
          key={reg.value}
          onClick={() => handleTabClick(reg.value)}
          className={`${styles.tab.base} ${
            activeRegulation === reg.value ? styles.tab.active : styles.tab.inactive
          }`}
        >
          {reg.label}
        </button>
      ))}
    </div>
  );

  const renderEmptyState = (title: string, subtitle: string) => (
    <div className={styles.emptyWrapper}>
      <p className={styles.emptyTitle}>{title}</p>
      <p className={styles.emptySubtitle}>{subtitle}</p>
    </div>
  );

  const renderBulkBar = () => {
    if (selectedIds.length === 0) return null;
    return (
      <div className={styles.bulkBar}>
        <span className="text-sm font-medium text-amber-800">{selectedIds.length} selected</span>
        <button
          onClick={handleMarkResolved}
          className="px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded-lg hover:bg-green-700"
        >
          Mark Resolved
        </button>
        <button
          onClick={handleArchive}
          className="px-3 py-1.5 border border-[#E2E8F0] bg-white text-xs font-medium rounded-lg text-[#334155] hover:bg-gray-50"
        >
          Archive
        </button>
      </div>
    );
  };

  const renderStatusReason = (gap: Gap) => {
    if (gap.status === "unknown") {
      return "This article cannot be automatically evaluated. It requires you to upload evidence or manually confirm compliance.";
    }
    if (gap.status === "not_met") {
      return gap.remediation_hint ?? "Your current profile indicates this requirement is not yet in place.";
    }
    if (gap.status === "partial") {
      return gap.remediation_hint ?? "You have partially addressed this requirement but further action is needed.";
    }
    return null;
  };

  const renderExpandedRow = (gap: Gap) => (
    <div className={styles.expandedSection}>
      {/* ── Section 1: Why this article applies ── */}
      <div className="mb-5">
        <p className="text-xs font-semibold text-[#64748B] mb-2 uppercase tracking-wide flex items-center gap-1.5">
          <span className="inline-block w-2 h-2 rounded-full bg-blue-400" />
          Why this applies to you
        </p>
        <p className="text-sm text-[#334155] leading-relaxed bg-blue-50 border border-blue-100 rounded-lg px-4 py-3">
          {gap.plain_english ?? gap.remediation_hint ?? "This article is applicable based on your company profile and the regulations you are subject to."}
        </p>
      </div>

      {/* ── Section 2: What's wrong ── */}
      {gap.status !== "met" && (
        <div className="mb-5">
          <p className="text-xs font-semibold text-[#64748B] mb-2 uppercase tracking-wide flex items-center gap-1.5">
            <span className="inline-block w-2 h-2 rounded-full bg-amber-400" />
            What&apos;s missing
          </p>
          <p className="text-sm text-[#334155] leading-relaxed bg-amber-50 border border-amber-100 rounded-lg px-4 py-3">
            {renderStatusReason(gap)}
          </p>
        </div>
      )}

      {/* ── Section 3: How to fix it ── */}
      {gap.remediation_steps?.steps && gap.remediation_steps.steps.length > 0 && (
        <div className="mb-5">
          <p className="text-xs font-semibold text-[#64748B] mb-2 uppercase tracking-wide flex items-center gap-1.5">
            <span className="inline-block w-2 h-2 rounded-full bg-green-400" />
            How to fix it
          </p>
          <ul className="space-y-2">
            {gap.remediation_steps.steps.map((step: string, i: number) => (
              <li key={i} className="flex items-start gap-3 text-sm text-[#334155] bg-green-50 border border-green-100 rounded-lg px-4 py-2.5">
                <span className="mt-0.5 flex-shrink-0 w-5 h-5 rounded-full bg-green-100 text-green-700 text-xs font-bold flex items-center justify-center">
                  {i + 1}
                </span>
                {step}
              </li>
            ))}
          </ul>
        </div>
      )}

      {gap.notes && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-[#64748B] mb-1 uppercase tracking-wide">Notes</p>
          <p className="text-sm text-[#334155] border border-[#E2E8F0] rounded-lg px-3 py-2 bg-white">
            {gap.notes}
          </p>
        </div>
      )}

      {/* ── Generate policy callout ── */}
      {gap.status !== "met" && gap.status !== "not_applicable" && (
        <div className="mb-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl px-4 py-3.5 flex gap-3 items-start">
          <div className="w-8 h-8 rounded-lg bg-[#EFF6FF] flex items-center justify-center flex-shrink-0 mt-0.5">
            <svg className="w-4 h-4 text-[#1D4ED8]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <p className="text-[13px] font-medium text-[#0F172A] mb-0.5">Generate a policy document</p>
            <p className="text-xs text-[#64748B] leading-relaxed mb-2.5">
              ComplianceKit can draft a compliance policy tailored to close this gap. Takes about 30 seconds and you can edit it before publishing.
            </p>
            <button
              onClick={() => router.push(`/policies?gap_id=${gap.gap_id}&regulation=${activeRegulation}` as never)}
              className="text-xs font-medium text-[#1D4ED8] border border-[#BFDBFE] rounded-md px-3 py-1.5 bg-transparent hover:bg-[#EFF6FF] transition-colors"
            >
              Generate policy
            </button>
          </div>
        </div>
      )}

      <div className="mt-1">
        <button
          onClick={() => setSelectedGapId(gap.gap_id)}
          className="w-full py-2.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
        >
          Mark as resolved
        </button>
      </div>
    </div>
  );

  const renderPagination = () => {
    const pageSize = 20;
    const totalItems = filteredGaps.length;
    const totalPages = Math.ceil(totalItems / pageSize);

    if (totalPages <= 1) return null;

    const start = (currentPage - 1) * pageSize + 1;
    const end = Math.min(currentPage * pageSize, totalItems);
    const maxChips = 5;
    const pageChips = Array.from({ length: Math.min(totalPages, maxChips) }, (_, i) => i + 1);

    return (
      <div className="flex items-center justify-between mt-4 px-2">
        <span className="text-sm text-[#64748B]">
          Showing {start}–{end} of {totalItems} gaps
        </span>
        <div className="flex items-center gap-1">
          <button
            onClick={handlePrevPage}
            disabled={currentPage === 1}
            className="px-3 py-1.5 text-sm border border-[#E2E8F0] rounded-lg text-[#334155] hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Prev
          </button>
          {pageChips.map((page) => (
            <button
              key={page}
              onClick={() => handleGoToPage(page)}
              className={`w-8 h-8 text-sm rounded-lg font-medium ${
                page === currentPage
                  ? "bg-[#D97706] text-white"
                  : "border border-[#E2E8F0] text-[#334155] hover:bg-gray-50"
              }`}
            >
              {page}
            </button>
          ))}
          <button
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
            className="px-3 py-1.5 text-sm border border-[#E2E8F0] rounded-lg text-[#334155] hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    );
  };

  const renderTable = () => {
    if (filteredGaps.length === 0) {
      return renderEmptyState("No gaps found", "Try adjusting your filters");
    }

    const pageSize = 20;
    const pagedGaps = filteredGaps.slice((currentPage - 1) * pageSize, currentPage * pageSize);
    const allIds = filteredGaps.map((g) => g.gap_id);
    const allSelected = allIds.length > 0 && selectedIds.length === allIds.length;

    return (
      <div className={styles.table}>
        <div className={styles.tableHeader}>
          <div className="flex items-center justify-center">
            <input
              type="checkbox"
              checked={allSelected}
              onChange={handleSelectAll}
              className="w-4 h-4 rounded border-gray-300 cursor-pointer"
            />
          </div>
          <span>Article</span>
          <span>Regulation</span>
          <span>Severity</span>
          <span>Status</span>
          <span>Due Date</span>
          <span />
        </div>
        {pagedGaps.map((gap) => (
          <div key={gap.gap_id}>
            <div
              className={styles.tableRow}
              onClick={() => handleRowExpand(gap.gap_id)}
            >
              <div
                className="flex items-center justify-center"
                onClick={(e) => e.stopPropagation()}
              >
                <input
                  type="checkbox"
                  checked={selectedIds.includes(gap.gap_id)}
                  onChange={() => handleSelectRow(gap.gap_id)}
                  className="w-4 h-4 rounded border-gray-300 cursor-pointer"
                />
              </div>
              <div className="min-w-0">
                <span className="font-medium text-[#0F172A] text-sm block truncate">
                  {gap.article}
                </span>
                {gap.title && (
                  <span className="text-xs text-[#64748B] block truncate">{gap.title}</span>
                )}
              </div>
              <span className="text-xs font-medium text-[#334155]">
                {REGULATION_LABELS[activeRegulation]}
              </span>
              <span className={`text-xs font-medium capitalize ${getSeverityColor(gap.severity)}`}>
                {gap.severity ?? "N/A"}
              </span>
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium w-fit ${getStatusBadgeClass(gap.status)}`}
              >
                {gap.status.replace("_", " ")}
              </span>
              <span className="text-xs text-[#64748B]">{formatDate(gap.due_date)}</span>
              <button
                className="flex items-center justify-center"
                onClick={(e) => {
                  e.stopPropagation();
                  handleRowExpand(gap.gap_id);
                }}
              >
                {expandedRowId === gap.gap_id ? <ChevronUpIcon /> : <ChevronDownIcon />}
              </button>
            </div>
            {expandedRowId === gap.gap_id && renderExpandedRow(gap)}
          </div>
        ))}
      </div>
    );
  };

  const renderContent = () => {
    if (isLoading)
      return (
        <div className="flex items-center justify-center py-24">
          <div className="w-8 h-8 border-2 border-[#D97706] border-t-transparent rounded-full animate-spin" />
        </div>
      );

    if (!activeAssessment?.assessment_id) {
      return renderEmptyState(
        "No assessment yet for this regulation",
        "Run an assessment from the dashboard first"
      );
    }

    if (activeAssessment.status !== "completed") {
      return renderEmptyState(
        "Assessment is still running",
        "Check back in a moment, or view progress on the dashboard"
      );
    }

    if (gapsError) {
      return renderEmptyState(
        "Could not load gaps",
        "There was a problem fetching your gap data. Try refreshing the page."
      );
    }

    return (
      <>
        {renderBulkBar()}
        {renderTable()}
        {renderPagination()}
      </>
    );
  };

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.wrapper}>
      <div className={styles.inner}>
        {renderFilterBar()}
        {renderTabs()}
        {renderContent()}
      </div>
      {activeAssessment?.assessment_id && (
        <GapDetailModal
          gapId={selectedGapId}
          assessmentId={activeAssessment.assessment_id}
          regulation={activeRegulation}
          isOpen={!!selectedGapId}
          onClose={handleModalClose}
        />
      )}
    </div>
  );
};
