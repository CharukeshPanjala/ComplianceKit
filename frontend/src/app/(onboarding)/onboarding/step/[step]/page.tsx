import { redirect } from "next/navigation";
import { apiFetch } from "@/lib/api";
import Step1Form from "@/app/(onboarding)/_components/Step1Form";
import Step2Form from "@/app/(onboarding)/_components/Step2Form";
import Step3Form from "@/app/(onboarding)/_components/Step3Form";
import Step4Form from "@/app/(onboarding)/_components/Step4Form";
import Step5Form from "@/app/(onboarding)/_components/Step5Form";
import type { Profile } from "@/types/profile";

const TOTAL_STEPS = 5;

const STEP_TITLES: Record<number, string> = {
  1: "Company Basics",
  2: "Jurisdiction & Data",
  3: "Tech Stack",
  4: "Infrastructure",
  5: "Regulations & Contacts",
};

const STEP_SUBTITLES: Record<number, string> = {
  1: "Tell us about your company",
  2: "Where do you operate and what data do you process?",
  3: "What tools and technologies do you use?",
  4: "How is your infrastructure set up?",
  5: "Almost done — compliance contacts",
};

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
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-gray-500 mb-2">
          <span>
            Step {step} of {TOTAL_STEPS}
          </span>
          <span className="font-medium text-gray-700">{STEP_TITLES[step]}</span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-1.5">
          <div
            className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
            style={{ width: `${(step / TOTAL_STEPS) * 100}%` }}
          />
        </div>
      </div>

      {/* Step header */}
      <div className="mb-8">
        <h1 className="text-xl font-semibold text-gray-900">{STEP_SUBTITLES[step]}</h1>
      </div>

      {/* Step form */}
      <StepContent step={step} profile={profile} />
    </div>
  );
}
