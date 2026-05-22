"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/ui/FormField";
import { SelectCard } from "@/components/ui/SelectCard";
import { CheckboxCard } from "@/components/ui/CheckboxCard";
import { Tooltip } from "@/components/ui/Tooltip";
import { clientApiFetch } from "@/lib/clientApi";
import type { Profile } from "@/types/profile";
import { OtherInput } from "@/components/ui/OtherInput";

// ── Schema ────────────────────────────────────────────────

const schema = z.object({
  primary_jurisdiction: z.string().min(1, "Please select a jurisdiction"),
  data_role: z
    .string()
    .refine((v) => ["controller", "processor", "both"].includes(v), "Please select your data role"),
  number_of_data_subjects: z
    .string()
    .refine(
      (v) => ["under_1k", "under_10k", "under_100k", "over_100k"].includes(v),
      "Please select an approximate count"
    ),
  data_categories_processed: z.array(z.string()).min(1, "Select at least one data category"),
  data_subject_categories: z.array(z.string()).min(1, "Select at least one subject type"),
  processing_purposes: z.array(z.string()).min(1, "Select at least one processing purpose"),
});

type FormData = z.infer<typeof schema>;

// ── Constants ─────────────────────────────────────────────

const JURISDICTION_OPTIONS = [
  { value: "DE", label: "🇩🇪 Germany" },
  { value: "FR", label: "🇫🇷 France" },
  { value: "NL", label: "🇳🇱 Netherlands" },
  { value: "IE", label: "🇮🇪 Ireland" },
  { value: "GB", label: "🇬🇧 United Kingdom" },
  { value: "US", label: "🇺🇸 United States" },
  { value: "CH", label: "🇨🇭 Switzerland" },
  { value: "EU", label: "🇪🇺 Other EU member state" },
];

const DATA_ROLE_OPTIONS = [
  {
    value: "controller",
    label: "Controller",
    description: "You decide why and how personal data is processed",
  },
  {
    value: "processor",
    label: "Processor",
    description: "You process data on behalf of another organisation",
  },
  { value: "both", label: "Both", description: "You act as both controller and processor" },
];

const DATA_SUBJECT_COUNT_OPTIONS = [
  { value: "under_1k", label: "Under 1K" },
  { value: "under_10k", label: "Under 10K" },
  { value: "under_100k", label: "Under 100K" },
  { value: "over_100k", label: "Over 100K" },
];

const DATA_CATEGORY_OPTIONS = [
  { value: "name_contact", label: "Name & Contact Info", special: false },
  { value: "financial", label: "Financial Data", special: false },
  { value: "health", label: "Health Data ⚠️", special: true },
  { value: "biometric", label: "Biometric Data ⚠️", special: true },
  { value: "location", label: "Location Data", special: false },
  { value: "racial_ethnic", label: "Racial / Ethnic ⚠️", special: true },
  { value: "political", label: "Political Opinions ⚠️", special: true },
  { value: "criminal", label: "Criminal Records ⚠️", special: true },
  { value: "other", label: "Other", special: false },
];

const DATA_SUBJECT_OPTIONS = [
  { value: "customers", label: "Customers" },
  { value: "employees", label: "Employees" },
  { value: "minors", label: "Minors ⚠️" },
  { value: "patients", label: "Patients" },
  { value: "website_visitors", label: "Website Visitors" },
  { value: "job_applicants", label: "Job Applicants" },
  { value: "other", label: "Other" },
];

const PROCESSING_PURPOSE_OPTIONS = [
  { value: "service_delivery", label: "Service Delivery" },
  { value: "marketing", label: "Marketing" },
  { value: "analytics", label: "Analytics" },
  { value: "legal_obligation", label: "Legal Obligation" },
  { value: "legitimate_interest", label: "Legitimate Interest" },
  { value: "contract_performance", label: "Contract Performance" },
  { value: "other", label: "Other" },
];

// ── Styles ────────────────────────────────────────────────

const styles = {
  section: "space-y-6",
  pillGroup: "flex flex-wrap gap-2",
  pill: {
    base: "px-4 py-2 text-sm border rounded-full transition-colors",
    active: "border-navy bg-navy/10 text-navy font-medium",
    inactive: "border-gray-300 text-gray-600 hover:border-navy",
  },
  cardGroup: "grid grid-cols-3 gap-2",
  grid: "grid grid-cols-1 sm:grid-cols-2 gap-2",
  labelRow: "flex items-center gap-1.5 mb-2",
  warning: "text-xs text-amber-600 mt-2",
  nav: "flex justify-between mt-8",
};

// ── Props ─────────────────────────────────────────────────

interface Props {
  initialData: Profile | null;
}

// ── Component ─────────────────────────────────────────────

