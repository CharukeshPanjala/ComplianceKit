"use client";

import { useState } from "react";
import type { DsarCreateRequest, DsarRequestType } from "@/lib/dsarApi";

// ── Constants ─────────────────────────────────────────────────────────────────

const REQUEST_TYPES: { value: DsarRequestType; label: string }[] = [
  { value: "access", label: "Right of Access (Art. 15)" },
  { value: "rectification", label: "Right to Rectification (Art. 16)" },
  { value: "erasure", label: "Right to Erasure / Forgotten (Art. 17)" },
  { value: "portability", label: "Right to Data Portability (Art. 20)" },
  { value: "restriction", label: "Right to Restrict Processing (Art. 18)" },
  { value: "objection", label: "Right to Object (Art. 21)" },
  { value: "withdraw_consent", label: "Withdraw Consent (Art. 7)" },
];

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  overlay: "fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4",
  modal: "bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto",
  header: "flex items-center justify-between px-6 py-4 border-b border-gray-100",
  title: "text-base font-semibold text-gray-900",
  closeBtn: "p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-500",
  body: "px-6 py-5 space-y-4",
  label: "block text-sm font-medium text-gray-700 mb-1",
  input: "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D97706]",
  select: "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-[#D97706]",
  textarea: "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[#D97706]",
  hint: "text-xs text-gray-400 mt-1",
  footer: "px-6 py-4 border-t border-gray-100 flex justify-end gap-3",
  cancelBtn: "px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 border border-gray-200 rounded-lg transition-colors",
  submitBtn: "px-4 py-2 text-sm font-medium bg-[#D97706] hover:bg-[#B45309] text-white rounded-lg transition-colors disabled:opacity-50",
  error: "px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700",
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface Props {
  onClose: () => void;
  onSubmit: (body: DsarCreateRequest) => Promise<void>;
}

// ── Component ─────────────────────────────────────────────────────────────────

export const DsarFormModal = ({ onClose, onSubmit }: Props) => {
  // ── State ─────────────────────────────────────────────────────────────────
  const [form, setForm] = useState({
    request_type: "access" as DsarRequestType,
    requester_email: "",
    requester_name: "",
    description: "",
    received_at: new Date().toISOString().slice(0, 10),
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleChange = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async () => {
    if (!form.requester_email.trim()) { setError("Requester email is required"); return; }
    setSaving(true);
    setError(null);
    try {
      await onSubmit({
        request_type: form.request_type,
        requester_email: form.requester_email.trim(),
        requester_name: form.requester_name.trim() || undefined,
        description: form.description.trim() || undefined,
        received_at: form.received_at
          ? new Date(form.received_at).toISOString()
          : undefined,
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to log DSAR request");
    } finally {
      setSaving(false);
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <span className={styles.title}>Log DSAR Request</span>
          <button className={styles.closeBtn} onClick={onClose}>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className={styles.body}>
          {error && <div className={styles.error}>{error}</div>}

          <div>
            <label className={styles.label}>Request type *</label>
            <select
              className={styles.select}
              value={form.request_type}
              onChange={(e) => handleChange("request_type", e.target.value)}
            >
              {REQUEST_TYPES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={styles.label}>Requester email *</label>
              <input
                type="email"
                className={styles.input}
                value={form.requester_email}
                onChange={(e) => handleChange("requester_email", e.target.value)}
                placeholder="john@example.com"
              />
            </div>
            <div>
              <label className={styles.label}>Requester name</label>
              <input
                className={styles.input}
                value={form.requester_name}
                onChange={(e) => handleChange("requester_name", e.target.value)}
                placeholder="John Smith"
              />
            </div>
          </div>

          <div>
            <label className={styles.label}>Date received *</label>
            <input
              type="date"
              className={styles.input}
              value={form.received_at}
              onChange={(e) => handleChange("received_at", e.target.value)}
            />
            <p className={styles.hint}>30-day GDPR deadline is automatically calculated from this date.</p>
          </div>

          <div>
            <label className={styles.label}>Description</label>
            <textarea
              className={styles.textarea}
              rows={3}
              value={form.description}
              onChange={(e) => handleChange("description", e.target.value)}
              placeholder="What is the data subject requesting?"
            />
          </div>
        </div>

        <div className={styles.footer}>
          <button className={styles.cancelBtn} onClick={onClose}>Cancel</button>
          <button className={styles.submitBtn} onClick={handleSubmit} disabled={saving}>
            {saving ? "Logging..." : "Log request"}
          </button>
        </div>
      </div>
    </div>
  );
};
