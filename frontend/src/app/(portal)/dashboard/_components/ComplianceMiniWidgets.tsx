"use client";

import Link from "next/link";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";
import type { DsarRequest } from "@/lib/dsarApi";
import type { Processor } from "@/lib/processorsApi";

// ── Styles ────────────────────────────────────────────────

const styles = {
  grid: "grid grid-cols-1 md:grid-cols-2 gap-4",
  card: "bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-5 flex flex-col gap-3",
  cardTitle: "text-xs font-semibold text-[#64748B] uppercase tracking-wider",
  statsRow: "flex items-center gap-6",
  stat: "flex flex-col",
  statVal: "text-2xl font-bold text-[#0F172A]",
  statValRed: "text-2xl font-bold text-red-600",
  statLabel: "text-[10px] text-[#94A3B8] uppercase",
  pieRow: "flex justify-center",
  highlight: "text-xs text-[#64748B]",
  highlightName: "font-semibold text-[#0F172A]",
  allGood: "text-xs font-medium text-green-600",
  link: "text-xs font-semibold text-[#D97706] hover:text-[#B45309] transition-colors self-start mt-auto",
};

// ── Types ──────────────────────────────────────────────────

interface Props {
  dsarRequests: DsarRequest[];
  vendors: Processor[];
}

// ── Sub-components ────────────────────────────────────────

const DsarCard = ({ dsarRequests }: { dsarRequests: DsarRequest[] }) => {
  const active = dsarRequests.filter(
    (d) => d.status === "pending" || d.status === "in_progress" || d.status === "awaiting_info"
  ).length;
  const completed = dsarRequests.filter((d) => d.status === "completed").length;
  const overdue = dsarRequests.filter((d) => d.is_overdue).length;

  const pieData = [
    { name: "Active", value: active || 0, color: "#7C3AED" },
    { name: "Completed", value: completed || 0, color: "#22C55E" },
    { name: "Overdue", value: overdue || 0, color: "#EF4444" },
  ].filter((d) => d.value > 0);

  return (
    <div className={styles.card}>
      <p className={styles.cardTitle}>DSAR Requests</p>
      <div className={styles.statsRow}>
        <div className={styles.stat}>
          <span className={styles.statVal}>{active}</span>
          <span className={styles.statLabel}>Active</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statVal}>{completed}</span>
          <span className={styles.statLabel}>Completed</span>
        </div>
        <div className={styles.stat}>
          <span className={overdue > 0 ? styles.statValRed : styles.statVal}>{overdue}</span>
          <span className={styles.statLabel}>Overdue</span>
        </div>
      </div>
      {pieData.length > 0 && (
        <div className={styles.pieRow}>
          <ResponsiveContainer width={90} height={90}>
            <PieChart>
              <Pie data={pieData} dataKey="value" outerRadius={40}>
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      <Link href={"/dsar" as any} className={styles.link}>
        View all →
      </Link>
    </div>
  );
};

const VendorCard = ({ vendors }: { vendors: Processor[] }) => {
  const compliant = vendors.filter((v) => v.dpa_signed).length;
  const pending = vendors.filter((v) => !v.dpa_signed).length;
  const firstUnsigned = vendors.find((v) => !v.dpa_signed);

  return (
    <div className={styles.card}>
      <p className={styles.cardTitle}>Vendor Register</p>
      <div className={styles.statsRow}>
        <div className={styles.stat}>
          <span className={styles.statVal}>{compliant}</span>
          <span className={styles.statLabel}>Compliant</span>
        </div>
        <div className={styles.stat}>
          <span className={pending > 0 ? styles.statValRed : styles.statVal}>{pending}</span>
          <span className={styles.statLabel}>Pending DPA</span>
        </div>
      </div>
      {firstUnsigned ? (
        <p className={styles.highlight}>
          Highest risk:{" "}
          <span className={styles.highlightName}>{firstUnsigned.name}</span>
        </p>
      ) : (
        <p className={styles.allGood}>All DPAs signed</p>
      )}
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      <Link href={"/vendors" as any} className={styles.link}>
        View all →
      </Link>
    </div>
  );
};

// ── Component ─────────────────────────────────────────────

export const ComplianceMiniWidgets = ({ dsarRequests, vendors }: Props) => {
  // ── Render ────────────────────────────────────────────

  return (
    <div className={styles.grid}>
      <DsarCard dsarRequests={dsarRequests} />
      <VendorCard vendors={vendors} />
    </div>
  );
};
