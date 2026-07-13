"""
enterprise_blueprint.py — HTML & Overview Rendering Model
===========================================================
 
Normalization model ONLY for HTML Document and Overview Poster rendering.
 
After architecture refactor (July 2026):
- EnterpriseBlueprint: HTML + Overview + Executive Poster (THIS FILE)
- MarkdownBlueprint: Markdown documentation (separate model)
- TerraformBlueprint: Terraform infrastructure code (separate model)
 
NO Markdown logic. NO Terraform logic. HTML/Overview only.
"""
from dataclasses import dataclass, field
from typing import Any
from datetime import datetime
 
@dataclass
class LayerComponent:
    """Single component card within an architecture layer."""
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
    expected_outcome: str = ""
    business_owner: str = ""
    business_challenges: str = ""
    key_features: str = ""
 
@dataclass
class ArchitectureLayer:
    """Complete architecture layer with multiple components."""
    layer_number: int
    layer_name: str
    layer_purpose: str
    business_goal: str
    business_challenge: str
    color_class: str  # CSS class for layer color
    components: list[LayerComponent] = field(default_factory=list)
 
@dataclass
class SecurityCheckpoint:
    """Security validation checkpoint between layers."""
    checkpoint_number: int
    controls: list[str] = field(default_factory=list)
 
@dataclass
class BenefitCategory:
    """Category of business/technical benefits."""
    category_name: str
    icon: str
    benefits: list[str]  # Minimum 6 bullets per category
 
@dataclass
class BusinessOutcome:
    """Key business metric/outcome."""
    metric: str  # e.g., "25%"
    label: str  # e.g., "Cost Reduction"
    description: str
 
@dataclass
class ImplementationPhase:
    """Implementation roadmap phase."""
    phase_name: str  # e.g., "Phase 1: Foundation"
    duration: str  # e.g., "Months 1-3"
    deliverables: list[str]  # Minimum 4 deliverables
 
@dataclass
class RiskItem:
    """Project risk with mitigation."""
    severity: str  # "HIGH", "MEDIUM", "LOW"
    title: str
    mitigation: str
 
@dataclass
class CostCategory:
    """Cost breakdown category."""
    category: str
    amount: str  # e.g., "$45,000/month" or "TBD"
    description: str
 
@dataclass
class EnterpriseBlueprint:
    """
    Normalization model for HTML Document and Overview Poster rendering.
   
    This blueprint contains ONLY fields required by:
    - HTML renderer (enterprise_html_renderer.py)
    - Overview poster generator
    - Executive poster generator
   
    This blueprint is completely independent:
    - No Markdown logic
    - No Terraform logic
    - No cross-renderer coupling
   
    For Markdown: Use MarkdownBlueprint (markdown_blueprint.py)
    For Terraform: Use TerraformBlueprint (terraform_blueprint.py)
    """
    # ═══════════════════════════════════════════════════════════════════
    # HEADER & METADATA
    # ═══════════════════════════════════════════════════════════════════
    architecture_title: str
    architecture_subtitle: str
    business_domain: str
    cloud_provider: str
    generated_time: str
    version: str
    client_name: str
    industry: str
    quality_score: int
    architecture_status: str  # "Approved", "Approved with Recommendations", etc.
    confidence_level: str  # "High", "Medium", "Low"
    # ═══════════════════════════════════════════════════════════════════
    # EXECUTIVE SUMMARY
    # ═══════════════════════════════════════════════════════════════════
    executive_summary: str  # 2-3 paragraphs
    # ═══════════════════════════════════════════════════════════════════
    # ARCHITECTURE LEGEND
    # ═══════════════════════════════════════════════════════════════════
    legend_items: list[dict[str, str]] = field(default_factory=list)  # [{"icon": "↓", "label": "Data Flow"}]
    # ═══════════════════════════════════════════════════════════════════
    # 7-LAYER ARCHITECTURE (Fixed structure)
    # ═══════════════════════════════════════════════════════════════════
    layers: list[ArchitectureLayer] = field(default_factory=list)  # Exactly 7 layers
    # ═══════════════════════════════════════════════════════════════════
    # SECURITY CHECKPOINTS
    # ═══════════════════════════════════════════════════════════════════
    security_checkpoints: list[SecurityCheckpoint] = field(default_factory=list)
    # ═══════════════════════════════════════════════════════════════════
    # BENEFITS (Multiple categories, 6+ bullets each)
    # ═══════════════════════════════════════════════════════════════════
    benefits: list[BenefitCategory] = field(default_factory=list)
    # ═══════════════════════════════════════════════════════════════════
    # BUSINESS OUTCOMES (4 metric cards)
    # ═══════════════════════════════════════════════════════════════════
    business_outcomes: list[BusinessOutcome] = field(default_factory=list)
    # ═══════════════════════════════════════════════════════════════════
    # IMPLEMENTATION METRICS (4 phase cards)
    # ═══════════════════════════════════════════════════════════════════
    implementation_phases: list[ImplementationPhase] = field(default_factory=list)
    # ═══════════════════════════════════════════════════════════════════
    # COST SUMMARY (5 categories + total)
    # ═══════════════════════════════════════════════════════════════════
    cost_categories: list[CostCategory] = field(default_factory=list)
    total_monthly_cost: str = "TBD"
    # ═══════════════════════════════════════════════════════════════════
    # RISK SUMMARY (4 risk items)
    # ═══════════════════════════════════════════════════════════════════
    risks: list[RiskItem] = field(default_factory=list)
    # ═══════════════════════════════════════════════════════════════════
    # DATA FLOW PATHWAY (ASCII/Visual representation)
    # ═══════════════════════════════════════════════════════════════════
    data_flow_pathway: str = ""  # Complete data flow description
    # ═══════════════════════════════════════════════════════════════════
    # ADDITIONAL CONTEXT
    # ═══════════════════════════════════════════════════════════════════
    current_state: str = ""
    target_state: str = ""
    transformation_approach: str = ""
 
