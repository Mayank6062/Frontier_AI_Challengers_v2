"""
markdown_blueprint.py — Markdown-Specific Normalization Model
==============================================================
 
Independent blueprint for Markdown documentation generation.
 
This blueprint is completely independent from HTML and Terraform blueprints.
It contains ONLY the fields required for Markdown output formatting.
 
No inheritance. No cross-renderer dependencies.
Each renderer owns its own data model.
"""
 
from dataclasses import dataclass, field
from typing import Any
from datetime import datetime
 
 
@dataclass
class MarkdownLayerComponent:
    """Component for Markdown documentation."""
    title: str
    purpose: str
    technology: str
    protocols: str = ""
    standards: str = ""
    inputs: str = ""
    outputs: str = ""
    data_formats: str = ""
    expected_volume: str = ""
    scalability: str = ""
    performance: str = ""
    monitoring: str = ""
    security: str = ""
    availability: str = ""
    disaster_recovery: str = ""
    business_value: str = ""
    operational_value: str = ""
    business_owner: str = ""
    business_challenges: str = ""
    key_features: str = ""
 
 
@dataclass
class MarkdownArchitectureLayer:
    """Architecture layer for Markdown documentation."""
    layer_number: int
    layer_name: str
    layer_purpose: str
    business_goal: str
    business_challenge: str
    components: list[MarkdownLayerComponent] = field(default_factory=list)
 
 
@dataclass
class MarkdownBenefitCategory:
    """Benefit category for Markdown documentation."""
    category_name: str
    icon: str
    benefits: list[str]
 
 
@dataclass
class MarkdownImplementationPhase:
    """Implementation phase for Markdown roadmap."""
    phase_name: str
    duration: str
    deliverables: list[str]
 
 
@dataclass
class MarkdownBusinessOutcome:
    """Business outcome metric for Markdown success metrics."""
    metric: str
    label: str
    description: str
 
 
@dataclass
class MarkdownBlueprint:
    """
    Complete Markdown-specific normalization model.
   
    This blueprint is independent from enterprise_blueprint and terraform_blueprint.
    It contains ONLY fields required for Markdown documentation generation.
   
    Responsibilities:
    - Executive Summary
    - Architecture Overview
    - Layer Overview & Components
    - Benefits
    - Implementation Roadmap
    - Success Metrics
    - Conclusion
    """
    # ═══════════════════════════════════════════════════════════════════
    # HEADER & METADATA
    # ═══════════════════════════════════════════════════════════════════
    architecture_title: str
    architecture_subtitle: str
    version: str
    generated_time: str
    client_name: str
    industry: str
    cloud_provider: str
    architecture_status: str
    quality_score: int
    confidence_level: str
   
    # ═══════════════════════════════════════════════════════════════════
    # CORE CONTENT
    # ═══════════════════════════════════════════════════════════════════
    executive_summary: str
    current_state: str = ""
    target_state: str = ""
    transformation_approach: str = ""
    data_flow_pathway: str = ""
   
    # ═══════════════════════════════════════════════════════════════════
    # 7-LAYER ARCHITECTURE
    # ═══════════════════════════════════════════════════════════════════
    layers: list[MarkdownArchitectureLayer] = field(default_factory=list)
   
    # ═══════════════════════════════════════════════════════════════════
    # BENEFITS
    # ═══════════════════════════════════════════════════════════════════
    benefits: list[MarkdownBenefitCategory] = field(default_factory=list)
   
    # ═══════════════════════════════════════════════════════════════════
    # IMPLEMENTATION ROADMAP
    # ═══════════════════════════════════════════════════════════════════
    implementation_phases: list[MarkdownImplementationPhase] = field(default_factory=list)
   
    # ═══════════════════════════════════════════════════════════════════
    # SUCCESS METRICS
    # ═══════════════════════════════════════════════════════════════════
    business_outcomes: list[MarkdownBusinessOutcome] = field(default_factory=list)
 
 
