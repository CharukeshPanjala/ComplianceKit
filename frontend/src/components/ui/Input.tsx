import { InputHTMLAttributes, forwardRef } from "react";

// ── Styles ─────────────────────────────────────────────────

const styles = {
  base: "w-full px-3 py-2 border rounded-lg text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-navy focus:border-transparent",
  default: "border-gray-300 text-gray-900 placeholder-gray-400",
  error: "border-red-400 text-gray-900 placeholder-gray-400",
};

// ── Types ──────────────────────────────────────────────────

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  hasError?: boolean;
}

// ── Component ─────────────────────────────────────────────

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ hasError = false, className = "", ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={`${styles.base} ${hasError ? styles.error : styles.default} ${className}`}
        {...props}
      />
    );
  }
);

Input.displayName = "Input";
