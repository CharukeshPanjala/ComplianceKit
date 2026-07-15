"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useClerk, useUser } from "@clerk/nextjs";

// ── Constants ─────────────────────────────────────────────

const NAV_SECTIONS = [
  {
    label: "OVERVIEW",
    items: [
      {
        href: "/dashboard",
        label: "Dashboard",
        locked: false,
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
        ),
      },
    ],
  },
  {
    label: "COMPLIANCE",
    items: [
      {
        href: "/gaps",
        label: "Gap Analysis",
        locked: false,
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        ),
      },
      {
        href: "/policies",
        label: "Policies",
        locked: false,
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
        ),
      },
      {
        href: "/evidence",
        label: "Evidence",
        locked: false,
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        ),
      },
    ],
  },
  {
    label: "DATA OPERATIONS",
    items: [
      {
        href: "/ropa",
        label: "ROPA",
        locked: false,
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        ),
      },
      {
        href: "/vendors",
        label: "Vendor Register",
        locked: false,
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        ),
      },
      {
        href: "/breach",
        label: "Breach Tracker",
        locked: false,
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        ),
      },
      {
        href: "/dsar",
        label: "DSAR",
        locked: false,
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        ),
      },
    ],
  },
  {
    label: "SETTINGS",
    items: [
      {
        href: "/settings/profile",
        label: "Settings",
        locked: false,
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        ),
      },
      {
        href: "/billing",
        label: "Billing",
        locked: true,
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
          </svg>
        ),
      },
    ],
  },
];

// ── Styles ────────────────────────────────────────────────

const styles = {
  aside: "hidden md:flex w-[260px] bg-[#0B1120] flex-col h-screen flex-shrink-0 overflow-y-auto fixed left-0 top-0 border-r border-white/5",
  logo: {
    wrapper: "px-5 py-5 border-b border-white/5",
    inner: "flex items-center gap-3",
    textBlock: "flex flex-col",
    name: "text-white font-bold text-base leading-tight tracking-tight",
    subtitle: "text-white/40 text-[10px] font-medium tracking-wide uppercase",
  },
  nav: "flex-1 px-3 py-4 space-y-5 overflow-y-auto",
  sectionLabel: "text-[10px] font-semibold tracking-widest text-white/30 uppercase px-2 mb-1 block",
  sectionItems: "space-y-0.5",
  item: {
    base: "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm font-medium w-full text-left",
    active: "border-l-[3px] border-[#F59E0B] text-[#F59E0B] bg-white/10 rounded-l-none pl-[calc(0.75rem-3px)]",
    inactive: "text-white/60 hover:text-white hover:bg-white/5",
    locked: "opacity-50 cursor-not-allowed text-white/40",
  },
  soonBadge: "ml-auto text-[10px] font-medium bg-white/10 text-white/40 rounded px-1.5 py-0.5 flex-shrink-0",
  footer: "px-4 py-4 border-t border-white/5",
  footerInner: "flex items-center gap-3",
  avatar: "w-8 h-8 rounded-full bg-[#D97706] flex items-center justify-center text-white text-sm font-bold flex-shrink-0",
  footerText: "flex flex-col flex-1 min-w-0",
  footerName: "text-white text-sm font-medium truncate",
  footerRole: "text-white/40 text-xs",
  signOutBtn: "w-8 h-8 flex items-center justify-center text-white/40 hover:text-white transition-colors rounded-lg hover:bg-white/5 flex-shrink-0",
};

// ── Sub-components ────────────────────────────────────────

const ShieldIcon = () => (
  <svg className="w-7 h-7 text-[#F59E0B]" fill="currentColor" viewBox="0 0 24 24">
    <path d="M12 2L4 5v6c0 5.25 3.5 10.15 8 11.35C16.5 21.15 20 16.25 20 11V5l-8-3z" />
  </svg>
);

const SoonBadge = () => <span className={styles.soonBadge}>Soon</span>;

const SignOutIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
  </svg>
);

// ── Component ─────────────────────────────────────────────

export const Sidebar = () => {
  const pathname = usePathname();
  const { signOut } = useClerk();
  const { user } = useUser();

  // ── Handlers ──────────────────────────────────────────

  const handleSignOut = () => signOut({ redirectUrl: "/sign-in" });

  // ── Render helpers ─────────────────────────────────────

  const renderLogo = () => (
    <div className={styles.logo.wrapper}>
      <div className={styles.logo.inner}>
        <ShieldIcon />
        <div className={styles.logo.textBlock}>
          <span className={styles.logo.name}>ComplianceKit</span>
          <span className={styles.logo.subtitle}>EU Compliance Platform</span>
        </div>
      </div>
    </div>
  );

  const renderNavItem = (item: (typeof NAV_SECTIONS)[0]["items"][0]) => {
    const isActive = pathname.startsWith(item.href) && item.href !== "/";

    if (item.locked) {
      return (
        <div key={item.href} className={`${styles.item.base} ${styles.item.locked}`}>
          {item.icon}
          <span>{item.label}</span>
          <SoonBadge />
        </div>
      );
    }

    return (
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      <Link key={item.href} href={item.href as any} className={`${styles.item.base} ${isActive ? styles.item.active : styles.item.inactive}`}>
        {item.icon}
        <span>{item.label}</span>
      </Link>
    );
  };

  const renderSection = (section: (typeof NAV_SECTIONS)[0]) => (
    <div key={section.label}>
      <span className={styles.sectionLabel}>{section.label}</span>
      <div className={styles.sectionItems}>{section.items.map(renderNavItem)}</div>
    </div>
  );

  const renderNav = () => <nav className={styles.nav}>{NAV_SECTIONS.map(renderSection)}</nav>;

  const renderFooter = () => (
    <div className={styles.footer}>
      <div className={styles.footerInner}>
        <div className={styles.avatar}>
          {(user?.firstName?.[0] ?? user?.emailAddresses?.[0]?.emailAddress?.[0] ?? "U").toUpperCase()}
        </div>
        <div className={styles.footerText}>
          <span className={styles.footerName}>{user?.firstName ?? user?.emailAddresses?.[0]?.emailAddress ?? "User"}</span>
          <span className={styles.footerRole}>{user?.organizationMemberships?.[0]?.role === "org:admin" ? "Administrator" : "Member"}</span>
        </div>
        <button onClick={handleSignOut} className={styles.signOutBtn} title="Sign out">
          <SignOutIcon />
        </button>
      </div>
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
