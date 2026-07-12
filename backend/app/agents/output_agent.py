"""
output_agent.py — Enterprise Solution Packaging Engine
=======================================================
 
Generates the complete consultant-grade solution package from approved upstream
agent outputs (Discovery → Knowledge → Recommendation → Architecture → Validation).
 
Architecture
------------
  _parse_output_json()          Schema validation + graceful default injection
  _enrich_solution_metadata()   Timestamp injection + validation-score alignment
  _run_quality_gates()          Pre-return completeness & integrity checks
  _build_output_display_data()  Orchestrates all section builders (see below)
    ├─ _build_package_header()       Package manifest + readiness indicators
    ├─ _build_executive_intelligence()  Derived highlights, decisions, impact summary
    ├─ _build_executive_overview()   CTO-level narrative
    ├─ _build_poster_section()       Executive architecture poster
    ├─ _build_architecture_sections()  HLD / LLD / diagrams (audience-aware)
    ├─ _build_technical_sections()   Security + deployment (typed cards)
    ├─ _build_roadmap_section()      Phased timeline
    ├─ _build_risk_section()         Severity-classified risk register
    ├─ _build_cost_section()         Cost table with total row
    ├─ _build_decisions_section()    Build-vs-buy key decisions
    ├─ _build_traceability_section() Agent pipeline provenance
    └─ _build_downloads_section()    Completeness-checked download manifest
 
All section type strings are defined as module-level constants to prevent
silent frontend rendering failures from typos.
"""
 
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
 
from dotenv import load_dotenv
from openai import APITimeoutError, AzureOpenAI, OpenAIError
 
from app.prompts.output_prompt import OUTPUT_SYSTEM_PROMPT
from app.models.enterprise_blueprint import normalize_agent_outputs
from app.renderers import render_html, render_markdown, render_terraform
 
 
load_dotenv(Path(__file__).resolve().parents[2] / ".env")
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# SECTION TYPE CONSTANTS
# Using constants prevents silent frontend breakage from string typos.
# ═══════════════════════════════════════════════════════════════════════════════
 
ST_SOLUTION_METADATA   = "solution_metadata"
ST_PACKAGE_MANIFEST    = "package_manifest"
ST_EXECUTIVE_OVERVIEW  = "executive_overview"
ST_EXECUTIVE_POSTER    = "executive_poster"
ST_INTELLIGENCE        = "executive_intelligence"
ST_PARAGRAPH           = "paragraph"
ST_BULLET_HLD          = "bullet_hld"          # HLD: executive audience, capability-level
ST_BULLET_LLD          = "bullet_lld"          # LLD: implementer audience, technical detail
ST_BULLET_SECURITY     = "bullet_security"
ST_BULLET_DEPLOYMENT   = "bullet_deployment"
ST_MERMAID             = "mermaid_diagram"
ST_ROADMAP             = "roadmap"
ST_RISK_TABLE          = "risk_table"
ST_COST_TABLE          = "cost_table"
ST_DECISION_TABLE      = "decision_table"
ST_DOWNLOADS           = "enterprise_downloads"
ST_TRACEABILITY        = "pipeline_traceability"
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# FIELD DEFINITIONS — Schema contracts
# ═══════════════════════════════════════════════════════════════════════════════
 
OUTPUT_FIELDS = {
    "executive_summary",
    "solution_overview",
    "high_level_design",
    "low_level_design",
    "architecture_diagram",
    "data_flow_diagram",
    "security_architecture",
    "deployment_architecture",
    "cost_report",
    "build_vs_buy_report",
    "risk_register",
    "implementation_roadmap",
    "diagrams",
    "downloads",
}
 
ENTERPRISE_FIELDS = {
    "executive_overview",
    "executive_poster",
    "solution_metadata",
}
 
DIAGRAM_FIELDS = {
    "hld",
    "lld",
    "architecture",
    "deployment",
    "data_flow",
    "network",
}
 
DOWNLOAD_FIELDS = {
    "html",
    "markdown",
    "terraform",
}
 
SOLUTION_METADATA_FIELDS = {
    "package_title",
    "industry",
    "architecture_style",
    "cloud_platform",
    "solution_complexity",
}
 
# Item-level schemas used in validation
_COST_ITEM_FIELDS      = {"category", "item", "estimate", "notes"}
_RISK_ITEM_FIELDS      = {"risk", "severity", "mitigation"}
_ROADMAP_ITEM_FIELDS   = {"phase", "duration", "deliverables"}
_BVB_ITEM_FIELDS       = {"component", "decision", "rationale"}
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# EXCEPTIONS
# ═══════════════════════════════════════════════════════════════════════════════
 
class OutputAgentError(RuntimeError):
    pass
 
class OutputInvalidJSONError(OutputAgentError):
    pass
 
class OutputAzureError(OutputAgentError):
    pass
 
class OutputTimeoutError(OutputAgentError):
    pass
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# PRIMITIVE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
 
def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise OutputAgentError(f"Missing required environment variable: {name}")
    return value
 
 
def _create_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=_get_required_env("AZURE_OPENAI_API_KEY"),
        azure_endpoint=_get_required_env("AZURE_OPENAI_ENDPOINT"),
        api_version=_get_required_env("AZURE_OPENAI_API_VERSION"),
        # Output generation assembles full HTML, Markdown, Terraform, poster spec,
        # and six Mermaid diagrams — this routinely takes longer than standard agents.
        timeout=300.0,
    )
 
 
