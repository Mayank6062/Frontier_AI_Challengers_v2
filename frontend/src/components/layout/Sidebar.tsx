import { History, Settings, Upload, Workflow } from "lucide-react";
import { NavLink } from "react-router-dom";

import { cn } from "@/utils/cn";

const items = [
  { label: "Upload", href: "/", icon: Upload },
  { label: "Workspace", href: "/workspace", icon: Workflow },
  { label: "History", href: "/history", icon: History },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="border-b border-slate-200 bg-white lg:min-h-screen lg:w-64 lg:border-b-0 lg:border-r">
      <div className="hidden h-20 items-center border-b border-slate-200 px-6 lg:flex">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-sm font-bold text-white">
          AI
        </div>
      </div>
      <nav className="flex gap-2 overflow-x-auto p-3 lg:flex-col lg:p-4">
        {items.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.href}
              to={item.href}
              end={item.href === "/"}
              className={({ isActive }) =>
                cn(
                  "flex min-w-fit items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-950",
                  isActive && "bg-blue-50 text-primary",
                )
              }
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
