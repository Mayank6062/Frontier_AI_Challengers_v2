"""
enterprise_markdown_renderer.py — Enterprise Architecture Markdown Documentation
===================================================================================
 
Renders MarkdownBlueprint to concise, professional Markdown documentation.
 
The document is structured like an enterprise architecture specification:
compact, readable, and fully driven by the normalized blueprint.
 
Note: This renderer is completely independent from HTML and Terraform renderers.
It accepts MarkdownBlueprint (not EnterpriseBlueprint) to ensure separation of concerns.
"""
 
from __future__ import annotations
 
import re
 
from app.models.markdown_blueprint import MarkdownBlueprint, MarkdownArchitectureLayer, MarkdownLayerComponent
 
 
def render_markdown(blueprint: MarkdownBlueprint) -> str:
    sections = [
        _render_header(blueprint),
        _render_executive_summary(blueprint),
        _render_architecture_overview(blueprint),
        _render_data_flow(blueprint),
        *(_render_layer_section(layer) for layer in blueprint.layers),
        _render_benefits(blueprint),
        _render_implementation_roadmap(blueprint),
        _render_success_metrics(blueprint),
        _render_conclusion(blueprint),
    ]
    return "\n\n".join(section for section in sections if section)
 
 
def _render_header(bp: MarkdownBlueprint) -> str:
    metadata_table = f"""| Property | Value |
|----------|-------|
| Version | {_clean(bp.version)} |
| Generated | {_clean(bp.generated_time)} |
| Client | {_clean(bp.client_name)} |
| Industry | {_clean(bp.industry)} |
| Cloud | {_clean(bp.cloud_provider)} |
| Status | {_clean(bp.architecture_status)} |
| Quality Score | {bp.quality_score}/100 |
| Confidence | {_clean(bp.confidence_level)} |"""
 
    return f"""# {_clean(bp.architecture_title)}
 
{_clean(bp.architecture_subtitle)}
 
{metadata_table}"""
 
 
def _render_executive_summary(bp: MarkdownBlueprint) -> str:
    summary = _paragraph(bp.executive_summary, min_sentences=2, max_sentences=3, max_words=150)
    if not summary:
        summary = "This architecture consolidates enterprise data flow, governance, and delivery objectives into a unified, scalable blueprint."
   
    return f"""---
 
## Executive Summary
 
> {summary}"""
 
 
def _render_architecture_overview(bp: MarkdownBlueprint) -> str:
    sections = ["---", "", "## Architecture Overview", ""]
   
    current_state = _paragraph(bp.current_state, min_sentences=1, max_sentences=2, max_words=80)
    if current_state:
        sections.append("### Current State")
        sections.append("")
        sections.append(current_state)
        sections.append("")
   
    target_state = _paragraph(bp.target_state, min_sentences=1, max_sentences=2, max_words=80)
    if target_state:
        sections.append("### Target State")
        sections.append("")
        sections.append(target_state)
        sections.append("")
   
    approach = _paragraph(bp.transformation_approach, min_sentences=1, max_sentences=2, max_words=100)
    if approach:
        sections.append("### Transformation Strategy")
        sections.append("")
        sections.append(approach)
   
    if len(sections) <= 4:
        return ""
   
    return "\n".join(sections)
 
 
def _render_layer_section(layer: MarkdownArchitectureLayer) -> str:
    lines = []
   
    lines.append("---")
    lines.append("")
    lines.append(f"## Layer {layer.layer_number} — {_clean(layer.layer_name)}")
    lines.append("")
   
    if layer.layer_purpose:
        purpose_text = _paragraph(layer.layer_purpose, min_sentences=2, max_sentences=3, max_words=90)
        lines.append(f"> {purpose_text}")
        lines.append("")
   
    if layer.business_goal:
        lines.append("**Business Goal**")
        lines.append("")
        goal_bullets = _extract_bullets(layer.business_goal, max_items=3, max_words=30)
        if goal_bullets:
            lines.extend(goal_bullets)
        else:
            lines.append(f"- {_sentence(layer.business_goal, max_words=30)}")
        lines.append("")
   
    if layer.business_challenge:
        lines.append("**Business Challenge**")
        lines.append("")
        challenge_bullets = _extract_bullets(layer.business_challenge, max_items=3, max_words=30)
        if challenge_bullets:
            lines.extend(challenge_bullets)
        else:
            lines.append(f"- {_sentence(layer.business_challenge, max_words=30)}")
        lines.append("")
   
    if layer.components:
        lines.append("---")
        lines.append("")
        lines.append("### Components")
        lines.append("")
       
        component_lines = []
        for component in layer.components:
            if component.title:
                component_lines.append(_render_component(component))
       
        lines.append("\n\n".join(component_lines))
   
    return "\n".join(lines)
 
 
