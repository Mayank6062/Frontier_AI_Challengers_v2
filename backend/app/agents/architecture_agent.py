import json
import os
from pathlib import Path
from typing import Any
 
from dotenv import load_dotenv
from openai import APITimeoutError, AzureOpenAI, OpenAIError
 
from app.prompts.architecture_prompt import ARCHITECTURE_SYSTEM_PROMPT
from app.utils.mermaid_validator import (
    validate_mermaid_diagram,
    validate_drawio_xml,
    sanitize_mermaid_code,
    wrap_drawio_xml,
)
 
 
load_dotenv(Path(__file__).resolve().parents[2] / ".env")
 
 
# Top-level fields the LLM must return
ARCHITECTURE_FIELDS = {
    "current_state",
    "target_state",
    "high_level_design",
    "low_level_design",
    "data_flow",
    "deployment_view",
    "integration_view",
    "security_view",
    "network_view",
    "infrastructure_view",
    "architecture_summary",
}
 
# Expected diagram titles (7 comprehensive enterprise diagrams — quality over quantity)
EXPECTED_DIAGRAM_TITLES = [
    "ExecutiveArchitecturePoster",
    "Overall Solution Architecture",
    "Enterprise Architecture Design",
    "System Design",
    "Data Architecture",
    "Platform Architecture",
    "Operations Architecture",
]
 
# Legacy diagram fields (for backward compat if LLM returns old format)
LEGACY_DIAGRAM_FIELDS = {
    "high_level_diagram",
    "data_flow",
    "deployment_view",
    "integration_view",
    "network_view",
    "infrastructure_view",
    "overall_architecture_diagram",
}
 
 
class ArchitectureAgentError(RuntimeError):
    pass
 
 
class ArchitectureInvalidJSONError(ArchitectureAgentError):
    pass
 
 
class ArchitectureAzureError(ArchitectureAgentError):
    pass
 
 
class ArchitectureTimeoutError(ArchitectureAgentError):
    pass
 
 
def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ArchitectureAgentError(f"Missing required environment variable: {name}")
    return value
 
 
def _create_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=_get_required_env("AZURE_OPENAI_API_KEY"),
        azure_endpoint=_get_required_env("AZURE_OPENAI_ENDPOINT"),
        api_version=_get_required_env("AZURE_OPENAI_API_VERSION"),
        timeout=120.0,
    )
 
 
def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, "", "Not Specified"):
        return []
    return [value]
 
 
