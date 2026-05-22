"use client";

import { useState, KeyboardEvent } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/ui/FormField";
import { CheckboxCard } from "@/components/ui/CheckboxCard";
import { Tooltip } from "@/components/ui/Tooltip";
import { clientApiFetch } from "@/lib/clientApi";
import type { Profile } from "@/types/profile";

// ── Schema ────────────────────────────────────────────────

const schema = z
  .object({
    uses_cloud_services: z.boolean({ error: "Please answer this question" }),
    cloud_providers: z.array(z.string()).optional(),
    primary_cloud_region: z.string().optional(),
    has_on_premise_servers: z.boolean({ error: "Please answer this question" }),
  })
  .superRefine((data, ctx) => {
    if (data.uses_cloud_services === true) {
      if (!data.cloud_providers?.length) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Select at least one cloud provider",
          path: ["cloud_providers"],
        });
      }
      if (!data.primary_cloud_region) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Please select a primary region",
          path: ["primary_cloud_region"],
        });
      }
    }
  });

type FormData = z.infer<typeof schema>;

// ── Constants ─────────────────────────────────────────────

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

// ── Styles ────────────────────────────────────────────────

const styles = {
  section: "space-y-6",
  labelRow: "flex items-center gap-1.5 mb-2",
  yesNoGroup: "flex gap-3",
  yesNoBtn: {
    base: "flex-1 py-3 border rounded-lg text-sm text-center transition-colors",
    active: "border-navy bg-navy/10 text-navy font-medium",
    inactive: "border-gray-300 text-gray-600 hover:border-navy hover:bg-gray-50",
  },
  grid: "grid grid-cols-1 sm:grid-cols-2 gap-2",

  // Custom provider chips + input
  chipRow: "flex flex-wrap gap-2 mb-2",
  chip: "inline-flex items-center gap-1 bg-navy/10 border border-navy/30 text-navy px-2.5 py-0.5 rounded-full text-xs font-medium",
  chipRemove: "text-navy/40 hover:text-navy ml-0.5 font-bold text-sm leading-none",
  customRow: "flex gap-2 mt-2",
  customInput:
    "flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none " +
    "focus:ring-2 focus:ring-navy focus:border-transparent",

  nav: "flex justify-between mt-8",
};

// ── Props ─────────────────────────────────────────────────

interface Props {
  initialData: Profile | null;
}

// ── Component ─────────────────────────────────────────────

