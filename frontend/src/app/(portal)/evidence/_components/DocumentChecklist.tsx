"use client";

import { useState } from "react";
import { useEvidenceList } from "@/lib/hooks/useEvidence";
import { UploadModal } from "./UploadModal";
import { DOCUMENT_TYPE_META } from "@/types/evidence";
import type { DocumentType, EvidenceDocument, OverallStatus } from "@/types/evidence";

// ── Constants ─────────────────────────────────────────────

const DOC_TYPES: DocumentType[] = [
  "privacy_notice",
  "security_policy",
  "breach_response_plan",
  "dpia_template",
];

// ── Styles ────────────────────────────────────────────────

const styles = {
  grid: "grid grid-cols-1 md:grid-cols-2 gap-4",
  card: "bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-5 flex flex-col gap-3",
  cardHeader: "flex items-start justify-between gap-2",
  cardTitle: "text-sm font-bold text-[#0F172A]",
  cardDesc: "text-xs text-[#64748B] leading-relaxed",
  articleRow: "flex flex-wrap gap-1.5",
  articleTag: "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#F1F5F9] text-[#475569]",
  statusBadge: "text-[10px] font-bold px-2.5 py-1 rounded-full flex-shrink-0",
  uploadBtn: "mt-auto text-xs font-medium py-2 px-4 rounded-lg border border-[#E2E8F0] text-[#334155] hover:bg-[#F8FAFC] transition-colors self-start",
  uploadedFile: "text-xs text-[#94A3B8] truncate",
  loading: "py-16 text-center text-sm text-[#94A3B8]",
  error: "p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700",
};

// ── Helpers ────────────────────────────────────────────────

const statusBadgeCls = (status: OverallStatus | "not_uploaded") => {
  if (status === "compliant") return `${styles.statusBadge} bg-green-50 text-green-700`;
  if (status === "partial") return `${styles.statusBadge} bg-amber-50 text-amber-700`;
  if (status === "non_compliant") return `${styles.statusBadge} bg-red-50 text-red-600`;
  return `${styles.statusBadge} bg-[#F1F5F9] text-[#94A3B8]`;
};

const statusLabel = (status: OverallStatus | "not_uploaded") => {
  if (status === "compliant") return "Compliant";
  if (status === "partial") return "Partial";
  if (status === "non_compliant") return "Not compliant";
  return "Not uploaded";
};

// ── Sub-components ────────────────────────────────────────

const UploadIcon = () => (
  <svg className="w-3.5 h-3.5 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
  </svg>
);

// ── Component ─────────────────────────────────────────────

export const DocumentChecklist = () => {
  const [activeUpload, setActiveUpload] = useState<DocumentType | null>(null);
  const { data, isLoading, error } = useEvidenceList();

  // ── Handlers ──────────────────────────────────────────

  const handleOpenUpload = (type: DocumentType) => setActiveUpload(type);
  const handleCloseUpload = () => setActiveUpload(null);

  // ── Render helpers ─────────────────────────────────────

  const getLatestDoc = (type: DocumentType): EvidenceDocument | undefined =>
    data?.documents.filter((d) => d.document_type === type)[0];

  const renderCard = (type: DocumentType) => {
    const meta = DOCUMENT_TYPE_META[type];
    const doc = getLatestDoc(type);
    const overallStatus = doc?.evaluation_results?.overall_status ?? "not_uploaded";

    return (
      <div key={type} className={styles.card}>
        <div className={styles.cardHeader}>
          <span className={styles.cardTitle}>{meta.label}</span>
          <span className={statusBadgeCls(overallStatus)}>
            {statusLabel(overallStatus)}
          </span>
        </div>

        <p className={styles.cardDesc}>{meta.description}</p>

        <div className={styles.articleRow}>
          {meta.articles.map((a) => (
            <span key={a} className={styles.articleTag}>Art. {a}</span>
          ))}
        </div>

        {doc && (
          <p className={styles.uploadedFile}>{doc.file_name}</p>
        )}

        <button
          onClick={() => handleOpenUpload(type)}
          className={styles.uploadBtn}
        >
          <UploadIcon />
          {doc ? "Replace document" : "Upload document"}
        </button>
      </div>
    );
  };

  // ── Render ────────────────────────────────────────────

  if (isLoading) return <p className={styles.loading}>Loading evidence documents...</p>;
  if (error) return <p className={styles.error}>Failed to load evidence documents. Try refreshing.</p>;

  return (
    <>
      <div className={styles.grid}>
        {DOC_TYPES.map(renderCard)}
      </div>

      {activeUpload && (
        <UploadModal documentType={activeUpload} onClose={handleCloseUpload} />
      )}
    </>
  );
};
