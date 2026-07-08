import { useState } from "react";
import ReactMarkdown from "react-markdown";

import { Card } from "@/components/common/Card";
import { Button } from "@/components/common/Button";
import { cn } from "@/utils/cn";
import type { DisplayData } from "@/types/workflow";
import { EmptyState } from "@/components/common/EmptyState";
import { useWorkflow } from "@/hooks/useWorkflow";

type Tab = "overview" | "html" | "markdown" | "terraform";

export function OutputWorkspace({ displayData }: { displayData?: DisplayData | null }) {
  const [tab, setTab] = useState<Tab>("overview");
  const { workflowContext } = useWorkflow();
  const safeDisplayData = displayData ?? {
    title: "No output",
    subtitle: "No output available",
    sections: [],
  };

  const outputContext = (workflowContext && (workflowContext as any).output) || {};
  // downloads may live under outputContext.downloads or directly under outputContext
  const downloads = outputContext.downloads ?? outputContext ?? {};

  const html = String(downloads.html ?? "");
  const markdown = String(downloads.markdown ?? "");
  const terraform = String(downloads.terraform ?? "");

  return (
    <Card className="overflow-hidden">
      <div className="border-b border-slate-200 bg-white p-5 sm:p-6">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold text-slate-950">{safeDisplayData.title}</h2>
            {safeDisplayData.subtitle ? (
              <p className="mt-1 text-sm text-slate-500">{safeDisplayData.subtitle}</p>
            ) : null}
          </div>
        </div>
      </div>

      <div className="p-4 sm:p-6">
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <TabButton active={tab === "overview"} onClick={() => setTab("overview")}>
            Overview
          </TabButton>
          <TabButton active={tab === "html"} onClick={() => setTab("html")}>HTML Preview</TabButton>
          <TabButton active={tab === "markdown"} onClick={() => setTab("markdown")}>
            Markdown Preview
          </TabButton>
          <TabButton active={tab === "terraform"} onClick={() => setTab("terraform")}>
            Terraform Preview
          </TabButton>
        </div>

        <div>
          {tab === "overview" && (
            <div className="space-y-4">
                  {Array.isArray(safeDisplayData.sections) && safeDisplayData.sections.length > 0 ? (
                    safeDisplayData.sections.map((section) => (
                      <section key={section.heading ?? Math.random()} className="rounded-lg border border-slate-100 bg-white p-4">
                        <h3 className="mb-2 text-sm font-semibold text-slate-800">{section.heading ?? ""}</h3>
                        {section.content ? <p className="text-sm text-slate-600">{section.content}</p> : null}
                        {section.type === "download_card" && (
                          <div className="mt-3 flex flex-wrap gap-2">
                            {(section as any).downloads?.map((d: any) => (
                              <Button key={d.key} variant="secondary" onClick={() => {
                                if (d.key === 'html') setTab('html');
                                if (d.key === 'markdown') setTab('markdown');
                                if (d.key === 'terraform') setTab('terraform');
                              }}>{d.label}</Button>
                            ))}
                          </div>
                        )}
                      </section>
                    ))
                  ) : (
                    <EmptyState title={safeDisplayData.title} description={safeDisplayData.subtitle ?? "No output available"} />
                  )}
                </div>
          )}

          {tab === "html" && (
            <div className="h-[60vh] w-full overflow-hidden rounded-lg border border-slate-200">
              {html ? (
                <iframe
                  title="HTML Preview"
                  srcDoc={html}
                  sandbox="allow-same-origin"
                  className="h-full w-full bg-white"
                />
              ) : (
                <div className="p-6 text-sm text-slate-500">No HTML output available.</div>
              )}
            </div>
          )}

          {tab === "markdown" && (
            <div className="prose max-w-none rounded-lg border border-slate-200 bg-white p-6">
              {markdown ? (
                <ReactMarkdown>{markdown}</ReactMarkdown>
              ) : (
                <div className="text-sm text-slate-500">No Markdown output available.</div>
              )}
            </div>
          )}

          {tab === "terraform" && (
            <div>
              {terraform ? (
                <pre className="max-h-[60vh] overflow-auto rounded bg-slate-900 p-4 text-sm text-slate-100">
                  <code>{terraform}</code>
                </pre>
              ) : (
                <div className="p-6 text-sm text-slate-500">No Terraform output available.</div>
              )}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}

function TabButton({ active, children, onClick }: { active?: boolean; children: any; onClick?: () => void }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "inline-flex items-center rounded-md px-3 py-1 text-sm font-medium",
        active ? "bg-primary text-white" : "bg-white border border-slate-100 text-slate-700",
      )}
    >
      {children}
    </button>
  );
}
