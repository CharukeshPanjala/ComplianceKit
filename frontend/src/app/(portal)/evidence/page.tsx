"use client";

import { DocumentChecklist } from "./_components/DocumentChecklist";

// ── Styles ────────────────────────────────────────────────

const styles = {
  page: "p-6 lg:p-8 max-w-5xl mx-auto",
  header: "mb-6",
  heading: "text-2xl font-bold text-[#0F172A]",
  subheading: "text-sm text-[#64748B] mt-0.5",
};

// ── Component ─────────────────────────────────────────────

export default function EvidencePage() {
  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.heading}>Evidence Center</h1>
        <p className={styles.subheading}>
          Upload compliance documents to automatically evaluate coverage of GDPR obligations.
        </p>
      </div>
      <DocumentChecklist />
    </div>
  );
}
