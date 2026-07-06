"use client";

// ── Types ──────────────────────────────────────────────────
interface QuestionOption {
  value: string;
  label: string;
}

interface Question {
  id: string;
  badge: string;
  articleRef: string;
  title: string;
  description: string;
  options: QuestionOption[];
}

interface TrackQuestionProps {
  question: Question;
  currentAnswer: string | null;
  onAnswer: (value: string) => void;
}

// ── Styles ──────────────────────────────────────────────────
const styles = {
  card: "bg-white rounded-xl shadow-md p-6",
  badge: "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-700 border border-amber-200 mb-3",
  articleRef: "text-xs text-[#94A3B8] font-mono mb-2",
  title: "text-lg font-bold text-[#0F172A] mb-2",
  description: "text-sm text-[#64748B] mb-5 leading-relaxed",
  optionsGrid: "space-y-3",
  option: {
    base: "flex items-center gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all hover:border-amber-300 hover:bg-amber-50/30",
    selected: "border-[#D97706] bg-amber-50",
    unselected: "border-gray-200 bg-white",
  },
  radioOuter: {
    base: "w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all",
    selected: "border-[#D97706] bg-[#D97706]",
    unselected: "border-gray-300",
  },
  radioDot: "w-2 h-2 rounded-full bg-white",
  optionLabel: "text-sm font-medium text-[#334155] flex-1",
  checkIcon: "w-5 h-5 text-[#D97706] flex-shrink-0",
};

// ── Sub-components ───────────────────────────────────────────
const CheckIcon = () => (
  <svg className={styles.checkIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
  </svg>
);

// ── Component ───────────────────────────────────────────────
export const TrackQuestion = ({ question, currentAnswer, onAnswer }: TrackQuestionProps) => {
  // ── Render helpers ───────────────────────────────────────
  const renderOption = (option: QuestionOption) => {
    const isSelected = currentAnswer === option.value;
    const handleSelect = () => onAnswer(option.value);

    return (
      <div
        key={option.value}
        onClick={handleSelect}
        className={`${styles.option.base} ${isSelected ? styles.option.selected : styles.option.unselected}`}
      >
        <div className={`${styles.radioOuter.base} ${isSelected ? styles.radioOuter.selected : styles.radioOuter.unselected}`}>
          {isSelected && <div className={styles.radioDot} />}
        </div>
        <span className={styles.optionLabel}>{option.label}</span>
        {isSelected && <CheckIcon />}
      </div>
    );
  };

  // ── Render ───────────────────────────────────────────────
  return (
    <div className={styles.card}>
      <div className={styles.badge}>{question.badge}</div>
      <div className={styles.articleRef}>{question.articleRef}</div>
      <h3 className={styles.title}>{question.title}</h3>
      <p className={styles.description}>{question.description}</p>
      <div className={styles.optionsGrid}>{question.options.map(renderOption)}</div>
    </div>
  );
};
