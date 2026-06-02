"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { getGaps } from "@/lib/assessmentApi";
import { assessmentKeys } from "./useTriggerAssessment";

interface GapFilters {
  status?: string;
  severity?: string;
  category?: string;
  remediation_priority?: string;
  resolved?: boolean;
  limit?: number;
  offset?: number;
}

export function useGaps(assessmentId: string | null, filters?: GapFilters) {
  const { getToken } = useAuth();

  return useQuery({
    queryKey: assessmentKeys.gaps(assessmentId ?? "", filters),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return getGaps(token, assessmentId!, filters);
    },
    enabled: !!assessmentId,
    staleTime: 1000 * 30,
    placeholderData: (prev) => prev, // keep previous data while filters change
  });
}
