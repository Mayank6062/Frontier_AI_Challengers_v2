"""
terraform_blueprint.py — Terraform-Specific Normalization Model
==============================================================
 
Independent blueprint for Terraform infrastructure code generation.
 
This blueprint dynamically extracts ALL infrastructure components from agent outputs
and generates Terraform code based on actual recommended architecture.
 
No static templates. No hardcoded technologies.
Each infrastructure resource is generated from agent recommendations.
"""
 
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime
 
 
@dataclass
class TerraformResource:
    """Generic infrastructure resource extracted from agent outputs."""
    name: str
    resource_type: str  # network, storage, compute, database, analytics, monitoring, etc.
    category: str  # specific category like "data lake", "streaming", "warehouse"
    technology: str  # e.g., "Azure Data Lake", "AWS S3", "Kafka"
    purpose: str
    properties: dict[str, Any] = field(default_factory=dict)
 
 
@dataclass
class NetworkConfig:
    """Network configuration extracted from architecture."""
    requires_vnet: bool = False
    requires_private_endpoints: bool = False
    subnets: list[dict[str, str]] = field(default_factory=list)
 
 
@dataclass
class SecurityConfig:
    """Security configuration extracted from architecture."""
    requires_encryption: bool = True
    requires_backup: bool = False
    requires_dr: bool = False
    encryption_keys: list[str] = field(default_factory=list)
    access_policies: list[str] = field(default_factory=list)
 
 
@dataclass
class TerraformBlueprint:
    """
    Complete Terraform-specific normalization model.
   
    Dynamically extracts ALL infrastructure resources from agent outputs.
    No static templates. Generates only what agents recommend.
    """
    # ═══════════════════════════════════════════════════════════════════
    # METADATA
    # ═══════════════════════════════════════════════════════════════════
    architecture_title: str
    architecture_subtitle: str
    version: str
    generated_time: str
    client_name: str
    industry: str
    cloud_provider: str
    region: str
    environment: str
   
    # ═══════════════════════════════════════════════════════════════════
    # INFRASTRUCTURE RESOURCES (extracted from agent outputs)
    # ═══════════════════════════════════════════════════════════════════
    network_config: NetworkConfig = field(default_factory=NetworkConfig)
    security_config: SecurityConfig = field(default_factory=SecurityConfig)
   
    storage_resources: list[TerraformResource] = field(default_factory=list)
    database_resources: list[TerraformResource] = field(default_factory=list)
    compute_resources: list[TerraformResource] = field(default_factory=list)
    analytics_resources: list[TerraformResource] = field(default_factory=list)
    monitoring_resources: list[TerraformResource] = field(default_factory=list)
    iam_resources: list[TerraformResource] = field(default_factory=list)
   
    # All discovered infrastructure resources
    all_resources: list[TerraformResource] = field(default_factory=list)
 
 
def normalize_for_terraform(
    discovery: dict[str, Any],
    knowledge: dict[str, Any],
    recommendation: dict[str, Any],
    architecture: dict[str, Any],
    validation: dict[str, Any],
    output: dict[str, Any],
) -> TerraformBlueprint:
    """
    Normalize all agent outputs into Terraform-specific blueprint.
   
    Extracts ALL infrastructure resources dynamically from agent recommendations.
    No hardcoded resources. Generates only what agents recommend.
    """
    from app.models.enterprise_blueprint import (
        _extract_cloud_provider,
        _extract_client_name,
        _extract_industry,
    )
   
    metadata = output.get("solution_metadata", {})
    cloud_provider = _extract_cloud_provider(recommendation)
   
    blueprint = TerraformBlueprint(
        architecture_title=metadata.get("package_title", "Enterprise Data Platform"),
        architecture_subtitle=metadata.get("solution_type", "Cloud-Native Architecture"),
        version=metadata.get("document_version", "1.0"),
        generated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        client_name=_extract_client_name(discovery),
        industry=_extract_industry(discovery),
        cloud_provider=cloud_provider,
        region=_extract_region(recommendation, cloud_provider),
        environment="production",
    )
   
    # Extract infrastructure resources from agent outputs
    all_resources = _extract_all_resources(recommendation, architecture)
   
    # Categorize resources by type
    blueprint.storage_resources = _filter_resources(all_resources, ["storage", "data lake", "blob", "s3", "datalake"])
    blueprint.database_resources = _filter_resources(all_resources, ["database", "sql", "nosql", "warehouse", "synapse", "redshift", "snowflake"])
    blueprint.compute_resources = _filter_resources(all_resources, ["compute", "vm", "container", "kubernetes", "function", "lambda", "app service"])
    blueprint.analytics_resources = _filter_resources(all_resources, ["analytics", "databricks", "synapse", "emr", "glue", "spark"])
    blueprint.monitoring_resources = _filter_resources(all_resources, ["monitoring", "logging", "observability", "cloudwatch", "monitor"])
    blueprint.iam_resources = _filter_resources(all_resources, ["identity", "iam", "rbac", "access", "auth"])
   
    blueprint.all_resources = all_resources
   
    # Extract network configuration
    blueprint.network_config = _extract_network_config(architecture, all_resources)
   
    # Extract security configuration
    blueprint.security_config = _extract_security_config(architecture, validation)
   
    return blueprint
 
 
def _extract_region(recommendation: dict[str, Any], cloud_provider: str) -> str:
    """Extract recommended region from recommendation."""
    region = recommendation.get("region", "")
    if region:
        return region
   
    # Default regions based on cloud provider
    if "azure" in cloud_provider.lower():
        return "eastus"
    elif "aws" in cloud_provider.lower():
        return "us-east-1"
    elif "gcp" in cloud_provider.lower():
        return "us-central1"
    else:
        return "eastus"
 
 
