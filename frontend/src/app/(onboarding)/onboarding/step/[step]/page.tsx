import { redirect } from "next/navigation";

const TOTAL_STEPS = 5;

const STEP_TITLES: Record<number, string> = {
  1: "Company Basics",
  2: "Jurisdiction & Data",
  3: "Tech Stack",
  4: "Infrastructure",
  5: "Regulations",
};

export default async function OnboardingStepPage({
  params,
}: {
  params: Promise<{ step: string }>;
}) {
  const { step: stepParam } = await params;
  const step = Number(stepParam);

  if (!step || step < 1 || step > TOTAL_STEPS) {
    // next.js typedRoutes requires a cast for dynamic route redirects
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    redirect("/onboarding/step/1" as any);
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-gray-500 mb-2">
          <span>
            Step {step} of {TOTAL_STEPS}
          </span>
          <span>{STEP_TITLES[step]}</span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(step / TOTAL_STEPS) * 100}%` }}
          />
        </div>
      </div>

      {/* Step content placeholder */}
      <div className="min-h-48 flex items-center justify-center text-gray-400 border-2 border-dashed border-gray-200 rounded-lg">
        {STEP_TITLES[step]} — coming soon
      </div>

      {/* Navigation */}
      <div className="flex justify-between mt-8">
        {step > 1 ? (
          <a
            href={`/onboarding/step/${step - 1}`}
            className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Back
          </a>
        ) : (
          <div />
        )}
        <a
          href={step < TOTAL_STEPS ? `/onboarding/step/${step + 1}` : "/dashboard"}
          className="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700"
        >
          {step < TOTAL_STEPS ? "Next" : "Finish"}
        </a>
      </div>
    </div>
  );
}
