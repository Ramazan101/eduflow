import type { ApplicationStatus } from "@/lib/types/application";
import { cn } from "@/lib/utils";

const STATUS_STYLES: Record<
  ApplicationStatus,
  { label: string; className: string }
> = {
  NEW: {
    label: "New",
    className: "bg-slate-100 text-slate-700 ring-slate-200",
  },
  PENDING_REVIEW: {
    label: "Pending review",
    className: "bg-amber-50 text-amber-800 ring-amber-200",
  },
  CONTRACT_GENERATED: {
    label: "Contract generated",
    className: "bg-emerald-50 text-emerald-800 ring-emerald-200",
  },
  ACCEPTED: {
    label: "Accepted",
    className: "bg-sky-50 text-sky-800 ring-sky-200",
  },
  REJECTED: {
    label: "Rejected",
    className: "bg-rose-50 text-rose-700 ring-rose-200",
  },
};

type StatusBadgeProps = {
  status: ApplicationStatus;
  className?: string;
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const style = STATUS_STYLES[status];

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ring-1 ring-inset",
        style.className,
        className,
      )}
    >
      {style.label}
    </span>
  );
}
