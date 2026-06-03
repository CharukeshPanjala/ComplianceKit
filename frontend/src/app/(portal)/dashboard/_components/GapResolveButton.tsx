"use client";

import { useUpdateGap } from "@/lib/hooks/useUpdateGap";
import { showToast } from "@/components/ui/Toast";
import type { Gap } from "@/types/assessment";

// ── Types ─────────────────────────────────────────────────

interface GapResolveButtonProps {
  gap: Gap;
  assessmentId: string;
  notes: string;
  onNotesChange: (notes: string) => void;
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "space-y-3",
  notesLabel: "text-xs font-semibold text-gray-400 uppercase tracking-wider",
  notesInput:
    "w-full text-sm border border-gray-200 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-navy/20 focus:border-navy resize-none text-gray-700 placeholder-gray-400",
  actions: "flex gap-2",
  resolveBtn:
    "flex-1 py-2.5 text-sm font-medium rounded-xl transition-colors bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed",
  unresolveBtn:
    "flex-1 py-2.5 text-sm font-medium rounded-xl transition-colors border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed",
  resolvedBanner:
    "flex items-center gap-2 text-sm text-green-700 bg-green-50 border border-green-200 rounded-xl px-4 py-3",
  resolvedIcon: "w-4 h-4 text-green-600 flex-shrink-0",
  resolvedDate: "text-xs text-green-600 ml-auto",
};

// ── Sub-components ────────────────────────────────────────

const CheckIcon = () => (
  <svg className={styles.resolvedIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

// ── Component ─────────────────────────────────────────────

export const GapResolveButton = ({
  gap,
  assessmentId,
  notes,
  onNotesChange,
}: GapResolveButtonProps) => {
  const { mutate: updateGap, isPending } = useUpdateGap(assessmentId);

  // ── Handlers ─────────────────────────────────────────

  const handleResolve = () => {
    updateGap(
      { gapId: gap.gap_id, body: { resolved: true, notes: notes || undefined } },
      {
        onSuccess: () => showToast.success("Gap marked as resolved"),
        onError: () => showToast.error("Failed to resolve gap. Please try again."),
      }
    );
  };

  const handleUnresolve = () => {
    updateGap(
      { gapId: gap.gap_id, body: { resolved: false } },
      {
        onSuccess: () => showToast.success("Gap marked as unresolved"),
        onError: () => showToast.error("Failed to update gap. Please try again."),
      }
    );
  };

  // ── Render helpers ────────────────────────────────────

  const renderResolvedBanner = () => {
    const resolvedDate = gap.resolved_at ? new Date(gap.resolved_at).toLocaleDateString() : "";

    return (
      <div className={styles.resolvedBanner}>
        <CheckIcon />
        <span>Marked as resolved</span>
        {resolvedDate && <span className={styles.resolvedDate}>{resolvedDate}</span>}
      </div>
    );
  };

  const renderNotes = () => (
    <div className="space-y-1.5">
      <p className={styles.notesLabel}>Notes</p>
      <textarea
        rows={3}
        value={notes}
        onChange={(e) => onNotesChange(e.target.value)}
        placeholder="Add context or evidence for resolving this gap..."
        className={styles.notesInput}
      />
    </div>
  );

  const renderActions = () => (
    <div className={styles.actions}>
      {!gap.resolved ? (
        <button onClick={handleResolve} disabled={isPending} className={styles.resolveBtn}>
          {isPending ? "Saving..." : "✓ Mark as Resolved"}
        </button>
      ) : (
        <button onClick={handleUnresolve} disabled={isPending} className={styles.unresolveBtn}>
          {isPending ? "Saving..." : "Undo Resolution"}
        </button>
      )}
    </div>
  );

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.wrapper}>
      {gap.resolved && renderResolvedBanner()}
      {!gap.resolved && renderNotes()}
      {renderActions()}
    </div>
  );
};