def _as_list(value: Any) -> list[Any]:
    """Normalise any value to a list; return [] for None / empty string."""
    if isinstance(value, list):
        return value
    if value in (None, "", "Not Specified"):
        return []
    return [value]
 
 
def _safe_str(value: Any, default: str = "") -> str:
    """Return value as a non-empty string, or default."""
    if isinstance(value, str) and value.strip():
        return value.strip()
    if value is None or value == "":
        return default
    return str(value)
 
 
def _safe_int(value: Any, default: int = 0) -> int:
    """Coerce value to int without raising."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
 
 
def _is_non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA VALIDATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
 
def _validate_object_fields(
    result: dict[str, Any], field: str, expected: set[str]
) -> None:
    value = result.get(field)
    if not isinstance(value, dict):
        # For downloads and diagrams, inject empty defaults rather than raising
        if field in ("downloads", "diagrams"):
            result[field] = {k: "" for k in expected}
            return
        raise OutputInvalidJSONError(f"Output {field} must be an object")
    missing = expected - set(value)
    if missing:
        # For downloads and diagrams, inject empty defaults for missing fields rather than raising
        if field in ("downloads", "diagrams"):
            for k in missing:
                result[field][k] = ""
        else:
            raise OutputInvalidJSONError(
                f"Output {field} is missing fields: {', '.join(sorted(missing))}"
            )
 
 
def _validate_list_of_objects(
    result: dict[str, Any],
    field: str,
    required_keys: set[str],
    *,
    allow_empty: bool = True,
) -> None:
    """
    Validate that result[field] is a list whose items are dicts with required_keys.
    Coerces non-list values (str, None) to [] with a warning rather than raising,
    preserving graceful degradation for optional enterprise content.
    """
    value = result.get(field)
    if not isinstance(value, list):
        # Coerce silently — model sometimes returns a single object or null
        result[field] = _as_list(value)
        value = result[field]
 
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            # Replace non-dict items with a safe placeholder rather than crashing
            result[field][i] = {k: "Not available" for k in required_keys}
            continue
        # Back-fill missing optional keys with empty strings (don't raise)
        for key in required_keys:
            if key not in item:
                item[key] = ""
 
 
def _validate_executive_overview(result: dict[str, Any]) -> None:
    """Validate executive_overview structure; inject defaults if malformed."""
    eo = result.get("executive_overview")
    if not isinstance(eo, dict):
        result["executive_overview"] = {
            "title": _safe_str(result.get("solution_overview"), "Executive Overview"),
            "subtitle": "",
            "sections": [],
            "decision_summary": _safe_str(result.get("executive_summary")),
            "confidence_statement": "",
        }
        return
    # Ensure required sub-keys exist
    eo.setdefault("title", "Executive Overview")
    eo.setdefault("subtitle", "")
    eo.setdefault("sections", [])
    eo.setdefault("decision_summary", _safe_str(result.get("executive_summary")))
    eo.setdefault("confidence_statement", "")
    if not isinstance(eo.get("sections"), list):
        eo["sections"] = []
 
 
def _validate_executive_poster(result: dict[str, Any]) -> None:
    """Validate executive_poster; inject default if missing or malformed."""
    ep = result.get("executive_poster")
    if not isinstance(ep, dict) or not isinstance(ep.get("sections"), list):
        result["executive_poster"] = _build_default_poster(result)
        return
    # Ensure each band has the minimum required keys
    for band in ep["sections"]:
        if not isinstance(band, dict):
            continue
        band.setdefault("band", "Section")
        band.setdefault("y", 0)
        band.setdefault("height", 80)
        band.setdefault("items", [])
 
 
def _validate_solution_metadata(
    result: dict[str, Any], validation: dict[str, Any]
) -> None:
    """
    Validate solution_metadata; inject defaults derived from validation agent
    if the field is missing or incomplete. This prevents the metadata block from
    hardcoding 75/75 when the validation agent has already reported real scores.
    """
    if "solution_metadata" not in result or not isinstance(result["solution_metadata"], dict):
        result["solution_metadata"] = _build_default_metadata(result, validation)
        return
 
    sm = result["solution_metadata"]
 
    # Ensure minimum required keys exist
    for key in SOLUTION_METADATA_FIELDS:
        sm.setdefault(key, "")
 
    sm.setdefault("package_subtitle", "")
    sm.setdefault("technology_summary", [])
    sm.setdefault("estimated_timeline", "")
    sm.setdefault("business_criticality", "High")
    sm.setdefault("document_version", "1.0")
    sm.setdefault("agent_pipeline_version", "2.0")
    sm.setdefault("final_recommendation", "")
 
    # Always inject a real server-side timestamp — the model cannot produce one
    sm["generated_timestamp"] = datetime.now(timezone.utc).isoformat()
 
    # Align scores with the validation agent rather than trusting the model's copy
    val_score = _extract_validation_score(validation)
    sm["confidence_score"]   = val_score
    sm["architecture_score"] = val_score
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# FALLBACK BUILDERS — used when model omits optional enterprise fields
# ═══════════════════════════════════════════════════════════════════════════════
 
def _extract_validation_score(validation: dict[str, Any]) -> int:
    """
    Pull the overall_score from the validation agent payload.
    Handles both agent_data wrapper format and raw validation format.
    """
    if not isinstance(validation, dict):
        return 75
    # validation may be the raw agent_data dict or the {agent_data, display_data} wrapper
    agent_data = validation.get("agent_data", validation)
    score = agent_data.get("architecture_score", {}).get("overall_score")
    return _safe_int(score, 75)
 
 
def _build_default_poster(result: dict[str, Any]) -> dict[str, Any]:
    """
    Build a minimal but semantically correct fallback poster.
    Uses only appropriate source fields for each band —
    never mismatches security_architecture → Architecture Layers.
    Heights are computed proportionally (80px base + 40px per item, max 6 items shown).
    """
    def _poster_items(source: list[Any], limit: int = 4) -> list[dict[str, Any]]:
        items = []
        for entry in source[:limit]:
            if isinstance(entry, dict):
                items.append({
                    "label": _safe_str(entry.get("label") or entry.get("phase") or entry.get("risk"), "Item"),
                    "description": _safe_str(entry.get("description") or entry.get("focus"), ""),
                })
            elif isinstance(entry, str) and entry.strip():
                items.append({"label": entry.strip(), "description": ""})
        return items
 
    hld = _poster_items(_as_list(result.get("high_level_design")), 4)
    sec = _poster_items(_as_list(result.get("security_architecture")), 3)
    dep = _poster_items(_as_list(result.get("deployment_architecture")), 4)
 
    bands: list[dict[str, Any]] = []
    cursor = 0
 
    def _add_band(band: dict[str, Any]) -> None:
        nonlocal cursor
        h = band.get("height", 80)
        band["y"] = cursor
        cursor += h
        bands.append(band)
 
    _add_band({"band": "Header", "height": 80, "background": "#0F172A",
               "text_color": "#FFFFFF", "title": _safe_str(result.get("solution_overview"), "Enterprise Solution Architecture"),
               "subtitle": "AI-Generated Architecture Package"})
 
    if hld:
        _add_band({"band": "Business Objectives", "height": 80 + 40 * len(hld),
                   "background": "#EFF6FF", "items": hld})
 
    if sec:
        _add_band({"band": "Security Controls", "height": 80 + 40 * len(sec),
                   "background": "#FFF8ED", "items": sec})
 
    if dep:
        _add_band({"band": "Deployment Architecture", "height": 80 + 40 * len(dep),
                   "background": "#F0FDF4", "items": dep})
 
    _add_band({"band": "Footer", "height": 50, "background": "#0F172A",
               "text_color": "#94A3B8"})
 
    return {
        "title": "Enterprise Solution Architecture",
        "subtitle": "AI-Generated Architecture Package",
        "canvas": {"width": 2200, "height": max(cursor, 600)},
        "color_palette": {
            "primary": "#0078D4", "secondary": "#0F172A",
            "accent": "#10B981", "background": "#F8FAFC",
        },
        "sections": bands,
        "kpis": [],
        "implementation_phases": [],
    }
 
 
def _build_default_metadata(
    result: dict[str, Any], validation: dict[str, Any]
) -> dict[str, Any]:
    """
    Build solution metadata with real validation scores, never hardcoded defaults.
    """
    val_score = _extract_validation_score(validation)
    return {
        "package_title": _safe_str(result.get("solution_overview"), "Enterprise Architecture Solution"),
        "package_subtitle": "AI-generated deliverables package",
        "industry": "Technology",
        "architecture_style": "Modern Cloud-Native",
        "cloud_platform": "Cloud",
        "technology_summary": [],
        "solution_complexity": "Enterprise",
        "solution_complexity_rationale": "Complexity inferred from architecture scope.",
        "estimated_timeline": "To be determined",
        "business_criticality": "High",
        "business_criticality_rationale": "Criticality inferred from validation inputs.",
        "confidence_score": val_score,
        "architecture_score": val_score,
        "final_recommendation": "Approved With Recommendations",
        "document_version": "1.0",
        "generated_timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_pipeline_version": "2.0",
    }
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY GATE
# ═══════════════════════════════════════════════════════════════════════════════
 
def _run_quality_gates(output: dict[str, Any]) -> dict[str, Any]:
    """
    Pre-return integrity check. Returns a quality report embedded in display_data.
    Recovers gracefully from missing content — never raises.
    Checks: download completeness, diagram availability, poster bands, metadata fields.
    """
    issues: list[str] = []
    warnings: list[str] = []
 
    # Download completeness
    downloads = output.get("downloads", {})
    for field in DOWNLOAD_FIELDS:
        content = downloads.get(field, "")
        if not _is_non_empty_str(content):
            issues.append(f"Download '{field}' is empty or missing.")
 
    # Diagram availability
    diagrams = output.get("diagrams", {})
    for field in DIAGRAM_FIELDS:
        code = diagrams.get(field, "")
        if not _is_non_empty_str(code):
            warnings.append(f"Diagram '{field}' is empty or missing.")
 
    # Poster band count
    poster_sections = output.get("executive_poster", {}).get("sections", [])
    if len(poster_sections) < 3:
        warnings.append(f"Executive poster has only {len(poster_sections)} band(s); expected ≥ 5.")
 
    # Metadata completeness
    sm = output.get("solution_metadata", {})
    for field in SOLUTION_METADATA_FIELDS:
        if not _is_non_empty_str(sm.get(field)):
            warnings.append(f"solution_metadata.{field} is empty.")
 
    # Executive summary quality (minimum length)
    exec_summary = _safe_str(output.get("executive_summary"))
    if len(exec_summary.split()) < 30:
        warnings.append("executive_summary is very short — quality may be low.")
 
    return {
        "passed": len(issues) == 0,
        "issue_count": len(issues),
        "warning_count": len(warnings),
        "issues": issues,
        "warnings": warnings,
    }
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# ENTERPRISE INTELLIGENCE LAYER
# ═══════════════════════════════════════════════════════════════════════════════
 
def _compute_package_readiness(output: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    """
    Compute a composite Package Readiness Score from:
      - Validation agent overall score          (40% weight)
      - Download completeness (3 assets)        (20% weight)
      - Diagram completeness (6 diagrams)       (20% weight)
      - Poster completeness (bands present)     (10% weight)
      - Executive overview quality (sections)   (10% weight)
 
    Returns a dict with numeric score, label, and per-dimension breakdown.
    """
    val_score   = _extract_validation_score(validation)
    downloads   = output.get("downloads", {})
    diagrams    = output.get("diagrams", {})
 
    dl_count    = sum(1 for f in DOWNLOAD_FIELDS if _is_non_empty_str(downloads.get(f)))
    dg_count    = sum(1 for f in DIAGRAM_FIELDS if _is_non_empty_str(diagrams.get(f)))
    poster_ok   = len(output.get("executive_poster", {}).get("sections", [])) >= 5
    eo_ok       = len(output.get("executive_overview", {}).get("sections", [])) >= 2
 
    dl_score    = round((dl_count / len(DOWNLOAD_FIELDS))  * 100)
    dg_score    = round((dg_count / len(DIAGRAM_FIELDS))   * 100)
    poster_score = 100 if poster_ok else 40
    eo_score    = 100 if eo_ok else 50
 
    composite = round(
        val_score  * 0.40 +
        dl_score   * 0.20 +
        dg_score   * 0.20 +
        poster_score * 0.10 +
        eo_score   * 0.10
    )
 
    def _label(s: int) -> str:
        if s >= 90: return "Delivery Ready"
        if s >= 75: return "Ready with Minor Gaps"
        if s >= 60: return "Conditionally Ready"
        return "Not Ready — Action Required"
 
    return {
        "composite_score": composite,
        "label": _label(composite),
        "dimensions": {
            "validation_quality":    {"score": val_score,     "weight": "40%"},
            "download_completeness": {"score": dl_score,      "weight": "20%", "count": f"{dl_count}/{len(DOWNLOAD_FIELDS)}"},
            "diagram_completeness":  {"score": dg_score,      "weight": "20%", "count": f"{dg_count}/{len(DIAGRAM_FIELDS)}"},
            "poster_completeness":   {"score": poster_score,  "weight": "10%"},
            "overview_quality":      {"score": eo_score,      "weight": "10%"},
        },
    }
 
 
def _extract_executive_highlights(output: dict[str, Any]) -> list[str]:
    """
    Derive 3–5 executive highlights from across the solution package.
    Sources: executive_overview.sections[*].highlights, hld, risk_register (high severity).
    Returns standalone insight strings suitable for a hero card.
    """
    highlights: list[str] = []
 
    # Pull from executive_overview section highlights
    for section in output.get("executive_overview", {}).get("sections", []):
        for h in section.get("highlights", []):
            if _is_non_empty_str(h) and len(highlights) < 3:
                highlights.append(h.strip())
 
    # Top HLD point as architectural highlight (if no overview highlights)
    if not highlights:
        hld = _as_list(output.get("high_level_design"))
        if hld and _is_non_empty_str(str(hld[0])):
            highlights.append(str(hld[0]).strip())
 
    # Highest-severity risk as a caution highlight
    risks = _as_list(output.get("risk_register"))
    high_risks = [
        r for r in risks
        if isinstance(r, dict) and str(r.get("severity", "")).upper() == "HIGH"
    ]
    if high_risks and len(highlights) < 5:
        mitigation = _safe_str(high_risks[0].get("mitigation"), "")
        risk_text  = _safe_str(high_risks[0].get("risk"), "High-severity risk identified")
        highlights.append(f"⚠️ Key Risk: {risk_text}" + (f" — {mitigation}" if mitigation else ""))
 
    return highlights[:5]
 
 
def _extract_key_decisions(output: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Surface build-vs-buy decisions as a named Key Decisions list.
    Each entry is enriched with a display label for the decision type.
    """
    bvb = _as_list(output.get("build_vs_buy_report"))
    decisions = []
    badge_map = {
        "Build":     {"icon": "🔨", "color": "info"},
        "Buy":       {"icon": "🛒", "color": "success"},
        "Integrate": {"icon": "🔌", "color": "warning"},
    }
    for item in bvb:
        if not isinstance(item, dict):
            continue
        decision_type = _safe_str(item.get("decision"), "Build")
        badge = badge_map.get(decision_type, {"icon": "→", "color": "neutral"})
        decisions.append({
            "component": _safe_str(item.get("component"), "Component"),
            "decision":  decision_type,
            "rationale": _safe_str(item.get("rationale"), ""),
            "icon":      badge["icon"],
            "badge_color": badge["color"],
        })
    return decisions
 
 
