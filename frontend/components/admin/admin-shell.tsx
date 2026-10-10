"use client";

import {
  GraduationCap,
  LayoutGrid,
  Menu,
  PanelLeftClose,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";

import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/admin", label: "Applications", icon: LayoutGrid },
];

type AdminShellProps = {
  children: ReactNode;
};

export function AdminShell({ children }: AdminShellProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();

  return (
    <div className="flex min-h-screen bg-[#f6f8fb]">
      {mobileOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-slate-900/30 lg:hidden"
          aria-label="Close navigation"
          onClick={() => setMobileOpen(false)}
        />
      ) : null}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex w-60 flex-col border-r border-slate-200 bg-white lg:static lg:translate-x-0",
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
        )}
      >
        <div className="flex h-14 items-center justify-between border-b border-slate-100 px-4">
          <Link href="/admin" className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 text-white">
              <GraduationCap className="h-4 w-4" aria-hidden />
            </span>
            <span className="text-sm font-semibold tracking-tight text-slate-900">
              EduFlow
            </span>
          </Link>
          <button
            type="button"
            className="rounded-md p-1 text-slate-400 hover:bg-slate-50 lg:hidden"
            onClick={() => setMobileOpen(false)}
            aria-label="Close sidebar"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 p-3">
          <p className="px-2 pb-2 text-[11px] font-medium uppercase tracking-[0.16em] text-slate-400">
            Workspace
          </p>
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  "flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium transition",
                  active
                    ? "bg-slate-900 text-white shadow-sm"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900",
                )}
              >
                <Icon className="h-4 w-4" aria-hidden />
                {label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-slate-100 p-4">
          <p className="text-xs font-medium text-slate-700">Admin</p>
          <p className="text-[11px] text-slate-400">Northstar Education</p>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-slate-200 bg-white/90 px-4 backdrop-blur lg:px-6">
          <div className="flex items-center gap-2">
            <button
              type="button"
              className="rounded-md p-1.5 text-slate-500 hover:bg-slate-50 lg:hidden"
              onClick={() => setMobileOpen(true)}
              aria-label="Open sidebar"
            >
              <Menu className="h-4 w-4" />
            </button>
            <div className="hidden items-center gap-1.5 text-slate-400 lg:flex">
              <PanelLeftClose className="h-3.5 w-3.5" aria-hidden />
              <span className="text-xs">Admin</span>
              <span className="text-slate-300">/</span>
              <span className="text-xs font-medium text-slate-700">
                Applications
              </span>
            </div>
          </div>
          <Link
            href="/apply"
            className="text-xs font-medium text-slate-500 transition hover:text-slate-900"
          >
            Student portal
          </Link>
        </header>
        <main className="flex-1 px-4 py-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
