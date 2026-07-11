import { FileText, Package } from "lucide-react";
import { Card } from "@/components/common/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { Loading } from "@/components/common/Loading";
import type { DisplayData, DisplaySection } from "@/types/workflow";
import {
  getHeadingIcon,
  isArchitectureDisplayData,
  isDiscoveryDisplayData,
  isOutputDisplayData,
  renderArchitectureSection,
} from "@/components/document/ArchitectureRenderer";
import {
  EnterpriseMermaidCard,
} from "@/components/document/EnterpriseMermaidCard";
 
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
      <div className="space-y-4">
        {section.diagrams.map((diagram, idx) => (
          <EnterpriseMermaidCard key={diagram.title + idx} title={diagram.title} code={diagram.code} />
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
 
  // ── Discovery Report Rendering ──────────────────────────────────
  const isDiscovery = isDiscoveryDisplayData(displayData.sections);
 
  // DEBUG: Log data structure
  if (isDiscovery) {
    console.log("🔍 DISCOVERY DATA RECEIVED:", {
      title: displayData.title,
      sectionCount: displayData.sections.length,
      sections: displayData.sections.map(s => ({
        heading: s.heading,
        type: (s as Record<string, unknown>).type,
        hasContent: !!s.content || !!(s as Record<string, unknown>).items || !!(s as Record<string, unknown>).data
      }))
    });
  }
 
  if (isDiscovery) {
    return (
      <Card className="overflow-hidden">
        {/* Header */}
        <div className="border-b border-slate-200 bg-gradient-to-r from-blue-50 to-indigo-50 p-5 sm:p-6">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-100 text-primary">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-slate-950">
                {displayData.title ?? "Requirement Discovery Report"}
              </h2>
              {displayData.subtitle ? (
                <p className="mt-1 text-sm text-slate-500">{displayData.subtitle}</p>
              ) : null}
            </div>
          </div>
        </div>
 
        {/* Sections */}
        <div className="divide-y divide-slate-100">
          {displayData.sections.map((section) => {
            const icon = getHeadingIcon(section.heading);
            return (
              <section
                key={section.heading ?? Math.random()}
                className="p-5 sm:p-6"
              >
                <div className="mb-4 flex items-center gap-2">
                  {icon}
                  <h3 className="text-base font-semibold text-slate-950">
                    {section.heading ?? "Section"}
                  </h3>
                </div>
                {renderArchitectureSection(section)}
              </section>
            );
          })}
        </div>
      </Card>
    );
  }
 
  // ── Architecture-specific rendering ──────────────────────────────
  const isArchitecture = isArchitectureDisplayData(displayData.sections);
 
  if (isArchitecture) {
    return (
      <Card className="overflow-hidden">
        {/* Header */}
        <div className="border-b border-slate-200 bg-gradient-to-r from-blue-50 to-indigo-50 p-5 sm:p-6">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-100 text-primary">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-slate-950">
                {displayData.title ?? "Architecture Design Report"}
              </h2>
              {displayData.subtitle ? (
                <p className="mt-1 text-sm text-slate-500">{displayData.subtitle}</p>
              ) : null}
            </div>
          </div>
        </div>
 
        {/* Sections */}
        <div className="divide-y divide-slate-100">
          {displayData.sections.map((section) => {
            const icon = getHeadingIcon(section.heading);
            return (
              <section
                key={section.heading ?? Math.random()}
                className="p-5 sm:p-6"
              >
                <div className="mb-4 flex items-center gap-2">
                  {icon}
                  <h3 className="text-base font-semibold text-slate-950">
                    {section.heading ?? "Section"}
                  </h3>
                </div>
                {renderArchitectureSection(section)}
              </section>
            );
          })}
        </div>
      </Card>
    );
  }
 
  // ── Output Package rendering (Enterprise Solution Packaging Engine) ───
  const isOutput = isOutputDisplayData(displayData.sections);
 
  if (isOutput) {
    return (
      <Card className="overflow-hidden border-indigo-100 shadow-lg">
        {/* Enterprise Header with premium gradient */}
        <div className="border-b border-indigo-200 bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 p-5 sm:p-6">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-md">
              <Package className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-slate-950">
                {displayData.title ?? "Enterprise Solution Package"}
              </h2>
              {displayData.subtitle ? (
                <p className="mt-1 text-sm text-slate-500">{displayData.subtitle}</p>
              ) : (
                <p className="mt-1 text-sm text-indigo-600">Consultant-Grade Architecture Deliverable</p>
              )}
            </div>
          </div>
        </div>
 
        {/* Sections with enhanced styling */}
        <div className="divide-y divide-slate-100">
          {displayData.sections.map((section) => {
            const icon = getHeadingIcon(section.heading);
            return (
              <section
                key={section.heading ?? Math.random()}
                className="p-5 sm:p-6"
              >
                <div className="mb-4 flex items-center gap-2">
                  {icon}
                  <h3 className="text-base font-semibold text-slate-950">
                    {section.heading ?? "Section"}
                  </h3>
                </div>
                {renderArchitectureSection(section)}
              </section>
            );
          })}
        </div>
      </Card>
    );
  }
 
  // ── Default rendering for non-architecture stages ────────────────
  // Use renderArchitectureSection for all reports (supports knowledge sections)
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
        {displayData.sections.map((section) => {
          const icon = getHeadingIcon(section.heading);
          return (
            <section key={section.heading ?? Math.random()} className="p-5 sm:p-6">
              <div className="mb-4 flex items-center gap-2">
                {icon}
                <h3 className="text-base font-semibold text-slate-950">{section.heading ?? "Section"}</h3>
              </div>
              {renderArchitectureSection(section)}
            </section>
          );
        })}
      </div>
    </Card>
  );
}
