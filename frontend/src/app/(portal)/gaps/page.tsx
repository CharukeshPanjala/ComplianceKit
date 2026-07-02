import { TopBar } from "../_components/TopBar";
import { GapsPageContent } from "./_components/GapsPageContent";

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "flex flex-col h-full",
};

// ── Page ──────────────────────────────────────────────────

export default function GapsPage() {
  return (
    <div className={styles.wrapper}>
      <TopBar title="Gap Analysis" subtitle="Compliance gaps across every regulation" />
      <GapsPageContent />
    </div>
  );
}
