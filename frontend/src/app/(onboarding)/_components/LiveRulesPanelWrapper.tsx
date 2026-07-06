"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { LiveRulesPanel } from "./LiveRulesPanel";

// ── Types ──────────────────────────────────────────────────
type RegulationType = "GDPR" | "NIS2" | "AI_ACT";

interface StoredRules {
  activeRuleIds: string[];
  regulation: RegulationType;
  trackProgress: { gdpr: number; nis2: number; aiAct: number };
}

// ── Constants ──────────────────────────────────────────────
const STEP_DEFAULTS: Record<string, StoredRules> = {
  "/onboarding/step-1": {
    activeRuleIds: [],
    regulation: "GDPR",
    trackProgress: { gdpr: 0, nis2: 0, aiAct: 0 },
  },
  "/onboarding/step-2": {
    activeRuleIds: [],
    regulation: "GDPR",
    trackProgress: { gdpr: 0, nis2: 0, aiAct: 0 },
  },
  "/onboarding/step-3": {
    activeRuleIds: ["Art.5", "Art.6", "Art.30"],
    regulation: "GDPR",
    trackProgress: { gdpr: 1, nis2: 0, aiAct: 0 },
  },
  "/onboarding/step-4": {
    activeRuleIds: ["Art.5", "Art.6", "Art.30", "Art.44", "Art.45", "Art.46"],
    regulation: "GDPR",
    trackProgress: { gdpr: 2, nis2: 0, aiAct: 0 },
  },
  "/onboarding/step-5": {
    activeRuleIds: ["Art.5", "Art.6", "Art.30", "Art.37"],
    regulation: "GDPR",
    trackProgress: { gdpr: 2, nis2: 0, aiAct: 0 },
  },
};

const DEFAULT_STATE: StoredRules = {
  activeRuleIds: [],
  regulation: "GDPR",
  trackProgress: { gdpr: 0, nis2: 0, aiAct: 0 },
};

const STORAGE_KEY = "ck_live_rules";

// ── Component ──────────────────────────────────────────────
export const LiveRulesPanelWrapper = () => {
  const pathname = usePathname();
  const [state, setState] = useState<StoredRules>(DEFAULT_STATE);

  // ── Handlers ────────────────────────────────────────────
  const handleStorage = () => {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (raw) {
        setState(JSON.parse(raw) as StoredRules);
        return;
      }
    } catch {
      // ignore parse errors
    }
    setState(STEP_DEFAULTS[pathname] ?? DEFAULT_STATE);
  };

  // ── Effects ─────────────────────────────────────────────
  useEffect(() => {
    handleStorage();
    window.addEventListener("storage", handleStorage);
    window.addEventListener("ck:rules-update", handleStorage);
    return () => {
      window.removeEventListener("storage", handleStorage);
      window.removeEventListener("ck:rules-update", handleStorage);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  // On step change, load step default if no sessionStorage value
  useEffect(() => {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) {
      setState(STEP_DEFAULTS[pathname] ?? DEFAULT_STATE);
    }
  }, [pathname]);

  return (
    <LiveRulesPanel
      activeRuleIds={state.activeRuleIds}
      regulation={state.regulation}
      trackProgress={state.trackProgress}
    />
  );
};
