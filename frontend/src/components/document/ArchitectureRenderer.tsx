/**
 * Architecture-specific renderers for structured items returned by
 * the Architecture Agent.
 *
 * Enterprise-grade section renderer that supports:
 *  - Mermaid diagrams (via EnterpriseMermaidCard)
 *  - Executive infographic poster (via ExecutiveArchitecturePoster)
 *  - Rich metadata: key components, design decisions, principles,
 *    assumptions, and architect explanations
 */
 
import {
  ArrowRight,
  Box,
  CheckCircle2,
  ChevronDown,
  Cpu,
  Globe,
  Info,
  Layers,
  Lightbulb,
  Lock,
  Network,
  Server,
  Shield,
  Sparkles,
} from "lucide-react";
import { useState, type ReactNode } from "react";
 
import { cn } from "@/utils/cn";
import type { DisplaySection } from "@/types/workflow";
import {
  EnterpriseMermaidCard,
  EnterpriseMermaidSection,
  isMermaidSource,
  splitMermaidBlocks,
} from "@/components/document/EnterpriseMermaidCard";
import { ExecutiveArchitecturePoster } from "@/components/document/ExecutiveArchitecturePoster";
 
// ─── Tiny type guards ────────────────────────────────────────────────
 
function isObj(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}
 
function hasKeys<K extends string>(
  v: unknown,
  ...keys: K[]
): v is Record<K, unknown> {
  return isObj(v) && keys.every((k) => k in v);
}
 
// ─── Shape detectors ─────────────────────────────────────────────────
 
function isComponentItem(v: unknown): v is { component: string; description: string } {
  return hasKeys(v, "component", "description");
}
 
function isStepItem(v: unknown): v is { step: string; description: string } {
  return hasKeys(v, "step", "description");
}
 
function isResourceItem(v: unknown): v is { resource: string; purpose: string } {
  return hasKeys(v, "resource", "purpose");
}
 
function isDeploymentNode(
  v: unknown,
): v is { node: string; components: string[]; description: string } {
  return hasKeys(v, "node", "description") && ("components" in (v as Record<string, unknown>));
}
 
function isIntegrationItem(
  v: unknown,
): v is { source: string; target: string; integration_type: string; security: string } {
  return hasKeys(v, "source", "target");
}
 
function isAspectItem(v: unknown): v is { aspect: string; description: string } {
  return hasKeys(v, "aspect", "description");
}
 
// ─── Shared helpers ──────────────────────────────────────────────────
 
function safeString(v: unknown): string {
  if (typeof v === "string") return v;
  if (v === null || v === undefined) return "Not specified";
  if (typeof v === "object") return JSON.stringify(v, null, 2);
  return String(v);
}
 
function safeArray(v: unknown): unknown[] {
  if (Array.isArray(v)) return v;
  if (v === null || v === undefined) return [];
  return [v];
}
 
// ─── Per-heading icon map ────────────────────────────────────────────
 
const HEADING_ICON: Record<string, ReactNode> = {
  // Text sections
  "Executive Architecture Poster": <Sparkles className="h-5 w-5 text-indigo-500" />,
  "Architecture Summary": <Layers className="h-5 w-5 text-blue-600" />,
  "Current State": <Box className="h-5 w-5 text-slate-500" />,
  "Target State": <Layers className="h-5 w-5 text-emerald-500" />,
  "High Level Design": <Layers className="h-5 w-5 text-blue-500" />,
  "Low Level Design": <Cpu className="h-5 w-5 text-indigo-500" />,
  "Data Flow": <ArrowRight className="h-5 w-5 text-emerald-500" />,
  "Deployment View": <Server className="h-5 w-5 text-orange-500" />,
  "Integration View": <Globe className="h-5 w-5 text-cyan-500" />,
  "Security View": <Shield className="h-5 w-5 text-red-500" />,
  "Network View": <Network className="h-5 w-5 text-violet-500" />,
  "Infrastructure View": <Box className="h-5 w-5 text-amber-500" />,
 
  // ═══ 6 COMPREHENSIVE DIAGRAMS ═══
  "Overall Solution Architecture": <Layers className="h-5 w-5 text-blue-600" />,
  "Enterprise Architecture Design": <Sparkles className="h-5 w-5 text-indigo-600" />,
  "System Design": <Cpu className="h-5 w-5 text-violet-600" />,
  "Data Architecture": <ArrowRight className="h-5 w-5 text-emerald-600" />,
  "Platform Architecture": <Server className="h-5 w-5 text-orange-600" />,
  "Operations Architecture": <Shield className="h-5 w-5 text-cyan-600" />,
 
  // Legacy/backward compatibility
  "Architecture Diagram": <Layers className="h-5 w-5 text-blue-600" />,
};
 
