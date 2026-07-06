import { GapsPageContent } from "./_components/GapsPageContent";

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "min-h-screen bg-[#F8FAFC]",
  inner: "max-w-7xl mx-auto px-6 py-8 space-y-6",
  breadcrumb: "text-xs text-[#94A3B8]",
  title: "text-2xl font-bold text-[#0F172A]",
};

// ── Page ──────────────────────────────────────────────────

export default function GapsPage() {
  return (
    <div className={styles.wrapper}>
      <div className={styles.inner}>
        <nav className={styles.breadcrumb}>Portal / Gap Analysis</nav>
        <h1 className={styles.title}>Gap Analysis</h1>
        <GapsPageContent />
      </div>
    </div>
  );
}
