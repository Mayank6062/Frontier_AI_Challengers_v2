"""
enterprise_markdown_renderer.py — Enterprise Architecture Markdown Documentation
===================================================================================
 
Renders EnterpriseBlueprint to concise, professional Markdown documentation.
 
The document is structured like an enterprise architecture specification:
compact, readable, and fully driven by the normalized blueprint.
"""
 
from __future__ import annotations
 
import re
 
from app.models.enterprise_blueprint import EnterpriseBlueprint, ArchitectureLayer, LayerComponent
 
 
def render_markdown(blueprint: EnterpriseBlueprint) -> str:
    sections = [
        _render_header(blueprint),
        _render_executive_summary(blueprint),
        _render_architecture_overview(blueprint),
        *(_render_layer_section(layer) for layer in blueprint.layers),
        _render_benefits(blueprint),
        _render_implementation_roadmap(blueprint),
        _render_success_metrics(blueprint),
        _render_conclusion(blueprint),
    ]
    return "\n\n".join(section for section in sections if section)
 
 
def _render_header(bp: EnterpriseBlueprint) -> str:
    metadata_lines = [
        f"- **Version:** {_clean(bp.version)}",
        f"- **Generated:** {_clean(bp.generated_time)}",
        f"- **Client:** {_clean(bp.client_name)}",
        f"- **Industry:** {_clean(bp.industry)}",
        f"- **Cloud Provider:** {_clean(bp.cloud_provider)}",
        f"- **Status:** {_clean(bp.architecture_status)}",
        f"- **Quality Score:** {bp.quality_score}/100",
        f"- **Confidence Level:** {_clean(bp.confidence_level)}",
    ]
 
    return f"""# {_clean(bp.architecture_title)}
 
### {_clean(bp.architecture_subtitle)}
 
#### Document Metadata
 
{chr(10).join(metadata_lines)}"""
 
 
def _render_executive_summary(bp: EnterpriseBlueprint) -> str:
    summary = _paragraph(bp.executive_summary, min_sentences=2, max_sentences=3, max_words=150)
    if not summary:
        summary = "This architecture consolidates the enterprise data flow, governance posture, and delivery roadmap into one normalized blueprint."
    return f"""## Executive Summary
 
{summary}"""
 
 
def _render_architecture_overview(bp: EnterpriseBlueprint) -> str:
    lines = []
    current_state = _paragraph(bp.current_state, min_sentences=1, max_sentences=2, max_words=45)
    target_state = _paragraph(bp.target_state, min_sentences=1, max_sentences=2, max_words=45)
    approach = _paragraph(bp.transformation_approach, min_sentences=1, max_sentences=2, max_words=45)
    data_flow = _paragraph(bp.data_flow_pathway, min_sentences=1, max_sentences=2, max_words=45)
 
    if current_state:
        lines.append(f"- **Current State:** {current_state}")
    if target_state:
        lines.append(f"- **Target State:** {target_state}")
    if approach:
        lines.append(f"- **Transformation Approach:** {approach}")
    if data_flow:
        lines.append(f"- **Data Flow:** {data_flow}")
 
    return f"""## Architecture Overview
 
{chr(10).join(lines)}"""
 
 
def _render_layer_section(layer: ArchitectureLayer) -> str:
    overview_parts = []
    if layer.layer_purpose:
        overview_parts.append(_paragraph(layer.layer_purpose, min_sentences=2, max_sentences=3, max_words=70))
    if layer.business_goal:
        overview_parts.append(f"**Business Goal:** {_sentence(layer.business_goal, max_words=24)}")
    if layer.business_challenge:
        overview_parts.append(f"**Business Challenge:** {_sentence(layer.business_challenge, max_words=24)}")
 
    components = [
        _render_component(component)
        for component in layer.components
        if component.title
    ]
 
    return f"""## Layer {layer.layer_number}: {_clean(layer.layer_name)}
 
### Overview
 
{chr(10).join(overview_parts)}
 
### Components
 
{chr(10).join(components)}"""
 
 
def _render_component(component: LayerComponent) -> str:
    lines: list[str] = [f"#### {_clean(component.title)}"]
 
    purpose = _paragraph(component.purpose, min_sentences=2, max_sentences=3, max_words=50)
    if purpose:
        lines.append(f"**Purpose:** {purpose}")
 
    technology = _list_line(component.technology, max_items=6)
    if technology:
        lines.append(f"**Technology:** {technology}")
 
    protocols = _list_line(component.protocols, max_items=5)
    if protocols:
        lines.append(f"**Protocols:** {protocols}")
 
    standards = _list_line(component.standards, max_items=5)
    if standards:
        lines.append(f"**Standards:** {standards}")
 
    inputs = _sentence(component.inputs, max_words=22)
    if inputs:
        lines.append(f"**Input:** {inputs}")
 
    outputs = _sentence(component.outputs, max_words=22)
    if outputs:
        lines.append(f"**Output:** {outputs}")
 
    security = _two_line_value(component.security)
    if security:
        lines.append(f"**Security:** {security}")
 
    business_value = _two_line_value(component.business_value)
    if business_value:
        lines.append(f"**Business Value:** {business_value}")
 
    operational_value = _two_line_value(component.operational_value)
    if operational_value:
        lines.append(f"**Operational Value:** {operational_value}")
 
    optional_pairs = [
        ("Performance", _sentence(component.performance, max_words=18)),
        ("Scalability", _sentence(component.scalability, max_words=18)),
        ("Monitoring", _sentence(component.monitoring, max_words=18)),
        ("Availability", _sentence(component.availability, max_words=18)),
        ("Disaster Recovery", _sentence(component.disaster_recovery, max_words=18)),
        ("Expected Volume", _sentence(component.expected_volume, max_words=18)),
        ("Business Owner", _sentence(component.business_owner, max_words=18)),
        ("Business Challenges", _sentence(component.business_challenges, max_words=18)),
        ("Data Formats", _sentence(component.data_formats, max_words=18)),
    ]
    for label, value in optional_pairs:
        if value:
            lines.append(f"**{label}:** {value}")
 
    key_features = _feature_bullets(component.key_features)
    if key_features:
        lines.append("**Key Features:**")
        lines.extend(f"- {feature}" for feature in key_features)
 
    return "\n\n".join(lines)
 
 