def _extract_all_resources(recommendation: dict[str, Any], architecture: dict[str, Any]) -> list[TerraformResource]:
    """Extract all infrastructure resources from agent recommendations."""
    resources = []
   
    # Extract from recommended_products
    products = recommendation.get("recommended_products", [])
    if isinstance(products, list):
        for product in products:
            if isinstance(product, dict):
                resource = _product_to_resource(product)
                if resource:
                    resources.append(resource)
   
    # Extract from architecture layers if needed
    layers = architecture.get("layers", [])
    if isinstance(layers, list):
        for layer in layers:
            if isinstance(layer, dict):
                components = layer.get("components", [])
                for component in components:
                    if isinstance(component, dict):
                        resource = _component_to_resource(component)
                        if resource:
                            resources.append(resource)
   
    return resources
 
 
def _product_to_resource(product: dict[str, Any]) -> Optional[TerraformResource]:
    """Convert recommended product to Terraform resource."""
    name = product.get("name", product.get("technology", ""))
    if not name:
        return None
   
    category = product.get("category", "general")
    purpose = product.get("purpose", product.get("description", ""))
   
    # Determine resource type from category and name
    resource_type = _determine_resource_type(name, category)
   
    return TerraformResource(
        name=name,
        resource_type=resource_type,
        category=category,
        technology=name,
        purpose=purpose,
        properties={
            "business_value": product.get("business_value", ""),
            "integration": product.get("integration", ""),
        }
    )
 
 
def _component_to_resource(component: dict[str, Any]) -> Optional[TerraformResource]:
    """Convert architecture component to Terraform resource."""
    title = component.get("title", "")
    if not title:
        return None
   
    technology = component.get("technology", "")
    purpose = component.get("purpose", "")
   
    # Determine resource type
    resource_type = _determine_resource_type(technology, title)
   
    return TerraformResource(
        name=title,
        resource_type=resource_type,
        category=title.lower(),
        technology=technology,
        purpose=purpose,
        properties={
            "security": component.get("security", ""),
            "protocols": component.get("protocols", ""),
        }
    )
 
 
def _determine_resource_type(name: str, category: str) -> str:
    """Determine Terraform resource type from name and category."""
    text = f"{name} {category}".lower()
   
    if any(kw in text for kw in ["storage", "blob", "s3", "data lake", "datalake"]):
        return "storage"
    elif any(kw in text for kw in ["database", "sql", "postgres", "mysql", "cosmos", "dynamodb"]):
        return "database"
    elif any(kw in text for kw in ["warehouse", "synapse", "redshift", "snowflake", "bigquery"]):
        return "database"
    elif any(kw in text for kw in ["compute", "vm", "container", "kubernetes", "aks", "eks", "gke"]):
        return "compute"
    elif any(kw in text for kw in ["function", "lambda", "azure function"]):
        return "compute"
    elif any(kw in text for kw in ["analytics", "databricks", "spark", "emr", "dataproc"]):
        return "analytics"
    elif any(kw in text for kw in ["streaming", "kafka", "event hub", "kinesis", "pubsub"]):
        return "analytics"
    elif any(kw in text for kw in ["monitor", "logging", "cloudwatch", "log analytics"]):
        return "monitoring"
    elif any(kw in text for kw in ["identity", "iam", "rbac", "active directory", "cognito"]):
        return "iam"
    else:
        return "general"
 
 
def _filter_resources(resources: list[TerraformResource], keywords: list[str]) -> list[TerraformResource]:
    """Filter resources by keywords in name, category, or technology."""
    filtered = []
    for resource in resources:
        text = f"{resource.name} {resource.category} {resource.technology} {resource.resource_type}".lower()
        if any(keyword.lower() in text for keyword in keywords):
            if resource not in filtered:  # Avoid duplicates
                filtered.append(resource)
    return filtered
 
 
def _extract_network_config(architecture: dict[str, Any], resources: list[TerraformResource]) -> NetworkConfig:
    """Extract network configuration requirements."""
    config = NetworkConfig()
   
    # Check if any resources require networking
    if len(resources) > 2:
        config.requires_vnet = True
       
        # Create default subnets based on resource types
        resource_types = set(r.resource_type for r in resources)
       
        if "database" in resource_types or "storage" in resource_types:
            config.subnets.append({"name": "data-subnet", "cidr": "10.0.1.0/24", "purpose": "Data services"})
       
        if "compute" in resource_types:
            config.subnets.append({"name": "compute-subnet", "cidr": "10.0.2.0/24", "purpose": "Compute resources"})
       
        if "analytics" in resource_types:
            config.subnets.append({"name": "analytics-subnet", "cidr": "10.0.3.0/24", "purpose": "Analytics workloads"})
       
        # Default subnet if none created
        if not config.subnets:
            config.subnets.append({"name": "default-subnet", "cidr": "10.0.1.0/24", "purpose": "Default services"})
       
        config.requires_private_endpoints = True
   
    return config
 
 
def _extract_security_config(architecture: dict[str, Any], validation: dict[str, Any]) -> SecurityConfig:
    """Extract security configuration requirements."""
    config = SecurityConfig()
   
    # Check validation results for security requirements
    security_arch = architecture.get("security_architecture", "")
   
    config.requires_encryption = True  # Always enable encryption
    config.requires_backup = "backup" in security_arch.lower() or "recovery" in security_arch.lower()
    config.requires_dr = "disaster recovery" in security_arch.lower() or "dr" in security_arch.lower()
   
    # Extract security policies
    if "authentication" in security_arch.lower():
        config.access_policies.append("authentication_required")
    if "authorization" in security_arch.lower():
        config.access_policies.append("role_based_access_control")
    if "encryption" in security_arch.lower():
        config.encryption_keys.append("data_encryption_key")
   
    return config
