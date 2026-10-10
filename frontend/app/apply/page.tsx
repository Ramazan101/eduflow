import { ApplicationFlow } from "@/components/apply/application-flow";
import { SiteHeader } from "@/components/brand/site-header";

export default function ApplyPage() {
  return (
    <div className="min-h-screen">
      <a
        href="#application"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-white focus:px-3 focus:py-2"
      >
        Skip to application
      </a>
      <SiteHeader />
      <main className="mx-auto grid max-w-6xl gap-12 px-6 py-12 lg:grid-cols-[1fr_1.05fr] lg:items-start lg:py-16">
        <section className="max-w-xl">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--accent)]">
            Student application
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">
            Apply to a published programme.
          </h1>
          <p className="mt-4 text-base leading-7 text-[var(--muted)]">
            Choose the institution and programme, read the verified admissions
            profile, then submit the contact details that profile requires.
            Success appears only after EduFlow accepts the file.
          </p>
          <ol className="mt-8 space-y-3 text-sm text-[var(--muted)]">
            <li>1. Select institution and programme</li>
            <li>2. Read the requirement profile</li>
            <li>3. Enter name, date of birth, phone, and email</li>
            <li>4. Review and submit</li>
          </ol>
        </section>
        <section id="application">
          <ApplicationFlow />
        </section>
      </main>
    </div>
  );
}
