"use client";

import { useState } from "react";
import { LiveRulesPanel } from "./LiveRulesPanel";
import { TrackQuestion } from "./TrackQuestion";

// ── Types ──────────────────────────────────────────────────
type RegulationType = "GDPR" | "NIS2" | "AI_ACT";

interface Step3TracksProps {
  selectedRegulations: string[];
  onComplete: () => void;
}

interface Question {
  id: string;
  badge: string;
  articleRef: string;
  title: string;
  description: string;
  options: Array<{ value: string; label: string }>;
}

// ── Constants ───────────────────────────────────────────────
const GDPR_QUESTIONS: Question[] = [
  {
    id: "eu_residents",
    badge: "GDPR",
    articleRef: "Articles 3, 4",
    title: "Do you process personal data of EU residents?",
    description: "This includes collecting, storing, using, or sharing any data that can identify a person in the EU.",
    options: [{ value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "unsure", label: "Not sure" }],
  },
  {
    id: "special_categories",
    badge: "GDPR",
    articleRef: "Article 9",
    title: "Do you process special categories of personal data?",
    description: "Health data, biometric data, racial or ethnic origin, political opinions, religious beliefs, trade union membership, genetic data, or sexual orientation.",
    options: [{ value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "unsure", label: "Not sure" }],
  },
  {
    id: "automated_decisions",
    badge: "GDPR",
    articleRef: "Article 22",
    title: "Do you use automated decision-making or profiling?",
    description: "Decisions made solely by automated systems that have a significant effect on individuals (e.g., credit scoring, hiring algorithms).",
    options: [{ value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "unsure", label: "Not sure" }],
  },
  {
    id: "eea_transfers",
    badge: "GDPR",
    articleRef: "Articles 44-49",
    title: "Do you transfer personal data outside the EEA?",
    description: "Sending or accessing personal data from countries outside the European Economic Area, including via cloud services hosted outside the EU.",
    options: [{ value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "unsure", label: "Not sure" }],
  },
  {
    id: "large_scale",
    badge: "GDPR",
    articleRef: "Article 30",
    title: "Do you have 250+ employees or process data on a large scale?",
    description: "Large-scale processing means processing a large volume of data, affecting a large number of people, or covering a large geographic area.",
    options: [{ value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "unsure", label: "Not sure" }],
  },
];

const NIS2_QUESTIONS: Question[] = [
  {
    id: "critical_sector",
    badge: "NIS2",
    articleRef: "Article 3",
    title: "Is your organisation in a critical sector?",
    description: "Energy, transport, banking, financial markets, health, drinking water, wastewater, digital infrastructure, managed services, public administration, or space.",
    options: [{ value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "unsure", label: "Not sure" }],
  },
  {
    id: "management_approval",
    badge: "NIS2",
    articleRef: "Article 20",
    title: "Has management formally approved your cybersecurity measures?",
    description: "Management bodies must approve the cybersecurity risk management measures and are personally liable for compliance.",
    options: [{ value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "working_on_it", label: "Working on it" }],
  },
  {
    id: "mfa_enforced",
    badge: "NIS2",
    articleRef: "Article 21",
    title: "Do you have multi-factor authentication (MFA) enforced?",
    description: "MFA must be enabled for all access to critical systems and sensitive data as part of NIS2 cybersecurity requirements.",
    options: [{ value: "yes", label: "Yes, for all systems" }, { value: "partial", label: "Partially" }, { value: "no", label: "Not yet" }],
  },
  {
    id: "incident_response",
    badge: "NIS2",
    articleRef: "Articles 20, 23",
    title: "Do you have a documented incident response plan?",
    description: "A formal plan for detecting, responding to, and recovering from cybersecurity incidents, including notification procedures.",
    options: [{ value: "yes", label: "Yes, documented" }, { value: "informal", label: "Informal only" }, { value: "no", label: "Not yet" }],
  },
  {
    id: "info_sharing",
    badge: "NIS2",
    articleRef: "Article 29",
    title: "Do you participate in any information-sharing arrangements?",
    description: "Sharing cybersecurity threat intelligence with sector peers, ISACs, or government bodies like ENISA.",
    options: [{ value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "planning", label: "Planning to" }],
  },
];