def _render_component(component: MarkdownLayerComponent) -> str:
    lines: list[str] = [f"#### {_clean(component.title)}"]
 
    purpose = _extract_bullets(component.purpose, max_items=1, max_words=40)
    if purpose:
        lines.append("")
        lines.append("**Purpose**")
        lines.append("")
        lines.extend(purpose)
 
    technology = _extract_bullets(component.technology, max_items=5, max_words=18)
    if technology:
        lines.append("")
        lines.append("**Technology**")
        lines.append("")
        lines.extend(technology)
 
    protocols = _extract_bullets(component.protocols, max_items=4, max_words=18)
    if protocols:
        lines.append("")
        lines.append("**Protocols**")
        lines.append("")
        lines.extend(protocols)
 
    security = _extract_bullets(component.security, max_items=2, max_words=20)
    if security:
        lines.append("")
        lines.append("**Security**")
        lines.append("")
        lines.extend(security)
 
    business_value = _extract_bullets(component.business_value, max_items=2, max_words=25)
    if business_value:
        lines.append("")
        lines.append("**Business Value**")
        lines.append("")
        lines.extend(business_value)
 
    operational_value = _extract_bullets(component.operational_value, max_items=2, max_words=25)
    if operational_value:
        lines.append("")
        lines.append("**Operational Value**")
        lines.append("")
        lines.extend(operational_value)
 
    key_features = _extract_bullets(component.key_features, max_items=3, max_words=20)
    if key_features:
        lines.append("")
        lines.append("**Key Features**")
        lines.append("")
        lines.extend(key_features)
 
    lines.append("")
    lines.append("---")
   
    return "\n".join(lines)
 
 
def _render_benefits(bp: MarkdownBlueprint) -> str:
    if not bp.benefits:
        return ""
 
    sections = ["---", "", "## Architecture Benefits", ""]
   
    for benefit in bp.benefits:
        bullets = _benefit_bullets(benefit.benefits, max_items=6)
        if not bullets:
            continue
       
        sections.append(f"### {_clean(benefit.category_name)}")
        sections.append("")
        sections.extend(bullets)
        sections.append("")
   
    if len(sections) <= 4:
        return ""
   
    return "\n".join(sections)
 
 
def _render_implementation_roadmap(bp: MarkdownBlueprint) -> str:
    if not bp.implementation_phases:
        return ""
 
    sections = ["---", "", "## Implementation Roadmap", ""]
   
    for phase in bp.implementation_phases:
        deliverables = _implementation_deliverables(phase.deliverables)
        if not deliverables:
            continue
       
        sections.append(f"### {_clean(phase.phase_name)}")
        sections.append("")
       
        if phase.duration:
            sections.append("**Duration**")
            sections.append("")
            sections.append(f"{_clean(phase.duration)}")
            sections.append("")
       
        sections.append("**Deliverables**")
        sections.append("")
        sections.extend(deliverables)
        sections.append("")
       
        # Add default success criteria
        sections.append("**Success Criteria**")
        sections.append("")
        sections.append("- Completion on schedule")
        sections.append("- Quality benchmarks met")
        sections.append("")
   
    if len(sections) <= 4:
        return ""
   
    return "\n".join(sections)
 
 
def _render_success_metrics(bp: MarkdownBlueprint) -> str:
    sections = ["---", "", "## Success Metrics", ""]
   
    # Business Metrics
    sections.append("### Business Metrics")
    sections.append("")
    sections.append("- **ROI:** Measurable cost optimization")
    sections.append("- **Efficiency:** Automated workflows and governance")
    sections.append("")
   
    # Technical Metrics
    sections.append("### Technical Metrics")
    sections.append("")
    sections.append(f"- **Availability:** Enterprise-grade 99.95%")
    sections.append(f"- **Performance:** Sub-second response times")
    sections.append("")
   
    # Delivery Metrics
    sections.append("### Delivery Metrics")
    sections.append("")
    sections.append(f"- **Quality Score:** {bp.quality_score}/100")
    sections.append(f"- **Confidence Level:** {_clean(bp.confidence_level)}")
    sections.append("")
   
    return "\n".join(sections)
 
 
def _render_data_flow(bp: MarkdownBlueprint) -> str:
    if not bp.data_flow_pathway:
        return ""
   
    return f"""---
 
## Data Flow
 
```text
{bp.data_flow_pathway.strip()}
```"""
 
 
def _render_conclusion(bp: MarkdownBlueprint) -> str:
    closing = _paragraph(bp.executive_summary, min_sentences=1, max_sentences=2, max_words=120)
    if not closing:
        closing = "This architecture blueprint delivers enterprise-grade governance, scalability, and operational excellence."
   
    return f"""---
 
## Conclusion
 
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
 
 
def _extract_bullets(value: str | None, max_items: int = 8, max_words: int = 20) -> list[str]:
    """Convert text to markdown bullet list items."""
    if not value:
        return []
   
    items = _split_items(value)
    if not items:
        return []
   
    bullets = []
    for item in items[:max_items]:
        text = _truncate_words(item, max_words)
        if text:
            bullets.append(f"- {text}")
   
    return bullets
 
 
def _sentence(value: str | None, max_words: int = 24) -> str:
    text = _clean(value)
    if not text:
        return ""
    return _truncate_words(text, max_words)
 
 
def _implementation_deliverables(value: str | list | None) -> list[str]:
    """Extract implementation deliverables from list or string, formatted as bullets."""
    if not value:
        return []
   
    if isinstance(value, list):
        items = [_clean(str(item)) for item in value if item]
    else:
        items = _split_items(value)
   
    bullets = []
    for item in items[:6]:
        text = _truncate_words(item, 20)
        if text:
            bullets.append(f"- {text}")
   
    return bullets
 
 
def _benefit_bullets(items: list[str], max_items: int = 6) -> list[str]:
    """Convert benefit items to proper bullet list, max 6 items."""
    bullets = []
    for item in items:
        text = _clean(item)
        if text:
            formatted = _truncate_words(text, 22)
            bullets.append(f"- {formatted}")
        if len(bullets) >= max_items:
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
