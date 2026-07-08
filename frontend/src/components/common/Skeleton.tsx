export function Skeleton({ className = "", lines = 3 }: { className?: string; lines?: number }) {
  return (
    <div className={className}>
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="mb-2 h-3 w-full animate-pulse rounded bg-slate-100" />
      ))}
    </div>
  );
}
