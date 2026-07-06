// WHAT: ROPA empty state | CHANGE: new file | WHY: COM-173 — shown when no entries exist
"use client";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  wrapper: "flex flex-col items-center justify-center py-24 px-6 text-center",
  icon: "w-16 h-16 text-gray-200 mx-auto mb-6",
  title: "text-xl font-bold text-[#0F172A] mb-2",
  subtitle: "text-sm text-[#64748B] max-w-md mb-8",
  btn: "px-6 py-3 bg-[#D97706] text-white text-sm font-semibold rounded-xl hover:bg-[#B45309] transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
  spinner: "w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin",
};

// ── Sub-components ────────────────────────────────────────────────────────────

const BookIcon = () => (
  <svg className={styles.icon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
      d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
  </svg>
);

// ── Component ─────────────────────────────────────────────────────────────────

interface RopaEmptyStateProps {
  onGenerate: () => void;
  isGenerating: boolean;
}

export const RopaEmptyState = ({ onGenerate, isGenerating }: RopaEmptyStateProps) => (
  <div className={styles.wrapper}>
    <BookIcon />
    <h2 className={styles.title}>No processing activities yet</h2>
    <p className={styles.subtitle}>
      Auto-generate your GDPR Article 30 register from your company profile, then edit and activate each entry.
    </p>
    <button onClick={onGenerate} disabled={isGenerating} className={styles.btn}>
      {isGenerating ? (
        <span className="flex items-center gap-2">
          <span className={styles.spinner} /> Generating…
        </span>
      ) : (
        "Generate from profile"
      )}
    </button>
  </div>
);
