"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { getLatestAssessments } from "@/lib/assessmentApi";
import { assessmentKeys } from "./useTriggerAssessment";

export function useLatestAssessments() {
  const { getToken } = useAuth();

  return useQuery({
    queryKey: assessmentKeys.latest(),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return getLatestAssessments(token);
    },
    staleTime: 1000 * 10,
    refetchInterval: (query) => {
      const assessments = query.state.data;
      if (!assessments) return false;
      const anyRunning = assessments.some(
        (a) => a.status === "pending" || a.status === "running"
      );
      return anyRunning ? 3000 : false;
    },
  });
}
