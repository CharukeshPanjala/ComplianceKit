import type { DocumentType, EvidenceDocument } from "@/types/evidence";

const POLICY_BASE = process.env.NEXT_PUBLIC_POLICY_URL ?? "http://localhost:8001";

export async function uploadEvidence(
  token: string,
  documentType: DocumentType,
  file: File,
): Promise<EvidenceDocument> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${POLICY_BASE}/api/v1/evidence/${documentType}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(
      (err as { detail?: string }).detail ?? `Upload failed: ${res.status}`,
    );
  }

  return res.json();
}

export async function listEvidence(
  token: string,
): Promise<{ documents: EvidenceDocument[] }> {
  const res = await fetch(`${POLICY_BASE}/api/v1/evidence`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to load evidence documents");
  return res.json();
}

export async function getEvidenceByType(
  token: string,
  documentType: DocumentType,
): Promise<EvidenceDocument> {
  const res = await fetch(`${POLICY_BASE}/api/v1/evidence/${documentType}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`No evidence found for ${documentType}`);
  return res.json();
}
