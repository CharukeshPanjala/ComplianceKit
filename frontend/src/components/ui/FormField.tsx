const styles = {
  wrapper: "flex flex-col gap-1",
  label: "text-sm font-medium text-gray-700",
  required: "text-red-500 ml-0.5",
  hint: "text-xs text-gray-400 font-normal",
  error: "text-xs text-red-600 mt-0.5",
};

interface FormFieldProps {
  label: string;
  required?: boolean;
  hint?: string;
  error?: string;
  children: React.ReactNode;
}

export function FormField({ label, required = false, hint, error, children }: FormFieldProps) {
  return (
    <div className={styles.wrapper}>
      <label className={styles.label}>
        {label}
        {required && <span className={styles.required}>*</span>}
        {hint && <span className={styles.hint}> ({hint})</span>}
      </label>
      {children}
      {error && <p className={styles.error}>{error}</p>}
    </div>
  );
}
