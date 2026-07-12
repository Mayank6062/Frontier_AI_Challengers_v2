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
 
  // ═══ OUTPUT PACKAGE SECTIONS ═══
  "Package Manifest": <Sparkles className="h-5 w-5 text-indigo-600" />,
  "Executive Intelligence": <Lightbulb className="h-5 w-5 text-amber-600" />,
  "High-Level Design (Bullet)": <Layers className="h-5 w-5 text-blue-600" />,
  "Low-Level Design (Bullet)": <Cpu className="h-5 w-5 text-violet-600" />,
  "Security Architecture (Bullet)": <Shield className="h-5 w-5 text-red-600" />,
  "Deployment Architecture (Bullet)": <Server className="h-5 w-5 text-orange-600" />,
  "Pipeline Traceability": <CheckCircle2 className="h-5 w-5 text-emerald-600" />,
 
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
 
/** Render a list of component badge chips */
function ComponentBadges({ items }: { items: string[] }) {
  if (!items || items.length === 0) return null;
  return (
    <>
      {items.map((item, i) => (
        <span
          key={i}
          className="inline-flex items-center rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700 border border-blue-100"
        >
          {item}
        </span>
      ))}
    </>
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
    recommendations.length || componentExplanations.length ||
    assumptions.length || explanation.length;
 
  if (!hasMetadata) return null;
 
  return (
    <div className="space-y-3">
      {/* Component Explanations (Detailed Cards) */}
      {componentExplanations.length > 0 && (
        <CollapsibleSection title="Component Details" defaultOpen={true}>
          <div className="space-y-3">
            {componentExplanations.map((item, i) => {
              const comp = String(item.component ?? "Component");
              const expl = String(item.explanation ?? "");
              return (
                <div key={i} className="rounded-lg border border-slate-200 bg-white p-3">
                  <h4 className="text-sm font-semibold text-slate-900 mb-1">{comp}</h4>
                  <p className="text-sm leading-relaxed text-slate-600">{expl}</p>
                </div>
              );
            })}
          </div>
        </CollapsibleSection>
      )}
 
      {/* Business Benefits */}
      {businessBenefits.length > 0 && (
        <CollapsibleSection title="Business Benefits" defaultOpen={true}>
          <ul className="space-y-2 text-sm leading-relaxed text-slate-700">
            {businessBenefits.map((benefit, i) => (
              <li key={i} className="flex items-start gap-2">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                <span>{benefit}</span>
              </li>
            ))}
          </ul>
        </CollapsibleSection>
      )}
 
      {/* Technical Benefits */}
      {technicalBenefits.length > 0 && (
        <CollapsibleSection title="Technical Benefits" defaultOpen={false}>
          <ul className="space-y-2 text-sm leading-relaxed text-slate-700">
            {technicalBenefits.map((benefit, i) => (
              <li key={i} className="flex items-start gap-2">
                <Cpu className="mt-0.5 h-4 w-4 shrink-0 text-blue-500" />
                <span>{benefit}</span>
              </li>
            ))}
          </ul>
        </CollapsibleSection>
      )}
 
      {/* Key Components */}
      {components.length > 0 && (
        <div className="rounded-lg border border-slate-200 bg-slate-50/60 p-3">
          <div className="mb-2 flex items-center gap-1.5">
            <Box className="h-3.5 w-3.5 text-blue-500" />
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
              Key Components
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            <ComponentBadges items={components} />
          </div>
        </div>
      )}
 
      {/* Design Decisions */}
      {decisions.length > 0 && (
        <CollapsibleSection title="Design Decisions" defaultOpen={false}>
          <ul className="space-y-2 text-sm leading-relaxed text-slate-700">
            {decisions.map((dec, i) => (
              <li key={i} className="flex items-start gap-2">
                <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-yellow-500" />
                <span>{dec}</span>
              </li>
            ))}
          </ul>
        </CollapsibleSection>
      )}
 
      {/* Architecture Principles */}
      {principles.length > 0 && (
        <CollapsibleSection title="Architecture Principles" defaultOpen={false}>
          <ul className="space-y-2 text-sm leading-relaxed text-slate-700">
            {principles.map((prin, i) => (
              <li key={i} className="flex items-start gap-2">
                <Shield className="mt-0.5 h-4 w-4 shrink-0 text-indigo-500" />
                <span>{prin}</span>
              </li>
            ))}
          </ul>
        </CollapsibleSection>
      )}
 
      {/* Risks */}
      {risks.length > 0 && (
        <CollapsibleSection title="Risks & Mitigation" defaultOpen={false}>
          <ul className="space-y-2 text-sm leading-relaxed text-slate-700">
            {risks.map((risk, i) => (
              <li key={i} className="flex items-start gap-2">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-500" />
                <span>{risk}</span>
              </li>
            ))}
          </ul>
        </CollapsibleSection>
      )}
 
      {/* Recommendations */}
      {recommendations.length > 0 && (
        <CollapsibleSection title="Recommendations" defaultOpen={false}>
          <ul className="space-y-2 text-sm leading-relaxed text-slate-700">
            {recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-2">
                <ArrowRight className="mt-0.5 h-4 w-4 shrink-0 text-green-500" />
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </CollapsibleSection>
      )}
 
      {/* Assumptions */}
      {assumptions.length > 0 && (
        <CollapsibleSection title="Assumptions" defaultOpen={false}>
          <ul className="space-y-1.5 text-sm leading-relaxed text-slate-700">
            {assumptions.map((asmp, i) => (
              <li key={i} className="flex items-start gap-2">
                <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-400" />
                <span className="text-slate-600">{asmp}</span>
              </li>
            ))}
          </ul>
        </CollapsibleSection>
      )}
 
      {/* Architect's Explanation */}
      {explanation.length > 0 && <ExplanationList items={explanation} />}
    </div>
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
 
  // ═══ VALIDATION AGENT RENDERERS ═══════════════════════════════════════
 
  // Architecture Review Cards (Object with 6 executive assessment cards)
  if (sectionType === "review_cards") {
    const reviewObj = (sectionAny.review_data as Record<string, string>) ?? {};
    const assessmentKeys = [
      { key: "executive_assessment", label: "Executive Assessment", icon: "🎯", color: "indigo" },
      { key: "business_alignment", label: "Business Alignment", icon: "🎯", color: "blue" },
      { key: "technical_readiness", label: "Technical Readiness", icon: "⚙️", color: "cyan" },
      { key: "production_readiness", label: "Production Readiness", icon: "🚀", color: "emerald" },
      { key: "governance_readiness", label: "Governance Readiness", icon: "📋", color: "violet" },
      { key: "overall_verdict", label: "Overall Verdict", icon: "✅", color: "emerald" }
    ];
 
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {assessmentKeys.map(({ key, label, icon, color }) => {
          const value = reviewObj[key] || "Assessment not available";
          const colorClasses = {
            indigo: "bg-gradient-to-br from-indigo-50 to-indigo-100/50 border-indigo-200",
            blue: "bg-gradient-to-br from-blue-50 to-blue-100/50 border-blue-200",
            cyan: "bg-gradient-to-br from-cyan-50 to-cyan-100/50 border-cyan-200",
            emerald: "bg-gradient-to-br from-emerald-50 to-emerald-100/50 border-emerald-200",
            violet: "bg-gradient-to-br from-violet-50 to-violet-100/50 border-violet-200"
          }[color] || "bg-gradient-to-br from-slate-50 to-slate-100/50 border-slate-200";
 
          return (
            <div key={key} className={`rounded-xl border-2 ${colorClasses} p-5 shadow-sm hover:shadow-md transition-all duration-300`}>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-2xl">{icon}</span>
                <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wide">{label}</h4>
              </div>
              <p className="text-sm leading-relaxed text-slate-700">{value}</p>
            </div>
          );
        })}
      </div>
    );
  }
 
  // Best Practice Validation Cards
  if (sectionType === "practice_cards") {
    const items = (sectionAny.items as any[]) ?? [];
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((item, idx) => {
          const statusColors = {
            "✔ Pass": { bg: "from-emerald-50 to-emerald-100/50", border: "emerald-300", badge: "bg-emerald-600 text-white", icon: "✓" },
            "⚠ Partial": { bg: "from-yellow-50 to-yellow-100/50", border: "yellow-300", badge: "bg-yellow-600 text-white", icon: "⚠" },
            "✗ Fail": { bg: "from-red-50 to-red-100/50", border: "red-300", badge: "bg-red-600 text-white", icon: "✗" }
          };
          const statusConfig = statusColors[item.status as keyof typeof statusColors] || statusColors["⚠ Partial"];
          const borderColorMap = {
            "emerald-300": "#a7f3d0",
            "yellow-300": "#fcd34d",
            "red-300": "#fca5a5"
          };
 
          return (
            <div key={idx} className={`rounded-xl border-2 bg-gradient-to-br ${statusConfig.bg} p-5 shadow-lg hover:shadow-xl transition-all duration-300`} style={{ borderColor: borderColorMap[statusConfig.border as keyof typeof borderColorMap] }}>
              <div className="flex items-start justify-between mb-4">
                <h4 className="text-base font-bold text-slate-900 flex-1 pr-2">{item.practice}</h4>
                <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold ${statusConfig.badge} shadow-sm`}>
                  {statusConfig.icon} {item.status}
                </span>
              </div>
 
              <div className="space-y-3">
                <div className="bg-white/60 rounded-lg p-3 border border-slate-200/50">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Assessment</p>
                  <p className="text-sm text-slate-800 leading-relaxed">{item.assessment}</p>
                </div>
 
                <div className="bg-white/60 rounded-lg p-3 border border-slate-200/50">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Why It Matters</p>
                  <p className="text-sm text-slate-800 leading-relaxed">{item.why_it_matters}</p>
                </div>
 
                {item.recommendation && (
                  <div className="bg-blue-50/80 rounded-lg p-3 border border-blue-200/50">
                    <p className="text-xs font-semibold text-blue-700 uppercase tracking-wider mb-1">💡 Recommendation</p>
                    <p className="text-sm text-blue-900 leading-relaxed">{item.recommendation}</p>
                  </div>
                )}
 
                <div className="bg-emerald-50/80 rounded-lg p-3 border border-emerald-200/50">
                  <p className="text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">Expected Benefit</p>
                  <p className="text-sm text-emerald-900 leading-relaxed">{item.expected_benefit}</p>
                </div>
 
                {item.risk_level && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-600">Risk Level:</span>
                    <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                      item.risk_level === "High" ? "bg-red-100 text-red-700" :
                      item.risk_level === "Medium" ? "bg-yellow-100 text-yellow-700" :
                      "bg-green-100 text-green-700"
                    }`}>
                      {item.risk_level}
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  }
 
  // Compliance Validation Cards
  if (sectionType === "compliance_cards") {
    const items = (sectionAny.items as any[]) ?? [];
    return (
      <div className="grid gap-4 sm:grid-cols-2">
        {items.map((item, idx) => {
          const statusColors = {
            "Compliant": { bg: "from-emerald-50 to-green-100/50", border: "emerald-400", badge: "bg-emerald-600 text-white", icon: "✓" },
            "Partially Compliant": { bg: "from-yellow-50 to-amber-100/50", border: "yellow-400", badge: "bg-yellow-600 text-white", icon: "⚠" },
            "Non-Compliant": { bg: "from-red-50 to-rose-100/50", border: "red-400", badge: "bg-red-600 text-white", icon: "✗" }
          };
          const statusConfig = statusColors[item.status as keyof typeof statusColors] || statusColors["Partially Compliant"];
          const borderColorMap = {
            "emerald-400": "#10b981",
            "yellow-400": "#facc15",
            "red-400": "#f87171"
          };
 
          return (
            <div key={idx} className={`rounded-xl border-2 bg-gradient-to-br ${statusConfig.bg} p-5 shadow-lg hover:shadow-xl transition-all duration-300`} style={{ borderColor: borderColorMap[statusConfig.border as keyof typeof borderColorMap] }}>
              <div className="flex items-start justify-between mb-4">
                <h4 className="text-base font-bold text-slate-900 flex-1 pr-2">{item.framework}</h4>
                <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold ${statusConfig.badge} shadow-sm`}>
                  {statusConfig.icon} {item.status}
                </span>
              </div>
 
              <div className="space-y-3">
                <div className="bg-white/60 rounded-lg p-3 border border-slate-200/50">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Purpose</p>
                  <p className="text-sm text-slate-800 leading-relaxed">{item.purpose}</p>
                </div>
 
                <div className="bg-white/60 rounded-lg p-3 border border-slate-200/50">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Current Assessment</p>
                  <p className="text-sm text-slate-800 leading-relaxed">{item.current_assessment}</p>
                </div>
 
                <div className="bg-blue-50/80 rounded-lg p-3 border border-blue-200/50">
                  <p className="text-xs font-semibold text-blue-700 uppercase tracking-wider mb-1">Evidence</p>
                  <p className="text-sm text-blue-900 leading-relaxed">{item.evidence}</p>
                </div>
 
                {item.recommendation && (
                  <div className="bg-amber-50/80 rounded-lg p-3 border border-amber-200/50">
                    <p className="text-xs font-semibold text-amber-700 uppercase tracking-wider mb-1">💡 Recommendation</p>
                    <p className="text-sm text-amber-900 leading-relaxed">{item.recommendation}</p>
                  </div>
                )}
 
                <div className="bg-violet-50/80 rounded-lg p-3 border border-violet-200/50">
                  <p className="text-xs font-semibold text-violet-700 uppercase tracking-wider mb-1">Business Impact</p>
                  <p className="text-sm text-violet-900 leading-relaxed">{item.business_impact}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  }

   
  // Detail Cards (Security, Performance, Scalability, Reliability, Observability)
  if (sectionType === "detail_cards") {
    const items = (sectionAny.items as any[]) ?? [];
    return (
      <div className="grid gap-4 sm:grid-cols-2">
        {items.map((item, idx) => {
          const hasRecommendation = item.recommendation && item.recommendation !== "null";
          const cardColor = hasRecommendation
            ? "bg-gradient-to-br from-amber-50 to-orange-100/50 border-amber-300"
            : "bg-gradient-to-br from-blue-50 to-cyan-100/50 border-blue-200";
 
          return (
            <div key={idx} className={`rounded-xl border-2 ${cardColor} p-5 shadow-lg hover:shadow-xl transition-all duration-300`}>
              <h4 className="text-base font-bold text-slate-900 mb-4">{item.title}</h4>
 
              <div className="space-y-3">
                <div className="bg-white/70 rounded-lg p-3 border border-slate-200/50">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Assessment</p>
                  <p className="text-sm text-slate-800 leading-relaxed">{item.assessment}</p>
                </div>
 
                <div className="bg-red-50/70 rounded-lg p-3 border border-red-200/50">
                  <p className="text-xs font-semibold text-red-700 uppercase tracking-wider mb-1">⚠️ Why It Matters</p>
                  <p className="text-sm text-red-900 leading-relaxed">{item.why_it_matters}</p>
                </div>
 
                {hasRecommendation && (
                  <div className="bg-blue-50/80 rounded-lg p-3 border border-blue-200/50">
                    <p className="text-xs font-semibold text-blue-700 uppercase tracking-wider mb-1">💡 Recommendation</p>
                    <p className="text-sm text-blue-900 leading-relaxed">{item.recommendation}</p>
                  </div>
                )}
 
                <div className="bg-emerald-50/80 rounded-lg p-3 border border-emerald-200/50">
                  <p className="text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">✨ Expected Outcome</p>
                  <p className="text-sm text-emerald-900 leading-relaxed">{item.expected_outcome}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  }
 
  // Cost Validation Card
  if (sectionType === "cost_card") {
    const estimatedCost = sectionAny.estimated_cost as string || "Cost estimate not available";
    const optimizationOpps = (sectionAny.optimization_opportunities as string[]) || [];
    const resourceUtil = sectionAny.resource_utilization as string || "Resource utilization data not available";
 
    return (
      <div className="space-y-4">
        {/* Estimated Cost */}
        <div className="rounded-xl border-2 border-emerald-300 bg-gradient-to-br from-emerald-50 to-green-100/50 p-6 shadow-lg">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">💰</span>
            <h4 className="text-lg font-bold text-emerald-900">Estimated Monthly Cost</h4>
          </div>
          <p className="text-2xl font-bold text-emerald-700 mb-2">{estimatedCost}</p>
          <p className="text-sm text-emerald-800">Based on current architecture design and expected workload patterns</p>
        </div>
 
        {/* Resource Utilization */}
        <div className="rounded-xl border-2 border-blue-300 bg-gradient-to-br from-blue-50 to-cyan-100/50 p-6 shadow-lg">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">📊</span>
            <h4 className="text-lg font-bold text-blue-900">Resource Utilization</h4>
          </div>
          <p className="text-sm text-blue-800 leading-relaxed">{resourceUtil}</p>
        </div>
 
        {/* Optimization Opportunities */}
        {optimizationOpps.length > 0 && (
          <div className="rounded-xl border-2 border-amber-300 bg-gradient-to-br from-amber-50 to-yellow-100/50 p-6 shadow-lg">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">⚡</span>
              <h4 className="text-lg font-bold text-amber-900">Cost Optimization Opportunities</h4>
            </div>
            <ul className="space-y-2">
              {optimizationOpps.map((opp, idx) => (
                <li key={idx} className="flex items-start gap-3 bg-white/60 rounded-lg p-3 border border-amber-200/50">
                  <span className="text-amber-600 font-bold text-lg shrink-0">•</span>
                  <p className="text-sm text-amber-900 leading-relaxed">{opp}</p>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }
 
  // Risk Register (Comprehensive Risk Management)
  if (sectionType === "risk_register") {
    const highRisks = (sectionAny.high_risks as any[]) || [];
    const mediumRisks = (sectionAny.medium_risks as any[]) || [];
    const lowRisks = (sectionAny.low_risks as any[]) || [];
    const mitigationSuggestions = (sectionAny.mitigation_suggestions as string[]) || [];
 
    const renderRiskCard = (risk: any, severity: "Critical" | "High" | "Medium" | "Low") => {
      const severityConfig = {
        Critical: { bg: "from-red-50 to-rose-100/50", border: "red-500", badge: "bg-red-600 text-white", icon: "🔴" },
        High: { bg: "from-orange-50 to-amber-100/50", border: "orange-500", badge: "bg-orange-600 text-white", icon: "🟠" },
        Medium: { bg: "from-yellow-50 to-amber-100/50", border: "yellow-500", badge: "bg-yellow-600 text-white", icon: "🟡" },
        Low: { bg: "from-blue-50 to-cyan-100/50", border: "blue-500", badge: "bg-blue-600 text-white", icon: "🟢" }
      }[severity];
 
      return (
        <div className={`rounded-xl border-2 border-${severityConfig.border} bg-gradient-to-br ${severityConfig.bg} p-5 shadow-lg hover:shadow-xl transition-all duration-300`}>
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-2 flex-1">
              <span className="text-2xl">{severityConfig.icon}</span>
              <h5 className="text-base font-bold text-slate-900">{risk.risk}</h5>
            </div>
            <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold ${severityConfig.badge} shadow-sm`}>
              {risk.priority}
            </span>
          </div>
 
          <div className="space-y-3">
            <div className="bg-white/60 rounded-lg p-3 border border-slate-200/50">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Business Impact</p>
              <p className="text-sm text-slate-800 leading-relaxed">{risk.business_impact}</p>
            </div>
 
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white/60 rounded-lg p-3 border border-slate-200/50">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Likelihood</p>
                <p className="text-sm font-bold text-slate-900">{risk.likelihood}</p>
              </div>
              <div className="bg-white/60 rounded-lg p-3 border border-slate-200/50">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Severity</p>
                <p className="text-sm font-bold text-slate-900">{risk.severity}</p>
              </div>
            </div>
 
            <div className="bg-emerald-50/80 rounded-lg p-3 border border-emerald-200/50">
              <p className="text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">✅ Mitigation</p>
              <p className="text-sm text-emerald-900 leading-relaxed">{risk.mitigation}</p>
            </div>
 
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-blue-50/80 rounded-lg p-3 border border-blue-200/50">
                <p className="text-xs font-semibold text-blue-700 uppercase tracking-wider mb-1">Owner</p>
                <p className="text-sm font-medium text-blue-900">{risk.owner}</p>
              </div>
              <div className="bg-violet-50/80 rounded-lg p-3 border border-violet-200/50">
                <p className="text-xs font-semibold text-violet-700 uppercase tracking-wider mb-1">Timeline</p>
                <p className="text-sm font-medium text-violet-900">{risk.expected_resolution}</p>
              </div>
            </div>
          </div>
        </div>
      );
    };
 
    return (
      <div className="space-y-6">
        {/* High/Critical Risks */}
        {highRisks.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-4 pb-2 border-b-2 border-red-300">
              <span className="text-2xl">🔴</span>
              <h4 className="text-lg font-bold text-red-900">Critical Risks ({highRisks.length})</h4>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              {highRisks.map((risk, idx) => (
                <div key={idx}>{renderRiskCard(risk, "Critical")}</div>
              ))}
            </div>
          </div>
        )}
 
        {/* Medium Risks */}
        {mediumRisks.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-4 pb-2 border-b-2 border-yellow-300">
              <span className="text-2xl">🟡</span>
              <h4 className="text-lg font-bold text-yellow-900">Moderate Risks ({mediumRisks.length})</h4>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              {mediumRisks.map((risk, idx) => (
                <div key={idx}>{renderRiskCard(risk, "High")}</div>
              ))}
            </div>
          </div>
        )}
 
        {/* Low Risks */}
        {lowRisks.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-4 pb-2 border-b-2 border-blue-300">
              <span className="text-2xl">🟢</span>
              <h4 className="text-lg font-bold text-blue-900">Low Risks ({lowRisks.length})</h4>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              {lowRisks.map((risk, idx) => (
                <div key={idx}>{renderRiskCard(risk, "Low")}</div>
              ))}
            </div>
          </div>
        )}
 
        {/* Mitigation Suggestions */}
        {mitigationSuggestions.length > 0 && (
          <div className="rounded-xl border-2 border-indigo-300 bg-gradient-to-br from-indigo-50 to-blue-100/50 p-6 shadow-lg">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">💡</span>
              <h4 className="text-lg font-bold text-indigo-900">Strategic Mitigation Recommendations</h4>
            </div>
            <ul className="space-y-2">
              {mitigationSuggestions.map((suggestion, idx) => (
                <li key={idx} className="flex items-start gap-3 bg-white/60 rounded-lg p-3 border border-indigo-200/50">
                  <span className="text-indigo-600 font-bold text-lg shrink-0">•</span>
                  <p className="text-sm text-indigo-900 leading-relaxed">{suggestion}</p>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }
 
  // ═══ END VALIDATION AGENT RENDERERS ═══════════════════════════════════
 
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
            {items.map((item, idx) => {
              const statusColor = item.status === "PASS" ? "border-emerald-200 bg-emerald-50" :
                                 item.status === "FAIL" ? "border-red-200 bg-red-50" :
                                 "border-yellow-200 bg-yellow-50";
              const statusBadge = item.status === "PASS" ? "bg-emerald-100 text-emerald-800" :
                                 item.status === "FAIL" ? "bg-red-100 text-red-800" :
                                 "bg-yellow-100 text-yellow-800";
              const statusIcon = item.status === "PASS" ? "✓" :
                                item.status === "FAIL" ? "✗" :
                                "⚠";
 
              return (
                <div key={idx} className={`rounded-lg border p-4 shadow-sm hover:shadow-md transition-shadow ${statusColor}`}>
                  <div className="flex items-start justify-between mb-3">
                    <h4 className="text-sm font-semibold text-slate-900 flex-1">{item.title}</h4>
                    {item.status && (
                      <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ml-2 ${statusBadge}`}>
                        {statusIcon} {item.status}
                      </span>
                    )}
                  </div>
                 
                  {item.description && (
                    <p className="text-sm text-slate-700 mb-3">{item.description}</p>
                  )}
                 
                  {item.business_impact && (
                    <div className="mb-2 rounded bg-white/50 p-2">
                      <p className="text-xs font-semibold text-slate-700 mb-1">💼 Business Impact</p>
                      <p className="text-xs text-slate-600">{item.business_impact}</p>
                    </div>
                  )}
                 
                  {item.recommendation && (
                    <div className="mb-2 rounded bg-white/50 p-2">
                      <p className="text-xs font-semibold text-slate-700 mb-1">💡 Recommendation</p>
                      <p className="text-xs text-slate-600">{item.recommendation}</p>
                    </div>
                  )}
 
                  {item.metadata && Array.isArray(item.metadata) && (
                    <div className="space-y-1.5 mt-3 border-t pt-2">
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
              );
            })}
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
 
  // ═══════════════════════════════════════════════════════════════════════════════
  // OUTPUT AGENT RENDERERS — Enterprise Solution Package
  // ═══════════════════════════════════════════════════════════════════════════════
 
  // Package Manifest — Comprehensive Package Overview with Readiness Indicators
  if (sectionType === "package_manifest") {
    const metadata = sectionAny.metadata as Record<string, unknown> | undefined;
    const readiness = sectionAny.readiness as Record<string, unknown> | undefined;
    const docQualityScore = Number(sectionAny.document_quality_score || 0);
    const archScore = Number(sectionAny.architecture_score || 0);
    const recBadge = sectionAny.recommendation_badge as { label?: string; color?: string } | undefined;
 
    if (!metadata) {
      return <p className="text-sm text-slate-400 italic">Package manifest not available.</p>;
    }
 
    const packageTitle = String(metadata.package_title || "Enterprise Solution Package");
    const packageSubtitle = String(metadata.package_subtitle || "");
    const finalRec = recBadge?.label || String(metadata.final_recommendation || "Pending Review");
    const recColorClass = recBadge?.color === "success"
      ? "bg-emerald-100 text-emerald-800 border-emerald-300"
      : recBadge?.color === "info"
      ? "bg-blue-100 text-blue-800 border-blue-300"
      : recBadge?.color === "warning"
      ? "bg-amber-100 text-amber-800 border-amber-300"
      : "bg-red-100 text-red-800 border-red-300";
 
    const compositeScore = readiness ? Number((readiness as any).composite_score || 0) : 0;
    const readinessLabel = readiness ? String((readiness as any).label || "Pending Assessment") : "Pending Assessment";
    const dimensions = readiness ? (readiness as any).dimensions as Record<string, any> || {} : {};
 
    return (
      <div className="space-y-6">
        {/* Hero Header */}
        <div className="rounded-xl border-2 border-indigo-300 bg-gradient-to-br from-indigo-50 via-blue-50 to-white p-6 shadow-xl">
          <div className="flex items-start justify-between gap-4 mb-6">
            <div>
              <h3 className="text-2xl font-bold text-slate-900">{packageTitle}</h3>
              {packageSubtitle && <p className="text-sm text-slate-600 mt-1">{packageSubtitle}</p>}
            </div>
            <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-bold border-2 ${recColorClass}`}>
              {finalRec}
            </span>
          </div>
 
          {/* Readiness Score */}
          <div className="rounded-lg bg-white/80 border border-indigo-200 p-4 mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-indigo-700 uppercase tracking-wider">Package Readiness</span>
              <span className="text-2xl font-bold text-indigo-900">{compositeScore}%</span>
            </div>
            <div className="h-3 w-full rounded-full bg-indigo-100 overflow-hidden mb-2">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-blue-500 transition-all duration-500"
                style={{ width: `${Math.min(compositeScore, 100)}%` }}
              />
            </div>
            <p className="text-xs font-semibold text-indigo-700">{readinessLabel}</p>
          </div>
 
          {/* Dimension Breakdown */}
          {Object.keys(dimensions).length > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {Object.entries(dimensions).map(([key, dim]: [string, any]) => (
                <div key={key} className="rounded-lg bg-white/60 border border-slate-200 p-3 text-center">
                  <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                    {key.replace(/_/g, ' ')}
                  </p>
                  <p className="text-lg font-bold text-slate-800">{dim.score || 0}%</p>
                  {dim.count && <p className="text-[10px] text-slate-500">{dim.count}</p>}
                </div>
              ))}
            </div>
          )}
 
          {/* Score Cards */}
          <div className="grid grid-cols-2 gap-4 mt-4">
            <div className="rounded-lg bg-white/80 border border-slate-200 p-4">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Architecture Score</p>
              <p className="text-2xl font-bold text-indigo-600">{archScore}/100</p>
            </div>
            <div className="rounded-lg bg-white/80 border border-slate-200 p-4">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Document Quality</p>
              <p className="text-2xl font-bold text-emerald-600">{docQualityScore}%</p>
            </div>
          </div>
        </div>
      </div>
    );
  }
 
  // Executive Intelligence — Derived Insights Summary
  if (sectionType === "executive_intelligence") {
    const highlights = sectionAny.highlights as string[] | undefined;
    const keyDecisionsCount = Number(sectionAny.key_decisions_count || 0);
    const riskProfile = sectionAny.risk_profile as Record<string, any> | undefined;
    const costSnapshot = sectionAny.cost_snapshot as string | undefined;
    const topDecisions = sectionAny.top_decisions as any[] | undefined;
 
    return (
      <div className="space-y-4">
        {/* Highlights */}
        {highlights && highlights.length > 0 && (
          <div className="rounded-xl border-2 border-amber-200 bg-gradient-to-br from-amber-50 to-yellow-50 p-5 shadow-md">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="h-5 w-5 text-amber-600" />
              <h4 className="text-sm font-bold text-amber-900 uppercase tracking-wide">Executive Highlights</h4>
            </div>
            <ul className="space-y-2">
              {highlights.map((h, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-amber-900">
                  <span className="text-amber-500 font-bold mt-0.5">→</span>
                  <span>{h}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
 
        {/* Quick Stats Row */}
        <div className="grid grid-cols-3 gap-4">
          {/* Key Decisions */}
          <div className="rounded-lg border border-purple-200 bg-purple-50 p-4 text-center">
            <p className="text-[10px] font-semibold text-purple-600 uppercase tracking-wider mb-1">Key Decisions</p>
            <p className="text-2xl font-bold text-purple-900">{keyDecisionsCount}</p>
          </div>
 
          {/* Risk Profile */}
          {riskProfile && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-center">
              <p className="text-[10px] font-semibold text-red-600 uppercase tracking-wider mb-1">Risk Profile</p>
              <p className="text-sm font-bold text-red-900">{riskProfile.profile || "Unknown"}</p>
              <p className="text-[10px] text-red-700 mt-1">
                {riskProfile.high || 0} High · {riskProfile.medium || 0} Med · {riskProfile.low || 0} Low
              </p>
            </div>
          )}
 
          {/* Cost Snapshot */}
          {costSnapshot && (
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-center">
              <p className="text-[10px] font-semibold text-emerald-600 uppercase tracking-wider mb-1">Est. Cost</p>
              <p className="text-lg font-bold text-emerald-900">{costSnapshot}</p>
            </div>
          )}
        </div>
 
        {/* Top Decisions Preview */}
        {topDecisions && topDecisions.length > 0 && (
          <div className="rounded-lg border border-slate-200 bg-white p-4">
            <h5 className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-3">Top Architectural Decisions</h5>
            <div className="space-y-2">
              {topDecisions.slice(0, 3).map((dec, i) => (
                <div key={i} className="flex items-center gap-3 p-2 rounded bg-slate-50">
                  <span className="text-lg">{dec.icon || "→"}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-900 truncate">{dec.component}</p>
                    <p className="text-xs text-slate-500 truncate">{dec.rationale}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    dec.badge_color === "success" ? "bg-emerald-100 text-emerald-800" :
                    dec.badge_color === "info" ? "bg-blue-100 text-blue-800" :
                    dec.badge_color === "warning" ? "bg-amber-100 text-amber-800" :
                    "bg-slate-100 text-slate-800"
                  }`}>
                    {dec.decision}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }
 
  // Bullet HLD — High-Level Design (Executive Audience)
  if (sectionType === "bullet_hld") {
    const hldItems = sectionAny.items as any[] | undefined;
    const audience = sectionAny.audience as string | undefined;
    const description = sectionAny.description as string | undefined;
 
    if (!hldItems || hldItems.length === 0) {
      return <p className="text-sm text-slate-400 italic">High-level design not available.</p>;
    }
 
    return (
      <div className="space-y-4">
        {/* Audience Badge & Description */}
        <div className="flex items-start justify-between gap-4">
          {description && <p className="text-sm text-slate-600 flex-1">{description}</p>}
          {audience && (
            <span className="inline-flex items-center px-3 py-1 rounded-full bg-blue-100 text-xs font-semibold text-blue-800">
              👔 {audience}
            </span>
          )}
        </div>
 
        {/* HLD Items */}
        <div className="rounded-xl border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-white p-5">
          <ul className="space-y-3">
            {hldItems.map((item, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-500 text-white text-xs font-bold">
                  {idx + 1}
                </div>
                <p className="text-sm text-slate-700 leading-relaxed pt-0.5">
                  {typeof item === "string" ? item : JSON.stringify(item)}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  }
 
  // Bullet LLD — Low-Level Design (Implementation Team)
  if (sectionType === "bullet_lld") {
    const lldItems = sectionAny.items as any[] | undefined;
    const audience = sectionAny.audience as string | undefined;
    const description = sectionAny.description as string | undefined;
 
    if (!lldItems || lldItems.length === 0) {
      return <p className="text-sm text-slate-400 italic">Low-level design not available.</p>;
    }
 
    return (
      <div className="space-y-4">
        {/* Audience Badge & Description */}
        <div className="flex items-start justify-between gap-4">
          {description && <p className="text-sm text-slate-600 flex-1">{description}</p>}
          {audience && (
            <span className="inline-flex items-center px-3 py-1 rounded-full bg-indigo-100 text-xs font-semibold text-indigo-800">
              💻 {audience}
            </span>
          )}
        </div>
 
        {/* LLD Items with Technical Styling */}
        <div className="rounded-xl border-2 border-indigo-200 bg-gradient-to-br from-indigo-50 to-white p-5">
          <ul className="space-y-2">
            {lldItems.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm">
                <Cpu className="h-4 w-4 text-indigo-500 shrink-0 mt-0.5" />
                <code className="text-slate-700 bg-white/50 px-1 rounded font-mono text-xs leading-relaxed">
                  {typeof item === "string" ? item : JSON.stringify(item)}
                </code>
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  }
 
  // Bullet Security — Security Architecture
  if (sectionType === "bullet_security") {
    const securityItems = sectionAny.items as any[] | undefined;
    const description = sectionAny.description as string | undefined;
 
    if (!securityItems || securityItems.length === 0) {
      return <p className="text-sm text-slate-400 italic">Security architecture not available.</p>;
    }
 
    return (
      <div className="space-y-4">
        {description && <p className="text-sm text-slate-600">{description}</p>}
 
        <div className="rounded-xl border-2 border-red-200 bg-gradient-to-br from-red-50 to-white p-5">
          <ul className="space-y-3">
            {securityItems.map((item, idx) => (
              <li key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-white/60 border border-red-100">
                <Shield className="h-5 w-5 text-red-500 shrink-0" />
                <p className="text-sm text-slate-700 leading-relaxed">
                  {typeof item === "string" ? item : JSON.stringify(item)}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  }
 
  // Bullet Deployment — Deployment Architecture
  if (sectionType === "bullet_deployment") {
    const deploymentItems = sectionAny.items as any[] | undefined;
    const description = sectionAny.description as string | undefined;
 
    if (!deploymentItems || deploymentItems.length === 0) {
      return <p className="text-sm text-slate-400 italic">Deployment architecture not available.</p>;
    }
 
    return (
      <div className="space-y-4">
        {description && <p className="text-sm text-slate-600">{description}</p>}
 
        <div className="rounded-xl border-2 border-orange-200 bg-gradient-to-br from-orange-50 to-white p-5">
          <ul className="space-y-3">
            {deploymentItems.map((item, idx) => (
              <li key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-white/60 border border-orange-100">
                <Server className="h-5 w-5 text-orange-500 shrink-0" />
                <p className="text-sm text-slate-700 leading-relaxed">
                  {typeof item === "string" ? item : JSON.stringify(item)}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  }
 
  // Pipeline Traceability — Agent Provenance
  if (sectionType === "pipeline_traceability") {
    const agents = sectionAny.agents as any[] | undefined;
 
    if (!agents || agents.length === 0) {
      return <p className="text-sm text-slate-400 italic">Pipeline traceability not available.</p>;
    }
 
    return (
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
        <div className="flex items-center gap-2 mb-4">
          <Network className="h-5 w-5 text-slate-500" />
          <h4 className="text-sm font-bold text-slate-700 uppercase tracking-wide">Agent Pipeline Provenance</h4>
        </div>
 
        <div className="grid gap-2">
          {agents.map((agent, idx) => (
            <div key={idx} className="flex items-center gap-4 p-3 rounded-lg bg-white border border-slate-200">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-sm font-bold text-slate-600">
                {idx + 1}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-slate-900">{agent.name}</p>
                <p className="text-xs text-slate-500 truncate">{agent.role}</p>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-semibold ${
                agent.status?.includes("✓")
                  ? "bg-emerald-100 text-emerald-700"
                  : "bg-red-100 text-red-700"
              }`}>
                {agent.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }
 
  // Solution Metadata — Enterprise Package Header
  if (sectionType === "solution_metadata") {
    const metadata = sectionAny.metadata as Record<string, unknown> | undefined;
    if (!metadata) {
      return <p className="text-sm text-slate-400 italic">Solution metadata not available.</p>;
    }
 
    const packageTitle = String(metadata.package_title || "Enterprise Solution Package");
    const packageSubtitle = String(metadata.package_subtitle || "");
    const industry = String(metadata.industry || "Technology");
    const archStyle = String(metadata.architecture_style || "Modern");
    const cloudPlatform = String(metadata.cloud_platform || "Cloud");
    const complexity = String(metadata.solution_complexity || "Enterprise");
    const timeline = String(metadata.estimated_timeline || "TBD");
    const criticality = String(metadata.business_criticality || "High");
    const confidenceScore = Number(metadata.confidence_score || 0);
    const archScore = Number(metadata.architecture_score || 0);
    const finalRec = String(metadata.final_recommendation || "Pending Review");
    const docVersion = String(metadata.document_version || "1.0");
    const techSummary = Array.isArray(metadata.technology_summary)
      ? metadata.technology_summary as string[]
      : [];
 
    const confidenceColor = confidenceScore >= 85 ? "text-emerald-600" : confidenceScore >= 70 ? "text-blue-600" : "text-amber-600";
    const recColor = finalRec.includes("Approved") && !finalRec.includes("Recommendations")
      ? "bg-emerald-100 text-emerald-800 border-emerald-300"
      : finalRec.includes("Approved")
      ? "bg-blue-100 text-blue-800 border-blue-300"
      : "bg-amber-100 text-amber-800 border-amber-300";
 
    return (
      <div className="space-y-4">
        {/* Hero Card */}
        <div className="rounded-xl border-2 border-indigo-200 bg-gradient-to-br from-indigo-50 via-blue-50 to-white p-6 shadow-lg">
          <div className="flex items-start justify-between gap-4 mb-4">
            <div>
              <h3 className="text-2xl font-bold text-slate-900">{packageTitle}</h3>
              {packageSubtitle && (
                <p className="text-sm text-slate-600 mt-1">{packageSubtitle}</p>
              )}
            </div>
            <div className="flex flex-col items-end gap-2">
              <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-bold border ${recColor}`}>
                {finalRec}
              </span>
              <span className="text-xs text-slate-500">v{docVersion}</span>
            </div>
          </div>
 
          {/* Badges Row */}
          <div className="flex flex-wrap gap-2 mb-4">
            <span className="inline-flex items-center px-3 py-1 rounded-full bg-slate-100 text-xs font-medium text-slate-700">
              🏢 {industry}
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full bg-blue-100 text-xs font-medium text-blue-700">
              🏗️ {archStyle}
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full bg-cyan-100 text-xs font-medium text-cyan-700">
              ☁️ {cloudPlatform}
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full bg-purple-100 text-xs font-medium text-purple-700">
              📊 {complexity}
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full bg-amber-100 text-xs font-medium text-amber-700">
              ⚡ {criticality} Criticality
            </span>
          </div>
 
          {/* Scores */}
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="rounded-lg bg-white/80 p-4 border border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Confidence</p>
              <p className={`text-2xl font-bold ${confidenceColor}`}>{confidenceScore}%</p>
            </div>
            <div className="rounded-lg bg-white/80 p-4 border border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Architecture Score</p>
              <p className="text-2xl font-bold text-indigo-600">{archScore}/100</p>
            </div>
            <div className="rounded-lg bg-white/80 p-4 border border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Timeline</p>
              <p className="text-lg font-bold text-slate-800">{timeline}</p>
            </div>
          </div>
 
          {/* Technology Stack */}
          {techSummary.length > 0 && (
            <div className="pt-4 border-t border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Technology Stack</p>
              <div className="flex flex-wrap gap-2">
                {techSummary.map((tech, i) => (
                  <span key={i} className="inline-flex items-center px-3 py-1 rounded-full bg-slate-800 text-xs font-medium text-white">
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }
 
  // Executive Overview — Structured CTO Summary
  if (sectionType === "executive_overview") {
    const overviewSections = sectionAny.sections as any[] | undefined;
    const confidenceStatement = sectionAny.confidence_statement as string | undefined;
    const content = section.content;
 
    return (
      <div className="space-y-4">
        {/* Main Summary */}
        {content && (
          <div className="rounded-xl border-2 border-slate-200 bg-gradient-to-br from-slate-50 to-white p-6 shadow-md">
            <div className="flex items-start gap-3 mb-3">
              <span className="text-2xl">📋</span>
              <h4 className="text-lg font-bold text-slate-900">Decision Summary</h4>
            </div>
            <p className="text-sm leading-relaxed text-slate-700">{content}</p>
          </div>
        )}
 
        {/* Detailed Sections */}
        {overviewSections && overviewSections.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2">
            {overviewSections.map((sec, idx) => (
              <div key={idx} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
                <h5 className="text-sm font-bold text-slate-900 mb-2">{sec.heading}</h5>
                <p className="text-sm text-slate-600 leading-relaxed mb-2">{sec.content}</p>
                {sec.highlights && Array.isArray(sec.highlights) && sec.highlights.length > 0 && (
                  <ul className="space-y-1">
                    {sec.highlights.map((h: string, hi: number) => (
                      <li key={hi} className="flex items-start gap-2 text-xs text-slate-600">
                        <CheckCircle2 className="h-3 w-3 text-emerald-500 shrink-0 mt-0.5" />
                        <span>{h}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}
 
        {/* Confidence Statement */}
        {confidenceStatement && (
          <div className="rounded-lg border-l-4 border-blue-500 bg-blue-50/80 p-4">
            <p className="text-xs font-semibold text-blue-700 uppercase tracking-wider mb-1">Confidence Assessment</p>
            <p className="text-sm text-blue-900">{confidenceStatement}</p>
          </div>
        )}
      </div>
    );
  }
   // Roadmap — Implementation Timeline
  if (sectionType === "roadmap") {
    const roadmapItems = sectionAny.items as any[] | undefined;
   
    if (!roadmapItems || roadmapItems.length === 0) {
      return <p className="text-sm text-slate-400 italic">Implementation roadmap not available.</p>;
    }
 
    return (
      <div className="relative space-y-4 pl-8">
        {/* Timeline line */}
        <div className="absolute left-3 top-4 bottom-4 w-0.5 bg-gradient-to-b from-indigo-400 via-blue-400 to-emerald-400" />
       
        {roadmapItems.map((item, idx) => {
          const phaseColors = [
            "border-indigo-300 bg-indigo-50",
            "border-blue-300 bg-blue-50",
            "border-cyan-300 bg-cyan-50",
            "border-emerald-300 bg-emerald-50",
          ];
          const dotColors = [
            "bg-indigo-500",
            "bg-blue-500",
            "bg-cyan-500",
            "bg-emerald-500",
          ];
          const colorClass = phaseColors[idx % phaseColors.length];
          const dotColor = dotColors[idx % dotColors.length];
 
          const deliverables = Array.isArray(item.deliverables) ? item.deliverables : [];
          const dependencies = Array.isArray(item.dependencies) ? item.dependencies : [];
 
          return (
            <div key={idx} className={`relative rounded-lg border-2 ${colorClass} p-4 shadow-sm`}>
              {/* Timeline dot */}
              <div className={`absolute -left-[29px] top-6 h-4 w-4 rounded-full ${dotColor} border-2 border-white shadow`} />
             
              <div className="flex items-start justify-between gap-3 mb-2">
                <div>
                  <span className="inline-block px-2 py-0.5 rounded text-xs font-bold bg-white/70 text-slate-700 mb-1">
                    Phase {idx + 1}
                  </span>
                  <h5 className="text-base font-bold text-slate-900">
                    {typeof item === "string" ? item : (item.phase || `Phase ${idx + 1}`)}
                  </h5>
                </div>
                {item.duration && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full bg-white/80 text-xs font-semibold text-slate-700">
                    🕐 {item.duration}
                  </span>
                )}
              </div>
 
              {deliverables.length > 0 && (
                <div className="mb-2">
                  <p className="text-xs font-semibold text-slate-600 mb-1">Deliverables:</p>
                  <ul className="space-y-1">
                    {deliverables.slice(0, 4).map((d: string, di: number) => (
                      <li key={di} className="flex items-start gap-2 text-xs text-slate-700">
                        <span className="text-emerald-500">✓</span>
                        <span>{d}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
 
              {dependencies.length > 0 && (
                <div className="pt-2 border-t border-slate-200/50">
                  <p className="text-xs font-semibold text-slate-600 mb-1">Dependencies:</p>
                  <div className="flex flex-wrap gap-1">
                    {dependencies.slice(0, 3).map((dep: string, di: number) => (
                      <span key={di} className="inline-flex items-center px-2 py-0.5 rounded bg-white/70 text-xs text-slate-600">
                        {dep}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  }
 
  // Cost Table — Investment Summary
  if (sectionType === "cost_table") {
    const costItems = sectionAny.items as any[] | undefined;
   
    if (!costItems || costItems.length === 0) {
      return <p className="text-sm text-slate-400 italic">Cost breakdown not available.</p>;
    }
 
    return (
      <div className="space-y-4">
        <div className="overflow-hidden rounded-xl border-2 border-emerald-200 shadow-lg">
          <div className="bg-gradient-to-r from-emerald-600 to-green-600 px-6 py-4">
            <h4 className="text-lg font-bold text-white flex items-center gap-2">
              💰 Cost Breakdown
            </h4>
          </div>
          <table className="w-full">
            <thead className="bg-emerald-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-bold text-emerald-800 uppercase tracking-wider">Category</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-emerald-800 uppercase tracking-wider">Item</th>
                <th className="px-4 py-3 text-right text-xs font-bold text-emerald-800 uppercase tracking-wider">Estimate</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-emerald-800 uppercase tracking-wider">Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-emerald-100">
              {costItems.map((item, idx) => (
                <tr key={idx} className="hover:bg-emerald-50/50 transition-colors">
                  <td className="px-4 py-3 text-sm font-medium text-slate-900">
                    {typeof item === "string" ? "General" : (item.category || "—")}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-700">
                    {typeof item === "string" ? item : (item.item || "—")}
                  </td>
                  <td className="px-4 py-3 text-sm font-bold text-emerald-700 text-right">
                    {typeof item === "string" ? "—" : (item.estimate || "TBD")}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">
                    {typeof item === "string" ? "" : (item.notes || "")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }
 
  // Decision Table — Build vs Buy Analysis
  if (sectionType === "decision_table") {
    const decisionItems = sectionAny.items as any[] | undefined;
   
    if (!decisionItems || decisionItems.length === 0) {
      return <p className="text-sm text-slate-400 italic">Build vs Buy analysis not available.</p>;
    }
 
    return (
      <div className="space-y-4">
        <div className="overflow-hidden rounded-xl border-2 border-purple-200 shadow-lg">
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-4">
            <h4 className="text-lg font-bold text-white flex items-center gap-2">
              ⚖️ Build vs Buy Decisions
            </h4>
          </div>
          <table className="w-full">
            <thead className="bg-purple-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-bold text-purple-800 uppercase tracking-wider">Component</th>
                <th className="px-4 py-3 text-center text-xs font-bold text-purple-800 uppercase tracking-wider">Decision</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-purple-800 uppercase tracking-wider">Rationale</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-purple-100">
              {decisionItems.map((item, idx) => {
                const decision = typeof item === "string" ? "—" : (item.decision || "—");
                const decisionColor = decision === "Build"
                  ? "bg-green-100 text-green-800"
                  : decision === "Buy"
                  ? "bg-blue-100 text-blue-800"
                  : "bg-slate-100 text-slate-800";
               
                return (
                  <tr key={idx} className="hover:bg-purple-50/50 transition-colors">
                    <td className="px-4 py-3 text-sm font-medium text-slate-900">
                      {typeof item === "string" ? item : (item.component || "—")}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${decisionColor}`}>
                        {decision}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-600">
                      {typeof item === "string" ? "" : (item.rationale || "—")}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  }
 
  // Risk Table — Enterprise Risk Register
  if (sectionType === "risk_table") {
    const riskItems = sectionAny.items as any[] | undefined;
   
    if (!riskItems || riskItems.length === 0) {
      return <p className="text-sm text-slate-400 italic">Risk register not available.</p>;
    }
 
    return (
      <div className="space-y-4">
        <div className="overflow-hidden rounded-xl border-2 border-red-200 shadow-lg">
          <div className="bg-gradient-to-r from-red-600 to-rose-600 px-6 py-4">
            <h4 className="text-lg font-bold text-white flex items-center gap-2">
              ⚠️ Risk Register
            </h4>
          </div>
          <table className="w-full">
            <thead className="bg-red-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-bold text-red-800 uppercase tracking-wider">Risk</th>
                <th className="px-4 py-3 text-center text-xs font-bold text-red-800 uppercase tracking-wider">Severity</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-red-800 uppercase tracking-wider">Mitigation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-red-100">
              {riskItems.map((item, idx) => {
                const severity = typeof item === "string" ? "Medium" : (item.severity || "Medium");
                const severityColor = severity === "High" || severity === "Critical"
                  ? "bg-red-100 text-red-800"
                  : severity === "Medium"
                  ? "bg-amber-100 text-amber-800"
                  : "bg-green-100 text-green-800";
               
                return (
                  <tr key={idx} className="hover:bg-red-50/50 transition-colors">
                    <td className="px-4 py-3 text-sm font-medium text-slate-900">
                      {typeof item === "string" ? item : (item.risk || "—")}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${severityColor}`}>
                        {severity}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-600">
                      {typeof item === "string" ? "—" : (item.mitigation || "To be determined")}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  }
 
  // Enterprise Downloads — Professional Download Cards
  if (sectionType === "enterprise_downloads") {
    const downloadsArray = sectionAny.downloads as any[] | undefined;
   
    if (!downloadsArray || downloadsArray.length === 0) {
      return <p className="text-sm text-slate-400 italic">Downloadable deliverables not available.</p>;
    }
 
    return (
      <div className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-3">
          {downloadsArray.map((dl, idx) => {
            const formatColors: Record<string, string> = {
              HTML: "from-blue-500 to-cyan-500",
              Markdown: "from-slate-600 to-slate-800",
              HCL: "from-purple-500 to-indigo-600",
            };
            const gradientClass = formatColors[dl.format] || "from-slate-500 to-slate-700";
 
            return (
              <div
                key={idx}
                className="group rounded-xl border-2 border-slate-200 bg-white overflow-hidden shadow-lg hover:shadow-xl transition-all hover:border-blue-300"
              >
                <div className={`bg-gradient-to-br ${gradientClass} px-4 py-4`}>
                  <span className="text-3xl">{dl.icon || "📄"}</span>
                </div>
                <div className="p-4">
                  <h5 className="text-sm font-bold text-slate-900 mb-1">{dl.label}</h5>
                  <p className="text-xs text-slate-500 mb-3">{dl.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="inline-flex items-center px-2 py-1 rounded bg-slate-100 text-xs font-medium text-slate-600">
                      {dl.format}
                    </span>
                    <button
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-600 text-xs font-semibold text-white hover:bg-blue-700 transition-colors"
                      data-download-key={dl.key}
                    >
                      <ArrowRight className="h-3 w-3" />
                      Download
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
       
        {/* Package Summary */}
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs text-slate-600 text-center">
            📦 <span className="font-semibold">Enterprise Solution Package</span> — All deliverables are generated dynamically based on your specific requirements and validated architecture.
          </p>
        </div>
      </div>
    );
  }
 
  // ═══════════════════════════════════════════════════════════════════════════════
  // END OUTPUT AGENT RENDERERS
  // ═══════════════════════════════════════════════════════════════════════════════
 
  // 0 — Executive Poster
  if (sectionType === "executive_poster") {
    const poster = sectionAny.poster as any;
    if (!poster) {
      console.warn("⚠️ ExecutiveArchitecturePoster: section type is 'executive_poster' but 'poster' prop is missing", sectionAny);
      return (
        <div className="rounded-lg border border-amber-200 bg-amber-50/60 p-4 text-sm text-amber-800">
          Executive Architecture Poster data was not generated. Please re-run the architecture agent.
        </div>
      );
    }
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
 
  // 1a — Alert sections (Architecture Review Board decisions)
  if (sectionType === "alert") {
    const content = sectionAny.content as string | undefined;
    const color = sectionAny.color as string | undefined;
    const icon = sectionAny.icon as string | undefined;
    const score = sectionAny.score as number | undefined;
    const rating = sectionAny.rating as string | undefined;
 
    const bgColor = color === "success" ? "border-emerald-300 bg-emerald-50" :
                   color === "info" ? "border-blue-300 bg-blue-50" :
                   color === "warning" ? "border-yellow-300 bg-yellow-50" :
                   "border-red-300 bg-red-50";
   
    const textColor = color === "success" ? "text-emerald-900" :
                     color === "info" ? "text-blue-900" :
                     color === "warning" ? "text-yellow-900" :
                     "text-red-900";
   
    const buttonColor = color === "success" ? "bg-emerald-600 hover:bg-emerald-700" :
                       color === "info" ? "bg-blue-600 hover:bg-blue-700" :
                       color === "warning" ? "bg-yellow-600 hover:bg-yellow-700" :
                       "bg-red-600 hover:bg-red-700";
 
    return (
      <div className={`rounded-lg border-2 p-6 ${bgColor}`}>
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className={`text-3xl font-bold ${textColor}`}>{icon} {content}</p>
            {rating && <p className={`text-sm font-semibold ${textColor} mt-1`}>{rating}</p>}
          </div>
          {score !== undefined && (
            <div className={`text-4xl font-bold ${textColor}`}>{score}/100</div>
          )}
        </div>
        <p className={`text-sm leading-relaxed ${textColor}`}>
          This architectural assessment has been reviewed in accordance with enterprise governance standards and the Architecture Review Board decision framework.
        </p>
      </div>
    );
  }
 
  // 1b — Score card sections (Architecture dimensions scorecard with rationales)
  if (sectionType === "score_card") {
    const scoreItems = items as any[] | undefined;
    const framework = sectionAny.framework as string | undefined;
 
    if (!scoreItems || scoreItems.length === 0) {
      return <p className="text-sm text-slate-400 italic">Score card data not available.</p>;
    }
 
    const overallScore = scoreItems[0];
    const dimensionScores = scoreItems.slice(1);
 
    return (
      <div className="space-y-4">
        {/* Overall Score Progress */}
        {overallScore && (
          <div className="rounded-xl border-2 border-indigo-400 bg-gradient-to-br from-indigo-50 via-indigo-100/50 to-white p-6 shadow-xl">
            <div className="flex items-end justify-between mb-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-indigo-600 mb-1">Overall Architecture Score</p>
                <p className="text-5xl font-bold text-indigo-900">{overallScore.value}<span className="text-2xl text-indigo-600">/100</span></p>
              </div>
              <p className="text-sm font-semibold px-4 py-2 bg-indigo-600 text-white rounded-lg shadow">{overallScore.rating}</p>
            </div>
            <div className="h-3 w-full rounded-full bg-indigo-200 overflow-hidden shadow-inner mb-3">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 via-indigo-600 to-indigo-700 shadow-sm"
                style={{ width: `${Math.min(overallScore.value, 100)}%` }}
              />
            </div>
            {overallScore.rationale && (
              <div className="bg-white/80 rounded-lg p-3 border border-indigo-200/50 mt-3">
                <p className="text-sm text-indigo-900 leading-relaxed">{overallScore.rationale}</p>
              </div>
            )}
          </div>
        )}
 
        {/* Dimension Scores Grid with Rationales */}
        <div className="grid gap-4 sm:grid-cols-2">
          {dimensionScores.map((item, idx) => {
            const scorePercent = Math.min(item.value || 0, 100);
            const scoreColors = scorePercent >= 90
              ? { border: "emerald-300", bg: "from-emerald-50 to-green-100/50", prog: "bg-emerald-500", text: "emerald" }
              : scorePercent >= 75
              ? { border: "blue-300", bg: "from-blue-50 to-cyan-100/50", prog: "bg-blue-500", text: "blue" }
              : scorePercent >= 60
              ? { border: "yellow-300", bg: "from-yellow-50 to-amber-100/50", prog: "bg-yellow-500", text: "yellow" }
              : { border: "red-300", bg: "from-red-50 to-rose-100/50", prog: "bg-red-500", text: "red" };
 
            return (
              <div key={idx} className={`rounded-xl border-2 border-${scoreColors.border} bg-gradient-to-br ${scoreColors.bg} p-5 shadow-lg hover:shadow-xl transition-all duration-300`}>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wide">{item.label}</h4>
                  <span className="text-2xl font-bold text-slate-900">{item.value}</span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-200 overflow-hidden mb-2 shadow-inner">
                  <div
                    className={`h-full ${scoreColors.prog} shadow-sm`}
                    style={{ width: `${scorePercent}%` }}
                  />
                </div>
                <p className="text-xs font-semibold text-slate-600 mb-3">{item.rating}</p>
               
                {item.rationale && (
                  <div className="bg-white/70 rounded-lg p-3 border border-slate-200/50">
                    <p className="text-xs text-slate-700 leading-relaxed">{item.rationale}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
 
        {/* Framework Reference */}
        {framework && (
          <div className="rounded-xl border-2 border-slate-300 bg-gradient-to-br from-slate-50 to-slate-100/50 p-4 shadow-md">
            <div className="flex items-center gap-2">
              <span className="text-lg">📐</span>
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Assessment Framework:</span>
              <span className="text-xs text-slate-600 font-medium">{framework}</span>
            </div>
          </div>
        )}
      </div>
    );
  }
 
  // 1c — Bullet list sections — render items as structured cards or list
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
        {/* Description */}
        {description && (
          <p className="text-sm leading-relaxed text-slate-700 font-medium">{description}</p>
        )}
       
        {/* Business Summary - Prominent Display */}
        {businessSummary && (
          <div className="rounded-lg border-l-4 border-emerald-500 bg-emerald-50/80 p-4">
            <div className="flex items-start gap-2 mb-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0 mt-0.5" />
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-800">
                Business Value
              </span>
            </div>
            <p className="text-sm leading-relaxed text-emerald-900 font-medium">
              {businessSummary}
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
  // ═══ EXECUTIVE POSTER (HERO SECTION) ═══
  "ExecutiveArchitecturePoster",
 
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
 
// ═══ OUTPUT PACKAGE HEADINGS ═══
const OUTPUT_HEADINGS = new Set([
  "Package Manifest",
  "Executive Intelligence",
  "Executive Overview",
  "Executive Architecture Poster",
  "High-Level Design (Bullet)",
  "Low-Level Design (Bullet)",
  "Security Architecture (Bullet)",
  "Deployment Architecture (Bullet)",
  "Pipeline Traceability",
  "Roadmap",
  "Risk Analysis",
  "Cost Analysis",
  "Architecture Decisions",
  "Downloads",
]);
 
export function isOutputDisplayData(sections: DisplaySection[]): boolean {
  if (!sections || sections.length < 2) return false;
  return sections.some((s) => OUTPUT_HEADINGS.has(s.heading));
}
 