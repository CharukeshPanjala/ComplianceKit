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
    staleTime: 1000 * 10, // 10 seconds — refresh frequently
  });
}
