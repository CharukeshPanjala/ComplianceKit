"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import {
  listBreaches, createBreach, updateBreach, deleteBreach, draftNotification,
  type BreachCreateRequest, type BreachUpdateRequest,
} from "@/lib/breachApi";

export const breachKeys = {
  all: ["breaches"] as const,
  list: () => [...breachKeys.all, "list"] as const,
};

export const useBreachList = () => {
  const { getToken } = useAuth();
  return useQuery({
    queryKey: breachKeys.list(),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return listBreaches(token);
    },
    staleTime: 1000 * 30,
  });
};

export const useCreateBreach = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: BreachCreateRequest) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return createBreach(token, body);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: breachKeys.all }),
  });
};

export const useUpdateBreach = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ breachId, body }: { breachId: string; body: BreachUpdateRequest }) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return updateBreach(token, breachId, body);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: breachKeys.all }),
  });
};

export const useDeleteBreach = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (breachId: string) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return deleteBreach(token, breachId);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: breachKeys.all }),
  });
};

export const useDraftNotification = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (breachId: string) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return draftNotification(token, breachId);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: breachKeys.all }),
  });
};
