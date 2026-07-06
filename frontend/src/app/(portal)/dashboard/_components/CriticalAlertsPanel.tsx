"use client";

import Link from "next/link";
import type { LatestAssessment, Gap } from "@/types/assessment";
import type { DsarRequest } from "@/lib/dsarApi";
import type { BreachIncident } from "@/lib/breachApi";

// ── Constants ─────────────────────────────────────────────

type AlertType = "gap" | "dsar" | "breach" | "deadline";

const STRIPE_COLORS: Record<AlertType, string> = {
  gap: "#EF4444",
  dsar: "#7C3AED",
  breach: "#F97316",
  deadline: "#D97706",
};

const CTA_LABELS: Record<AlertType, string> = {
  gap: "Remediate",
  dsar: "Respond",
  breach: "Act Now",
  deadline: "View",
};

const CTA_HREFS: Record<AlertType, string> = {
  gap: "/gaps",
  dsar: "/dsar",
  breach: "/breach",
  deadline: "/gaps",
};

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "space-y-3",
  empty: "flex items-center gap-3 bg-green-50 border border-green-100 rounded-xl px-4 py-4",
  emptyDot: "w-8 h-8 text-green-500 flex-shrink-0",
  emptyText: "text-sm font-semibold text-green-700",
  emptySubtext: "text-xs text-green-500",
  item: "flex items-stretch bg-white rounded-xl border border-[#E2E8F0] shadow-sm overflow-hidden",
  stripe: "w-1 flex-shrink-0",
  content: "flex-1 px-4 py-3 flex items-center gap-3 min-w-0",
  icon: "text-xl flex-shrink-0",
  body: "flex-1 min-w-0",
  title: "text-xs font-bold text-[#64748B] uppercase tracking-wide",
  desc: "text-sm font-medium text-[#0F172A] truncate mt-0.5",
  regBadge: "mt-1 inline-block text-[10px] font-bold px-1.5 py-0.5 rounded uppercase",
  cta: "ml-2 flex-shrink-0 text-xs font-semibold px-3 py-1.5 rounded-lg border border-[#E2E8F0] text-[#334155] hover:bg-gray-50 transition-colors whitespace-nowrap",
};

const REG_BADGE_STYLES: Record<string, string> = {
  GDPR: "bg-purple-100 text-purple-700",
  NIS2: "bg-cyan-100 text-cyan-700",
  EU_AI_ACT: "bg-pink-100 text-pink-700",
};

// ── Types ──────────────────────────────────────────────────

interface AlertItem {
  id: string;
  type: AlertType;
  title: string;
  desc: string;
  regulation?: string;
  urgency: number;
}

interface Props {
  assessments: LatestAssessment[];
  gaps: Gap[];
  dsarRequests: DsarRequest[];
  breachIncidents: BreachIncident[];
}

// ── Helpers ────────────────────────────────────────────────

const buildAlerts = (
  gaps: Gap[],
  dsarRequests: DsarRequest[],
  breachIncidents: BreachIncident[]
): AlertItem[] => {
  const items: AlertItem[] = [];

  try {
    gaps.forEach((g) => {
      if (g.severity === "critical" && g.status === "not_met") {
        items.push({
          id: `gap-${g.gap_id}`,
          type: "gap",
          title: "Critical Gap",
          desc: g.title ?? g.article,
          urgency: 4,
        });
      }
    });

    dsarRequests.forEach((d) => {
      if (d.is_overdue) {
        items.push({
          id: `dsar-${d.dsar_id}`,
          type: "dsar",
          title: "DSAR Overdue",
          desc: `${Math.abs(d.days_remaining)} days overdue`,
          urgency: 3,
        });
      }
    });

    breachIncidents.forEach((b) => {
      if (
        b.status !== "closed" &&
        b.status !== "reported_to_dpa" &&
        b.status !== "reported_to_individuals"
      ) {
        items.push({
          id: `breach-${b.breach_id}`,
          type: "breach",
          title: "Open Breach",
          desc: b.title,
          urgency: 3,
        });
      }
    });

    const sevenDaysMs = 7 * 86_400_000;
    gaps.forEach((g) => {
      if (
        g.due_date &&
        g.status !== "met" &&
        new Date(g.due_date).getTime() - Date.now() < sevenDaysMs &&
        new Date(g.due_date).getTime() > Date.now()
      ) {
        items.push({
          id: `dl-${g.gap_id}`,
          type: "deadline",
          title: "Deadline Soon",
          desc: g.title ?? g.article,
          urgency: 2,
        });
      }
    });
  } catch {
    // return whatever was collected
  }

  return items
    .sort((a, b) => b.urgency - a.urgency)
    .slice(0, 4);
};

// ── Sub-components ────────────────────────────────────────

const ICONS: Record<AlertType, string> = {
  gap: "⚠️",
  dsar: "👤",
  breach: "🔴",
  deadline: "⏰",
};

const AlertRow = ({ alert }: { alert: AlertItem }) => (
  <div className={styles.item}>
    <div className={styles.stripe} style={{ backgroundColor: STRIPE_COLORS[alert.type] }} />
    <div className={styles.content}>
      <span className={styles.icon}>{ICONS[alert.type]}</span>
      <div className={styles.body}>
        <p className={styles.title}>{alert.title}</p>
        <p className={styles.desc}>{alert.desc}</p>
        {alert.regulation && (
          <span
            className={`${styles.regBadge} ${REG_BADGE_STYLES[alert.regulation] ?? "bg-gray-100 text-gray-600"}`}
          >
            {alert.regulation === "EU_AI_ACT" ? "AI Act" : alert.regulation}
          </span>
        )}
      </div>
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      <Link href={CTA_HREFS[alert.type] as any} className={styles.cta}>
        {CTA_LABELS[alert.type]}
      </Link>
    </div>
  </div>
);

// ── Component ─────────────────────────────────────────────

export const CriticalAlertsPanel = ({
  gaps,
  dsarRequests,
  breachIncidents,
}: Props) => {
  const alerts = buildAlerts(gaps, dsarRequests, breachIncidents);

  // ── Render helpers ─────────────────────────────────────

  const renderEmpty = () => (
    <div className={styles.empty}>
      <span className={styles.emptyDot}>✅</span>
      <div>
        <p className={styles.emptyText}>All clear</p>
        <p className={styles.emptySubtext}>No urgent items need your attention today</p>
      </div>
    </div>
  );

  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.wrapper}>
      {alerts.length === 0
        ? renderEmpty()
        : alerts.map((a) => <AlertRow key={a.id} alert={a} />)}
    </div>
  );
};