export function getHeadingIcon(heading: string): ReactNode {
  return HEADING_ICON[heading] ?? null;
}
 
// ─── Card renderers ──────────────────────────────────────────────────
 
/** component + description → colored card */
function ComponentCard({ item }: { item: { component: string; description: string } }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md">
      <div className="mb-1 flex items-center gap-2">
        <span className="inline-block h-2 w-2 rounded-full bg-blue-500" />
        <h4 className="text-sm font-semibold text-slate-900">{item.component}</h4>
      </div>
      <p className="text-sm leading-relaxed text-slate-600">{item.description}</p>
    </div>
  );
}
 
/** aspect + description → security card */
function AspectCard({ item }: { item: { aspect: string; description: string } }) {
  return (
    <div className="rounded-lg border border-red-100 bg-red-50/40 p-4">
      <div className="mb-1 flex items-center gap-2">
        <Lock className="h-4 w-4 text-red-500" />
        <h4 className="text-sm font-semibold text-slate-900">{item.aspect}</h4>
      </div>
      <p className="text-sm leading-relaxed text-slate-600">{item.description}</p>
    </div>
  );
}
 
/** resource + purpose → two-column card */
function ResourceCard({ item }: { item: { resource: string; purpose: string } }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="grid grid-cols-[1fr_2fr] gap-4">
        <div>
          <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
            Resource
          </span>
          <p className="mt-1 text-sm font-semibold text-slate-900">{item.resource}</p>
        </div>
        <div>
          <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
            Purpose
          </span>
          <p className="mt-1 text-sm text-slate-600">{item.purpose}</p>
        </div>
      </div>
    </div>
  );
}
 
/** node + components[] + description → deployment card */
function DeploymentNodeCard({
  item,
}: {
  item: { node: string; components: unknown; description: string };
}) {
  const chips = safeArray(item.components).map(safeString);
 
  return (
    <div className="rounded-lg border border-orange-200 bg-orange-50/40 p-4">
      <div className="mb-2 flex items-center gap-2">
        <Server className="h-4 w-4 text-orange-500" />
        <h4 className="text-sm font-semibold text-slate-900">{item.node}</h4>
      </div>
      {chips.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-1.5">
          {chips.map((c, i) => (
            <span
              key={i}
              className="inline-flex items-center rounded-full bg-orange-100 px-2.5 py-0.5 text-xs font-medium text-orange-800"
            >
              {c}
            </span>
          ))}
        </div>
      )}
      <p className="text-sm leading-relaxed text-slate-600">{item.description}</p>
    </div>
  );
}
 
/** step + description → timeline row */
function StepTimeline({ items }: { items: { step: string; description: string }[] }) {
  return (
    <div className="relative space-y-0 pl-6">
      {/* vertical line */}
      <div className="absolute left-[11px] top-2 bottom-2 w-0.5 bg-emerald-200" />
      {items.map((item, i) => (
        <div key={i} className="relative pb-5 last:pb-0">
          {/* dot */}
          <div className="absolute -left-6 top-1 flex h-5 w-5 items-center justify-center rounded-full border-2 border-emerald-400 bg-white">
            <span className="text-[9px] font-bold text-emerald-600">{i + 1}</span>
          </div>
          <h4 className="text-sm font-semibold text-slate-900">{item.step}</h4>
          <p className="mt-0.5 text-sm leading-relaxed text-slate-600">{item.description}</p>
        </div>
      ))}
    </div>
  );
}
 
