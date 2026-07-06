import type { LatestAssessment, Gap } from "@/types/assessment";
import type { DsarRequest } from "@/lib/dsarApi";
import type { BreachIncident } from "@/lib/breachApi";

// ── Constants ─────────────────────────────────────────────

const DOT_COLORS = {
  gap_resolved: "#22C55E",
  dsar: "#7C3AED",
  breach: "#EF4444",
  assessment: "#D97706",
} as const;

const REG_BADGE_STYLES: Record<string, string> = {
  GDPR: "bg-purple-100 text-purple-700",
  NIS2: "bg-cyan-100 text-cyan-700",
  EU_AI_ACT: "bg-pink-100 text-pink-700",
  gdpr: "bg-purple-100 text-purple-700",
  nis2: "bg-cyan-100 text-cyan-700",
  both: "bg-gray-100 text-gray-600",
};

// ── Styles ────────────────────────────────────────────────

const styles = {
  list: "space-y-3",
  row: "flex items-start gap-3",
  dotWrapper: "mt-1.5 flex-shrink-0",
  dot: "w-2 h-2 rounded-full",
  body: "flex-1 min-w-0",
  title: "text-sm text-[#0F172A]",
  meta: "flex items-center gap-1.5 mt-0.5",
  time: "text-xs text-[#94A3B8]",
  regBadge: "text-[10px] font-semibold px-1.5 py-0.5 rounded uppercase",
  empty: "text-sm text-[#94A3B8] text-center py-4",
};

// ── Types ──────────────────────────────────────────────────

type EventType = keyof typeof DOT_COLORS;

interface ActivityEvent {
  id: string;
  type: EventType;
  title: string;
  timestamp: string;
  regulation?: string;
}

interface Props {
  assessments: LatestAssessment[];
  gaps: Gap[];
  dsarRequests: DsarRequest[];
  breachIncidents: BreachIncident[];
}

// ── Helpers ────────────────────────────────────────────────

const formatRelativeTime = (dateStr: string): string => {
  try {
    const diff = Date.now() - new Date(dateStr).getTime();
    const hours = Math.floor(diff / 3_600_000);
    if (hours < 1) return "just now";
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  } catch {
    return "";
  }
};

const buildEvents = (
  assessments: LatestAssessment[],
  gaps: Gap[],
  dsarRequests: DsarRequest[],
  breachIncidents: BreachIncident[]
): ActivityEvent[] => {
  const events: ActivityEvent[] = [];

  try {
    gaps.forEach((g) => {
      if (g.status === "met" && g.resolved_at) {
        events.push({
          id: `gap-${g.gap_id}`,
          type: "gap_resolved",
          title: `Gap resolved: ${g.title ?? g.article}`,
          timestamp: g.resolved_at,
        });
      }
    });

    assessments.forEach((a) => {
      if (a.status === "completed" && a.completed_at) {
        events.push({
          id: `asm-${a.regulation}`,
          type: "assessment",
          title: `Assessment completed: ${a.regulation === "EU_AI_ACT" ? "AI Act" : a.regulation}`,
          timestamp: a.completed_at,
          regulation: a.regulation,
        });
      }
    });

    dsarRequests.forEach((d) => {
      const ts = d.created_at ?? d.received_at;
      if (ts) {
        events.push({
          id: `dsar-${d.dsar_id}`,
          type: "dsar",
          title: `DSAR submitted: ${d.requester_name ?? "Data subject"}`,
          timestamp: ts,
        });
      }
    });

    breachIncidents.forEach((b) => {
      const ts = b.reported_at ?? b.created_at;
      if (ts) {
        events.push({
          id: `breach-${b.breach_id}`,
          type: "breach",
          title: "Breach incident reported",
          timestamp: ts,
          regulation: b.regulation ?? undefined,
        });
      }
    });
  } catch {
    // return whatever collected
  }

  return events
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 8);
};

// ── Sub-components ────────────────────────────────────────

const ActivityRow = ({ event }: { event: ActivityEvent }) => (
  <div className={styles.row}>
    <div className={styles.dotWrapper}>
      <div className={styles.dot} style={{ backgroundColor: DOT_COLORS[event.type] }} />
    </div>
    <div className={styles.body}>
      <p className={styles.title}>{event.title}</p>
      <div className={styles.meta}>
        <span className={styles.time}>{formatRelativeTime(event.timestamp)}</span>
        {event.regulation && (
          <span
            className={`${styles.regBadge} ${REG_BADGE_STYLES[event.regulation] ?? "bg-gray-100 text-gray-600"}`}
          >
            {event.regulation === "EU_AI_ACT" ? "AI Act" : event.regulation}
          </span>
        )}
      </div>
    </div>
  </div>
);

// ── Component ─────────────────────────────────────────────

export const RecentActivityFeed = ({
  assessments,
  gaps,
  dsarRequests,
  breachIncidents,
}: Props) => {
  const events = buildEvents(assessments, gaps, dsarRequests, breachIncidents);

  return (
    <div className={styles.list}>
      {events.length === 0 ? (
        <p className={styles.empty}>No recent activity</p>
      ) : (
        events.map((e) => <ActivityRow key={e.id} event={e} />)
      )}
    </div>
  );
};