def _render_benefits(bp: EnterpriseBlueprint) -> str:
    if not bp.benefits:
        return ""
 
    sections = []
    for benefit in bp.benefits:
        bullets = _benefit_bullets(benefit.benefits)
        if not bullets:
            continue
        sections.append(f"""### {_clean(benefit.icon)} {_clean(benefit.category_name)}
 
{chr(10).join(f'- {item}' for item in bullets)}""")
 
    return f"""## Architecture Benefits
 
{chr(10).join(sections)}""" if sections else ""
 
 
def _render_implementation_roadmap(bp: EnterpriseBlueprint) -> str:
    if not bp.implementation_phases:
        return ""
 
    phases = []
    for phase in bp.implementation_phases:
        deliverables = _feature_bullets(phase.deliverables, max_items=4, max_words=14)
        if not deliverables:
            continue
        phases.append(f"""### {_clean(phase.phase_name)} ({_clean(phase.duration)})
 
{chr(10).join(f'- {item}' for item in deliverables)}""")
 
    return f"""## Implementation Roadmap
 
{chr(10).join(phases)}""" if phases else ""
 
 
def _render_success_metrics(bp: EnterpriseBlueprint) -> str:
    rows = ["| Metric | Value | Description |", "|---|---:|---|"]
    rows.append(f"| Quality Score | {bp.quality_score}/100 | {_clean(bp.architecture_status)} |")
    rows.append(f"| Confidence | {_clean(bp.confidence_level)} | {_sentence(bp.executive_summary, max_words=16)} |")
 
    for outcome in bp.business_outcomes[:4]:
        rows.append(f"| {_clean(outcome.label)} | {_clean(outcome.metric)} | {_sentence(outcome.description, max_words=18)} |")
 
    return f"""## Success Metrics
 
{chr(10).join(rows)}"""
 
 
def _render_conclusion(bp: EnterpriseBlueprint) -> str:
    closing = _paragraph(bp.executive_summary, min_sentences=1, max_sentences=2, max_words=110)
    if not closing:
        closing = "This blueprint keeps the architecture, delivery, and governance narrative aligned while remaining readable as a compact design document."
    return f"""## Conclusion
 
{closing}"""
 
 
def _paragraph(value: str | None, min_sentences: int = 1, max_sentences: int = 2, max_words: int = 60) -> str:
    text = _clean(value)
    if not text:
        return ""
 
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if not sentences:
        return _truncate_words(text, max_words)
 
    selected = sentences[:max_sentences]
    if len(selected) < min_sentences:
        selected = sentences[:min_sentences]
 
    return _truncate_words(" ".join(selected), max_words)
 
 
def _sentence(value: str | None, max_words: int = 24) -> str:
    text = _clean(value)
    if not text:
        return ""
    return _truncate_words(text, max_words)
 
 
def _two_line_value(value: str | None) -> str:
    text = _clean(value)
    if not text:
        return ""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if not sentences:
        return _truncate_words(text, 28)
    return _truncate_words(" ".join(sentences[:2]), 28)
 
 
def _list_line(value: str | None, max_items: int = 5) -> str:
    items = _split_items(value)
    if not items:
        return ""
    return ", ".join(items[:max_items])
 
 
def _feature_bullets(value: str | None, max_items: int = 5, max_words: int = 10) -> list[str]:
    items = _split_items(value)
    return [_truncate_words(item, max_words) for item in items[:max_items]]
 
 
def _benefit_bullets(items: list[str]) -> list[str]:
    bullets = []
    for item in items:
        text = _clean(item)
        if text:
            bullets.append(_truncate_words(text, 14))
        if len(bullets) >= 6:
            break
    return bullets
 
 
def _split_items(value: str | None) -> list[str]:
    text = _clean(value)
    if not text:
        return []
 
    if "•" in text or ";" in text or "|" in text:
        pieces = re.split(r"\s*[•;|]\s*", text)
    elif text.count(",") >= 2:
        pieces = [part.strip() for part in text.split(",")]
    else:
        pieces = [text]
 
    return [piece.strip(" -") for piece in pieces if piece and piece.strip(" -")]
 
 
def _truncate_words(value: str, max_words: int) -> str:
    words = value.split()
    if len(words) <= max_words:
        return value
    return " ".join(words[:max_words]) + "…"
 
 
def _clean(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()