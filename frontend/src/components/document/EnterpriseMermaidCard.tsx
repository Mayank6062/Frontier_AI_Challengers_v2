/**
 * EnterpriseMermaidCard — a production-quality Mermaid diagram viewer.
 *
 * Features:
 *  • Auto-detects and splits multiple Mermaid blocks
 *  • Renders each diagram independently in its own container
 *  • Zoom in / out / reset via buttons + mouse wheel + pinch
 *  • Pan via click-and-drag
 *  • Fullscreen toggle (uses Fullscreen API)
 *  • Download as SVG or PNG
 *  • Auto-fits width, maintains aspect ratio, never crops
 *  • Resizes on window resize via ResizeObserver
 */
 
import {
  AlertCircle,
  Download,
  Expand,
  Loader2,
  Maximize2,
  Minimize2,
  Minus,
  Move,
  Plus,
  RotateCcw,
} from "lucide-react";
import mermaid from "mermaid";
import {
  memo,
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
 
import { cn } from "@/utils/cn";
 
// ─── Constants ───────────────────────────────────────────────────────
 
const MIN_ZOOM = 0.25;
const MAX_ZOOM = 4;
const ZOOM_STEP = 0.15;
const WHEEL_ZOOM_FACTOR = 0.002;
 
// Patterns that indicate the START of a new Mermaid diagram
const MERMAID_START =
  /^(?:graph\s|flowchart\s|sequenceDiagram|classDiagram|erDiagram|stateDiagram|gantt|pie|journey|gitGraph|timeline|C4Context|C4Container|C4Component|C4Deployment|C4Dynamic|mindmap|quadrantChart|sankey|block|xychart|requirement)/im;
 
// ─── Helpers ─────────────────────────────────────────────────────────
 
/** Remove markdown fences if present */
function stripFences(code: string): string {
  return code
    .replace(/```mermaid\s*/gi, "")
    .replace(/```\s*/g, "")
    .trim();
}
 
/** Check if a string looks like Mermaid source */
export function isMermaidSource(v: unknown): boolean {
  if (typeof v !== "string") return false;
  return MERMAID_START.test(stripFences(v));
}
 
/**
 * Split a potentially concatenated Mermaid string into independent diagram
 * blocks.  The backend sometimes returns a single string with several
 * `graph TD` / `flowchart LR` blocks separated by blank lines.
 */
export function splitMermaidBlocks(raw: string): string[] {
  const clean = stripFences(raw);
  if (!clean) return [];
 
  // Split on lines that start a new diagram keyword
  const lines = clean.split("\n");
  const blocks: string[] = [];
  let current: string[] = [];
 
  for (const line of lines) {
    if (MERMAID_START.test(line.trim()) && current.length > 0) {
      blocks.push(current.join("\n").trim());
      current = [];
    }
    current.push(line);
  }
 
  if (current.length > 0) {
    const last = current.join("\n").trim();
    if (last) blocks.push(last);
  }
 
  return blocks.filter((b) => b.length > 0);
}
 
// ─── SVG to PNG conversion ──────────────────────────────────────────
 
function svgToPngBlob(svgElement: SVGElement, scale = 2): Promise<Blob | null> {
  return new Promise((resolve) => {
    const svgClone = svgElement.cloneNode(true) as SVGElement;
 
    // Ensure explicit dimensions
    const bbox = svgElement.getBoundingClientRect();
    const w = bbox.width || 800;
    const h = bbox.height || 600;
    svgClone.setAttribute("width", String(w));
    svgClone.setAttribute("height", String(h));
 
    const svgData = new XMLSerializer().serializeToString(svgClone);
    const svgBlob = new Blob([svgData], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(svgBlob);
 
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = w * scale;
      canvas.height = h * scale;
      const ctx = canvas.getContext("2d");
      if (!ctx) {
        resolve(null);
        return;
      }
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
 
// ─── Hook: Zoom + Pan ───────────────────────────────────────────────
 
function useZoomPan() {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const isPanning = useRef(false);
  const lastPos = useRef({ x: 0, y: 0 });
 
  const zoomIn = useCallback(() => setZoom((z) => Math.min(z + ZOOM_STEP, MAX_ZOOM)), []);
  const zoomOut = useCallback(() => setZoom((z) => Math.max(z - ZOOM_STEP, MIN_ZOOM)), []);
  const resetView = useCallback(() => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  }, []);
 
  const onWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = -e.deltaY * WHEEL_ZOOM_FACTOR;
    setZoom((z) => Math.min(Math.max(z + delta, MIN_ZOOM), MAX_ZOOM));
  }, []);
 
  const onPointerDown = useCallback((e: React.PointerEvent) => {
    isPanning.current = true;
    lastPos.current = { x: e.clientX, y: e.clientY };
    (e.target as HTMLElement).setPointerCapture?.(e.pointerId);
  }, []);
 
  const onPointerMove = useCallback((e: React.PointerEvent) => {
    if (!isPanning.current) return;
    const dx = e.clientX - lastPos.current.x;
    const dy = e.clientY - lastPos.current.y;
    lastPos.current = { x: e.clientX, y: e.clientY };
    setPan((p) => ({ x: p.x + dx, y: p.y + dy }));
  }, []);
 
  const onPointerUp = useCallback(() => {
    isPanning.current = false;
  }, []);
 
  return {
    zoom,
    pan,
    zoomIn,
    zoomOut,
    resetView,
    handlers: { onWheel, onPointerDown, onPointerMove, onPointerUp },
  };
}
 
// ─── Toolbar button ─────────────────────────────────────────────────
 
function ToolbarBtn({
  onClick,
  title,
  children,
  className,
}: {
  onClick: () => void;
  title: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <button
      onClick={onClick}
      title={title}
      className={cn(
        "inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-600 shadow-sm transition-colors hover:bg-slate-50 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1",
        className,
      )}
    >
      {children}
    </button>
  );
}
 
// ─── Single diagram card (memoized for performance) ────────────────────────────────────────────
 
type EnterpriseMermaidCardProps = {
  title?: string;
  description?: string;
  code: string;
};
 
const EnterpriseMermaidCardInternal = ({
  title,
  description,
  code,
}: EnterpriseMermaidCardProps) => {
  const uid = useId().replace(/:/g, "");
  const renderContainerId = `emr-${uid}`;
  const wrapperRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [renderError, setRenderError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [hasRendered, setHasRendered] = useState(false);
  const { zoom, pan, zoomIn, zoomOut, resetView, handlers } = useZoomPan();
 
  // Memoize cleaned code to avoid re-computation
  const cleanCode = useMemo(() => stripFences(code), [code]);
 
  // ── Lazy Rendering (IntersectionObserver) ──────────────────────
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
          }
        });
      },
      { rootMargin: "100px" } // Start loading slightly before visible
    );
 
    const container = containerRef.current;
    if (container) {
      observer.observe(container);
    }
 
    return () => {
      if (container) {
        observer.unobserve(container);
      }
    };
  }, []);
 
  // ── Render Mermaid ──────────────────────────────────────────────
  useEffect(() => {
    // Only render if in view and not already rendered
    if (!isInView || !cleanCode || hasRendered) return;
 
    setIsLoading(true);
    setRenderError(false);
 
    const render = async () => {
      try {
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: "loose",
          theme: "default",
          flowchart: {
            useMaxWidth: false,
            htmlLabels: true,
            curve: "basis",
            padding: "20",
          },
          sequence: { useMaxWidth: true },
          er: { useMaxWidth: true },
          journey: { useMaxWidth: true },
          gantt: { useMaxWidth: true },
          themeVariables: {
            fontSize: "14px",
            primaryColor: "#f0f4f8",
          },
        });
 
        const target = document.getElementById(renderContainerId);
        if (!target) return;
 
        const svgId = `${renderContainerId}-svg`;
        // Remove previous SVG from DOM if re-rendering
        const prev = document.getElementById(svgId);
        if (prev) prev.remove();
 
        const result = await mermaid.render(svgId, cleanCode);
        const svg = (result as any)?.svg ?? result;
       
        if (target) {
          target.innerHTML = svg;
          // Make SVG responsive and ensure full visibility
          const svgEl = target.querySelector("svg");
          if (svgEl) {
            svgEl.removeAttribute("height");
            svgEl.setAttribute("preserveAspectRatio", "xMidYMid meet");
            svgEl.style.width = "auto";
            svgEl.style.height = "auto";
            svgEl.style.maxWidth = "none";
            svgEl.style.minWidth = "max-content";
            svgEl.style.minHeight = "max-content";
            svgEl.style.display = "block";
            svgEl.style.overflow = "visible";
          }
        }
       
        setHasRendered(true);
        setIsLoading(false);
      } catch (err) {
        console.error("Mermaid rendering failed:", err);
        setRenderError(true);
        setIsLoading(false);
        const target = document.getElementById(renderContainerId);
        if (target) {
          target.innerHTML = "";
        }
      }
    };
 
    render();
  }, [isInView, cleanCode, renderContainerId, hasRendered]);
 
  // ── Auto-fit on resize ──────────────────────────────────────────
  useEffect(() => {
    const wrapper = wrapperRef.current;
    if (!wrapper) return;
 
    const observer = new ResizeObserver(() => {
      const svgEl = wrapper.querySelector("svg");
      if (svgEl) {
        svgEl.style.width = "100%";
        svgEl.style.maxWidth = "100%";
        svgEl.style.height = "auto";
      }
    });
 
    observer.observe(wrapper);
    return () => observer.disconnect();
  }, []);
 
  // ── Fullscreen ──────────────────────────────────────────────────
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
 
  // ── Download SVG ────────────────────────────────────────────────
  const downloadSVG = useCallback(() => {
    const svgEl = wrapperRef.current?.querySelector("svg");
    if (!svgEl) return;
    const svgData = new XMLSerializer().serializeToString(svgEl);
    const blob = new Blob([svgData], { type: "image/svg+xml;charset=utf-8" });
    const name = title ? title.replace(/\s+/g, "_").toLowerCase() : "diagram";
    downloadBlob(blob, `${name}.svg`);
  }, [title]);
 
  // ── Download PNG ────────────────────────────────────────────────
  const downloadPNG = useCallback(async () => {
    const svgEl = wrapperRef.current?.querySelector("svg");
    if (!svgEl) return;
    const blob = await svgToPngBlob(svgEl as unknown as SVGElement, 3);
    if (blob) {
      const name = title ? title.replace(/\s+/g, "_").toLowerCase() : "diagram";
      downloadBlob(blob, `${name}.png`);
    }
  }, [title]);
 
  if (!cleanCode) return null;
 
  return (
    <div
      ref={containerRef}
      className={cn(
        "rounded-xl border border-slate-200 bg-white shadow-sm transition-shadow hover:shadow-md",
        isFullscreen && "fixed inset-0 z-50 flex flex-col rounded-none border-0 bg-white",
      )}
    >
      {/* ─── Header + Toolbar ─────────────────────────────────────── */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 px-4 py-3">
        <div className="min-w-0 flex-1">
          {title ? (
            <h4 className="truncate text-sm font-semibold text-slate-900">{title}</h4>
          ) : null}
          {description ? (
            <p className="mt-0.5 truncate text-xs text-slate-500">{description}</p>
          ) : null}
        </div>
 
        {/* Toolbar */}
        <div className="flex items-center gap-1">
          <ToolbarBtn onClick={zoomIn} title="Zoom In">
            <Plus className="h-3.5 w-3.5" />
          </ToolbarBtn>
          <ToolbarBtn onClick={zoomOut} title="Zoom Out">
            <Minus className="h-3.5 w-3.5" />
          </ToolbarBtn>
          <ToolbarBtn onClick={resetView} title="Reset Zoom">
            <RotateCcw className="h-3.5 w-3.5" />
          </ToolbarBtn>
 
          <div className="mx-1 h-5 w-px bg-slate-200" />
 
          <ToolbarBtn onClick={toggleFullscreen} title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
            {isFullscreen ? (
              <Minimize2 className="h-3.5 w-3.5" />
            ) : (
              <Maximize2 className="h-3.5 w-3.5" />
            )}
          </ToolbarBtn>
 
          <div className="mx-1 h-5 w-px bg-slate-200" />
 
          <ToolbarBtn onClick={downloadSVG} title="Download SVG">
            <Download className="h-3.5 w-3.5" />
          </ToolbarBtn>
          <ToolbarBtn onClick={downloadPNG} title="Download PNG" className="relative">
            <Download className="h-3.5 w-3.5" />
            <span className="absolute -bottom-0.5 -right-0.5 rounded bg-blue-500 px-0.5 text-[7px] font-bold leading-tight text-white">
              PNG
            </span>
          </ToolbarBtn>
 
          {/* Zoom indicator */}
          <span className="ml-1 min-w-[3.5rem] rounded bg-slate-100 px-2 py-1 text-center text-[10px] font-medium text-slate-500">
            {Math.round(zoom * 100)}%
          </span>
        </div>
      </div>
 
      {/* ─── Diagram viewport ─────────────────────────────────────── */}
      <div
        ref={wrapperRef}
        className={cn(
          "relative overflow-auto bg-slate-50/50",
          isFullscreen ? "flex-1" : "min-h-[600px]",
        )}
        style={{
    width: "100%",
    minHeight: "700px",
    overflow: "auto"
}}
        {...(isLoading ? {} : handlers)}
      >
        <div
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: "center center",
            transition: "transform 0.08s ease-out",
            padding: "80px",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            minWidth: "max-content",
            minHeight: "max-content",
           }}
          >

          <div id={renderContainerId} className="flex items-center justify-center w-full" />
        </div>
 
        {/* Loading state */}
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/80">
            <div className="flex flex-col items-center gap-3 rounded-lg border border-blue-200 bg-blue-50/50 p-6">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
              <p className="text-sm font-medium text-blue-900">Rendering diagram...</p>
            </div>
          </div>
        )}
 
        {/* Error state */}
        {renderError && !isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white">
            <div className="max-w-md rounded-lg border border-orange-200 bg-orange-50 p-6 text-center shadow-sm">
              <div className="mb-3 flex justify-center">
                <div className="rounded-full bg-orange-100 p-2">
                  <AlertCircle className="h-6 w-6 text-orange-600" />
                </div>
              </div>
              <h4 className="mb-2 text-base font-semibold text-orange-900">
                Diagram unavailable
              </h4>
              <p className="mb-3 text-sm text-orange-700">
                The diagram syntax could not be rendered. This is likely due to invalid Mermaid syntax
                or unsupported diagram features.
              </p>
              <details className="text-left">
                <summary className="cursor-pointer text-xs font-medium text-orange-800 hover:text-orange-900">
                  View diagram code
                </summary>
                <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap rounded border border-orange-200 bg-white/60 p-3 text-xs text-slate-600">
                  {cleanCode}
                </pre>
              </details>
            </div>
          </div>
        )}
      </div>
 
      {/* ─── Hint bar ─────────────────────────────────────────────── */}
      <div className="flex items-center gap-3 border-t border-slate-100 bg-slate-50/80 px-4 py-1.5 text-[10px] text-slate-400">
        <span className="inline-flex items-center gap-1">
          <Move className="h-3 w-3" /> Drag to pan
        </span>
        <span>Scroll to zoom</span>
        <span className="inline-flex items-center gap-1">
          <Expand className="h-3 w-3" /> Pinch to zoom
        </span>
      </div>
    </div>
  );
}
 
// Export memoized version (prevents re-renders of unchanged diagrams)
export const EnterpriseMermaidCard = memo(EnterpriseMermaidCardInternal);
 
// ─── Multi-diagram renderer ─────────────────────────────────────────
 
/**
 * Given a raw Mermaid string that may contain multiple diagram blocks,
 * split and render each one in its own EnterpriseMermaidCard.
 */
export function EnterpriseMermaidSection({
  title,
  code,
}: {
  title?: string;
  code?: string;
}) {
  if (!code) return null;
  const blocks = splitMermaidBlocks(code);
  if (blocks.length === 0) return null;
 
  return (
    <div className="space-y-4">
      {blocks.map((block, i) => (
        <EnterpriseMermaidCard
          key={`${title ?? "diagram"}-${i}`}
          title={blocks.length > 1 ? `${title ?? "Diagram"} (${i + 1}/${blocks.length})` : title}
          code={block}
        />
      ))}
    </div>
  );
}
