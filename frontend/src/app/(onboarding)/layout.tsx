import { OnboardingTopBar } from "./_components/OnboardingTopBar";
import { LiveRulesPanelWrapper } from "./_components/LiveRulesPanelWrapper";

// ── Styles ─────────────────────────────────────────────
const styles = {
  shell: "min-h-screen bg-white flex flex-col",
  body: "flex flex-1 overflow-hidden",
  content: "flex-1 overflow-y-auto",
  panel: "hidden lg:flex flex-shrink-0",
};

export default function OnboardingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className={styles.shell}>
      <OnboardingTopBar />
      <div className={styles.body}>
        <div className={styles.content}>{children}</div>
        <div className={styles.panel}>
          <LiveRulesPanelWrapper />
        </div>
      </div>
    </div>
  );
}
