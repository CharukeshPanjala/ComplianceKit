"use client";

import { useState } from "react";
import { Modal } from "@/components/ui/Modal";
import { GapResolveButton } from "./GapResolveButton";
import { useGaps } from "@/lib/hooks/useGaps";
import type { Gap } from "@/types/assessment";

// ── Constants ─────────────────────────────────────────────

const SEVERITY_CONFIG = {
  critical: { text: "text-red-700", bg: "bg-red-50", label: "Critical" },
  high: { text: "text-orange-700", bg: "bg-orange-50", label: "High" },
  medium: { text: "text-amber-700", bg: "bg-amber-50", label: "Medium" },
  low: { text: "text-blue-700", bg: "bg-blue-50", label: "Low" },
};

const STATUS_CONFIG = {
  not_met: { text: "text-red-600", bg: "bg-red-50", label: "Not Met" },
  partial: { text: "text-amber-600", bg: "bg-amber-50", label: "Partial" },
  unknown: { text: "text-gray-500", bg: "bg-gray-100", label: "Unknown" },
  met: { text: "text-green-600", bg: "bg-green-50", label: "Met" },
  not_applicable: { text: "text-gray-400", bg: "bg-gray-50", label: "N/A" },
};

const FINE_EXPOSURE = {
  tier_2: "Up to €20M or 4% of global annual turnover",
  tier_1: "Up to €10M or 2% of global annual turnover",
};

// ── Types ─────────────────────────────────────────────────

interface GapDetailModalProps {
  gapId: string | null;
  assessmentId: string;
  isOpen: boolean;
  onClose: () => void;
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  badges: "flex flex-wrap gap-2 mb-4",
  badge: "text-xs font-medium px-2.5 py-1 rounded-full",
  section: "mb-5",
  sectionTitle: "text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2",
  chapter: "text-sm text-gray-600",
  plainEnglish:
    "text-sm text-gray-700 leading-relaxed bg-blue-50 border border-blue-100 rounded-xl p-4",
  fineBox: "text-sm text-red-700 bg-red-50 border border-red-100 rounded-xl p-4",
  fineLabel: "font-semibold text-xs uppercase tracking-wide text-red-500 mb-1",
  steps: "space-y-2",
  step: "flex gap-3 text-sm text-gray-700",
  stepNum:
    "w-5 h-5 rounded-full bg-navy text-white text-xs flex items-center justify-center flex-shrink-0 mt-0.5",
  evidenceBox: "bg-gray-50 rounded-xl p-3 text-xs text-gray-500 font-mono break-all",
  resolveSection: "border-t border-gray-100 pt-4 mt-4",
  loadingWrapper: "py-8 text-center text-sm text-gray-400",
  notFoundWrapper: "py-8 text-center text-sm text-gray-400",
};

// ── Component ─────────────────────────────────────────────

export const GapDetailModal = ({ gapId, assessmentId, isOpen, onClose }: GapDetailModalProps) => {
  const [notes, setNotes] = useState("");

  const { data, isLoading } = useGaps(isOpen ? assessmentId : null);

  const gap: Gap | null = data?.gaps.find((g) => g.gap_id === gapId) ?? null;

  const severity = SEVERITY_CONFIG[gap?.severity ?? "medium"] ?? SEVERITY_CONFIG.medium;
  const status = STATUS_CONFIG[gap?.status ?? "unknown"] ?? STATUS_CONFIG.unknown;
  const fineText = gap?.fine_tier ? FINE_EXPOSURE[gap.fine_tier] : null;
  const steps = gap?.remediation_steps?.steps ?? [];

  // ── Render helpers ────────────────────────────────────

  const renderLoading = () => <div className={styles.loadingWrapper}>Loading gap details...</div>;

  const renderNotFound = () => <div className={styles.notFoundWrapper}>Gap not found.</div>;

  const renderBadges = () => (
    <div className={styles.badges}>
      <span className={`${styles.badge} ${severity.bg} ${severity.text}`}>
        {severity.label} Severity
      </span>
      <span className={`${styles.badge} ${status.bg} ${status.text}`}>{status.label}</span>
      {gap?.chapter && (
        <span className={`${styles.badge} bg-gray-100 text-gray-600`}>{gap.chapter}</span>
      )}
    </div>
  );

  const renderPlainEnglish = () => {
    if (!gap?.plain_english) return null;
    return (
      <div className={styles.section}>
        <p className={styles.sectionTitle}>Plain English</p>
        <p className={styles.plainEnglish}>{gap.plain_english}</p>
      </div>
    );
  };

  const renderFineExposure = () => {
    if (!fineText) return null;
    return (
      <div className={styles.section}>
        <div className={styles.fineBox}>
          <p className={styles.fineLabel}>⚠ Fine Exposure</p>
          <p>{fineText}</p>
        </div>
      </div>
    );
  };

  const renderSteps = () => {
    if (steps.length === 0) return null;
    return (
      <div className={styles.section}>
        <p className={styles.sectionTitle}>Remediation Steps</p>
        <div className={styles.steps}>
          {steps.map((step, i) => (
            <div key={i} className={styles.step}>
              <div className={styles.stepNum}>{i + 1}</div>
              <p>{step}</p>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderEvidence = () => {
    if (!gap?.evidence || Object.keys(gap.evidence).length === 0) return null;
    return (
      <div className={styles.section}>
        <p className={styles.sectionTitle}>Evidence Used</p>
        <div className={styles.evidenceBox}>{JSON.stringify(gap.evidence, null, 2)}</div>
      </div>
    );
  };

  const renderResolve = () => {
    if (!gap) return null;
    return (
      <div className={styles.resolveSection}>
        <GapResolveButton
          gap={gap}
          assessmentId={assessmentId}
          notes={notes}
          onNotesChange={setNotes}
        />
      </div>
    );
  };

  const renderContent = () => {
    if (isLoading) return renderLoading();
    if (!gap) return renderNotFound();
    return (
      <>
        {renderBadges()}
        {renderPlainEnglish()}
        {renderFineExposure()}
        {renderSteps()}
        {renderEvidence()}
        {renderResolve()}
      </>
    );
  };

  // ── Render ────────────────────────────────────────────

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={gap?.title ?? gap?.article ?? "Gap Details"}
      size="lg"
    >
      {renderContent()}
    </Modal>
  );
};
