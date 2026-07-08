import type { HTMLAttributes } from "react";

import { cn } from "@/utils/cn";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-xl border border-slate-200 bg-card shadow-enterprise transition-transform hover:-translate-y-1",
        className,
      )}
      {...props}
    />
  );
}