/** source → target integration table */
function IntegrationTable({
  items,
}: {
  items: { source: string; target: string; integration_type?: string; security?: string }[];
}) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-200">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 font-semibold text-slate-700">Source</th>
            <th className="px-4 py-3 font-semibold text-slate-700" />
            <th className="px-4 py-3 font-semibold text-slate-700">Target</th>
            <th className="px-4 py-3 font-semibold text-slate-700">Type</th>
            <th className="px-4 py-3 font-semibold text-slate-700">Security</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.map((row, i) => (
            <tr key={i} className="hover:bg-slate-50/60">
              <td className="px-4 py-3 font-medium text-slate-800">
                {safeString(row.source)}
              </td>
              <td className="px-2 py-3 text-center text-slate-400">→</td>
              <td className="px-4 py-3 font-medium text-slate-800">
                {safeString(row.target)}
              </td>
              <td className="px-4 py-3 text-slate-600">
                {safeString((row as Record<string, unknown>).integration_type ?? (row as Record<string, unknown>).type)}
              </td>
              <td className="px-4 py-3 text-slate-600">
                {safeString(row.security)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
 
// ─── Mermaid Diagram — delegated to EnterpriseMermaidCard ────────────
// The old MermaidDiagram component is replaced by EnterpriseMermaidCard
// which lives in EnterpriseMermaidCard.tsx and is imported above.
// Re-export for backward compatibility if anything else imports from here.
export { EnterpriseMermaidCard as MermaidDiagram } from "@/components/document/EnterpriseMermaidCard";
 
// ─── Generic object card (catches anything not matched above) ────────
 
function GenericObjectCard({ item }: { item: Record<string, unknown> }) {
  const entries = Object.entries(item).filter(
    ([, v]) => v !== null && v !== undefined && v !== "",
  );
 
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      {entries.map(([key, value]) => {
        const label = key
          .replace(/_/g, " ")
          .replace(/\b\w/g, (c) => c.toUpperCase());
 
        if (Array.isArray(value)) {
          return (
            <div key={key} className="mb-2 last:mb-0">
              <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
                {label}
              </span>
              <div className="mt-1 flex flex-wrap gap-1.5">
                {value.map((v, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700"
                  >
                    {safeString(v)}
                  </span>
                ))}
              </div>
            </div>
          );
        }
 
        return (
          <div key={key} className="mb-2 last:mb-0">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
              {label}
            </span>
            <p className="mt-0.5 text-sm text-slate-700">{safeString(value)}</p>
          </div>
        );
      })}
    </div>
  );
}
 
// ─── Single item dispatcher ──────────────────────────────────────────
 
function renderStructuredItem(item: unknown, idx: number): ReactNode {
  if (typeof item === "string") {
    // Could be a mermaid block
    if (isMermaidSource(item)) {
      return <EnterpriseMermaidSection key={idx} code={item} />;
    }
    return (
      <li key={idx} className="text-sm leading-relaxed text-slate-600">
        {item}
      </li>
    );
  }
 
  if (isComponentItem(item)) return <ComponentCard key={idx} item={item} />;
  if (isStepItem(item)) return null; // handled in batch via StepTimeline
  if (isResourceItem(item)) return <ResourceCard key={idx} item={item} />;
  if (isDeploymentNode(item)) return <DeploymentNodeCard key={idx} item={item} />;
  if (isIntegrationItem(item)) return null; // handled in batch via IntegrationTable
  if (isAspectItem(item)) return <AspectCard key={idx} item={item} />;
 
  if (isObj(item)) return <GenericObjectCard key={idx} item={item} />;
 
  return (
    <p key={idx} className="text-sm text-slate-600">
      {safeString(item)}
    </p>
  );
}
 
// ─── Public: Render an architecture section ──────────────────────────
 
/** Render a labeled chip group */
function ChipRow({
  label,
  items,
  colorClass,
  icon,
}: {
  label: string;
  items: string[];
  colorClass: string;
  icon?: ReactNode;
}) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <div className="flex items-center gap-1.5">
        {icon}
        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
          {label}
        </span>
      </div>
      <div className="mt-1.5 flex flex-wrap gap-1.5">
        {items.map((c, i) => (
          <span
            key={i}
            className={cn(
              "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
              colorClass,
            )}
          >
            {c}
          </span>
        ))}
      </div>
    </div>
  );
}
 
