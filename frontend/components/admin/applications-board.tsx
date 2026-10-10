"use client";

import { RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { ApplicationDetailModal } from "@/components/admin/application-detail-modal";
import { ApplicationsTable } from "@/components/admin/applications-table";
import { TableSkeleton } from "@/components/admin/table-skeleton";
import {
  ApiError,
  generateContract,
  getApplication,
  listApplications,
} from "@/lib/api";
import type {
  Application,
  ApplicationDetail,
  ApplicationStatus,
} from "@/lib/types/application";
import { cn } from "@/lib/utils";

const PAGE_SIZE = 20;

const STATUS_FILTERS: { label: string; value: ApplicationStatus | "ALL" }[] = [
  { label: "All", value: "ALL" },
  { label: "New", value: "NEW" },
  { label: "Pending", value: "PENDING_REVIEW" },
  { label: "Contract", value: "CONTRACT_GENERATED" },
  { label: "Accepted", value: "ACCEPTED" },
  { label: "Rejected", value: "REJECTED" },
];

export function ApplicationsBoard() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [statusFilter, setStatusFilter] = useState<ApplicationStatus | "ALL">(
    "ALL",
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [generatingId, setGeneratingId] = useState<string | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [detail, setDetail] = useState<ApplicationDetail | null>(null);

  const load = useCallback(async (options?: { silent?: boolean }) => {
    if (!options?.silent) {
      setLoading(true);
    }
    setError(null);
    try {
      const data = await listApplications({
        status: statusFilter === "ALL" ? undefined : statusFilter,
        limit: PAGE_SIZE,
        offset,
      });
      setApplications(data.items);
      setTotal(data.total);
    } catch (err) {
      setApplications([]);
      setTotal(0);
      setError(
        err instanceof ApiError
          ? err.message
          : "We could not load applications.",
      );
    } finally {
      if (!options?.silent) {
        setLoading(false);
      }
    }
  }, [offset, statusFilter]);

  useEffect(() => {
    void load();
  }, [load]);

  const openDetails = async (application: Application) => {
    setDetailOpen(true);
    setDetail(null);
    setDetailError(null);
    setDetailLoading(true);
    try {
      const data = await getApplication(application.id);
      setDetail(data);
    } catch (err) {
      setDetailError(
        err instanceof ApiError
          ? err.message
          : "We could not load this application.",
      );
    } finally {
      setDetailLoading(false);
    }
  };

  const handleGenerate = async (application: Application) => {
    setActionError(null);
    setGeneratingId(application.id);
    try {
      await generateContract(application.id);
      await load({ silent: true });
    } catch (err) {
      setActionError(
        err instanceof ApiError
          ? err.message
          : "We could not generate the contract.",
      );
    } finally {
      setGeneratingId(null);
    }
  };

  const pageStart = total === 0 ? 0 : offset + 1;
  const pageEnd = Math.min(offset + PAGE_SIZE, total);
  const canPrev = offset > 0;
  const canNext = offset + PAGE_SIZE < total;

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-slate-900">
            Applications
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Review incoming students and generate training contracts.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          className="inline-flex items-center gap-1.5 self-start rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-sm hover:bg-slate-50"
        >
          <RefreshCw className="h-3.5 w-3.5" aria-hidden />
          Refresh
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
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
                "rounded-full px-3 py-1 text-xs font-medium ring-1 transition",
                active
                  ? "bg-slate-900 text-white ring-slate-900"
                  : "bg-white text-slate-600 ring-slate-200 hover:bg-slate-50",
              )}
            >
              {filter.label}
            </button>
          );
        })}
      </div>

      {actionError ? (
        <p
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          {actionError}
        </p>
      ) : null}

      {loading ? (
        <TableSkeleton />
      ) : error ? (
        <div className="rounded-xl border border-slate-200 bg-white px-6 py-12 text-center">
          <p className="text-sm font-medium text-slate-900">
            Couldn’t load applications
          </p>
          <p className="mt-1 text-sm text-slate-500">{error}</p>
          <button
            type="button"
            onClick={() => void load()}
            className="mt-4 rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-medium text-white"
          >
            Try again
          </button>
        </div>
      ) : (
        <>
          <ApplicationsTable
            applications={applications}
            generatingId={generatingId}
            onView={(application) => void openDetails(application)}
            onGenerate={(application) => void handleGenerate(application)}
          />
          <div className="flex items-center justify-between text-xs text-slate-500">
            <p>
              {total === 0
                ? "0 applications"
                : `${pageStart}–${pageEnd} of ${total}`}
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={!canPrev}
                onClick={() => setOffset((value) => Math.max(0, value - PAGE_SIZE))}
                className="rounded-md border border-slate-200 bg-white px-2.5 py-1 font-medium text-slate-700 disabled:opacity-40"
              >
                Previous
              </button>
              <button
                type="button"
                disabled={!canNext}
                onClick={() => setOffset((value) => value + PAGE_SIZE)}
                className="rounded-md border border-slate-200 bg-white px-2.5 py-1 font-medium text-slate-700 disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}

      <ApplicationDetailModal
        open={detailOpen}
        loading={detailLoading}
        error={detailError}
        application={detail}
        onClose={() => setDetailOpen(false)}
      />
    </div>
  );
}
