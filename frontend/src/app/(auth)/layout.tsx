export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      {/* Left — Navy brand panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-navy flex-col justify-between p-12">
        {/* Logo */}
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 bg-amber-500 rounded-lg flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold text-sm">C</span>
          </div>
          <span className="text-white font-bold text-xl tracking-tight">ComplianceKit</span>
        </div>

        {/* Tagline */}
        <div>
          <h1 className="text-4xl font-bold text-white leading-snug mb-4">
            Your compliance
            <br />
            co-pilot.
          </h1>
          <p className="text-blue-200 text-lg leading-relaxed max-w-sm">
            Understand your GDPR obligations, identify gaps, and stay audit-ready — all in one
            place.
          </p>
        </div>

        {/* Footer note */}
        <p className="text-blue-300 text-sm">Trusted by privacy-conscious teams across Europe.</p>
      </div>

      {/* Right — Clerk form */}
      <div className="flex flex-1 items-center justify-center bg-warm-white p-8">{children}</div>
    </div>
  );
}
