import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { ToastProvider } from "@/components/ui/Toast";
import "./globals.css";

export const metadata: Metadata = {
  title: "ComplianceKit",
  description: "GDPR, NIS2 and AI Act compliance for modern companies",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>
          <QueryProvider>
            {children}
            <ToastProvider />
          </QueryProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
