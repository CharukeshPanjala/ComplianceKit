"use client";

import { useState } from "react";

// ── Types ──────────────────────────────────────────────────
type RegulationId = "gdpr" | "nis2" | "eu_ai_act";

interface RegulationConfig {
  id: RegulationId;
  label: string;
  subtitle: string;
  fineLabel: string;
  chips: string[];
  accentClass: string;
  iconPath: string;
}

interface Step2RegulationPickerProps {
  onContinue: (selectedRegulations: RegulationId[]) => void;
  onBack: () => void;
}

// ── Constants ───────────────────────────────────────────────
const REGULATIONS: RegulationConfig[] = [
  {
    id: "gdpr",
    label: "GDPR",
    subtitle: "General Data Protection Regulation",
    fineLabel: "Up to €20M or 4% turnover",
    chips: ["Personal Data", "Privacy Rights", "Data Processing"],
    accentClass: "border-purple-500 bg-purple-50",
    iconPath:
      "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
  },
  {
    id: "nis2",
    label: "NIS2 Directive",
    subtitle: "Network & Information Security",
    fineLabel: "Up to €10M or 2% turnover",
    chips: ["Cybersecurity", "Incident Reporting", "Critical Infrastructure"],
    accentClass: "border-cyan-500 bg-cyan-50",
    iconPath:
      "M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z",
  },
  {
    id: "eu_ai_act",
    label: "EU AI Act",
    subtitle: "Artificial Intelligence Act",
    fineLabel: "Up to €35M or 7% turnover",
    chips: ["AI Systems", "High-Risk AI", "Transparency"],
    accentClass: "border-pink-500 bg-pink-50",
    iconPath:
      "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
  },
];

// ── Styles ──────────────────────────────────────────────────
const styles = {
  wrapper: "w-full max-w-4xl mx-auto px-4 py-8",
  warningBox: "bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6 flex gap-3",
  warningIcon: "flex-shrink-0 w-5 h-5 text-amber-600 mt-0.5",
  warningTitle: "text-sm font-semibold text-amber-800 mb-1",
  warningText: "text-sm text-amber-700",
  cardsGrid: "grid grid-cols-1 md:grid-cols-3 gap-4 mb-8",
  card: {
    base: "relative rounded-xl border-2 p-5 cursor-pointer transition-all hover:shadow-md",
    unselected: "border-gray-200 bg-white hover:border-gray-300",
    selected: "border-[#D97706] bg-amber-50",
  },
  checkmark: "absolute top-3 right-3 w-6 h-6 rounded-full bg-[#D97706] text-white flex items-center justify-center",
  checkmarkHidden: "absolute top-3 right-3 w-6 h-6 rounded-full border-2 border-gray-200",
  iconWrapper: "w-10 h-10 rounded-lg flex items-center justify-center mb-3",
  iconGdpr: "bg-purple-100 text-purple-600",
  iconNis2: "bg-cyan-100 text-cyan-600",
  iconAiAct: "bg-pink-100 text-pink-600",
  cardLabel: "font-bold text-[#0F172A] text-base mb-0.5",
  cardSubtitle: "text-xs text-[#64748B] mb-3",
  fineBox: "bg-red-50 border border-red-100 rounded-lg px-2.5 py-1.5 mb-3",
  fineText: "text-xs font-semibold text-red-700",
  chipsRow: "flex flex-wrap gap-1",
  chip: "text-xs px-2 py-0.5 rounded-full border border-gray-200 bg-white text-[#64748B]",
  footer: "flex items-center justify-between",
  continueBtn: "px-6 py-2.5 bg-[#D97706] text-white text-sm font-semibold rounded-lg transition-colors",
  continueBtnEnabled: "hover:bg-[#B45309]",
  continueBtnDisabled: "opacity-50 cursor-not-allowed",
  skipLink: "text-sm text-[#64748B] hover:text-[#334155] transition-colors cursor-pointer",
};

// ── Sub-components ───────────────────────────────────────────
const CheckIcon = () => (
  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
  </svg>
);

const WarnIcon = () => (
  <svg className={styles.warningIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
  </svg>
);

const ICON_COLORS: Record<RegulationId, string> = {
  gdpr: styles.iconGdpr,
  nis2: styles.iconNis2,
  eu_ai_act: styles.iconAiAct,
};

const RegulationCard = ({
  regulation,
  isSelected,
  onToggle,
}: {
  regulation: RegulationConfig;
  isSelected: boolean;
  onToggle: (id: RegulationId) => void;
}) => {
  const handleClick = () => onToggle(regulation.id);

  return (
    <div
      onClick={handleClick}
      className={`${styles.card.base} ${isSelected ? styles.card.selected : styles.card.unselected}`}
    >
      {isSelected ? (
        <div className={styles.checkmark}>
          <CheckIcon />
        </div>
      ) : (
        <div className={styles.checkmarkHidden} />
      )}
      <div className={`${styles.iconWrapper} ${ICON_COLORS[regulation.id]}`}>
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={regulation.iconPath} />
        </svg>
      </div>
      <div className={styles.cardLabel}>{regulation.label}</div>
      <div className={styles.cardSubtitle}>{regulation.subtitle}</div>
      <div className={styles.fineBox}>
        <div className={styles.fineText}>{regulation.fineLabel}</div>
      </div>
      <div className={styles.chipsRow}>
        {regulation.chips.map((chip) => (
          <span key={chip} className={styles.chip}>
            {chip}
          </span>
        ))}
      </div>
    </div>
  );
};

// ── Component ───────────────────────────────────────────────
export const Step2RegulationPicker = ({ onContinue, onBack }: Step2RegulationPickerProps) => {
  // ── State ────────────────────────────────────────────────
  const [selectedRegulations, setSelectedRegulations] = useState<RegulationId[]>([]);

  // ── Handlers ─────────────────────────────────────────────
  const handleToggle = (id: RegulationId) => {
    setSelectedRegulations((prev) =>
      prev.includes(id) ? prev.filter((r) => r !== id) : [...prev, id]
    );
  };

  const handleContinue = () => {
    if (selectedRegulations.length > 0) {
      onContinue(selectedRegulations);
    }
  };

  // ── Render ───────────────────────────────────────────────
  return (
    <div className={styles.wrapper}>
      <div className={styles.warningBox}>
        <WarnIcon />
        <div>
          <div className={styles.warningTitle}>Potential penalty exposure</div>
          <div className={styles.warningText}>
            GDPR: up to €20M. NIS2: up to €10M. EU AI Act: up to €35M. Select all regulations that apply to your organisation.
          </div>
        </div>
      </div>
      <div className={styles.cardsGrid}>
        {REGULATIONS.map((regulation) => (
          <RegulationCard
            key={regulation.id}
            regulation={regulation}
            isSelected={selectedRegulations.includes(regulation.id)}
            onToggle={handleToggle}
          />
        ))}
      </div>
      <div className={styles.footer}>
        <button onClick={onBack} className={styles.skipLink}>
          Skip for now
        </button>
        <button
          onClick={handleContinue}
          disabled={selectedRegulations.length === 0}
          className={`${styles.continueBtn} ${selectedRegulations.length === 0 ? styles.continueBtnDisabled : styles.continueBtnEnabled}`}
        >
          Continue →
        </button>
      </div>
    </div>
  );
};
