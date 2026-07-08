import {
  CheckCircle2,
  Circle,
  Clock3,
  Search,
  BookOpen,
  Lightbulb,
  Layers,
  ShieldCheck,
  FileText,
} from "lucide-react";

import { cn } from "@/utils/cn";

const steps = ["Discovery", "Knowledge", "Recommendation", "Architecture", "Validation", "Output"];

const iconMap: Record<string, any> = {
  discovery: Search,
  knowledge: BookOpen,
  recommendation: Lightbulb,
  architecture: Layers,
  validation: ShieldCheck,
  output: FileText,
};

type WorkflowTimelineProps = {
  currentStep?: string;
};

export function WorkflowTimeline({ currentStep = "Discovery" }: WorkflowTimelineProps) {
  const currentIndex = steps.findIndex((step) => step.toLowerCase() === currentStep.toLowerCase());

  return (
    <div className="rounded-xl border border-slate-200 bg-card p-4 shadow-enterprise">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-slate-950">Workflow Timeline</h2>
          <p className="text-sm text-slate-500">Current AI architecture workflow stage</p>
        </div>
        <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-primary">{currentStep}</span>
      </div>
      <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
        {steps.map((step, index) => {
          const key = step.toLowerCase();
          const isComplete = currentIndex > index;
          const isActive = currentIndex === index;
          const StepIcon = isComplete ? CheckCircle2 : isActive ? Clock3 : iconMap[key] ?? Circle;

          return (
            <div
              key={step}
              className={cn(
                "flex items-center gap-3 rounded-lg border px-3 py-2 transition-opacity",
                isActive && "border-primary bg-blue-50 text-primary ring-1 ring-inset ring-primary/10",
                isComplete && "border-success bg-success/10 text-success",
                !isActive && !isComplete && "border-slate-200 bg-slate-50 text-slate-500",
              )}
            >
              <div className={cn("flex h-8 w-8 items-center justify-center rounded-md", isActive ? "bg-blue-100" : isComplete ? "bg-success/20" : "bg-transparent")}> 
                <StepIcon className="h-4 w-4 shrink-0" />
              </div>
              <span className="truncate text-sm font-medium">{step}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