def _safe_str(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return "Not Specified"
    return str(value)
 
 
def _validate_and_fix_diagram(diag: dict[str, Any]) -> dict[str, Any]:
    """Validate and auto-fix Mermaid and Draw.io XML in a diagram."""
   
    # Validate and fix Mermaid
    mermaid_code = diag.get("mermaid", "")
    if mermaid_code and isinstance(mermaid_code, str) and mermaid_code.strip():
        # Try to sanitize first
        mermaid_code = sanitize_mermaid_code(mermaid_code)
       
        # Validate
        is_valid, errors = validate_mermaid_diagram(mermaid_code)
        if not is_valid:
            print(f"⚠️  Mermaid validation failed for '{diag.get('title', 'Unknown')}':")
            for err in errors[:5]:  # Show first 5 errors
                print(f"   - {err}")
            # Keep the code anyway but log the issue
       
        diag["mermaid"] = mermaid_code
   
    # Validate and fix Draw.io XML
    drawio_xml = diag.get("drawio_xml", "")
    if drawio_xml and isinstance(drawio_xml, str) and drawio_xml.strip():
        # Wrap if needed
        drawio_xml = wrap_drawio_xml(drawio_xml)
       
        # Validate
        is_valid, errors = validate_drawio_xml(drawio_xml)
        if not is_valid:
            print(f"⚠️  Draw.io XML validation failed for '{diag.get('title', 'Unknown')}':")
            for err in errors[:5]:
                print(f"   - {err}")
       
        diag["drawio_xml"] = drawio_xml
   
    return diag
 
 
def _normalize_diagram(raw: Any) -> dict[str, Any]:
    """Ensure a diagram object has all required enterprise-grade fields."""
    if not isinstance(raw, dict):
        return {
            "title": "Diagram",
            "description": "",
            "diagram_type": "flowchart",
            "mermaid": "",
            "drawio_xml": "",
            "svg_layout": {},
            "key_components": [],
            "design_decisions": [],
            "architecture_principles": [],
            "assumptions": [],
            "explanation": [],
        }
 
    svg_layout = raw.get("svg_layout")
    if not isinstance(svg_layout, dict):
        svg_layout = {}
 
    diagram_type = _safe_str(raw.get("diagram_type", "flowchart"))
 
    normalized = {
        "title": _safe_str(raw.get("title", "Diagram")),
        "description": _safe_str(raw.get("description", "")),
        "diagram_type": diagram_type,
        "mermaid": _safe_str(raw.get("mermaid", "")),
        "drawio_xml": _safe_str(raw.get("drawio_xml", "")),
        "svg_layout": svg_layout,
        "key_components": _as_list(raw.get("key_components")),
        "design_decisions": _as_list(raw.get("design_decisions")),
        "architecture_principles": _as_list(raw.get("architecture_principles")),
        "assumptions": _as_list(raw.get("assumptions")),
        "explanation": _as_list(raw.get("explanation")),
        # Preserve executive_poster payload so _build_architecture_display_data can access it
        "executive_poster": raw.get("executive_poster") if diagram_type == "executive_poster" else None,
        "business_summary": _safe_str(raw.get("business_summary", "")),
    }
   
    # Validate and auto-fix Mermaid and Draw.io XML (skip for executive poster — no mermaid)
    if diagram_type == "executive_poster":
        return normalized
    return _validate_and_fix_diagram(normalized)
 
 
def _convert_legacy_diagrams(legacy: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert old architecture_diagram dict format to new array format."""
    mapping = [
        ("overall_architecture_diagram", "Overall Solution Architecture"),
        ("high_level_diagram", "High Level Architecture"),
        ("data_flow", "Data Flow Architecture"),
        ("deployment_view", "Deployment Architecture"),
        ("integration_view", "Integration Architecture"),
        ("network_view", "Network Architecture"),
        ("infrastructure_view", "Infrastructure Architecture"),
    ]
    diagrams = []
    for field, title in mapping:
        code = legacy.get(field, "")
        if code and isinstance(code, str) and code.strip():
            diagrams.append(_normalize_diagram({
                "title": title,
                "description": f"Auto-converted from legacy {field}",
                "diagram_type": "flowchart",
                "mermaid": code.strip(),
            }))
    return diagrams
 
 
def _parse_architecture_json(content: str) -> dict[str, Any]:
    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ArchitectureInvalidJSONError("Architecture agent returned invalid JSON") from exc
 
    if not isinstance(result, dict):
        raise ArchitectureInvalidJSONError("Architecture agent JSON must be an object")
 
    # Fill missing top-level fields with defaults
    for field in ARCHITECTURE_FIELDS:
        if field not in result:
            if field in ("current_state", "target_state", "architecture_summary"):
                result[field] = "Not Specified"
            else:
                result[field] = []
 
    # Handle diagrams: new format (architecture_diagrams array) or legacy (architecture_diagram dict)
    if "architecture_diagrams" in result and isinstance(result["architecture_diagrams"], list):
        # New format — normalize each diagram
        result["architecture_diagrams"] = [
            _normalize_diagram(d) for d in result["architecture_diagrams"]
        ]
    elif "architecture_diagram" in result and isinstance(result["architecture_diagram"], dict):
        # Legacy format — convert to new format
        result["architecture_diagrams"] = _convert_legacy_diagrams(result["architecture_diagram"])
    else:
        # Neither exists — empty diagrams
        result["architecture_diagrams"] = []
 
    # Also keep architecture_diagram for backward compat with validation agent
    if "architecture_diagram" not in result:
        result["architecture_diagram"] = {}
        # Populate legacy fields from new diagrams for downstream agents
        title_to_legacy = {
            "Overall Solution Architecture": "overall_architecture_diagram",
            "High Level Architecture": "high_level_diagram",
            "Data Flow Architecture": "data_flow",
            "Deployment Architecture": "deployment_view",
            "Integration Architecture": "integration_view",
            "Network Architecture": "network_view",
            "Infrastructure Architecture": "infrastructure_view",
        }
        for diag in result["architecture_diagrams"]:
            legacy_key = title_to_legacy.get(diag.get("title", ""))
            if legacy_key:
                result["architecture_diagram"][legacy_key] = diag.get("mermaid", "")
 
    # Fill any missing legacy diagram sub-fields
    for field in LEGACY_DIAGRAM_FIELDS:
        if field not in result.get("architecture_diagram", {}):
            result.setdefault("architecture_diagram", {})[field] = ""
 
    return result
 
 
def _build_architecture_display_data(architecture: dict[str, Any]) -> dict[str, Any]:
    """Build display_data with rich, enterprise-grade diagram sections."""
 
    sections: list[dict[str, Any]] = [
        {
            "heading": "Architecture Summary",
            "type": "paragraph",
            "content": architecture.get("architecture_summary", "Not Specified"),
        },
        {
            "heading": "Current State",
            "type": "paragraph",
            "content": architecture.get("current_state", "Not Specified"),
        },
        {
            "heading": "Target State",
            "type": "paragraph",
            "content": architecture.get("target_state", "Not Specified"),
        },
        {
            "heading": "High Level Design",
            "type": "bullet_list",
            "items": _as_list(architecture.get("high_level_design")),
        },
        {
            "heading": "Low Level Design",
            "type": "bullet_list",
            "items": _as_list(architecture.get("low_level_design")),
        },
        {
            "heading": "Data Flow",
            "type": "bullet_list",
            "items": _as_list(architecture.get("data_flow")),
        },
        {
            "heading": "Deployment View",
            "type": "bullet_list",
            "items": _as_list(architecture.get("deployment_view")),
        },
        {
            "heading": "Integration View",
            "type": "bullet_list",
            "items": _as_list(architecture.get("integration_view")),
        },
        {
            "heading": "Security View",
            "type": "bullet_list",
            "items": _as_list(architecture.get("security_view")),
        },
        {
            "heading": "Network View",
            "type": "bullet_list",
            "items": _as_list(architecture.get("network_view")),
        },
        {
            "heading": "Infrastructure View",
            "type": "bullet_list",
            "items": _as_list(architecture.get("infrastructure_view")),
        },
    ]
 
    # ── Individual Enterprise Diagrams (7 total) ─────────────────────────
    # DIAGRAM 1: ExecutiveArchitecturePoster (component-based, not Mermaid)
    # DIAGRAMS 2-7: Mermaid diagrams
    diagrams = architecture.get("architecture_diagrams", [])
    if isinstance(diagrams, list):
        for idx, diag in enumerate(diagrams):
            if not isinstance(diag, dict):
                continue
 
            diagram_type = _safe_str(diag.get("diagram_type", "flowchart"))
           
            # ── DIAGRAM 1: Executive Poster (component-based) ──
            if diagram_type == "executive_poster":
                poster = diag.get("executive_poster")
                if isinstance(poster, dict):
                    # Ensure sections list exists even if LLM omits it
                    if not poster.get("sections"):
                        print(f"⚠️  ExecutiveArchitecturePoster: 'sections' missing — poster will not render")
                    sections.append({
                        "heading": _safe_str(diag.get("title", "ExecutiveArchitecturePoster")),
                        "type": "executive_poster",
                        "content": _safe_str(diag.get("description", "")),
                        "poster": poster,
                    })
                else:
                    print(f"⚠️  ExecutiveArchitecturePoster: 'executive_poster' key missing or not a dict — skipping")
                continue  # Skip to next diagram
 
            # ── DIAGRAMS 2-7: Mermaid diagrams ──
            mermaid_code = diag.get("mermaid", "")
            svg_layout = diag.get("svg_layout") or {}
            drawio_xml = diag.get("drawio_xml", "")
 
            # Skip completely empty diagrams (no mermaid, no svg, no drawio)
            if (
                (not mermaid_code or not str(mermaid_code).strip())
                and not svg_layout
                and (not drawio_xml or not str(drawio_xml).strip())
            ):
                continue
 
            diagram_section: dict[str, Any] = {
                "heading": _safe_str(diag.get("title", "Architecture Diagram")),
                "type": "architecture_diagram",
                "content": _safe_str(diag.get("description", "")),
                "business_summary": _safe_str(diag.get("business_summary", "")),
                "diagram_type": diagram_type,
                "diagrams": [
                    {
                        "title": _safe_str(diag.get("title", "Architecture Diagram")),
                        "code": (mermaid_code or "").strip(),
                    }
                ] if mermaid_code and str(mermaid_code).strip() else [],
                "drawio_xml": (drawio_xml or "").strip(),
                "svg_layout": svg_layout if isinstance(svg_layout, dict) else {},
                "metadata": {
                    "key_components": _as_list(diag.get("key_components")),
                    "component_explanations": diag.get("component_explanations", []) if isinstance(diag.get("component_explanations"), list) else [],
                    "design_decisions": _as_list(diag.get("design_decisions")),
                    "business_benefits": _as_list(diag.get("business_benefits")),
                    "technical_benefits": _as_list(diag.get("technical_benefits")),
                    "architecture_principles": _as_list(diag.get("architecture_principles")),
                    "risks": _as_list(diag.get("risks")),
                    "recommendations": _as_list(diag.get("recommendations")),
                    "assumptions": _as_list(diag.get("assumptions")),
                    "explanation": _as_list(diag.get("explanation")),
                },
            }
            sections.append(diagram_section)
 
    return {
        "title": "Enterprise Architecture Design Report",
        "subtitle": "Production-ready architecture for CTO approval and enterprise review",
        "sections": sections,
        "actions": [
            {"label": "Edit Requirement", "action": "edit"},
            {"label": "Approve & Continue", "action": "approve"},
        ],
    }
 
 
def generate_architecture(
    discovery: dict[str, Any],
    knowledge: dict[str, Any],
    recommendation: dict[str, Any],
) -> dict[str, Any]:
    if not discovery:
        raise ArchitectureAgentError("Approved discovery output cannot be empty")
    if not knowledge:
        raise ArchitectureAgentError("Approved knowledge output cannot be empty")
    if not recommendation:
        raise ArchitectureAgentError("Approved recommendation output cannot be empty")
 
    payload = {
        "discovery": discovery,
        "knowledge": knowledge,
        "recommendation": recommendation,
    }
 
    try:
        client = _create_client()
        response = client.chat.completions.create(
            model=_get_required_env("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": ARCHITECTURE_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload)},
            ],
            response_format={"type": "json_object"},
        )
    except APITimeoutError as exc:
        raise ArchitectureTimeoutError("Azure OpenAI request timed out") from exc
    except OpenAIError as exc:
        raise ArchitectureAzureError(f"Azure OpenAI request failed: {exc}") from exc
    except Exception as exc:
        raise ArchitectureAgentError(f"Unexpected architecture error: {exc}") from exc
 
    content = response.choices[0].message.content
    if not content:
        raise ArchitectureInvalidJSONError("Architecture agent returned an empty response")
 
    agent_data = _parse_architecture_json(content)
 
    return {
        "agent_data": agent_data,
        "display_data": _build_architecture_display_data(agent_data),
    }
 