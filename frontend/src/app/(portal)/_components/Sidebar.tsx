"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useClerk } from "@clerk/nextjs";

// ── Constants ─────────────────────────────────────────────

const NAV_ITEMS = [
  {
    href: "/dashboard",
    label: "Dashboard",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
        />
      </svg>
    ),
  },
  {
    href: "/gaps",
    label: "Gap Analysis",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
        />
      </svg>
    ),
    comingSoon: true,
  },
  {
    href: "/ropa",
    label: "ROPA",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
    ),
  },
  {
    href: "/policies",
    label: "Policies",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
        />
      </svg>
    ),
  },
  {
    href: "/breach",
    label: "Breach Tracker",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
    ),
    comingSoon: true,
  },
  {
    href: "/dsar",
    label: "DSAR",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
        />
      </svg>
    ),
    comingSoon: true,
  },
];

// ── Styles ────────────────────────────────────────────────

const styles = {
  aside:
    "hidden md:flex md:w-64 lg:w-72 bg-navy flex-col h-screen flex-shrink-0 overflow-y-auto fixed left-0 top-0",
  logo: {
    wrapper: "px-6 py-6 border-b border-white/10",
    inner: "flex items-center gap-2.5",
    icon: "w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center flex-shrink-0",
    iconText: "text-white font-bold text-sm",
    name: "text-white font-bold text-lg tracking-tight",
  },
  nav: "flex-1 px-3 py-4 space-y-0.5",
  item: {
    base: "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm font-medium w-full",
    active: "bg-white/15 text-white",
    inactive: "text-blue-100 hover:bg-white/10 hover:text-white",
    disabled: "opacity-40 cursor-not-allowed",
  },
  badge: "ml-auto text-xs bg-white/10 text-blue-200 px-2 py-0.5 rounded-full",
  footer: "px-4 py-4 border-t border-white/10",
  signOut:
    "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-blue-100 hover:bg-white/10 hover:text-white transition-colors w-full",
  signOutIcon: "w-5 h-5",
  backLink: "mt-3 block text-xs text-blue-300 hover:text-white transition-colors",
  footerText: "text-xs text-blue-200/60 leading-relaxed",
};

// ── Sub-components ────────────────────────────────────────

const SignOutIcon = () => (
  <svg className={styles.signOutIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={1.5}
      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
    />
  </svg>
);

// ── Component ─────────────────────────────────────────────

export const Sidebar = () => {
  const pathname = usePathname();
  const { signOut } = useClerk();

  // ── Handlers ──────────────────────────────────────────

  const handleSignOut = () => signOut({ redirectUrl: "/sign-in" });

  const getItemClass = (isActive: boolean) =>
    `${styles.item.base} ${isActive ? styles.item.active : styles.item.inactive}`;

  // ── Render helpers ─────────────────────────────────────

  const renderLogo = () => (
    <div className={styles.logo.wrapper}>
      <div className={styles.logo.inner}>
        <div className={styles.logo.icon}>
          <span className={styles.logo.iconText}>C</span>
        </div>
        <span className={styles.logo.name}>ComplianceKit</span>
      </div>
    </div>
  );

  const renderNavItem = (item: (typeof NAV_ITEMS)[0]) => {
    const isActive = pathname === item.href;

    if (item.comingSoon) {
      return (
        <div key={item.href} className={`${styles.item.base} ${styles.item.disabled}`}>
          {item.icon}
          <span>{item.label}</span>
          <span className={styles.badge}>Soon</span>
        </div>
      );
    }

    return (
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      <Link key={item.href} href={item.href as any} className={getItemClass(isActive)}>
        {item.icon}
        <span>{item.label}</span>
      </Link>
    );
  };

  const renderNav = () => <nav className={styles.nav}>{NAV_ITEMS.map(renderNavItem)}</nav>;

  const renderFooter = () => (
    <div className={styles.footer}>
      <button onClick={handleSignOut} className={styles.signOut}>
        <SignOutIcon />
        Sign out
      </button>
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      <a href={"/dashboard" as any} className={styles.backLink}>
        ← Back to Dashboard
      </a>
    </div>
  );

  // ── Render ────────────────────────────────────────────

  return (
    <aside className={styles.aside}>
      {renderLogo()}
      {renderNav()}
      {renderFooter()}
    </aside>
  );
};
