/**
 * ExecutiveArchitecturePoster — Premium Enterprise Architecture Infographic
 *
 * v2: Dynamic-height poster template (content-driven, NOT fixed pixel regions).
 *
 * Design reference: Microsoft Architecture Center / Azure Reference Architectures /
 * Gartner Enterprise Blueprint / EPAM & Deloitte solution-architecture one-pagers.
 *
 * WHY THIS REWRITE:
 * The previous version assigned every region (businessHero, columns, technology,
 * footer) a HARD-CODED pixel height inside a fixed 2400x1400 canvas, then flattened
 * every matched section into one undifferentiated card grid per region. Because the
 * number of items per section is entirely data-driven, and the grid's card height
 * had a `min(90, max(60, ...))` floor that ignored the region's available height,
 * any section with more than a handful of items simply overflowed its box — which is
 * exactly what the screenshot shows (Business Objectives bleeding into the 3-column
 * row, RBAC pushed out below Technology Foundation, the footer band floating mid-page
 * on top of overflowed content). On top of that, every region used the same flat
 * "rows of bordered rectangles" card, all mapped sections were merged into a single
 * undifferentiated pool (losing the Security vs Monitoring vs Governance distinction),
 * and there was no visual narrative connecting one region to the next — so the result
 * reads as a dashboard/spreadsheet export rather than a designed poster.
 *
 * This version:
 *   1. Computes every block's height from its own content (rows × card height),
 *      then stacks blocks top-to-bottom and sizes the SVG canvas to the real total —
 *      nothing overflows and nothing overlaps, at any data volume.
 *   2. Keeps each semantic sub-group (Security / Platform / Monitoring / Governance,
 *      Objectives / Challenges, etc.) in its own labeled lane instead of one merged pool.
 *   3. Renders the "Solution Architecture" column as a connected vertical spine
 *      (numbered, linked nodes) instead of a plain card grid, and threads a single
 *      numbered narrative rail (01 → 06) through the whole poster so the eye reads
 *      Business Context → Inputs/Architecture/Value → Foundation → Roadmap in order.
 *   4. Replaces the dashboard card styling (thin border + top stripe) with a quieter
 *      editorial system: soft tint panels, glass cards with a colored left rule and
 *      icon badge, restrained shadows, and a real typographic scale.
 *
 * KEY BEHAVIOR PRESERVED: consumes EXACTLY `poster.sections` as before (same
 * `PosterBand` shape). No backend / schema changes required. `y` / `height` on
 * incoming sections are still ignored — layout is entirely template + content driven.
 */

import { Download, Maximize2, Minimize2 } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { cn } from "@/utils/cn";

// ─── Types (unchanged shape — backend/schema compatible) ────────────

export type PosterBand = {
  band: string;
  y?: number;              // ignored — layout is content-driven
  height?: number;         // ignored — layout is content-driven
  background?: string;
  text_color?: string;
  title?: string;
  subtitle?: string;
  items?: Array<string | { label?: string; description?: string; color?: string }>;
};

export type ExecutivePoster = {
  title?: string;
  subtitle?: string;
  canvas?: { width?: number; height?: number };
  sections?: PosterBand[];
};

// ─── Design tokens ───────────────────────────────────────────────────

const CANVAS_W = 2400;
const MARGIN = 44;
const CONTENT_W = CANVAS_W - MARGIN * 2;

const T = {
  canvasBg: "#F6F7FA",
  header: { from: "#0B1220", to: "#18213A", accent: "#818CF8", fg: "#F8FAFC", sub: "#9AA5C0" },
  objectives: { accent: "#2563EB", tint: "#EEF3FF", fg: "#1E3A8A", icon: "🎯" },
  challenges: { accent: "#DC2626", tint: "#FEF1F1", fg: "#7F1D1D", icon: "⚠️" },
  overview: { accent: "#059669", tint: "#ECFDF5", fg: "#065F46", icon: "💡" },
  inputs: { accent: "#0D9488", tint: "#F0FDFA", fg: "#134E4A", icon: "📥" },
  architecture: { accent: "#4F46E5", tint: "#F3F3FF", fg: "#312E81", icon: "🏗️" },
  outputs: { accent: "#D97706", tint: "#FFFBEB", fg: "#78350F", icon: "📊" },
  security: { accent: "#B45309", tint: "#FFF8ED", fg: "#78350F", icon: "🔐" },
  platform: { accent: "#059669", tint: "#ECFDF5", fg: "#065F46", icon: "☁️" },
  monitoring: { accent: "#0284C7", tint: "#F0F9FF", fg: "#0C4A6E", icon: "📈" },
  governance: { accent: "#475569", tint: "#F8FAFC", fg: "#1E293B", icon: "🛡️" },
  roadmap: { accent: "#818CF8", fg: "#E7E9FF" },
  footer: { bg: "#0B1220", fg: "#8792AD" },
} as const;

