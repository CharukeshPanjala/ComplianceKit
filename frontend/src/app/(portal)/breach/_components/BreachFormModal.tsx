"use client";

import { useState } from "react";
import type { BreachCreateRequest, BreachType, BreachSeverity, BreachRegulation } from "@/lib/breachApi";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  overlay: "fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4",
  modal: "bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto",
  header: "flex items-center justify-between px-6 py-4 border-b border-gray-100",
  title: "text-base font-semibold text-gray-900",
  closeBtn: "p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-500",
  body: "px-6 py-5 space-y-4",
  label: "block text-sm font-medium text-gray-700 mb-1",
  input: "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500",
  select: "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500",
  textarea: "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500",
  checkRow: "flex items-center gap-2",
  checkbox: "w-4 h-4 text-blue-600 border-gray-300 rounded cursor-pointer",
  checkLabel: "text-sm text-gray-700",
  hint: "text-xs text-amber-600 mt-1",
  footer: "px-6 py-4 border-t border-gray-100 flex justify-end gap-3",
  cancelBtn: "px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 border border-gray-200 rounded-lg transition-colors",
  submitBtn: "px-4 py-2 text-sm font-medium bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50",
  error: "px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700",
};

const REGULATION_HINTS: Record<string, string> = {
  gdpr: "GDPR Art. 33: 72-hour notification window to DPA",
  nis2: "NIS2 Art. 23: 24-hour notification window to authority",
  both: "Both apply, 24-hour window (tightest deadline)",
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface Props {
  onClose: () => void;
  onSubmit: (body: BreachCreateRequest) => Promise<void>;
}

// ── Component ─────────────────────────────────────────────────────────────────

export const BreachFormModal = ({ onClose, onSubmit }: Props) => {
  // ── State ─────────────────────────────────────────────────────────────────
  const [form, setForm] = useState({
    title: "",
    description: "",
    breach_type: "confidentiality" as BreachType,
    severity: "medium" as BreachSeverity,
    regulation: "gdpr" as BreachRegulation,
    discovered_at: new Date().toISOString().slice(0, 16),
    occurred_at: "",
    affected_individual_count: "",
    data_categories_affected: "",
    notification_required: false,
    containment_measures: "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleChange = (field: string, value: string | boolean) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async () => {
    if (!form.title.trim()) { setError("Title is required"); return; }
    if (!form.discovered_at) { setError("Discovery date/time is required"); return; }
    setSaving(true);
    setError(null);
    try {
      const categories = form.data_categories_affected
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      await onSubmit({
        title: form.title.trim(),
        description: form.description.trim() || undefined,
        breach_type: form.breach_type,
        severity: form.severity,
        regulation: form.regulation,
        discovered_at: new Date(form.discovered_at).toISOString(),
        occurred_at: form.occurred_at ? new Date(form.occurred_at).toISOString() : undefined,
        affected_individual_count: form.affected_individual_count
          ? parseInt(form.affected_individual_count, 10)
          : undefined,
        data_categories_affected: categories.length ? categories : undefined,
        notification_required: form.notification_required,
        containment_measures: form.containment_measures.trim() || undefined,
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create incident");
    } finally {
      setSaving(false);
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <span className={styles.title}>Report Breach Incident</span>
          <button className={styles.closeBtn} onClick={onClose}>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className={styles.body}>
          {error && <div className={styles.error}>{error}</div>}

          <div>
            <label className={styles.label}>Title *</label>
            <input
              className={styles.input}
              value={form.title}
              onChange={(e) => handleChange("title", e.target.value)}
              placeholder="e.g. Unauthorised access to customer database"
            />
          </div>

          <div>
            <label className={styles.label}>Description</label>
            <textarea
              className={styles.textarea}
              rows={3}
              value={form.description}
              onChange={(e) => handleChange("description", e.target.value)}
              placeholder="Describe what happened..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={styles.label}>Discovered at *</label>
              <input
                type="datetime-local"
                className={styles.input}
                value={form.discovered_at}
                onChange={(e) => handleChange("discovered_at", e.target.value)}
              />
            </div>
            <div>
              <label className={styles.label}>Occurred at</label>
              <input
                type="datetime-local"
                className={styles.input}
                value={form.occurred_at}
                onChange={(e) => handleChange("occurred_at", e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className={styles.label}>Type</label>
              <select className={styles.select} value={form.breach_type} onChange={(e) => handleChange("breach_type", e.target.value)}>
                <option value="confidentiality">Confidentiality</option>
                <option value="integrity">Integrity</option>
                <option value="availability">Availability</option>
                <option value="combined">Combined</option>
              </select>
            </div>
            <div>
              <label className={styles.label}>Severity</label>
              <select className={styles.select} value={form.severity} onChange={(e) => handleChange("severity", e.target.value)}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div>
              <label className={styles.label}>Regulation</label>
              <select className={styles.select} value={form.regulation} onChange={(e) => handleChange("regulation", e.target.value)}>
                <option value="gdpr">GDPR</option>
                <option value="nis2">NIS2</option>
                <option value="both">Both</option>
              </select>
            </div>
          </div>

          {REGULATION_HINTS[form.regulation] && (
            <p className={styles.hint}>{REGULATION_HINTS[form.regulation]}</p>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={styles.label}>Affected individuals</label>
              <input
                type="number"
                className={styles.input}
                value={form.affected_individual_count}
                onChange={(e) => handleChange("affected_individual_count", e.target.value)}
                placeholder="e.g. 500"
                min={0}
              />
            </div>
            <div>
              <label className={styles.label}>Data categories (comma-separated)</label>
              <input
                className={styles.input}
                value={form.data_categories_affected}
                onChange={(e) => handleChange("data_categories_affected", e.target.value)}
                placeholder="e.g. email, name, financial"
              />
            </div>
          </div>

          <div>
            <label className={styles.label}>Containment measures taken</label>
            <textarea
              className={styles.textarea}
              rows={2}
              value={form.containment_measures}
              onChange={(e) => handleChange("containment_measures", e.target.value)}
              placeholder="What steps have already been taken to contain this breach?"
            />
          </div>

          <div className={styles.checkRow}>
            <input
              id="notif_required"
              type="checkbox"
              className={styles.checkbox}
              checked={form.notification_required}
              onChange={(e) => handleChange("notification_required", e.target.checked)}
            />
            <label htmlFor="notif_required" className={styles.checkLabel}>
              DPA notification required
            </label>
          </div>
        </div>

        <div className={styles.footer}>
          <button className={styles.cancelBtn} onClick={onClose}>Cancel</button>
          <button className={styles.submitBtn} onClick={handleSubmit} disabled={saving}>
            {saving ? "Reporting..." : "Report incident"}
          </button>
        </div>
      </div>
    </div>
  );
};
