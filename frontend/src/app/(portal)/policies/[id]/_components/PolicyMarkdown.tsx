// WHAT: Policy markdown renderer | CHANGE: new file | WHY: COM-176 — render policy content with Tailwind-styled headings, lists, tables
"use client";

import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  h1: "text-xl font-bold text-[#0F2044] mt-2 mb-3",
  h2: "text-lg font-bold text-[#0F2044] mt-6 mb-2",
  h3: "text-base font-semibold text-gray-800 mt-4 mb-2",
  p: "text-sm text-gray-700 leading-relaxed mb-3",
  ul: "list-disc pl-5 space-y-1 text-sm text-gray-700 mb-3",
  ol: "list-decimal pl-5 space-y-1 text-sm text-gray-700 mb-3",
  table: "w-full border border-gray-100 rounded-xl text-sm mb-4 overflow-hidden",
  th: "px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase bg-gray-50 border-b border-gray-100",
  td: "px-3 py-2 text-sm text-gray-700 border-b border-gray-50",
  strong: "font-semibold text-gray-900",
  empty: "text-sm text-gray-400",
};

// ── Markdown component map ───────────────────────────────────────────────────

const components: Components = {
  h1: (props) => <h1 className={styles.h1} {...props} />,
  h2: (props) => <h2 className={styles.h2} {...props} />,
  h3: (props) => <h3 className={styles.h3} {...props} />,
  p: (props) => <p className={styles.p} {...props} />,
  ul: (props) => <ul className={styles.ul} {...props} />,
  ol: (props) => <ol className={styles.ol} {...props} />,
  table: (props) => <table className={styles.table} {...props} />,
  th: (props) => <th className={styles.th} {...props} />,
  td: (props) => <td className={styles.td} {...props} />,
  strong: (props) => <strong className={styles.strong} {...props} />,
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface PolicyMarkdownProps {
  content: string;
}

// ── Component ─────────────────────────────────────────────────────────────────

export const PolicyMarkdown = ({ content }: PolicyMarkdownProps) => {
  if (!content) return <p className={styles.empty}>This policy has no content yet.</p>;
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {content}
    </ReactMarkdown>
  );
};
