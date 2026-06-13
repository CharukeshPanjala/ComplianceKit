// WHAT: ROPA edit modal | CHANGE: new file | WHY: COM-173 — edit/activate/archive a ROPA entry
"use client";

import { useState } from "react";
import type { RopaEntry, RopaStatus } from "@/lib/ropaApi";

// ── Constants ─────────────────────────────────────────────────────────────────

const LEGAL_BASIS_OPTIONS = [
  { value: "consent", label: "Consent (Art. 6(1)(a))" },
  { value: "contract", label: "Contract (Art. 6(1)(b))" },
  { value: "legal_obligation", label: "Legal Obligation (Art. 6(1)(c))" },
  { value: "vital_interests", label: "Vital Interests (Art. 6(1)(d))" },
  { value: "public_task", label: "Public Task (Art. 6(1)(e))" },
  { value: "legitimate_interests", label: "Legitimate Interests (Art. 6(1)(f))" },
];

const TRANSFER_MECHANISM_OPTIONS = [
  { value: "none", label: "No transfers outside EEA" },
  { value: "scc", label: "Standard Contractual Clauses" },
  { value: "bcr", label: "Binding Corporate Rules" },
  { value: "adequacy_decision", label: "Adequacy Decision" },
  { value: "derogation", label: "Art. 49 Derogation" },
];

const SPECIAL_CONDITION_OPTIONS = [
  { value: "explicit_consent", label: "Explicit consent (Art. 9(2)(a))" },
  { value: "employment_law", label: "Employment law (Art. 9(2)(b))" },
  { value: "vital_interests", label: "Vital interests (Art. 9(2)(c))" },
  { value: "non_profit", label: "Non-profit body (Art. 9(2)(d))" },
  { value: "made_public", label: "Made public (Art. 9(2)(e))" },
  { value: "legal_claims", label: "Legal claims (Art. 9(2)(f))" },
  { value: "public_interest", label: "Public interest (Art. 9(2)(g))" },
  { value: "health_care", label: "Health or social care (Art. 9(2)(h))" },
  { value: "public_health", label: "Public health (Art. 9(2)(i))" },
  { value: "research", label: "Research / statistics (Art. 9(2)(j))" },
];

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  overlay: "fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4",
  modal: "bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col",
  header: "flex items-center justify-between px-6 py-4 border-b border-gray-100",
  title: "text-base font-bold text-gray-900",
  closeBtn: "text-gray-400 hover:text-gray-600 transition-colors",
  body: "overflow-y-auto flex-1 px-6 py-4 space-y-4",
  section: "space-y-3",
  sectionTitle: "text-xs font-semibold text-gray-400 uppercase tracking-wider",
  row: "grid grid-cols-2 gap-3",
  field: "flex flex-col gap-1",
  label: "text-xs font-medium text-gray-600",
  input: "w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0F2044]/20 focus:border-[#0F2044]",
  select: "w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0F2044]/20 focus:border-[#0F2044] bg-white",
  textarea: "w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0F2044]/20 focus:border-[#0F2044] resize-none",
  checkRow: "flex items-center gap-2",
  check: "w-4 h-4 text-[#0F2044] rounded",
  checkLabel: "text-sm text-gray-700",
  footer: "flex items-center justify-between px-6 py-4 border-t border-gray-100 gap-3",
  statusBtns: "flex gap-2",
  statusBtn: (active: boolean, color: string) =>
    `px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors ${active ? `bg-${color}-50 border-${color}-200 text-${color}-700` : "border-gray-200 text-gray-500 hover:border-gray-300"}`,
  saveBtn: "px-5 py-2 bg-[#0F2044] text-white text-sm font-semibold rounded-xl hover:bg-[#1a3366] transition-colors disabled:opacity-50",
  cancelBtn: "px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors",
};

// ── Component ─────────────────────────────────────────────────────────────────

interface RopaEditModalProps {
  entry: RopaEntry;
  onSave: (updates: Partial<RopaEntry>) => void;
  onStatusChange: (status: RopaStatus) => void;
  onClose: () => void;
  isSaving: boolean;
}