const AI_ACT_QUESTIONS: Question[] = [
  {
    id: "ai_role",
    badge: "AI Act",
    articleRef: "Articles 3, 6",
    title: "What is your role in relation to AI systems?",
    description: "Your obligations under the EU AI Act depend on whether you develop, deploy, or use AI systems.",
    options: [
      { value: "provider", label: "Provider -- we develop or sell AI systems" },
      { value: "deployer", label: "Deployer -- we use AI systems in our products/services" },
      { value: "both", label: "Both provider and deployer" },
      { value: "none", label: "We don't use AI" },
    ],
  },
  {
    id: "high_risk",
    badge: "AI Act",
    articleRef: "Article 6, Annex III",
    title: "Do you use AI systems in high-risk categories?",
    description: "Hiring and recruitment, credit scoring, biometric identification, law enforcement, education, access to essential services, or critical infrastructure.",
    options: [{ value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "unsure", label: "Not sure" }],
  },
  {
    id: "gpai",
    badge: "AI Act",
    articleRef: "Articles 51-55",
    title: "Do you use any general-purpose AI models (GPAI)?",
    description: "Models like GPT-4, Gemini, Claude, Llama, Mistral, or other foundation models accessed via API or self-hosted.",
    options: [{ value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "unsure", label: "Not sure" }],
  },
  {
    id: "chatbot_synthetic",
    badge: "AI Act",
    articleRef: "Article 50",
    title: "Do you deploy chatbots, generate synthetic content, or use emotion recognition?",
    description: "AI systems that interact with humans, generate text/image/audio/video, or infer emotional states require special transparency disclosures.",
    options: [{ value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "unsure", label: "Not sure" }],
  },
];

const QUESTIONS_BY_REG: Record<RegulationType, Question[]> = {
  GDPR: GDPR_QUESTIONS,
  NIS2: NIS2_QUESTIONS,
  AI_ACT: AI_ACT_QUESTIONS,
};

const ALWAYS_ACTIVE: Record<RegulationType, string[]> = {
  GDPR: ["Art.5", "Art.6"],
  NIS2: ["Art.18", "Art.23"],
  AI_ACT: [],
};

// ── Styles ──────────────────────────────────────────────────
const styles = {
  wrapper: "flex h-full min-h-screen",
  main: "flex-1 flex flex-col p-6 lg:p-8 overflow-y-auto",
  header: "mb-6",
  title: "text-xl font-bold text-[#0F172A]",
  subtitle: "text-sm text-[#64748B] mt-1",
  tabRow: "flex gap-1 mb-6 bg-[#F8FAFC] rounded-xl p-1 w-fit",
  tab: {
    base: "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
    active: "bg-white text-[#0F172A] shadow-sm font-semibold",
    inactive: "text-[#64748B] hover:text-[#334155]",
  },
  progressWrapper: "mb-6",
  progressLabel: "text-xs text-[#94A3B8] mb-1",
  progressTrack: "w-full h-1.5 bg-gray-200 rounded-full overflow-hidden",
  progressFill: "h-full bg-[#D97706] rounded-full transition-all duration-300",
  questionWrapper: "flex-1",
  buttonRow: "flex items-center justify-between mt-6",
  prevBtn: "px-4 py-2 text-sm font-medium text-[#64748B] border border-[#E2E8F0] rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-40",
  skipBtn: "px-4 py-2 text-sm font-medium text-[#64748B] hover:text-[#334155] transition-colors",
  nextBtn: "px-6 py-2.5 bg-[#D97706] text-white text-sm font-semibold rounded-lg hover:bg-[#B45309] transition-colors disabled:opacity-50",
  completeBtn: "px-6 py-2.5 bg-green-600 text-white text-sm font-semibold rounded-lg hover:bg-green-700 transition-colors",
};

