// WHAT: /ropa portal page | CHANGE: new file | WHY: COM-173 — ROPA register page
"use client";

import { useRopaList } from "@/lib/hooks/useRopa";
import { RopaTable } from "./_components/RopaTable";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  page: "p-6 max-w-7xl mx-auto",
  skeleton: "animate-pulse space-y-3",
  skRow: "h-10 bg-gray-100 rounded-lg",
  error: "text-sm text-red-500 py-8 text-center",
};

// ── Component ─────────────────────────────────────────────────────────────────

export default function RopaPage() {
  const { data, isLoading, isError } = useRopaList();

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className={styles.skeleton}>
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className={styles.skRow} />
          ))}
        </div>
      );
    }
    if (isError) return <p className={styles.error}>Failed to load ROPA entries. Please try again.</p>;
    return <RopaTable entries={data?.entries ?? []} />;
  };

  return <div className={styles.page}>{renderContent()}</div>;
}