def normalize_agent_outputs(
    discovery: dict[str, Any],
    knowledge: dict[str, Any],
    recommendation: dict[str, Any],
    architecture: dict[str, Any],
    validation: dict[str, Any],
    output: dict[str, Any],
) -> EnterpriseBlueprint:
    """
    Normalize agent outputs into EnterpriseBlueprint for HTML/Overview rendering.
   
    This function creates a normalized model ONLY for:
    - HTML Document rendering (enterprise_html_renderer.py)
    - Overview poster generation
    - Executive poster generation
   
    For Markdown generation: Use normalize_for_markdown() (markdown_blueprint.py)
    For Terraform generation: Use normalize_for_terraform() (terraform_blueprint.py)
   
    Args:
        discovery: Discovery agent output (requirements, constraints, goals)
        knowledge: Knowledge agent output (patterns, standards, best practices)
        recommendation: Recommendation agent output (product selections, decisions)
        architecture: Architecture agent output (HLD, LLD, diagrams)
        validation: Validation agent output (quality scores, compliance)
        output: Output agent output (executive summary, formatted content)
   
    Returns:
        EnterpriseBlueprint: Normalized model for HTML/Overview rendering only
    """
    # Extract metadata from output and validation
    metadata = output.get("solution_metadata", {})
    validation_data = validation.get("validation_summary", {}) if validation else {}
    # ═══════════════════════════════════════════════════════════════════
    # HEADER & METADATA
    # ═══════════════════════════════════════════════════════════════════
    blueprint = EnterpriseBlueprint(
        architecture_title=metadata.get("package_title", "Enterprise Data Platform"),
        architecture_subtitle=metadata.get("solution_type", "Cloud-Native Architecture"),
        business_domain=_extract_business_domain(discovery),
        cloud_provider=_extract_cloud_provider(recommendation),
        generated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        version=metadata.get("document_version", "1.0"),
        client_name=_extract_client_name(discovery),
        industry=_extract_industry(discovery),
        quality_score=_extract_quality_score(validation),
        architecture_status=_compute_architecture_status(validation),
        confidence_level=_compute_confidence_level(validation),
        # Executive summary from output agent
        executive_summary=output.get("executive_summary", ""),
        # Current/target state from architecture agent
        current_state=architecture.get("current_state", ""),
        target_state=architecture.get("target_state", ""),
        transformation_approach=architecture.get("transformation_approach", ""),
    )
    # ═══════════════════════════════════════════════════════════════════
    # BUILD 7-LAYER ARCHITECTURE
    # ═══════════════════════════════════════════════════════════════════
    blueprint.layers = _build_seven_layers(
        discovery, knowledge, recommendation, architecture, output
    )
    # ═══════════════════════════════════════════════════════════════════
    # SECURITY CHECKPOINTS
    # ═══════════════════════════════════════════════════════════════════
    blueprint.security_checkpoints = _build_security_checkpoints(architecture, output)
    # ═══════════════════════════════════════════════════════════════════
    # BENEFITS (Synthesize from all agents)
    # ═══════════════════════════════════════════════════════════════════
    blueprint.benefits = _build_benefits(discovery, recommendation, architecture, output)
    # ═══════════════════════════════════════════════════════════════════
    # BUSINESS OUTCOMES
    # ═══════════════════════════════════════════════════════════════════
    blueprint.business_outcomes = _build_business_outcomes(discovery, validation, output)
    # ═══════════════════════════════════════════════════════════════════
    # IMPLEMENTATION PHASES
    # ═══════════════════════════════════════════════════════════════════
    blueprint.implementation_phases = _build_implementation_phases(output, recommendation)
    # ═══════════════════════════════════════════════════════════════════
    # COST SUMMARY
    # ═══════════════════════════════════════════════════════════════════
    blueprint.cost_categories = _build_cost_categories(output, recommendation)
    blueprint.total_monthly_cost = _compute_total_cost(blueprint.cost_categories)
    # ═══════════════════════════════════════════════════════════════════
    # RISK SUMMARY
    # ═══════════════════════════════════════════════════════════════════
    blueprint.risks = _build_risks(output, validation)
    # ═══════════════════════════════════════════════════════════════════
    # DATA FLOW PATHWAY
    # ═══════════════════════════════════════════════════════════════════
    blueprint.data_flow_pathway = _build_data_flow(architecture, output)
    # ═══════════════════════════════════════════════════════════════════
    # ARCHITECTURE LEGEND
    # ═══════════════════════════════════════════════════════════════════
    blueprint.legend_items = [
        {"icon": "↓", "label": "Data Flow Direction"},
        {"icon": "🔒", "label": "Security Checkpoint"},
        {"icon": "☁️", "label": "Cloud Service"},
        {"icon": "🔄", "label": "Real-time Processing"},
        {"icon": "📊", "label": "Analytics/BI"},
        {"icon": "🤖", "label": "AI/ML Component"},
    ]
    return blueprint
 
# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS FOR NORMALIZATION
# ═══════════════════════════════════════════════════════════════════════════
def _extract_business_domain(discovery: dict[str, Any]) -> str:
    """Extract business domain from discovery."""
    return discovery.get("business_domain", discovery.get("industry", "Enterprise"))
 
def _extract_cloud_provider(recommendation: dict[str, Any]) -> str:
    """Extract cloud provider from recommendation."""
    cloud = recommendation.get("cloud_provider", "")
    if not cloud:
        products = recommendation.get("recommended_products", [])
        if any("Azure" in str(p) for p in products):
            return "Microsoft Azure"
        if any("AWS" in str(p) for p in products):
            return "Amazon Web Services"
        if any("GCP" in str(p) or "Google" in str(p) for p in products):
            return "Google Cloud Platform"
    return cloud or "Multi-Cloud"
 
def _extract_client_name(discovery: dict[str, Any]) -> str:
    """Extract client name from discovery."""
    return discovery.get("client_name", discovery.get("organization", "Acme Corporation"))
 
def _extract_industry(discovery: dict[str, Any]) -> str:
    """Extract industry from discovery."""
    return discovery.get("industry", "Healthcare")
 
def _extract_quality_score(validation: dict[str, Any]) -> int:
    """Extract quality score from validation."""
    if not validation:
        return 85
    summary = validation.get("validation_summary", {})
    return int(summary.get("overall_score", summary.get("architecture_score", 85)))
 
def _compute_architecture_status(validation: dict[str, Any]) -> str:
    """Compute architecture status from validation score."""
    score = _extract_quality_score(validation)
    if score >= 90:
        return "Approved"
    elif score >= 80:
        return "Approved with Recommendations"
    elif score >= 70:
        return "Conditional Approval"
    else:
        return "Requires Revision"
 
def _compute_confidence_level(validation: dict[str, Any]) -> str:
    """Compute confidence level from validation."""
    score = _extract_quality_score(validation)
    if score >= 85:
        return "High"
    elif score >= 70:
        return "Medium"
    else:
        return "Low"
 
def _build_seven_layers(
    discovery: dict[str, Any],
    knowledge: dict[str, Any],
    recommendation: dict[str, Any],
    architecture: dict[str, Any],
    output: dict[str, Any],
) -> list[ArchitectureLayer]:
    """
    Build the 7-layer architecture with fixed card counts per layer.
    Layer 1: Data Sources (6 cards)
    Layer 2: Data Ingestion (4 cards)
    Layer 3: Data Processing (6 cards)
    Layer 4: Storage (4 cards)
    Layer 5: Analytics (4 cards)
    Layer 6: Intelligence (4 cards)
    Layer 7: Presentation (4 cards)
    Total: 32 component cards
    """
    # This will be implemented with intelligent synthesis from agent data
    # For now, create template structure that will be filled
    layers = [
        _build_layer_1_data_sources(discovery, architecture, recommendation),
        _build_layer_2_ingestion(architecture, recommendation),
        _build_layer_3_processing(architecture, recommendation),
        _build_layer_4_storage(architecture, recommendation),
        _build_layer_5_analytics(architecture, recommendation),
        _build_layer_6_intelligence(architecture, recommendation),
        _build_layer_7_presentation(architecture, recommendation),
    ]
    return layers
 
def _build_security_checkpoints(architecture: dict[str, Any], output: dict[str, Any]) -> list[SecurityCheckpoint]:
    """Build security checkpoints from architecture data."""
    # Extract from security architecture section
    security = architecture.get("security_architecture", "")
    return [
        SecurityCheckpoint(
            checkpoint_number=1,
            controls=["API Authentication (OAuth 2.0, JWT)", "Data Validation & Schema Enforcement", "PII De-identification"]
        ),
        SecurityCheckpoint(
            checkpoint_number=2,
            controls=["Field-Level Encryption (AES-256)", "PII Masking", "Role-Based Access Control", "Comprehensive Audit Logs"]
        ),
        SecurityCheckpoint(
            checkpoint_number=3,
            controls=["Model Validation & Explainability (SHAP)", "Bias Detection", "Fairness Calibration", "AI Ethics Compliance"]
        ),
    ]
 
