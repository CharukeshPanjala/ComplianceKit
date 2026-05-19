"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { FormField } from "@/components/ui/FormField";
import { CheckboxCard } from "@/components/ui/CheckboxCard";
import { Tooltip } from "@/components/ui/Tooltip";
import { clientApiFetch } from "@/lib/clientApi";
import type { Profile } from "@/types/profile";

const schema = z.object({
  has_compliance_officer: z.boolean().optional(),
  dpo_name: z.string().optional(),
  dpo_email: z.string().email("Must be a valid email").optional().or(z.literal("")),
  legal_contact_email: z.string().email("Must be a valid email").optional().or(z.literal("")),
  certifications: z.array(z.string()).optional(),
  previous_regulatory_action: z.boolean().optional(),
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
  twoCol: "grid grid-cols-2 gap-4",
  labelRow: "flex items-center gap-1.5 mb-2",
  nav: "flex justify-between mt-8",
};

const CERTIFICATION_OPTIONS = [
  { value: "iso_27001", label: "ISO 27001" },
  { value: "soc2", label: "SOC 2" },
  { value: "pci_dss", label: "PCI-DSS" },
  { value: "hipaa", label: "HIPAA" },
  { value: "none", label: "None" },
];

interface Props {
  initialData: Profile | null;
}

export default function Step5Form({ initialData }: Props) {
  const { getToken } = useAuth();
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      has_compliance_officer: initialData?.has_compliance_officer ?? undefined,
      dpo_name: initialData?.dpo_name ?? "",
      dpo_email: initialData?.dpo_email ?? "",
      legal_contact_email: initialData?.legal_contact_email ?? "",
      certifications: initialData?.certifications ?? [],
      previous_regulatory_action: initialData?.previous_regulatory_action ?? undefined,
    },
  });

  const hasDpo = watch("has_compliance_officer");
  const certifications = watch("certifications") ?? [];
  const previousAction = watch("previous_regulatory_action");

  function toggleCertification(value: string) {
    if (value === "none") {
      setValue("certifications", certifications.includes("none") ? [] : ["none"]);
      return;
    }
    const without = certifications.filter((v) => v !== "none");
    const updated = without.includes(value)
      ? without.filter((v) => v !== value)
      : [...without, value];
    setValue("certifications", updated);
  }

  // ── Sections ──────────────────────────────────────────────

  function DpoField() {
    return (
      <div>
        <div className={styles.labelRow}>
          <span className="text-sm font-medium text-gray-700">
            Do you have a Data Protection Officer (DPO)?
          </span>
          <Tooltip text="A DPO is mandatory under GDPR Art. 37 for public authorities, organisations processing special category data at large scale, or those conducting large-scale systematic monitoring." />
        </div>
        <div className={styles.yesNoGroup}>
          <button
            type="button"
            onClick={() => setValue("has_compliance_officer", true)}
            className={`${styles.yesNoBtn.base} ${
              hasDpo === true ? styles.yesNoBtn.active : styles.yesNoBtn.inactive
            }`}
          >
            Yes
          </button>
          <button
            type="button"
            onClick={() => {
              setValue("has_compliance_officer", false);
              setValue("dpo_name", "");
              setValue("dpo_email", "");
            }}
            className={`${styles.yesNoBtn.base} ${
              hasDpo === false ? styles.yesNoBtn.active : styles.yesNoBtn.inactive
            }`}
          >
            No
          </button>
        </div>
      </div>
    );
  }

  function DpoDetailsField() {
    if (!hasDpo) return null;

    return (
      <div className={styles.twoCol}>
        <FormField label="DPO name" error={errors.dpo_name?.message}>
          <Input {...register("dpo_name")} placeholder="Jane Smith" hasError={!!errors.dpo_name} />
        </FormField>
        <FormField label="DPO email" error={errors.dpo_email?.message}>
          <Input
            {...register("dpo_email")}
            type="email"
            placeholder="dpo@example.com"
            hasError={!!errors.dpo_email}
          />
        </FormField>
      </div>
    );
  }

  function LegalContactField() {
    return (
      <FormField
        label="Legal contact email"
        hint="optional"
        error={errors.legal_contact_email?.message}
      >
        <Input
          {...register("legal_contact_email")}
          type="email"
          placeholder="legal@example.com"
          hasError={!!errors.legal_contact_email}
        />
      </FormField>
    );
  }

  function CertificationsField() {
    return (
      <FormField label="Existing certifications">
        <div className={styles.grid}>
          {CERTIFICATION_OPTIONS.map((opt) => (
            <CheckboxCard
              key={opt.value}
              label={opt.label}
              checked={certifications.includes(opt.value)}
              onChange={() => toggleCertification(opt.value)}
              className={opt.value === "none" ? "col-span-2" : ""}
            />
          ))}
        </div>
      </FormField>
    );
  }

  function RegulatoryActionField() {
    return (
      <div>
        <div className={styles.labelRow}>
          <span className="text-sm font-medium text-gray-700">
            Previous regulatory action or fine?
          </span>
          <Tooltip text="Prior infractions are a factor in GDPR fine calculations under Art. 83(2)(e). This helps us accurately assess your risk exposure." />
        </div>
        <div className={styles.yesNoGroup}>
          <button
            type="button"
            onClick={() => setValue("previous_regulatory_action", true)}
            className={`${styles.yesNoBtn.base} ${
              previousAction === true ? styles.yesNoBtn.active : styles.yesNoBtn.inactive
            }`}
          >
            Yes
          </button>
          <button
            type="button"
            onClick={() => setValue("previous_regulatory_action", false)}
            className={`${styles.yesNoBtn.base} ${
              previousAction === false ? styles.yesNoBtn.active : styles.yesNoBtn.inactive
            }`}
          >
            No
          </button>
        </div>
      </div>
    );
  }

  function Navigation() {
    return (
      <div className={styles.nav}>
        <Button
          type="button"
          variant="secondary"
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          onClick={() => router.push("/onboarding/step/4" as any)}
        >
          ← Back
        </Button>
        <Button type="submit" variant="success" loading={isSubmitting} loadingText="Submitting...">
          Finish & Submit ✓
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
          has_compliance_officer: data.has_compliance_officer ?? null,
          dpo_name: data.dpo_name || null,
          dpo_email: data.dpo_email || null,
          legal_contact_email: data.legal_contact_email || null,
          certifications: data.certifications ?? [],
          previous_regulatory_action: data.previous_regulatory_action ?? null,
          is_complete: true,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.detail ?? "Failed to save. Please try again.");
      }

      router.push("/dashboard");
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Something went wrong.");
    }
  }

  // ── Render ─────────────────────────────────────────────────

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div className={styles.section}>
        <DpoField />
        <DpoDetailsField />
        <LegalContactField />
        <CertificationsField />
        <RegulatoryActionField />
      </div>
      {serverError && <p className="mt-4 text-sm text-red-600">{serverError}</p>}
      <Navigation />
    </form>
  );
}
