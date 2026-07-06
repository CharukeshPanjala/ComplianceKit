const styles = {
  wrapper: "p-6 lg:p-8 max-w-7xl mx-auto animate-pulse",
  titleBar: "flex items-center justify-between mb-6",
  titleBlock: "space-y-2",
  titleLine: "h-7 w-48 bg-gray-200 rounded-lg",
  subtitleLine: "h-4 w-64 bg-gray-100 rounded-lg",
  btnPlaceholder: "h-9 w-36 bg-gray-200 rounded-lg",
  statsRow: "grid grid-cols-2 md:grid-cols-4 gap-4 mb-6",
  statCard: "h-24 bg-gray-100 rounded-xl",
  tableHeader: "h-10 bg-gray-100 rounded-lg mb-2",
  tableRow: "h-14 bg-gray-50 rounded-lg mb-2",
};

export const PageSkeleton = () => (
  <div className={styles.wrapper}>
    <div className={styles.titleBar}>
      <div className={styles.titleBlock}>
        <div className={styles.titleLine} />
        <div className={styles.subtitleLine} />
      </div>
      <div className={styles.btnPlaceholder} />
    </div>
    <div className={styles.statsRow}>
      {[0, 1, 2, 3].map((i) => (
        <div key={i} className={styles.statCard} />
      ))}
    </div>
    <div className={styles.tableHeader} />
    {[0, 1, 2, 3, 4, 5].map((i) => (
      <div key={i} className={styles.tableRow} />
    ))}
  </div>
);