export const RopaEditModal = ({ entry, onSave, onStatusChange, onClose, isSaving }: RopaEditModalProps) => {
  const [form, setForm] = useState({
    activity_name: entry.activity_name ?? "",
    purpose: entry.purpose ?? "",
    legal_basis: entry.legal_basis ?? "legitimate_interests",
    retention_period: entry.retention_period ?? "",
    security_measures: entry.security_measures ?? "",
    transfer_mechanism: entry.transfer_mechanism ?? "none",
    special_category_condition: entry.special_category_condition ?? "",
    has_special_category_data: entry.has_special_category_data ?? false,
    has_automated_decision_making: entry.has_automated_decision_making ?? false,
    requires_dpia: entry.requires_dpia ?? false,
    dpia_completed: entry.dpia_completed ?? false,
  });

  const handleField = (field: string, value: string | boolean) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSave = () => onSave(form);

  const renderField = (label: string, field: string, type: "text" | "textarea" = "text") => (
    <div className={styles.field}>
      <label className={styles.label}>{label}</label>
      {type === "textarea" ? (
        <textarea
          className={styles.textarea}
          rows={2}
          value={(form as unknown as Record<string, string>)[field] ?? ""}
          onChange={(e) => handleField(field, e.target.value)}
        />
      ) : (
        <input
          className={styles.input}
          value={(form as unknown as Record<string, string>)[field] ?? ""}
          onChange={(e) => handleField(field, e.target.value)}
        />
      )}
    </div>
  );

  const renderSelect = (label: string, field: string, options: { value: string; label: string }[]) => (
    <div className={styles.field}>
      <label className={styles.label}>{label}</label>
      <select
        className={styles.select}
        value={(form as unknown as Record<string, string>)[field] ?? ""}
        onChange={(e) => handleField(field, e.target.value)}
      >
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );

  const renderCheck = (label: string, field: string) => (
    <label className={styles.checkRow}>
      <input
        type="checkbox"
        className={styles.check}
        checked={(form as unknown as Record<string, boolean>)[field] ?? false}
        onChange={(e) => handleField(field, e.target.checked)}
      />
      <span className={styles.checkLabel}>{label}</span>
    </label>
  );

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <span className={styles.title}>Edit Processing Activity</span>
          <button className={styles.closeBtn} onClick={onClose}>✕</button>
        </div>

        <div className={styles.body}>
          <div className={styles.section}>
            <p className={styles.sectionTitle}>Activity</p>
            <div className={styles.row}>
              {renderField("Activity name", "activity_name")}
              {renderField("Purpose", "purpose")}
            </div>
            {renderSelect("Legal basis", "legal_basis", LEGAL_BASIS_OPTIONS)}
            {renderField("Retention period", "retention_period")}
            {renderField("Security measures", "security_measures", "textarea")}
          </div>

          <div className={styles.section}>
            <p className={styles.sectionTitle}>Transfers</p>
            {renderSelect("Transfer mechanism", "transfer_mechanism", TRANSFER_MECHANISM_OPTIONS)}
          </div>

          <div className={styles.section}>
            <p className={styles.sectionTitle}>Special categories & automated decisions</p>
            {renderCheck("Processes special category data (Art. 9)", "has_special_category_data")}
            {form.has_special_category_data && renderSelect("Art. 9(2) condition", "special_category_condition", SPECIAL_CONDITION_OPTIONS)}
            {renderCheck("Has automated decision-making (Art. 22)", "has_automated_decision_making")}
          </div>

          <div className={styles.section}>
            <p className={styles.sectionTitle}>DPIA (Art. 35)</p>
            {renderCheck("Requires Data Protection Impact Assessment", "requires_dpia")}
            {form.requires_dpia && renderCheck("DPIA completed", "dpia_completed")}
          </div>
        </div>

        <div className={styles.footer}>
          <div className={styles.statusBtns}>
            {(["draft", "active", "archived"] as RopaStatus[]).map((s) => (
              <button
                key={s}
                onClick={() => onStatusChange(s)}
                className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors ${
                  entry.status === s
                    ? s === "active" ? "bg-green-50 border-green-200 text-green-700"
                      : s === "archived" ? "bg-gray-100 border-gray-300 text-gray-600"
                      : "bg-amber-50 border-amber-200 text-amber-700"
                    : "border-gray-200 text-gray-400 hover:border-gray-300"
                }`}
              >
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <button className={styles.cancelBtn} onClick={onClose}>Cancel</button>
            <button className={styles.saveBtn} onClick={handleSave} disabled={isSaving}>
              {isSaving ? "Saving…" : "Save changes"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
