export function LogoMark({ className = "h-9 w-9" }: { className?: string }) {
  return (
    <span
      className={`inline-flex items-center justify-center rounded-md bg-[var(--accent)] text-[#f7f4ee] ${className}`}
      aria-hidden
    >
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M3 10.5 12 5l9 5.5-9 5.5L3 10.5Z" />
        <path d="M7 13v4.5c2 1.4 8 1.4 10 0V13" />
      </svg>
    </span>
  );
}
