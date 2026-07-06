import { currentUser } from "@clerk/nextjs/server";

// ── Types ─────────────────────────────────────────────────

interface TopBarProps {
  title: string;
  subtitle?: string;
}

// ── Styles ────────────────────────────────────────────────

const styles = {
  header:
    "h-16 bg-white border-b border-gray-100 flex items-center justify-between px-6 flex-shrink-0",
  titleWrapper: "flex flex-col",
  title: "text-lg font-semibold text-gray-900",
  subtitle: "text-xs text-gray-500 mt-0.5",
  userWrapper: "flex items-center gap-3",
  userInfo: "text-right hidden sm:block",
  userName: "text-sm font-medium text-gray-900",
  userEmail: "text-xs text-gray-500",
  avatar: "w-8 h-8 bg-navy rounded-full flex items-center justify-center flex-shrink-0",
  avatarText: "text-white text-xs font-bold uppercase",
};

// ── Component ─────────────────────────────────────────────

export const TopBar = async ({ title, subtitle }: TopBarProps) => {
  const user = await currentUser();
  const name = user?.firstName ?? "there";

  return (
    <header className={styles.header}>
      <div className={styles.titleWrapper}>
        <h1 className={styles.title}>{title}</h1>
        {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      </div>

      <div className={styles.userWrapper}>
        <div className={styles.userInfo}>
          <p className={styles.userName}>{name}</p>
        </div>
        <div className={styles.avatar}>
          <span className={styles.avatarText}>{name.charAt(0)}</span>
        </div>
      </div>
    </header>
  );
};
