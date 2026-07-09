"use client";

// ── Types ──────────────────────────────────────────────────
type RegulationType = "GDPR" | "NIS2" | "AI_ACT";

interface Rule {
  id: string;
  summary: string;
}

interface LiveRulesPanelProps {
  activeRuleIds: string[];
  regulation: RegulationType;
  trackProgress: { gdpr: number; nis2: number; aiAct: number };
}

// ── Constants ───────────────────────────────────────────────
const RULES_BY_REGULATION: Record<RegulationType, Rule[]> = {
  GDPR: [
    { id: "Art.5", summary: "Data processing principles" },
    { id: "Art.6", summary: "Lawful basis for processing" },
    { id: "Art.9", summary: "Special categories of data" },
    { id: "Art.17", summary: "Right to erasure" },
    { id: "Art.21", summary: "Right to object to processing" },
    { id: "Art.22", summary: "Automated decisions and profiling" },
    { id: "Art.30", summary: "Records of processing activities" },
    { id: "Art.35", summary: "Data protection impact assessment" },
    { id: "Art.37", summary: "DPO appointment obligation" },
    { id: "Art.38", summary: "DPO position and tasks" },
    { id: "Art.39", summary: "DPO duties" },
    { id: "Art.44", summary: "Transfer restriction principles" },
    { id: "Art.45", summary: "Adequacy decisions" },
    { id: "Art.46", summary: "Appropriate safeguards" },
    { id: "Art.49", summary: "Derogations for specific situations" },
  ],
  NIS2: [
    { id: "Art.18", summary: "Incident reporting to authorities" },
    { id: "Art.20", summary: "Governance and management oversight" },
    { id: "Art.21", summary: "Cybersecurity risk management measures" },
    { id: "Art.23", summary: "Reporting obligations timeline" },
    { id: "Art.24", summary: "Use of certified products/services" },
    { id: "Art.29", summary: "Information sharing arrangements" },
  ],
  AI_ACT: [
    { id: "Art.6", summary: "Classification rules for high-risk AI" },
    { id: "Art.9", summary: "Risk management system" },
    { id: "Art.10", summary: "Data and data governance" },
    { id: "Art.11", summary: "Technical documentation" },
    { id: "Art.12", summary: "Record-keeping and logging" },
    { id: "Art.13", summary: "Transparency and information" },
    { id: "Art.14", summary: "Human oversight measures" },
    { id: "Art.15", summary: "Accuracy, robustness, cybersecurity" },
    { id: "Art.17", summary: "Quality management system" },
    { id: "Art.26", summary: "Obligations of deployers" },
    { id: "Art.43", summary: "Conformity assessment" },
    { id: "Art.50", summary: "Transparency obligations for GPAI" },
    { id: "Art.51", summary: "GPAI model classification" },
    { id: "Art.52", summary: "Transparency for GPAI providers" },
    { id: "Art.53", summary: "Obligations for GPAI providers" },
    { id: "Art.54", summary: "Authorised representatives of GPAI providers" },
    { id: "Art.55", summary: "Systemic risk mitigation" },
    { id: "Art.86", summary: "Right to explanation of decisions" },
  ],
};

// ── Styles ──────────────────────────────────────────────────
const styles = {
  panel: "w-[340px] flex-shrink-0 bg-[#0B1120] flex flex-col h-full",
  header: "px-5 py-4 border-b border-white/10 flex-shrink-0",
  headerRow: "flex items-center gap-2",
  pulseDot: "w-2 h-2 rounded-full bg-[#F59E0B] animate-pulse flex-shrink-0",
  headerTitle: "text-white font-semibold text-sm flex-1",
  countBadge: "bg-[#D97706] text-white text-xs font-bold px-2 py-0.5 rounded-full",
  rulesList: "flex-1 overflow-y-auto px-4 py-4 space-y-2",
  ruleRow: {
    base: "flex items-start gap-3 py-2 px-2 rounded-lg transition-all",
    active: "border-l-2 border-[#F59E0B] pl-3",
    inactive: "opacity-30",
  },
  articleId: "text-[#F59E0B] font-mono text-xs font-bold flex-shrink-0 mt-0.5",
  ruleSummary: {
    active: "text-white text-xs leading-relaxed",
    inactive: "text-gray-400 text-xs leading-relaxed",
  },
  progressSection: "px-4 py-4 border-t border-white/10 flex-shrink-0 space-y-3",
  progressLabel: "text-white/40 text-[10px] font-semibold uppercase tracking-widest",
  progressRow: "space-y-1",
  progressTrackLabel: "flex items-center justify-between",
  progressTrackName: "text-white/50 text-xs",
  progressTrackCount: "text-white/30 text-xs",
  progressTrack: "w-full h-1 bg-white/10 rounded-full overflow-hidden",
  progressFill: "h-full bg-[#D97706] rounded-full transition-all",
};

// ── Component ───────────────────────────────────────────────
export const LiveRulesPanel = ({ activeRuleIds, regulation, trackProgress }: LiveRulesPanelProps) => {
  const rules = RULES_BY_REGULATION[regulation];
  const activeCount = rules.filter((r) => activeRuleIds.includes(r.id)).length;

  // ── Render helpers ───────────────────────────────────────
  const renderRule = (rule: Rule) => {
    const isActive = activeRuleIds.includes(rule.id);
    return (
      <div
        key={rule.id}
        className={`${styles.ruleRow.base} ${isActive ? styles.ruleRow.active : styles.ruleRow.inactive}`}
      >
        <span className={styles.articleId}>{rule.id}</span>
        <span className={isActive ? styles.ruleSummary.active : styles.ruleSummary.inactive}>
          {rule.summary}
        </span>
      </div>
    );
  };

  const renderProgressBar = (label: string, value: number, max: number) => (
    <div key={label} className={styles.progressRow}>
      <div className={styles.progressTrackLabel}>
        <span className={styles.progressTrackName}>{label}</span>
        <span className={styles.progressTrackCount}>
          {value}/{max}
        </span>
      </div>
      <div className={styles.progressTrack}>
        <div
          className={styles.progressFill}
          style={{ width: `${(value / max) * 100}%` }}
        />
      </div>
    </div>
  );

  // ── Render ───────────────────────────────────────────────
  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <div className={styles.headerRow}>
          <div className={styles.pulseDot} />
          <span className={styles.headerTitle}>Rules that now apply to you</span>
          <span className={styles.countBadge}>{activeCount}</span>
        </div>
      </div>
      <div className={styles.rulesList}>{rules.map(renderRule)}</div>
      <div className={styles.progressSection}>
        <div className={styles.progressLabel}>Track progress</div>
        {renderProgressBar("GDPR", trackProgress.gdpr, 5)}
        {renderProgressBar("AI Act", trackProgress.aiAct, 4)}
        {renderProgressBar("NIS2", trackProgress.nis2, 5)}
      </div>
    </div>
  );
};