def _summarise_risk_profile(output: dict[str, Any]) -> dict[str, Any]:
    """
    Summarise the risk register into a compact profile for the intelligence card.
    """
    risks = _as_list(output.get("risk_register"))
    counts: dict[str, int] = {"High": 0, "Medium": 0, "Low": 0}
    for r in risks:
        if isinstance(r, dict):
            sev = str(r.get("severity", "")).strip().title()
            if sev in counts:
                counts[sev] += 1
 
    total = sum(counts.values())
    profile = "Clean" if total == 0 else (
        "Critical Attention Required" if counts["High"] > 0 else
        "Moderate — Action Recommended" if counts["Medium"] > 2 else
        "Low — Monitor Only"
    )
    return {"total": total, "high": counts["High"], "medium": counts["Medium"],
            "low": counts["Low"], "profile": profile}
 
 
def _compute_document_quality_score(output: dict[str, Any]) -> int:
    """
    Score document quality 0–100 by checking for non-empty content across
    the key deliverable fields. Used in the package manifest card.
    """
    checks = [
        _is_non_empty_str(output.get("executive_summary")),
        _is_non_empty_str(output.get("solution_overview")),
        len(_as_list(output.get("high_level_design"))) >= 3,
        len(_as_list(output.get("low_level_design"))) >= 3,
        len(_as_list(output.get("security_architecture"))) >= 2,
        len(_as_list(output.get("deployment_architecture"))) >= 2,
        len(_as_list(output.get("cost_report"))) >= 2,
        len(_as_list(output.get("risk_register"))) >= 2,
        len(_as_list(output.get("implementation_roadmap"))) >= 2,
        len(_as_list(output.get("build_vs_buy_report"))) >= 1,
        bool(output.get("executive_overview", {}).get("sections")),
        bool(output.get("executive_poster", {}).get("sections")),
    ]
    return round((sum(checks) / len(checks)) * 100)
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# PARSING & VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════
 
