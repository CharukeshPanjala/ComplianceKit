"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { getAssessment } from "@/lib/assessmentApi";
import { assessmentKeys } from "./useTriggerAssessment";

export function useAssessment(assessmentId: string | null, poll = false) {
  const { getToken } = useAuth();

  return useQuery({
    queryKey: assessmentKeys.detail(assessmentId ?? ""),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return getAssessment(token, assessmentId!);
    },
    enabled: !!assessmentId,
    // Poll every 3s when assessment is pending/running
    refetchInterval: poll ? 3000 : false,
    refetchIntervalInBackground: false, // pause polling when tab not focused
    staleTime: poll ? 0 : 1000 * 30,
  });
}
