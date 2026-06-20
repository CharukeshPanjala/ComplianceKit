"use client";

import { useState } from "react";
import { toast } from "sonner";
import type { BreachIncident, BreachUpdateRequest } from "@/lib/breachApi";
import { CountdownBadge } from "./CountdownBadge";
import { NotificationDraftModal } from "./NotificationDraftModal";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  wrapper: "overflow-x-auto rounded-xl border border-gray-100 shadow-sm",
  table: "w-full text-sm",
  thead: "bg-gray-50 border-b border-gray-100",
  th: "px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap",
  tr: "border-b border-gray-50 hover:bg-gray-50/50 transition-colors",
  td: "px-4 py-3 align-top",
  title: "font-medium text-gray-900 leading-snug",
  meta: "text-xs text-gray-400 mt-0.5",
  severityBadge: {
    base: "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
    critical: "bg-red-100 text-red-700",
    high: "bg-orange-100 text-orange-700",
    medium: "bg-amber-100 text-amber-700",
    low: "bg-green-100 text-green-700",
  },
  actionBtn: "px-2.5 py-1 text-xs font-medium rounded-lg border transition-colors",
  draftBtn: "text-blue-600 border-blue-200 hover:bg-blue-50",
  editBtn: "text-gray-600 border-gray-200 hover:bg-gray-50",
  deleteBtn: "text-red-500 border-red-200 hover:bg-red-50",
  emptyRow: "py-16 text-center text-gray-400 text-sm",
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface Props {
  breaches: BreachIncident[];
  onUpdate: (breachId: string, body: BreachUpdateRequest) => Promise<void>;
  onDelete: (breachId: string) => void;
  onDraft: (breachId: string) => Promise<{ breach_id: string; draft: { subject: string; body: string } }>;
}

// ── Component ─────────────────────────────────────────────────────────────────

export const BreachTable = ({ breaches, onUpdate, onDelete, onDraft }: Props) => {
  // ── State ─────────────────────────────────────────────────────────────────
  const [draftModal, setDraftModal] = useState<{ subject: string; body: string } | null>(null);
  const [drafting, setDrafting] = useState<string | null>(null);

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleStatusChange = async (b: BreachIncident, status: string) => {
    try {
      await onUpdate(b.breach_id, { status: status as BreachIncident["status"] });
    } catch {
      toast.error("Failed to update status");
    }
  };

  const handleDraft = async (b: BreachIncident) => {
    if (b.ai_notification_draft) {
      setDraftModal(b.ai_notification_draft);
      return;
    }
    setDrafting(b.breach_id);
    try {
      const res = await onDraft(b.breach_id);
      setDraftModal(res.draft);
    } catch {
      toast.error("Failed to generate draft");
    } finally {
      setDrafting(null);
    }
  };

  // ── Render helpers ────────────────────────────────────────────────────────

  const renderSeverity = (severity: string | null) => {
    if (!severity) return null;
    const cls = styles.severityBadge[severity as keyof typeof styles.severityBadge] ?? styles.severityBadge.medium;
    return <span className={`${styles.severityBadge.base} ${cls}`}>{severity.charAt(0).toUpperCase() + severity.slice(1)}</span>;
  };

  const renderRow = (b: BreachIncident) => (
    <tr key={b.breach_id} className={styles.tr}>
      <td className={styles.td}>
        <div className={styles.title}>{b.title}</div>
        <div className={styles.meta}>
          {b.regulation?.toUpperCase()} · {b.breach_type?.replace("_", " ")}
          {b.affected_individual_count != null && ` · ${b.affected_individual_count.toLocaleString()} individuals`}
        </div>
      </td>
      <td className={styles.td}>{renderSeverity(b.severity)}</td>
      <td className={styles.td}>
        {b.discovered_at && (
          <CountdownBadge
            deadlineAt={b.deadline_at}
            hoursWindow={b.deadline_hours}
            dpaNotified={b.dpa_notified}
          />
        )}
      </td>
      <td className={styles.td}>
        <select
          className="text-xs border border-gray-200 rounded-lg px-2 py-1 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
          value={b.status ?? "draft"}
          onChange={(e) => handleStatusChange(b, e.target.value)}
        >
          <option value="draft">Draft</option>
          <option value="under_investigation">Investigating</option>
          <option value="reported_to_dpa">Reported to DPA</option>
          <option value="reported_to_individuals">Individuals notified</option>
          <option value="closed">Closed</option>
        </select>
      </td>
      <td className={styles.td}>
        <div className="flex items-center gap-2">
          <button
            className={`${styles.actionBtn} ${styles.draftBtn}`}
            onClick={() => handleDraft(b)}
            disabled={drafting === b.breach_id}
          >
            {drafting === b.breach_id ? "Drafting..." : b.ai_notification_draft ? "View draft" : "Draft notification"}
          </button>
          <button
            className={`${styles.actionBtn} ${styles.deleteBtn}`}
            onClick={() => onDelete(b.breach_id)}
          >
            Delete
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
              <th className={styles.th}>Incident</th>
              <th className={styles.th}>Severity</th>
              <th className={styles.th}>Notification deadline</th>
              <th className={styles.th}>Status</th>
              <th className={styles.th}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {breaches.length === 0 ? (
              <tr>
                <td colSpan={5} className={styles.emptyRow}>
                  No breach incidents recorded.
                </td>
              </tr>
            ) : (
              breaches.map(renderRow)
            )}
          </tbody>
        </table>
      </div>

      {draftModal && (
        <NotificationDraftModal draft={draftModal} onClose={() => setDraftModal(null)} />
      )}
    </>
  );
};
