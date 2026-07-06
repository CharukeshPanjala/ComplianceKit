"use client";

import { useState } from "react";
import type { DsarRequest, DsarUpdateRequest } from "@/lib/dsarApi";
import { DaysRemainingBadge } from "./DaysRemainingBadge";
import { DsarDetailModal } from "./DsarDetailModal";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  wrapper: "bg-white overflow-x-auto rounded-xl border border-gray-100 shadow-sm",
  table: "w-full text-sm",
  thead: "bg-gray-50 border-b border-gray-100",
  th: "px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap",
  tr: "border-b border-gray-50 hover:bg-gray-50/50 transition-colors cursor-pointer",
  td: "px-4 py-3 align-middle",
  reqType: "font-medium text-gray-900 text-sm",
  requester: "text-xs text-gray-400 mt-0.5",
  statusBadge: {
    base: "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
    pending: "bg-gray-100 text-gray-600",
    in_progress: "bg-blue-100 text-blue-700",
    awaiting_info: "bg-amber-100 text-amber-700",
    completed: "bg-green-100 text-green-700",
    rejected: "bg-red-100 text-red-700",
    withdrawn: "bg-gray-100 text-gray-500",
  },
  idBadge: "inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-purple-50 text-purple-700",
  editBtn: "px-3 py-1.5 text-xs font-medium text-blue-600 hover:bg-blue-50 rounded-lg border border-blue-200 transition-colors",
  deleteBtn: "px-3 py-1.5 text-xs font-medium text-red-500 hover:bg-red-50 rounded-lg border border-red-200 transition-colors",
  emptyRow: "py-16 text-center text-gray-400 text-sm",
};

const STATUS_LABELS: Record<string, string> = {
  pending: "Pending",
  in_progress: "In progress",
  awaiting_info: "Awaiting info",
  completed: "Completed",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
};

const TERMINAL = new Set(["completed", "rejected", "withdrawn"]);

// ── Sub-components ─────────────────────────────────────────────────────────────

const WorkflowDots = ({ status }: { status: string }) => {
  const stepIndex = status === "pending" ? 0 : status === "in_progress" ? 1 : 2;
  return (
    <div className="flex items-center gap-1">
      {[0, 1, 2].map((i) => (
        <div key={i} className="flex items-center gap-1">
          <div
            className={`w-2.5 h-2.5 rounded-full ${
              i < stepIndex ? "bg-green-500" : i === stepIndex ? "bg-[#D97706]" : "bg-gray-200"
            }`}
          />
          {i < 2 && <div className="w-4 h-px bg-gray-200" />}
        </div>
      ))}
    </div>
  );
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface Props {
  dsars: DsarRequest[];
  onUpdate: (dsarId: string, body: DsarUpdateRequest) => Promise<void>;
  onDelete: (dsarId: string) => void;
}

// ── Component ─────────────────────────────────────────────────────────────────

export const DsarTable = ({ dsars, onUpdate, onDelete }: Props) => {
  // ── State ─────────────────────────────────────────────────────────────────
  const [detail, setDetail] = useState<DsarRequest | null>(null);

  // ── Render helpers ────────────────────────────────────────────────────────

  const renderStatus = (status: string | null) => {
    if (!status) return null;
    const cls = styles.statusBadge[status as keyof typeof styles.statusBadge] ?? styles.statusBadge.pending;
    return <span className={`${styles.statusBadge.base} ${cls}`}>{STATUS_LABELS[status] ?? status}</span>;
  };

  const renderRow = (d: DsarRequest) => {
    const isTerminal = TERMINAL.has(d.status ?? "");
    return (
      <tr key={d.dsar_id} className={styles.tr} onClick={() => setDetail(d)}>
        <td className={styles.td}>
          <div className={styles.reqType}>{d.request_type_label}</div>
          <div className={styles.requester}>{d.requester_name ?? d.requester_email}</div>
        </td>
        <td className={styles.td}>
          <DaysRemainingBadge
            daysRemaining={d.days_remaining}
            isOverdue={d.is_overdue}
            isTerminal={isTerminal}
          />
        </td>
        <td className={styles.td}>
          <div className="flex flex-col gap-1.5">
            {renderStatus(d.status)}
            <WorkflowDots status={d.status ?? "pending"} />
          </div>
        </td>
        <td className={styles.td}>
          {d.identity_verified ? (
            <span className={styles.idBadge}>
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
              </svg>
              Verified
            </span>
          ) : (
            <span className="text-xs text-gray-400">Not verified</span>
          )}
        </td>
        <td className={styles.td}>
          <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
            <button className={styles.editBtn} onClick={() => setDetail(d)}>View / Edit</button>
            <button className={styles.deleteBtn} onClick={() => onDelete(d.dsar_id)}>Delete</button>
          </div>
        </td>
      </tr>
    );
  };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <>
      <div className={styles.wrapper}>
        <table className={styles.table}>
          <thead className={styles.thead}>
            <tr>
              <th className={styles.th}>Request</th>
              <th className={styles.th}>Deadline (30d)</th>
              <th className={styles.th}>Status</th>
              <th className={styles.th}>Identity</th>
              <th className={styles.th}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {dsars.length === 0 ? (
              <tr><td colSpan={5} className={styles.emptyRow}>No DSAR requests yet.</td></tr>
            ) : (
              dsars.map(renderRow)
            )}
          </tbody>
        </table>
      </div>

      {detail && (
        <DsarDetailModal
          dsar={detail}
          onClose={() => setDetail(null)}
          onSave={async (id, body) => { await onUpdate(id, body); setDetail(null); }}
        />
      )}
    </>
  );
};