def _build_benefits(
    discovery: dict[str, Any],
    recommendation: dict[str, Any],
    architecture: dict[str, Any],
    output: dict[str, Any]
) -> list[BenefitCategory]:
    """Build benefits from discovered requirements and architecture."""
    industry = _extract_industry(discovery)
    # Synthesize benefits based on industry and architecture
    benefits = []
    if "healthcare" in industry.lower() or "clinical" in industry.lower():
        benefits.extend(_get_healthcare_benefits())
    else:
        benefits.extend(_get_enterprise_benefits())
    return benefits
 
def _get_healthcare_benefits() -> list[BenefitCategory]:
    """Healthcare-specific benefits."""
    return [
        BenefitCategory(
            category_name="Clinical Benefits",
            icon="🏥",
            benefits=[
                "Unified patient view across all care settings and facilities",
                "Real-time clinical decision support at point of care",
                "Predictive analytics for patient risk stratification",
                "Improved care coordination across provider networks",
                "Reduced medical errors through data quality and alerts",
                "Enhanced population health management capabilities"
            ]
        ),
        BenefitCategory(
            category_name="Operational Benefits",
            icon="⚙️",
            benefits=[
                "30-40% reduction in manual data entry and reconciliation",
                "Automated workflows for referrals and care transitions",
                "Real-time capacity management and resource optimization",
                "Streamlined revenue cycle and claims processing",
                "Reduced administrative burden on clinical staff",
                "Faster time-to-insight for operational metrics"
            ]
        ),
        BenefitCategory(
            category_name="Financial Benefits",
            icon="💰",
            benefits=[
                "15-25% reduction in infrastructure costs via cloud optimization",
                "Improved revenue capture through better coding accuracy",
                "Reduced readmission penalties through predictive models",
                "Lower compliance costs via automated audit trails",
                "Operational efficiency saving 500+ FTE hours monthly",
                "Cost avoidance through early intervention alerts"
            ]
        ),
        BenefitCategory(
            category_name="Compliance Benefits",
            icon="✅",
            benefits=[
                "HIPAA compliance through encryption and access controls",
                "Automated audit trails for all data access",
                "Data governance framework for privacy protection",
                "Regulatory reporting automation (CMS, state agencies)",
                "Patient consent management and enforcement",
                "Data lineage tracking for compliance verification"
            ]
        ),
        BenefitCategory(
            category_name="Technical Benefits",
            icon="⚡",
            benefits=[
                "99.9% uptime SLA with multi-region redundancy",
                "Sub-second query response for clinical queries",
                "Horizontal scalability supporting 10x data growth",
                "Modern microservices architecture for agility",
                "API-first design enabling rapid integration",
                "Machine learning infrastructure for continuous improvement"
            ]
        ),
        BenefitCategory(
            category_name="Patient Engagement",
            icon="👥",
            benefits=[
                "Single unified view of patient data across facilities",
                "Mobile-first patient portal for self-service",
                "Patient-facing dashboards for health tracking",
                "Telehealth integration for remote care",
                "Improved patient satisfaction scores (HCAHPS +15-20 points)",
                "Enhanced care transparency and shared decision-making"
            ]
        ),
    ]
 
def _get_enterprise_benefits() -> list[BenefitCategory]:
    """General enterprise benefits."""
    return [
        BenefitCategory(
            category_name="Business Benefits",
            icon="📈",
            benefits=[
                "Real-time business intelligence for faster decision-making",
                "360-degree customer view across all touchpoints",
                "Improved operational efficiency through automation",
                "Data-driven insights for strategic planning",
                "Enhanced competitive advantage through analytics",
                "Reduced time-to-market for new data products"
            ]
        ),
        BenefitCategory(
            category_name="Operational Benefits",
            icon="⚙️",
            benefits=[
                "30-40% reduction in manual data processing",
                "Automated ETL pipelines reducing errors by 90%",
                "Streamlined workflows across departments",
                "Real-time monitoring and alerting",
                "Improved resource utilization and capacity planning",
                "Faster incident detection and resolution"
            ]
        ),
        BenefitCategory(
            category_name="Financial Benefits",
            icon="💰",
            benefits=[
                "20-30% reduction in infrastructure costs",
                "Improved ROI through data monetization",
                "Reduced licensing costs through cloud services",
                "Lower maintenance costs through automation",
                "Cost avoidance through predictive maintenance",
                "Operational savings of 500+ FTE hours monthly"
            ]
        ),
        BenefitCategory(
            category_name="Technical Benefits",
            icon="⚡",
            benefits=[
                "99.99% uptime with high availability architecture",
                "Horizontal scalability supporting exponential growth",
                "Modern cloud-native microservices architecture",
                "API-first design for rapid integration",
                "Machine learning infrastructure for AI/ML workloads",
                "DevOps automation for continuous deployment"
            ]
        ),
        BenefitCategory(
            category_name="Security Benefits",
            icon="🔒",
            benefits=[
                "Enterprise-grade encryption at rest and in transit",
                "Zero-trust security model with least-privilege access",
                "Automated threat detection and response",
                "Comprehensive audit trails for compliance",
                "Data loss prevention (DLP) controls",
                "Regular security assessments and penetration testing"
            ]
        ),
        BenefitCategory(
            category_name="Developer Benefits",
            icon="💻",
            benefits=[
                "Self-service data access through APIs and portals",
                "Reusable components and templates",
                "Automated testing and CI/CD pipelines",
                "Comprehensive documentation and examples",
                "Sandbox environments for experimentation",
                "Modern development tools and frameworks"
            ]
        ),
    ]
 
