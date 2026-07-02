"use client";

import { useState } from "react";
import type { Processor, ProcessorUpdateRequest } from "@/lib/processorsApi";
import { VendorEditModal } from "./VendorEditModal";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  wrapper: "overflow-x-auto rounded-xl border border-gray-100 shadow-sm",
  table: "w-full text-sm",
  thead: "bg-gray-50 border-b border-gray-100",
  th: "px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap",
  tr: "border-b border-gray-50 hover:bg-gray-50/50 transition-colors",
  td: "px-4 py-3 text-sm text-gray-700",
  name: "font-medium text-gray-900",
  link: "text-blue-600 hover:underline",
  riskBadge: {
    base: "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
    high: "bg-red-50 text-red-700",
    medium: "bg-amber-50 text-amber-700",
    low: "bg-green-50 text-green-700",
    unknown: "bg-gray-100 text-gray-500",
  },
  statusBadge: {
    base: "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
    active: "bg-green-50 text-green-700",
    inactive: "bg-gray-100 text-gray-500",
    under_review: "bg-amber-50 text-amber-700",
  },
  dpaYes: "inline-flex items-center gap-1 text-green-700 text-xs font-medium",
  dpaNo: "inline-flex items-center gap-1 text-red-600 text-xs font-medium",
  editBtn: "px-3 py-1.5 text-xs font-medium text-blue-600 hover:bg-blue-50 rounded-lg border border-blue-200 transition-colors",
  emptyRow: "py-16 text-center text-gray-400 text-sm",
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface Props {
  processors: Processor[];
  onUpdate: (processorId: string, body: ProcessorUpdateRequest) => Promise<void>;
  onDelete: (processorId: string) => void;
}

// ── Sub-components ────────────────────────────────────────────────────────────

const CheckIcon = () => (
  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
  </svg>
);

const XIcon = () => (
  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

// ── Component ─────────────────────────────────────────────────────────────────

export const VendorTable = ({ processors, onUpdate, onDelete }: Props) => {
  // ── State ─────────────────────────────────────────────────────────────────
  const [editing, setEditing] = useState<Processor | null>(null);

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleEdit = (p: Processor) => setEditing(p);
  const handleClose = () => setEditing(null);

  // ── Render helpers ────────────────────────────────────────────────────────

  const renderRiskBadge = (risk: string | null) => {
    if (!risk) return <span className={`${styles.riskBadge.base} ${styles.riskBadge.unknown}`}>-</span>;
    const cls = risk === "high" ? styles.riskBadge.high : risk === "medium" ? styles.riskBadge.medium : styles.riskBadge.low;
    return <span className={`${styles.riskBadge.base} ${cls}`}>{risk.charAt(0).toUpperCase() + risk.slice(1)}</span>;
  };

  const renderStatusBadge = (status: string | null) => {
    if (!status) return null;
    const cls =
      status === "active"
        ? styles.statusBadge.active
        : status === "under_review"
        ? styles.statusBadge.under_review
        : styles.statusBadge.inactive;
    const label = status === "under_review" ? "Under Review" : status.charAt(0).toUpperCase() + status.slice(1);
    return <span className={`${styles.statusBadge.base} ${cls}`}>{label}</span>;
  };

  const renderDpa = (signed: boolean) =>
    signed ? (
      <span className={styles.dpaYes}><CheckIcon />Signed</span>
    ) : (
      <span className={styles.dpaNo}><XIcon />Missing</span>
    );

  const renderTransfer = (mechanism: string | null) => {
    if (!mechanism || mechanism === "none") return <span className="text-gray-400 text-xs">-</span>;
    const labels: Record<string, string> = {
      scc: "SCC",
      bcr: "BCR",
      adequacy_decision: "Adequacy",
      derogation: "Derogation",
    };
    return <span className="text-xs text-gray-600">{labels[mechanism] ?? mechanism}</span>;
  };

  const renderRow = (p: Processor) => (
    <tr key={p.processor_id} className={styles.tr}>
      <td className={styles.td}>
        <div className={styles.name}>{p.name}</div>
        {p.website && (
          <a href={p.website} target="_blank" rel="noopener noreferrer" className={styles.link}>
            {new URL(p.website).hostname}
          </a>
        )}
      </td>
      <td className={styles.td}>{p.category ?? "-"}</td>
      <td className={styles.td}>{renderRiskBadge(p.risk_level)}</td>
      <td className={styles.td}>{renderDpa(p.dpa_signed)}</td>
      <td className={styles.td}>{renderTransfer(p.transfer_mechanism)}</td>
      <td className={styles.td}>{renderStatusBadge(p.status)}</td>
      <td className={styles.td}>
        <div className="flex items-center gap-2">
          <button className={styles.editBtn} onClick={() => handleEdit(p)}>
            Edit
          </button>
          <button
            className="px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 rounded-lg border border-red-200 transition-colors"
            onClick={() => onDelete(p.processor_id)}
          >
            Remove
          </button>
        </div>
      </td>
    </tr>
  );

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <>
      <div className={styles.wrapper}>
        <table className={styles.table}>
          <thead className={styles.thead}>
            <tr>
              <th className={styles.th}>Vendor</th>
              <th className={styles.th}>Category</th>
              <th className={styles.th}>Risk</th>
              <th className={styles.th}>DPA</th>
              <th className={styles.th}>Transfer</th>
              <th className={styles.th}>Status</th>
              <th className={styles.th}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {processors.length === 0 ? (
              <tr>
                <td colSpan={7} className={styles.emptyRow}>
                  No vendors yet. Generate from your tech stack to get started.
                </td>
              </tr>
            ) : (
              processors.map(renderRow)
            )}
          </tbody>
        </table>
      </div>

      {editing && (
        <VendorEditModal processor={editing} onClose={handleClose} onSave={onUpdate} />
      )}
    </>
  );
};