/** Render architect's explanation as a professional list */
function ExplanationList({ items }: { items: string[] }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50/60 p-4">
      <div className="mb-2 flex items-center gap-1.5">
        <Info className="h-3.5 w-3.5 text-blue-500" />
        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
          Architect's Rationale
        </span>
      </div>
      <ul className="space-y-1.5 text-sm leading-relaxed text-slate-700">
        {items.map((e, i) => (
          <li key={i} className="flex items-start gap-2">
            <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-500" />
            <span>{e}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
 
/** Collapsible section wrapper for metadata */
function CollapsibleSection({
  title,
  defaultOpen = true,
  children,
}: {
  title: string;
  defaultOpen?: boolean;
  children: ReactNode;
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
 
  return (
    <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center justify-between px-4 py-3 text-left transition-colors hover:bg-slate-50"
      >
        <span className="text-sm font-semibold text-slate-900">{title}</span>
        <ChevronDown
          className={cn(
            "h-4 w-4 text-slate-500 transition-transform",
            isOpen && "rotate-180",
          )}
        />
      </button>
      {isOpen && <div className="border-t border-slate-100 p-4">{children}</div>}
    </div>
  );
}
 
/** Render comprehensive diagram metadata (all enterprise fields) */
function DiagramMetadata({ metadata }: { metadata?: Record<string, unknown> }) {
  if (!metadata) return null;
  const components = Array.isArray(metadata.key_components)
    ? (metadata.key_components as string[]).filter(Boolean)
    : [];
  const decisions = Array.isArray(metadata.design_decisions)
    ? (metadata.design_decisions as string[]).filter(Boolean)
    : [];
  const businessBenefits = Array.isArray(metadata.business_benefits)
    ? (metadata.business_benefits as string[]).filter(Boolean)
    : [];
  const technicalBenefits = Array.isArray(metadata.technical_benefits)
    ? (metadata.technical_benefits as string[]).filter(Boolean)
    : [];
  const principles = Array.isArray(metadata.architecture_principles)
    ? (metadata.architecture_principles as string[]).filter(Boolean)
    : [];
  const risks = Array.isArray(metadata.risks)
    ? (metadata.risks as string[]).filter(Boolean)
    : [];
  const recommendations = Array.isArray(metadata.recommendations)
    ? (metadata.recommendations as string[]).filter(Boolean)
    : [];
  const componentExplanations = Array.isArray(metadata.component_explanations)
    ? (metadata.component_explanations as Record<string, unknown>[]).filter(Boolean)
    : [];
  const assumptions = Array.isArray(metadata.assumptions)
    ? (metadata.assumptions as string[]).filter(Boolean)
    : [];
  const explanation = Array.isArray(metadata.explanation)
    ? (metadata.explanation as string[]).filter(Boolean)
    : [];
 
  const hasMetadata =
    components.length || decisions.length || businessBenefits.length ||
    technicalBenefits.length || principles.length || risks.length ||
    recommendations.length || componentExplanations.length || assumptions.length || explanation.length;
 
  if (!hasMetadata) return null;
 
  return (
    <CollapsibleSection title="Architecture Details & Rationale" defaultOpen={false}>
      <div className="space-y-4">
        {/* Core Architecture Data */}
        {(components.length || decisions.length || principles.length || assumptions.length) && (
          <div className="grid gap-3 sm:grid-cols-2">
            <ChipRow
              label="Key Components"
              items={components}
              colorClass="bg-blue-50 text-blue-700 border border-blue-100"
              icon={<Cpu className="h-3 w-3 text-blue-500" />}
            />
            <ChipRow
              label="Design Decisions"
              items={decisions}
              colorClass="bg-amber-50 text-amber-800 border border-amber-100"
              icon={<Lightbulb className="h-3 w-3 text-amber-500" />}
            />
            <ChipRow
              label="Architecture Principles"
              items={principles}
              colorClass="bg-violet-50 text-violet-700 border border-violet-100"
              icon={<Sparkles className="h-3 w-3 text-violet-500" />}
            />
            <ChipRow
              label="Assumptions"
              items={assumptions}
              colorClass="bg-slate-50 text-slate-700 border border-slate-200"
              icon={<Info className="h-3 w-3 text-slate-500" />}
            />
          </div>
        )}
 
        {/* Business Value */}
        {businessBenefits.length > 0 && (
          <div className="rounded-lg border border-emerald-100 bg-emerald-50/60 p-3">
            <div className="mb-2 flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
              <span className="text-[10px] font-semibold uppercase tracking-wider text-emerald-700">
                Business Benefits
              </span>
            </div>
            <ul className="space-y-1 text-sm text-emerald-900">
              {businessBenefits.map((b, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-emerald-600">•</span>
                  <span>{b}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
 
        {/* Technical Value */}
        {technicalBenefits.length > 0 && (
          <div className="rounded-lg border border-blue-100 bg-blue-50/60 p-3">
            <div className="mb-2 flex items-center gap-1.5">
              <Cpu className="h-3.5 w-3.5 text-blue-600" />
              <span className="text-[10px] font-semibold uppercase tracking-wider text-blue-700">
                Technical Benefits
              </span>
            </div>
            <ul className="space-y-1 text-sm text-blue-900">
              {technicalBenefits.map((t, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-blue-600">•</span>
                  <span>{t}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
 
        {/* Component Explanations */}
        {componentExplanations.length > 0 && (
          <div className="space-y-2">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
              Component Explanations
            </span>
            <div className="space-y-2">
              {componentExplanations.map((comp, i) => {
                const name = safeString(comp.component || comp.name || `Component ${i + 1}`);
                const purpose = safeString(comp.purpose || "");
                const role = safeString(comp.role || "");
                const whySelected = safeString(comp.why_selected || comp.rationale || "");
                return (
                  <div key={i} className="rounded-lg border border-slate-200 bg-slate-50 p-2.5">
                    <h5 className="text-xs font-semibold text-slate-900">{name}</h5>
                    {purpose && <p className="mt-1 text-xs text-slate-600"><strong>Purpose:</strong> {purpose}</p>}
                    {role && <p className="mt-1 text-xs text-slate-600"><strong>Role:</strong> {role}</p>}
                    {whySelected && <p className="mt-1 text-xs text-slate-600"><strong>Why:</strong> {whySelected}</p>}
                  </div>
                );
              })}
            </div>
          </div>
        )}
 
        {/* Risks & Mitigations */}
        {risks.length > 0 && (
          <div className="rounded-lg border border-red-100 bg-red-50/60 p-3">
            <div className="mb-2 flex items-center gap-1.5">
              <Shield className="h-3.5 w-3.5 text-red-600" />
              <span className="text-[10px] font-semibold uppercase tracking-wider text-red-700">
                Risks & Mitigations
              </span>
            </div>
            <ul className="space-y-1 text-sm text-red-900">
              {risks.map((r, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-red-600">⚠️</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
 
        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div className="rounded-lg border border-cyan-100 bg-cyan-50/60 p-3">
            <div className="mb-2 flex items-center gap-1.5">
              <Lightbulb className="h-3.5 w-3.5 text-cyan-600" />
              <span className="text-[10px] font-semibold uppercase tracking-wider text-cyan-700">
                Recommendations
              </span>
            </div>
            <ul className="space-y-1 text-sm text-cyan-900">
              {recommendations.map((r, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-cyan-600">→</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
 
        {/* Architect's Rationale */}
        <ExplanationList items={explanation} />
      </div>
    </CollapsibleSection>
  );
}
 
export function renderArchitectureSection(section: DisplaySection): ReactNode {
  const items = section.items;
  const sectionAny = section as Record<string, unknown>;
  const sectionType = String(sectionAny.type ?? "");
 
  // 0 — Executive Poster
  if (sectionType === "executive_poster") {
    const poster = sectionAny.poster as any;
    if (!poster) return null;
    return (
      <div className="space-y-3">
        {section.content && typeof section.content === "string" && (
          <p className="text-sm leading-relaxed text-slate-600">{section.content}</p>
        )}
        <ExecutiveArchitecturePoster poster={poster} />
      </div>
    );
  }
 
  // 1 — Paragraph (text/description) sections — render content directly
  if (sectionType === "paragraph") {
    if (section.content) {
      // Check if content itself is mermaid
      if (typeof section.content === "string" && isMermaidSource(section.content)) {
        return <EnterpriseMermaidSection title={section.heading} code={section.content} />;
      }
      // Render as rich text paragraph (may contain markdown or structured content patterns)
      return <p className="text-sm leading-relaxed text-slate-600 whitespace-pre-wrap">{section.content}</p>;
    }
    return <p className="text-sm text-slate-400 italic">Not specified.</p>;
  }
 
  // 1b — Bullet list sections — render items as structured cards or list
  if (sectionType === "bullet_list") {
    if (items && Array.isArray(items) && items.length > 0) {
      // Detect if items are structured objects or plain strings
      if (items.every((i) => typeof i === "string")) {
        // All strings → render as bullet list
        return (
          <ul className="list-disc space-y-2 pl-5 text-sm leading-6 text-slate-600">
            {items.map((item, idx) => (
              <li key={idx}>{item as string}</li>
            ))}
          </ul>
        );
      }
     
      // Mixed or structured items → render as card grid for better visibility
      // Detect homogeneous item shapes for batch renders
      const firstObj = items.find(isObj);
 
      // All steps? → timeline
      if (firstObj && isStepItem(firstObj) && items.every(isStepItem)) {
        return <StepTimeline items={items as { step: string; description: string }[]} />;
      }
 
      // All integrations? → table
      if (firstObj && isIntegrationItem(firstObj) && items.every(isIntegrationItem)) {
        return (
          <IntegrationTable
            items={
              items as {
                source: string;
                target: string;
                integration_type: string;
                security: string;
              }[]
            }
          />
        );
      }
 
      // Structured items → card grid
      return (
        <div className="grid gap-3 sm:grid-cols-2">
          {items.map((item, idx) => renderStructuredItem(item, idx))}
        </div>
      );
    }
    // Empty bullet list → fallback to content if available
    if (section.content) {
      return <p className="text-sm leading-relaxed text-slate-600">{section.content}</p>;
    }
    return <p className="text-sm text-slate-400 italic">Not specified.</p>;
  }
 
  // 2 — Architecture Diagram section (mermaid + svg_layout + drawio_xml + metadata)
  const isDiagramSection =
    sectionType === "architecture_diagram" ||
    (section.diagrams && Array.isArray(section.diagrams) && section.diagrams.length > 0);
 
  if (isDiagramSection) {
    const metadata = sectionAny.metadata as Record<string, unknown> | undefined;
    const description =
      section.content && typeof section.content === "string" ? section.content : undefined;
    const businessSummary =
      sectionAny.business_summary && typeof sectionAny.business_summary === "string"
        ? sectionAny.business_summary
        : undefined;
 
    const hasMermaid =
      section.diagrams && Array.isArray(section.diagrams) && section.diagrams.length > 0;
 
    return (
      <div className="space-y-4">
        {/* Description + Business Summary */}
        {description && (
          <p className="text-sm leading-relaxed text-slate-600">{description}</p>
        )}
        {businessSummary && (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3">
            <p className="text-sm leading-relaxed text-emerald-900">
              <strong>Business Impact:</strong> {businessSummary}
            </p>
          </div>
        )}
 
        {/* Mermaid diagram(s) */}
        {hasMermaid &&
          section.diagrams!.map((d, i) => {
            const diagramAny = d as Record<string, unknown>;
            const code = diagramAny.code as string | undefined;
            const isValid = diagramAny.mermaid_valid !== false; // default to true if not specified
            const errors = diagramAny.mermaid_errors as string[] | undefined;
 
            // Skip rendering if diagram is marked invalid
            if (!isValid || !code) {
              if (!isValid && errors && errors.length > 0) {
                return (
                  <div key={`${d.title}-${i}`} className="rounded-lg border border-amber-200 bg-amber-50/60 p-4">
                    <div className="mb-2 flex items-center gap-2">
                      <Lightbulb className="h-4 w-4 text-amber-600" />
                      <h4 className="text-sm font-semibold text-amber-900">{d.title}</h4>
                    </div>
                    <p className="text-xs leading-relaxed text-amber-800 mb-2">
                      Diagram generation encountered issues and could not be rendered. The architecture analysis is complete, but this visualization requires adjustment.
                    </p>
                    <div className="text-xs text-amber-700 italic">
                      {errors.slice(0, 3).map((err, ei) => (
                        <div key={ei}>{err}</div>
                      ))}
                    </div>
                  </div>
                );
              }
              return null;
            }
 
            const blocks = splitMermaidBlocks(code);
            if (blocks.length === 0) return null;
            return blocks.map((block, bi) => (
              <EnterpriseMermaidCard
                key={`${d.title}-${i}-${bi}`}
                title={blocks.length > 1 ? `${d.title} (${bi + 1}/${blocks.length})` : d.title}
                code={block}
              />
            ));
          })}
 
 
        {/* Rich metadata */}
        <DiagramMetadata metadata={metadata} />
      </div>
    );
  }
 
  // 3 — Generic fallback: items exist but type not explicitly handled
  if (items && Array.isArray(items) && items.length > 0) {
    // Detect if items are structured objects or plain strings
    if (items.every((i) => typeof i === "string")) {
      // All strings → render as bullet list
      return (
        <ul className="list-disc space-y-2 pl-5 text-sm leading-6 text-slate-600">
          {items.map((item, idx) => (
            <li key={idx}>{item as string}</li>
          ))}
        </ul>
      );
    }
 
    // Detect homogeneous item shapes for batch renders
    const firstObj = items.find(isObj);
 
    // All steps? → timeline
    if (firstObj && isStepItem(firstObj) && items.every(isStepItem)) {
      return <StepTimeline items={items as { step: string; description: string }[]} />;
    }
 
    // All integrations? → table
    if (firstObj && isIntegrationItem(firstObj) && items.every(isIntegrationItem)) {
      return (
        <IntegrationTable
          items={
            items as {
              source: string;
              target: string;
              integration_type: string;
              security: string;
            }[]
          }
        />
      );
    }
 
    // Mixed or structured items → card grid
    return (
      <div className="grid gap-3 sm:grid-cols-2">
        {items.map((item, idx) => renderStructuredItem(item, idx))}
      </div>
    );
  }
 
  // 4 — Final fallback: no items and no explicit type handler
  if (section.content) {
    // Check if content itself is mermaid
    if (typeof section.content === "string" && isMermaidSource(section.content)) {
      return <EnterpriseMermaidSection title={section.heading} code={section.content} />;
    }
    return <p className="text-sm leading-relaxed text-slate-600">{section.content}</p>;
  }
 
  return <p className="text-sm text-slate-400 italic">Not specified.</p>;
}
 
// ─── Detect if DisplayData looks like Architecture ───────────────────
 
const ARCHITECTURE_HEADINGS = new Set([
  // Core text sections (new format)
  "Architecture Summary",
  "Current State",
  "Target State",
 
  // Legacy text sections
  "High Level Design",
  "Low Level Design",
  "Data Flow",
  "Deployment View",
  "Integration View",
  "Security View",
  "Network View",
  "Infrastructure View",
  "Architecture Diagram",
 
  // ═══ 6 COMPREHENSIVE DIAGRAMS ═══
  "Overall Solution Architecture",
  "Enterprise Architecture Design",
  "System Design",
  "Data Architecture",
  "Platform Architecture",
  "Operations Architecture",
]);
 
export function isArchitectureDisplayData(sections: DisplaySection[]): boolean {
  if (!sections || sections.length < 3) return false;
  return sections.some((s) => ARCHITECTURE_HEADINGS.has(s.heading));
}