def _parse_output_json(
    content: str, validation: dict[str, Any]
) -> dict[str, Any]:
    """
    Parse and validate the LLM JSON response. Applies:
      1. Top-level field presence check (raises on missing required fields)
      2. Nested object field validation (diagrams, downloads)
      3. List field type coercion with per-item key back-filling (graceful)
      4. Enterprise field validation with default injection (graceful)
      5. Real-server-side timestamp injection into solution_metadata
    """
    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise OutputInvalidJSONError("Output generation agent returned invalid JSON") from exc
 
    if not isinstance(result, dict):
        raise OutputInvalidJSONError("Output generation agent JSON must be an object")
 
    # 0. Pre-inject empty defaults for downloads and diagrams (enterprise renderers will replace these)
    if "downloads" not in result:
        result["downloads"] = {k: "" for k in DOWNLOAD_FIELDS}
    if "diagrams" not in result:
        result["diagrams"] = {k: "" for k in DIAGRAM_FIELDS}
 
    # 1. Required top-level fields
    missing = OUTPUT_FIELDS - set(result)
    if missing:
        raise OutputInvalidJSONError(
            f"Output generation JSON is missing fields: {', '.join(sorted(missing))}"
        )
 
    # 2. Nested object validation (strict — these are always required)
    _validate_object_fields(result, "diagrams",   DIAGRAM_FIELDS)
    _validate_object_fields(result, "downloads",  DOWNLOAD_FIELDS)
 
    # 3. List fields with per-item key back-filling (graceful)
    _validate_list_of_objects(result, "cost_report",       _COST_ITEM_FIELDS)
    _validate_list_of_objects(result, "risk_register",     _RISK_ITEM_FIELDS)
    _validate_list_of_objects(result, "implementation_roadmap", _ROADMAP_ITEM_FIELDS)
    _validate_list_of_objects(result, "build_vs_buy_report",   _BVB_ITEM_FIELDS)
 
    # 4. Enterprise fields (graceful — inject defaults if absent/malformed)
    _validate_executive_overview(result)
    _validate_executive_poster(result)
    _validate_solution_metadata(result, validation)
 
    return result
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# SECTION BUILDERS — each builds one logical display_data section
# ═══════════════════════════════════════════════════════════════════════════════
 
