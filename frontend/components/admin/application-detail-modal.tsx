"use client";

import { Loader2, X } from "lucide-react";
import { useEffect } from "react";

import { StatusBadge } from "@/components/admin/status-badge";
import { formatDateTime, formatDisplayDate } from "@/lib/format";
import type { ApplicationDetail } from "@/lib/types/application";

type ApplicationDetailModalProps = {
  open: boolean;
  loading: boolean;
  error: string | null;
  application: ApplicationDetail | null;
  onClose: () => void;
};

export function ApplicationDetailModal({
  open,
  loading,
  error,
  application,
  onClose,
}: ApplicationDetailModalProps) {
  useEffect(() => {
    if (!open) {
      return;
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto px-4 py-10 sm:items-center">
      <button
        type="button"
        className="fixed inset-0 bg-slate-900/40"
        aria-label="Close details"
        onClick={onClose}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="application-detail-title"
        className="relative z-10 w-full max-w-lg rounded-2xl border border-slate-200 bg-white shadow-2xl shadow-slate-900/10"
      >
        <div className="flex items-start justify-between border-b border-slate-100 px-5 py-4">
          <div>
            <p className="text-[11px] font-medium uppercase tracking-[0.16em] text-slate-400">
              Application
            </p>
            <h2
              id="application-detail-title"
              className="mt-1 text-base font-semibold text-slate-900"
            >
              {application?.applicant_name ?? "Details"}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1 text-slate-400 hover:bg-slate-50 hover:text-slate-700"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="px-5 py-5">
          {loading ? (
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              Loading application…
            </div>
          ) : error ? (
            <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          ) : application ? (
            <div className="space-y-5">
              <div className="flex items-center justify-between">
                <StatusBadge status={application.status} />
                <p className="text-xs text-slate-400">
                  Submitted {formatDateTime(application.created_at)}
                </p>
              </div>
              <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
                <Detail label="Email" value={application.email} />
                <Detail label="Phone" value={application.phone} />
                <Detail
                  label="Birth date"
                  value={formatDisplayDate(application.birth_date)}
                />
                <Detail label="Course" value={application.course_name} />
              </dl>
              {application.admin_notes ? (
                <div>
                  <p className="text-[11px] font-medium uppercase tracking-wider text-slate-400">
                    Admin notes
                  </p>
                  <p className="mt-1 text-sm text-slate-700">
                    {application.admin_notes}
                  </p>
                </div>
              ) : null}
              <div>
                <p className="text-[11px] font-medium uppercase tracking-wider text-slate-400">
                  Documents
                </p>
                {application.documents.length === 0 ? (
                  <p className="mt-1 text-sm text-slate-500">
                    No documents generated yet.
                  </p>
                ) : (
                  <ul className="mt-2 space-y-2">
                    {application.documents.map((document) => (
                      <li
                        key={document.id}
                        className="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2"
                      >
                        <p className="text-sm font-medium text-slate-800">
                          {document.doc_type === "CONTRACT"
                            ? "Training contract"
                            : "Questionnaire"}
                        </p>
                        <p className="truncate font-mono text-[11px] text-slate-400">
                          {document.file_path}
                        </p>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-[11px] font-medium uppercase tracking-wider text-slate-400">
        {label}
      </dt>
      <dd className="mt-0.5 text-slate-800">{value}</dd>
    </div>
  );
}
