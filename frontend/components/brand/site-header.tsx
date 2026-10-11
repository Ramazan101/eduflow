import Link from "next/link";

import { LogoMark } from "@/components/brand/logo-mark";

export function SiteHeader() {
  return (
    <header className="border-b border-[var(--line)] bg-[#fffcf7]/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <LogoMark />
          <div className="leading-tight">
            <p className="text-sm font-semibold tracking-tight">EduFlow</p>
            <p className="text-[11px] font-medium uppercase tracking-[0.16em] text-[var(--muted)]">
              Admissions
            </p>
          </div>
        </Link>
        <nav className="flex items-center gap-5 text-sm">
          <Link href="/apply" className="font-medium text-[var(--ink)]">
            Apply
          </Link>
          <Link
            href="/admin/login"
            className="text-[var(--muted)] transition hover:text-[var(--ink)]"
          >
            Registrar
          </Link>
        </nav>
      </div>
    </header>
  );
}