type Theme = { accent: string; tint: string; fg: string; icon?: string };

type BucketKey =
  | "objectives" | "challenges" | "overview"
  | "inputs" | "architecture" | "outputs"
  | "security" | "platform" | "monitoring" | "governance"
  | "roadmap" | "footer" | "header" | "other";

function classifyBand(bandName: string): BucketKey {
  const n = (bandName || "").toLowerCase();
  if (n.includes("header")) return "header";
  if (n.includes("footer")) return "footer";
  if (n.includes("roadmap") || n.includes("next step") || n.includes("implementation")) return "roadmap";
  if (n.includes("objective")) return "objectives";
  if (n.includes("challenge")) return "challenges";
  if (n.includes("overview")) return "overview";
  if (n.includes("input") || n.includes("data source")) return "inputs";
  if (n.includes("output") || n.includes("outcome") || n.includes("benefit") || n.includes("kpi") || n.includes("business value")) return "outputs";
  if (n.includes("security")) return "security";
  if (n.includes("monitor") || n.includes("operation")) return "monitoring";
  if (n.includes("governance") || n.includes("compliance")) return "governance";
  if (n.includes("cloud") || n.includes("technology stack") || n.includes("platform")) return "platform";
  // Core components / data flow / agent flow / platform components -> architecture spine
  return "architecture";
}

function themeFor(key: BucketKey): Theme {
  switch (key) {
    case "objectives": return T.objectives;
    case "challenges": return T.challenges;
    case "overview": return T.overview;
    case "inputs": return T.inputs;
    case "architecture": return T.architecture;
    case "outputs": return T.outputs;
    case "security": return T.security;
    case "platform": return T.platform;
    case "monitoring": return T.monitoring;
    case "governance": return T.governance;
    default: return { accent: "#64748B", tint: "#F8FAFC", fg: "#334155", icon: "→" };
  }
}

// ─── Download helpers (unchanged) ────────────────────────────────────

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 100);
}

function svgToPngBlob(svgEl: SVGElement, scale = 2): Promise<Blob | null> {
  return new Promise((resolve) => {
    const clone = svgEl.cloneNode(true) as SVGElement;
    const bbox = svgEl.getBoundingClientRect();
    const w = bbox.width || 2200;
    const h = bbox.height || 1600;
    clone.setAttribute("width", String(w));
    clone.setAttribute("height", String(h));

    const svgData = new XMLSerializer().serializeToString(clone);
    const svgBlob = new Blob([svgData], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(svgBlob);

    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = w * scale;
      canvas.height = h * scale;
      const ctx = canvas.getContext("2d");
      if (!ctx) return resolve(null);
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((blob) => {
        URL.revokeObjectURL(url);
        resolve(blob);
      }, "image/png");
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      resolve(null);
    };
    img.src = url;
  });
}

// ─── Content helpers ──────────────────────────────────────────────────

type Item = { label: string; description?: string; color?: string };

function normalizeItem(item: unknown): Item {
  if (typeof item === "string") return { label: item };
  if (item && typeof item === "object") {
    const obj = item as Record<string, unknown>;
    return {
      label: String(obj.label ?? obj.name ?? obj.title ?? ""),
      description: obj.description ? String(obj.description) : undefined,
      color: obj.color ? String(obj.color) : undefined,
    };
  }
  return { label: String(item ?? "") };
}

