import { StepSidebar } from "@/app/(onboarding)/_components/StepSidebar";

// ── Styles ─────────────────────────────────────────────────

const styles = {
  shell: "h-screen flex overflow-hidden",
  main: "flex-1 flex flex-col bg-warm-white overflow-hidden",
  mobileHeader: "md:hidden bg-navy px-4 py-3 flex items-center gap-2.5",
  mobileIcon: "w-7 h-7 bg-amber-500 rounded-lg flex items-center justify-center flex-shrink-0",
  mobileIconText: "text-white font-bold text-xs",
  mobileName: "text-white font-semibold text-sm",
  content: "flex-1 overflow-y-auto p-4 md:p-10",
  inner: "w-full max-w-4xl mx-auto min-h-full flex flex-col justify-center py-6",
};

// ── Layout ─────────────────────────────────────────────────

export default function OnboardingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className={styles.shell}>
      <StepSidebar />

      <div className={styles.main}>
        {/* Mobile header — hidden on md+ */}
        <div className={styles.mobileHeader}>
          <div className={styles.mobileIcon}>
            <span className={styles.mobileIconText}>C</span>
          </div>
          <span className={styles.mobileName}>ComplianceKit</span>
        </div>

        {/* Form area */}
        <div className={styles.content}>
          <div className={styles.inner}>{children}</div>
        </div>
      </div>
    </div>
  );
}
