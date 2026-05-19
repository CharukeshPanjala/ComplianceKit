"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/ui/FormField";
import { CheckboxCard } from "@/components/ui/CheckboxCard";
import { Tooltip } from "@/components/ui/Tooltip";
import { clientApiFetch } from "@/lib/clientApi";
import type { Profile } from "@/types/profile";

const schema = z.object({
  uses_cloud_services: z.boolean().optional(),
  cloud_providers: z.array(z.string()).optional(),
  primary_cloud_region: z.string().optional(),
  has_on_premise_servers: z.boolean().optional(),
});

type FormData = z.infer<typeof schema>;

const styles = {
  section: "space-y-6",
  yesNoGroup: "flex gap-3",
  yesNoBtn: {
    base: "flex-1 py-3 border rounded-lg text-sm text-center transition-colors",
    active: "border-blue-600 bg-blue-50 text-blue-700 font-medium",
    inactive: "border-gray-300 text-gray-600 hover:border-gray-400 hover:bg-gray-50",
  },
  grid: "grid grid-cols-2 gap-2",
  labelRow: "flex items-center gap-1.5 mb-2",
  nav: "flex justify-between mt-8",
};

const CLOUD_PROVIDER_OPTIONS = [
  { value: "aws", label: "AWS" },
  { value: "azure", label: "Azure" },
  { value: "gcp", label: "GCP" },
  { value: "other", label: "Other" },
];

const CLOUD_REGION_OPTIONS = [
  { value: "eu", label: "🇪🇺 EU / EEA" },
  { value: "us", label: "🇺🇸 United States" },
  { value: "gb", label: "🇬🇧 United Kingdom" },
  { value: "ch", label: "🇨🇭 Switzerland" },
  { value: "apac", label: "🌏 Asia-Pacific" },
];

interface Props {
  initialData: Profile | null;
}

export default function Step4Form({ initialData }: Props) {
  const { getToken } = useAuth();
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    handleSubmit,
    watch,
    setValue,
    register,
    formState: { isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      uses_cloud_services: initialData?.uses_cloud_services ?? undefined,
      cloud_providers: initialData?.cloud_providers ?? [],
      primary_cloud_region: initialData?.primary_cloud_region ?? "",
      has_on_premise_servers: initialData?.has_on_premise_servers ?? undefined,
    },
  });

  const usesCloud = watch("uses_cloud_services");
  const cloudProviders = watch("cloud_providers") ?? [];
  const hasOnPremise = watch("has_on_premise_servers");

  function toggleProvider(value: string) {
    const updated = cloudProviders.includes(value)
      ? cloudProviders.filter((v) => v !== value)
      : [...cloudProviders, value];
    setValue("cloud_providers", updated);
  }

  // ── Sections ──────────────────────────────────────────────

  function CloudServicesField() {
    return (
      <FormField label="Do you use cloud services?">
        <div className={styles.yesNoGroup}>
          <button
            type="button"
            onClick={() => setValue("uses_cloud_services", true)}
            className={`${styles.yesNoBtn.base} ${
              usesCloud === true ? styles.yesNoBtn.active : styles.yesNoBtn.inactive
            }`}
          >
            Yes
          </button>
          <button
            type="button"
            onClick={() => {
              setValue("uses_cloud_services", false);
              setValue("cloud_providers", []);
              setValue("primary_cloud_region", "");
            }}
            className={`${styles.yesNoBtn.base} ${
              usesCloud === false ? styles.yesNoBtn.active : styles.yesNoBtn.inactive
            }`}
          >
            No
          </button>
        </div>
      </FormField>
    );
  }

  function CloudDetailsField() {
    if (!usesCloud) return null;

    return (
      <>
        <FormField label="Cloud providers">
          <div className={styles.grid}>
            {CLOUD_PROVIDER_OPTIONS.map((opt) => (
              <CheckboxCard
                key={opt.value}
                label={opt.label}
                checked={cloudProviders.includes(opt.value)}
                onChange={() => toggleProvider(opt.value)}
              />
            ))}
          </div>
        </FormField>

        <div>
          <div className={styles.labelRow}>
            <span className="text-sm font-medium text-gray-700">Primary cloud region</span>
            <Tooltip text="Transferring personal data outside the EU requires safeguards under GDPR Art. 44–49 (e.g. Standard Contractual Clauses)." />
          </div>
          <select
            {...register("primary_cloud_region")}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select a region</option>
            {CLOUD_REGION_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </>
    );
  }

  function OnPremiseField() {
    return (
      <FormField label="Do you have on-premise servers?">
        <div className={styles.yesNoGroup}>
          <button
            type="button"
            onClick={() => setValue("has_on_premise_servers", true)}
            className={`${styles.yesNoBtn.base} ${
              hasOnPremise === true ? styles.yesNoBtn.active : styles.yesNoBtn.inactive
            }`}
          >
            Yes
          </button>
          <button
            type="button"
            onClick={() => setValue("has_on_premise_servers", false)}
            className={`${styles.yesNoBtn.base} ${
              hasOnPremise === false ? styles.yesNoBtn.active : styles.yesNoBtn.inactive
            }`}
          >
            No
          </button>
        </div>
      </FormField>
    );
  }

  function Navigation() {
    return (
      <div className={styles.nav}>
        <Button
          type="button"
          variant="secondary"
          onClick={() =>
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            router.push("/onboarding/step/3" as any)
          }
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
          uses_cloud_services: data.uses_cloud_services ?? null,
          cloud_providers: data.cloud_providers ?? [],
          primary_cloud_region: data.primary_cloud_region || null,
          has_on_premise_servers: data.has_on_premise_servers ?? null,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.detail ?? "Failed to save. Please try again.");
      }

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      router.push("/onboarding/step/5" as any);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Something went wrong.");
    }
  }

  // ── Render ─────────────────────────────────────────────────

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div className={styles.section}>
        <CloudServicesField />
        <CloudDetailsField />
        <OnPremiseField />
      </div>
      {serverError && <p className="mt-4 text-sm text-red-600">{serverError}</p>}
      <Navigation />
    </form>
  );
}