def normalize_for_markdown(
    discovery: dict[str, Any],
    knowledge: dict[str, Any],
    recommendation: dict[str, Any],
    architecture: dict[str, Any],
    validation: dict[str, Any],
    output: dict[str, Any],
) -> MarkdownBlueprint:
    """
    Normalize all agent outputs into Markdown-specific blueprint.
   
    This function receives the same agent outputs as other blueprints but
    transforms them independently for Markdown generation.
   
    Args:
        discovery: Discovery agent output
        knowledge: Knowledge agent output
        recommendation: Recommendation agent output
        architecture: Architecture agent output
        validation: Validation agent output
        output: Output agent output
   
    Returns:
        MarkdownBlueprint: Markdown-specific normalized model
    """
    from app.models.enterprise_blueprint import (
        _extract_business_domain,
        _extract_cloud_provider,
        _extract_client_name,
        _extract_industry,
        _extract_quality_score,
        _compute_architecture_status,
        _compute_confidence_level,
        _build_seven_layers,
        _build_benefits,
        _build_business_outcomes,
        _build_implementation_phases,
        _build_data_flow,
    )
   
    metadata = output.get("solution_metadata", {})
   
    blueprint = MarkdownBlueprint(
        architecture_title=metadata.get("package_title", "Enterprise Data Platform"),
        architecture_subtitle=metadata.get("solution_type", "Cloud-Native Architecture"),
        version=metadata.get("document_version", "1.0"),
        generated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        client_name=_extract_client_name(discovery),
        industry=_extract_industry(discovery),
        cloud_provider=_extract_cloud_provider(recommendation),
        architecture_status=_compute_architecture_status(validation),
        quality_score=_extract_quality_score(validation),
        confidence_level=_compute_confidence_level(validation),
        executive_summary=output.get("executive_summary", ""),
        current_state=architecture.get("current_state", ""),
        target_state=architecture.get("target_state", ""),
        transformation_approach=architecture.get("transformation_approach", ""),
        data_flow_pathway=_build_data_flow(architecture, output),
    )
   
    # Build 7-layer architecture for Markdown
    layers_data = _build_seven_layers(discovery, knowledge, recommendation, architecture, output)
    blueprint.layers = [
        _convert_layer_to_markdown(layer) for layer in layers_data
    ]
   
    # Build benefits for Markdown
    benefits_data = _build_benefits(discovery, recommendation, architecture, output)
    blueprint.benefits = [
        MarkdownBenefitCategory(
            category_name=b.category_name,
            icon=b.icon,
            benefits=b.benefits
        ) for b in benefits_data
    ]
   
    # Build business outcomes for Markdown
    outcomes_data = _build_business_outcomes(discovery, validation, output)
    blueprint.business_outcomes = [
        MarkdownBusinessOutcome(
            metric=o.metric,
            label=o.label,
            description=o.description
        ) for o in outcomes_data
    ]
   
    # Build implementation phases for Markdown
    phases_data = _build_implementation_phases(output, recommendation)
    blueprint.implementation_phases = [
        MarkdownImplementationPhase(
            phase_name=p.phase_name,
            duration=p.duration,
            deliverables=p.deliverables
        ) for p in phases_data
    ]
   
    return blueprint
 
 
def _convert_layer_to_markdown(layer: Any) -> MarkdownArchitectureLayer:
    """Convert enterprise layer to Markdown layer."""
    return MarkdownArchitectureLayer(
        layer_number=layer.layer_number,
        layer_name=layer.layer_name,
        layer_purpose=layer.layer_purpose,
        business_goal=layer.business_goal,
        business_challenge=layer.business_challenge,
        components=[
            MarkdownLayerComponent(
                title=c.title,
                purpose=c.purpose,
                technology=c.technology,
                protocols=c.protocols,
                standards=c.standards,
                inputs=c.inputs,
                outputs=c.outputs,
                data_formats=c.data_formats,
                expected_volume=c.expected_volume,
                scalability=c.scalability,
                performance=c.performance,
                monitoring=c.monitoring,
                security=c.security,
                availability=c.availability,
                disaster_recovery=c.disaster_recovery,
                business_value=c.business_value,
                operational_value=c.operational_value,
                business_owner=c.business_owner,
                business_challenges=c.business_challenges,
                key_features=c.key_features,
            ) for c in layer.components
        ]
    )
