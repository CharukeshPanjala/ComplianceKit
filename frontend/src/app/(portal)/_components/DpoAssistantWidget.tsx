"use client";

import { useState, useRef, useEffect } from "react";
import { useDpoChat, useDpaAnalyser } from "@/lib/hooks/useDpoChat";
import type { ContractAnalysisResult } from "@/lib/dpoAssistantApi";

// ── Constants ─────────────────────────────────────────────────────────────────

const REGULATION_OPTIONS = [
  { value: null, label: "All regulations" },
  { value: "gdpr", label: "GDPR" },
  { value: "nis2", label: "NIS2" },
  { value: "eu_ai_act", label: "EU AI Act" },
];

const STARTER_QUESTIONS = [
  "Do I need to appoint a DPO?",
  "What must a privacy notice include under Art. 13?",
  "When must I notify the DPA of a breach?",
  "What are the conditions for legitimate interest?",
];

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  // Floating toggle button
  toggleBtn: "fixed bottom-6 right-6 z-50 w-13 h-13 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-200 hover:scale-105 active:scale-95",
  toggleBtnOpen: "fixed bottom-6 right-6 z-50 w-13 h-13 bg-gray-700 hover:bg-gray-800 text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-200",

  // Panel
  panel: "fixed bottom-24 right-6 z-50 w-96 h-[600px] bg-white rounded-2xl shadow-2xl border border-gray-100 flex flex-col overflow-hidden transition-all duration-200 origin-bottom-right",

  // Header
  header: "flex items-center gap-2 px-4 py-3 bg-navy border-b border-white/10 flex-shrink-0",
  headerIcon: "w-7 h-7 bg-amber-500 rounded-lg flex items-center justify-center text-white text-xs font-bold flex-shrink-0",
  headerTitle: "text-sm font-semibold text-white flex-1",
  closeBtn: "p-1 rounded hover:bg-white/10 transition-colors text-white/70 hover:text-white",

  // Tabs
  tabs: "flex border-b border-gray-100 flex-shrink-0",
  tab: "flex-1 px-3 py-2 text-xs font-medium transition-colors",
  tabActive: "text-blue-600 border-b-2 border-blue-600 bg-blue-50/50",
  tabInactive: "text-gray-500 hover:text-gray-700",

  // Chat
  messages: "flex-1 overflow-y-auto p-4 space-y-3",
  userMsg: "flex justify-end",
  userBubble: "max-w-[80%] px-3 py-2 bg-blue-600 text-white text-sm rounded-2xl rounded-br-sm",
  assistantMsg: "flex justify-start",
  assistantBubble: "max-w-[85%] px-3 py-2 bg-gray-100 text-gray-800 text-sm rounded-2xl rounded-bl-sm leading-relaxed",
  streamingDot: "inline-flex gap-1 items-center py-1",
  dot: "w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce",
  errorBubble: "max-w-[85%] px-3 py-2 bg-red-50 border border-red-200 text-red-700 text-xs rounded-2xl",
  starterGrid: "grid grid-cols-1 gap-2 mt-2",
  starterBtn: "text-left px-3 py-2 text-xs text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-xl border border-blue-100 transition-colors",

  // Input
  inputArea: "flex-shrink-0 border-t border-gray-100 p-3",
  inputRow: "flex items-end gap-2",
  regulationSelect: "text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white text-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500 flex-shrink-0",
  textarea: "flex-1 px-3 py-2 text-sm border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent max-h-24 leading-snug",
  sendBtn: "flex-shrink-0 w-8 h-8 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white rounded-xl flex items-center justify-center transition-colors",

  // DPA Analyser
  analyserBody: "flex-1 overflow-y-auto p-4",
  dropzone: "border-2 border-dashed border-gray-200 rounded-xl p-6 text-center hover:border-blue-300 hover:bg-blue-50/30 transition-colors cursor-pointer",
  dropzoneLabel: "text-sm text-gray-500 mt-2",
  fileInput: "hidden",
  analysingText: "text-sm text-gray-500 text-center py-8 animate-pulse",
  resultScore: "text-center py-3",
  scoreNum: "text-3xl font-bold",
  scoreLabel: "text-xs text-gray-400 mt-0.5",
  summary: "text-xs text-gray-600 mb-4 leading-relaxed",
  clauseRow: "flex items-start gap-2 py-2 border-b border-gray-50 last:border-0",
  clauseLabel: "flex-1 text-xs text-gray-700 leading-snug",
  clauseNote: "text-xs text-gray-400 mt-0.5",
  clauseStatus: {
    covered: "flex-shrink-0 w-4 h-4 rounded-full bg-green-100 text-green-600 flex items-center justify-center",
    partial: "flex-shrink-0 w-4 h-4 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center",
    missing: "flex-shrink-0 w-4 h-4 rounded-full bg-red-100 text-red-600 flex items-center justify-center",
    unknown: "flex-shrink-0 w-4 h-4 rounded-full bg-gray-100 text-gray-400 flex items-center justify-center",
  },
};

