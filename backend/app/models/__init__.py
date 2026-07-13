"""
Enterprise Architecture Models
================================
 
Normalized data models for enterprise architecture documentation.
 
Separation of Concerns:
- EnterpriseBlueprint: HTML and Overview rendering
- MarkdownBlueprint: Markdown documentation generation
- TerraformBlueprint: Terraform infrastructure code generation
 
Each blueprint is completely independent with no inheritance.
"""
 
from app.models.enterprise_blueprint import (
    EnterpriseBlueprint,
    ArchitectureLayer,
    LayerComponent,
    SecurityCheckpoint,
    BenefitCategory,
    BusinessOutcome,
    ImplementationPhase,
    RiskItem,
    CostCategory,
    normalize_agent_outputs,
)
from app.models.markdown_blueprint import (
    MarkdownBlueprint,
    MarkdownArchitectureLayer,
    MarkdownLayerComponent,
    MarkdownBenefitCategory,
    MarkdownImplementationPhase,
    MarkdownBusinessOutcome,
    normalize_for_markdown,
)
from app.models.terraform_blueprint import (
    TerraformBlueprint,
    normalize_for_terraform,
)
 
__all__ = [
    # Enterprise Blueprint (HTML + Overview)
    "EnterpriseBlueprint",
    "ArchitectureLayer",
    "LayerComponent",
    "SecurityCheckpoint",
    "BenefitCategory",
    "BusinessOutcome",
    "ImplementationPhase",
    "RiskItem",
    "CostCategory",
    "normalize_agent_outputs",
    # Markdown Blueprint
    "MarkdownBlueprint",
    "MarkdownArchitectureLayer",
    "MarkdownLayerComponent",
    "MarkdownBenefitCategory",
    "MarkdownImplementationPhase",
    "MarkdownBusinessOutcome",
    "normalize_for_markdown",
    # Terraform Blueprint
    "TerraformBlueprint",
    "normalize_for_terraform",
]
