// WHAT: /policies portal page | CHANGE: new file | WHY: COM-176 — policy library + generate-from-gap entrypoint
"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { usePoliciesList } from "@/lib/hooks/usePolicies";
import { PolicyLibrary } from "./_components/PolicyLibrary";
import { GeneratePolicyModal } from "./_components/GeneratePolicyModal";
import type { RegulationName } from "@/types/assessment";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  page: "p-6 max-w-7xl mx-auto space-y-6",
  header: "flex items-center justify-between",
  title: "text-xl font-bold text-gray-900",
  subtitle: "text-sm text-gray-400 mt-0.5",
  generateBtn: "px-4 py-2 bg-[#0F2044] text-white text-sm font-semibold rounded-xl hover:bg-[#1a3366] transition-colors",
  skeleton: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 animate-pulse",
  skCard: "h-28 bg-gray-100 rounded-2xl",
  error: "text-sm text-red-500 py-8 text-center",
};

// ── Content ──────────────────────────────────────────────────────────────────

const PoliciesContent = () => {
  const { data, isLoading, isError } = usePoliciesList();
  const searchParams = useSearchParams();
  const [isGenerateOpen, setIsGenerateOpen] = useState(false);

  const initialGapId = searchParams.get("gap_id");
  const initialRegulation = searchParams.get("regulation") as RegulationName | null;

  // ── Effects ───────────────────────────────────────────

  useEffect(() => {
    if (initialGapId) setIsGenerateOpen(true);
  }, [initialGapId]);

  // ── Handlers ──────────────────────────────────────────

  const handleOpenGenerate = () => setIsGenerateOpen(true);
  const handleCloseGenerate = () => setIsGenerateOpen(false);

  // ── Render helpers ────────────────────────────────────

  const renderList = () => {
    if (isLoading) {
      return (
        <div className={styles.skeleton}>
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className={styles.skCard} />
          ))}
        </div>
      );
    }
    if (isError) return <p className={styles.error}>Failed to load policies. Please try again.</p>;
    return <PolicyLibrary policies={data?.policies ?? []} onGenerateClick={handleOpenGenerate} />;
  };

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Policy Library</h1>
          <p className={styles.subtitle}>Generated compliance documents, drafted from your assessment gaps</p>
        </div>
        <button className={styles.generateBtn} onClick={handleOpenGenerate}>
          Generate Policy
        </button>
      </div>
      {renderList()}
      <GeneratePolicyModal
        isOpen={isGenerateOpen}
        onClose={handleCloseGenerate}
        initialGapId={initialGapId}
        initialRegulation={initialRegulation}
      />
    </div>
  );
};

// ── Page ─────────────────────────────────────────────────────────────────────

export default function PoliciesPage() {
  return (
    <Suspense fallback={null}>
      <PoliciesContent />
    </Suspense>
  );
}
