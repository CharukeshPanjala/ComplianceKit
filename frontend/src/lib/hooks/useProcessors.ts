"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import {
  listProcessors,
  generateProcessors,
  updateProcessor,
  deleteProcessor,
  type ProcessorListFilters,
  type ProcessorUpdateRequest,
} from "@/lib/processorsApi";

// ── Query keys ────────────────────────────────────────────────────────────────

export const processorKeys = {
  all: ["processors"] as const,
  list: (filters?: ProcessorListFilters) => [...processorKeys.all, "list", filters] as const,
};

// ── useProcessorList ──────────────────────────────────────────────────────────

export const useProcessorList = (filters?: ProcessorListFilters) => {
  const { getToken } = useAuth();
  return useQuery({
    queryKey: processorKeys.list(filters),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return listProcessors(token, filters);
    },
    staleTime: 1000 * 30,
  });
};

// ── useGenerateProcessors ─────────────────────────────────────────────────────

export const useGenerateProcessors = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return generateProcessors(token);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: processorKeys.all }),
  });
};

// ── useUpdateProcessor ────────────────────────────────────────────────────────

export const useUpdateProcessor = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ processorId, body }: { processorId: string; body: ProcessorUpdateRequest }) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return updateProcessor(token, processorId, body);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: processorKeys.all }),
  });
};

// ── useDeleteProcessor ────────────────────────────────────────────────────────

export const useDeleteProcessor = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (processorId: string) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return deleteProcessor(token, processorId);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: processorKeys.all }),
  });
};
