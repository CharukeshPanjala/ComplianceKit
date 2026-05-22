"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { FormField } from "@/components/ui/FormField";
import { SelectCard } from "@/components/ui/SelectCard";
import { clientApiFetch } from "@/lib/clientApi";
import type { Profile } from "@/types/profile";
import { OtherInput } from "@/components/ui/OtherInput";

// ── Schema ────────────────────────────────────────────────

const schema = z.object({
  tenant_name: z.string().min(1, "Company name is required"),
  industry: z.string().min(1, "Please select an industry"),
  company_size: z.string().min(1, "Please select a company size"),
  b2b_or_b2c: z.string().min(1, "Please select a customer type"),
  website_url: z.string().url("Must be a valid URL").optional().or(z.literal("")),
});

type FormData = z.infer<typeof schema>;

// ── Constants ─────────────────────────────────────────────

const INDUSTRY_OPTIONS = [
  { value: "technology", label: "Technology" },
  { value: "healthcare", label: "Healthcare" },
  { value: "finance", label: "Finance" },
  { value: "legal", label: "Legal" },
  { value: "retail", label: "Retail" },
  { value: "education", label: "Education" },
  { value: "manufacturing", label: "Manufacturing" },
  { value: "other", label: "Other" },
];

const COMPANY_SIZE_OPTIONS = [
  { value: "1-10", label: "1–10" },
  { value: "11-50", label: "11–50" },
  { value: "51-200", label: "51–200" },
  { value: "201-1000", label: "201–1,000" },
  { value: "1000+", label: "1,000+" },
];

const B2B_OR_B2C_OPTIONS = [
  { value: "b2b", label: "B2B", description: "You sell to other businesses" },
  { value: "b2c", label: "B2C", description: "You sell directly to consumers" },
  { value: "both", label: "Both", description: "You serve both businesses and consumers" },
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
  nav: "flex justify-end mt-8",
};

// ── Props ─────────────────────────────────────────────────

interface Props {
  initialData: Profile | null;
}

// ── Component ─────────────────────────────────────────────

export default function Step1Form({ initialData }: Props) {
  const { getToken } = useAuth();
  const router = useRouter();

  // ── State ────────────────────────────────────────────────

  const [serverError, setServerError] = useState<string | null>(null);
  const [customIndustry, setCustomIndustry] = useState(
    // pre-fill if saved value isn't one of the known options
    initialData?.industry &&
      ![
        "technology",
        "healthcare",
        "finance",
        "legal",
        "retail",
        "education",
        "manufacturing",
        "other",
      ].includes(initialData.industry)
      ? initialData.industry
      : ""
  );

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
      tenant_name: initialData?.tenant_name ?? "",
      industry: initialData?.industry ?? "",
      company_size: initialData?.company_size ?? "",
      b2b_or_b2c: initialData?.b2b_or_b2c ?? "",
      website_url: initialData?.website_url ?? "",
    },
  });

  const companySize = watch("company_size");
  const b2bOrB2c = watch("b2b_or_b2c");

  // ── Render helpers ────────────────────────────────────────

  const renderCompanyName = () => (
    <FormField label="Company name" required error={errors.tenant_name?.message}>
      <Input {...register("tenant_name")} placeholder="Acme GmbH" hasError={!!errors.tenant_name} />
    </FormField>
  );

  const renderIndustry = () => (
    <FormField label="Industry" required error={errors.industry?.message}>
      <select
        {...register("industry")}
        className={`w-full px-3 py-2 border rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-navy ${
          errors.industry ? "border-red-400" : "border-gray-300"
        }`}
      >
        <option value="">Select your industry</option>
        {INDUSTRY_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      <OtherInput
        show={watch("industry") === "other"}
        values={customIndustry ? [customIndustry] : []}
        onChange={(vals) => setCustomIndustry(vals[vals.length - 1] ?? "")}
        placeholder="e.g. Hospitality, Non-profit, Gaming..."
        label="Please specify your industry"
      />
    </FormField>
  );
  const renderCompanySize = () => (
    <FormField label="Company size" required error={errors.company_size?.message}>
      <div className={styles.pillGroup}>
        {COMPANY_SIZE_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            type="button"
            onClick={() => setValue("company_size", opt.value, { shouldValidate: true })}
            className={`${styles.pill.base} ${
              companySize === opt.value ? styles.pill.active : styles.pill.inactive
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </FormField>
  );

  const renderCustomerType = () => (
    <FormField label="Who are your customers?" required error={errors.b2b_or_b2c?.message}>
      <div className={styles.cardGroup}>
        {B2B_OR_B2C_OPTIONS.map((opt) => (
          <SelectCard
            key={opt.value}
            label={opt.label}
            description={opt.description}
            selected={b2bOrB2c === opt.value}
            onClick={() => setValue("b2b_or_b2c", opt.value, { shouldValidate: true })}
          />
        ))}
      </div>
    </FormField>
  );

  const renderWebsite = () => (
    <FormField label="Website" hint="optional" error={errors.website_url?.message}>
      <Input
        {...register("website_url")}
        type="url"
        placeholder="https://example.com"
        hasError={!!errors.website_url}
      />
    </FormField>
  );

  const renderNavigation = () => (
    <div className={styles.nav}>
      <Button type="submit" loading={isSubmitting} loadingText="Saving...">
        Save & Continue →
      </Button>
    </div>
  );

  // ── Submit ─────────────────────────────────────────────────

  const onSubmit = async (data: FormData) => {
    setServerError(null);
    try {
      const token = await getToken();
      const res = await clientApiFetch("/api/v1/profile", token!, {
        method: initialData ? "PATCH" : "POST",
        body: JSON.stringify({
          tenant_name: data.tenant_name,
          industry: watch("industry") === "other" ? customIndustry || null : data.industry || null,
          company_size: data.company_size || null,
          b2b_or_b2c: data.b2b_or_b2c || null,
          website_url: data.website_url || null,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.detail ?? "Failed to save. Please try again.");
      }

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      router.push("/onboarding/step/2" as any);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Something went wrong.");
    }
  };

  // ── Render ─────────────────────────────────────────────────

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div className={styles.section}>
        {renderCompanyName()}
        {renderIndustry()}
        {renderCompanySize()}
        {renderCustomerType()}
        {renderWebsite()}
      </div>
      {serverError && <p className="mt-4 text-sm text-red-600">{serverError}</p>}
      {renderNavigation()}
    </form>
  );
}