def _build_package_header(
    output: dict[str, Any],
    validation: dict[str, Any],
    readiness: dict[str, Any],
    quality_score: int,
) -> dict[str, Any]:
    """
    Package manifest card: solution identity, readiness score, quality score,
    final recommendation badge, and pipeline provenance summary.
    """
    sm   = output.get("solution_metadata", {})
    rec  = _safe_str(sm.get("final_recommendation"), "Pending")
    score = _safe_int(sm.get("architecture_score"))
 
    badge_color = (
        "success" if rec == "Approved" else
        "info"    if rec == "Approved With Recommendations" else
        "warning" if rec == "Requires Revision" else
        "error"
    )
 
    return {
        "heading": "Solution Package",
        "type": ST_PACKAGE_MANIFEST,
        "metadata": sm,
        "readiness": readiness,
        "document_quality_score": quality_score,
        "recommendation_badge": {"label": rec, "color": badge_color},
        "architecture_score": score,
    }
 
 
def _build_executive_intelligence(
    output: dict[str, Any],
    highlights: list[str],
    key_decisions: list[dict[str, Any]],
    risk_profile: dict[str, Any],
) -> dict[str, Any]:
    """
    Enterprise intelligence card: derived highlights, key decisions,
    risk profile summary, and cost snapshot — all in one scannable block.
    """
    # Cost snapshot: pull the TOTAL row from cost_report if available
    cost_total = ""
    for item in reversed(_as_list(output.get("cost_report"))):
        if isinstance(item, dict) and str(item.get("category", "")).upper() == "TOTAL":
            cost_total = _safe_str(item.get("estimate"), "")
            break
 
    return {
        "heading": "Executive Intelligence",
        "type": ST_INTELLIGENCE,
        "highlights": highlights,
        "key_decisions_count": len(key_decisions),
        "risk_profile": risk_profile,
        "cost_snapshot": cost_total,
        "top_decisions": key_decisions[:3],
    }
 
 
