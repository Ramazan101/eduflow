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
      <label
        htmlFor={id}
        className="block text-sm font-medium text-slate-700"
      >
        {label}
      </label>
      {children}
      {error ? (
        <p id={`${id}-error`} role="alert" className="text-xs text-red-600">
          {error}
        </p>
      ) : hint ? (
        <p className="text-xs text-slate-400">{hint}</p>
      ) : null}
    </div>
  );
}

export const controlClassName = cn(
  "w-full rounded-lg border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition",
  "placeholder:text-slate-400",
  "hover:border-slate-300",
  "focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20",
  "disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-500",
);

export function controlClass(hasError: boolean): string {
  return cn(
    controlClassName,
    hasError &&
      "border-red-300 focus:border-red-500 focus:ring-red-500/20",
  );
}
