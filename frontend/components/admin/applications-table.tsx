"use client";

import { Eye, Inbox } from "lucide-react";

import { StatusBadge } from "@/components/admin/status-badge";
import { formatDisplayDate } from "@/lib/format";
import type { Application, Program } from "@/lib/types/application";

type ApplicationsTableProps = {
  applications: Application[];
  programs: Program[];
  onView: (application: Application) => void;
};

export function ApplicationsTable({
  applications,
  programs,
  onView,
}: ApplicationsTableProps) {
  if (applications.length === 0) {
    return (
      <div className="flex flex-col items-center rounded-xl border border-dashed border-[var(--line)] bg-[#fffcf7] px-6 py-16 text-center">
        <Inbox className="h-6 w-6 text-[var(--muted)]" aria-hidden />
        <h3 className="mt-4 text-sm font-semibold">No applications in this view</h3>
        <p className="mt-1 max-w-sm text-sm text-[var(--muted)]">
          New submissions from the applicant portal will appear here.
        </p>
      </div>
    );
  }

  const programName = (id: string) =>
    programs.find((item) => item.id === id)?.name ?? "Programme";

  return (
    <div className="overflow-hidden rounded-xl border border-[var(--line)] bg-[#fffcf7]">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-[var(--line)] bg-[#ece8de]/60 text-[11px] font-medium uppercase tracking-wider text-[var(--muted)]">
            <tr>
              <th className="px-5 py-3 font-medium">Applicant</th>
              <th className="px-5 py-3 font-medium">Programme</th>
              <th className="px-5 py-3 font-medium">Submitted</th>
              <th className="px-5 py-3 font-medium">Status</th>
              <th className="px-5 py-3 text-right font-medium"> </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--line)]">
            {applications.map((application) => (
              <tr key={application.id} className="bg-[#fffcf7] hover:bg-white">
                <td className="px-5 py-3.5">
                  <p className="font-medium">{application.applicant_name}</p>
                  <p className="text-xs text-[var(--muted)]">{application.email}</p>
                </td>
                <td className="px-5 py-3.5">{programName(application.program_id)}</td>
                <td className="whitespace-nowrap px-5 py-3.5 text-[var(--muted)]">
                  {formatDisplayDate(application.created_at)}
                </td>
                <td className="px-5 py-3.5">
                  <StatusBadge status={application.status} />
                </td>
                <td className="px-5 py-3.5 text-right">
                  <button
                    type="button"
                    onClick={() => onView(application)}
                    className="inline-flex items-center gap-1.5 rounded-md border border-[var(--line)] bg-white px-2.5 py-1.5 text-xs font-medium hover:bg-[#f3efe6]"
                  >
                    <Eye className="h-3.5 w-3.5" aria-hidden />
                    Review
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
