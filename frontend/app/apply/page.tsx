import { BadgeCheck, FileSignature, ShieldCheck } from "lucide-react";

import { ApplicationFlow } from "@/components/apply/application-flow";
import { SiteHeader } from "@/components/apply/site-header";

const highlights = [
  {
    icon: ShieldCheck,
    title: "Reviewed by admins",
    text: "Every application is screened before a contract is issued.",
  },
  {
    icon: FileSignature,
    title: "Digital training contract",
    text: "We generate a professional agreement from your submitted details.",
  },
  {
    icon: BadgeCheck,
    title: "Cohort-ready onboarding",
    text: "Accepted students move into course access without extra paperwork.",
  },
];

export default function ApplyPage() {
  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_#f0fdfa_0%,_#f8fafc_42%,_#f1f5f9_100%)]">
      <SiteHeader />

      <main className="mx-auto grid max-w-6xl gap-12 px-6 py-12 lg:grid-cols-[1.05fr_0.95fr] lg:items-start lg:py-16">
        <section className="max-w-xl">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-700">
            Student application
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight text-slate-900 sm:text-[2.6rem] sm:leading-tight">
            Enrol in professional training with a contract-ready application.
          </h1>
          <p className="mt-4 text-base leading-7 text-slate-600">
            EduFlow is the onboarding workspace for B2B training teams. Submit
            your details once. Our administrators review your profile and
            prepare a training contract for signature.
          </p>

          <ul className="mt-8 space-y-4">
            {highlights.map(({ icon: Icon, title, text }) => (
              <li key={title} className="flex gap-3">
                <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-white text-sky-700 shadow-sm">
                  <Icon className="h-4 w-4" aria-hidden />
                </span>
                <div>
                  <p className="text-sm font-semibold text-slate-900">{title}</p>
                  <p className="text-sm leading-6 text-slate-500">{text}</p>
                </div>
              </li>
            ))}
          </ul>

          <dl className="mt-10 grid grid-cols-3 gap-4 border-t border-slate-200/80 pt-6">
            <div>
              <dt className="text-[11px] font-medium uppercase tracking-wider text-slate-400">
                Typical review
              </dt>
              <dd className="mt-1 text-lg font-semibold text-slate-900">48h</dd>
            </div>
            <div>
              <dt className="text-[11px] font-medium uppercase tracking-wider text-slate-400">
                Programmes
              </dt>
              <dd className="mt-1 text-lg font-semibold text-slate-900">5</dd>
            </div>
            <div>
              <dt className="text-[11px] font-medium uppercase tracking-wider text-slate-400">
                Format
              </dt>
              <dd className="mt-1 text-lg font-semibold text-slate-900">
                Digital
              </dd>
            </div>
          </dl>
        </section>

        <section>
          <ApplicationFlow />
        </section>
      </main>
    </div>
  );
}
