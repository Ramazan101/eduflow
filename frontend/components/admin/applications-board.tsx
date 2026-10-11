"use client";

import { RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { ApplicationDetailModal } from "@/components/admin/application-detail-modal";
import { ApplicationsTable } from "@/components/admin/applications-table";
import { TableSkeleton } from "@/components/admin/table-skeleton";
import {
  ApiError,
  listApplications,
  listPrograms,
  listRequirementProfiles,
} from "@/lib/api";
import type {
  Application,
  ApplicationStatus,
  Program,
  RequirementProfile,
} from "@/lib/types/application";
import { cn } from "@/lib/utils";

const PAGE_SIZE = 20;

const STATUS_FILTERS: { label: string; value: ApplicationStatus | "ALL" }[] = [
  { label: "All", value: "ALL" },
  { label: "Received", value: "NEW" },
  { label: "In review", value: "PENDING_REVIEW" },
  { label: "Accepted", value: "ACCEPTED" },
  { label: "Not accepted", value: "REJECTED" },
];

type Counts = {
  total: number;
  NEW: number;
  PENDING_REVIEW: number;
  ACCEPTED: number;
  REJECTED: number;
};

const EMPTY_COUNTS: Counts = {
  total: 0,
  NEW: 0,
  PENDING_REVIEW: 0,
  ACCEPTED: 0,
  REJECTED: 0,
};

export function ApplicationsBoard() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [programs, setPrograms] = useState<Program[]>([]);
  const [profiles, setProfiles] = useState<RequirementProfile[]>([]);
  const [counts, setCounts] = useState<Counts>(EMPTY_COUNTS);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [statusFilter, setStatusFilter] = useState<ApplicationStatus | "ALL">(
    "ALL",
  );
  const [programFilter, setProgramFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [detailId, setDetailId] = useState<string | null>(null);

  const load = useCallback(async (options?: { silent?: boolean }) => {
    if (!options?.silent) {
      setLoading(true);
    }
    setError(null);
    try {
      const [page, allPrograms, allProfiles, all, received, review, accepted, rejected] =
        await Promise.all([
          listApplications({
            status: statusFilter === "ALL" ? undefined : statusFilter,
            program_id: programFilter || undefined,
            limit: PAGE_SIZE,
            offset,
          }),
          listPrograms(),
          listRequirementProfiles(),
          listApplications({ limit: 1 }),
          listApplications({ status: "NEW", limit: 1 }),
          listApplications({ status: "PENDING_REVIEW", limit: 1 }),
          listApplications({ status: "ACCEPTED", limit: 1 }),
          listApplications({ status: "REJECTED", limit: 1 }),
        ]);
      setApplications(page.items);
      setTotal(page.total);
      setPrograms(allPrograms);
      setProfiles(allProfiles);
      setCounts({
        total: all.total,
        NEW: received.total,
        PENDING_REVIEW: review.total,
        ACCEPTED: accepted.total,
        REJECTED: rejected.total,
      });
    } catch (err) {
      setApplications([]);
      setTotal(0);
      setCounts(EMPTY_COUNTS);
      setError(
        err instanceof ApiError ? err.message : "We could not load applications.",
      );
    } finally {
      if (!options?.silent) {
        setLoading(false);
      }
    }
  }, [offset, programFilter, statusFilter]);

  useEffect(() => {
    void load();
  }, [load]);

  const pageStart = total === 0 ? 0 : offset + 1;
  const pageEnd = Math.min(offset + PAGE_SIZE, total);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Applications</h1>
          <p className="mt-1 text-sm text-[var(--muted)]">
            Queue, history, and decisions from the live EduFlow API.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          className="inline-flex items-center gap-1.5 self-start rounded-md border border-[var(--line)] bg-[#fffcf7] px-3 py-1.5 text-xs font-medium"
        >
          <RefreshCw className="h-3.5 w-3.5" aria-hidden />
          Refresh
        </button>
      </div>

      <div className="grid gap-3 sm:grid-cols-4">
        <Metric label="In queue" value={counts.total} />
        <Metric label="Received" value={counts.NEW} />
        <Metric label="In review" value={counts.PENDING_REVIEW} />
        <Metric label="Decided" value={counts.ACCEPTED + counts.REJECTED} />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {STATUS_FILTERS.map((filter) => {
          const active = statusFilter === filter.value;
          return (
            <button
              key={filter.value}
              type="button"
              onClick={() => {
                setOffset(0);
                setStatusFilter(filter.value);
              }}
              className={cn(
                "rounded-full px-3 py-1 text-xs font-medium ring-1",
                active
                  ? "bg-[var(--ink)] text-[#f7f4ee] ring-[var(--ink)]"
                  : "bg-[#fffcf7] text-[var(--muted)] ring-[var(--line)]",
              )}
            >
              {filter.label}
            </button>
          );
        })}
        <select
          aria-label="Filter by programme"
          value={programFilter}
          onChange={(event) => {
            setOffset(0);
            setProgramFilter(event.target.value);
          }}
          className="rounded-full border border-[var(--line)] bg-[#fffcf7] px-3 py-1 text-xs"
        >
          <option value="">All programmes</option>
          {programs.map((program) => (
            <option key={program.id} value={program.id}>
              {program.name}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <TableSkeleton />
      ) : error ? (
        <div className="rounded-xl border border-[var(--line)] bg-[#fffcf7] px-6 py-12 text-center">
          <p className="text-sm font-medium">Couldn’t load applications</p>
          <p className="mt-1 text-sm text-[var(--muted)]">{error}</p>
          <button
            type="button"
            onClick={() => void load()}
            className="mt-4 rounded-md bg-[var(--ink)] px-3 py-1.5 text-xs font-medium text-[#f7f4ee]"
          >
            Try again
          </button>
        </div>
      ) : (
        <>
          <ApplicationsTable
            applications={applications}
            programs={programs}
            onView={(application) => setDetailId(application.id)}
          />
          <div className="flex items-center justify-between text-xs text-[var(--muted)]">
            <p>
              {total === 0 ? "0 applications" : `${pageStart}–${pageEnd} of ${total}`}
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={offset <= 0}
                onClick={() => setOffset((value) => Math.max(0, value - PAGE_SIZE))}
                className="rounded-md border border-[var(--line)] bg-[#fffcf7] px-2.5 py-1 font-medium disabled:opacity-40"
              >
                Previous
              </button>
              <button
                type="button"
                disabled={offset + PAGE_SIZE >= total}
                onClick={() => setOffset((value) => value + PAGE_SIZE)}
                className="rounded-md border border-[var(--line)] bg-[#fffcf7] px-2.5 py-1 font-medium disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}

      <ApplicationDetailModal
        open={Boolean(detailId)}
        applicationId={detailId}
        programs={programs}
        profiles={profiles}
        onClose={() => setDetailId(null)}
        onChanged={() => void load({ silent: true })}
      />
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-[var(--line)] bg-[#fffcf7] px-4 py-3">
      <p className="text-[11px] font-medium uppercase tracking-wider text-[var(--muted)]">
        {label}
      </p>
      <p className="mt-1 text-2xl font-semibold tabular-nums">{value}</p>
    </div>
  );
}
