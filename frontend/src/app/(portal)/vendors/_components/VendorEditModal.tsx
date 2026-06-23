"use client";

import { useState } from "react";
import type { Processor, ProcessorUpdateRequest, ProcessorStatus, ProcessorRisk, ProcessorTransferMechanism } from "@/lib/processorsApi";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  overlay: "fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4",
  modal: "bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto",
  header: "flex items-center justify-between px-6 py-4 border-b border-gray-100",
  title: "text-lg font-semibold text-gray-900",
  closeBtn: "p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-500",
  body: "px-6 py-5 space-y-4",
  label: "block text-sm font-medium text-gray-700 mb-1",
  input: "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
  select: "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
  textarea: "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none",
  checkRow: "flex items-center gap-3",
  checkbox: "w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer",
  checkLabel: "text-sm text-gray-700",
  footer: "px-6 py-4 border-t border-gray-100 flex justify-end gap-3",
  cancelBtn: "px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 border border-gray-200 rounded-lg transition-colors",
  saveBtn: "px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50",
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface Props {
  processor: Processor;
  onClose: () => void;
  onSave: (processorId: string, body: ProcessorUpdateRequest) => Promise<void>;
}

type FormState = {
  dpa_signed: boolean;
  dpa_date: string;
  contract_review_date: string;
  status: ProcessorStatus;
  risk_level: ProcessorRisk;
  transfer_mechanism: ProcessorTransferMechanism | "";
  notes: string;
  service_description: string;
};

// ── Component ─────────────────────────────────────────────────────────────────

export const VendorEditModal = ({ processor, onClose, onSave }: Props) => {
  // ── State ─────────────────────────────────────────────────────────────────
  const [form, setForm] = useState<FormState>({
    dpa_signed: processor.dpa_signed,
    dpa_date: processor.dpa_date ?? "",
    contract_review_date: processor.contract_review_date ?? "",
    status: (processor.status as ProcessorStatus) ?? "active",
    risk_level: (processor.risk_level as ProcessorRisk) ?? "medium",
    transfer_mechanism: (processor.transfer_mechanism as ProcessorTransferMechanism) ?? "",
    notes: processor.notes ?? "",
    service_description: processor.service_description ?? "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleChange = (field: keyof FormState, value: string | boolean) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    setSaving(true);
    setError(null);
    try {
      const body: ProcessorUpdateRequest = {
        dpa_signed: form.dpa_signed,
        dpa_date: form.dpa_date || null,
        contract_review_date: form.contract_review_date || null,
        status: form.status,
        risk_level: form.risk_level,
        transfer_mechanism: (form.transfer_mechanism as ProcessorTransferMechanism) || undefined,
        notes: form.notes || null,
        service_description: form.service_description || null,
      };
      await onSave(processor.processor_id, body);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save changes");
    } finally {
      setSaving(false);
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <span className={styles.title}>{processor.name}</span>
          <button className={styles.closeBtn} onClick={onClose}>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className={styles.body}>
          {error && (
            <div className="px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {error}
            </div>
          )}

          <div>
            <label className={styles.label}>Service Description</label>
            <input
              className={styles.input}
              value={form.service_description}
              onChange={(e) => handleChange("service_description", e.target.value)}
              placeholder="What does this vendor do?"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={styles.label}>Status</label>
              <select
                className={styles.select}
                value={form.status}
                onChange={(e) => handleChange("status", e.target.value)}
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="under_review">Under Review</option>
              </select>
            </div>

            <div>
              <label className={styles.label}>Risk Level</label>
              <select
                className={styles.select}
                value={form.risk_level}
                onChange={(e) => handleChange("risk_level", e.target.value)}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>

          <div>
            <label className={styles.label}>Transfer Mechanism</label>
            <select
              className={styles.select}
              value={form.transfer_mechanism}
              onChange={(e) => handleChange("transfer_mechanism", e.target.value)}
            >
              <option value="">None / EEA only</option>
              <option value="scc">Standard Contractual Clauses (SCC)</option>
              <option value="bcr">Binding Corporate Rules (BCR)</option>
              <option value="adequacy_decision">Adequacy Decision</option>
              <option value="derogation">Derogation (Art. 49)</option>
              <option value="none">No transfer mechanism</option>
            </select>
          </div>

          <div className={styles.checkRow}>
            <input
              id="dpa_signed"
              type="checkbox"
              className={styles.checkbox}
              checked={form.dpa_signed}
              onChange={(e) => handleChange("dpa_signed", e.target.checked)}
            />
            <label htmlFor="dpa_signed" className={styles.checkLabel}>
              DPA / Data Processing Agreement signed
            </label>
          </div>

          {form.dpa_signed && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={styles.label}>DPA Signed Date</label>
                <input
                  type="date"
                  className={styles.input}
                  value={form.dpa_date}
                  onChange={(e) => handleChange("dpa_date", e.target.value)}
                />
              </div>
              <div>
                <label className={styles.label}>Next Review Date</label>
                <input
                  type="date"
                  className={styles.input}
                  value={form.contract_review_date}
                  onChange={(e) => handleChange("contract_review_date", e.target.value)}
                />
              </div>
            </div>
          )}

          <div>
            <label className={styles.label}>Notes</label>
            <textarea
              className={styles.textarea}
              rows={3}
              value={form.notes}
              onChange={(e) => handleChange("notes", e.target.value)}
              placeholder="Internal notes about this vendor..."
            />
          </div>
        </div>

        <div className={styles.footer}>
          <button className={styles.cancelBtn} onClick={onClose}>
            Cancel
          </button>
          <button className={styles.saveBtn} onClick={handleSubmit} disabled={saving}>
            {saving ? "Saving..." : "Save changes"}
          </button>
        </div>
      </div>
    </div>
  );
};
