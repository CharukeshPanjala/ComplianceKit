import { ButtonHTMLAttributes } from "react";

// ── Styles ─────────────────────────────────────────────────

const styles = {
  base: "inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
  variants: {
    primary: "px-6 py-2 bg-navy text-white hover:bg-navy-dark",
    secondary: "px-4 py-2 border border-gray-300 text-gray-600 hover:bg-gray-50",
    success: "px-6 py-2 bg-amber-500 text-white hover:bg-amber-600",
  },
  spinner: "animate-spin -ml-1 mr-2 h-4 w-4 text-white",
};

// ── Types ──────────────────────────────────────────────────

type Variant = "primary" | "secondary" | "success";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  loading?: boolean;
  loadingText?: string;
}

// ── Component ─────────────────────────────────────────────

export function Button({
  variant = "primary",
  loading = false,
  loadingText,
  children,
  disabled,
  className = "",
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={`${styles.base} ${styles.variants[variant]} ${className}`}
      {...props}
    >
      {loading ? (
        <>
          <svg
            className={styles.spinner}
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          {loadingText ?? children}
        </>
      ) : (
        children
      )}
    </button>
  );
}