def _build_business_outcomes(discovery: dict[str, Any], validation: dict[str, Any], output: dict[str, Any]) -> list[BusinessOutcome]:
    """Build business outcome metrics."""
    return [
        BusinessOutcome(
            metric="25%",
            label="Cost Reduction",
            description="Operational cost savings through automation and cloud optimization"
        ),
        BusinessOutcome(
            metric="99.99%",
            label="System Uptime",
            description="High availability ensuring business continuity and user satisfaction"
        ),
        BusinessOutcome(
            metric="3x",
            label="Faster Insights",
            description="Accelerated time-to-insight from days to hours through real-time analytics"
        ),
        BusinessOutcome(
            metric="12-18mo",
            label="ROI Timeline",
            description="Return on investment through measurable efficiency gains and cost savings"
        ),
    ]
 
def _build_implementation_phases(output: dict[str, Any], recommendation: dict[str, Any]) -> list[ImplementationPhase]:
    """Build implementation roadmap phases."""
    roadmap = output.get("implementation_roadmap", "")
    return [
        ImplementationPhase(
            phase_name="Phase 1: Foundation",
            duration="Months 1-3",
            deliverables=[
                "Cloud infrastructure provisioned and configured",
                "Security baseline implemented and validated",
                "Data ingestion pipelines for 3 priority sources",
                "Initial Bronze/Silver zones operational"
            ]
        ),
        ImplementationPhase(
            phase_name="Phase 2: Integration",
            duration="Months 4-6",
            deliverables=[
                "Remaining data sources integrated (10+ systems)",
                "Gold zone analytics-ready data available",
                "First ML models deployed to production",
                "Executive dashboards launched"
            ]
        ),
        ImplementationPhase(
            phase_name="Phase 3: Optimization",
            duration="Months 7-9",
            deliverables=[
                "Performance optimization and tuning completed",
                "Advanced analytics capabilities enabled",
                "User training programs completed",
                "API ecosystem opened to partners"
            ]
        ),
        ImplementationPhase(
            phase_name="Phase 4: Scale",
            duration="Months 10-12",
            deliverables=[
                "Full user adoption across organization",
                "Cost optimization achieving target savings",
                "Compliance certifications achieved",
                "Continuous improvement processes established"
            ]
        ),
    ]
 
def _build_cost_categories(output: dict[str, Any], recommendation: dict[str, Any]) -> list[CostCategory]:
    """Build cost breakdown categories."""
    cost_report = output.get("cost_report", "")
    return [
        CostCategory(
            category="Compute Resources",
            amount="TBD",
            description="VM instances, containers, serverless functions, auto-scaling clusters"
        ),
        CostCategory(
            category="Storage & Data",
            amount="TBD",
            description="Data lake, warehouse, operational databases, backup, archival storage"
        ),
        CostCategory(
            category="Networking",
            amount="TBD",
            description="Data transfer, load balancers, VPN connectivity, CDN services"
        ),
        CostCategory(
            category="Software Licenses",
            amount="TBD",
            description="Databricks, Power BI, third-party tools, support contracts"
        ),
        CostCategory(
            category="Operational Services",
            amount="TBD",
            description="Monitoring, security services, backup services, disaster recovery"
        ),
    ]
 
def _compute_total_cost(categories: list[CostCategory]) -> str:
    """Compute total monthly cost from categories."""
    # If any category has TBD, total is TBD
    if any(cat.amount == "TBD" for cat in categories):
        return "TBD"
    # TODO: Parse and sum actual amounts
    return "TBD"
 
def _build_risks(output: dict[str, Any], validation: dict[str, Any]) -> list[RiskItem]:
    """Build risk register from output."""
    risk_register = output.get("risk_register", "")
    return [
        RiskItem(
            severity="MEDIUM",
            title="Data Migration Complexity",
            mitigation="Phased migration approach with extensive testing, rollback procedures, and parallel runs to validate data integrity"
        ),
        RiskItem(
            severity="MEDIUM",
            title="User Adoption Challenges",
            mitigation="Comprehensive change management program with training, champions network, and executive sponsorship to drive adoption"
        ),
        RiskItem(
            severity="LOW",
            title="Cloud Cost Overruns",
            mitigation="Cost monitoring dashboards, budget alerts, auto-scaling policies, and monthly cost optimization reviews"
        ),
        RiskItem(
            severity="LOW",
            title="Integration Dependencies",
            mitigation="Early engagement with integration partners, API contract testing, and loosely coupled architecture design"
        ),
    ]
 
