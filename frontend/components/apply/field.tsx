import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type FieldProps = {
  id: string;
  label: string;
  error?: string;
  hint?: string;
  children: ReactNode;
};

export function Field({ id, label, error, hint, children }: FieldProps) {
  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="block text-sm font-medium text-[var(--ink)]">
        {label}
      </label>
      {children}
      {error ? (
        <p id={`${id}-error`} role="alert" className="text-xs text-[var(--danger)]">
          {error}
        </p>
      ) : hint ? (
        <p className="text-xs text-[var(--muted)]">{hint}</p>
      ) : null}
    </div>
  );
}

export const controlClassName = cn(
  "w-full rounded-md border border-[var(--line)] bg-white px-3.5 py-2.5 text-sm text-[var(--ink)] shadow-sm outline-none transition",
  "placeholder:text-slate-400",
  "hover:border-[#c4bba9]",
  "focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent)]/15",
  "disabled:cursor-not-allowed disabled:bg-[#f7f4ee] disabled:text-[var(--muted)]",
);

export function controlClass(hasError: boolean): string {
  return cn(
    controlClassName,
    hasError && "border-red-300 focus:border-red-500 focus:ring-red-500/20",
  );
}
