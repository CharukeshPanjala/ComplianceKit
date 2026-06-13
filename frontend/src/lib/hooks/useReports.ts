// WHAT: TanStack Query hook for compliance report downloads | CHANGE: new file | WHY: COM-177 — one-click PDF/DOCX compliance report from the dashboard
"use client";

import { useMutation } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { downloadComplianceReport, type ReportFormat } from "@/lib/reportsApi";

export const useDownloadComplianceReport = () => {
  const { getToken } = useAuth();
  return useMutation({
    mutationFn: async (format: ReportFormat) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return downloadComplianceReport(token, format);
    },
  });
};
