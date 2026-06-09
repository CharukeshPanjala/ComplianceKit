// WHAT: TanStack Query hooks for ROPA | CHANGE: new file | WHY: COM-173 — UI data layer
"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import {
  listRopa, generateRopa, updateRopa, updateRopaStatus,
  deleteRopa, exportRopaPdf, createRopa,
  type RopaEntry, type RopaStatus, type RopaUpdateRequest,
} from "@/lib/ropaApi";

// ── Query keys ────────────────────────────────────────────────────────────────

export const ropaKeys = {
  all: ["ropa"] as const,
  list: () => [...ropaKeys.all, "list"] as const,
};

// ── useRopaList ───────────────────────────────────────────────────────────────

export const useRopaList = () => {
  const { getToken } = useAuth();
  return useQuery({
    queryKey: ropaKeys.list(),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return listRopa(token);
    },
    staleTime: 1000 * 30,
  });
};

// ── useGenerateRopa ───────────────────────────────────────────────────────────

export const useGenerateRopa = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return generateRopa(token);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ropaKeys.list() }),
  });
};

// ── useCreateRopa ─────────────────────────────────────────────────────────────

export const useCreateRopa = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: Partial<RopaEntry>) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return createRopa(token, body);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ropaKeys.list() }),
  });
};

// ── useUpdateRopa ─────────────────────────────────────────────────────────────

export const useUpdateRopa = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ ropaId, body }: { ropaId: string; body: RopaUpdateRequest }) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return updateRopa(token, ropaId, body);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ropaKeys.list() }),
  });
};

// ── useUpdateRopaStatus ───────────────────────────────────────────────────────

export const useUpdateRopaStatus = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ ropaId, status }: { ropaId: string; status: RopaStatus }) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return updateRopaStatus(token, ropaId, status);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ropaKeys.list() }),
  });
};

// ── useDeleteRopa ─────────────────────────────────────────────────────────────

export const useDeleteRopa = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (ropaId: string) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return deleteRopa(token, ropaId);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ropaKeys.list() }),
  });
};

// ── useExportRopaPdf ──────────────────────────────────────────────────────────

export const useExportRopaPdf = () => {
  const { getToken } = useAuth();
  return useMutation({
    mutationFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return exportRopaPdf(token);
    },
  });
};
