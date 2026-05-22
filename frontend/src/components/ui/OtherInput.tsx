"use client";

import { useState, KeyboardEvent } from "react";
import { Button } from "@/components/ui/Button";

// ── Styles ─────────────────────────────────────────────────

const styles = {
  wrapper: "mt-2 space-y-2",
  chipRow: "flex flex-wrap gap-2",
  chip: "inline-flex items-center gap-1 bg-navy/10 border border-navy/30 text-navy px-2.5 py-0.5 rounded-full text-xs font-medium",
  chipRemove: "text-navy/40 hover:text-navy ml-0.5 font-bold text-sm leading-none",
  row: "flex gap-2",
  input:
    "flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none " +
    "focus:ring-2 focus:ring-navy focus:border-transparent",
};

// ── Types ──────────────────────────────────────────────────

interface OtherInputProps {
  show: boolean;
  values: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
  label?: string;
}

// ── Component ─────────────────────────────────────────────

export function OtherInput({
  show,
  values,
  onChange,
  placeholder = "Type and press Enter to add...",
  label,
}: OtherInputProps) {
  const [draft, setDraft] = useState("");

  if (!show) return null;

  const confirm = () => {
    const trimmed = draft.trim();
    if (!trimmed || values.includes(trimmed)) return;
    onChange([...values, trimmed]);
    setDraft("");
  };

  const remove = (value: string) => {
    onChange(values.filter((v) => v !== value));
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      confirm();
    }
  };

  return (
    <div className={styles.wrapper}>
      {label && <p className="text-xs text-gray-500">{label}</p>}

      {values.length > 0 && (
        <div className={styles.chipRow}>
          {values.map((v) => (
            <span key={v} className={styles.chip}>
              {v}
              <button type="button" onClick={() => remove(v)} className={styles.chipRemove}>
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      <div className={styles.row}>
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={confirm}
          placeholder={placeholder}
          className={styles.input}
        />
        <Button type="button" variant="secondary" onClick={confirm} disabled={!draft.trim()}>
          + Add
        </Button>
      </div>
    </div>
  );
}