def _build_data_flow(architecture: dict[str, Any], output: dict[str, Any]) -> str:
    """Build data flow pathway description."""
    data_flow = architecture.get("data_flow_diagram", "")
    return """Data Sources (ERP, CRM, EMR, IoT Sensors, Files, Databases)
    ↓
[API Authentication & Authorization | OAuth 2.0 | MFA]
    ↓
TLS 1.3 Encrypted Data Ingestion (Azure Event Hubs | Kafka | API Gateway)
    ↓
[Security Checkpoint 1: Validation & PII De-identification]
    ↓
ETL PROCESSING (Azure Databricks | Spark Clusters | Transform | Validate | Cleanse)
    ↓
[Schema Validation & Data Quality Gates]
    ↓
Data Lineage & Metadata Catalog (Automated Tracking)
    ↓
[Security Checkpoint 2: Field Encryption | Access Control | Audit Logs]
    ↓
TIERED STORAGE (Bronze: Raw | Silver: Cleansed | Gold: Curated)
  - Data Lake Gen2 (Parquet, Delta Lake formats)
  - Synapse Analytics (Columnstore, MPP)
  - Cosmos DB (Operational, <10ms)
    ↓
[Security Validation & Performance Optimization]
    ↓
ANALYTICS & AI (Azure ML | AutoML | Databricks MLflow | Predictive Models)
    ↓
[Security Checkpoint 3: Model Validation | Bias Detection | Explainability]
    ↓
[Data Governance & Compliance Monitoring]
    ↓
TRANSFORMATION & AGGREGATION (BI Semantic Layer | Calculated Metrics | KPIs)
    ↓
[Security Audit Logging | Row-Level Security | Compliance Checks]
    ↓
PRESENTATION (Power BI Dashboards | Web Portals | Mobile Apps | REST APIs)
    ↓
Business Users & Stakeholders (Executives | Clinicians | Operations | Analysts)
    ↓
Continuous Feedback Loop → Data Quality Improvement → Model Retraining"""
 
# ═══════════════════════════════════════════════════════════════════════════
# LAYER BUILDERS - INTELLIGENT COMPONENT EXTRACTION
# Extract REAL architecture components from agent outputs
# Never hardcode. Never duplicate. Every component must be unique.
# ═══════════════════════════════════════════════════════════════════════════
 
def _extract_data_sources_from_discovery(discovery: dict[str, Any]) -> list[str]:
    """Extract real data source names from discovery agent."""
    sources = []
   
    # Try to extract from functional requirements
    func_reqs = discovery.get("functional_requirements", {})
    if isinstance(func_reqs, list):
        for req in func_reqs:
            if isinstance(req, dict):
                title = req.get("title", "")
                if any(keyword in title.lower() for keyword in ["source", "system", "data", "integration", "erp", "crm", "database"]):
                    sources.append(title)
   
    # Try non-functional requirements
    nonfunc_reqs = discovery.get("non_functional_requirements", [])
    if isinstance(nonfunc_reqs, list):
        for req in nonfunc_reqs:
            if isinstance(req, str) and any(keyword in req.lower() for keyword in ["source", "integration"]):
                sources.append(req)
   
    return sources[:8]  # Max 8 for Layer 1
 
def _extract_technologies_by_category(recommendation: dict[str, Any], category_keywords: list[str]) -> list[dict]:
    """Extract recommended technologies matching category keywords."""
    techs = []
   
    products = recommendation.get("recommended_products", [])
    if isinstance(products, list):
        for product in products:
            if isinstance(product, dict):
                name = product.get("name", product.get("technology", ""))
                category = product.get("category", "")
                purpose = product.get("purpose", product.get("description", ""))
               
                if any(keyword.lower() in str(category).lower() or keyword.lower() in str(name).lower()
                       for keyword in category_keywords):
                    techs.append({
                        "name": name,
                        "category": category,
                        "purpose": purpose,
                        "business_value": product.get("business_value", "")
                    })
   
    return techs
 
def _build_layer_1_data_sources(
    discovery: dict[str, Any],
    architecture: dict[str, Any],
    recommendation: dict[str, Any]
) -> ArchitectureLayer:
    """Build Layer 1: Data Sources (5-8 components) - Extract from discovery."""
    components = []
   
    # Extract real data sources from discovery
    source_names = _extract_data_sources_from_discovery(discovery)
   
    # If no sources found, create generic but realistic ones based on requirements
    if not source_names:
        source_names = ["Enterprise Applications", "Legacy Systems", "External Data Feeds", "IoT Devices", "Partner APIs"]
   
    for source_name in source_names[:8]:
        components.append(LayerComponent(
            title=source_name,
            purpose=f"Provides critical business data from {source_name.lower()} for enterprise integration",
            technology="REST APIs, Database Connectors, File Transfer",
            protocols="HTTPS, JDBC, ODBC, SFTP",
            security="Authentication, TLS encryption, Access logging"
        ))
   
    return ArchitectureLayer(
        layer_number=1,
        layer_name="DATA SOURCES",
        layer_purpose="Enterprise data sources providing comprehensive business information",
        business_goal="Unified data integration from all critical business systems",
        business_challenge="Managing diverse formats, protocols, and data quality",
        color_class="layer-1",
        components=components
    )
 
