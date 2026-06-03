"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { getAssessmentStats } from "@/lib/assessmentApi";
import { assessmentKeys } from "./useTriggerAssessment";

export const useAssessmentStats = (assessmentId: string | null) => {
  const { getToken } = useAuth();

  return useQuery({
    queryKey: assessmentKeys.stats(assessmentId ?? ""),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return getAssessmentStats(token, assessmentId!);
    },
    enabled: !!assessmentId,
    staleTime: 1000 * 60,
  });
};