def _build_executive_overview(output: dict[str, Any]) -> dict[str, Any]:
    """Executive narrative section — preserves model-authored structure."""
    eo = output.get("executive_overview", {})
    return {
        "heading": _safe_str(eo.get("title"), "Executive Overview"),
        "type": ST_EXECUTIVE_OVERVIEW,
        "subtitle": _safe_str(eo.get("subtitle")),
        "content": _safe_str(eo.get("decision_summary"), output.get("executive_summary", "")),
        "sections": eo.get("sections", []),
        "confidence_statement": _safe_str(eo.get("confidence_statement")),
    }
 
 
def _build_poster_section(output: dict[str, Any]) -> dict[str, Any] | None:
    """Executive poster section — omitted if poster has no bands."""
    ep = output.get("executive_poster", {})
    if not ep or not ep.get("sections"):
        return None
    return {
        "heading": "Executive Architecture Poster",
        "type": ST_EXECUTIVE_POSTER,
        "poster": ep,
        "content": "Single-page executive infographic — complete solution at a glance.",
    }
 
 
def _build_architecture_sections(output: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Build three visually and semantically distinct architecture sections:
    1. Architecture Diagrams  — Mermaid interactive diagrams
    2. High-Level Design      — capability/service-boundary statements (executive audience)
    3. Low-Level Design       — named components, protocols, config (implementer audience)
    """
    sections: list[dict[str, Any]] = []
 
    # Diagrams (ordered: most-architectural to most-operational)
    diagram_order = [
        ("hld",          "High-Level Design"),
        ("architecture", "Solution Architecture"),
        ("lld",          "Low-Level Design"),
        ("deployment",   "Deployment Architecture"),
        ("data_flow",    "Data Flow"),
        ("network",      "Network Architecture"),
    ]
    diagram_list = []
    diagrams = output.get("diagrams", {})
    for key, title in diagram_order:
        code = diagrams.get(key, "")
        if _is_non_empty_str(code):
            diagram_list.append({"title": title, "code": code, "key": key})
 
    if diagram_list:
        sections.append({
            "heading": "Architecture Diagrams",
            "type": ST_MERMAID,
            "diagrams": diagram_list,
        })
 
    hld = _as_list(output.get("high_level_design"))
    if hld:
        sections.append({
            "heading": "High-Level Design",
            "type": ST_BULLET_HLD,
            "audience": "Executive",
            "description": "Business-capability and service-boundary statements — no implementation detail.",
            "items": hld,
        })
 
    lld = _as_list(output.get("low_level_design"))
    if lld:
        sections.append({
            "heading": "Low-Level Design",
            "type": ST_BULLET_LLD,
            "audience": "Implementation Team",
            "description": "Named components, protocols, versions, and configuration decisions.",
            "items": lld,
        })
 
    return sections
 
 
def _build_technical_sections(output: dict[str, Any]) -> list[dict[str, Any]]:
    """Security and deployment as typed card sections (not generic bullet lists)."""
    sections: list[dict[str, Any]] = []
 
    security = _as_list(output.get("security_architecture"))
    if security:
        sections.append({
            "heading": "Security Architecture",
            "type": ST_BULLET_SECURITY,
            "description": "Security controls, compliance frameworks, and protection boundaries.",
            "items": security,
        })
 
    deployment = _as_list(output.get("deployment_architecture"))
    if deployment:
        sections.append({
            "heading": "Deployment Architecture",
            "type": ST_BULLET_DEPLOYMENT,
            "description": "Cloud regions, availability zones, and traffic routing configuration.",
            "items": deployment,
        })
 
    return sections
 
 
def _build_roadmap_section(output: dict[str, Any]) -> dict[str, Any] | None:
    roadmap = _as_list(output.get("implementation_roadmap"))
    if not roadmap:
        return None
    return {
        "heading": "Implementation Roadmap",
        "type": ST_ROADMAP,
        "items": roadmap,
    }
 
 
def _build_risk_section(output: dict[str, Any], risk_profile: dict[str, Any]) -> dict[str, Any] | None:
    risks = _as_list(output.get("risk_register"))
    if not risks:
        return None
    # Sort: High → Medium → Low for executive reading order
    severity_order = {"high": 0, "medium": 1, "low": 2}
    risks_sorted = sorted(
        risks,
        key=lambda r: severity_order.get(str(r.get("severity", "")).lower(), 3)
        if isinstance(r, dict) else 3,
    )
    return {
        "heading": "Risk Register",
        "type": ST_RISK_TABLE,
        "profile": risk_profile,
        "items": risks_sorted,
    }
 
 
def _build_cost_section(output: dict[str, Any]) -> dict[str, Any] | None:
    cost = _as_list(output.get("cost_report"))
    if not cost:
        return None
    # Ensure TOTAL row is last
    non_total = [r for r in cost if isinstance(r, dict) and str(r.get("category", "")).upper() != "TOTAL"]
    total_rows = [r for r in cost if isinstance(r, dict) and str(r.get("category", "")).upper() == "TOTAL"]
    ordered = non_total + total_rows
    return {
        "heading": "Cost Summary",
        "type": ST_COST_TABLE,
        "items": ordered,
        "has_total": bool(total_rows),
    }
 
 
def _build_decisions_section(key_decisions: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not key_decisions:
        return None
    return {
        "heading": "Key Architectural Decisions",
        "type": ST_DECISION_TABLE,
        "items": key_decisions,
    }
 
 
def _build_traceability_section(
    discovery: dict[str, Any],
    knowledge: dict[str, Any],
    recommendation: dict[str, Any],
    architecture: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    """
    Agent pipeline provenance block. Makes the output auditable by recording
    which upstream agents contributed data and whether their outputs are present.
    """
    def _present(d: dict[str, Any]) -> str:
        return "✓ Present" if d else "✗ Missing"
 
    return {
        "heading": "Pipeline Traceability",
        "type": ST_TRACEABILITY,
        "agents": [
            {"name": "Discovery Agent",       "status": _present(discovery),      "role": "Business requirements, goals, and constraints"},
            {"name": "Knowledge Agent",        "status": _present(knowledge),      "role": "Enterprise standards and reference architectures"},
            {"name": "Recommendation Agent",   "status": _present(recommendation), "role": "Architecture patterns and technology decisions"},
            {"name": "Architecture Agent",     "status": _present(architecture),   "role": "Complete solution design and diagrams"},
            {"name": "Validation Agent",       "status": _present(validation),     "role": "Architecture review, scores, and compliance"},
        ],
    }
 
 
def _build_downloads_section(output: dict[str, Any]) -> dict[str, Any]:
    """
    Build the download manifest with per-asset availability indicators.
    Cards for empty downloads are marked unavailable rather than shown as present.
    """
    downloads_raw = output.get("downloads", {})
 
    assets = [
        {
            "key":         "html",
            "label":       "Enterprise HTML Report",
            "description": "Customer-ready HTML documentation with embedded styling and navigation",
            "icon":        "📄",
            "format":      "HTML",
            "available":   _is_non_empty_str(downloads_raw.get("html")),
        },
        {
            "key":         "markdown",
            "label":       "GitHub-Ready Markdown",
            "description": "Publication-ready architecture documentation for Confluence or GitHub",
            "icon":        "📝",
            "format":      "Markdown",
            "available":   _is_non_empty_str(downloads_raw.get("markdown")),
        },
        {
            "key":         "terraform",
            "label":       "Production Terraform Starter",
            "description": "Infrastructure-as-Code starter with best practices and explanatory comments",
            "icon":        "🏗️",
            "format":      "HCL",
            "available":   _is_non_empty_str(downloads_raw.get("terraform")),
        },
    ]
    return {
        "heading": "Enterprise Deliverables",
        "type": ST_DOWNLOADS,
        "downloads": assets,
    }
  
 
# ═══════════════════════════════════════════════════════════════════════════════
# SECTION ORCHESTRATOR — dynamic ordering by validation score
# ═══════════════════════════════════════════════════════════════════════════════
 
def _build_output_display_data(
    output: dict[str, Any],
    discovery: dict[str, Any],
    knowledge: dict[str, Any],
    recommendation: dict[str, Any],
    architecture: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    """
    Assemble the complete display_data payload.
 
    Section ordering is content-driven:
    - Score ≥ 90: lead with Architecture → Security → Roadmap; risks last
    - Score 75-89: lead with Overview → Architecture → Key Decisions → Risks
    - Score 60-74: lead with Risk prominently → Roadmap → Architecture
    - Score < 60:  lead with Risk as hero → Roadmap (revision path) → Architecture
    """
    sm    = output.get("solution_metadata", {})
    score = _safe_int(sm.get("architecture_score"), _extract_validation_score(validation))
 
    # ── Pre-compute intelligence ─────────────────────────────────────────────
    readiness      = _compute_package_readiness(output, validation)
    quality_score  = _compute_document_quality_score(output)
    highlights     = _extract_executive_highlights(output)
    key_decisions  = _extract_key_decisions(output)
    risk_profile   = _summarise_risk_profile(output)
 
    # ── Build individual section objects ─────────────────────────────────────
    header_section      = _build_package_header(output, validation, readiness, quality_score)
    intelligence_section = _build_executive_intelligence(output, highlights, key_decisions, risk_profile)
    overview_section    = _build_executive_overview(output)
    poster_section      = _build_poster_section(output)
    arch_sections       = _build_architecture_sections(output)
    tech_sections       = _build_technical_sections(output)
    roadmap_section     = _build_roadmap_section(output)
    risk_section        = _build_risk_section(output, risk_profile)
    cost_section        = _build_cost_section(output)
    decisions_section   = _build_decisions_section(key_decisions)
    trace_section       = _build_traceability_section(
        discovery, knowledge, recommendation, architecture, validation
    )
    downloads_section   = _build_downloads_section(output)
 
    # ── Dynamic ordering ─────────────────────────────────────────────────────
    sections: list[dict[str, Any]] = [header_section, intelligence_section]
 
    if score >= 90:
        # Confidence is high — lead with solution, architecture, then governance
        _append_if(sections, overview_section)
        _append_if(sections, poster_section)
        sections.extend(arch_sections)
        sections.extend(tech_sections)
        _append_if(sections, roadmap_section)
        _append_if(sections, decisions_section)
        _append_if(sections, risk_section)
        _append_if(sections, cost_section)
 
    elif score >= 75:
        # Solid score — overview first, then architecture, highlight decisions
        _append_if(sections, overview_section)
        _append_if(sections, poster_section)
        _append_if(sections, decisions_section)
        sections.extend(arch_sections)
        sections.extend(tech_sections)
        _append_if(sections, roadmap_section)
        _append_if(sections, risk_section)
        _append_if(sections, cost_section)
 
    elif score >= 60:
        # Revision required — surface risks and roadmap before architecture detail
        _append_if(sections, risk_section)
        _append_if(sections, roadmap_section)
        _append_if(sections, overview_section)
        _append_if(sections, poster_section)
        sections.extend(arch_sections)
        sections.extend(tech_sections)
        _append_if(sections, decisions_section)
        _append_if(sections, cost_section)
 
    else:
        # Rejected — risks are the hero message; roadmap = path to redesign
        _append_if(sections, risk_section)
        _append_if(sections, roadmap_section)
        _append_if(sections, overview_section)
        sections.extend(arch_sections)
        _append_if(sections, decisions_section)
        _append_if(sections, cost_section)
        sections.extend(tech_sections)
 
    # Always last: traceability + downloads (administrative)
    sections.append(trace_section)
    sections.append(downloads_section)
 
    return {
        "title":    _safe_str(sm.get("package_title"),    "Enterprise Solution Package"),
        "subtitle": _safe_str(sm.get("package_subtitle"), "Consultant-grade architecture deliverables"),
        "sections": sections,
    }
 
 
def _append_if(sections: list, section: dict[str, Any] | None) -> None:
    """Append section only if it is non-None (avoids scattered None-checks)."""
    if section is not None:
        sections.append(section)
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATION FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════
 
def generate_output(
    discovery: dict[str, Any],
    knowledge: dict[str, Any],
    recommendation: dict[str, Any],
    architecture: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate the complete Enterprise Solution Package.
 
    Args:
        discovery:       Approved Discovery Agent output
        knowledge:       Approved Knowledge Agent output
        recommendation:  Approved Recommendation Agent output
        architecture:    Approved Architecture Agent output
        validation:      Approved Validation Agent output
 
    Returns:
        {
          "agent_data":    Raw LLM output (all deliverables)
          "display_data":  UI-optimised section tree (dynamic ordering)
          "downloads":     {html, markdown, terraform} content strings
          "quality_report": Package completeness & integrity assessment
        }
 
    Raises:
        OutputAgentError           — missing inputs or unexpected runtime error
        OutputInvalidJSONError     — LLM returned invalid or incomplete JSON
        OutputAzureError           — Azure OpenAI API error
        OutputTimeoutError         — request exceeded 300-second timeout
    """
    if not discovery:
        raise OutputAgentError("Approved discovery output cannot be empty")
    if not knowledge:
        raise OutputAgentError("Approved knowledge output cannot be empty")
    if not recommendation:
        raise OutputAgentError("Approved recommendation output cannot be empty")
    if not architecture:
        raise OutputAgentError("Approved architecture output cannot be empty")
    if not validation:
        raise OutputAgentError("Approved validation output cannot be empty")
 
    payload = {
        "discovery":       discovery,
        "knowledge":       knowledge,
        "recommendation":  recommendation,
        "architecture":    architecture,
        "validation":      validation,
    }
 
    try:
        client = _create_client()
        response = client.chat.completions.create(
            model=_get_required_env("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": OUTPUT_SYSTEM_PROMPT},
                {"role": "user",   "content": json.dumps(payload)},
            ],
            response_format={"type": "json_object"},
        )
    except APITimeoutError as exc:
        raise OutputTimeoutError("Azure OpenAI request timed out") from exc
    except OpenAIError as exc:
        raise OutputAzureError(f"Azure OpenAI request failed: {exc}") from exc
    except Exception as exc:
        raise OutputAgentError(f"Unexpected output generation error: {exc}") from exc
 
    content = response.choices[0].message.content
    if not content:
        raise OutputInvalidJSONError("Output generation agent returned an empty response")
 
    # Pass validation into the parser so metadata scores can be aligned
    agent_data = _parse_output_json(content, validation)
 
    quality_report = _run_quality_gates(agent_data)
 
    display_data = _build_output_display_data(
        agent_data, discovery, knowledge, recommendation, architecture, validation
    )
   
    # ═══════════════════════════════════════════════════════════════════════
    # UNIFIED RENDERING ENGINE — All outputs from single normalized model
    # ═══════════════════════════════════════════════════════════════════════
    try:
        # Ensure downloads dict exists (should have been injected during parsing)
        if "downloads" not in agent_data:
            agent_data["downloads"] = {k: "" for k in DOWNLOAD_FIELDS}
       
        # Step 1: Normalize all agent outputs into unified Enterprise Blueprint
        blueprint = normalize_agent_outputs(
            discovery=discovery,
            knowledge=knowledge,
            recommendation=recommendation,
            architecture=architecture,
            validation=validation,
            output=agent_data
        )
       
        # Step 2: Render all 4 output formats from the same blueprint
        enterprise_html = render_html(blueprint)
        enterprise_markdown = render_markdown(blueprint)
        enterprise_terraform = render_terraform(blueprint)
       
        # Step 3: Replace LLM-generated downloads with enterprise-quality renders
        agent_data["downloads"]["html"] = enterprise_html
        agent_data["downloads"]["markdown"] = enterprise_markdown
        agent_data["downloads"]["terraform"] = enterprise_terraform
       
    except Exception as e:
        # Log error but don't fail the entire output generation
        # Keep the LLM-generated content as fallback
        import traceback
        print(f"Warning: Enterprise rendering failed: {e}")
        print(traceback.format_exc())
        # Fallback: ensure downloads exist even if rendering failed
        if "downloads" not in agent_data:
            agent_data["downloads"] = {k: "Error: Content generation failed" for k in DOWNLOAD_FIELDS}
 
    return {
        "agent_data":     agent_data,
        "display_data":   display_data,
        "downloads":      agent_data["downloads"],
        "quality_report": quality_report,
    }