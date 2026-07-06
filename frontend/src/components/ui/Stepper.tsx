// ── Types ──────────────────────────────────────────────
interface StepperProps {
  steps: Array<{ label: string }>;
  currentStep: number;
}

// ── Styles ─────────────────────────────────────────────
const styles = {
  wrapper: "flex items-center w-full",
  stepWrapper: "flex items-center",
  stepContent: "flex flex-col items-center",
  circleBase: "w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0",
  circleDone: "bg-green-500 text-white",
  circleCurrent: "bg-[#D97706] text-white",
  circlePending: "bg-gray-200 text-gray-500",
  labelBase: "text-xs mt-1 font-medium",
  labelDone: "text-green-600",
  labelCurrent: "text-[#D97706] font-bold",
  labelPending: "text-gray-400",
  connectorBase: "flex-1 h-0.5 mx-2",
  connectorDone: "bg-green-400",
  connectorPending: "bg-gray-200",
};

// ── Sub-components ─────────────────────────────────────
const CheckIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
  </svg>
);

// ── Component ──────────────────────────────────────────
export const Stepper = ({ steps, currentStep }: StepperProps) => (
  <div className={styles.wrapper}>
    {steps.map((step, index) => {
      const stepNumber = index + 1;
      const isDone = stepNumber < currentStep;
      const isCurrent = stepNumber === currentStep;
      const isLast = index === steps.length - 1;

      return (
        <div key={step.label} className={`${styles.stepWrapper} ${!isLast ? "flex-1" : ""}`}>
          <div className={styles.stepContent}>
            <div
              className={`${styles.circleBase} ${
                isDone ? styles.circleDone : isCurrent ? styles.circleCurrent : styles.circlePending
              }`}
            >
              {isDone ? <CheckIcon /> : stepNumber}
            </div>
            <span
              className={`${styles.labelBase} ${
                isDone ? styles.labelDone : isCurrent ? styles.labelCurrent : styles.labelPending
              }`}
            >
              {step.label}
            </span>
          </div>
          {!isLast && (
            <div className={`${styles.connectorBase} ${isDone ? styles.connectorDone : styles.connectorPending}`} />
          )}
        </div>
      );
    })}
  </div>
);
