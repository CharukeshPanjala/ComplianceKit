"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { triggerAssessment, triggerAllApplicableAssessments } from "@/lib/assessmentApi";
import type { RegulationName } from "@/types/assessment";

// ── Query keys ────────────────────────────────────────────────────────────────

export const assessmentKeys = {
  all: ["assessments"] as const,
  latest: () => [...assessmentKeys.all, "latest"] as const,
  detail: (id: string) => [...assessmentKeys.all, "detail", id] as const,
  gaps: (id: string, filters?: object) => [...assessmentKeys.all, "gaps", id, filters] as const,
  history: (regulation?: string) => [...assessmentKeys.all, "history", regulation] as const,
  stats: (id: string) => [...assessmentKeys.all, "stats", id] as const,
};

// ── Trigger single regulation ─────────────────────────────────────────────────

export function useTriggerAssessment() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (regulation: RegulationName) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return triggerAssessment(token, regulation);
    },
    onSuccess: () => {
      // Invalidate latest assessments so cards refresh
      queryClient.invalidateQueries({ queryKey: assessmentKeys.latest() });
    },
  });
}

// ── Trigger all applicable regulations ───────────────────────────────────────

export function useTriggerAllAssessments() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (profile: {
      nis2_data: Record<string, unknown> | null;
      ai_act_data: Record<string, unknown> | null;
    }) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return triggerAllApplicableAssessments(token, profile);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: assessmentKeys.latest() });
    },
  });
}
