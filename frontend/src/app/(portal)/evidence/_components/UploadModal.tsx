"use client";

import { useRef, useState } from "react";
import { useUploadEvidence } from "@/lib/hooks/useEvidence";
import { EvaluationResults } from "./EvaluationResults";
import { DOCUMENT_TYPE_META } from "@/types/evidence";
import type { DocumentType, EvidenceDocument } from "@/types/evidence";

// ── Styles ────────────────────────────────────────────────

const styles = {
  overlay: "fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4",
  modal: "bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto",
  header: "flex items-center justify-between px-6 pt-6 pb-4 border-b border-[#F1F5F9]",
  title: "text-base font-bold text-[#0F172A]",
  closeBtn: "w-8 h-8 flex items-center justify-center rounded-lg text-[#94A3B8] hover:text-[#334155] hover:bg-[#F8FAFC] transition-colors",
  body: "px-6 py-5 space-y-5",
  docMeta: "text-sm text-[#64748B] leading-relaxed",
  dropZone: "relative border-2 border-dashed border-[#E2E8F0] rounded-xl p-8 text-center cursor-pointer hover:border-[#D97706] hover:bg-amber-50/30 transition-colors",
  dropZoneActive: "border-[#D97706] bg-amber-50/30",
  dropIcon: "w-8 h-8 text-[#94A3B8] mx-auto mb-2",
  dropText: "text-sm text-[#64748B]",
  dropHint: "text-xs text-[#94A3B8] mt-1",
  fileInput: "absolute inset-0 w-full h-full opacity-0 cursor-pointer",
  selectedFile: "flex items-center gap-3 p-3 bg-[#F8FAFC] rounded-lg border border-[#E2E8F0]",
  fileName: "text-sm font-medium text-[#334155] truncate flex-1",
  fileSize: "text-xs text-[#94A3B8] flex-shrink-0",
  clearBtn: "w-6 h-6 flex items-center justify-center text-[#94A3B8] hover:text-red-400 transition-colors flex-shrink-0",
  errorBox: "p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700",
  resultsSection: "border-t border-[#F1F5F9] pt-4",
  resultsTitle: "text-sm font-semibold text-[#0F172A] mb-3",
  footer: "px-6 pb-6 flex gap-3",
  cancelBtn: "flex-1 py-2.5 text-sm font-medium text-[#64748B] border border-[#E2E8F0] rounded-xl hover:bg-[#F8FAFC] transition-colors",
  uploadBtn: "flex-1 py-2.5 text-sm font-medium text-white bg-[#D97706] hover:bg-[#B45309] rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
};

// ── Sub-components ────────────────────────────────────────

const UploadIcon = () => (
  <svg className={styles.dropIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
  </svg>
);

const CloseIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const DocIcon = () => (
  <svg className="w-4 h-4 text-[#D97706] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

// ── Component ─────────────────────────────────────────────

interface Props {
  documentType: DocumentType;
  onClose: () => void;
}

export const UploadModal = ({ documentType, onClose }: Props) => {
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [result, setResult] = useState<EvidenceDocument | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { mutateAsync: upload, isPending, error: uploadError } = useUploadEvidence();

  const meta = DOCUMENT_TYPE_META[documentType];

  // ── Handlers ──────────────────────────────────────────

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0] ?? null;
    setFileError(null);
    setResult(null);
    if (!selected) return;
    if (!selected.name.toLowerCase().endsWith(".pdf")) {
      setFileError("Only PDF files are supported.");
      setFile(null);
      return;
    }
    if (selected.size > 10 * 1024 * 1024) {
      setFileError("File must be under 10MB.");
      setFile(null);
      return;
    }
    setFile(selected);
  };

  const handleClearFile = () => {
    setFile(null);
    setFileError(null);
    setResult(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const handleUpload = async () => {
    if (!file) return;
    try {
      const doc = await upload({ documentType, file });
      setResult(doc);
    } catch {
      // error shown via uploadError
    }
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) onClose();
  };

  // ── Render helpers ─────────────────────────────────────

  const renderFileInput = () => (
    <div>
      {!file ? (
        <label className={styles.dropZone}>
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            className={styles.fileInput}
            onChange={handleFileChange}
          />
          <UploadIcon />
          <p className={styles.dropText}>Click to select a PDF</p>
          <p className={styles.dropHint}>Max 10MB, PDF only</p>
        </label>
      ) : (
        <div className={styles.selectedFile}>
          <DocIcon />
          <span className={styles.fileName}>{file.name}</span>
          <span className={styles.fileSize}>{(file.size / 1024).toFixed(0)} KB</span>
          <button onClick={handleClearFile} className={styles.clearBtn}>
            <CloseIcon />
          </button>
        </div>
      )}
    </div>
  );

  const renderError = () => {
    const msg = fileError ?? (uploadError instanceof Error ? uploadError.message : null);
    if (!msg) return null;
    return <p className={styles.errorBox}>{msg}</p>;
  };

  const renderResults = () => {
    if (!result?.evaluation_results) return null;
    return (
      <div className={styles.resultsSection}>
        <p className={styles.resultsTitle}>Evaluation Results</p>
        <EvaluationResults results={result.evaluation_results} />
      </div>
    );
  };

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.overlay} onClick={handleOverlayClick}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <span className={styles.title}>Upload {meta.label}</span>
          <button onClick={onClose} className={styles.closeBtn}>
            <CloseIcon />
          </button>
        </div>

        <div className={styles.body}>
          <p className={styles.docMeta}>
            Covers Art. {meta.articles.join(", ")} — {meta.description}
          </p>
          {renderFileInput()}
          {renderError()}
          {isPending && (
            <p className="text-sm text-[#64748B] text-center animate-pulse">
              Analysing document...
            </p>
          )}
          {renderResults()}
        </div>

        <div className={styles.footer}>
          <button onClick={onClose} className={styles.cancelBtn}>
            {result ? "Done" : "Cancel"}
          </button>
          {!result && (
            <button
              onClick={handleUpload}
              disabled={!file || isPending}
              className={styles.uploadBtn}
            >
              {isPending ? "Uploading..." : "Upload and Analyse"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
