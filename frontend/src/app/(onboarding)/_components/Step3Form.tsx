"use client";

import { useEffect, useMemo, useRef, useState, KeyboardEvent } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Tooltip } from "@/components/ui/Tooltip";
import { clientApiFetch } from "@/lib/clientApi";
import type { Profile } from "@/types/profile";

// ── Schema ────────────────────────────────────────────────

const schema = z.object({
  tech_stack: z.array(z.string()).optional(),
});

type FormData = z.infer<typeof schema>;

// ── Types ─────────────────────────────────────────────────

interface ToolOption {
  name: string;
  category: string;
}

// ── Helpers ───────────────────────────────────────────────

const formatCategory = (category: string): string =>
  category
    .split(/[-_]/)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

// ── Styles ────────────────────────────────────────────────

const styles = {
  section: "space-y-5",
  labelRow: "flex items-center gap-1.5 mb-1.5",

  // Tag box
  tagBox:
    "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm flex flex-wrap gap-2 " +
    "min-h-[44px] focus-within:ring-2 focus-within:ring-navy focus-within:border-transparent",
  tag: "inline-flex items-center gap-1 bg-navy/10 border border-navy/30 text-navy px-2.5 py-0.5 rounded-full text-xs font-medium",
  tagRemove: "text-navy/40 hover:text-navy ml-0.5 font-bold text-sm leading-none",
  tagInput: "flex-1 min-w-[160px] outline-none text-sm bg-transparent placeholder-gray-400",

  // Category sections
  categories: "space-y-8 max-h-[420px] overflow-y-auto pr-1",
  categoryLabel: "text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2",
  chipGroup: "flex flex-wrap gap-2",

  // Chips
  chip: {
    base: "px-3 py-1.5 text-xs border rounded-full transition-all cursor-pointer flex items-center gap-1.5",
    selected: "bg-navy/10 border-navy text-navy font-medium",
    default: "border-gray-200 text-gray-600 hover:border-navy hover:text-navy",
  },

  // Custom tool
  customSection: "pt-4 border-t border-gray-100",
  customLabel: "text-sm font-medium text-gray-700 mb-2",
  customRow: "flex gap-2",
  customInput:
    "flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none " +
    "focus:ring-2 focus:ring-navy focus:border-transparent",

  hint: "text-xs text-gray-400 mt-1.5",
  nav: "flex justify-between mt-8",
};

// ── Props ─────────────────────────────────────────────────

interface Props {
  initialData: Profile | null;
}

// ── Component ─────────────────────────────────────────────

