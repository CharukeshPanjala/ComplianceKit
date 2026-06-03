import { redirect } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { TopBar } from "../_components/TopBar";
import { DashboardContent } from "./_components/DashboardContent";
import type { Profile } from "@/types/profile";

// ── Styles ────────────────────────────────────────────────

const styles = {
  wrapper: "flex flex-col h-full",
};

// ── Page ──────────────────────────────────────────────────

export default async function DashboardPage() {
  let profile: Profile | null = null;

  try {
    const res = await apiFetch("/api/v1/profile");
    if (res.ok) profile = await res.json();
  } catch {
    // API unreachable — redirect to onboarding
  }

  if (!profile?.is_complete) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    redirect("/onboarding/step/1" as any);
  }

  return (
    <div className={styles.wrapper}>
      <TopBar title="Compliance Dashboard" subtitle="Your real-time compliance posture" />
      <DashboardContent profile={profile!} />
    </div>
  );
}
