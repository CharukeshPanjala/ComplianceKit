"use client";

import { useState } from "react";
import type { DsarRequest, DsarUpdateRequest, DsarStatus } from "@/lib/dsarApi";
import { DaysRemainingBadge } from "./DaysRemainingBadge";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  overlay: "fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4",
  modal: "bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col",
  header: "flex items-start justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0",
  titleBlock: "flex-1 min-w-0",
  title: "text-base font-semibold text-gray-900",
  subtitle: "text-xs text-gray-400 mt-0.5",
  closeBtn: "p-1.5 ml-4 rounded-lg hover:bg-gray-100 transition-colors text-gray-500 flex-shrink-0",
  body: "flex-1 overflow-y-auto px-6 py-5 space-y-5",
  section: "space-y-1",
  sectionTitle: "text-xs font-semibold text-gray-400 uppercase tracking-wide",
  row: "grid grid-cols-2 gap-x-4 gap-y-3",
  fieldLabel: "text-xs text-gray-500",
  fieldValue: "text-sm text-gray-800 font-medium",
  label: "block text-sm font-medium text-gray-700 mb-1",
  select: "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500",
  input: "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500",
  textarea: "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500",
  checkRow: "flex items-center gap-2",
  checkbox: "w-4 h-4 text-blue-600 border-gray-300 rounded cursor-pointer",
  checkLabel: "text-sm text-gray-700",
  footer: "px-6 py-4 border-t border-gray-100 flex justify-end gap-3 flex-shrink-0",
  cancelBtn: "px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 border border-gray-200 rounded-lg transition-colors",
  saveBtn: "px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50",
  error: "px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700",
};

const TERMINAL_STATUSES = new Set(["completed", "rejected", "withdrawn"]);

// ── Types ─────────────────────────────────────────────────────────────────────

interface Props {
  dsar: DsarRequest;
  onClose: () => void;
  onSave: (dsarId: string, body: DsarUpdateRequest) => Promise<void>;
}

// ── Component ─────────────────────────────────────────────────────────────────

export const DsarDetailModal = ({ dsar, onClose, onSave }: Props) => {
  // ── State ─────────────────────────────────────────────────────────────────
  const [form, setForm] = useState({
    status: dsar.status ?? "pending",
    identity_verified: dsar.identity_verified,
    identity_verification_method: dsar.identity_verification_method ?? "",
    assigned_to: dsar.assigned_to ?? "",
    rejection_reason: dsar.rejection_reason ?? "",
    internal_notes: dsar.internal_notes ?? "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isTerminal = TERMINAL_STATUSES.has(dsar.status ?? "");

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleChange = (field: string, value: string | boolean) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const body: DsarUpdateRequest = {
        status: form.status as DsarStatus,
        identity_verified: form.identity_verified,
        identity_verification_method: form.identity_verification_method || undefined,
        assigned_to: form.assigned_to || undefined,
        rejection_reason: form.rejection_reason || undefined,
        internal_notes: form.internal_notes || undefined,
      };
      await onSave(dsar.dsar_id, body);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <div className={styles.titleBlock}>
            <div className={styles.title}>{dsar.request_type_label}</div>
            <div className={styles.subtitle}>
              {dsar.requester_name ?? dsar.requester_email} · received {dsar.received_at ? new Date(dsar.received_at).toLocaleDateString() : "—"}
            </div>
          </div>
          <button className={styles.closeBtn} onClick={onClose}>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className={styles.body}>
          {error && <div className={styles.error}>{error}</div>}

          <div className={styles.section}>
            <div className={styles.sectionTitle}>Request details</div>
            <div className={styles.row}>
              <div>
                <div className={styles.fieldLabel}>Requester email</div>
                <div className={styles.fieldValue}>{dsar.requester_email}</div>
              </div>
              <div>
                <div className={styles.fieldLabel}>Due date</div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className={styles.fieldValue}>
                    {dsar.due_date ? new Date(dsar.due_date).toLocaleDateString() : "—"}
                  </span>
                  <DaysRemainingBadge
                    daysRemaining={dsar.days_remaining}
                    isOverdue={dsar.is_overdue}
                    isTerminal={isTerminal}
                  />
                </div>
              </div>
            </div>
            {dsar.description && (
              <div className="mt-2">
                <div className={styles.fieldLabel}>Description</div>
                <div className="text-sm text-gray-700 mt-0.5">{dsar.description}</div>
              </div>
            )}
          </div>

          <div className={styles.section}>
            <div className={styles.sectionTitle}>Status &amp; assignment</div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={styles.label}>Status</label>
                <select
                  className={styles.select}
                  value={form.status}
                  onChange={(e) => handleChange("status", e.target.value)}
                >
                  <option value="pending">Pending</option>
                  <option value="in_progress">In progress</option>
                  <option value="awaiting_info">Awaiting info</option>
                  <option value="completed">Completed</option>
                  <option value="rejected">Rejected</option>
                  <option value="withdrawn">Withdrawn</option>
                </select>
              </div>
              <div>
                <label className={styles.label}>Assigned to (user ID)</label>
                <input
                  className={styles.input}
                  value={form.assigned_to}
                  onChange={(e) => handleChange("assigned_to", e.target.value)}
                  placeholder="user_xxx"
                />
              </div>
            </div>
          </div>

          <div className={styles.section}>
            <div className={styles.sectionTitle}>Identity verification</div>
            <div className={styles.checkRow}>
              <input
                id="id_verified"
                type="checkbox"
                className={styles.checkbox}
                checked={form.identity_verified}
                onChange={(e) => handleChange("identity_verified", e.target.checked)}
              />
              <label htmlFor="id_verified" className={styles.checkLabel}>
                Identity verified
              </label>
            </div>
            {form.identity_verified && (
              <div className="mt-2">
                <label className={styles.label}>Verification method</label>
                <input
                  className={styles.input}
                  value={form.identity_verification_method}
                  onChange={(e) => handleChange("identity_verification_method", e.target.value)}
                  placeholder="e.g. email confirmation, ID document"
                />
              </div>
            )}
          </div>

          {(form.status === "rejected") && (
            <div>
              <label className={styles.label}>Rejection reason</label>
              <textarea
                className={styles.textarea}
                rows={2}
                value={form.rejection_reason}
                onChange={(e) => handleChange("rejection_reason", e.target.value)}
                placeholder="Reason for rejecting this request..."
              />
            </div>
          )}

          <div>
            <label className={styles.label}>Internal notes</label>
            <textarea
              className={styles.textarea}
              rows={3}
              value={form.internal_notes}
              onChange={(e) => handleChange("internal_notes", e.target.value)}
              placeholder="Internal notes not shared with the requester..."
            />
          </div>
        </div>

        <div className={styles.footer}>
          <button className={styles.cancelBtn} onClick={onClose}>Cancel</button>
          <button className={styles.saveBtn} onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "Save changes"}
          </button>
        </div>
      </div>
    </div>
  );
};