function wrapText(text: string, maxChars: number, maxLines = 2): string[] {
  if (!text) return [];
  const words = text.split(/\s+/);
  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    if ((current + " " + word).trim().length > maxChars) {
      if (current) lines.push(current);
      current = word;
    } else {
      current = (current + " " + word).trim();
    }
  }
  if (current) lines.push(current);
  if (lines.length > maxLines) {
    lines[maxLines - 1] = lines[maxLines - 1].replace(/\s*\S*$/, "") + "…";
    return lines.slice(0, maxLines);
  }
  return lines;
}

function itemsOf(sections: PosterBand[]): Item[] {
  return sections.flatMap(s => (s.items ?? []).map(normalizeItem)).filter(i => i.label);
}

// ─── Layout constants ─────────────────────────────────────────────────

const HEADER_H = 168;
const FOOTER_H = 76;
const BLOCK_GAP = 46;          // vertical space between stacked blocks (holds the connector)
const LANE_GAP = 22;
const CARD_GAP = 12;
const PAD = 18;
const TITLE_H = 36;
const CARD_H = 78;
const CARD_H_COMPACT = 52;
const SPINE_NODE_H = 66;
const SPINE_GAP = 12;

function rowsFor(count: number, columns: number) {
  return Math.max(1, Math.ceil(Math.max(count, 1) / columns));
}

function gridLaneHeight(count: number, columns: number, cardH: number) {
  if (count === 0) return 0;
  const rows = rowsFor(count, columns);
  return PAD * 2 + TITLE_H + rows * cardH + (rows - 1) * CARD_GAP;
}

function spineLaneHeight(count: number) {
  if (count === 0) return 0;
  return PAD * 2 + TITLE_H + count * SPINE_NODE_H + (count - 1) * SPINE_GAP;
}

// ─── Lane (labeled group of glass cards) ──────────────────────────────

function Lane({
  x, y, width, height, title, theme, items, columns,
}: {
  x: number; y: number; width: number; height: number;
  title: string; theme: Theme; items: Item[]; columns: number;
}) {
  if (items.length === 0 || height === 0) return null;
  const innerW = width - PAD * 2;
  const cardW = (innerW - CARD_GAP * (columns - 1)) / columns;
  const rows = rowsFor(items.length, columns);
  const availH = height - PAD * 2 - TITLE_H - CARD_GAP * (rows - 1);
  const cardH = availH / rows;

  return (
    <g>
      <rect x={x} y={y} width={width} height={height} rx={16} fill={theme.tint} stroke="#FFFFFF" strokeWidth={1} />
      <rect x={x} y={y} width={4} height={height} rx={2} fill={theme.accent} />
      <text x={x + PAD} y={y + 25} fontSize={13} fontWeight={800} fill={theme.accent}
        fontFamily="Inter, -apple-system, sans-serif" letterSpacing={1}>
        {title.toUpperCase()}
      </text>
      {items.map((item, idx) => {
        const col = idx % columns;
        const row = Math.floor(idx / columns);
        const cx = x + PAD + col * (cardW + CARD_GAP);
        const cy = y + PAD + TITLE_H + row * (cardH + CARD_GAP);
        return <GlassCard key={idx} item={item} x={cx} y={cy} width={cardW} height={cardH} theme={theme} />;
      })}
    </g>
  );
}

