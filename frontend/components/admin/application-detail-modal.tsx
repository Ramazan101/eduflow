"use client";

import { Loader2, X } from "lucide-react";
import { useEffect, useState } from "react";

import { StatusBadge } from "@/components/admin/status-badge";
import {
  ApiError,
  changeApplicationStatus,
  downloadDocument,
  generateDocument,
  getApplication,
  listDocuments,
} from "@/lib/api";
import { formatDateTime, formatDisplayDate } from "@/lib/format";
import { nextStatusActions, STATUS_LABELS } from "@/lib/status";
import type {
  ApplicationDetail,
  DocumentMetadata,
  Program,
  RequirementProfile,
} from "@/lib/types/application";

type ApplicationDetailModalProps = {
  open: boolean;
  applicationId: string | null;
  programs: Program[];
  profiles: RequirementProfile[];
  onClose: () => void;
  onChanged: () => void;
};

export function ApplicationDetailModal({
  open,
  applicationId,
  programs,
  profiles,
  onClose,
  onChanged,
}: ApplicationDetailModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detail, setDetail] = useState<ApplicationDetail | null>(null);
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [busy, setBusy] = useState(false);

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

  useEffect(() => {
    if (!open || !applicationId) {
      return;
    }
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [application, docs] = await Promise.all([
          getApplication(applicationId),
          listDocuments(applicationId),
        ]);
        if (!cancelled) {
          setDetail(application);
          setDocuments(docs);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? err.message
              : "We could not load this application.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, [open, applicationId]);

  if (!open) {
    return null;
  }

  const programName =
    programs.find((item) => item.id === detail?.program_id)?.name ?? "Programme";
  const profileName =
    profiles.find((item) => item.id === detail?.requirement_profile_id)?.name ??
    "Requirements";

  const runStatus = async (confirmText: string, next: ApplicationDetail["status"]) => {
    if (!detail) {
      return;
    }
    if (!window.confirm(confirmText)) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const updated = await changeApplicationStatus(detail.id, next);
      setDetail(updated);
      onChanged();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Status change failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto px-4 py-10 sm:items-center">
      <button
        type="button"
        className="fixed inset-0 bg-[var(--ink)]/40"
        aria-label="Close details"
        onClick={onClose}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="application-detail-title"
        className="relative z-10 w-full max-w-lg rounded-xl border border-[var(--line)] bg-[#fffcf7] shadow-xl"
      >
        <div className="flex items-start justify-between border-b border-[var(--line)] px-5 py-4">
          <div>
            <p className="text-[11px] font-medium uppercase tracking-[0.16em] text-[var(--muted)]">
              Application
            </p>
            <h2 id="application-detail-title" className="mt-1 text-base font-semibold">
              {detail?.applicant_name ?? "Details"}
            </h2>
          </div>
          <button type="button" onClick={onClose} className="rounded-md p-1 text-[var(--muted)]" aria-label="Close">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="max-h-[75vh] space-y-5 overflow-y-auto px-5 py-5">
          {loading ? (
            <div className="flex items-center gap-2 text-sm text-[var(--muted)]">
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              Loading application…
            </div>
          ) : error ? (
            <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
              {error}
            </p>
          ) : detail ? (
            <>
              <div className="flex items-center justify-between gap-3">
                <StatusBadge status={detail.status} />
                <p className="text-xs text-[var(--muted)]">
                  Submitted {formatDateTime(detail.created_at)}
                </p>
              </div>
              <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
                <Detail label="Email" value={detail.email} />
                <Detail label="Phone" value={detail.phone} />
                <Detail label="Date of birth" value={formatDisplayDate(detail.birth_date)} />
                <Detail label="Programme" value={programName} />
                <Detail label="Requirement profile" value={profileName} />
              </dl>

              <section>
                <h3 className="text-[11px] font-medium uppercase tracking-wider text-[var(--muted)]">
                  Status history
                </h3>
                <ol className="mt-2 space-y-2">
                  {detail.status_history.map((entry) => (
                    <li key={entry.id} className="rounded-md border border-[var(--line)] bg-white px-3 py-2 text-sm">
                      <p className="font-medium">
                        {entry.from_status
                          ? STATUS_LABELS[entry.from_status]
                          : "Submitted"}{" "}
                        → {STATUS_LABELS[entry.to_status]}
                      </p>
                      <p className="text-xs text-[var(--muted)]">
                        {formatDateTime(entry.created_at)}
                        {entry.note ? ` · ${entry.note}` : ""}
                      </p>
                    </li>
                  ))}
                </ol>
              </section>

              <section className="space-y-2">
                <h3 className="text-[11px] font-medium uppercase tracking-wider text-[var(--muted)]">
                  Decision
                </h3>
                <div className="flex flex-wrap gap-2">
                  {nextStatusActions(detail.status).map((action) => (
                    <button
                      key={action.status}
                      type="button"
                      disabled={busy}
                      onClick={() => void runStatus(action.confirm, action.status)}
                      className={
                        action.tone === "danger"
                          ? "rounded-md border border-rose-200 px-3 py-1.5 text-xs font-medium text-rose-800 disabled:opacity-60"
                          : "rounded-md bg-[var(--ink)] px-3 py-1.5 text-xs font-medium text-[#f7f4ee] disabled:opacity-60"
                      }
                    >
                      {action.label}
                    </button>
                  ))}
                  {nextStatusActions(detail.status).length === 0 ? (
                    <p className="text-sm text-[var(--muted)]">This status is final in EduFlow.</p>
                  ) : null}
                </div>
              </section>

              <section>
                <h3 className="text-[11px] font-medium uppercase tracking-wider text-[var(--muted)]">
                  Demo document
                </h3>
                <p className="mt-1 text-xs text-[var(--muted)]">
                  Generating a PDF does not accept, enroll, or sign this application.
                </p>
                <button
                  type="button"
                  disabled={busy}
                  onClick={async () => {
                    setBusy(true);
                    setError(null);
                    try {
                      await generateDocument(detail.id);
                      setDocuments(await listDocuments(detail.id));
                    } catch (err) {
                      setError(
                        err instanceof ApiError
                          ? err.message
                          : "Document generation failed.",
                      );
                    } finally {
                      setBusy(false);
                    }
                  }}
                  className="mt-2 rounded-md border border-[var(--line)] bg-white px-3 py-1.5 text-xs font-medium"
                >
                  Generate demo summary
                </button>
                <ul className="mt-3 space-y-2">
                  {documents.length === 0 ? (
                    <li className="text-sm text-[var(--muted)]">No files yet.</li>
                  ) : (
                    documents.map((doc) => (
                      <li
                        key={doc.id}
                        className="flex items-center justify-between gap-3 rounded-md border border-[var(--line)] bg-white px-3 py-2 text-sm"
                      >
                        <div>
                          <p className="font-medium">
                            {doc.template_key} {doc.template_version}
                          </p>
                          <p className="text-xs text-[var(--muted)]">
                            {doc.generation_status}
                            {doc.error_code ? ` · ${doc.error_code}` : ""}
                          </p>
                        </div>
                        {doc.generation_status === "SUCCESS" ? (
                          <button
                            type="button"
                            className="text-xs font-medium underline underline-offset-2"
                            onClick={() => void downloadDocument(detail.id, doc.id)}
                          >
                            Download
                          </button>
                        ) : null}
                      </li>
                    ))
                  )}
                </ul>
              </section>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-[11px] font-medium uppercase tracking-wider text-[var(--muted)]">
        {label}
      </dt>
      <dd className="mt-0.5">{value}</dd>
    </div>
  );
}
