import { Moon, UserCircle } from "lucide-react";

import { Button } from "@/components/common/Button";

export function Header() {
  return (
    <header className="flex min-h-20 items-center justify-between border-b border-slate-200 bg-white px-4 sm:px-6 lg:px-8">
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-slate-950">
          AI Architecture Assistant
        </h1>
        <p className="mt-1 text-sm text-slate-500">Enterprise Solution Accelerator</p>
      </div>
      <div className="flex items-center gap-2">
        <Button variant="ghost" className="hidden gap-2 sm:inline-flex" aria-label="Theme toggle">
          <Moon className="h-4 w-4" />
          Theme
        </Button>
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-600">
          <UserCircle className="h-6 w-6" />
        </div>
      </div>
    </header>
  );
}
