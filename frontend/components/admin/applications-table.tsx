"use client";

import { Eye, FileSignature, Inbox, Loader2 } from "lucide-react";

import { StatusBadge } from "@/components/admin/status-badge";
import { formatDisplayDate } from "@/lib/format";
import {
  canGenerateContract,
  type Application,
} from "@/lib/types/application";

type ApplicationsTableProps = {
  applications: Application[];
  generatingId: string | null;
  onView: (application: Application) => void;
  onGenerate: (application: Application) => void;
};

export function ApplicationsTable({
  applications,
  generatingId,
  onView,
  onGenerate,
}: ApplicationsTableProps) {
  if (applications.length === 0) {
    return (
      <div className="flex flex-col items-center rounded-xl border border-dashed border-slate-200 bg-white px-6 py-16 text-center">
        <span className="flex h-11 w-11 items-center justify-center rounded-full bg-slate-50 text-slate-400 ring-1 ring-slate-200">
          <Inbox className="h-5 w-5" aria-hidden />
        </span>
        <h3 className="mt-4 text-sm font-semibold text-slate-900">
          No applications yet
        </h3>
        <p className="mt-1 max-w-sm text-sm text-slate-500">
          New student submissions will appear here for review and contract
          generation.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-[0_1px_2px_rgb(15_23_42/0.04)]">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-slate-100 bg-slate-50/80 text-[11px] font-medium uppercase tracking-wider text-slate-500">
            <tr>
              <th className="px-5 py-3 font-medium">Applicant</th>
              <th className="px-5 py-3 font-medium">Course</th>
              <th className="px-5 py-3 font-medium">Date</th>
              <th className="px-5 py-3 font-medium">Status</th>
              <th className="px-5 py-3 text-right font-medium">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {applications.map((application) => {
              const generating = generatingId === application.id;
              const eligible = canGenerateContract(application.status);
              return (
                <tr
                  key={application.id}
                  className="bg-white transition hover:bg-slate-50/70"
                >
                  <td className="px-5 py-3.5">
                    <p className="font-medium text-slate-900">
                      {application.applicant_name}
                    </p>
                    <p className="text-xs text-slate-400">{application.email}</p>
                  </td>
                  <td className="px-5 py-3.5 text-slate-700">
                    {application.course_name}
                  </td>
                  <td className="whitespace-nowrap px-5 py-3.5 text-slate-500">
                    {formatDisplayDate(application.created_at)}
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge status={application.status} />
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => onView(application)}
                        className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-50"
                      >
                        <Eye className="h-3.5 w-3.5" aria-hidden />
                        View
                      </button>
                      {eligible ? (
                        <button
                          type="button"
                          onClick={() => onGenerate(application)}
                          disabled={generating}
                          className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-2.5 py-1.5 text-xs font-medium text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
                        >
                          {generating ? (
                            <Loader2
                              className="h-3.5 w-3.5 animate-spin"
                              aria-hidden
                            />
                          ) : (
                            <FileSignature className="h-3.5 w-3.5" aria-hidden />
                          )}
                          {generating ? "Generating…" : "Generate Contract"}
                        </button>
                      ) : null}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
