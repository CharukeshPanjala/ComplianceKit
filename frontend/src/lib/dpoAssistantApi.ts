const POLICY_BASE = process.env.NEXT_PUBLIC_POLICY_URL ?? "http://localhost:8001";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface Art28Clause {
  id: string;
  label: string;
  status: "covered" | "partial" | "missing" | "unknown";
  note: string;
}

export interface ContractAnalysisResult {
  clauses: Art28Clause[];
  overall_score: number;
  summary: string;
}

// ── Streaming chat ────────────────────────────────────────────────────────────

export async function streamChat(
  token: string,
  messages: ChatMessage[],
  regulation: string | null,
  onChunk: (text: string) => void,
  onError: (msg: string) => void,
  onDone: () => void,
): Promise<void> {
  let res: Response;
  try {
    res = await fetch(`${POLICY_BASE}/api/v1/dpo-assistant/chat`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ messages, regulation: regulation ?? null }),
    });
  } catch {
    onError("Connection failed. Is the policy engine running?");
    onDone();
    return;
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    onError((err as { detail?: string }).detail ?? `Request failed: ${res.status}`);
    onDone();
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) { onDone(); return; }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const payload = line.slice(6).trim();
      if (payload === "[DONE]") { onDone(); return; }
      try {
        const data = JSON.parse(payload) as { text?: string; error?: string };
        if (data.error) { onError(data.error); }
        else if (data.text) { onChunk(data.text); }
      } catch {
        // ignore malformed chunk
      }
    }
  }

  onDone();
}

// ── Contract analyser ─────────────────────────────────────────────────────────

export async function analyseContract(
  token: string,
  file: File,
): Promise<ContractAnalysisResult> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${POLICY_BASE}/api/v1/dpo-assistant/analyse-contract`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? `Analysis failed: ${res.status}`);
  }

  return res.json() as Promise<ContractAnalysisResult>;
}
