type LoadingProps = {
  message?: string;
};

export function Loading({ message = "Loading workspace" }: LoadingProps) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-card p-4 text-sm text-slate-600">
      <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      <div className="flex-1">
        <div className="mb-1 font-medium text-slate-800">{message}</div>
        <div className="flex gap-2">
          <div className="h-2 w-24 animate-pulse rounded bg-slate-100" />
          <div className="h-2 w-16 animate-pulse rounded bg-slate-100" />
          <div className="h-2 w-32 animate-pulse rounded bg-slate-100" />
        </div>
      </div>
    </div>
  );
}
