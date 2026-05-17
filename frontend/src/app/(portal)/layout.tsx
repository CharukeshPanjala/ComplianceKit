import { redirect } from "next/navigation";
import { apiFetch } from "@/lib/api";

export default async function PortalLayout({ children }: { children: React.ReactNode }) {
  let isComplete = false;

  try {
    const res = await apiFetch("/api/v1/profile");
    if (res.ok) {
      const profile = await res.json();
      isComplete = profile.is_complete === true;
    }
  } catch {
    // If the API is unreachable, let them through — don't block the portal
  }

  if (!isComplete) {
    // next.js typedRoutes requires a cast for dynamic route redirects
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    redirect("/onboarding/step/1" as any);
  }

  return <>{children}</>;
}
