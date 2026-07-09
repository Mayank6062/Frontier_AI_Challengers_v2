import { FileText } from "lucide-react";
import mermaid from "mermaid";
import { useEffect, useId } from "react";

import { Card } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { Loading } from "@/components/common/Loading";
import type { DisplayData, DisplaySection } from "@/types/workflow";

type DocumentViewerProps = {
  displayData?: DisplayData | null;
};

// Agent JSON isn't schema-enforced at the item level, so list/table values can
// arrive as strings, numbers, or nested objects/arrays depending on what the LLM returns.
function renderValue(value: unknown): string {
  if (typeof value === "string") return value;
  if (value === null || value === undefined) return "Not specified";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function renderSection(section: DisplaySection) {
  if (section?.items && Array.isArray(section.items) && section.items.length) {
    return (
      <ul className="list-disc space-y-2 pl-5 text-sm leading-6 text-slate-600">
        {section.items.map((item, index) => (
          <li key={typeof item === "string" ? item : index}>{renderValue(item)}</li>
        ))}
      </ul>
    );
  }

  if (section?.diagrams && Array.isArray(section.diagrams) && section.diagrams.length) {
    return (
      <div className="grid gap-3 lg:grid-cols-2">
        {section.diagrams.map((diagram, idx) => (
          <MermaidDiagram key={diagram.title + idx} title={diagram.title} code={diagram.code} />
        ))}
      </div>
    );
  }
  if (section?.rows) {
    const rows = Array.isArray(section.rows)
      ? (section.rows as unknown[]).map((row, index) => [`Item ${index + 1}`, String(row)])
      : Object.entries(section.rows as Record<string, unknown>);

    return (
      <div className="overflow-hidden rounded-md border border-slate-200">
        <table className="w-full text-left text-sm">
          <tbody className="divide-y divide-slate-200">
            {rows.map(([label, value]) => (
              <tr key={label}>
                <th className="w-1/3 bg-slate-50 px-4 py-3 font-medium text-slate-700">
                  {label}
                </th>
                <td className="px-4 py-3 text-slate-600">{renderValue(value)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return (
    <p className="text-sm leading-6 text-slate-600">
      {typeof section.content === "string" ? section.content : renderValue(section.content ?? "Not specified")}
    </p>
  );
}

export function DocumentViewer({ displayData }: DocumentViewerProps) {
  // Loading: displayData undefined (not yet received)
  if (displayData === undefined) {
    return (
      <Card className="overflow-hidden">
        <div className="p-6">
          <Loading />
        </div>
      </Card>
    );
  }

  // Empty: null or missing sections or empty object
  if (!displayData || !displayData.sections || !Array.isArray(displayData.sections) || displayData.sections.length === 0) {
    return (
      <Card className="overflow-hidden">
        <div className="p-6">
          <EmptyState title={displayData?.title ?? "No content"} description={displayData?.subtitle ?? "No display data available"} />
        </div>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden">
      <div className="border-b border-slate-200 bg-white p-5 sm:p-6">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-primary">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-slate-950">{displayData?.title ?? "Untitled"}</h2>
            {displayData?.subtitle ? (
              <p className="mt-1 text-sm text-slate-500">{displayData.subtitle}</p>
            ) : null}
          </div>
        </div>
      </div>
      <div className="divide-y divide-slate-100">
        {displayData.sections.map((section) => (
          <section key={section.heading ?? Math.random()} className="p-5 sm:p-6">
            <h3 className="mb-3 text-base font-semibold text-slate-950">{section.heading ?? "Section"}</h3>
            {renderSection(section)}
          </section>
        ))}
      </div>
    </Card>
  );
}

function MermaidDiagram({ title, code }: { title?: string; code?: string }) {
  const id = useId();
  const containerId = `mermaid-${id}`;

  useEffect(() => {
    if (!code) return;

    const isMermaid = /(?:graph|sequenceDiagram|classDiagram|gantt|flowchart|stateDiagram)/i.test(code) || /```mermaid/.test(code);
    if (!isMermaid) return;

    try {
      mermaid.initialize({ startOnLoad: false, securityLevel: "loose" });
      const renderCode = code.replace(/```mermaid\s*/i, "").replace(/```$/, "");
      // mermaid.render returns a Promise in modern mermaid versions
      Promise.resolve(mermaid.render(containerId, renderCode)).then((result: any) => {
        const svgCode = result?.svg ?? result;
        const el = document.getElementById(containerId);
        if (el) el.innerHTML = svgCode;
      });
    } catch (e) {
      // ignore render errors and leave code block
    }
  }, [code, containerId]);

  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 p-4">
      {title ? <div className="mb-2 text-sm font-medium text-slate-700">{title}</div> : null}
      {code ? (
        <div>
          <div id={containerId} className="mermaid overflow-auto" />
          <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-xs text-slate-500">{code}</pre>
        </div>
      ) : (
        <div className="text-xs text-slate-500">Diagram placeholder</div>
      )}
    </div>
  );
}