// ── Helpers ──────────────────────────────────────────────────
const computeActiveRules = (
  answers: Record<string, string>,
  regulation: RegulationType
): string[] => {
  const active = [...ALWAYS_ACTIVE[regulation]];

  if (regulation === "GDPR") {
    if (answers.special_categories === "yes") active.push("Art.9", "Art.35");
    if (answers.automated_decisions === "yes") active.push("Art.22");
    if (answers.eea_transfers === "yes") active.push("Art.44", "Art.45", "Art.46", "Art.49");
    if (answers.large_scale === "yes") active.push("Art.30");
  }

  if (regulation === "NIS2") {
    if (answers.mfa_enforced === "no" || answers.mfa_enforced === "partial") active.push("Art.21");
    if (answers.incident_response !== "yes") active.push("Art.20");
    if (answers.info_sharing === "yes") active.push("Art.29");
  }

  if (regulation === "AI_ACT") {
    if (answers.ai_role === "provider" || answers.ai_role === "both")
      active.push("Art.6", "Art.9", "Art.10", "Art.11", "Art.12", "Art.13", "Art.14", "Art.15", "Art.17", "Art.43");
    if (answers.ai_role === "deployer" || answers.ai_role === "both")
      active.push("Art.26", "Art.52", "Art.86");
    if (answers.high_risk === "yes")
      active.push("Art.9", "Art.10", "Art.11", "Art.12", "Art.13", "Art.14", "Art.15", "Art.43");
    if (answers.gpai === "yes") active.push("Art.51", "Art.52", "Art.53", "Art.54", "Art.55");
    if (answers.chatbot_synthetic === "yes") active.push("Art.50");
  }

  return [...new Set(active)];
};

const REG_LABELS: Record<RegulationType, string> = {
  GDPR: "GDPR",
  NIS2: "NIS2",
  AI_ACT: "AI Act",
};

const ALL_REGS: RegulationType[] = ["GDPR", "NIS2", "AI_ACT"];
const REG_KEYS: Record<string, RegulationType> = {
  gdpr: "GDPR",
  nis2: "NIS2",
  eu_ai_act: "AI_ACT",
};

