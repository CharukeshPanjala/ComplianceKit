import { redirect } from "next/navigation";
import { apiFetch } from "@/lib/api";
import Step1Form from "@/app/(onboarding)/_components/Step1Form";
import Step2Form from "@/app/(onboarding)/_components/Step2Form";
import Step3Form from "@/app/(onboarding)/_components/Step3Form";
import Step4Form from "@/app/(onboarding)/_components/Step4Form";
import Step5Form from "@/app/(onboarding)/_components/Step5Form";
import type { Profile } from "@/types/profile";

// ── Constants ─────────────────────────────────────────────

const TOTAL_STEPS = 5;

const STEP_SUBTITLES: Record<number, string> = {
  1: "Tell us about your company",
  2: "Where do you operate and what data do you process?",
  3: "What tools and technologies do you use?",
  4: "How is your infrastructure set up?",
  5: "Almost done — compliance contacts",
};

const styles = {
  card: "bg-white rounded-2xl shadow-sm border border-gray-100 p-8 md:p-10",
  progressBar: "flex gap-1.5 mb-6",
  progressSegment: {
    base: "h-1 flex-1 rounded-full transition-all duration-500",
    done: "bg-amber-500",
    pending: "bg-amber-500/20",
  },
  stepLabel: "text-xs font-semibold text-amber-500 uppercase tracking-widest mb-1.5",
  heading: "text-2xl font-bold text-navy leading-snug",
  headerWrapper: "mb-8",
};
// ── Step content router ────────────────────────────────────

function StepContent({ step, profile }: { step: number; profile: Profile | null }) {
  switch (step) {
    case 1:
      return <Step1Form initialData={profile} />;
    case 2:
      return <Step2Form initialData={profile} />;
    case 3:
      return <Step3Form initialData={profile} />;
    case 4:
      return <Step4Form initialData={profile} />;
    case 5:
      return <Step5Form initialData={profile} />;
    default:
      return null;
  }
}

// ── Page ──────────────────────────────────────────────────

export default async function OnboardingStepPage({
  params,
}: {
  params: Promise<{ step: string }>;
}) {
  const { step: stepParam } = await params;
  const step = Number(stepParam);

  if (!step || step < 1 || step > TOTAL_STEPS) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    redirect("/onboarding/step/1" as any);
  }

  let profile: Profile | null = null;
  try {
    const res = await apiFetch("/api/v1/profile");
    if (res.ok) profile = await res.json();
  } catch {}

  return (
    <div className={styles.card}>
      <div className={styles.progressBar}>
        {Array.from({ length: TOTAL_STEPS }, (_, i) => i + 1).map((s) => (
          <div
            key={s}
            className={`${styles.progressSegment.base} ${
              s <= step ? styles.progressSegment.done : styles.progressSegment.pending
            }`}
          />
        ))}
      </div>

      <div className={styles.headerWrapper}>
        <p className={styles.stepLabel}>
          Step {step} of {TOTAL_STEPS}
        </p>
        <h1 className={styles.heading}>{STEP_SUBTITLES[step]}</h1>
      </div>

      <StepContent step={step} profile={profile} />
    </div>
  );
}
