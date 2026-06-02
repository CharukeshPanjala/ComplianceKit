"use client";

import { Toaster, toast } from "sonner";

// ── Styles ────────────────────────────────────────────────

const styles = {
  toast: "font-sans text-sm",
  success: "!bg-white !border-green-200 !text-gray-900",
  error: "!bg-white !border-red-200 !text-gray-900",
  warning: "!bg-white !border-amber-200 !text-gray-900",
};

// ── Provider ──────────────────────────────────────────────

export const ToastProvider = () => (
  <Toaster
    position="bottom-right"
    toastOptions={{
      duration: 4000,
      classNames: {
        toast: styles.toast,
        success: styles.success,
        error: styles.error,
        warning: styles.warning,
      },
    }}
  />
);

// ── Helpers ───────────────────────────────────────────────

export const showToast = {
  success: (message: string) => toast.success(message),
  error: (message: string) => toast.error(message),
  warning: (message: string) => toast.warning(message),
  info: (message: string) => toast.info(message),
  loading: (message: string) => toast.loading(message),
  promise: <T,>(
    promise: Promise<T>,
    messages: { loading: string; success: string; error: string }
  ) => toast.promise(promise, messages),
};