export default function Step3Form({ initialData }: Props) {
  const { getToken } = useAuth();
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);

  // ── State ────────────────────────────────────────────────

  const [allTools, setAllTools] = useState<ToolOption[]>([]);
  const [isLoadingTools, setIsLoadingTools] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [customInput, setCustomInput] = useState("");
  const [serverError, setServerError] = useState<string | null>(null);

  // ── Form ─────────────────────────────────────────────────

  const {
    handleSubmit,
    watch,
    setValue,
    formState: { isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { tech_stack: initialData?.tech_stack ?? [] },
  });

  const techStack = watch("tech_stack") ?? [];

  // ── Load tools from API ───────────────────────────────────

  useEffect(() => {
    const loadTools = async () => {
      try {
        const token = await getToken();
        const res = await clientApiFetch("/api/v1/tools", token!, { method: "GET" });
        if (res.ok) {
          const data: ToolOption[] = await res.json();
          setAllTools(data);
        }
      } catch {
        // Fail silently — user can still add custom tools
      } finally {
        setIsLoadingTools(false);
      }
    };

    loadTools();
  }, [getToken]);

  // ── Grouped tools (filtered by search) ───────────────────

  const groupedTools = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    const filtered = query
      ? allTools.filter((t) => t.name.toLowerCase().includes(query))
      : allTools;

    return filtered.reduce<Record<string, ToolOption[]>>((acc, tool) => {
      if (!acc[tool.category]) acc[tool.category] = [];
      acc[tool.category].push(tool);
      return acc;
    }, {});
  }, [allTools, searchQuery]);

  // ── Handlers ──────────────────────────────────────────────

  const toggleTool = (name: string) => {
    const updated = techStack.includes(name)
      ? techStack.filter((t) => t !== name)
      : [...techStack, name];
    setValue("tech_stack", updated);
  };

  const removeTag = (name: string) => {
    setValue(
      "tech_stack",
      techStack.filter((t) => t !== name)
    );
  };

  const addCustomTool = () => {
    const trimmed = customInput.trim();
    if (!trimmed || techStack.includes(trimmed)) return;
    setValue("tech_stack", [...techStack, trimmed]);
    setCustomInput("");
    inputRef.current?.focus();
  };

  const handleSearchKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && searchQuery === "" && techStack.length > 0) {
      removeTag(techStack[techStack.length - 1]);
    }
  };

  const handleCustomKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addCustomTool();
    }
  };

  // ── Render helpers ────────────────────────────────────────

  const renderTagBox = () => (
    <div>
      <div className={styles.labelRow}>
        <span className="text-sm font-medium text-gray-700">Search and add tools</span>
        <Tooltip text="Any third-party tool that processes personal data on your behalf is a data processor under GDPR Art. 28. AI tools may trigger EU AI Act high-risk classification." />
      </div>

      <div className={styles.tagBox}>
        {techStack.map((tool) => (
          <span key={tool} className={styles.tag}>
            {tool}
            <button type="button" onClick={() => removeTag(tool)} className={styles.tagRemove}>
              ×
            </button>
          </span>
        ))}
        <input
          ref={inputRef}
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={handleSearchKeyDown}
          placeholder={
            isLoadingTools
              ? "Loading tools..."
              : techStack.length === 0
                ? "Search 200+ tools below..."
                : "Search to filter..."
          }
          disabled={isLoadingTools}
          className={styles.tagInput}
        />
      </div>

      <p className={styles.hint}>Select tools below · Backspace to remove last</p>
    </div>
  );

  const renderCategories = () => {
    const categories = Object.keys(groupedTools);

    if (isLoadingTools) {
      return (
        <div className="flex items-center gap-2 py-6 text-sm text-gray-400">
          <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          Loading tools...
        </div>
      );
    }

    if (categories.length === 0) {
      return (
        <p className="py-4 text-sm text-gray-400 italic">
          No tools found for &ldquo;{searchQuery}&rdquo;. Add it as a custom tool below.
        </p>
      );
    }

    return (
      <div className={styles.categories}>
        {categories.map((category) => (
          <div key={category}>
            <p className={styles.categoryLabel}>{formatCategory(category)}</p>
            <div className={styles.chipGroup}>
              {groupedTools[category].map((tool) => {
                const isSelected = techStack.includes(tool.name);
                return (
                  <button
                    key={tool.name}
                    type="button"
                    onClick={() => toggleTool(tool.name)}
                    className={`${styles.chip.base} ${
                      isSelected ? styles.chip.selected : styles.chip.default
                    }`}
                  >
                    {isSelected && <span>✓</span>}
                    {tool.name}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderCustomTool = () => (
    <div className={styles.customSection}>
      <p className={styles.customLabel}>Can&apos;t find your tool? Add it manually:</p>
      <div className={styles.customRow}>
        <input
          type="text"
          value={customInput}
          onChange={(e) => setCustomInput(e.target.value)}
          onKeyDown={handleCustomKeyDown}
          placeholder="e.g. My Custom CRM"
          className={styles.customInput}
        />
        <Button
          type="button"
          variant="secondary"
          onClick={addCustomTool}
          disabled={!customInput.trim()}
        >
          + Add
        </Button>
      </div>
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
      await clientApiFetch("/api/v1/profile", token!, {
        method: "PATCH",
        body: JSON.stringify({ tech_stack: watch("tech_stack") ?? [] }),
      });
    } catch {}
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    router.push("/onboarding/step/2" as any);
  };

  const onSubmit = async (data: FormData) => {
    setServerError(null);
    try {
      const token = await getToken();
      const res = await clientApiFetch("/api/v1/profile", token!, {
        method: "PATCH",
        body: JSON.stringify({ tech_stack: data.tech_stack ?? [] }),
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
  };

  // ── Render ─────────────────────────────────────────────────

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div className={styles.section}>
        {renderTagBox()}
        {renderCategories()}
        {renderCustomTool()}
      </div>
      {serverError && <p className="mt-4 text-sm text-red-600">{serverError}</p>}
      {renderNavigation()}
    </form>
  );
}
