import { ButtonHTMLAttributes } from "react";

const styles = {
  base: "inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
  primary: "px-6 py-2 bg-blue-600 text-white hover:bg-blue-700",
  secondary: "px-4 py-2 border border-gray-300 text-gray-600 hover:bg-gray-50",
  success: "px-6 py-2 bg-green-600 text-white hover:bg-green-700",
};

type Variant = "primary" | "secondary" | "success";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  loading?: boolean;
  loadingText?: string;
}

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
      className={`${styles.base} ${styles[variant]} ${className}`}
      {...props}
    >
      {loading && loadingText ? loadingText : children}
    </button>
  );
}
