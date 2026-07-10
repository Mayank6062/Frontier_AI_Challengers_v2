/**
 * ExecutiveArchitecturePoster — renders a horizontal-band infographic SVG
 * from the Architecture Agent's executive_poster JSON.
 *
 * Bands from top to bottom:
 *   Header → Business Objectives → Input Systems → Architecture Layers
 *   → Agent Flow → Cloud Services → Security → Monitoring → Outputs
 *   → Business Benefits → Technology Stack → Footer
 */
 
import { Download, Maximize2, Minimize2 } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
 
import { cn } from "@/utils/cn";
 
// ─── Types ──────────────────────────────────────────────────────────
 
export type PosterBand = {
  band: string;
  y: number;
  height: number;
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
 
// ─── Band color palette (semantic) ──────────────────────────────────
 
const BAND_PALETTE: Record<string, { bg: string; accent: string; fg: string }> = {
  Header:                 { bg: "#0F172A", accent: "#3B82F6", fg: "#FFFFFF" },
  "Business Objectives":  { bg: "#EFF6FF", accent: "#2563EB", fg: "#1E3A8A" },
  "Input Systems":        { bg: "#F1F5F9", accent: "#64748B", fg: "#0F172A" },
  "Architecture Layers":  { bg: "#F0FDF4", accent: "#16A34A", fg: "#14532D" },
  "Agent Flow":           { bg: "#FEF3C7", accent: "#F59E0B", fg: "#78350F" },
  "Cloud Services":       { bg: "#EEF2FF", accent: "#6366F1", fg: "#312E81" },
  Security:               { bg: "#FEE2E2", accent: "#DC2626", fg: "#7F1D1D" },
  Monitoring:             { bg: "#F5F3FF", accent: "#7C3AED", fg: "#4C1D95" },
  Outputs:                { bg: "#ECFDF5", accent: "#10B981", fg: "#064E3B" },
  "Business Benefits":    { bg: "#FEF9C3", accent: "#CA8A04", fg: "#713F12" },
  "Technology Stack":     { bg: "#F0F9FF", accent: "#0284C7", fg: "#0C4A6E" },
  Footer:                 { bg: "#0F172A", accent: "#64748B", fg: "#94A3B8" },
};
 
function paletteFor(band: PosterBand) {
  return (
    BAND_PALETTE[band.band] ?? {
      bg: band.background ?? "#F8FAFC",
      accent: "#2563EB",
      fg: band.text_color ?? "#0F172A",
    }
  );
}
 
// ─── Download helpers ───────────────────────────────────────────────
 
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
    const h = bbox.height || 1400;
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
 
// ─── Helpers ────────────────────────────────────────────────────────
 
function normalizeItem(item: unknown): { label: string; description?: string; color?: string } {
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
 
// Simple word-wrap for SVG text (in characters)
function wrapText(text: string, maxChars: number): string[] {
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
  return lines.slice(0, 3); // max 3 lines per item
}
 
// ─── Chip renderer ──────────────────────────────────────────────────
 
function BandItems({
  items,
  y,
  height,
  canvasWidth,
  palette,
}: {
  items: Array<{ label: string; description?: string; color?: string }>;
  y: number;
  height: number;
  canvasWidth: number;
  palette: { bg: string; accent: string; fg: string };
}) {
  if (items.length === 0) return null;
 
  const padding = 32;
  const gap = 16;
  const availableWidth = canvasWidth - padding * 2;
  const chipWidth = Math.max(120, Math.min(280, (availableWidth - gap * (items.length - 1)) / items.length));
  const chipHeight = Math.max(48, height - 40);
  const chipY = y + 20;
 
  return (
    <>
      {items.map((item, i) => {
        const chipX = padding + i * (chipWidth + gap);
        // Prevent overflow — if chips exceed canvas, wrap
        if (chipX + chipWidth > canvasWidth - padding) return null;
        const chipColor = item.color ?? palette.accent;
        const labelLines = wrapText(item.label, Math.floor(chipWidth / 8));
 
        return (
          <g key={i}>
            <rect
              x={chipX}
              y={chipY}
              width={chipWidth}
              height={chipHeight}
              rx={10}
              ry={10}
              fill="#FFFFFF"
              stroke={chipColor}
              strokeWidth={1.5}
              filter="drop-shadow(0 2px 4px rgba(15,23,42,0.06))"
            />
            {/* accent stripe */}
            <rect x={chipX} y={chipY} width={4} height={chipHeight} rx={10} ry={10} fill={chipColor} />
            {/* label */}
            <text
              x={chipX + 16}
              y={chipY + 26}
              fontSize={13}
              fontWeight={600}
              fill="#0F172A"
              fontFamily="Inter, system-ui, sans-serif"
            >
              {labelLines[0] ?? ""}
            </text>
            {labelLines[1] ? (
              <text
                x={chipX + 16}
                y={chipY + 42}
                fontSize={12}
                fontWeight={500}
                fill="#475569"
                fontFamily="Inter, system-ui, sans-serif"
              >
                {labelLines[1]}
              </text>
            ) : null}
          </g>
        );
      })}
    </>
  );
}
 
// ─── Public component ───────────────────────────────────────────────
 
type Props = {
  poster: ExecutivePoster;
  description?: string;
};
 
export function ExecutiveArchitecturePoster({ poster, description }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
 
  const width = poster?.canvas?.width ?? 2200;
  const height = poster?.canvas?.height ?? 1400;
  const sections = poster?.sections ?? [];
 
  const normalizedSections = useMemo(
    () =>
      sections.map((s) => ({
        ...s,
        items: (s.items ?? []).map(normalizeItem).filter((i) => i.label),
      })),
    [sections],
  );
 
  // ── Fullscreen ─────────────────────────────────────────────────
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
 
  // ── Downloads ──────────────────────────────────────────────────
  const downloadSVG = useCallback(() => {
    const svg = svgRef.current;
    if (!svg) return;
    const data = new XMLSerializer().serializeToString(svg);
    const blob = new Blob([data], { type: "image/svg+xml;charset=utf-8" });
    downloadBlob(blob, "executive_architecture_poster.svg");
  }, []);
 
  const downloadPNG = useCallback(async () => {
    const svg = svgRef.current;
    if (!svg) return;
    const blob = await svgToPngBlob(svg, 3);
    if (blob) downloadBlob(blob, "executive_architecture_poster.png");
  }, []);
 
  if (!poster || normalizedSections.length === 0) return null;
 
  return (
    <div
      ref={containerRef}
      className={cn(
        "rounded-xl border border-slate-200 bg-white shadow-sm transition-shadow hover:shadow-md",
        isFullscreen && "fixed inset-0 z-50 flex flex-col rounded-none border-0",
      )}
    >
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 bg-gradient-to-r from-indigo-50 to-blue-50 px-4 py-3">
        <div className="min-w-0 flex-1">
          <h4 className="truncate text-sm font-semibold text-slate-900">
            Executive Architecture Poster
          </h4>
          {description ? (
            <p className="mt-0.5 truncate text-xs text-slate-500">{description}</p>
          ) : null}
          <span className="mt-1 inline-block rounded bg-blue-100 px-1.5 py-0.5 text-[9px] font-semibold uppercase tracking-wider text-blue-700">
            Infographic
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={toggleFullscreen}
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
            className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-600 shadow-sm hover:bg-slate-50"
          >
            {isFullscreen ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
          </button>
          <button
            onClick={downloadSVG}
            title="Download SVG"
            className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-600 shadow-sm hover:bg-slate-50"
          >
            <Download className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={downloadPNG}
            title="Download PNG"
            className="inline-flex items-center gap-1 rounded-md border border-blue-200 bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 shadow-sm hover:bg-blue-100"
          >
            <Download className="h-3 w-3" /> PNG
          </button>
        </div>
      </div>
 
      {/* Viewport */}
      <div
        className={cn(
          "overflow-auto bg-slate-50/50 p-3",
          isFullscreen ? "flex-1" : "",
        )}
      >
        <svg
          ref={svgRef}
          viewBox={`0 0 ${width} ${height}`}
          width="100%"
          style={{ maxWidth: "100%", height: "auto", display: "block" }}
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Global page background */}
          <rect x={0} y={0} width={width} height={height} fill="#F8FAFC" />
 
          {normalizedSections.map((section, idx) => {
            const palette = paletteFor(section);
            const bg = section.background ?? palette.bg;
            const fg = section.text_color ?? palette.fg;
            const isHeader = section.band === "Header";
            const isFooter = section.band === "Footer";
 
            return (
              <g key={`${section.band}-${idx}`}>
                {/* Band background */}
                <rect x={0} y={section.y} width={width} height={section.height} fill={bg} />
 
                {/* Left accent bar (not for header/footer) */}
                {!isHeader && !isFooter && (
                  <rect
                    x={0}
                    y={section.y}
                    width={6}
                    height={section.height}
                    fill={palette.accent}
                  />
                )}
 
                {/* Band title */}
                {isHeader ? (
                  <>
                    <text
                      x={width / 2}
                      y={section.y + section.height / 2 - 4}
                      textAnchor="middle"
                      fontSize={30}
                      fontWeight={800}
                      fill={fg}
                      fontFamily="Inter, system-ui, sans-serif"
                    >
                      {section.title ?? poster.title ?? "Enterprise Solution Architecture"}
                    </text>
                    {(section.subtitle ?? poster.subtitle) && (
                      <text
                        x={width / 2}
                        y={section.y + section.height / 2 + 22}
                        textAnchor="middle"
                        fontSize={14}
                        fill="#CBD5E1"
                        fontFamily="Inter, system-ui, sans-serif"
                      >
                        {section.subtitle ?? poster.subtitle}
                      </text>
                    )}
                  </>
                ) : isFooter ? (
                  <text
                    x={width / 2}
                    y={section.y + section.height / 2 + 5}
                    textAnchor="middle"
                    fontSize={11}
                    fill={fg}
                    fontFamily="Inter, system-ui, sans-serif"
                  >
                    Generated by AI Architecture Assistant — Enterprise Edition
                  </text>
                ) : (
                  <text
                    x={32}
                    y={section.y + 18}
                    fontSize={12}
                    fontWeight={700}
                    fill={palette.accent}
                    fontFamily="Inter, system-ui, sans-serif"
                    style={{ letterSpacing: 1 }}
                  >
                    {(section.band ?? "").toUpperCase()}
                  </text>
                )}
 
                {/* Items */}
                {!isHeader && !isFooter && (
                  <BandItems
                    items={section.items ?? []}
                    y={section.y}
                    height={section.height}
                    canvasWidth={width}
                    palette={palette}
                  />
                )}
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
 
 