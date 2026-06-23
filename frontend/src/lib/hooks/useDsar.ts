"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import {
  listDsars, createDsar, updateDsar, deleteDsar,
  type DsarCreateRequest, type DsarUpdateRequest,
} from "@/lib/dsarApi";

export const dsarKeys = {
  all: ["dsar"] as const,
  list: () => [...dsarKeys.all, "list"] as const,
};

export const useDsarList = () => {
  const { getToken } = useAuth();
  return useQuery({
    queryKey: dsarKeys.list(),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return listDsars(token);
    },
    staleTime: 1000 * 30,
  });
};

export const useCreateDsar = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: DsarCreateRequest) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return createDsar(token, body);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: dsarKeys.all }),
  });
};

export const useUpdateDsar = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ dsarId, body }: { dsarId: string; body: DsarUpdateRequest }) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return updateDsar(token, dsarId, body);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: dsarKeys.all }),
  });
};

export const useDeleteDsar = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (dsarId: string) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return deleteDsar(token, dsarId);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: dsarKeys.all }),
  });
};
