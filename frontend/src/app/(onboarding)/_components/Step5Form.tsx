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
import { CheckboxCard } from "@/components/ui/CheckboxCard";
import { Tooltip } from "@/components/ui/Tooltip";
import { clientApiFetch } from "@/lib/clientApi";
import type { Profile } from "@/types/profile";
import { OtherInput } from "@/components/ui/OtherInput";

// ── Schema ────────────────────────────────────────────────

const schema = z
  .object({
    has_compliance_officer: z.boolean({ error: "Please answer this question" }),
    dpo_name: z.string().optional(),
    dpo_email: z.string().email("Must be a valid email").optional().or(z.literal("")),
    legal_contact_email: z.string().email("Must be a valid email").optional().or(z.literal("")),
    certifications: z.array(z.string()).optional(),
    previous_regulatory_action: z.boolean({ error: "Please answer this question" }),
  })
  .superRefine((data, ctx) => {
    if (data.has_compliance_officer === true) {
      if (!data.dpo_name?.trim()) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "DPO name is required",
          path: ["dpo_name"],
        });
      }
      if (!data.dpo_email?.trim()) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "DPO email is required",
          path: ["dpo_email"],
        });
      }
    }
  });

type FormData = z.infer<typeof schema>;

// ── Constants ─────────────────────────────────────────────

const CERTIFICATION_OPTIONS = [
  { value: "iso_27001", label: "ISO 27001" },
  { value: "soc2", label: "SOC 2" },
  { value: "pci_dss", label: "PCI-DSS" },
  { value: "hipaa", label: "HIPAA" },
  { value: "other", label: "Other" },
  { value: "none", label: "None" },
];

// ── Styles ────────────────────────────────────────────────

const styles = {
  section: "space-y-6",
  yesNoGroup: "flex gap-3",
  yesNoBtn: {
    base: "flex-1 py-3 border rounded-lg text-sm text-center transition-colors",
    active: "border-navy bg-navy/10 text-navy font-medium",
    inactive: "border-gray-300 text-gray-600 hover:border-navy hover:bg-gray-50",
  },
  grid: "grid grid-cols-1 sm:grid-cols-2 gap-2",
  twoCol: "grid grid-cols-1 sm:grid-cols-2 gap-4",
  labelRow: "flex items-center gap-1.5 mb-2",
  nav: "flex justify-between mt-8",
};

// ── Props ─────────────────────────────────────────────────

interface Props {
  initialData: Profile | null;
}

// ── Component ─────────────────────────────────────────────

export default function Step5Form({ initialData }: Props) {
  const { getToken } = useAuth();
  const router = useRouter();

  // ── State ────────────────────────────────────────────────

  const [serverError, setServerError] = useState<string | null>(null);
  const [otherCertifications, setOtherCertifications] = useState<string[]>([]);

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

  // ── Handlers ──────────────────────────────────────────────

  const toggleCertification = (value: string) => {
    if (value === "none") {
      setValue("certifications", certifications.includes("none") ? [] : ["none"]);
      setOtherCertifications([]);
      return;
    }
    if (value === "other" && certifications.includes("other")) {
      setOtherCertifications([]); // clear when unchecking
    }
    const without = certifications.filter((v) => v !== "none");
    const updated = without.includes(value)
      ? without.filter((v) => v !== value)
      : [...without, value];
    setValue("certifications", updated);
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

  const renderDpoQuestion = () => (
    <FormField
      label="Do you have a Data Protection Officer (DPO)?"
      required
      error={errors.has_compliance_officer?.message}
    >
      <div className={styles.labelRow}>
        <Tooltip text="A DPO is mandatory under GDPR Art. 37 for public authorities, organisations processing special category data at large scale, or those conducting large-scale systematic monitoring." />
      </div>
      {renderYesNo(
        hasDpo,
        () => setValue("has_compliance_officer", true, { shouldValidate: true }),
        () => {
          setValue("has_compliance_officer", false, { shouldValidate: true });
          setValue("dpo_name", "");
          setValue("dpo_email", "");
        }
      )}
    </FormField>
  );

  const renderDpoDetails = () => {
    if (!hasDpo) return null;
    return (
      <div className={styles.twoCol}>
        <FormField label="DPO name" required error={errors.dpo_name?.message}>
          <Input {...register("dpo_name")} placeholder="Jane Smith" hasError={!!errors.dpo_name} />
        </FormField>
        <FormField label="DPO email" required error={errors.dpo_email?.message}>
          <Input
            {...register("dpo_email")}
            type="email"
            placeholder="dpo@example.com"
            hasError={!!errors.dpo_email}
          />
        </FormField>
      </div>
    );
  };

  const renderLegalContact = () => (
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

  const renderCertifications = () => (
    <FormField label="Existing certifications" hint="optional">
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
      <OtherInput
        show={certifications.includes("other")}
        values={otherCertifications}
        onChange={setOtherCertifications}
        placeholder="e.g. CSA STAR, FedRAMP, TISAX..."
      />
    </FormField>
  );

  const renderRegulatoryAction = () => (
    <FormField
      label="Previous regulatory action or fine?"
      required
      error={errors.previous_regulatory_action?.message}
    >
      <div className={styles.labelRow}>
        <Tooltip text="Prior infractions are a factor in GDPR fine calculations under Art. 83(2)(e). This helps us accurately assess your risk exposure." />
      </div>
      {renderYesNo(
        previousAction,
        () => setValue("previous_regulatory_action", true, { shouldValidate: true }),
        () => setValue("previous_regulatory_action", false, { shouldValidate: true })
      )}
    </FormField>
  );

  const renderNavigation = () => (
    <div className={styles.nav}>
      <Button type="button" variant="secondary" onClick={() => onBack()}>
        ← Back
      </Button>
      <Button type="submit" variant="primary" loading={isSubmitting} loadingText="Saving...">
        Continue →
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
          has_compliance_officer: data.has_compliance_officer ?? null,
          dpo_name: data.dpo_name || null,
          dpo_email: data.dpo_email || null,
          legal_contact_email: data.legal_contact_email || null,
          certifications: [
            ...(data.certifications ?? []).filter((v) => v !== "other"),
            ...otherCertifications,
          ],
          previous_regulatory_action: data.previous_regulatory_action ?? null,
        }),
      });
    } catch {}
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    router.push("/onboarding/step/4" as any);
  };

  const onSubmit = async (data: FormData) => {
    setServerError(null);
    try {
      const token = await getToken();
      const saveRes = await clientApiFetch("/api/v1/profile", token!, {
        method: "PATCH",
        body: JSON.stringify({
          has_compliance_officer: data.has_compliance_officer ?? null,
          dpo_name: data.dpo_name || null,
          dpo_email: data.dpo_email || null,
          legal_contact_email: data.legal_contact_email || null,
          certifications: [
            ...(data.certifications ?? []).filter((v) => v !== "other"),
            ...otherCertifications,
          ],
          previous_regulatory_action: data.previous_regulatory_action ?? null,
        }),
      });
      if (!saveRes.ok) {
        const body = await saveRes.json().catch(() => ({}));
        throw new Error(body?.detail ?? "Failed to save. Please try again.");
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      router.push("/onboarding/step/6" as any);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Something went wrong.");
    }
  };

  // ── Render ─────────────────────────────────────────────────

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div className={styles.section}>
        {renderDpoQuestion()}
        {renderDpoDetails()}
        {renderLegalContact()}
        {renderCertifications()}
        {renderRegulatoryAction()}
      </div>
      {serverError && <p className="mt-4 text-sm text-red-600">{serverError}</p>}
      {renderNavigation()}
    </form>
  );
}
