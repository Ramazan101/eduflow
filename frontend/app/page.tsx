import Link from "next/link";

import { SiteHeader } from "@/components/brand/site-header";

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main className="mx-auto max-w-3xl px-6 py-16 sm:py-24">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--accent)]">
          Admissions workspace
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">
          Apply once. Registrars review with a clear record.
        </h1>
        <p className="mt-5 max-w-2xl text-base leading-7 text-[var(--muted)]">
          EduFlow is for institutions that need a reliable application file:
          identity-light contact details, a verified requirements profile, and a
          status history. A generated PDF is a demo summary, not a signed offer.
        </p>
        <div className="mt-10 flex flex-wrap gap-3">
          <Link
            href="/apply"
            className="rounded-md bg-[var(--accent)] px-5 py-2.5 text-sm font-semibold text-[#f7f4ee] hover:bg-[#17473b]"
          >
            Start an application
          </Link>
          <Link
            href="/admin/login"
            className="rounded-md border border-[var(--line)] bg-[#fffcf7] px-5 py-2.5 text-sm font-medium hover:bg-white"
          >
            Registrar sign in
          </Link>
        </div>
      </main>
    </div>
  );
}