// ── Component ───────────────────────────────────────────────
export const Step3Tracks = ({ selectedRegulations, onComplete }: Step3TracksProps) => {
  const availableRegs = ALL_REGS.filter((r) =>
    selectedRegulations.some((sel) => REG_KEYS[sel] === r)
  );

  const [activeRegIndex, setActiveRegIndex] = useState(0);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [answeredCount, setAnsweredCount] = useState<Record<RegulationType, number>>({
    GDPR: 0,
    NIS2: 0,
    AI_ACT: 0,
  });

  const currentReg = availableRegs[activeRegIndex] ?? "GDPR";
  const currentQuestions = QUESTIONS_BY_REG[currentReg] ?? [];
  const currentQuestion = currentQuestions[questionIndex];
  const currentAnswerKey = `${currentReg}_${currentQuestion?.id}`;
  const currentAnswer = answers[currentAnswerKey] ?? null;

  const isLastQuestion = questionIndex === currentQuestions.length - 1;
  const isLastReg = activeRegIndex === availableRegs.length - 1;
  const isComplete = isLastQuestion && isLastReg;

  const activeRuleIds = computeActiveRules(
    Object.fromEntries(
      Object.entries(answers)
        .filter(([k]) => k.startsWith(currentReg))
        .map(([k, v]) => [k.replace(`${currentReg}_`, ""), v])
    ),
    currentReg
  );

  const gdprAnswered = Object.keys(answers).filter((k) => k.startsWith("GDPR")).length;
  const nis2Answered = Object.keys(answers).filter((k) => k.startsWith("NIS2")).length;
  const aiActAnswered = Object.keys(answers).filter((k) => k.startsWith("AI_ACT")).length;

  // ── Handlers ─────────────────────────────────────────────
  const handleAnswer = (value: string) => {
    setAnswers((prev) => ({ ...prev, [currentAnswerKey]: value }));
    setAnsweredCount((prev) => ({
      ...prev,
      [currentReg]: Math.max(prev[currentReg], questionIndex + 1),
    }));
  };

  const handleNext = () => {
    if (!isLastQuestion) {
      setQuestionIndex((i) => i + 1);
    } else if (!isLastReg) {
      setActiveRegIndex((i) => i + 1);
      setQuestionIndex(0);
    } else {
      onComplete();
    }
  };

  const handlePrev = () => {
    if (questionIndex > 0) {
      setQuestionIndex((i) => i - 1);
    } else if (activeRegIndex > 0) {
      setActiveRegIndex((i) => i - 1);
      const prevReg = availableRegs[activeRegIndex - 1];
      setQuestionIndex((QUESTIONS_BY_REG[prevReg]?.length ?? 1) - 1);
    }
  };

  const handleSkipTrack = () => {
    if (!isLastReg) {
      setActiveRegIndex((i) => i + 1);
      setQuestionIndex(0);
    } else {
      onComplete();
    }
  };

  const handleTabSwitch = (index: number) => {
    setActiveRegIndex(index);
    setQuestionIndex(0);
  };

  // ── Render helpers ────────────────────────────────────────
  const renderTabs = () => (
    <div className={styles.tabRow}>
      {availableRegs.map((reg, i) => (
        <button
          key={reg}
          onClick={() => handleTabSwitch(i)}
          className={`${styles.tab.base} ${i === activeRegIndex ? styles.tab.active : styles.tab.inactive}`}
        >
          {REG_LABELS[reg]}
        </button>
      ))}
    </div>
  );

  const renderProgress = () => {
    const total = currentQuestions.length;
    const answered = answeredCount[currentReg];
    const pct = total > 0 ? (answered / total) * 100 : 0;
    return (
      <div className={styles.progressWrapper}>
        <div className={styles.progressLabel}>
          {answered} of {total} questions answered
        </div>
        <div className={styles.progressTrack}>
          <div className={styles.progressFill} style={{ width: `${pct}%` }} />
        </div>
      </div>
    );
  };

  const renderButtons = () => (
    <div className={styles.buttonRow}>
      <div className="flex gap-2">
        <button
          onClick={handlePrev}
          disabled={questionIndex === 0 && activeRegIndex === 0}
          className={styles.prevBtn}
        >
          Previous
        </button>
        <button onClick={handleSkipTrack} className={styles.skipBtn}>
          Skip track
        </button>
      </div>
      {isComplete && currentAnswer ? (
        <button onClick={onComplete} className={styles.completeBtn}>
          Complete Setup
        </button>
      ) : (
        <button onClick={handleNext} disabled={!currentAnswer} className={styles.nextBtn}>
          {isLastQuestion && isLastReg ? "Complete Setup" : "Next question →"}
        </button>
      )}
    </div>
  );

  // ── Render ───────────────────────────────────────────────
  return (
    <div className={styles.wrapper}>
      <div className={styles.main}>
        <div className={styles.header}>
          <h2 className={styles.title}>Your Compliance Profile</h2>
          <p className={styles.subtitle}>Answer a few questions to see which rules apply to you</p>
        </div>
        {renderTabs()}
        {renderProgress()}
        {currentQuestion && (
          <div className={styles.questionWrapper}>
            <TrackQuestion
              question={currentQuestion}
              currentAnswer={currentAnswer}
              onAnswer={handleAnswer}
            />
          </div>
        )}
        {renderButtons()}
      </div>
      <LiveRulesPanel
        activeRuleIds={activeRuleIds}
        regulation={currentReg}
        trackProgress={{
          gdpr: gdprAnswered,
          nis2: nis2Answered,
          aiAct: aiActAnswered,
        }}
      />
    </div>
  );
};