// ── Sub-components ────────────────────────────────────────────────────────────

const ChatIcon = () => (
  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
  </svg>
);

const CloseIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const SendIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
  </svg>
);

const UploadIcon = () => (
  <svg className="w-8 h-8 text-gray-300 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
  </svg>
);

// ── Streaming dots ────────────────────────────────────────────────────────────

const StreamingDots = () => (
  <span className={styles.streamingDot}>
    <span className={styles.dot} style={{ animationDelay: "0ms" }} />
    <span className={styles.dot} style={{ animationDelay: "150ms" }} />
    <span className={styles.dot} style={{ animationDelay: "300ms" }} />
  </span>
);

// ── Analysis results ──────────────────────────────────────────────────────────

const StatusIcon = ({ status }: { status: string }) => {
  if (status === "covered") return <span className={styles.clauseStatus.covered}>✓</span>;
  if (status === "partial") return <span className={styles.clauseStatus.partial}>~</span>;
  if (status === "missing") return <span className={styles.clauseStatus.missing}>✗</span>;
  return <span className={styles.clauseStatus.unknown}>?</span>;
};

const AnalysisResults = ({ result }: { result: ContractAnalysisResult }) => {
  const scoreColor = result.overall_score >= 80 ? "text-green-600" : result.overall_score >= 50 ? "text-amber-600" : "text-red-600";
  return (
    <div>
      <div className={styles.resultScore}>
        <div className={`${styles.scoreNum} ${scoreColor}`}>{result.overall_score}%</div>
        <div className={styles.scoreLabel}>Art. 28 compliance score</div>
      </div>
      <p className={styles.summary}>{result.summary}</p>
      {result.clauses.map((c) => (
        <div key={c.id} className={styles.clauseRow}>
          <StatusIcon status={c.status} />
          <div>
            <div className={styles.clauseLabel}>{c.label}</div>
            {c.note && <div className={styles.clauseNote}>{c.note}</div>}
          </div>
        </div>
      ))}
    </div>
  );
};

// ── Main widget ───────────────────────────────────────────────────────────────