export default function Step4Form({ initialData }: Props) {
  const { getToken } = useAuth();
  const router = useRouter();

  // ── State ────────────────────────────────────────────────

  const [serverError, setServerError] = useState<string | null>(null);
  const [customDraft, setCustomDraft] = useState("");
  const [customProviders, setCustomProviders] = useState<string[]>(
    // Pre-fill custom providers saved previously (anything that isn't a known value)
    initialData?.cloud_providers?.filter((p) => !["aws", "azure", "gcp", "other"].includes(p)) ?? []
  );

  // ── Form ─────────────────────────────────────────────────

  const {
    handleSubmit,
    watch,
    setValue,
    register,
    formState: { errors, isSubmitting },
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

  // ── Handlers ──────────────────────────────────────────────

  const toggleProvider = (value: string) => {
    if (value === "other" && cloudProviders.includes("other")) {
      setCustomProviders([]);
    }
    const updated = cloudProviders.includes(value)
      ? cloudProviders.filter((v) => v !== value)
      : [...cloudProviders, value];
    setValue("cloud_providers", updated);
  };

  const confirmCustomProvider = () => {
    const trimmed = customDraft.trim();
    if (!trimmed || customProviders.includes(trimmed)) return;
    setCustomProviders((prev) => [...prev, trimmed]);
    setCustomDraft("");
  };

  const removeCustomProvider = (name: string) => {
    setCustomProviders((prev) => prev.filter((p) => p !== name));
  };

  const handleCustomKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      confirmCustomProvider();
    }
  };

  // ── Render helpers ────────────────────────────────────────

  const renderYesNo = (value: boolean | undefined, onYes: () => void, onNo: () => void) => (
    <div className={styles.yesNoGroup}>
      <button
        type="button"
        onClick={onYes}
        className={`${styles.yesNoBtn.base} ${value === true ? styles.yesNoBtn.active : styles.yesNoBtn.inactive}`}
      >
        Yes
      </button>
      <button
        type="button"
        onClick={onNo}
        className={`${styles.yesNoBtn.base} ${value === false ? styles.yesNoBtn.active : styles.yesNoBtn.inactive}`}
      >
        No
      </button>
    </div>
  );

  const renderCloudProviders = () => (
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
  );

  const renderOtherProviderInput = () => {
    if (!cloudProviders.includes("other")) return null;

    return (
      <FormField label="Specify your other provider(s)">
        {/* Confirmed chips */}
        {customProviders.length > 0 && (
          <div className={styles.chipRow}>
            {customProviders.map((name) => (
              <span key={name} className={styles.chip}>
                {name}
                <button
                  type="button"
                  onClick={() => removeCustomProvider(name)}
                  className={styles.chipRemove}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}

        {/* Draft input + Add button */}
        <div className={styles.customRow}>
          <input
            type="text"
            value={customDraft}
            onChange={(e) => setCustomDraft(e.target.value)}
            onKeyDown={handleCustomKeyDown}
            onBlur={confirmCustomProvider}
            placeholder="e.g. Hetzner, OVH, Alibaba Cloud..."
            className={styles.customInput}
          />
          <Button
            type="button"
            variant="secondary"
            onClick={confirmCustomProvider}
            disabled={!customDraft.trim()}
          >
            + Add
          </Button>
        </div>
      </FormField>
    );
  };

  const renderCloudRegion = () => (
    <div>
      <div className={styles.labelRow}>
        <span className="text-sm font-medium text-gray-700">
          Primary cloud region <span className="text-red-500">*</span>
        </span>
        <Tooltip text="Transferring personal data outside the EU requires safeguards under GDPR Art. 44–49 (e.g. Standard Contractual Clauses)." />
      </div>
      <select
        {...register("primary_cloud_region")}
        className={`w-full px-3 py-2 border rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-navy ${
          errors.primary_cloud_region ? "border-red-400" : "border-gray-300"
        }`}
      >
        <option value="">Select a region</option>
        {CLOUD_REGION_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {errors.primary_cloud_region && (
        <p className="text-xs text-red-600 mt-1">{errors.primary_cloud_region.message}</p>
      )}
    </div>
  );

  const renderCloudDetails = () => {
    if (!usesCloud) return null;

    return (
      <>
        {renderCloudProviders()}
        {renderOtherProviderInput()}
        {renderCloudRegion()}
      </>
    );
  };

  const renderCloudServices = () => (
    <FormField
      label="Do you use cloud services?"
      required
      error={errors.uses_cloud_services?.message}
    >
      {renderYesNo(
        usesCloud,
        () => setValue("uses_cloud_services", true, { shouldValidate: true }),
        () => {
          setValue("uses_cloud_services", false, { shouldValidate: true });
          setValue("cloud_providers", []);
          setValue("primary_cloud_region", "");
          setCustomProviders([]);
        }
      )}
    </FormField>
  );

  const renderOnPremise = () => (
    <FormField
      label="Do you have on-premise servers?"
      required
      error={errors.has_on_premise_servers?.message}
    >
      {renderYesNo(
        hasOnPremise,
        () => setValue("has_on_premise_servers", true, { shouldValidate: true }),
        () => setValue("has_on_premise_servers", false, { shouldValidate: true })
      )}
    </FormField>
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
          uses_cloud_services: data.uses_cloud_services ?? null,
          cloud_providers: [
            ...(data.cloud_providers ?? []).filter((v) => v !== "other"),
            ...customProviders,
          ],
          primary_cloud_region: data.primary_cloud_region || null,
          has_on_premise_servers: data.has_on_premise_servers ?? null,
        }),
      });
    } catch {}
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    router.push("/onboarding/step/3" as any);
  };

  const onSubmit = async (data: FormData) => {
    setServerError(null);
    try {
      const token = await getToken();

      // Merge known providers (excluding "other" flag) with confirmed custom ones
      const providers = [
        ...(data.cloud_providers ?? []).filter((p) => p !== "other"),
        ...customProviders,
      ];

      const res = await clientApiFetch("/api/v1/profile", token!, {
        method: "PATCH",
        body: JSON.stringify({
          uses_cloud_services: data.uses_cloud_services ?? null,
          cloud_providers: providers,
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
  };

  // ── Render ─────────────────────────────────────────────────

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div className={styles.section}>
        {renderCloudServices()}
        {renderCloudDetails()}
        {renderOnPremise()}
      </div>
      {serverError && <p className="mt-4 text-sm text-red-600">{serverError}</p>}
      {renderNavigation()}
    </form>
  );
}
