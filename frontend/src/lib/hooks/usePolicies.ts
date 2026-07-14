// WHAT: TanStack Query hooks for policies | CHANGE: new file | WHY: COM-176 — UI data layer for policy library, generation, status and exports
"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import {
  listPolicies, getPolicy, generatePolicy, updatePolicyStatus, updatePolicyContent,
  exportPolicyPdf, exportPolicyDocx,
  type PolicyGenerateRequest, type PolicyStatus, type PolicyType,
} from "@/lib/policiesApi";

// ── Query keys ────────────────────────────────────────────────────────────────

export const policyKeys = {
  all: ["policies"] as const,
  list: () => [...policyKeys.all, "list"] as const,
  detail: (policyId: string) => [...policyKeys.all, "detail", policyId] as const,
};

// ── usePoliciesList ───────────────────────────────────────────────────────────

export const usePoliciesList = () => {
  const { getToken } = useAuth();
  return useQuery({
    queryKey: policyKeys.list(),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return listPolicies(token);
    },
    staleTime: 1000 * 30,
  });
};

// ── usePolicy ─────────────────────────────────────────────────────────────────

export const usePolicy = (policyId: string | undefined) => {
  const { getToken } = useAuth();
  return useQuery({
    queryKey: policyKeys.detail(policyId ?? ""),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return getPolicy(token, policyId as string);
    },
    enabled: !!policyId,
    staleTime: 1000 * 30,
  });
};

// ── useGeneratePolicy ─────────────────────────────────────────────────────────

export const useGeneratePolicy = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: PolicyGenerateRequest) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return generatePolicy(token, body);
    },
    onSuccess: (policy) => {
      qc.invalidateQueries({ queryKey: policyKeys.list() });
      qc.invalidateQueries({ queryKey: policyKeys.detail(policy.policy_id) });
    },
  });
};

// ── useUpdatePolicyStatus ─────────────────────────────────────────────────────

export const useUpdatePolicyStatus = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ policyId, status }: { policyId: string; status: PolicyStatus }) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return updatePolicyStatus(token, policyId, status);
    },
    onSuccess: (policy) => {
      qc.invalidateQueries({ queryKey: policyKeys.list() });
      qc.invalidateQueries({ queryKey: policyKeys.detail(policy.policy_id) });
    },
  });
};

// ── useUpdatePolicyContent ────────────────────────────────────────────────────

export const useUpdatePolicyContent = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ policyId, content }: { policyId: string; content: string }) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return updatePolicyContent(token, policyId, content);
    },
    onSuccess: (policy) => {
      qc.invalidateQueries({ queryKey: policyKeys.list() });
      qc.invalidateQueries({ queryKey: policyKeys.detail(policy.policy_id) });
    },
  });
};

// ── useExportPolicyPdf ────────────────────────────────────────────────────────

export const useExportPolicyPdf = () => {
  const { getToken } = useAuth();
  return useMutation({
    mutationFn: async ({ policyId, policyType }: { policyId: string; policyType: PolicyType }) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return exportPolicyPdf(token, policyId, policyType);
    },
  });
};

// ── useExportPolicyDocx ───────────────────────────────────────────────────────

export const useExportPolicyDocx = () => {
  const { getToken } = useAuth();
  return useMutation({
    mutationFn: async ({ policyId, policyType }: { policyId: string; policyType: PolicyType }) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return exportPolicyDocx(token, policyId, policyType);
    },
  });
};
