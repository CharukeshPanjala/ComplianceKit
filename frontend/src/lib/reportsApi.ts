// WHAT: Compliance report API client | CHANGE: new file | WHY: COM-177 — typed fetch call to policy-engine /api/v1/reports/compliance

const POLICY_BASE = process.env.NEXT_PUBLIC_POLICY_URL ?? "http://localhost:8001";

export type ReportFormat = "pdf" | "docx";

export class ReportApiError extends Error {
  constructor(
    message: string,
    public status?: number
  ) {
    super(message);
    this.name = "ReportApiError";
  }
}

export async function downloadComplianceReport(token: string, format: ReportFormat): Promise<void> {
  const res = await fetch(`${POLICY_BASE}/api/v1/reports/compliance?format=${format}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new ReportApiError(
      (err as { detail?: string }).detail ?? "Failed to generate compliance report",
      res.status
    );
  }

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `compliance_report.${format}`;
  a.click();
  URL.revokeObjectURL(url);
}
