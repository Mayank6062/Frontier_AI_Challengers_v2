import type { DisplaySection } from "@/types/workflow";
import { EnterpriseMermaidCard } from "@/components/document/EnterpriseMermaidCard";
 
type EnterpriseArchitectureBlueprintProps = {
  sections: DisplaySection[];
};
 
export function EnterpriseArchitectureBlueprint({ sections }: EnterpriseArchitectureBlueprintProps) {
  // ═══════════════════════════════════════════════════════════════
  // DATA EXTRACTION - Map backend sections to visual components
  // ═══════════════════════════════════════════════════════════════
 
  const manifestSection = sections.find(s => s.type === "package_manifest") as any;
  const overviewSection = sections.find(s => s.type === "executive_overview") as any;
  const posterSection = sections.find(s => s.type === "executive_poster") as any;
  const hldSection = sections.find(s => s.type === "bullet_hld");
  const lldSection = sections.find(s => s.type === "bullet_lld");
  const securitySection = sections.find(s => s.type === "bullet_security");
  const deploymentSection = sections.find(s => s.type === "bullet_deployment");
  const roadmapSection = sections.find(s => s.type === "roadmap") as any;
  const riskSection = sections.find(s => s.type === "risk_table") as any;
  const costSection = sections.find(s => s.type === "cost_table") as any;
  const decisionSection = sections.find(s => s.type === "decision_table") as any;
  const diagramSection = sections.find(s => s.type === "mermaid");
 
  const manifest = manifestSection?.metadata || {};
  const score = manifestSection?.architecture_score || 0;
  const recommendation = manifestSection?.recommendation_badge || { label: "Pending", color: "info" };
 
  const overview = overviewSection;
  const poster = posterSection?.poster;
  const hldItems = hldSection?.items || [];
  const lldItems = lldSection?.items || [];
  const securityItems = securitySection?.items || [];
  const deploymentItems = deploymentSection?.items || [];
  const phases = roadmapSection?.phases || [];
  const risks = riskSection?.risks || [];
  const costs = costSection?.costs || [];
  const decisions = decisionSection?.decisions || [];
  const diagrams = diagramSection?.diagrams || [];
 
  // Calculate metrics
  const totalCost = costs.find((c: any) =>
    c.category?.toLowerCase() === "total" || c.component?.toLowerCase() === "total"
  );
  const highRisks = risks.filter((r: any) =>
    (r.severity?.toLowerCase() === "high" || r.impact?.toLowerCase() === "high")
  ).length;
 
  // Extract source systems from HLD
  const sourceSystems = hldItems.slice(0, 3).map((item: any) => String(item));
 
  // Extract architecture components from poster sections
  const archComponents = poster?.sections?.flatMap((band: any) =>
    (band.items || []).map((item: any) => ({
      name: String(item.component || item.title || item),
      description: item.description ? String(item.description) : null
    }))
  ) || [];
 
  // Extract technology stack
  const techKeywords = ["Azure", "AWS", "GCP", "Kubernetes", "Docker", "React", "Node.js", "Python", "PostgreSQL", "MongoDB", "Redis", "Kafka", "Databricks", "Snowflake"];
  const technologies = new Set<string>();
  [...hldItems, ...lldItems].forEach((item: any) => {
    const itemStr = String(item);
    techKeywords.forEach(tech => {
      if (itemStr.toLowerCase().includes(tech.toLowerCase())) technologies.add(tech);
    });
  });
 
  const primaryDiagram = diagrams.find((d: any) => d.key === "data_flow" || d.key === "architecture") || diagrams[0];
 
  // If no content, don't render
  if (!manifestSection && !overviewSection && !diagrams.length) {
    return null;
  }
 
  return (
    <div className="relative w-full bg-white" style={{ minHeight: "1400px" }}>
      {/* SVG Definitions for Arrows and Icons */}
      <svg width="0" height="0" className="absolute">
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
            <polygon points="0 0, 10 3, 0 6" fill="#64748B" />
          </marker>
          <marker id="arrowhead-blue" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
            <polygon points="0 0, 10 3, 0 6" fill="#2563EB" />
          </marker>
        </defs>
      </svg>
 
      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* EXECUTIVE HEADER - Solution Identity & Quality Score            */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <div className="relative border-b-4 border-blue-600 bg-gradient-to-r from-slate-50 to-blue-50 px-12 py-8">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-blue-600 px-4 py-1 text-xs font-bold uppercase tracking-wider text-white">
              <span>✨</span> Enterprise Architecture Blueprint
            </div>
            <h1 className="text-4xl font-bold text-slate-900 tracking-tight">
              {manifest.package_title || "Enterprise Solution Architecture"}
            </h1>
            <p className="mt-2 text-lg text-slate-600">
              {manifest.package_subtitle || overview?.content || "End-to-end architecture design and implementation roadmap"}
            </p>
            <div className="mt-4 flex flex-wrap gap-3">
              {manifest.industry && (
                <span className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-1 text-sm font-medium text-slate-700">
                  <span className="text-base">🏢</span> {manifest.industry}
                </span>
              )}
              {manifest.cloud_platform && (
                <span className="inline-flex items-center gap-1 rounded-lg border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">
                  <span className="text-base">☁️</span> {manifest.cloud_platform}
                </span>
              )}
              {phases.length > 0 && (
                <span className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-1 text-sm font-medium text-slate-700">
                  <span className="text-base">📅</span> {phases.length} Implementation Phases
                </span>
              )}
            </div>
          </div>
          <div className="flex flex-col items-end gap-3">
            <div className="flex h-24 w-24 flex-col items-center justify-center rounded-2xl bg-white border-4 border-blue-600 shadow-lg">
              <div className="text-3xl font-bold text-blue-600">{score}</div>
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Quality</div>
            </div>
            <div className={`rounded-xl px-6 py-2 text-center font-bold uppercase tracking-wide text-white ${
              recommendation.color === "success" ? "bg-emerald-600" :
              recommendation.color === "warning" ? "bg-amber-600" :
              recommendation.color === "error" ? "bg-red-600" : "bg-blue-600"
            }`}>
              {recommendation.label}
            </div>
          </div>
        </div>
      </div>
 
      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* BUSINESS CONTEXT - WHY (Executive Overview)                      */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      {overview && (
        <div className="border-b-2 border-slate-200 bg-gradient-to-r from-amber-50 to-orange-50 px-12 py-6">
          <div className="mb-3 inline-flex items-center gap-2 rounded-lg bg-amber-600 px-3 py-1 text-xs font-bold uppercase tracking-wider text-white">
            <span>🎯</span> Business Context
          </div>
          <div className="grid gap-6 lg:grid-cols-3">
            {overview.sections?.map((section: any, idx: number) => (
              <div key={idx} className="rounded-lg border border-amber-200 bg-white p-4">
                <h3 className="mb-2 text-sm font-bold uppercase tracking-wide text-amber-700">
                  {section.label || `Context ${idx + 1}`}
                </h3>
                <p className="text-sm leading-relaxed text-slate-700">{section.text}</p>
              </div>
            ))}
          </div>
        </div>
      )}
 
      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* MAIN ARCHITECTURE FLOW - Three-Column Layout                     */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <div className="relative grid grid-cols-12 gap-0" style={{ minHeight: "800px" }}>
        {/* LEFT LANE: Source Systems */}
        <div className="col-span-2 border-r-2 border-slate-200 bg-slate-50 p-6">
          <div className="sticky top-4">
            <div className="mb-6 rounded-lg bg-slate-700 px-3 py-2 text-center text-sm font-bold uppercase tracking-wider text-white">
              Source Systems
            </div>
            <div className="space-y-4">
              {sourceSystems.length > 0 ? sourceSystems.map((system, idx) => (
                <div key={idx} className="relative rounded-lg border-2 border-slate-300 bg-white p-4 text-center shadow-sm">
                  <div className="mb-2 text-2xl">📦</div>
                  <div className="text-xs font-semibold text-slate-700">{system}</div>
                  {/* Arrow pointing right */}
                  <div className="absolute -right-6 top-1/2 -translate-y-1/2 text-slate-400 text-2xl">→</div>
                </div>
              )) : (
                <div className="rounded-lg border-2 border-slate-300 bg-white p-4 text-center">
                  <div className="mb-2 text-2xl">📦</div>
                  <div className="text-xs font-semibold text-slate-700">Data Sources</div>
                </div>
              )}
            </div>
          </div>
        </div>
 
        {/* CENTER LANE: Architecture Flow with Numbered Steps */}
        <div className="col-span-8 relative bg-white p-8">
          {/* Numbered Architecture Steps */}
          <div className="space-y-6">
            {/* Step 1: Ingestion */}
            <div className="relative rounded-xl border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-cyan-50 p-6">
              <div className="absolute -left-4 -top-4 flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-lg font-bold text-white shadow-lg">
                1
              </div>
              <h3 className="mb-3 text-lg font-bold text-blue-900">🔵 Ingestion Layer</h3>
              <div className="grid gap-3 sm:grid-cols-2">
                {archComponents.slice(0, 4).map((comp, idx) => (
                  <div key={idx} className="rounded-lg border border-blue-200 bg-white p-3">
                    <div className="text-sm font-semibold text-slate-900">{comp.name}</div>
                    {comp.description && <div className="mt-1 text-xs text-slate-600">{comp.description}</div>}
                  </div>
                ))}
              </div>
              <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 text-3xl text-blue-600">↓</div>
            </div>
 
            {/* Step 2: Processing */}
            <div className="relative rounded-xl border-2 border-purple-200 bg-gradient-to-r from-purple-50 to-pink-50 p-6">
              <div className="absolute -left-4 -top-4 flex h-10 w-10 items-center justify-center rounded-full bg-purple-600 text-lg font-bold text-white shadow-lg">
                2
              </div>
              <h3 className="mb-3 text-lg font-bold text-purple-900">🟣 Processing & Transformation</h3>
              <div className="grid gap-3 sm:grid-cols-3">
                {lldItems.slice(0, 6).map((item: any, idx: number) => (
                  <div key={idx} className="flex items-center gap-2 rounded-lg border border-purple-200 bg-white px-3 py-2">
                    <div className="h-2 w-2 rounded-full bg-purple-500"></div>
                    <div className="text-xs font-medium text-slate-700">{String(item)}</div>
                  </div>
                ))}
              </div>
              <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 text-3xl text-purple-600">↓</div>
            </div>
 
            {/* Step 3: Storage & Architecture Diagram */}
            <div className="relative rounded-xl border-2 border-green-200 bg-gradient-to-r from-green-50 to-emerald-50 p-6">
              <div className="absolute -left-4 -top-4 flex h-10 w-10 items-center justify-center rounded-full bg-green-600 text-lg font-bold text-white shadow-lg">
                3
              </div>
              <h3 className="mb-3 text-lg font-bold text-green-900">🟢 Storage & Data Lake</h3>
              {primaryDiagram && (
                <div className="mt-4">
                  <EnterpriseMermaidCard
                    title={primaryDiagram.title || "Solution Architecture"}
                    code={primaryDiagram.code}
                  />
                </div>
              )}
              <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 text-3xl text-green-600">↓</div>
            </div>
 
            {/* Step 4: Analytics */}
            <div className="relative rounded-xl border-2 border-orange-200 bg-gradient-to-r from-orange-50 to-amber-50 p-6">
              <div className="absolute -left-4 -top-4 flex h-10 w-10 items-center justify-center rounded-full bg-orange-600 text-lg font-bold text-white shadow-lg">
                4
              </div>
              <h3 className="mb-3 text-lg font-bold text-orange-900">🟠 Analytics & Compute</h3>
              <div className="flex flex-wrap gap-2">
                {Array.from(technologies).map((tech, idx) => (
                  <span key={idx} className="inline-flex items-center gap-1 rounded-full border border-orange-300 bg-white px-3 py-1 text-xs font-semibold text-orange-700">
                    <span className="text-sm">⚡</span> {tech}
                  </span>
                ))}
              </div>
              <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 text-3xl text-orange-600">↓</div>
            </div>
 
            {/* Step 5: Consumption */}
            <div className="relative rounded-xl border-2 border-pink-200 bg-gradient-to-r from-pink-50 to-rose-50 p-6">
              <div className="absolute -left-4 -top-4 flex h-10 w-10 items-center justify-center rounded-full bg-pink-600 text-lg font-bold text-white shadow-lg">
                5
              </div>
              <h3 className="mb-3 text-lg font-bold text-pink-900">🔴 APIs & Consumption Layer</h3>
              <div className="grid gap-3 sm:grid-cols-2">
                {archComponents.slice(4, 8).map((comp, idx) => (
                  <div key={idx} className="rounded-lg border border-pink-200 bg-white p-3">
                    <div className="text-sm font-semibold text-slate-900">{comp.name}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
 
        {/* RIGHT LANE: Outputs & Business Value */}
        <div className="col-span-2 border-l-2 border-slate-200 bg-slate-50 p-6">
          <div className="sticky top-4">
            <div className="mb-6 rounded-lg bg-emerald-700 px-3 py-2 text-center text-sm font-bold uppercase tracking-wider text-white">
              Business Value
            </div>
            <div className="space-y-4">
              <div className="rounded-lg border-2 border-emerald-300 bg-white p-4 text-center shadow-sm">
                <div className="mb-2 text-2xl">📊</div>
                <div className="text-xs font-semibold text-slate-700">BI & Analytics</div>
              </div>
              <div className="rounded-lg border-2 border-emerald-300 bg-white p-4 text-center shadow-sm">
                <div className="mb-2 text-2xl">👥</div>
                <div className="text-xs font-semibold text-slate-700">Business Users</div>
              </div>
              <div className="rounded-lg border-2 border-emerald-300 bg-white p-4 text-center shadow-sm">
                <div className="mb-2 text-2xl">📱</div>
                <div className="text-xs font-semibold text-slate-700">Applications</div>
              </div>
            </div>
          </div>
        </div>
      </div>
 
      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* PLATFORM LAYER - Security, Compliance, Monitoring               */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <div className="border-t-4 border-slate-300 bg-slate-100 px-12 py-6">
        <div className="mb-4 inline-flex items-center gap-2 rounded-lg bg-slate-700 px-3 py-1 text-xs font-bold uppercase tracking-wider text-white">
          <span>🛡️</span> Platform Services & Governance
        </div>
        <div className="grid gap-4 lg:grid-cols-4">
          {/* Security */}
          {securityItems.length > 0 && (
            <div className="rounded-lg border border-slate-300 bg-white p-4">
              <h4 className="mb-2 text-sm font-bold text-slate-900">🔒 Security</h4>
              <ul className="space-y-1">
                {securityItems.slice(0, 3).map((item: any, idx: number) => (
                  <li key={idx} className="text-xs text-slate-600">• {String(item).substring(0, 50)}</li>
                ))}
              </ul>
            </div>
          )}
          {/* Deployment */}
          {deploymentItems.length > 0 && (
            <div className="rounded-lg border border-slate-300 bg-white p-4">
              <h4 className="mb-2 text-sm font-bold text-slate-900">🚀 Deployment</h4>
              <ul className="space-y-1">
                {deploymentItems.slice(0, 3).map((item: any, idx: number) => (
                  <li key={idx} className="text-xs text-slate-600">• {String(item).substring(0, 50)}</li>
                ))}
              </ul>
            </div>
          )}
          {/* Monitoring */}
          <div className="rounded-lg border border-slate-300 bg-white p-4">
            <h4 className="mb-2 text-sm font-bold text-slate-900">📊 Monitoring</h4>
            <div className="space-y-1 text-xs text-slate-600">
              <div>• Performance metrics</div>
              <div>• Cost tracking</div>
              <div>• Compliance auditing</div>
            </div>
          </div>
          {/* Governance */}
          <div className="rounded-lg border border-slate-300 bg-white p-4">
            <h4 className="mb-2 text-sm font-bold text-slate-900">⚖️ Governance</h4>
            <div className="space-y-1 text-xs text-slate-600">
              <div>• Data cataloging</div>
              <div>• Access controls</div>
              <div>• Policy enforcement</div>
            </div>
          </div>
        </div>
      </div>
 
      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* VALUE SUMMARY - Timeline, Risks, Costs, Decisions              */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <div className="border-t-2 border-slate-200 bg-white px-12 py-6">
        <div className="grid gap-6 lg:grid-cols-4">
          {/* Timeline */}
          {phases.length > 0 && (
            <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
              <h4 className="mb-3 flex items-center gap-2 text-sm font-bold text-blue-900">
                <span className="text-base">📅</span> Timeline
              </h4>
              <div className="space-y-2">
                {phases.slice(0, 3).map((phase: any, idx: number) => (
                  <div key={idx} className="flex items-center gap-2">
                    <div className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">{idx + 1}</div>
                    <div className="text-xs font-medium text-slate-700">{phase.phase || phase.name}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
 
          {/* Risks */}
          {risks.length > 0 && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
              <h4 className="mb-3 flex items-center gap-2 text-sm font-bold text-amber-900">
                <span className="text-base">⚠️</span> Key Risks
              </h4>
              <div className="mb-2 text-2xl font-bold text-amber-700">
                {risks.length} Total
                {highRisks > 0 && <span className="ml-2 text-base text-red-600">({highRisks} High)</span>}
              </div>
              <div className="text-xs text-slate-600">Risk mitigation strategies defined</div>
            </div>
          )}
 
          {/* Costs */}
          {totalCost && (
            <div className="rounded-lg border border-green-200 bg-green-50 p-4">
              <h4 className="mb-3 flex items-center gap-2 text-sm font-bold text-green-900">
                <span className="text-base">💰</span> Investment
              </h4>
              <div className="text-2xl font-bold text-green-700">
                {totalCost.estimate || totalCost.cost || "TBD"}
              </div>
              <div className="mt-1 text-xs text-slate-600">Total estimated cost</div>
            </div>
          )}
 
          {/* Decisions */}
          {decisions.length > 0 && (
            <div className="rounded-lg border border-purple-200 bg-purple-50 p-4">
              <h4 className="mb-3 flex items-center gap-2 text-sm font-bold text-purple-900">
                <span className="text-base">✓</span> Decisions
              </h4>
              <div className="text-2xl font-bold text-purple-700">{decisions.length}</div>
              <div className="mt-1 text-xs text-slate-600">Architecture decisions documented</div>
            </div>
          )}
        </div>
      </div>
 
      {/* ═══════════════════════════════════════════════════════════════ */}
      {/* FOOTER - Final Recommendation & Expected Outcomes               */}
      {/* ═══════════════════════════════════════════════════════════════ */}
      <div className={`border-t-4 px-12 py-6 text-white ${
        recommendation.color === "success" ? "border-emerald-600 bg-gradient-to-r from-emerald-600 to-teal-600" :
        recommendation.color === "warning" ? "border-amber-600 bg-gradient-to-r from-amber-600 to-orange-600" :
        "border-blue-600 bg-gradient-to-r from-blue-600 to-indigo-600"
      }`}>
        <div className="flex items-center justify-between">
          <div>
            <div className="mb-2 text-sm font-bold uppercase tracking-wider opacity-90">Final Recommendation</div>
            <div className="text-3xl font-bold">{recommendation.label}</div>
            {manifest.final_recommendation && (
              <p className="mt-2 max-w-2xl text-sm opacity-90">{String(manifest.final_recommendation)}</p>
            )}
          </div>
          <div className="text-right">
            <div className="mb-1 text-sm font-semibold opacity-90">Document Version</div>
            <div className="text-xl font-bold">{manifest.document_version || "1.0"}</div>
            <div className="mt-1 text-xs opacity-75">Generated {new Date().toLocaleDateString()}</div>
          </div>
        </div>
      </div>
    </div>
  );
}