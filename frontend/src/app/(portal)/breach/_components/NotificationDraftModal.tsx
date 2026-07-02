"use client";

import { useState } from "react";
import { toast } from "sonner";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  overlay: "fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4",
  modal: "bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col",
  header: "flex items-center justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0",
  title: "text-base font-semibold text-gray-900",
  closeBtn: "p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-500",
  body: "flex-1 overflow-y-auto px-6 py-5 space-y-4",
  label: "text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1",
  subject: "px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-800 font-medium",
  textarea: "w-full px-3 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-700 font-mono leading-relaxed resize-none focus:outline-none focus:ring-2 focus:ring-blue-500",
  footer: "px-6 py-4 border-t border-gray-100 flex justify-between items-center flex-shrink-0",
  copyBtn: "px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors",
  closeFooterBtn: "px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 border border-gray-200 rounded-lg transition-colors",
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface Props {
  draft: { subject: string; body: string };
  onClose: () => void;
}

// ── Component ─────────────────────────────────────────────────────────────────

export const NotificationDraftModal = ({ draft, onClose }: Props) => {
  const [body, setBody] = useState(draft.body);

  const handleCopy = () => {
    navigator.clipboard.writeText(`Subject: ${draft.subject}\n\n${body}`).then(
      () => toast.success("Copied to clipboard"),
      () => toast.error("Failed to copy"),
    );
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <span className={styles.title}>DPA Notification Draft</span>
          <button className={styles.closeBtn} onClick={onClose}>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className={styles.body}>
          <div>
            <div className={styles.label}>Subject</div>
            <div className={styles.subject}>{draft.subject}</div>
          </div>
          <div>
            <div className={styles.label}>Body (edit before sending)</div>
            <textarea
              className={styles.textarea}
              rows={20}
              value={body}
              onChange={(e) => setBody(e.target.value)}
            />
          </div>
        </div>

        <div className={styles.footer}>
          <p className="text-xs text-gray-400">Review carefully before sending to your DPA</p>
          <div className="flex gap-3">
            <button className={styles.closeFooterBtn} onClick={onClose}>Close</button>
            <button className={styles.copyBtn} onClick={handleCopy}>Copy to clipboard</button>
          </div>
        </div>
      </div>
    </div>
  );
};
