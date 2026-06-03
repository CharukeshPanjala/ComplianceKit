"use client";

import { useEffect, useCallback } from "react";

// ── Types ─────────────────────────────────────────────────

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl";
}

// ── Constants ─────────────────────────────────────────────

const SIZES = {
  sm: "max-w-md",
  md: "max-w-lg",
  lg: "max-w-2xl",
  xl: "max-w-4xl",
};

// ── Styles ────────────────────────────────────────────────

const styles = {
  overlay: "fixed inset-0 z-50 flex items-center justify-center p-4",
  backdrop: "absolute inset-0 bg-black/40 backdrop-blur-sm",
  panel: "relative w-full bg-white rounded-2xl shadow-xl max-h-[90vh] flex flex-col",
  header: "flex items-center justify-between px-6 py-4 border-b border-gray-100",
  title: "text-lg font-semibold text-gray-900",
  closeBtn: "text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-lg hover:bg-gray-100",
  closeIcon: "w-5 h-5",
  content: "overflow-y-auto flex-1 px-6 py-4",
};

// ── Close icon ────────────────────────────────────────────

const CloseIcon = () => (
  <svg className={styles.closeIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

// ── Component ─────────────────────────────────────────────

export const Modal = ({ isOpen, onClose, title, children, size = "md" }: ModalProps) => {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    },
    [onClose]
  );

  useEffect(() => {
    if (!isOpen) return;
    document.addEventListener("keydown", handleKeyDown);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  return (
    <div className={styles.overlay}>
      <div className={styles.backdrop} onClick={onClose} />
      <div className={`${styles.panel} ${SIZES[size]}`} role="dialog" aria-modal="true">
        {title && (
          <div className={styles.header}>
            <h2 className={styles.title}>{title}</h2>
            <button onClick={onClose} className={styles.closeBtn} aria-label="Close">
              <CloseIcon />
            </button>
          </div>
        )}
        <div className={styles.content}>{children}</div>
      </div>
    </div>
  );
};
