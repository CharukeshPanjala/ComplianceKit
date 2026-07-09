import { redirect } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { Sidebar } from "./_components/Sidebar";
import { DpoAssistantWidget } from "./_components/DpoAssistantWidget";

export default async function PortalLayout({ children }: { children: React.ReactNode }) {
  let isComplete = false;

  try {
    const res = await apiFetch("/api/v1/profile");
    if (res.ok) {
      const profile = await res.json();
      isComplete = profile.is_complete === true;
    }
  } catch {
    isComplete = true; // API unreachable — let them through, don't block portal
  }

  if (!isComplete) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    redirect("/onboarding/step/1" as any);
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 md:ml-64 lg:ml-72">{children}</div>
      <DpoAssistantWidget />
    </div>
  );
}
