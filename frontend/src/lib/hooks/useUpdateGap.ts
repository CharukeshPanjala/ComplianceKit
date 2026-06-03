"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { updateGap } from "@/lib/assessmentApi";
import { assessmentKeys } from "./useTriggerAssessment";
import type { Gap, UpdateGapRequest } from "@/types/assessment";

export function useUpdateGap(assessmentId: string) {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ gapId, body }: { gapId: string; body: UpdateGapRequest }) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return updateGap(token, assessmentId, gapId, body);
    },

    // ── Optimistic update ──────────────────────────────────────────────────
    onMutate: async ({ gapId, body }) => {
      // Cancel outgoing refetches to avoid overwriting optimistic update
      await queryClient.cancelQueries({ queryKey: assessmentKeys.gaps(assessmentId) });

      // Snapshot previous gaps for rollback
      const previousGaps = queryClient.getQueriesData({
        queryKey: assessmentKeys.gaps(assessmentId),
      });

      // Optimistically update all gap query variants in cache
      queryClient.setQueriesData(
        { queryKey: assessmentKeys.gaps(assessmentId) },
        (old: { gaps: Gap[]; total: number } | undefined) => {
          if (!old) return old;
          return {
            ...old,
            gaps: old.gaps.map((g) =>
              g.gap_id === gapId
                ? {
                    ...g,
                    resolved: body.resolved ?? g.resolved,
                    notes: body.notes ?? g.notes,
                    assigned_to: body.assigned_to ?? g.assigned_to,
                    due_date: body.due_date ?? g.due_date,
                    resolved_at: body.resolved ? new Date().toISOString() : g.resolved_at,
                  }
                : g
            ),
          };
        }
      );

      return { previousGaps };
    },

    // ── Rollback on error ──────────────────────────────────────────────────
    onError: (_err, _vars, context) => {
      if (context?.previousGaps) {
        context.previousGaps.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }
    },

    // ── Invalidate after success ───────────────────────────────────────────
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: assessmentKeys.gaps(assessmentId) });
    },
  });
}
