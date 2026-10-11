import { STATUS_LABELS } from "@/lib/status";
import type { ApplicationStatus } from "@/lib/types/application";
import { cn } from "@/lib/utils";

const STATUS_STYLES: Record<ApplicationStatus, string> = {
  NEW: "bg-[#ece8de] text-[var(--ink)] ring-[#d8d1c3]",
  PENDING_REVIEW: "bg-amber-50 text-amber-900 ring-amber-200",
  ACCEPTED: "bg-[var(--accent-soft)] text-[var(--accent)] ring-[#c5d8d1]",
  REJECTED: "bg-rose-50 text-rose-800 ring-rose-200",
};

export function StatusBadge({
  status,
  className,
}: {
  status: ApplicationStatus;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ring-1 ring-inset",
        STATUS_STYLES[status],
        className,
      )}
    >
      {STATUS_LABELS[status]}
    </span>
  );
}
