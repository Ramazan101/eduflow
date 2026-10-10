import { GraduationCap } from "lucide-react";

export function SiteHeader() {
  return (
    <header className="border-b border-slate-200/80 bg-white/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <div className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-sky-600 to-teal-600 text-white shadow-sm">
            <GraduationCap className="h-5 w-5" aria-hidden />
          </span>
          <div className="leading-tight">
            <p className="text-sm font-semibold tracking-tight text-slate-900">
              EduFlow
            </p>
            <p className="text-[11px] font-medium uppercase tracking-[0.16em] text-slate-400">
              Enterprise onboarding
            </p>
          </div>
        </div>
        <p className="hidden text-sm text-slate-500 sm:block">
          Contract-ready student applications
        </p>
      </div>
    </header>
  );
}
