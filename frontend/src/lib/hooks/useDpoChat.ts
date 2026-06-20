"use client";

import { useState, useCallback } from "react";
import { useAuth } from "@clerk/nextjs";
import { streamChat, analyseContract, type ChatMessage, type ContractAnalysisResult } from "@/lib/dpoAssistantApi";

export type { ChatMessage };

export interface UseDpoChatReturn {
  messages: ChatMessage[];
  isStreaming: boolean;
  error: string | null;
  regulation: string | null;
  setRegulation: (r: string | null) => void;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
}

export const useDpoChat = (): UseDpoChatReturn => {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [regulation, setRegulation] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    if (isStreaming || !content.trim()) return;

    const userMsg: ChatMessage = { role: "user", content: content.trim() };
    const history = [...messages, userMsg];

    setMessages([...history, { role: "assistant", content: "" }]);
    setIsStreaming(true);
    setError(null);

    const token = await getToken();
    if (!token) {
      setError("Not authenticated");
      setIsStreaming(false);
      return;
    }

    await streamChat(
      token,
      history,
      regulation,
      (chunk) => {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          updated[updated.length - 1] = { ...last, content: last.content + chunk };
          return updated;
        });
      },
      (msg) => setError(msg),
      () => setIsStreaming(false),
    );
  }, [messages, isStreaming, regulation, getToken]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { messages, isStreaming, error, regulation, setRegulation, sendMessage, clearMessages };
};

export interface UseDpaAnalyserReturn {
  result: ContractAnalysisResult | null;
  isAnalysing: boolean;
  error: string | null;
  analyseFile: (file: File) => Promise<void>;
  clearResult: () => void;
}

export const useDpaAnalyser = (): UseDpaAnalyserReturn => {
  const { getToken } = useAuth();
  const [result, setResult] = useState<ContractAnalysisResult | null>(null);
  const [isAnalysing, setIsAnalysing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyseFile = useCallback(async (file: File) => {
    setIsAnalysing(true);
    setError(null);
    setResult(null);
    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      const res = await analyseContract(token, file);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setIsAnalysing(false);
    }
  }, [getToken]);

  const clearResult = useCallback(() => { setResult(null); setError(null); }, []);

  return { result, isAnalysing, error, analyseFile, clearResult };
};
