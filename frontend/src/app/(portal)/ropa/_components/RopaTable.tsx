// WHAT: ROPA entries table | CHANGE: new file | WHY: COM-173 — main table UI for /ropa page
"use client";

import { useState } from "react";
import { useGenerateRopa, useUpdateRopa, useUpdateRopaStatus, useDeleteRopa, useExportRopaPdf } from "@/lib/hooks/useRopa";
import { RopaEditModal } from "./RopaEditModal";
import { RopaEmptyState } from "./RopaEmptyState";
import type { RopaEntry, RopaStatus } from "@/lib/ropaApi";

// ── Constants ─────────────────────────────────────────────────────────────────

const LEGAL_BASIS_LABELS: Record<string, string> = {
  consent: "Consent",
  contract: "Contract",
  legal_obligation: "Legal Obligation",
  vital_interests: "Vital Interests",
  public_task: "Public Task",
  legitimate_interests: "Legitimate Interests",
};

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  wrapper: "space-y-4",
  header: "flex items-center justify-between",
  title: "text-2xl font-bold text-[#0F172A]",
  headerRight: "flex items-center gap-2",
  generateBtn: "px-4 py-2 text-sm font-medium border border-[#E2E8F0] bg-white text-[#334155] rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50",
  exportBtn: "px-4 py-2 text-sm font-medium border border-[#E2E8F0] bg-white text-[#334155] rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50",
  addBtn: "px-4 py-2 bg-[#0F2044] text-white text-sm font-semibold rounded-xl hover:bg-[#1a3366] transition-colors",
  table: "w-full border border-[#E2E8F0] rounded-xl overflow-hidden",
  thead: "bg-[#F8FAFC] border-b border-[#E2E8F0]",
  th: "px-4 py-3 text-left text-xs font-semibold text-[#64748B] uppercase tracking-wide",
  tr: "border-b border-[#E2E8F0] even:bg-[#F8FAFC] hover:bg-gray-50/50 transition-colors",
  td: "px-4 py-3 text-sm text-[#334155]",
  activityName: "font-medium text-[#0F172A]",
  badge: (status: RopaStatus) => {
    const map: Record<RopaStatus, string> = {
      active: "bg-green-50 text-green-700 border border-green-100",
      draft: "bg-amber-50 text-amber-700 border border-amber-100",
      archived: "bg-gray-100 text-gray-500 border border-gray-200",
    };
    return `inline-flex px-2 py-0.5 text-xs font-medium rounded-full ${map[status] ?? map.draft}`;
  },
  sourceBadge: "inline-flex px-2 py-0.5 text-xs rounded-full bg-blue-50 text-blue-600 border border-blue-100",
  actions: "flex items-center gap-2",
  editBtn: "text-xs text-[#0F2044] hover:underline font-medium",
  deleteBtn: "text-xs text-red-400 hover:text-red-600 transition-colors",
  dpiaTag: "inline-flex px-1.5 py-0.5 text-xs rounded bg-red-50 text-red-600 border border-red-100",
};

// ── Sub-components ────────────────────────────────────────────────────────────

const EditIcon = () => (
  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
  </svg>
);

// ── Component ─────────────────────────────────────────────────────────────────

interface RopaTableProps {
  entries: RopaEntry[];
}

export const RopaTable = ({ entries }: RopaTableProps) => {
  const [editingEntry, setEditingEntry] = useState<RopaEntry | null>(null);

  const generateRopa = useGenerateRopa();
  const updateRopa = useUpdateRopa();
  const updateStatus = useUpdateRopaStatus();
  const deleteRopa = useDeleteRopa();
  const exportPdf = useExportRopaPdf();

  const handleSave = (updates: Partial<RopaEntry>) => {
    if (!editingEntry) return;
    updateRopa.mutate(
      { ropaId: editingEntry.ropa_id, body: updates },
      { onSuccess: () => setEditingEntry(null) },
    );
  };

  const handleStatusChange = (status: RopaStatus) => {
    if (!editingEntry) return;
    updateStatus.mutate(
      { ropaId: editingEntry.ropa_id, status },
      { onSuccess: () => setEditingEntry(null) },
    );
  };

  const handleDelete = (ropaId: string) => {
    if (!confirm("Delete this processing activity?")) return;
    deleteRopa.mutate(ropaId);
  };

  if (entries.length === 0) {
    return (
      <RopaEmptyState
        onGenerate={() => generateRopa.mutate()}
        isGenerating={generateRopa.isPending}
      />
    );
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <h1 className={styles.title}>
          Processing Activities
          <span className="text-sm font-normal text-gray-400 ml-2">{entries.length} entries</span>
        </h1>
        <div className={styles.headerRight}>
          <button
            className={styles.generateBtn}
            onClick={() => generateRopa.mutate()}
            disabled={generateRopa.isPending}
          >
            {generateRopa.isPending ? "Regenerating…" : "Regenerate"}
          </button>
          <button
            className={styles.exportBtn}
            onClick={() => exportPdf.mutate()}
            disabled={exportPdf.isPending}
          >
            {exportPdf.isPending ? "Exporting…" : "Export PDF"}
          </button>
        </div>
      </div>

      <div className={styles.table}>
        <table className="w-full">
          <thead className={styles.thead}>
            <tr>
              <th className={styles.th}>Activity</th>
              <th className={styles.th}>Legal Basis</th>
              <th className={styles.th}>Data Categories</th>
              <th className={styles.th}>Transfers</th>
              <th className={styles.th}>Status</th>
              <th className={styles.th}>Source</th>
              <th className={styles.th}></th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr key={entry.ropa_id} className={styles.tr}>
                <td className={styles.td}>
                  <div className={styles.activityName}>{entry.activity_name}</div>
                  {entry.requires_dpia && (
                    <span className={styles.dpiaTag}>DPIA required</span>
                  )}
                </td>
                <td className={styles.td}>
                  {LEGAL_BASIS_LABELS[entry.legal_basis ?? ""] ?? entry.legal_basis ?? "-"}
                </td>
                <td className={styles.td}>
                  {entry.data_categories?.slice(0, 3).join(", ") ?? "-"}
                  {(entry.data_categories?.length ?? 0) > 3 && (
                    <span className="text-gray-400"> +{(entry.data_categories?.length ?? 0) - 3}</span>
                  )}
                </td>
                <td className={styles.td}>
                  {entry.transfer_mechanism === "none" || !entry.transfer_mechanism
                    ? "None"
                    : entry.transfer_mechanism.toUpperCase()}
                </td>
                <td className={styles.td}>
                  <span className={styles.badge(entry.status)}>
                    {entry.status.charAt(0).toUpperCase() + entry.status.slice(1)}
                  </span>
                </td>
                <td className={styles.td}>
                  <span className={styles.sourceBadge}>
                    {entry.source === "auto_generated" ? "Auto" : "Manual"}
                  </span>
                </td>
                <td className={styles.td}>
                  <div className={styles.actions}>
                    <button className={styles.editBtn} onClick={() => setEditingEntry(entry)}>
                      <EditIcon />
                    </button>
                    <button className={styles.deleteBtn} onClick={() => handleDelete(entry.ropa_id)}>✕</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editingEntry && (
        <RopaEditModal
          entry={editingEntry}
          onSave={handleSave}
          onStatusChange={handleStatusChange}
          onClose={() => setEditingEntry(null)}
          isSaving={updateRopa.isPending || updateStatus.isPending}
        />
      )}
    </div>
  );
};