export const DpoAssistantWidget = () => {
  // ── State ─────────────────────────────────────────────────────────────────
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<"chat" | "dpa">("chat");
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const chat = useDpoChat();
  const analyser = useDpaAnalyser();

  // ── Effects ───────────────────────────────────────────────────────────────

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat.messages]);

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleToggle = () => setOpen((o) => !o);
  const handleClose = () => setOpen(false);

  const handleSend = async () => {
    if (!input.trim() || chat.isStreaming) return;
    const content = input;
    setInput("");
    await chat.sendMessage(content);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleStarter = (q: string) => chat.sendMessage(q);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) analyser.analyseFile(file);
  };

  const handleDropzonClick = () => fileInputRef.current?.click();

  // ── Render helpers ────────────────────────────────────────────────────────

  const renderChatMessages = () => (
    <div className={styles.messages}>
      {chat.messages.length === 0 && (
        <div className="text-center pt-4">
          <p className="text-xs text-gray-400 mb-4">Ask me anything about GDPR, NIS2, or EU AI Act</p>
          <div className={styles.starterGrid}>
            {STARTER_QUESTIONS.map((q) => (
              <button key={q} className={styles.starterBtn} onClick={() => handleStarter(q)}>
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {chat.messages.map((msg, i) => {
        if (msg.role === "user") {
          return (
            <div key={i} className={styles.userMsg}>
              <div className={styles.userBubble}>{msg.content}</div>
            </div>
          );
        }
        return (
          <div key={i} className={styles.assistantMsg}>
            <div className={styles.assistantBubble}>
              {msg.content === "" && chat.isStreaming && i === chat.messages.length - 1
                ? <StreamingDots />
                : msg.content}
            </div>
          </div>
        );
      })}

      {chat.error && (
        <div className={styles.assistantMsg}>
          <div className={styles.errorBubble}>{chat.error}</div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );

  const renderChatInput = () => (
    <div className={styles.inputArea}>
      <div className={styles.inputRow}>
        <select
          className={styles.regulationSelect}
          value={chat.regulation ?? ""}
          onChange={(e) => chat.setRegulation(e.target.value || null)}
        >
          {REGULATION_OPTIONS.map((o) => (
            <option key={String(o.value)} value={o.value ?? ""}>{o.label}</option>
          ))}
        </select>
        <textarea
          className={styles.textarea}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about GDPR, NIS2, EU AI Act..."
          disabled={chat.isStreaming}
        />
        <button
          className={styles.sendBtn}
          onClick={handleSend}
          disabled={!input.trim() || chat.isStreaming}
        >
          <SendIcon />
        </button>
      </div>
    </div>
  );

  const renderDpaTab = () => (
    <div className={styles.analyserBody}>
      {!analyser.result && !analyser.isAnalysing && (
        <div>
          <p className="text-xs text-gray-500 mb-4 leading-relaxed">
            Upload your Data Processing Agreement to check it against GDPR Art. 28 mandatory clauses.
          </p>
          <div className={styles.dropzone} onClick={handleDropzonClick}>
            <UploadIcon />
            <div className={styles.dropzoneLabel}>Click to upload PDF</div>
            <div className="text-xs text-gray-400 mt-1">Max 10MB · Text-based PDFs only</div>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            className={styles.fileInput}
            onChange={handleFileChange}
          />
          {analyser.error && (
            <div className="mt-3 px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700">
              {analyser.error}
            </div>
          )}
        </div>
      )}

      {analyser.isAnalysing && (
        <div className={styles.analysingText}>Analysing contract against Art. 28...</div>
      )}

      {analyser.result && !analyser.isAnalysing && (
        <div>
          <div className="flex justify-between items-center mb-3">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Results</span>
            <button
              className="text-xs text-blue-600 hover:underline"
              onClick={analyser.clearResult}
            >
              Analyse another
            </button>
          </div>
          <AnalysisResults result={analyser.result} />
        </div>
      )}
    </div>
  );

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <>
      {open && (
        <div className={styles.panel}>
          <div className={styles.header}>
            <div className={styles.headerIcon}>D</div>
            <span className={styles.headerTitle}>DPO Assistant</span>
            {chat.messages.length > 0 && tab === "chat" && (
              <button
                className="text-xs text-white/50 hover:text-white mr-2 transition-colors"
                onClick={chat.clearMessages}
              >
                Clear
              </button>
            )}
            <button className={styles.closeBtn} onClick={handleClose}>
              <CloseIcon />
            </button>
          </div>

          <div className={styles.tabs}>
            <button
              className={`${styles.tab} ${tab === "chat" ? styles.tabActive : styles.tabInactive}`}
              onClick={() => setTab("chat")}
            >
              Chat
            </button>
            <button
              className={`${styles.tab} ${tab === "dpa" ? styles.tabActive : styles.tabInactive}`}
              onClick={() => setTab("dpa")}
            >
              Analyse DPA
            </button>
          </div>

          {tab === "chat" ? (
            <>
              {renderChatMessages()}
              {renderChatInput()}
            </>
          ) : (
            renderDpaTab()
          )}
        </div>
      )}

      <button
        className={open ? styles.toggleBtnOpen : styles.toggleBtn}
        onClick={handleToggle}
        title="DPO Assistant"
      >
        {open ? <CloseIcon /> : <ChatIcon />}
      </button>
    </>
  );
};
