// ── Styles ────────────────────────────────────────────────

const styles = {
  base: "animate-pulse rounded-lg bg-gray-100",
  card: "bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-4",
  cardHeader: "flex items-center justify-between",
  cardGauge: "flex justify-center py-4",
  cardLines: "space-y-2",
  gapRow: "bg-white rounded-xl border border-gray-100 p-4 flex items-center gap-4",
  gapLines: "flex-1 space-y-2",
  grid: "grid grid-cols-1 md:grid-cols-3 gap-6",
  stack: "space-y-8",
  list: "space-y-3",
};

// ── Base ──────────────────────────────────────────────────

const Skeleton = ({ className = "" }: { className?: string }) => (
  <div className={`${styles.base} ${className}`} />
);

// ── Regulation card skeleton ──────────────────────────────

export const RegulationCardSkeleton = () => (
  <div className={styles.card}>
    <div className={styles.cardHeader}>
      <Skeleton className="h-5 w-24" />
      <Skeleton className="h-6 w-16 rounded-full" />
    </div>
    <div className={styles.cardGauge}>
      <Skeleton className="h-32 w-32 rounded-full" />
    </div>
    <div className={styles.cardLines}>
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-3/4" />
    </div>
    <Skeleton className="h-9 w-full rounded-lg" />
  </div>
);

// ── Gap list skeleton ─────────────────────────────────────

export const GapListSkeleton = () => (
  <div className={styles.list}>
    {Array.from({ length: 5 }).map((_, i) => (
      <div key={i} className={styles.gapRow}>
        <Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
        <div className={styles.gapLines}>
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-3 w-32" />
        </div>
        <Skeleton className="h-6 w-20 rounded-full" />
      </div>
    ))}
  </div>
);

// ── Dashboard skeleton ────────────────────────────────────

export const DashboardSkeleton = () => (
  <div className={styles.stack}>
    <div className={styles.grid}>
      <RegulationCardSkeleton />
      <RegulationCardSkeleton />
      <RegulationCardSkeleton />
    </div>
    <GapListSkeleton />
  </div>
);