export default function Step2Form({ initialData }: Props) {
  const { getToken } = useAuth();
  const router = useRouter();

  // ── State ────────────────────────────────────────────────

  const [serverError, setServerError] = useState<string | null>(null);
  const [otherCategories, setOtherCategories] = useState<string[]>([]);
  const [otherSubjects, setOtherSubjects] = useState<string[]>([]);
  const [otherPurposes, setOtherPurposes] = useState<string[]>([]);

  // ── Form ─────────────────────────────────────────────────

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      primary_jurisdiction: initialData?.primary_jurisdiction ?? "",
      data_role: initialData?.data_role ?? "",
      number_of_data_subjects: initialData?.number_of_data_subjects ?? "",
      data_categories_processed: initialData?.data_categories_processed ?? [],
      data_subject_categories: initialData?.data_subject_categories ?? [],
      processing_purposes: initialData?.processing_purposes ?? [],
    },
  });

  const dataRole = watch("data_role");
  const subjectCount = watch("number_of_data_subjects");
  const dataCategories = watch("data_categories_processed") ?? [];
  const subjectCategories = watch("data_subject_categories") ?? [];
  const purposes = watch("processing_purposes") ?? [];

  const hasSpecialCategory = dataCategories.some(
    (v) => DATA_CATEGORY_OPTIONS.find((o) => o.value === v)?.special
  );

  // ── Handlers ──────────────────────────────────────────────

  const toggleCategory = (value: string) => {
    if (value === "other" && dataCategories.includes("other")) setOtherCategories([]);
    const current = dataCategories;
    const updated = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value];
    setValue("data_categories_processed", updated, { shouldValidate: true });
  };

  const toggleSubject = (value: string) => {
    if (value === "other" && subjectCategories.includes("other")) setOtherSubjects([]);
    const current = subjectCategories;
    const updated = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value];
    setValue("data_subject_categories", updated, { shouldValidate: true });
  };

  const togglePurpose = (value: string) => {
    if (value === "other" && purposes.includes("other")) setOtherPurposes([]);
    const current = purposes;
    const updated = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value];
    setValue("processing_purposes", updated, { shouldValidate: true });
  };

  // ── Render helpers ────────────────────────────────────────

  const renderJurisdiction = () => (
    <FormField label="Primary jurisdiction" required error={errors.primary_jurisdiction?.message}>
      <select
        {...register("primary_jurisdiction")}
        className={`w-full px-3 py-2 border rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-navy ${
          errors.primary_jurisdiction ? "border-red-400" : "border-gray-300"
        }`}
      >
        <option value="">Select a country / region</option>
        {JURISDICTION_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </FormField>
  );

  const renderDataRole = () => (
    <FormField label="Your data role" required error={errors.data_role?.message}>
      <div className={styles.labelRow}>
        <Tooltip text="A Controller decides why and how data is processed. A Processor handles data on behalf of a Controller. Determines your obligations under GDPR Art. 4 & 28." />
      </div>
      <div className={styles.cardGroup}>
        {DATA_ROLE_OPTIONS.map((opt) => (
          <SelectCard
            key={opt.value}
            label={opt.label}
            description={opt.description}
            selected={dataRole === opt.value}
            onClick={() => setValue("data_role", opt.value, { shouldValidate: true })}
          />
        ))}
      </div>
    </FormField>
  );

  const renderSubjectCount = () => (
    <FormField
      label="Approximate number of data subjects"
      required
      error={errors.number_of_data_subjects?.message}
    >
      <div className={styles.pillGroup}>
        {DATA_SUBJECT_COUNT_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            type="button"
            onClick={() => setValue("number_of_data_subjects", opt.value, { shouldValidate: true })}
            className={`${styles.pill.base} ${
              subjectCount === opt.value ? styles.pill.active : styles.pill.inactive
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </FormField>
  );

  const renderDataCategories = () => (
    <div>
      <div className={styles.labelRow}>
        <span className="text-sm font-medium text-gray-700">
          Data categories processed <span className="text-red-500">*</span>
        </span>
        <Tooltip text="⚠️ marked categories are special category data under GDPR Art. 9 — stricter rules apply." />
      </div>
      <div className={styles.grid}>
        {DATA_CATEGORY_OPTIONS.map((opt) => (
          <CheckboxCard
            key={opt.value}
            label={opt.label}
            checked={dataCategories.includes(opt.value)}
            onChange={() => toggleCategory(opt.value)}
          />
        ))}
      </div>
      <OtherInput
        show={dataCategories.includes("other")}
        values={otherCategories}
        onChange={setOtherCategories}
        placeholder="e.g. Behavioural Data, Device Data..."
      />
      {hasSpecialCategory && (
        <p className={styles.warning}>
          ⚠️ Special category data detected — stricter obligations apply under GDPR Art. 9
        </p>
      )}
      {errors.data_categories_processed && (
        <p className="text-xs text-red-600 mt-1">{errors.data_categories_processed.message}</p>
      )}
    </div>
  );

  const renderSubjectCategories = () => (
    <div>
      <p className="text-sm font-medium text-gray-700 mb-2">
        Data subject categories <span className="text-red-500">*</span>
      </p>
      <div className={styles.grid}>
        {DATA_SUBJECT_OPTIONS.map((opt) => (
          <CheckboxCard
            key={opt.value}
            label={opt.label}
            checked={subjectCategories.includes(opt.value)}
            onChange={() => toggleSubject(opt.value)}
          />
        ))}
      </div>
      <OtherInput
        show={subjectCategories.includes("other")}
        values={otherSubjects}
        onChange={(vals) => {
          setOtherSubjects(vals);
        }}
        placeholder="e.g. Partners, Contractors..."
      />
      {errors.data_subject_categories && (
        <p className="text-xs text-red-600 mt-1">{errors.data_subject_categories.message}</p>
      )}
    </div>
  );

  const renderProcessingPurposes = () => (
    <div>
      <div className={styles.labelRow}>
        <span className="text-sm font-medium text-gray-700">
          Processing purposes <span className="text-red-500">*</span>
        </span>
        <Tooltip text="Legal Obligation means processing is required by law (e.g. tax records). Legitimate Interest requires a balancing test under GDPR Art. 6(1)(f)." />
      </div>
      <div className={styles.grid}>
        {PROCESSING_PURPOSE_OPTIONS.map((opt) => (
          <CheckboxCard
            key={opt.value}
            label={opt.label}
            checked={purposes.includes(opt.value)}
            onChange={() => togglePurpose(opt.value)}
          />
        ))}
      </div>
      <OtherInput
        show={purposes.includes("other")}
        values={otherPurposes}
        onChange={setOtherPurposes}
        placeholder="e.g. Fraud Prevention, Research..."
      />
      {errors.processing_purposes && (
        <p className="text-xs text-red-600 mt-1">{errors.processing_purposes.message}</p>
      )}
    </div>
  );

  const renderNavigation = () => (
    <div className={styles.nav}>
      <Button type="button" variant="secondary" onClick={() => onBack()}>
        ← Back
      </Button>
      <Button type="submit" loading={isSubmitting} loadingText="Saving...">
        Save & Continue →
      </Button>
    </div>
  );

  // ── Submit ─────────────────────────────────────────────────

  const onBack = async () => {
    try {
      const token = await getToken();
      const data = watch();
      await clientApiFetch("/api/v1/profile", token!, {
        method: "PATCH",
        body: JSON.stringify({
          primary_jurisdiction: data.primary_jurisdiction || null,
          data_role: data.data_role || null,
          number_of_data_subjects: data.number_of_data_subjects || null,
          data_categories_processed: [
            ...(data.data_categories_processed ?? []).filter((v) => v !== "other"),
            ...otherCategories,
          ],
          data_subject_categories: [
            ...(data.data_subject_categories ?? []).filter((v) => v !== "other"),
            ...otherSubjects,
          ],
          processing_purposes: [
            ...(data.processing_purposes ?? []).filter((v) => v !== "other"),
            ...otherPurposes,
          ],
        }),
      });
    } catch {}
    router.push("/onboarding/step/1" as any);
  };

  const onSubmit = async (data: FormData) => {
    setServerError(null);
    try {
      const token = await getToken();
      const res = await clientApiFetch("/api/v1/profile", token!, {
        method: "PATCH",
        body: JSON.stringify({
          primary_jurisdiction: data.primary_jurisdiction || null,
          data_role: data.data_role || null,
          number_of_data_subjects: data.number_of_data_subjects || null,
          data_categories_processed: [
            ...(data.data_categories_processed ?? []).filter((v) => v !== "other"),
            ...otherCategories,
          ],
          data_subject_categories: [
            ...(data.data_subject_categories ?? []).filter((v) => v !== "other"),
            ...otherSubjects,
          ],
          processing_purposes: [
            ...(data.processing_purposes ?? []).filter((v) => v !== "other"),
            ...otherPurposes,
          ],
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.detail ?? "Failed to save. Please try again.");
      }

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      router.push("/onboarding/step/3" as any);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Something went wrong.");
    }
  };

  // ── Render ─────────────────────────────────────────────────

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div className={styles.section}>
        {renderJurisdiction()}
        {renderDataRole()}
        {renderSubjectCount()}
        {renderDataCategories()}
        {renderSubjectCategories()}
        {renderProcessingPurposes()}
      </div>
      {serverError && <p className="mt-4 text-sm text-red-600">{serverError}</p>}
      {renderNavigation()}
    </form>
  );
}
