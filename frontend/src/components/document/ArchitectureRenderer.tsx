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
  AlertCircle,
  ArrowRight,
  Box,
  CheckCircle2,
  ChevronDown,
  Cpu,
  Globe,
  HelpCircle,
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
 
  // ═══ DISCOVERY REPORT SECTIONS ═══
  "Requirement Intelligence": <Sparkles className="h-5 w-5 text-blue-600" />,
  "Requirement Extraction": <Info className="h-5 w-5 text-indigo-600" />,
  "Functional Requirements": <CheckCircle2 className="h-5 w-5 text-emerald-600" />,
  "Non-Functional Requirements": <Layers className="h-5 w-5 text-orange-600" />,
  "Business Goals": <Lightbulb className="h-5 w-5 text-yellow-600" />,
  "Constraints": <Lock className="h-5 w-5 text-red-600" />,
  "Assumptions": <Box className="h-5 w-5 text-slate-600" />,
  "Ambiguity Detection": <AlertCircle className="h-5 w-5 text-amber-600" />,
  "Clarification Questions": <HelpCircle className="h-5 w-5 text-violet-600" />,
 
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
 
  // DEBUG: Log which renderer is executing
  if (sectionType.startsWith("requirement_") ||
      sectionType === "checklist" ||
      sectionType === "table" ||
      sectionType === "cards" ||
      sectionType === "alerts" ||
      sectionType === "questions") {
    console.log(`🎨 Rendering section: ${section.heading} (type: "${sectionType}")`);
  }
 
  // ─── DISCOVERY REPORT RENDERERS ───────────────────────────────
 
  // Requirement Intelligence (narrative with sections)
  if (sectionType === "requirement_intelligence") {
    const detailed = (sectionAny.detailed_sections as any[]) ?? [];
    return (
      <div className="space-y-4">
        {section.content && (
          <p className="text-sm leading-relaxed text-slate-600">{section.content}</p>
        )}
        {detailed.length > 0 && (
          <div className="space-y-3">
            {detailed.map((sec, idx) => (
              <div key={idx} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h4 className="text-sm font-semibold text-slate-900 mb-2">{sec.label}</h4>
                <p className="text-sm leading-relaxed text-slate-600">{sec.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }
 
  // Requirement Extraction (analysis narrative)
  if (sectionType === "requirement_extraction") {
    const analysis = (sectionAny.analysis_items as any[]) ?? [];
    return (
      <div className="space-y-4">
        {section.content && (
          <p className="text-sm leading-relaxed font-medium text-slate-700">{section.content}</p>
        )}
        {analysis.length > 0 && (
          <div className="space-y-3">
            {analysis.map((item, idx) => (
              <div key={idx} className="rounded-lg border border-blue-100 bg-blue-50/40 p-4">
                <h4 className="text-sm font-semibold text-blue-900 mb-1">{item.label}</h4>
                <p className="text-sm leading-relaxed text-blue-800">{item.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }
 
  // Checklist (Functional Requirements)
  if (sectionType === "checklist") {
    const items = (section as Record<string, unknown>).items as any[] ?? [];
    return (
      <div className="space-y-3">
        {section.content && (
          <p className="text-sm text-slate-600">{section.content}</p>
        )}
        {items.length > 0 ? (
          <div className="space-y-2">
            {items.map((item, idx) => (
              <div key={idx} className="rounded-lg border border-slate-200 bg-white p-3 flex gap-3">
                <input
                  type="checkbox"
                  disabled
                  className="mt-1 h-4 w-4 text-blue-500"
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-start gap-2 mb-1">
                    <span className="text-xs font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-700">{item.id}</span>
                    <h4 className="text-sm font-semibold text-slate-900">{item.title}</h4>
                    <span className={`text-xs font-medium px-2 py-0.5 rounded ${
                      item.priority === "High" ? "bg-red-100 text-red-700" :
                      item.priority === "Medium" ? "bg-yellow-100 text-yellow-700" :
                      "bg-green-100 text-green-700"
                    }`}>
                      {item.priority}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 mb-1">{item.description}</p>
                  <p className="text-xs text-slate-500 italic">Value: {item.business_value}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-400 italic">No requirements specified</p>
        )}
      </div>
    );
  }
 
  // Table (Non-Functional Requirements)
  if (sectionType === "table") {
    const columns = (sectionAny.columns as string[]) ?? [];
    const rows = (sectionAny.rows as any[][]) ?? [];
    return (
      <div className="space-y-3 overflow-x-auto">
        {section.content && (
          <p className="text-sm text-slate-600">{section.content}</p>
        )}
        {rows.length > 0 ? (
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b-2 border-slate-200">
                {columns.map((col) => (
                  <th key={col} className="text-left px-3 py-2 font-semibold text-slate-900 bg-slate-50">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, idx) => (
                <tr key={idx} className="border-b border-slate-200 hover:bg-slate-50/50">
                  {row.map((cell, cidx) => (
                    <td key={cidx} className="px-3 py-2 text-slate-600">{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-sm text-slate-400 italic">No requirements specified</p>
        )}
      </div>
    );
  }
 
  // Cards (Business Goals, Constraints, Assumptions)
  if (sectionType === "cards") {
    const items = (section as Record<string, unknown>).items as any[] ?? [];
    return (
      <div className="space-y-3">
        {section.content && (
          <p className="text-sm text-slate-600">{section.content}</p>
        )}
        {items.length > 0 ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {items.map((item, idx) => (
              <div key={idx} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
                <h4 className="text-sm font-semibold text-slate-900 mb-2">{item.title}</h4>
                {item.description && (
                  <p className="text-sm text-slate-600 mb-3">{item.description}</p>
                )}
                {item.metadata && Array.isArray(item.metadata) && (
                  <div className="space-y-1.5">
                    {item.metadata.map((meta, midx) => (
                      <div key={midx} className="text-xs">
                        <span className="font-medium text-slate-500">{meta.label}:</span>
                        <span className={`ml-1 ${meta.type === "badge" ? "inline-block px-1.5 py-0.5 rounded-full bg-blue-100 text-blue-700" : "text-slate-600"}`}>
                          {meta.value}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-400 italic">No items specified</p>
        )}
      </div>
    );
  }
 
  // Alerts (Ambiguity Detection)
  if (sectionType === "alerts") {
    const items = (section as Record<string, unknown>).items as any[] ?? [];
    return (
      <div className="space-y-3">
        {section.content && (
          <p className="text-sm text-slate-600">{section.content}</p>
        )}
        {items.length > 0 ? (
          <div className="space-y-2">
            {items.map((item, idx) => {
              const bgColor = item.level === "High" ? "border-red-200 bg-red-50" :
                             item.level === "Medium" ? "border-yellow-200 bg-yellow-50" :
                             "border-blue-200 bg-blue-50";
              const textColor = item.level === "High" ? "text-red-900" :
                               item.level === "Medium" ? "text-yellow-900" :
                               "text-blue-900";
              const badgeColor = item.level === "High" ? "bg-red-200 text-red-800" :
                                item.level === "Medium" ? "bg-yellow-200 text-yellow-800" :
                                "bg-blue-200 text-blue-800";
 
              return (
                <div key={idx} className={`rounded-lg border-l-4 ${bgColor} p-3`}>
                  <div className="flex items-start gap-2 mb-2">
                    <h4 className={`text-sm font-semibold ${textColor}`}>{item.title}</h4>
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded ${badgeColor}`}>{item.level}</span>
                  </div>
                  {item.description && (
                    <p className={`text-sm ${textColor} mb-2`}>{item.description}</p>
                  )}
                  {item.metadata && Array.isArray(item.metadata) && (
                    <div className="space-y-1">
                      {item.metadata.map((meta, midx) => (
                        <div key={midx} className={`text-xs ${textColor}`}>
                          <span className="font-medium">{meta.label}:</span>
                          <span className="ml-1">{meta.value}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-sm text-slate-400 italic">No ambiguities specified</p>
        )}
      </div>
    );
  }
 
  // Questions (Clarification Questions)
  if (sectionType === "questions") {
    const items = (section as Record<string, unknown>).items as any[] ?? [];
    return (
      <div className="space-y-3">
        {section.content && (
          <p className="text-sm text-slate-600">{section.content}</p>
        )}
        {items.length > 0 ? (
          <div className="space-y-2">
            {items.map((item, idx) => (
              <div key={idx} className="rounded-lg border border-indigo-200 bg-indigo-50/40 p-4">
                <div className="flex items-start gap-2 mb-2">
                  <span className="text-lg font-bold text-indigo-600 min-w-fit">{idx + 1}.</span>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-indigo-900 mb-1">{item.question}</p>
                    <div className="space-y-1 text-xs text-indigo-700">
                      <p><span className="font-medium">Reason:</span> {item.reason}</p>
                      <p><span className="font-medium">Expected Outcome:</span> {item.expected_outcome}</p>
                      <p><span className="font-medium">Priority:</span>
                        <span className={`ml-1 font-semibold ${
                          item.priority === "High" ? "text-red-600" :
                          item.priority === "Medium" ? "text-yellow-600" :
                          "text-green-600"
                        }`}>{item.priority}</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-400 italic">No questions specified</p>
        )}
      </div>
    );
  }
 
  // ─── KNOWLEDGE AGENT RENDERERS ───────────────────────────────
 
  // Knowledge Retrieval (content items with descriptions)
  if (sectionType === "knowledge_summary") {
    const content = sectionAny.content as any[] | undefined;
    if (content && Array.isArray(content) && content.length > 0) {
      return (
        <div className="space-y-4">
          {content.map((item, idx) => (
            <div
              key={idx}
              className="rounded-lg border border-slate-200 bg-gradient-to-br from-slate-50 to-white p-4 shadow-sm hover:shadow-md transition-shadow"
            >
              <h4 className="mb-2 font-semibold text-slate-900">{item.title || `Context ${idx + 1}`}</h4>
              <p className="text-sm leading-relaxed text-slate-600">{item.description || "No details provided"}</p>
            </div>
          ))}
        </div>
      );
    }
    const businessSummary = sectionAny.business_summary as string | undefined;
    if (businessSummary) {
      return <p className="text-sm leading-relaxed text-slate-600">{businessSummary}</p>;
    }
    return <p className="text-sm text-slate-400 italic">No knowledge retrieval data available</p>;
  }

   
  // Objects List (Standards, Practices, Architectures, Technologies, Solutions)
  if (sectionType === "objects_list") {
    const items = sectionAny.items as any[] | undefined;
    if (items && Array.isArray(items) && items.length > 0) {
      // Detect heading to determine rendering style
      const heading = section.heading?.toLowerCase() || "";
     
      // Standards → card grid with business values
      if (heading.includes("standard")) {
        return (
          <div className="space-y-3">
            {items.map((item, idx) => (
              <div key={idx} className="rounded-lg border border-blue-200 bg-blue-50 p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h4 className="font-semibold text-slate-900">{item.name || item.title || `Item ${idx + 1}`}</h4>
                    <p className="mt-1 text-sm text-slate-600">{item.description || ""}</p>
                  </div>
                  {item.business_value && (
                    <div className="flex-shrink-0">
                      <span className="inline-block rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-900">
                        {item.business_value.substring(0, 20)}...
                      </span>
                    </div>
                  )}
                </div>
                {item.business_value && (
                  <p className="mt-2 text-xs leading-relaxed text-slate-600">{item.business_value}</p>
                )}
              </div>
            ))}
          </div>
        );
      }
 
      // Best Practices → card grid with benefits
      if (heading.includes("practice")) {
        return (
          <div className="grid gap-4 sm:grid-cols-2">
            {items.map((item, idx) => (
              <div key={idx} className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
                <h4 className="font-semibold text-slate-900">{item.title || `Practice ${idx + 1}`}</h4>
                <p className="mt-2 text-sm text-slate-600">{item.description || ""}</p>
                {item.benefit && (
                  <div className="mt-3 rounded bg-emerald-100 px-2 py-1">
                    <p className="text-xs font-medium text-emerald-900">✓ {item.benefit}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        );
      }
 
      // Reference Architectures → detailed cards
      if (heading.includes("architecture")) {
        return (
          <div className="space-y-4">
            {items.map((item, idx) => (
              <div key={idx} className="rounded-lg border border-purple-200 bg-purple-50 p-4">
                <h4 className="font-semibold text-slate-900">{item.name || `Architecture ${idx + 1}`}</h4>
                <div className="mt-3 space-y-2">
                  <div>
                    <span className="text-xs font-medium uppercase text-slate-500">Purpose</span>
                    <p className="mt-1 text-sm text-slate-600">{item.purpose || "Not specified"}</p>
                  </div>
                  <div>
                    <span className="text-xs font-medium uppercase text-slate-500">When to Use</span>
                    <p className="mt-1 text-sm text-slate-600">{item.when_to_use || "Not specified"}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        );
      }
 
      // Technology Catalog → tech stack cards with category badges
      if (heading.includes("technology")) {
        return (
          <div className="grid gap-4 sm:grid-cols-2">
            {items.map((item, idx) => (
              <div key={idx} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h4 className="font-semibold text-slate-900">{item.technology || `Tech ${idx + 1}`}</h4>
                  <span className="inline-block rounded bg-slate-200 px-2 py-1 text-xs font-medium text-slate-700">
                    {item.category || "Other"}
                  </span>
                </div>
                <p className="text-sm text-slate-600">{item.purpose || ""}</p>
                {item.reason_selected && (
                  <p className="mt-2 text-xs leading-relaxed text-slate-500">
                    <span className="font-medium">Why: </span>{item.reason_selected}
                  </p>
                )}
              </div>
            ))}
          </div>
        );
      }
 
      // Compliance Standards → impact-colored badges
      if (heading.includes("compliance")) {
        return (
          <div className="space-y-3">
            {items.map((item, idx) => {
              const impactColors: Record<string, string> = {
                Mandatory: "border-red-300 bg-red-50 text-red-900",
                High: "border-orange-300 bg-orange-50 text-orange-900",
                Medium: "border-yellow-300 bg-yellow-50 text-yellow-900",
                Low: "border-green-300 bg-green-50 text-green-900",
              };
              const colorClass = impactColors[item.impact] || impactColors.Medium;
             
              return (
                <div key={idx} className={`rounded-lg border p-4 ${colorClass}`}>
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold">{item.name || `Standard ${idx + 1}`}</h4>
                      <p className="mt-1 text-sm">{item.description || ""}</p>
                    </div>
                    <span className="flex-shrink-0 rounded-full px-3 py-1 text-xs font-bold">
                      {item.impact || "Medium"}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        );
      }
 
      // Previous Solutions → success stories
      if (heading.includes("solution")) {
        return (
          <div className="space-y-4">
            {items.map((item, idx) => (
              <div key={idx} className="rounded-lg border border-amber-200 bg-amber-50 p-4">
                <h4 className="font-semibold text-slate-900">{item.name || `Solution ${idx + 1}`}</h4>
                <p className="mt-2 text-sm text-slate-600">{item.description || ""}</p>
                {item.outcome && (
                  <div className="mt-3 rounded-md bg-amber-100 px-3 py-2">
                    <p className="text-xs font-medium text-amber-900">🎯 Outcome: {item.outcome}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        );
      }
 
      // Default: render as generic object grid
      return (
        <div className="grid gap-4 sm:grid-cols-2">
          {items.map((item, idx) => renderStructuredItem(item, idx))}
        </div>
      );
    }
    const businessSummary = sectionAny.business_summary as string | undefined;
    if (businessSummary) {
      return <p className="text-sm leading-relaxed text-slate-600">{businessSummary}</p>;
    }
    return <p className="text-sm text-slate-400 italic">No items available</p>;
  }
 
  // Knowledge Confidence → readiness meter with assessment
  if (sectionType === "confidence") {
    const overall = sectionAny.overall_confidence as string | undefined;
    const completeness = sectionAny.knowledge_completeness as string | undefined;
    const risk = sectionAny.risk_level as string | undefined;
    const recommendation = sectionAny.recommendation as string | undefined;
 
    // Parse percentage
    const confidenceNum = parseInt(overall?.replace("%", "") || "0", 10);
    const confidenceColor = confidenceNum >= 85 ? "bg-emerald-500" : confidenceNum >= 70 ? "bg-yellow-500" : "bg-orange-500";
    const completenessColor = completeness === "High" ? "text-emerald-600" : completeness === "Medium" ? "text-yellow-600" : "text-red-600";
    const riskColor = risk === "Low" ? "text-emerald-600" : risk === "Medium" ? "text-yellow-600" : "text-red-600";
 
    return (
      <div className="space-y-6">
        {/* Confidence Meter */}
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold text-slate-900">Overall Confidence</h4>
            <span className="text-3xl font-bold text-slate-900">{overall || "N/A"}</span>
          </div>
          <div className="h-3 w-full rounded-full bg-slate-200 overflow-hidden">
            <div
              className={`h-full transition-all ${confidenceColor}`}
              style={{ width: `${Math.min(confidenceNum, 100)}%` }}
            />
          </div>
        </div>
 
        {/* Status Grid */}
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg border border-slate-200 bg-white p-4">
            <span className="text-xs font-medium uppercase text-slate-500">Knowledge Completeness</span>
            <p className={`mt-2 text-lg font-bold ${completenessColor}`}>
              {completeness || "Not assessed"}
            </p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4">
            <span className="text-xs font-medium uppercase text-slate-500">Risk Level</span>
            <p className={`mt-2 text-lg font-bold ${riskColor}`}>
              {risk || "Not assessed"}
            </p>
          </div>
        </div>
 
        {/* Recommendation */}
        {recommendation && (
          <div className="rounded-lg border border-blue-300 bg-blue-50 p-4">
            <span className="text-xs font-medium uppercase text-blue-700">Recommendation</span>
            <p className="mt-2 text-sm font-medium text-blue-900">{recommendation}</p>
          </div>
        )}
      </div>
    );
  }
 
  // ─── RECOMMENDATION AGENT RENDERERS ──────────────────────────────
 
  // Architecture Pattern Cards
  if (sectionType === "pattern_cards") {
    const items = sectionAny.items as any[] | undefined;
    if (items && Array.isArray(items) && items.length > 0) {
      return (
        <div className="space-y-4">
          {items.map((item, idx) => (
            <div key={idx} className="rounded-lg border border-indigo-200 bg-indigo-50 p-4">
              <div className="flex items-start justify-between gap-4 mb-2">
                <h4 className="font-semibold text-slate-900">{item.name || `Pattern ${idx + 1}`}</h4>
                {item.priority && (
                  <span className={`inline-block rounded-full px-3 py-1 text-xs font-bold ${
                    item.priority === "Critical" ? "bg-red-100 text-red-900" :
                    item.priority === "High" ? "bg-orange-100 text-orange-900" :
                    "bg-yellow-100 text-yellow-900"
                  }`}>
                    {item.priority}
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-700 mb-3">{item.business_purpose}</p>
              <div className="space-y-2 text-sm">
                {item.why_recommended && (
                  <div>
                    <span className="font-medium text-slate-700">Why: </span>
                    <span className="text-slate-600">{item.why_recommended}</span>
                  </div>
                )}
                {item.when_to_use && (
                  <div>
                    <span className="font-medium text-slate-700">When: </span>
                    <span className="text-slate-600">{item.when_to_use}</span>
                  </div>
                )}
              </div>
              {item.trade_offs && Array.isArray(item.trade_offs) && item.trade_offs.length > 0 && (
                <div className="mt-3 pt-3 border-t border-indigo-200">
                  <p className="text-xs font-medium text-slate-600 mb-1">Trade-offs:</p>
                  <ul className="text-xs text-slate-600 space-y-0.5 pl-4">
                    {item.trade_offs.map((t: string, i: number) => (
                      <li key={i} className="list-disc">{t}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      );
    }
    return <p className="text-sm text-slate-400 italic">No recommendations available</p>;
  }
 
  // Technology Cards
  if (sectionType === "tech_cards") {
    const items = sectionAny.items as any[] | undefined;
    if (items && Array.isArray(items) && items.length > 0) {
      return (
        <div className="grid gap-4 sm:grid-cols-2">
          {items.map((item, idx) => (
            <div key={idx} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between gap-2 mb-2">
                <h4 className="font-semibold text-slate-900">{item.technology || `Tech ${idx + 1}`}</h4>
                {item.enterprise_fit && (
                  <span className={`inline-block rounded px-2 py-1 text-xs font-medium ${
                    item.enterprise_fit === "High" ? "bg-green-100 text-green-800" :
                    item.enterprise_fit === "Medium" ? "bg-blue-100 text-blue-800" :
                    "bg-gray-100 text-gray-800"
                  }`}>
                    {item.enterprise_fit}
                  </span>
                )}
              </div>
              {item.category && (
                <p className="text-xs font-medium text-slate-500 mb-2">📦 {item.category}</p>
              )}
              <p className="text-sm text-slate-600 mb-2">{item.purpose}</p>
              {item.reason_selected && (
                <p className="text-xs text-slate-500 mb-2"><span className="font-medium">Reason:</span> {item.reason_selected}</p>
              )}
              {item.business_value && (
                <div className="mt-3 rounded bg-slate-50 p-2">
                  <p className="text-xs font-medium text-slate-700">🎯 {item.business_value}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      );
    }
    return <p className="text-sm text-slate-400 italic">No recommendations available</p>;
  }
 
  // Decision Cards (Cloud, etc.)
  if (sectionType === "decision_cards") {
    const items = sectionAny.items as any[] | undefined;
    if (items && Array.isArray(items) && items.length > 0) {
      return (
        <div className="space-y-4">
          {items.map((item, idx) => (
            <div key={idx} className="rounded-lg border border-blue-200 bg-blue-50 p-4">
              <h4 className="font-semibold text-slate-900 mb-2">{item.cloud_platform || item.recommendation || `Decision ${idx + 1}`}</h4>
              {item.recommendation && (
                <p className="text-sm font-medium text-slate-700 mb-2">✓ {item.recommendation}</p>
              )}
              {item.why && (
                <p className="text-sm text-slate-600 mb-3">{item.why}</p>
              )}
              {item.benefits && Array.isArray(item.benefits) && item.benefits.length > 0 && (
                <div className="mb-3">
                  <p className="text-xs font-medium text-slate-700 mb-1">Benefits:</p>
                  <ul className="text-xs text-slate-600 space-y-1 pl-4">
                    {item.benefits.map((b: string, i: number) => (
                      <li key={i} className="list-disc">{b}</li>
                    ))}
                  </ul>
                </div>
              )}
              {item.business_impact && (
                <div className="rounded bg-blue-100 p-2">
                  <p className="text-xs font-medium text-blue-900">💼 {item.business_impact}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      );
    }
    return <p className="text-sm text-slate-400 italic">No recommendations available</p>;
  }
 
  // Comparison Cards (Build vs Buy)
  if (sectionType === "comparison_cards") {
    const items = sectionAny.items as any[] | undefined;
    if (items && Array.isArray(items) && items.length > 0) {
      return (
        <div className="space-y-4">
          {items.map((item, idx) => {
            const recColor = item.recommendation === "Build" ? "border-green-200 bg-green-50" :
                            item.recommendation === "Buy" ? "border-blue-200 bg-blue-50" :
                            "border-purple-200 bg-purple-50";
            return (
              <div key={idx} className={`rounded-lg border p-4 ${recColor}`}>
                <div className="flex items-start justify-between gap-4 mb-2">
                  <h4 className="font-semibold text-slate-900">{item.component || `Component ${idx + 1}`}</h4>
                  <span className={`inline-block rounded-full px-3 py-1 text-xs font-bold ${
                    item.recommendation === "Build" ? "bg-green-100 text-green-900" :
                    item.recommendation === "Buy" ? "bg-blue-100 text-blue-900" :
                    "bg-purple-100 text-purple-900"
                  }`}>
                    {item.recommendation || "Decision"}
                  </span>
                </div>
                {item.reason && (
                  <p className="text-sm text-slate-700 mb-3">{item.reason}</p>
                )}
                <div className="grid grid-cols-2 gap-3 text-xs">
                  {item.pros && Array.isArray(item.pros) && (
                    <div className="rounded bg-green-100/50 p-2">
                      <p className="font-medium text-green-900 mb-1">Pros:</p>
                      <ul className="text-green-800 space-y-0.5">
                        {item.pros.slice(0, 2).map((p: string, i: number) => (
                          <li key={i}>✓ {p}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {item.cons && Array.isArray(item.cons) && (
                    <div className="rounded bg-red-100/50 p-2">
                      <p className="font-medium text-red-900 mb-1">Cons:</p>
                      <ul className="text-red-800 space-y-0.5">
                        {item.cons.slice(0, 2).map((c: string, i: number) => (
                          <li key={i}>✗ {c}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
                {item.business_impact && (
                  <div className="mt-3 rounded border-t border-gray-300 pt-2">
                    <p className="text-xs font-medium text-slate-700">Impact: {item.business_impact}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      );
    }
    return <p className="text-sm text-slate-400 italic">No recommendations available</p>;
  }
 
  // Process Cards (Data Flow)
  if (sectionType === "process_cards") {
    const items = sectionAny.items as any[] | undefined;
    if (items && Array.isArray(items) && items.length > 0) {
      return (
        <div className="space-y-3">
          {items.map((item, idx) => (
            <div key={idx} className="rounded-lg border border-slate-200 bg-white p-4">
              <div className="flex gap-3">
                <div className="flex-shrink-0 flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-sm font-bold text-slate-700">
                  {idx + 1}
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-slate-900">{item.flow || `Flow ${idx + 1}`}</h4>
                  <p className="mt-1 text-sm text-slate-600">{item.description}</p>
                  {item.business_reason && (
                    <p className="mt-2 text-xs text-slate-500">
                      <span className="font-medium">Why:</span> {item.business_reason}
                    </p>
                  )}
                  {item.expected_outcome && (
                    <div className="mt-2 rounded bg-slate-50 p-2">
                      <p className="text-xs font-medium text-slate-700">→ {item.expected_outcome}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      );
    }
    return <p className="text-sm text-slate-400 italic">No recommendations available</p>;
  }
 
 // Integration Cards
  if (sectionType === "integration_cards") {
    const items = sectionAny.items as any[] | undefined;
    if (items && Array.isArray(items) && items.length > 0) {
      return (
        <div className="grid gap-4 sm:grid-cols-2">
          {items.map((item, idx) => (
            <div key={idx} className="rounded-lg border border-slate-200 bg-white p-4">
              <h4 className="font-semibold text-slate-900 mb-2">{item.integration_point || `Integration ${idx + 1}`}</h4>
              {item.method && (
                <p className="text-xs font-medium text-blue-700 mb-2">🔗 {item.method}</p>
              )}
              <p className="text-sm text-slate-600 mb-3">{item.purpose}</p>
              {item.business_impact && (
                <div className="rounded bg-blue-50 p-2">
                  <p className="text-xs font-medium text-blue-900">💼 {item.business_impact}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      );
    }
    return <p className="text-sm text-slate-400 italic">No recommendations available</p>;
  }
 
  // Security Cards
  if (sectionType === "security_cards") {
    const items = sectionAny.items as any[] | undefined;
    if (items && Array.isArray(items) && items.length > 0) {
      return (
        <div className="space-y-3">
          {items.map((item, idx) => (
            <div key={idx} className="rounded-lg border border-red-200 bg-red-50 p-4">
              <div className="flex items-start justify-between gap-4 mb-2">
                <h4 className="font-semibold text-slate-900">🔒 {item.security_control || `Control ${idx + 1}`}</h4>
              </div>
              <p className="text-sm text-slate-700 mb-3">{item.business_reason}</p>
              <div className="space-y-2 text-sm">
                {item.risk_reduction && (
                  <div className="rounded bg-red-100 px-2 py-1">
                    <p className="font-medium text-red-900">Risk Reduction: {item.risk_reduction}</p>
                  </div>
                )}
                {item.compliance_mapping && (
                  <div>
                    <span className="font-medium text-slate-700">Compliance:</span>{" "}
                    <span className="text-slate-600">{item.compliance_mapping}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      );
    }
    return <p className="text-sm text-slate-400 italic">No recommendations available</p>;
  }
 
  // Improvement Cards (Simplification)
  if (sectionType === "improvement_cards") {
    const items = sectionAny.items as any[] | undefined;
    if (items && Array.isArray(items) && items.length > 0) {
      return (
        <div className="space-y-3">
          {items.map((item, idx) => (
            <div key={idx} className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
              <h4 className="font-semibold text-slate-900 mb-2">✨ {item.recommendation || `Improvement ${idx + 1}`}</h4>
              {item.problem_solved && (
                <p className="text-sm text-slate-700 mb-2">
                  <span className="font-medium">Problem:</span> {item.problem_solved}
                </p>
              )}
              {item.business_value && (
                <div className="rounded bg-emerald-100 px-2 py-1 mb-2">
                  <p className="text-sm font-medium text-emerald-900">💰 {item.business_value}</p>
                </div>
              )}
              {item.expected_improvement && (
                <p className="text-xs text-slate-600">
                  <span className="font-medium">Expected:</span> {item.expected_improvement}
                </p>
              )}
            </div>
          ))}
        </div>
      );
    }
    return <p className="text-sm text-slate-400 italic">No recommendations available</p>;
  }
 
  // Optimization Cards (Cost)
  if (sectionType === "optimization_cards") {
    const items = sectionAny.items as any[] | undefined;
    if (items && Array.isArray(items) && items.length > 0) {
      return (
        <div className="space-y-3">
          {items.map((item, idx) => (
            <div key={idx} className="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
              <h4 className="font-semibold text-slate-900 mb-2">💵 {item.recommendation || `Optimization ${idx + 1}`}</h4>
              {item.estimated_impact && (
                <div className="rounded bg-yellow-100 px-2 py-1 mb-2">
                  <p className="text-sm font-bold text-yellow-900">{item.estimated_impact}</p>
                </div>
              )}
              {item.business_reason && (
                <p className="text-sm text-slate-700 mb-2">{item.business_reason}</p>
              )}
              {item.optimization_strategy && (
                <p className="text-xs text-slate-600">
                  <span className="font-medium">Strategy:</span> {item.optimization_strategy}
                </p>
              )}
            </div>
          ))}
        </div>
      );
    }
    return <p className="text-sm text-slate-400 italic">No recommendations available</p>;
  }
 
  // Risk Cards
  if (sectionType === "risk_cards") {
    const items = sectionAny.items as any[] | undefined;
    if (items && Array.isArray(items) && items.length > 0) {
      return (
        <div className="space-y-3">
          {items.map((item, idx) => {
            const priorityColors = {
              Critical: "border-red-300 bg-red-50",
              High: "border-orange-300 bg-orange-50",
              Medium: "border-yellow-300 bg-yellow-50",
            };
            const colorClass = priorityColors[item.priority as keyof typeof priorityColors] || priorityColors.Medium;
           
            return (
              <div key={idx} className={`rounded-lg border p-4 ${colorClass}`}>
                <div className="flex items-start justify-between gap-4 mb-2">
                  <h4 className="font-semibold text-slate-900">⚠️ {item.risk || `Risk ${idx + 1}`}</h4>
                  <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-bold ${
                    item.priority === "Critical" ? "bg-red-100 text-red-900" :
                    item.priority === "High" ? "bg-orange-100 text-orange-900" :
                    "bg-yellow-100 text-yellow-900"
                  }`}>
                    {item.priority || "Medium"}
                  </span>
                </div>
                <p className="text-sm text-slate-700 mb-2">{item.business_impact}</p>
                <div className="text-xs">
                  <span className="font-medium text-slate-700">Likelihood:</span> {item.likelihood}
                </div>
                {item.mitigation && (
                  <div className="mt-2 rounded bg-white/50 p-2">
                    <p className="text-xs font-medium text-slate-900">Mitigation: {item.mitigation}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      );
    }
    return <p className="text-sm text-slate-400 italic">No recommendations available</p>;
  }
 
  // Premium Candidate Cards
  if (sectionType === "candidate_cards") {
    const items = sectionAny.items as any[] | undefined;
    if (items && Array.isArray(items) && items.length > 0) {
      return (
        <div className="space-y-4">
          {items.map((item, idx) => (
            <div key={idx} className="rounded-lg border border-indigo-300 bg-gradient-to-br from-indigo-50 to-white p-5 shadow-md">
              <div className="flex items-start justify-between gap-4 mb-3">
                <h4 className="text-lg font-semibold text-indigo-900">{item.candidate_name || `Candidate ${idx + 1}`}</h4>
                {item.architecture_score && (
                  <div className="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-full bg-indigo-100">
                    <span className="text-lg font-bold text-indigo-900">{item.architecture_score}</span>
                  </div>
                )}
              </div>
             
              {item.overview && (
                <p className="text-sm text-slate-700 mb-3">{item.overview}</p>
              )}
             
              <div className="grid grid-cols-2 gap-3 mb-3 text-xs">
                {item.strengths && Array.isArray(item.strengths) && (
                  <div className="rounded bg-green-100 p-2">
                    <p className="font-semibold text-green-900 mb-1">Strengths</p>
                    <ul className="text-green-800 space-y-0.5">
                      {item.strengths.slice(0, 2).map((s: string, i: number) => (
                        <li key={i}>✓ {s}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {item.weaknesses && Array.isArray(item.weaknesses) && (
                  <div className="rounded bg-red-100 p-2">
                    <p className="font-semibold text-red-900 mb-1">Weaknesses</p>
                    <ul className="text-red-800 space-y-0.5">
                      {item.weaknesses.slice(0, 2).map((w: string, i: number) => (
                        <li key={i}>✗ {w}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
             
              {item.best_fit && (
                <div className="rounded bg-indigo-100 px-3 py-2 mb-2">
                  <p className="text-xs font-medium text-indigo-900">Best Fit: {item.best_fit}</p>
                </div>
              )}
             
              {item.recommendation && (
                <div className={`rounded px-3 py-2 text-xs font-medium ${
                  item.recommendation === "High" ? "bg-green-100 text-green-900" :
                  item.recommendation === "Medium" ? "bg-yellow-100 text-yellow-900" :
                  "bg-red-100 text-red-900"
                }`}>
                  Recommendation: {item.recommendation}
                </div>
              )}
            </div>
          ))}
        </div>
      );
    }
    return <p className="text-sm text-slate-400 italic">No candidates available</p>;
  }
 
  // Scoring Cards
  if (sectionType === "scoring_cards") {
    const items = sectionAny.items as any[] | undefined;
    const recommended = sectionAny.recommended_candidate as string | undefined;
   
    return (
      <div className="space-y-4">
        {recommended && (
          <div className="rounded-lg border-2 border-emerald-300 bg-emerald-50 p-4">
            <p className="text-sm font-semibold text-emerald-900">
              ⭐ Recommended: <span className="text-emerald-700">{recommended}</span>
            </p>
          </div>
        )}
       
        {items && Array.isArray(items) && items.length > 0 && (
          <div className="space-y-3">
            {items.map((item, idx) => {
              const scorePercent = Math.min(item.score || 0, 100);
              const scoreColor = scorePercent >= 80 ? "bg-green-500" : scorePercent >= 60 ? "bg-blue-500" : "bg-orange-500";
             
              return (
                <div key={idx} className="rounded-lg border border-slate-200 bg-white p-4">
                  <div className="flex items-center justify-between gap-3 mb-2">
                    <h4 className="font-semibold text-slate-900">{item.candidate_name || `Candidate ${idx + 1}`}</h4>
                    <span className="text-2xl font-bold text-slate-900">{item.score || 0}</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-slate-200 overflow-hidden mb-2">
                    <div className={`h-full ${scoreColor}`} style={{ width: `${scorePercent}%` }} />
                  </div>
                  {item.reasoning && (
                    <p className="text-xs text-slate-600">{item.reasoning}</p>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  }
 
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
 
// Discovery Report Headings
const DISCOVERY_HEADINGS = new Set([
  "Requirement Intelligence",
  "Requirement Extraction",
  "Functional Requirements",
  "Non-Functional Requirements",
  "Business Goals",
  "Constraints",
  "Assumptions",
  "Ambiguity Detection",
  "Clarification Questions",
]);
 
export function isDiscoveryDisplayData(sections: DisplaySection[]): boolean {
  if (!sections || sections.length < 3) return false;
  return sections.some((s) => DISCOVERY_HEADINGS.has(s.heading));
}