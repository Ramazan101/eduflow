import { Check, Clock3, FileText, Mail } from "lucide-react";
import type { ReactNode } from "react";

export function SuccessState() {
  return (
    <div
      className="rounded-2xl border border-teal-100 bg-white p-8 shadow-card sm:p-10"
      role="status"
      aria-live="polite"
    >
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-sky-500 to-teal-500 text-white shadow-sm">
        <Check className="h-7 w-7" strokeWidth={2.5} aria-hidden />
      </div>
      <h2 className="mt-6 text-center text-2xl font-semibold tracking-tight text-slate-900">
        Application received
      </h2>
      <p className="mx-auto mt-3 max-w-md text-center text-sm leading-6 text-slate-600">
        Your application has been received. We will prepare your contract
        shortly.
      </p>

      <ol className="mt-8 space-y-3">
        <NextStep
          icon={<Mail className="h-4 w-4" />}
          title="Confirmation"
          description="Our admissions team reviews your details."
        />
        <NextStep
          icon={<FileText className="h-4 w-4" />}
          title="Contract"
          description="A training agreement PDF is generated for signature."
        />
        <NextStep
          icon={<Clock3 className="h-4 w-4" />}
          title="Onboarding"
          description="Once accepted, you receive course access and next steps."
        />
      </ol>
    </div>
  );
}

function NextStep({
  icon,
  title,
  description,
}: {
  icon: ReactNode;
  title: string;
  description: string;
}) {
  return (
    <li className="flex gap-3 rounded-xl border border-slate-100 bg-slate-50/80 px-4 py-3">
      <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white text-teal-700 shadow-sm ring-1 ring-slate-200/80">
        {icon}
      </span>
      <div>
        <p className="text-sm font-medium text-slate-900">{title}</p>
        <p className="text-xs leading-5 text-slate-500">{description}</p>
      </div>
    </li>
  );
}
