"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useState, KeyboardEvent } from "react";
import { Button } from "@/components/ui/Button";
import { Tooltip } from "@/components/ui/Tooltip";
import { clientApiFetch } from "@/lib/clientApi";
import type { Profile } from "@/types/profile";

const schema = z.object({
  tech_stack: z.array(z.string()).optional(),
});

type FormData = z.infer<typeof schema>;

const styles = {
  section: "space-y-6",
  tagInput:
    "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm flex flex-wrap gap-2 min-h-[44px] focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent",
  tag: "inline-flex items-center gap-1 bg-blue-50 border border-blue-200 text-blue-700 px-2.5 py-0.5 rounded-full text-xs",
  tagRemove: "text-blue-400 hover:text-blue-700 ml-1 font-medium",
  groupLabel: "text-xs font-medium text-gray-500 uppercase tracking-wide",
  chipGroup: "flex flex-wrap gap-2 mt-2",
  chip: "px-3 py-1.5 text-xs border border-gray-300 rounded-full text-gray-600 hover:border-blue-500 hover:text-blue-600 hover:bg-blue-50 transition-colors",
  labelRow: "flex items-center gap-1.5",
  hint: "text-xs text-gray-400 mt-1",
  nav: "flex justify-between mt-8",
};

const QUICK_ADD_GROUPS = [
  {
    label: "☁️ Cloud",
    tools: ["AWS", "Azure", "GCP", "Vercel", "Cloudflare"],
  },
  {
    label: "📋 CRM & Marketing",
    tools: ["HubSpot", "Salesforce", "Mailchimp", "Pipedrive", "Intercom"],
  },
  {
    label: "📊 Analytics",
    tools: ["Google Analytics", "Mixpanel", "Segment", "Amplitude"],
  },
  {
    label: "🤖 AI / ML",
    tools: ["OpenAI", "Claude", "Gemini", "Copilot", "Cursor"],
    showTooltip: true,
  },
];

interface Props {
  initialData: Profile | null;
}

export default function Step3Form({ initialData }: Props) {
  const { getToken } = useAuth();
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState("");

  const {
    handleSubmit,
    watch,
    setValue,
    formState: { isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      tech_stack: initialData?.tech_stack ?? [],
    },
  });

  const techStack = watch("tech_stack") ?? [];

  function addTool(tool: string) {
    const trimmed = tool.trim();
    if (!trimmed || techStack.includes(trimmed)) return;
    setValue("tech_stack", [...techStack, trimmed]);
  }

  function removeTool(tool: string) {
    setValue(
      "tech_stack",
      techStack.filter((t) => t !== tool)
    );
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTool(inputValue);
      setInputValue("");
    }
    if (e.key === "Backspace" && inputValue === "" && techStack.length > 0) {
      removeTool(techStack[techStack.length - 1]);
    }
  }

  // ── Sections ──────────────────────────────────────────────

  function TagInputField() {
    return (
      <div>
        <div className={styles.labelRow}>
          <span className="text-sm font-medium text-gray-700">Search and add tools</span>
          <Tooltip text="Any third-party tool that processes personal data on your behalf is a data processor under GDPR Art. 28. AI tools may trigger EU AI Act high-risk classification." />
        </div>
        <div className={`${styles.tagInput} mt-1`}>
          {techStack.map((tool) => (
            <span key={tool} className={styles.tag}>
              {tool}
              <button type="button" onClick={() => removeTool(tool)} className={styles.tagRemove}>
                ×
              </button>
            </span>
          ))}
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onBlur={() => {
              if (inputValue.trim()) {
                addTool(inputValue);
                setInputValue("");
              }
            }}
            placeholder={
              techStack.length === 0 ? "Type a tool name and press Enter..." : "Add more..."
            }
            className="flex-1 min-w-[140px] outline-none text-sm"
          />
        </div>
        <p className={styles.hint}>Press Enter or comma to add. Backspace to remove last.</p>
      </div>
    );
  }

  function QuickAddGroups() {
    return (
      <>
        {QUICK_ADD_GROUPS.map((group) => {
          const remaining = group.tools.filter((t) => !techStack.includes(t));
          return (
            <div key={group.label}>
              <div className={styles.labelRow}>
                <p className={styles.groupLabel}>{group.label}</p>
                {group.showTooltip && (
                  <Tooltip text="AI systems used in high-risk contexts may require conformity assessments under the EU AI Act." />
                )}
              </div>
              <div className={styles.chipGroup}>
                {remaining.length > 0 ? (
                  remaining.map((tool) => (
                    <button
                      key={tool}
                      type="button"
                      onClick={() => addTool(tool)}
                      className={styles.chip}
                    >
                      + {tool}
                    </button>
                  ))
                ) : (
                  <span className="text-xs text-gray-400 italic">All added ✓</span>
                )}
              </div>
            </div>
          );
        })}
      </>
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
            router.push("/onboarding/step/2" as any)
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
          tech_stack: data.tech_stack ?? [],
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.detail ?? "Failed to save. Please try again.");
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      router.push("/onboarding/step/4" as any);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Something went wrong.");
    }
  }

  // ── Render ─────────────────────────────────────────────────

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div className={styles.section}>
        <TagInputField />
        <QuickAddGroups />
      </div>
      {serverError && <p className="mt-4 text-sm text-red-600">{serverError}</p>}
      <Navigation />
    </form>
  );
}
