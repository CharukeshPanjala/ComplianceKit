"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/ui/FormField";
import { SelectCard } from "@/components/ui/SelectCard";
import { CheckboxCard } from "@/components/ui/CheckboxCard";
import { Tooltip } from "@/components/ui/Tooltip";
import { clientApiFetch } from "@/lib/clientApi";
import type { Profile } from "@/types/profile";

const schema = z.object({
  primary_jurisdiction: z.string().optional(),
  data_role: z.enum(["controller", "processor", "both"]).optional(),
  number_of_data_subjects: z.enum(["under_1k", "under_10k", "under_100k", "over_100k"]).optional(),
  data_categories_processed: z.array(z.string()).optional(),
  data_subject_categories: z.array(z.string()).optional(),
  processing_purposes: z.array(z.string()).optional(),
});

type FormData = z.infer<typeof schema>;

const styles = {
  section: "space-y-6",
  pillGroup: "flex flex-wrap gap-2",
  pill: {
    base: "px-4 py-2 text-sm border rounded-full transition-colors",
    active: "border-blue-600 bg-blue-50 text-blue-700 font-medium",
    inactive: "border-gray-300 text-gray-600 hover:border-blue-500",
  },
  cardGroup: "space-y-2",
  grid: "grid grid-cols-2 gap-2",
  labelRow: "flex items-center gap-1.5 mb-2",
  warning: "text-xs text-amber-600 mt-2",
  nav: "flex justify-between mt-8",
};

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
];

const DATA_SUBJECT_OPTIONS = [
  { value: "customers", label: "Customers" },
  { value: "employees", label: "Employees" },
  { value: "minors", label: "Minors ⚠️" },
  { value: "patients", label: "Patients" },
  { value: "website_visitors", label: "Website Visitors" },
  { value: "job_applicants", label: "Job Applicants" },
];

const PROCESSING_PURPOSE_OPTIONS = [
  { value: "service_delivery", label: "Service Delivery" },
  { value: "marketing", label: "Marketing" },
  { value: "analytics", label: "Analytics" },
  { value: "legal_obligation", label: "Legal Obligation" },
  { value: "legitimate_interest", label: "Legitimate Interest" },
  { value: "contract_performance", label: "Contract Performance" },
];

interface Props {
  initialData: Profile | null;
}

export default function Step2Form({ initialData }: Props) {
  const { getToken } = useAuth();
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      primary_jurisdiction: initialData?.primary_jurisdiction ?? "",
      data_role: initialData?.data_role ?? undefined,
      number_of_data_subjects: initialData?.number_of_data_subjects ?? undefined,
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

  function toggleMulti(
    field: "data_categories_processed" | "data_subject_categories" | "processing_purposes",
    value: string
  ) {
    const current = watch(field) ?? [];
    const updated = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value];
    setValue(field, updated);
  }

  // ── Sections ──────────────────────────────────────────────

  function JurisdictionField() {
    return (
      <FormField label="Primary jurisdiction">
        <select
          {...register("primary_jurisdiction")}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
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
  }

  function DataRoleField() {
    return (
      <div>
        <div className={styles.labelRow}>
          <span className="text-sm font-medium text-gray-700">Your data role</span>
          <Tooltip text="A Controller decides why and how data is processed. A Processor handles data on behalf of a Controller. Determines your obligations under GDPR Art. 4 & 28." />
        </div>
        <div className={styles.cardGroup}>
          {DATA_ROLE_OPTIONS.map((opt) => (
            <SelectCard
              key={opt.value}
              label={opt.label}
              description={opt.description}
              selected={dataRole === opt.value}
              onClick={() => setValue("data_role", opt.value as FormData["data_role"])}
            />
          ))}
        </div>
      </div>
    );
  }

  function DataSubjectCountField() {
    return (
      <FormField label="Approximate number of data subjects">
        <div className={styles.pillGroup}>
          {DATA_SUBJECT_COUNT_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() =>
                setValue(
                  "number_of_data_subjects",
                  opt.value as FormData["number_of_data_subjects"]
                )
              }
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
  }

  function DataCategoriesField() {
    return (
      <div>
        <div className={styles.labelRow}>
          <span className="text-sm font-medium text-gray-700">Data categories processed</span>
          <Tooltip text="⚠️ marked categories are special category data under GDPR Art. 9 — stricter rules apply including explicit consent or other legal basis." />
        </div>
        <div className={styles.grid}>
          {DATA_CATEGORY_OPTIONS.map((opt) => (
            <CheckboxCard
              key={opt.value}
              label={opt.label}
              checked={dataCategories.includes(opt.value)}
              onChange={() => toggleMulti("data_categories_processed", opt.value)}
            />
          ))}
        </div>
        {hasSpecialCategory && (
          <p className={styles.warning}>
            ⚠️ Special category data detected — stricter obligations apply under GDPR Art. 9
          </p>
        )}
      </div>
    );
  }

  function DataSubjectCategoriesField() {
    return (
      <div>
        <p className="text-sm font-medium text-gray-700 mb-2">Data subject categories</p>
        <div className={styles.grid}>
          {DATA_SUBJECT_OPTIONS.map((opt) => (
            <CheckboxCard
              key={opt.value}
              label={opt.label}
              checked={subjectCategories.includes(opt.value)}
              onChange={() => toggleMulti("data_subject_categories", opt.value)}
            />
          ))}
        </div>
      </div>
    );
  }

  function ProcessingPurposesField() {
    return (
      <div>
        <div className={styles.labelRow}>
          <span className="text-sm font-medium text-gray-700">Processing purposes</span>
          <Tooltip text="Legal Obligation means processing is required by law (e.g. tax records). Legitimate Interest requires a balancing test under GDPR Art. 6(1)(f)." />
        </div>
        <div className={styles.grid}>
          {PROCESSING_PURPOSE_OPTIONS.map((opt) => (
            <CheckboxCard
              key={opt.value}
              label={opt.label}
              checked={purposes.includes(opt.value)}
              onChange={() => toggleMulti("processing_purposes", opt.value)}
            />
          ))}
        </div>
      </div>
    );
  }

  function Navigation() {
    return (
      <div className={styles.nav}>
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        <Button
          type="button"
          variant="secondary"
          onClick={() => router.push("/onboarding/step/1" as any)}
        >
          ← Back
        </Button>
        <Button type="submit" loading={isSubmitting} loadingText="Saving...">
          Save & Continue →
        </Button>
      </div>
    );
  }

  // ── Submit ─────────────────────────────────────────────────

  async function onSubmit(data: FormData) {
    setServerError(null);
    try {
      const token = await getToken();
      const res = await clientApiFetch("/api/v1/profile", token!, {
        method: "PATCH",
        body: JSON.stringify({
          primary_jurisdiction: data.primary_jurisdiction || null,
          data_role: data.data_role || null,
          number_of_data_subjects: data.number_of_data_subjects || null,
          data_categories_processed: data.data_categories_processed ?? [],
          data_subject_categories: data.data_subject_categories ?? [],
          processing_purposes: data.processing_purposes ?? [],
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
  }

  // ── Render ─────────────────────────────────────────────────

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div className={styles.section}>
        <JurisdictionField />
        <DataRoleField />
        <DataSubjectCountField />
        <DataCategoriesField />
        <DataSubjectCategoriesField />
        <ProcessingPurposesField />
      </div>
      {serverError && <p className="mt-4 text-sm text-red-600">{serverError}</p>}
      <Navigation />
    </form>
  );
}
