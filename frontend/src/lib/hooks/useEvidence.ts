"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { uploadEvidence, listEvidence, getEvidenceByType } from "@/lib/evidenceApi";
import type { DocumentType } from "@/types/evidence";

export const evidenceKeys = {
  all: ["evidence"] as const,
  list: () => [...evidenceKeys.all, "list"] as const,
  byType: (type: DocumentType) => [...evidenceKeys.all, "type", type] as const,
};

export const useEvidenceList = () => {
  const { getToken } = useAuth();
  return useQuery({
    queryKey: evidenceKeys.list(),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return listEvidence(token);
    },
    staleTime: 1000 * 30,
  });
};

export const useEvidenceByType = (documentType: DocumentType) => {
  const { getToken } = useAuth();
  return useQuery({
    queryKey: evidenceKeys.byType(documentType),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return getEvidenceByType(token, documentType);
    },
    staleTime: 1000 * 30,
    retry: false,
  });
};

export const useUploadEvidence = () => {
  const { getToken } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      documentType,
      file,
    }: {
      documentType: DocumentType;
      file: File;
    }) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return uploadEvidence(token, documentType, file);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: evidenceKeys.all }),
  });
};