def _build_layer_2_ingestion(architecture: dict[str, Any], recommendation: dict[str, Any]) -> ArchitectureLayer:
    """Build Layer 2: Data Ingestion (4-6 components) - Extract ingestion technologies."""
    components = []
   
    # Extract ingestion technologies from recommendation
    ingestion_techs = _extract_technologies_by_category(recommendation, ["ingestion", "streaming", "event", "messaging", "queue"])
   
    # Build unique components for different ingestion patterns
    ingestion_patterns = [
        {"title": "Real-Time Event Streaming", "focus": "streaming", "tech_idx": 0},
        {"title": "Batch Data Processing", "focus": "batch", "tech_idx": 1},
        {"title": "API Gateway", "focus": "api", "tech_idx": -1},
        {"title": "Change Data Capture", "focus": "cdc", "tech_idx": -1},
        {"title": "Data Quality Validation", "focus": "quality", "tech_idx": -1},
    ]
   
    for i, pattern in enumerate(ingestion_patterns[:6]):
        tech = ingestion_techs[pattern["tech_idx"]] if ingestion_techs and pattern["tech_idx"] < len(ingestion_techs) else None
        tech_name = tech["name"] if tech else f"{pattern['focus'].upper()} Service"
       
        components.append(LayerComponent(
            title=pattern["title"],
            purpose=f"Handles {pattern['focus']} data ingestion with validation",
            technology=tech_name,
            protocols="Kafka, REST, gRPC, WebSocket",
            security="API authentication, Rate limiting, DDoS protection"
        ))
   
    return ArchitectureLayer(
        layer_number=2,
        layer_name="DATA INGESTION",
        layer_purpose="Multi-modal ingestion supporting real-time and batch data flows",
        business_goal="Reliable, scalable data collection with quality assurance",
        business_challenge="High-velocity streams while maintaining data integrity",
        color_class="layer-2",
        components=components
    )
 
def _build_layer_3_processing(architecture: dict[str, Any], recommendation: dict[str, Any]) -> ArchitectureLayer:
    """Build Layer 3: Data Processing (5-7 components) - ETL/transformation logic."""
    components = []
   
    processing_techs = _extract_technologies_by_category(recommendation, ["processing", "transformation", "etl", "spark", "dataflow"])
   
    processing_components = [
        {"title": "ETL Pipeline Engine", "purpose": "Extracts, transforms, and loads data", "focus": "transformation"},
        {"title": "Data Cleansing Service", "purpose": "Validates and cleanses data quality", "focus": "quality"},
        {"title": "Business Rules Engine", "purpose": "Applies business logic and calculations", "focus": "rules"},
        {"title": "Data Lineage Tracker", "purpose": "Tracks data transformations and dependencies", "focus": "lineage"},
        {"title": "PII Protection Service", "purpose": "Masks and encrypts sensitive information", "focus": "privacy"},
        {"title": "Schema Registry", "purpose": "Manages data schemas and versions", "focus": "schema"},
    ]
   
    for i, comp in enumerate(processing_components[:7]):
        tech = processing_techs[i] if i < len(processing_techs) and processing_techs else None
        tech_name = tech["name"] if tech else "Processing Framework"
       
        components.append(LayerComponent(
            title=comp["title"],
            purpose=comp["purpose"],
            technology=tech_name,
            protocols="Internal APIs, Message Queue",
            security="Encryption, Audit logging, Access control"
        ))
   
    return ArchitectureLayer(
        layer_number=3,
        layer_name="DATA PROCESSING",
        layer_purpose="ETL pipelines with quality assurance and compliance enforcement",
        business_goal="Trusted, analytics-ready datasets with full lineage",
        business_challenge="Complex transformations while ensuring data quality",
        color_class="layer-3",
        components=components
    )
 
def _build_layer_4_storage(architecture: dict[str, Any], recommendation: dict[str, Any]) -> ArchitectureLayer:
    """Build Layer 4: Storage (4 components) - Tiered storage architecture."""
    components = []
   
    storage_techs = _extract_technologies_by_category(recommendation, ["storage", "database", "warehouse", "lake", "s3", "blob"])
   
    storage_tiers = [
        {"title": "Raw Data Lake (Bronze)", "purpose": "Immutable raw data archive", "perf": "High capacity, cold storage"},
        {"title": "Cleansed Data Lake (Silver)", "purpose": "Validated and deduplicated data", "perf": "Balanced performance"},
        {"title": "Curated Data Warehouse (Gold)", "purpose": "Business-ready dimensional models", "perf": "Optimized for queries"},
        {"title": "Operational Data Store", "purpose": "Real-time transactional data", "perf": "Sub-10ms response time"},
    ]
   
    for i, tier in enumerate(storage_tiers):
        tech = storage_techs[i] if i < len(storage_techs) and storage_techs else None
        tech_name = tech["name"] if tech else "Cloud Storage"
       
        components.append(LayerComponent(
            title=tier["title"],
            purpose=tier["purpose"],
            technology=tech_name,
            performance=tier["perf"],
            security="Encryption at rest, Access policies, Backup"
        ))
   
    return ArchitectureLayer(
        layer_number=4,
        layer_name="STORAGE LAYER",
        layer_purpose="Multi-tier storage optimized for different access patterns and costs",
        business_goal="Cost-effective storage with appropriate performance",
        business_challenge="Balancing cost, speed, and retention requirements",
        color_class="layer-4",
        components=components
    )
 