function GlassCard({
  item, x, y, width, height, theme, compact = false,
}: { item: Item; x: number; y: number; width: number; height: number; theme: Theme; compact?: boolean }) {
  const uid = `${Math.round(x)}-${Math.round(y)}`;
  const hasIcon = !!theme.icon;
  const labelX = x + (hasIcon ? 40 : 16);
  const labelLines = wrapText(item.label, Math.floor((width - (hasIcon ? 48 : 24)) / 6.6), compact ? 1 : 2);
  const descLine = item.description ? wrapText(item.description, Math.floor((width - 24) / 6), 1)[0] : undefined;

  return (
    <g>
      <defs>
        <linearGradient id={`g-${uid}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#FFFFFF" stopOpacity={0.95} />
          <stop offset="100%" stopColor="#FFFFFF" stopOpacity={0.65} />
        </linearGradient>
      </defs>
      <rect x={x} y={y} width={width} height={height} rx={10} fill={`url(#g-${uid})`}
        stroke={theme.accent} strokeOpacity={0.35} strokeWidth={1}
        style={{ filter: "drop-shadow(0 1px 2px rgba(15,23,42,0.08))" }} />
      <rect x={x} y={y} width={3} height={height} rx={1.5} fill={theme.accent} />
      {hasIcon && (
        <>
          <circle cx={x + 22} cy={y + height / 2 - (descLine ? 6 : 0)} r={11} fill={theme.tint} stroke={theme.accent} strokeOpacity={0.4} />
          <text x={x + 22} y={y + height / 2 - (descLine ? 6 : 0) + 4} fontSize={11} textAnchor="middle">{theme.icon}</text>
        </>
      )}
      <text x={labelX} y={y + (labelLines.length > 1 ? height / 2 - 10 : height / 2 - (descLine ? 6 : -4))}
        fontSize={12.5} fontWeight={700} fill={theme.fg} fontFamily="Inter, -apple-system, sans-serif">
        {labelLines[0]}
      </text>
      {labelLines[1] && (
        <text x={labelX} y={y + height / 2 + 6} fontSize={12.5} fontWeight={700} fill={theme.fg}
          fontFamily="Inter, -apple-system, sans-serif">
          {labelLines[1]}
        </text>
      )}
      {descLine && (
        <text x={labelX} y={y + height - 12} fontSize={10.5} fontWeight={500} fill={theme.accent} opacity={0.85}
          fontFamily="Inter, -apple-system, sans-serif">
          {descLine}
        </text>
      )}
    </g>
  );
}

// ─── Architecture spine (signature element: connected node stack) ────

function ArchitectureSpine({
  x, y, width, height, title, theme, items,
}: { x: number; y: number; width: number; height: number; title: string; theme: Theme; items: Item[] }) {
  if (items.length === 0) return null;
  const railX = x + PAD + 14;
  const rowW = width - PAD * 2 - 30;
  const rowX = railX + 26;

  return (
    <g>
      <rect x={x} y={y} width={width} height={height} rx={16} fill={theme.tint} stroke="#FFFFFF" strokeWidth={1} />
      <rect x={x} y={y} width={4} height={height} rx={2} fill={theme.accent} />
      <text x={x + PAD} y={y + 25} fontSize={13} fontWeight={800} fill={theme.accent}
        fontFamily="Inter, -apple-system, sans-serif" letterSpacing={1}>
        {title.toUpperCase()}
      </text>
      {/* connecting rail */}
      <line x1={railX} y1={y + PAD + TITLE_H + SPINE_NODE_H / 2}
        x2={railX} y2={y + PAD + TITLE_H + (items.length - 1) * (SPINE_NODE_H + SPINE_GAP) + SPINE_NODE_H / 2}
        stroke={theme.accent} strokeOpacity={0.35} strokeWidth={2} strokeDasharray="1,6" strokeLinecap="round" />
      {items.map((item, idx) => {
        const ny = y + PAD + TITLE_H + idx * (SPINE_NODE_H + SPINE_GAP);
        const midY = ny + SPINE_NODE_H / 2;
        const label = wrapText(item.label, Math.floor((rowW - 20) / 7), 1)[0];
        const desc = item.description ? wrapText(item.description, Math.floor((rowW - 20) / 6.4), 1)[0] : undefined;
        return (
          <g key={idx}>
            <circle cx={railX} cy={midY} r={9} fill="#FFFFFF" stroke={theme.accent} strokeWidth={2} />
            <text x={railX} y={midY + 3.5} fontSize={9} fontWeight={800} textAnchor="middle" fill={theme.accent}
              fontFamily="Inter, -apple-system, sans-serif">{idx + 1}</text>
            <rect x={rowX} y={ny} width={rowW} height={SPINE_NODE_H} rx={9} fill="#FFFFFF"
              stroke={theme.accent} strokeOpacity={0.3}
              style={{ filter: "drop-shadow(0 1px 2px rgba(15,23,42,0.06))" }} />
            <text x={rowX + 14} y={ny + (desc ? 26 : SPINE_NODE_H / 2 + 4)} fontSize={13} fontWeight={700}
              fill={theme.fg} fontFamily="Inter, -apple-system, sans-serif">{label}</text>
            {desc && (
              <text x={rowX + 14} y={ny + 44} fontSize={10.5} fontWeight={500} fill={theme.accent} opacity={0.85}
                fontFamily="Inter, -apple-system, sans-serif">{desc}</text>
            )}
          </g>
        );
      })}
    </g>
  );
}

// ─── Connector between stacked blocks ─────────────────────────────────

function StageConnector({ cx, y1, y2, color }: { cx: number; y1: number; y2: number; color: string }) {
  const midY = (y1 + y2) / 2;
  return (
    <g opacity={0.6}>
      <line x1={cx} y1={y1} x2={cx} y2={y2 - 8} stroke={color} strokeWidth={2} strokeDasharray="1,6" strokeLinecap="round" />
      <path d={`M ${cx - 6} ${y2 - 12} L ${cx} ${y2} L ${cx + 6} ${y2 - 12}`} fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
    </g>
  );
}

// ─── Roadmap timeline band (a genuine ordered sequence → numbered) ────

function RoadmapBand({ x, y, width, height, items }: { x: number; y: number; width: number; height: number; items: Item[] }) {
  if (items.length === 0) return null;
  const n = items.length;
  const stepW = width / n;
  const lineY = y + 58;

  return (
    <g>
      <rect x={x} y={y} width={width} height={height} rx={18} fill={T.header.from} />
      <text x={x + 28} y={y + 30} fontSize={13} fontWeight={800} fill={T.roadmap.accent}
        letterSpacing={1} fontFamily="Inter, -apple-system, sans-serif">IMPLEMENTATION ROADMAP</text>
      <line x1={x + stepW / 2} y1={lineY} x2={x + width - stepW / 2} y2={lineY}
        stroke={T.roadmap.accent} strokeOpacity={0.4} strokeWidth={2} />
      {items.map((item, idx) => {
        const cx = x + stepW * idx + stepW / 2;
        const label = wrapText(item.label, Math.floor(stepW / 7), 2);
        return (
          <g key={idx}>
            <circle cx={cx} cy={lineY} r={16} fill={T.header.from} stroke={T.roadmap.accent} strokeWidth={2} />
            <text x={cx} y={lineY + 5} fontSize={12} fontWeight={800} textAnchor="middle" fill={T.roadmap.accent}
              fontFamily="Inter, -apple-system, sans-serif">{String(idx + 1).padStart(2, "0")}</text>
            {label.map((ln, li) => (
              <text key={li} x={cx} y={lineY + 34 + li * 16} fontSize={12} fontWeight={600} textAnchor="middle"
                fill={T.roadmap.fg} fontFamily="Inter, -apple-system, sans-serif">{ln}</text>
            ))}
          </g>
        );
      })}
    </g>
  );
}

// ─── Public component ─────────────────────────────────────────────────

type Props = { poster: ExecutivePoster; description?: string };

export function ExecutiveArchitecturePoster({ poster, description }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const sections = poster?.sections ?? [];

  const buckets = useMemo(() => {
    const b: Record<BucketKey, PosterBand[]> = {
      objectives: [], challenges: [], overview: [], inputs: [], architecture: [],
      outputs: [], security: [], platform: [], monitoring: [], governance: [],
      roadmap: [], footer: [], header: [], other: [],
    };
    for (const s of sections) b[classifyBand(s.band || "")].push(s);
    return b;
  }, [sections]);

  // ── Compute a dynamic, non-overlapping vertical stack ───────────────
  const layout = useMemo(() => {
    const objectives = itemsOf(buckets.objectives);
    const challenges = itemsOf(buckets.challenges);
    const overview = itemsOf(buckets.overview);
    const inputs = itemsOf(buckets.inputs);
    const architecture = itemsOf(buckets.architecture);
    const outputs = itemsOf(buckets.outputs);
    const security = itemsOf(buckets.security);
    const platform = itemsOf(buckets.platform);
    const monitoring = itemsOf(buckets.monitoring);
    const governance = itemsOf(buckets.governance);
    const roadmap = itemsOf(buckets.roadmap);

    let cursor = MARGIN + HEADER_H;
    const blocks: Array<{ key: string; y: number; height: number }> = [];

    const pushBlock = (key: string, height: number) => {
      if (height <= 0) return;
      if (blocks.length > 0) cursor += BLOCK_GAP;
      blocks.push({ key, y: cursor, height });
      cursor += height;
    };

    // Block 1: business context (objectives / challenges / overview banner)
    const overviewH = overview.length ? gridLaneHeight(overview.length, Math.min(3, overview.length), CARD_H_COMPACT) : 0;
    const objH = gridLaneHeight(objectives.length, objectives.length > 3 ? 2 : 1, CARD_H);
    const chalH = gridLaneHeight(challenges.length, challenges.length > 3 ? 2 : 1, CARD_H);
    const businessH = Math.max(objH, chalH);
    pushBlock("overview", overviewH);
    pushBlock("business", businessH);

    // Block 2: three-lane flow (inputs / architecture spine / outputs)
    const inputsH = gridLaneHeight(inputs.length, 1, CARD_H);
    const outputsH = gridLaneHeight(outputs.length, 1, CARD_H);
    const archH = spineLaneHeight(architecture.length);
    const flowH = Math.max(inputsH, outputsH, archH, 200);
    pushBlock("flow", flowH);

    // Block 3: technology foundation (security / platform / monitoring / governance)
    const techLanes = [
      { key: "security", items: security }, { key: "platform", items: platform },
      { key: "monitoring", items: monitoring }, { key: "governance", items: governance },
    ].filter(l => l.items.length > 0);
    const techH = techLanes.length
      ? Math.max(...techLanes.map(l => gridLaneHeight(l.items.length, 1, CARD_H_COMPACT)))
      : 0;
    pushBlock("technology", techH);

    // Block 4: roadmap
    const roadmapH = roadmap.length ? 190 : 0;
    pushBlock("roadmap", roadmapH);

    const totalHeight = cursor + BLOCK_GAP + FOOTER_H + MARGIN;

    return {
      totalHeight, blocks,
      data: { objectives, challenges, overview, inputs, architecture, outputs, security, platform, monitoring, governance, roadmap, techLanes },
      heights: { overviewH, objH, chalH, businessH, inputsH, outputsH, archH, flowH, techH, roadmapH },
    };
  }, [buckets]);

  const width = CANVAS_W;
  const height = Math.max(900, layout.totalHeight);
  const stageColor = T.header.accent;

  // ── Fullscreen ─────────────────────────────────────────────────────
  const toggleFullscreen = useCallback(() => {
    const card = containerRef.current;
    if (!card) return;
    if (!document.fullscreenElement) {
      card.requestFullscreen?.().then(() => setIsFullscreen(true)).catch(() => {});
    } else {
      document.exitFullscreen?.().then(() => setIsFullscreen(false)).catch(() => {});
    }
  }, []);

  useEffect(() => {
    const handler = () => setIsFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", handler);
    return () => document.removeEventListener("fullscreenchange", handler);
  }, []);

  // ── Downloads ──────────────────────────────────────────────────────
  const downloadSVG = useCallback(() => {
    const svg = svgRef.current;
    if (!svg) return;
    const data = new XMLSerializer().serializeToString(svg);
    const blob = new Blob([data], { type: "image/svg+xml;charset=utf-8" });
    downloadBlob(blob, "enterprise_architecture_infographic.svg");
  }, []);

  const downloadPNG = useCallback(async () => {
    const svg = svgRef.current;
    if (!svg) return;
    const blob = await svgToPngBlob(svg, 3);
    if (blob) downloadBlob(blob, "enterprise_architecture_infographic.png");
  }, []);

  if (!poster) return null;
  if (sections.length === 0) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50/60 p-4 text-sm text-amber-800">
        Executive Architecture Poster sections are empty. The LLM did not generate poster band data.
      </div>
    );
  }

  const find = (key: string) => layout.blocks.find(b => b.key === key);
  const overviewBlock = find("overview");
  const businessBlock = find("business");
  const flowBlock = find("flow");
  const techBlock = find("technology");
  const roadmapBlock = find("roadmap");

  const colGap = LANE_GAP;
  const colW = (CONTENT_W - colGap * 2) / 3;

  return (
    <div
      ref={containerRef}
      className={cn(
        "rounded-xl border border-slate-200 bg-white shadow-lg transition-shadow hover:shadow-xl",
        isFullscreen && "fixed inset-0 z-50 flex flex-col rounded-none border-0",
      )}
    >
      {/* Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 px-6 py-4 shadow-sm">
        <div className="min-w-0 flex-1">
          <h3 className="text-lg font-bold text-slate-900">🏢 Enterprise Architecture Infographic</h3>
          {description && <p className="mt-1 text-sm text-slate-600">{description}</p>}
          <div className="mt-2 flex items-center gap-2">
            <span className="inline-block rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider text-blue-700">
              Production Ready
            </span>
            <span className="text-xs text-slate-500">• AI Generated • CTO Approved</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={toggleFullscreen} title={isFullscreen ? "Exit Fullscreen" : "View Fullscreen"}
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 shadow-sm transition-all hover:bg-slate-50 hover:shadow-md">
            {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </button>
          <button onClick={downloadSVG} title="Download SVG (Vector)"
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 shadow-sm transition-all hover:bg-slate-50 hover:shadow-md">
            <Download className="h-4 w-4" />
          </button>
          <button onClick={downloadPNG} title="Download PNG (Raster)"
            className="inline-flex items-center gap-2 rounded-lg border-2 border-indigo-300 bg-gradient-to-r from-indigo-50 to-blue-50 px-3 py-2 text-sm font-semibold text-indigo-700 shadow-md transition-all hover:shadow-lg">
            <Download className="h-4 w-4" /> PNG
          </button>
        </div>
      </div>

      {/* Viewport */}
      <div className={cn("overflow-auto bg-gradient-to-b from-slate-50 to-slate-100 p-4", isFullscreen ? "flex-1" : "")}>
        <svg ref={svgRef} viewBox={`0 0 ${width} ${height}`} width="100%"
          style={{ maxWidth: "100%", height: "auto", display: "block" }} xmlns="http://www.w3.org/2000/svg">

          <rect x={0} y={0} width={width} height={height} fill={T.canvasBg} />

          {/* ── HEADER ── */}
          <defs>
            <linearGradient id="headerGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor={T.header.from} />
              <stop offset="100%" stopColor={T.header.to} />
            </linearGradient>
          </defs>
          <rect x={0} y={0} width={width} height={HEADER_H + MARGIN} fill="url(#headerGrad)" />
          <text x={MARGIN} y={54} fontSize={12} fontWeight={800} letterSpacing={2.5} fill={T.header.accent}
            fontFamily="Inter, -apple-system, sans-serif">ENTERPRISE ARCHITECTURE BLUEPRINT</text>
          <text x={MARGIN} y={102} fontSize={38} fontWeight={900} fill={T.header.fg} letterSpacing={-0.5}
            fontFamily="Inter, -apple-system, sans-serif">{poster.title ?? "Enterprise Solution Architecture"}</text>
          {poster.subtitle && (
            <text x={MARGIN} y={132} fontSize={15} fontWeight={500} fill={T.header.sub}
              fontFamily="Inter, -apple-system, sans-serif">{poster.subtitle}</text>
          )}
          <rect x={MARGIN} y={148} width={140} height={3} rx={1.5} fill={T.header.accent} />

          {/* ── OVERVIEW BANNER ── */}
          {overviewBlock && (
            <Lane x={MARGIN} y={overviewBlock.y} width={CONTENT_W} height={overviewBlock.height}
              title={buckets.overview[0]?.band || "Solution Overview"} theme={T.overview}
              items={layout.data.overview} columns={Math.min(3, layout.data.overview.length)} />
          )}

          {/* ── BUSINESS CONTEXT ── */}
          {businessBlock && (
            <>
              {layout.data.objectives.length > 0 && (
                <Lane x={MARGIN} y={businessBlock.y} width={CONTENT_W / 2 - colGap / 2} height={businessBlock.height}
                  title={buckets.objectives[0]?.band || "Business Objectives"} theme={T.objectives}
                  items={layout.data.objectives} columns={layout.data.objectives.length > 3 ? 2 : 1} />
              )}
              {layout.data.challenges.length > 0 && (
                <Lane x={MARGIN + CONTENT_W / 2 + colGap / 2} y={businessBlock.y}
                  width={CONTENT_W / 2 - colGap / 2} height={businessBlock.height}
                  title={buckets.challenges[0]?.band || "Current Challenges"} theme={T.challenges}
                  items={layout.data.challenges} columns={layout.data.challenges.length > 3 ? 2 : 1} />
              )}
            </>
          )}

          {/* ── THREE-LANE FLOW: Inputs → Core Architecture → Business Value ── */}
          {flowBlock && (
            <>
              <Lane x={MARGIN} y={flowBlock.y} width={colW} height={flowBlock.height}
                title="Inputs" theme={T.inputs} items={layout.data.inputs} columns={1} />
              <ArchitectureSpine x={MARGIN + colW + colGap} y={flowBlock.y} width={colW} height={flowBlock.height}
                title="Solution Architecture" theme={T.architecture} items={layout.data.architecture} />
              <Lane x={MARGIN + (colW + colGap) * 2} y={flowBlock.y} width={colW} height={flowBlock.height}
                title="Business Value" theme={T.outputs} items={layout.data.outputs} columns={1} />
              {layout.data.inputs.length > 0 && (
                <path d={`M ${MARGIN + colW} ${flowBlock.y + flowBlock.height / 2} L ${MARGIN + colW + colGap} ${flowBlock.y + flowBlock.height / 2}`}
                  stroke={T.architecture.accent} strokeOpacity={0.4} strokeWidth={2} markerEnd="url(#arrowIn)" />
              )}
              {layout.data.outputs.length > 0 && (
                <path d={`M ${MARGIN + (colW + colGap) * 2 - colGap} ${flowBlock.y + flowBlock.height / 2} L ${MARGIN + (colW + colGap) * 2} ${flowBlock.y + flowBlock.height / 2}`}
                  stroke={T.outputs.accent} strokeOpacity={0.4} strokeWidth={2} markerEnd="url(#arrowOut)" />
              )}
              <defs>
                <marker id="arrowIn" markerWidth={8} markerHeight={8} refX={6} refY={3} orient="auto">
                  <path d="M0,0 L0,6 L7,3 z" fill={T.architecture.accent} />
                </marker>
                <marker id="arrowOut" markerWidth={8} markerHeight={8} refX={6} refY={3} orient="auto">
                  <path d="M0,0 L0,6 L7,3 z" fill={T.outputs.accent} />
                </marker>
              </defs>
            </>
          )}

          {/* ── TECHNOLOGY FOUNDATION ── */}
          {techBlock && (() => {
            const lanes = layout.data.techLanes as Array<{ key: string; items: Item[] }>;
            const laneW = (CONTENT_W - colGap * (lanes.length - 1)) / lanes.length;
            const titles: Record<string, string> = { security: "Security", platform: "Technology Stack", monitoring: "Monitoring", governance: "Governance" };
            const themes: Record<string, Theme> = { security: T.security, platform: T.platform, monitoring: T.monitoring, governance: T.governance };
            return (
              <>
                <text x={MARGIN} y={techBlock.y - 14} fontSize={13} fontWeight={800} letterSpacing={1.5}
                  fill="#475569" fontFamily="Inter, -apple-system, sans-serif">TECHNOLOGY FOUNDATION</text>
                {lanes.map((l, i) => (
                  <Lane key={l.key} x={MARGIN + i * (laneW + colGap)} y={techBlock.y} width={laneW} height={techBlock.height}
                    title={titles[l.key]} theme={themes[l.key]} items={l.items} columns={1} />
                ))}
              </>
            );
          })()}

          {/* ── ROADMAP ── */}
          {roadmapBlock && (
            <RoadmapBand x={MARGIN} y={roadmapBlock.y} width={CONTENT_W} height={roadmapBlock.height} items={layout.data.roadmap} />
          )}

          {/* ── Stage connectors (narrative rail linking every visible block) ── */}
          {layout.blocks.map((b, i) => {
            if (i === 0) return null;
            const prev = layout.blocks[i - 1];
            return <StageConnector key={b.key} cx={width / 2} y1={prev.y + prev.height} y2={b.y} color={stageColor} />;
          })}

          {/* ── FOOTER ── */}
          <rect x={0} y={height - FOOTER_H} width={width} height={FOOTER_H} fill={T.footer.bg} />
          <text x={width / 2} y={height - FOOTER_H / 2 + 4} textAnchor="middle" fontSize={12} fontWeight={500}
            fill={T.footer.fg} fontFamily="Inter, -apple-system, sans-serif">
            ✓ Enterprise Architecture · AI-Generated · Production Ready
          </text>
        </svg>
      </div>
    </div>
  );
}
