"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { getAssessmentHistory } from "@/lib/assessmentApi";
import { assessmentKeys } from "./useTriggerAssessment";
import type { RegulationName } from "@/types/assessment";

export function useAssessmentHistory(regulation?: RegulationName, limit = 10) {
  const { getToken } = useAuth();

  return useQuery({
    queryKey: assessmentKeys.history(regulation),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return getAssessmentHistory(token, regulation, limit);
    },
    staleTime: 1000 * 60, // 1 minute — history doesn't change often
  });
}
