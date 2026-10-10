export function TableSkeleton({ rows = 8 }: { rows?: number }) {
  return (
    <div className="overflow-hidden rounded-xl border border-[var(--line)] bg-[#fffcf7]">
      <div className="h-10 animate-pulse bg-[#ece8de]/70" />
      <div className="divide-y divide-[var(--line)]">
        {Array.from({ length: rows }).map((_, row) => (
          <div key={row} className="h-14 animate-pulse bg-[#fffcf7]" />
        ))}
      </div>
    </div>
  );
}