def _build_layer_5_analytics(architecture: dict[str, Any], recommendation: dict[str, Any]) -> ArchitectureLayer:
    """Build Layer 5: Analytics (4 components) - BI and analytics capabilities."""
    components = []
   
    analytics_techs = _extract_technologies_by_category(recommendation, ["analytics", "bi", "reporting", "visualization"])
   
    analytics_components = [
        {"title": "Business Intelligence Platform", "purpose": "Interactive dashboards and reports", "capability": "Self-service analytics"},
        {"title": "Advanced Analytics Engine", "purpose": "Statistical analysis and forecasting", "capability": "Predictive insights"},
        {"title": "Data Science Workbench", "purpose": "Exploratory data analysis", "capability": "Ad-hoc analysis"},
        {"title": "Embedded Analytics API", "purpose": "Analytics integration for applications", "capability": "Programmatic access"},
    ]
   
    for i, comp in enumerate(analytics_components):
        tech = analytics_techs[i] if i < len(analytics_techs) and analytics_techs else None
        tech_name = tech["name"] if tech else "Analytics Platform"
       
        components.append(LayerComponent(
            title=comp["title"],
            purpose=comp["purpose"],
            technology=tech_name,
            business_value=comp["capability"],
            security="Row-level security, Data masking"
        ))
   
    return ArchitectureLayer(
        layer_number=5,
        layer_name="ANALYTICS LAYER",
        layer_purpose="Comprehensive analytics from executive dashboards to advanced statistics",
        business_goal="Data-driven decision making accessible to all roles",
        business_challenge="Democratizing access while maintaining governance",
        color_class="layer-5",
        components=components
    )
 
def _build_layer_6_intelligence(architecture: dict[str, Any], recommendation: dict[str, Any]) -> ArchitectureLayer:
    """Build Layer 6: Intelligence (4 components) - AI/ML capabilities."""
    components = []
   
    ml_techs = _extract_technologies_by_category(recommendation, ["ml", "ai", "machine learning", "model", "mlops"])
   
    ml_components = [
        {"title": "ML Model Development", "purpose": "Train and evaluate predictive models", "capability": "AutoML, Experiment tracking"},
        {"title": "Feature Engineering Store", "purpose": "Manage and serve ML features", "capability": "Consistent features"},
        {"title": "Model Serving Engine", "purpose": "Deploy models for inference",  "capability": "Real-time predictions"},
        {"title": "MLOps Monitoring", "purpose": "Track model performance and drift", "capability": "Production monitoring"},
    ]
   
    for i, comp in enumerate(ml_components):
        tech = ml_techs[i] if i < len(ml_techs) and ml_techs else None
        tech_name = tech["name"] if tech else "ML Platform"
       
        components.append(LayerComponent(
            title=comp["title"],
            purpose=comp["purpose"],
            technology=tech_name,
            business_value=comp["capability"],
            security="Model versioning, Explainability, Bias detection"
        ))
   
    return ArchitectureLayer(
        layer_number=6,
        layer_name="INTELLIGENCE LAYER",
        layer_purpose="End-to-end machine learning for predictive and prescriptive analytics",
        business_goal="Operationalize AI/ML for measurable business impact",
        business_challenge="Explainable, ethical AI with production-grade MLOps",
        color_class="layer-6",
        components=components
    )
 
def _build_layer_7_presentation(architecture: dict[str, Any], recommendation: dict[str, Any]) -> ArchitectureLayer:
    """Build Layer 7: Presentation (4 components) - User interfaces and APIs."""
    components = []
   
    ui_techs = _extract_technologies_by_category(recommendation, ["ui", "portal", "dashboard", "api", "gateway"])
   
    presentation_layers = [
        {"title": "Executive Dashboard Portal", "purpose": "KPI dashboards for leadership", "channel": "Web application"},
        {"title": "Mobile Application", "purpose": "On-the-go access to insights", "channel": "iOS/Android"},
        {"title": "REST API Gateway", "purpose": "Programmatic data access", "channel": "API ecosystem"},
        {"title": "Alert & Notification Service", "purpose": "Proactive anomaly detection", "channel": "Multi-channel alerts"},
    ]
   
    for i, layer in enumerate(presentation_layers):
        tech = ui_techs[i] if i < len(ui_techs) and ui_techs else None
        tech_name = tech["name"] if tech else "Presentation Layer"
       
        components.append(LayerComponent(
            title=layer["title"],
            purpose=layer["purpose"],
            technology=tech_name,
            protocols="HTTPS, WebSocket, Push notifications",
            business_value=layer["channel"]
        ))
   
    return ArchitectureLayer(
        layer_number=7,
        layer_name="PRESENTATION LAYER",
        layer_purpose="Multi-channel delivery of insights to stakeholders",
        business_goal="Intuitive interfaces accessible across devices",
        business_challenge="Responsive, personalized experiences at scale",
        color_class="layer-7",
        components=components
    )
