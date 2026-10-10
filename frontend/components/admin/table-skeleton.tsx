export function TableSkeleton({ rows = 8 }: { rows?: number }) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <div className="grid grid-cols-[1.4fr_1.1fr_0.8fr_1fr_1.1fr] gap-4 border-b border-slate-100 px-5 py-3">
        {Array.from({ length: 5 }).map((_, index) => (
          <div
            key={index}
            className="h-3 w-16 animate-pulse rounded bg-slate-100"
          />
        ))}
      </div>
      <div className="divide-y divide-slate-100">
        {Array.from({ length: rows }).map((_, row) => (
          <div
            key={row}
            className="grid grid-cols-[1.4fr_1.1fr_0.8fr_1fr_1.1fr] items-center gap-4 px-5 py-4"
          >
            <div className="space-y-2">
              <div className="h-3.5 w-36 animate-pulse rounded bg-slate-100" />
              <div className="h-3 w-28 animate-pulse rounded bg-slate-50" />
            </div>
            <div className="h-3.5 w-32 animate-pulse rounded bg-slate-100" />
            <div className="h-3.5 w-20 animate-pulse rounded bg-slate-100" />
            <div className="h-5 w-24 animate-pulse rounded-full bg-slate-100" />
            <div className="flex justify-end gap-2">
              <div className="h-8 w-16 animate-pulse rounded-lg bg-slate-100" />
              <div className="h-8 w-28 animate-pulse rounded-lg bg-slate-100" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
