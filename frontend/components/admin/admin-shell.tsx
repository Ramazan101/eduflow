"use client";

import { LayoutGrid, LogOut, Menu, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState, type ReactNode } from "react";

import { LogoMark } from "@/components/brand/logo-mark";
import { clearAdminToken } from "@/lib/session";
import { cn } from "@/lib/utils";

type AdminShellProps = {
  children: ReactNode;
};

export function AdminShell({ children }: AdminShellProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  const signOut = () => {
    clearAdminToken();
    router.replace("/admin/login");
  };

  return (
    <div className="flex min-h-screen bg-[var(--paper)]">
      {mobileOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-[var(--ink)]/30 lg:hidden"
          aria-label="Close navigation"
          onClick={() => setMobileOpen(false)}
        />
      ) : null}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex w-60 flex-col border-r border-[var(--line)] bg-[#fffcf7] lg:static lg:translate-x-0",
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
        )}
      >
        <div className="flex h-14 items-center justify-between border-b border-[var(--line)] px-4">
          <Link href="/admin" className="flex items-center gap-2.5">
            <LogoMark className="h-8 w-8" />
            <span className="text-sm font-semibold tracking-tight">EduFlow</span>
          </Link>
          <button
            type="button"
            className="rounded-md p-1 text-[var(--muted)] lg:hidden"
            onClick={() => setMobileOpen(false)}
            aria-label="Close sidebar"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        <nav className="flex-1 p-3">
          <p className="px-2 pb-2 text-[11px] font-medium uppercase tracking-[0.16em] text-[var(--muted)]">
            Workspace
          </p>
          <Link
            href="/admin"
            onClick={() => setMobileOpen(false)}
            className={cn(
              "flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm font-medium",
              pathname === "/admin"
                ? "bg-[var(--ink)] text-[#f7f4ee]"
                : "text-[var(--muted)] hover:bg-white",
            )}
          >
            <LayoutGrid className="h-4 w-4" aria-hidden />
            Applications
          </Link>
        </nav>
        <div className="border-t border-[var(--line)] p-3">
          <button
            type="button"
            onClick={signOut}
            className="flex w-full items-center gap-2 rounded-md px-2.5 py-2 text-sm text-[var(--muted)] hover:bg-white"
          >
            <LogOut className="h-4 w-4" aria-hidden />
            Sign out
          </button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-[var(--line)] bg-[#fffcf7]/90 px-4 backdrop-blur lg:px-6">
          <button
            type="button"
            className="rounded-md p-1.5 text-[var(--muted)] lg:hidden"
            onClick={() => setMobileOpen(true)}
            aria-label="Open sidebar"
          >
            <Menu className="h-4 w-4" />
          </button>
          <p className="hidden text-xs text-[var(--muted)] lg:block">
            Registrar workspace
          </p>
          <Link href="/apply" className="text-xs font-medium text-[var(--muted)] hover:text-[var(--ink)]">
            Applicant portal
          </Link>
        </header>
        <main className="flex-1 px-4 py-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
