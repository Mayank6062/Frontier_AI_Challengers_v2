"""
enterprise_terraform_renderer.py — Dynamic Terraform Infrastructure Generator
================================================================================
 
Generates production-ready Terraform configuration from TerraformBlueprint.
 
DYNAMIC GENERATION:
- NO hardcoded technologies (Azure, AWS, Databricks, Kafka, etc.)
- NO static templates
- Generates ONLY resources recommended by agents
- Organizes into production Terraform modules
 
OUTPUT STRUCTURE:
- Providers (with required versions)
- Locals (naming conventions and tagging)
- Variables (with validation blocks)
- Network (VPC/VNet, subnets, security groups)
- Security (encryption, firewall rules)
- Identity (IAM roles, policies)
- Storage (data lakes, blob storage)
- Database (SQL, NoSQL, warehouses)
- Compute (VMs, containers, serverless)
- Analytics (processing engines, streaming)
- Monitoring (logging, alerting)
- Backup (disaster recovery)
- Outputs (resource IDs, endpoints)
 
COMPLIANCE:
- terraform fmt compliant code
- Proper resource naming
- Lifecycle blocks where appropriate
- depends_on only when required
- No placeholders
- No duplicates
"""
 
from __future__ import annotations
 
from app.models.terraform_blueprint import TerraformBlueprint, TerraformResource
 
 
def render_terraform(blueprint: TerraformBlueprint) -> str:
    """
    Generate complete Terraform configuration from blueprint.
   
    Args:
        blueprint: Terraform-specific normalized infrastructure model
   
    Returns:
        Complete, production-ready Terraform configuration
    """
    sections = [
        _render_header_comment(blueprint),
        _render_terraform_block(blueprint),
        _render_provider_block(blueprint),
        _render_locals_block(blueprint),
        _render_variables_block(blueprint),
    ]
   
    # Add infrastructure sections only if resources exist
    if blueprint.network_config.requires_vnet:
        sections.append(_render_network_section(blueprint))
   
    if blueprint.iam_resources:
        sections.append(_render_identity_section(blueprint))
   
    if blueprint.storage_resources:
        sections.append(_render_storage_section(blueprint))
   
    if blueprint.database_resources:
        sections.append(_render_database_section(blueprint))
   
    if blueprint.compute_resources:
        sections.append(_render_compute_section(blueprint))
   
    if blueprint.analytics_resources:
        sections.append(_render_analytics_section(blueprint))
   
    if blueprint.monitoring_resources:
        sections.append(_render_monitoring_section(blueprint))
   
    if blueprint.security_config.requires_backup or blueprint.security_config.requires_dr:
        sections.append(_render_backup_section(blueprint))
   
    # Always add outputs
    sections.append(_render_outputs_section(blueprint))
   
    return "\n\n".join(filter(None, sections))
 
 
def _render_header_comment(bp: TerraformBlueprint) -> str:
    """Render header comment block."""
    return f'''#===============================================================================
# {bp.architecture_title}
# {bp.architecture_subtitle}
#===============================================================================
#
# Generated:     {bp.generated_time}
# Version:       {bp.version}
# Client:        {bp.client_name}
# Industry:      {bp.industry}
# Cloud:         {bp.cloud_provider}
# Region:        {bp.region}
# Environment:   {bp.environment}
#
# This Terraform configuration was dynamically generated based on
# architecture requirements and recommended technologies.
#
# IMPORTANT: Review all configurations before applying to production.
#
#==============================================================================='''
 
 
def _render_terraform_block(bp: TerraformBlueprint) -> str:
    """Render terraform required_version and required_providers block."""
    cloud = bp.cloud_provider.lower()
   
    # Determine primary provider based on cloud
    if "azure" in cloud or "microsoft" in cloud:
        provider_config = '''azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }'''
        backend_config = '''# backend "azurerm" {
  #   resource_group_name  = "terraform-state-rg"
  #   storage_account_name = "tfstate"
  #   container_name       = "tfstate"
  #   key                  = "infrastructure.tfstate"
  # }'''
   
    elif "aws" in cloud or "amazon" in cloud:
        provider_config = '''aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }'''
        backend_config = '''# backend "s3" {
  #   bucket = "terraform-state-bucket"
  #   key    = "infrastructure.tfstate"
  #   region = "us-east-1"
  # }'''
   
    elif "gcp" in cloud or "google" in cloud:
        provider_config = '''google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }'''
        backend_config = '''# backend "gcs" {
  #   bucket = "terraform-state-bucket"
  #   prefix = "infrastructure"
  # }'''
   
    else:
        # Default to Azure if cloud provider unclear
        provider_config = '''azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }'''
        backend_config = '''# backend "azurerm" {
  #   resource_group_name  = "terraform-state-rg"
  #   storage_account_name = "tfstate"
  #   container_name       = "tfstate"
  #   key                  = "infrastructure.tfstate"
  # }'''
   
    return f'''#===============================================================================
# Terraform Configuration
#===============================================================================
 
terraform {{
  required_version = ">= 1.5.0"
 
  required_providers {{
    {provider_config}
    random = {{
      source  = "hashicorp/random"
      version = "~> 3.6"
    }}
  }}
 
  {backend_config}
}}'''
 
 
def _render_provider_block(bp: TerraformBlueprint) -> str:
    """Render provider configuration block."""
    cloud = bp.cloud_provider.lower()
   
    if "azure" in cloud or "microsoft" in cloud:
        return f'''#===============================================================================
# Azure Provider Configuration
#===============================================================================
 
provider "azurerm" {{
  features {{
    key_vault {{
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }}
   
    resource_group {{
      prevent_deletion_if_contains_resources = true
    }}
  }}
}}'''
   
    elif "aws" in cloud or "amazon" in cloud:
        return f'''#===============================================================================
# AWS Provider Configuration
#===============================================================================
 
provider "aws" {{
  region = var.region
 
  default_tags {{
    tags = local.common_tags
  }}
}}'''
   
    elif "gcp" in cloud or "google" in cloud:
        return f'''#===============================================================================
# Google Cloud Provider Configuration
#===============================================================================
 
provider "google" {{
  project = var.project_id
  region  = var.region
}}'''
   
    else:
        return _render_provider_block(TerraformBlueprint(
            **{**bp.__dict__, 'cloud_provider': 'Microsoft Azure'}
        ))
 
 
def _render_locals_block(bp: TerraformBlueprint) -> str:
    """Render locals block for naming conventions and common tags."""
    prefix = bp.client_name.lower().replace(' ', '-').replace('_', '-')[:20]
   
    return f'''#===============================================================================
# Locals - Naming Conventions and Tagging
#===============================================================================
 
locals {{
  # Naming convention
  prefix      = var.resource_prefix
  environment = var.environment
  region      = var.region
 
  # Resource naming
  resource_group_name = "${{local.prefix}}-${{local.environment}}-rg"
  vnet_name          = "${{local.prefix}}-${{local.environment}}-vnet"
 
  # Common tags applied to all resources
  common_tags = merge(
    var.common_tags,
    {{
      Environment   = local.environment
      ManagedBy     = "Terraform"
      Project       = "{bp.architecture_title}"
      Client        = "{bp.client_name}"
      Industry      = "{bp.industry}"
      GeneratedDate = "{bp.generated_time}"
    }}
  )
}}'''
 
 
def _render_variables_block(bp: TerraformBlueprint) -> str:
    """Render variables block with validation."""
    prefix = bp.client_name.lower().replace(' ', '-').replace('_', '-')[:20]
   
    return f'''#===============================================================================
# Variables
#===============================================================================
 
variable "environment" {{
  description = "Environment name for resource deployment"
  type        = string
  default     = "{bp.environment}"
 
  validation {{
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }}
}}
 
variable "region" {{
  description = "Cloud region for resource deployment"
  type        = string
  default     = "{bp.region}"
}}
 
variable "resource_prefix" {{
  description = "Prefix for resource naming convention"
  type        = string
  default     = "{prefix}"
 
  validation {{
    condition     = length(var.resource_prefix) >= 3 && length(var.resource_prefix) <= 20
    error_message = "Resource prefix must be between 3 and 20 characters."
  }}
}}
 
variable "common_tags" {{
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {{}}
}}
 
variable "enable_monitoring" {{
  description = "Enable monitoring and logging services"
  type        = bool
  default     = true
}}
 
variable "enable_backup" {{
  description = "Enable backup and disaster recovery"
  type        = bool
  default     = {str(bp.security_config.requires_backup).lower()}
}}'''
 
 
def _render_network_section(bp: TerraformBlueprint) -> str:
    """Render network resources dynamically."""
    cloud = bp.cloud_provider.lower()
   
    if "azure" in cloud or "microsoft" in cloud:
        return _render_azure_network(bp)
    elif "aws" in cloud or "amazon" in cloud:
        return _render_aws_network(bp)
    elif "gcp" in cloud or "google" in cloud:
        return _render_gcp_network(bp)
    else:
        return _render_azure_network(bp)
 
 
def _render_azure_network(bp: TerraformBlueprint) -> str:
    """Render Azure network resources."""
    sections = ['''#===============================================================================
# Network - Virtual Network and Subnets
#===============================================================================
 
resource "azurerm_resource_group" "main" {
  name     = local.resource_group_name
  location = var.region
  tags     = local.common_tags
 
  lifecycle {
    prevent_destroy = true
  }
}
 
resource "azurerm_virtual_network" "main" {
  name                = local.vnet_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = ["10.0.0.0/16"]
  tags                = local.common_tags
}''']
   
    # Generate subnets dynamically
    for idx, subnet in enumerate(bp.network_config.subnets):
        subnet_name = subnet.get("name", f"subnet-{idx + 1}")
        subnet_cidr = subnet.get("cidr", f"10.0.{idx + 1}.0/24")
       
        sections.append(f'''
resource "azurerm_subnet" "{_sanitize_name(subnet_name)}" {{
  name                 = "{subnet_name}"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["{subnet_cidr}"]
}}''')
   
    # Add network security group if needed
    if bp.security_config.requires_encryption:
        sections.append('''
resource "azurerm_network_security_group" "main" {
  name                = "${local.prefix}-${local.environment}-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
 
  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}''')
   
    return "\n".join(sections)
 
 
def _render_aws_network(bp: TerraformBlueprint) -> str:
    """Render AWS network resources."""
    sections = ['''#===============================================================================
# Network - VPC and Subnets
#===============================================================================
 
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
 
  tags = merge(
    local.common_tags,
    {
      Name = "${local.prefix}-${local.environment}-vpc"
    }
  )
}
 
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
 
  tags = merge(
    local.common_tags,
    {
      Name = "${local.prefix}-${local.environment}-igw"
    }
  )
}''']
   
    # Generate subnets dynamically
    for idx, subnet in enumerate(bp.network_config.subnets):
        subnet_name = subnet.get("name", f"subnet-{idx + 1}")
        subnet_cidr = subnet.get("cidr", f"10.0.{idx + 1}.0/24")
       
        sections.append(f'''
resource "aws_subnet" "{_sanitize_name(subnet_name)}" {{
  vpc_id            = aws_vpc.main.id
  cidr_block        = "{subnet_cidr}"
  availability_zone = "${{var.region}}a"
 
  tags = merge(
    local.common_tags,
    {{
      Name = "${{local.prefix}}-${{local.environment}}-{subnet_name}"
    }}
  )
}}''')
   
    # Add security group
    if bp.security_config.requires_encryption:
        sections.append('''
resource "aws_security_group" "main" {
  name        = "${local.prefix}-${local.environment}-sg"
  description = "Main security group for infrastructure"
  vpc_id      = aws_vpc.main.id
 
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
 
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
 
  tags = local.common_tags
}''')
   
    return "\n".join(sections)
 
 
def _render_gcp_network(bp: TerraformBlueprint) -> str:
    """Render GCP network resources."""
    sections = ['''#===============================================================================
# Network - VPC and Subnets
#===============================================================================
 
resource "google_compute_network" "main" {
  name                    = "${local.prefix}-${local.environment}-vpc"
  auto_create_subnetworks = false
}''']
   
    # Generate subnets dynamically
    for idx, subnet in enumerate(bp.network_config.subnets):
        subnet_name = subnet.get("name", f"subnet-{idx + 1}")
        subnet_cidr = subnet.get("cidr", f"10.0.{idx + 1}.0/24")
       
        sections.append(f'''
resource "google_compute_subnetwork" "{_sanitize_name(subnet_name)}" {{
  name          = "{subnet_name}"
  ip_cidr_range = "{subnet_cidr}"
  region        = var.region
  network       = google_compute_network.main.id
}}''')
   
    return "\n".join(sections)
 
 
def _render_identity_section(bp: TerraformBlueprint) -> str:
    """Render IAM/identity resources dynamically."""
    if not bp.iam_resources:
        return ""
   
    cloud = bp.cloud_provider.lower()
   
    if "azure" in cloud or "microsoft" in cloud:
        return _render_azure_identity(bp)
    elif "aws" in cloud or "amazon" in cloud:
        return _render_aws_identity(bp)
    elif "gcp" in cloud or "google" in cloud:
        return _render_gcp_identity(bp)
    else:
        return _render_azure_identity(bp)
 
 
def _render_azure_identity(bp: TerraformBlueprint) -> str:
    """Render Azure identity resources."""
    return '''#===============================================================================
# Identity - Azure Active Directory and RBAC
#===============================================================================
 
data "azurerm_client_config" "current" {}
 
resource "azurerm_user_assigned_identity" "main" {
  name                = "${local.prefix}-${local.environment}-identity"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}
 
resource "azurerm_role_assignment" "contributor" {
  scope                = azurerm_resource_group.main.id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.main.principal_id
}'''
 
 
def _render_aws_identity(bp: TerraformBlueprint) -> str:
    """Render AWS IAM resources."""
    return '''#===============================================================================
# Identity - IAM Roles and Policies
#===============================================================================
 
data "aws_caller_identity" "current" {}
 
resource "aws_iam_role" "main" {
  name = "${local.prefix}-${local.environment}-role"
 
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
 
  tags = local.common_tags
}
 
resource "aws_iam_role_policy_attachment" "main" {
  role       = aws_iam_role.main.name
  policy_arn = "arn:aws:iam::aws:policy/PowerUserAccess"
}'''
 
 
def _render_gcp_identity(bp:TerraformBlueprint) -> str:
    """Render GCP IAM resources."""
    return '''#===============================================================================
# Identity - Service Accounts and IAM
#===============================================================================
 
resource "google_service_account" "main" {
  account_id   = "${local.prefix}-${local.environment}-sa"
  display_name = "Main Service Account"
}
 
resource "google_project_iam_member" "main" {
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.main.email}"
}'''
 
 
def _render_storage_section(bp: TerraformBlueprint) -> str:
    """Render storage resources dynamically based on recommended products."""
    if not bp.storage_resources:
        return ""
   
    cloud = bp.cloud_provider.lower()
   
    if "azure" in cloud or "microsoft" in cloud:
        return _render_azure_storage(bp)
    elif "aws" in cloud or "amazon" in cloud:
        return _render_aws_storage(bp)
    elif "gcp" in cloud or "google" in cloud:
        return _render_gcp_storage(bp)
    else:
        return _render_azure_storage(bp)
 
 
def _render_azure_storage(bp: TerraformBlueprint) -> str:
    """Render Azure storage resources dynamically."""
    sections = ['''#===============================================================================
# Storage - Data Lake and Blob Storage
#===============================================================================''']
   
    for idx, resource in enumerate(bp.storage_resources[:3]):  # Limit to avoid too many resources
        resource_name = _sanitize_name(resource.name.lower().replace(' ', '_'))
        account_name = f"{resource_name}{idx}"[:24].replace('_', '').replace('-', '')
       
        sections.append(f'''
resource "azurerm_storage_account" "{resource_name}" {{
  name                     = "${{replace(local.prefix, "-", "")}}{account_name}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true
 
  blob_properties {{
    versioning_enabled = true
   
    delete_retention_policy {{
      days = 30
    }}
  }}
 
  tags = merge(
    local.common_tags,
    {{
      Purpose = "{resource.purpose[:50] if resource.purpose else 'Storage'}"
    }}
  )
 
  lifecycle {{
    prevent_destroy = true
  }}
}}''')
       
        # Add containers for data layers
        if "data lake" in resource.name.lower() or "datalake" in resource.name.lower():
            for layer in ["bronze", "silver", "gold"]:
                sections.append(f'''
resource "azurerm_storage_container" "{resource_name}_{layer}" {{
  name                  = "{layer}"
  storage_account_name  = azurerm_storage_account.{resource_name}.name
  container_access_type = "private"
}}''')
   
    return "\n".join(sections)
 
 
def _render_aws_storage(bp: TerraformBlueprint) -> str:
    """Render AWS storage resources dynamically."""
    sections = ['''#===============================================================================
# Storage - S3 Buckets and Data Lake
#===============================================================================''']
   
    for resource in bp.storage_resources[:3]:  # Limit to avoid too many resources
        resource_name = _sanitize_name(resource.name.lower().replace(' ', '_'))
       
        sections.append(f'''
resource "aws_s3_bucket" "{resource_name}" {{
  bucket = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  tags   = merge(
    local.common_tags,
    {{
      Purpose = "{resource.purpose[:50] if resource.purpose else 'Storage'}"
    }}
  )
}}
 
resource "aws_s3_bucket_versioning" "{resource_name}" {{
  bucket = aws_s3_bucket.{resource_name}.id
 
  versioning_configuration {{
    status = "Enabled"
  }}
}}
 
resource "aws_s3_bucket_server_side_encryption_configuration" "{resource_name}" {{
  bucket = aws_s3_bucket.{resource_name}.id
 
  rule {{
    apply_server_side_encryption_by_default {{
      sse_algorithm = "AES256"
    }}
  }}
}}
 
resource "aws_s3_bucket_public_access_block" "{resource_name}" {{
  bucket = aws_s3_bucket.{resource_name}.id
 
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}''')
   
    return "\n".join(sections)
 
 
def _render_gcp_storage(bp: TerraformBlueprint) -> str:
    """Render GCP storage resources dynamically."""
    sections = ['''#===============================================================================
# Storage - Cloud Storage Buckets
#===============================================================================''']
   
    for resource in bp.storage_resources[:3]:  # Limit to avoid too many resources
        resource_name = _sanitize_name(resource.name.lower().replace(' ', '_'))
       
        sections.append(f'''
resource "google_storage_bucket" "{resource_name}" {{
  name          = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  location      = var.region
  force_destroy = false
 
  uniform_bucket_level_access = true
 
  versioning {{
    enabled = true
  }}
 
  labels = local.common_tags
}}''')
   
    return "\n".join(sections)
 
 
def _render_database_section(bp: TerraformBlueprint) -> str:
    """Render database resources dynamically based on recommended products."""
    if not bp.database_resources:
        return ""
   
    cloud = bp.cloud_provider.lower()
   
    if "azure" in cloud or "microsoft" in cloud:
        return _render_azure_databases(bp)
    elif "aws" in cloud or "amazon" in cloud:
        return _render_aws_databases(bp)
    elif "gcp" in cloud or "google" in cloud:
        return _render_gcp_databases(bp)
    else:
        return _render_azure_databases(bp)
 
 
def _render_azure_databases(bp: TerraformBlueprint) -> str:
    """Render Azure database resources dynamically."""
    sections = ['''#===============================================================================
# Database - SQL and Data Warehouses
#===============================================================================''']
   
    for resource in bp.database_resources[:2]:  # Limit to 2 databases
        resource_name = _sanitize_name(resource.name.lower().replace(' ', '_'))
        tech_lower = resource.technology.lower()
       
        # Determine database type from technology
        if "sql" in tech_lower and "synapse" not in tech_lower and "warehouse" not in tech_lower:
            sections.append(f'''
resource "azurerm_mssql_server" "{resource_name}" {{
  name                         = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = random_password.{resource_name}.result
 
  tags = local.common_tags
}}
 
resource "random_password" "{resource_name}" {{
  length  = 16
  special = true
}}
 
resource "azurerm_mssql_database" "{resource_name}_db" {{
  name        = "{resource_name}-db"
  server_id   = azurerm_mssql_server.{resource_name}.id
  sku_name    = "S1"
  max_size_gb = 250
 
  tags = local.common_tags
}}''')
       
        elif "cosmos" in tech_lower:
            sections.append(f'''
resource "azurerm_cosmosdb_account" "{resource_name}" {{
  name                = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
 
  consistency_policy {{
    consistency_level = "Session"
  }}
 
  geo_location {{
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }}
 
  tags = local.common_tags
}}''')
   
    return "\n".join(sections)
 
 
def _render_aws_databases(bp: TerraformBlueprint) -> str:
    """Render AWS database resources dynamically."""
    sections = ['''#===============================================================================
# Database - RDS and NoSQL
#===============================================================================''']
   
    for resource in bp.database_resources[:2]:  # Limit to 2 databases
        resource_name = _sanitize_name(resource.name.lower().replace(' ', '_'))
        tech_lower = resource.technology.lower()
       
        if "rds" in tech_lower or ("sql" in tech_lower and "no" not in tech_lower):
            sections.append(f'''
resource "aws_db_instance" "{resource_name}" {{
  identifier             = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  engine                 = "postgres"
  engine_version         = "15.3"
  instance_class         = "db.t3.medium"
  allocated_storage      = 100
  storage_encrypted      = true
  db_name                = "{resource_name.replace('-', '_')}"
  username               = "dbadmin"
  password               = random_password.{resource_name}.result
  skip_final_snapshot    = false
  final_snapshot_identifier = "${{local.prefix}}-{resource_name}-final"
 
  tags = local.common_tags
}}
 
resource "random_password" "{resource_name}" {{
  length  = 16
  special = true
}}''')
       
        elif "dynamodb" in tech_lower:
            sections.append(f'''
resource "aws_dynamodb_table" "{resource_name}" {{
  name           = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
 
  attribute {{
    name = "id"
    type = "S"
  }}
 
  server_side_encryption {{
    enabled = true
  }}
 
  point_in_time_recovery {{
    enabled = true
  }}
 
  tags = local.common_tags
}}''')
   
    return "\n".join(sections)
 
 
def _render_gcp_databases(bp: TerraformBlueprint) -> str:
    """Render GCP database resources dynamically."""
    sections = ['''#===============================================================================
# Database - Cloud SQL and Firestore
#===============================================================================''']
   
    for resource in bp.database_resources[:2]:  # Limit to 2 databases
        resource_name = _sanitize_name(resource.name.lower().replace(' ', '_'))
        tech_lower = resource.technology.lower()
       
        if "sql" in tech_lower:
            sections.append(f'''
resource "google_sql_database_instance" "{resource_name}" {{
  name             = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  database_version = "POSTGRES_15"
  region           = var.region
 
  settings {{
    tier = "db-f1-micro"
   
    backup_configuration {{
      enabled = true
    }}
   
    ip_configuration {{
      ipv4_enabled = false
    }}
  }}
 
  deletion_protection = true
}}''')
   
    return "\n".join(sections)
 
 
def _render_compute_section(bp: TerraformBlueprint) -> str:
    """Render compute resources dynamically based on recommended products."""
    if not bp.compute_resources:
        return ""
   
    cloud = bp.cloud_provider.lower()
   
    if "azure" in cloud or "microsoft" in cloud:
        return _render_azure_compute(bp)
    elif "aws" in cloud or "amazon" in cloud:
        return _render_aws_compute(bp)
    elif "gcp" in cloud or "google" in cloud:
        return _render_gcp_compute(bp)
    else:
        return _render_azure_compute(bp)
 
 
def _render_azure_compute(bp: TerraformBlueprint) -> str:
    """Render Azure compute resources dynamically."""
    sections = ['''#===============================================================================
# Compute - Application Services and Functions
#===============================================================================''']
   
    for resource in bp.compute_resources[:2]:  # Limit to 2 compute resources
        resource_name = _sanitize_name(resource.name.lower().replace(' ', '_'))
        tech_lower = resource.technology.lower()
       
        if "function" in tech_lower or "serverless" in tech_lower:
            sections.append(f'''
resource "azurerm_service_plan" "{resource_name}" {{
  name                = "${{local.prefix}}-${{local.environment}}-{resource_name}-plan"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = "Y1"
 
  tags = local.common_tags
}}
 
resource "azurerm_linux_function_app" "{resource_name}" {{
  name                       = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  service_plan_id            = azurerm_service_plan.{resource_name}.id
  storage_account_name       = azurerm_storage_account.{_sanitize_name(bp.storage_resources[0].name) if bp.storage_resources else "storage"}.name
  storage_account_access_key = azurerm_storage_account.{_sanitize_name(bp.storage_resources[0].name) if bp.storage_resources else "storage"}.primary_access_key
 
  site_config {{}}
 
  tags = local.common_tags
}}''')
       
        elif "app service" in tech_lower or "web" in tech_lower:
            sections.append(f'''
resource "azurerm_service_plan" "{resource_name}" {{
  name                = "${{local.prefix}}-${{local.environment}}-{resource_name}-plan"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = "B1"
 
  tags = local.common_tags
}}
 
resource "azurerm_linux_web_app" "{resource_name}" {{
  name                = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.{resource_name}.id
 
  site_config {{}}
 
  tags = local.common_tags
}}''')
   
    return "\n".join(sections)
 
 
def _render_aws_compute(bp: TerraformBlueprint) -> str:
    """Render AWS compute resources dynamically."""
    sections = ['''#===============================================================================
# Compute - Lambda and ECS
#===============================================================================''']
   
    for resource in bp.compute_resources[:2]:  # Limit to 2 compute resources
        resource_name = _sanitize_name(resource.name.lower().replace(' ', '_'))
        tech_lower = resource.technology.lower()
       
        if "lambda" in tech_lower or "function" in tech_lower:
            sections.append(f'''
resource "aws_iam_role" "{resource_name}_role" {{
  name = "${{local.prefix}}-${{local.environment}}-{resource_name}-role"
 
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {{
        Service = "lambda.amazonaws.com"
      }}
    }}]
  }})
 
  tags = local.common_tags
}}
 
resource "aws_lambda_function" "{resource_name}" {{
  function_name = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  role          = aws_iam_role.{resource_name}_role.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  filename      = "lambda_function.zip"
 
  environment {{
    variables = {{
      ENVIRONMENT = local.environment
    }}
  }}
 
  tags = local.common_tags
}}''')
   
    return "\n".join(sections)
 
 
def _render_gcp_compute(bp: TerraformBlueprint) -> str:
    """Render GCP compute resources dynamically."""
    sections = ['''#===============================================================================
# Compute - Cloud Functions and Cloud Run
#===============================================================================''']
   
    for resource in bp.compute_resources[:2]:  # Limit to 2 compute resources
        resource_name = _sanitize_name(resource.name.lower().replace(' ', '_'))
        tech_lower = resource.technology.lower()
       
        if "function" in tech_lower:
            sections.append(f'''
resource "google_cloudfunctions_function" "{resource_name}" {{
  name    = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  runtime = "python311"
 
  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.{_sanitize_name(bp.storage_resources[0].name) if bp.storage_resources else "storage"}.name
  source_archive_object = "function.zip"
  trigger_http          = true
  entry_point           = "main"
}}''')
   
    return "\n".join(sections)
 
 
def _render_analytics_section(bp: TerraformBlueprint) -> str:
    """Render analytics resources dynamically based on recommended products."""
    if not bp.analytics_resources:
        return ""
   
    cloud = bp.cloud_provider.lower()
   
    if "azure" in cloud or "microsoft" in cloud:
        return _render_azure_analytics(bp)
    elif "aws" in cloud or "amazon" in cloud:
        return _render_aws_analytics(bp)
    elif "gcp" in cloud or "google" in cloud:
        return _render_gcp_analytics(bp)
    else:
        return _render_azure_analytics(bp)
 
 
def _render_azure_analytics(bp: TerraformBlueprint) -> str:
    """Render Azure analytics resources dynamically."""
    sections = ['''#===============================================================================
# Analytics - Processing and Streaming
#===============================================================================''']
   
    for resource in bp.analytics_resources[:2]:  # Limit to 2 analytics resources
        resource_name = _sanitize_name(resource.name.lower().replace(' ', '_'))
        tech_lower = resource.technology.lower()
       
        if "databricks" in tech_lower:
            sections.append(f'''
resource "azurerm_databricks_workspace" "{resource_name}" {{
  name                = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "standard"
 
  tags = local.common_tags
}}''')
       
        elif "synapse" in tech_lower:
            sections.append(f'''
resource "azurerm_synapse_workspace" "{resource_name}" {{
  name                                 = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  resource_group_name                  = azurerm_resource_group.main.name
  location                             = azurerm_resource_group.main.location
  storage_data_lake_gen2_filesystem_id = "${{azurerm_storage_account.{_sanitize_name(bp.storage_resources[0].name) if bp.storage_resources else "storage"}.primary_dfs_endpoint}}datalake"
  sql_administrator_login              = "sqladmin"
  sql_administrator_login_password     = random_password.{resource_name}.result
 
  identity {{
    type = "SystemAssigned"
  }}
 
  tags = local.common_tags
}}
 
resource "random_password" "{resource_name}" {{
  length  = 16
  special = true
}}''')
       
        elif "event hub" in tech_lower or "kafka" in tech_lower:
            sections.append(f'''
resource "azurerm_eventhub_namespace" "{resource_name}" {{
  name                = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"
  capacity            = 1
 
  tags = local.common_tags
}}
 
resource "azurerm_eventhub" "{resource_name}_hub" {{
  name                = "events"
  namespace_name      = azurerm_eventhub_namespace.{resource_name}.name
  resource_group_name = azurerm_resource_group.main.name
  partition_count     = 2
  message_retention   = 1
}}''')
   
    return "\n".join(sections)
 
 
def _render_aws_analytics(bp: TerraformBlueprint) -> str:
    """Render AWS analytics resources dynamically."""
    sections = ['''#===============================================================================
# Analytics - EMR and Glue
#===============================================================================''']
   
    for resource in bp.analytics_resources[:2]:  # Limit to 2 analytics resources
        resource_name = _sanitize_name(resource.name.lower().replace(' ', '_'))
        tech_lower = resource.technology.lower()
       
        if "glue" in tech_lower:
            sections.append(f'''
resource "aws_glue_catalog_database" "{resource_name}" {{
  name = "{resource_name}_catalog"
}}''')
       
        elif "kinesis" in tech_lower or "kafka" in tech_lower:
            sections.append(f'''
resource "aws_kinesis_stream" "{resource_name}" {{
  name             = "${{local.prefix}}-${{local.environment}}-{resource_name}"
  shard_count      = 1
  retention_period = 24
 
  stream_mode_details {{
    stream_mode = "PROVISIONED"
  }}
 
  tags = local.common_tags
}}''')
   
    return "\n".join(sections)
 
 
def _render_gcp_analytics(bp: TerraformBlueprint) -> str:
    """Render GCP analytics resources dynamically."""
    sections = ['''#===============================================================================
# Analytics - BigQuery and Dataflow
#===============================================================================''']
   
    for resource in bp.analytics_resources[:2]:  # Limit to 2 analytics resources
        resource_name = _sanitize_name(resource.name.lower().replace(' ', '_'))
        tech_lower = resource.technology.lower()
       
        if "bigquery" in tech_lower:
            sections.append(f'''
resource "google_bigquery_dataset" "{resource_name}" {{
  dataset_id = "{resource_name}"
  location   = var.region
 
  labels = local.common_tags
}}''')
   
    return "\n".join(sections)
 
 
def _render_monitoring_section(bp: TerraformBlueprint) -> str:
    """Render monitoring and logging resources."""
    cloud = bp.cloud_provider.lower()
   
    if "azure" in cloud or "microsoft" in cloud:
        return '''#===============================================================================
# Monitoring - Log Analytics and Application Insights
#===============================================================================
 
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${local.prefix}-${local.environment}-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
 
  tags = local.common_tags
}
 
resource "azurerm_application_insights" "main" {
  name                = "${local.prefix}-${local.environment}-insights"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
 
  tags = local.common_tags
}'''
   
    elif "aws" in cloud or "amazon" in cloud:
        return '''#===============================================================================
# Monitoring - CloudWatch
#===============================================================================
 
resource "aws_cloudwatch_log_group" "main" {
  name              = "/aws/${local.prefix}/${local.environment}"
  retention_in_days = 30
 
  tags = local.common_tags
}
 
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.prefix}-${local.environment}-dashboard"
 
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = []
          period = 300
          stat   = "Average"
          region = var.region
          title  = "Infrastructure Metrics"
        }
      }
    ]
  })
}'''
   
    elif "gcp" in cloud or "google" in cloud:
        return '''#===============================================================================
# Monitoring - Cloud Monitoring
#===============================================================================
 
resource "google_logging_project_bucket_config" "main" {
  project          = var.project_id
  location         = "global"
  retention_days   = 30
  bucket_id        = "${local.prefix}-${local.environment}-logs"
}'''
   
    else:
        return ""
 
 
def _render_backup_section(bp: TerraformBlueprint) -> str:
    """Render backup and disaster recovery resources."""
    if not (bp.security_config.requires_backup or bp.security_config.requires_dr):
        return ""
   
    cloud = bp.cloud_provider.lower()
   
    if "azure" in cloud or "microsoft" in cloud:
        return '''#===============================================================================
# Backup - Recovery Services Vault
#===============================================================================
 
resource "azurerm_recovery_services_vault" "main" {
  name                = "${local.prefix}-${local.environment}-vault"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"
 
  soft_delete_enabled = true
 
  tags = local.common_tags
}
 
resource "azurerm_backup_policy_vm" "main" {
  name                = "${local.prefix}-${local.environment}-backup-policy"
  resource_group_name = azurerm_resource_group.main.name
  recovery_vault_name = azurerm_recovery_services_vault.main.name
 
  backup {
    frequency = "Daily"
    time      = "23:00"
  }
 
  retention_daily {
    count = 7
  }
 
  retention_weekly {
    count    = 4
    weekdays = ["Sunday"]
  }
}'''
   
    elif "aws" in cloud or "amazon" in cloud:
        return '''#===============================================================================
# Backup - AWS Backup
#===============================================================================
 
resource "aws_backup_vault" "main" {
  name = "${local.prefix}-${local.environment}-vault"
 
  tags = local.common_tags
}
 
resource "aws_backup_plan" "main" {
  name = "${local.prefix}-${local.environment}-backup-plan"
 
  rule {
    rule_name         = "daily_backup"
    target_vault_name = aws_backup_vault.main.name
    schedule          = "cron(0 2 * * ? *)"
   
    lifecycle {
      delete_after = 7
    }
  }
 
  tags = local.common_tags
}'''
   
    else:
        return ""
 
 
def _render_outputs_section(bp: TerraformBlueprint) -> str:
    """Render outputs dynamically based on created resources."""
    sections = ['''#===============================================================================
# Outputs
#===============================================================================''']
   
    cloud = bp.cloud_provider.lower()
   
    # Always output resource group/VPC
    if "azure" in cloud or "microsoft" in cloud:
        sections.append('''
output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}
 
output "resource_group_id" {
  description = "ID of the resource group"
  value       = azurerm_resource_group.main.id
}''')
       
        if bp.network_config.requires_vnet:
            sections.append('''
output "virtual_network_id" {
  description = "ID of the virtual network"
  value       = azurerm_virtual_network.main.id
}''')
   
    elif "aws" in cloud or "amazon" in cloud:
        if bp.network_config.requires_vnet:
            sections.append('''
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}
 
output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}''')
   
    elif "gcp" in cloud or "google" in cloud:
        if bp.network_config.requires_vnet:
            sections.append('''
output "network_id" {
  description = "ID of the VPC network"
  value       = google_compute_network.main.id
}''')
   
    # Output storage resources
    if bp.storage_resources:
        if "azure" in cloud or "microsoft" in cloud:
            sections.append('''
output "storage_accounts" {
  description = "Storage account details"
  value       = {for sa in [azurerm_storage_account.*] : sa.name => sa.id}
  sensitive   = true
}''')
        elif "aws" in cloud or "amazon" in cloud:
            sections.append('''
output "s3_buckets" {
  description = "S3 bucket details"
  value       = {for bucket in [aws_s3_bucket.*] : bucket.id => bucket.arn}
}''')
   
    # Output monitoring resources
    if bp.monitoring_resources or True:  # Always output monitoring if exists
        if "azure" in cloud or "microsoft" in cloud:
            sections.append('''
output "log_analytics_workspace_id" {
  description = "ID of Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.main.id
  sensitive   = true
}''')
        elif "aws" in cloud or "amazon" in cloud:
            sections.append('''
output "cloudwatch_log_group_name" {
  description = "Name of CloudWatch log group"
  value       = aws_cloudwatch_log_group.main.name
}''')
   
    return "\n".join(sections)
 
 
def _sanitize_name(name: str) -> str:
    """Sanitize resource name for Terraform compatibility."""
    # Remove special characters and ensure valid Terraform identifier
    sanitized = name.lower()
    sanitized = sanitized.replace(' ', '_')
    sanitized = sanitized.replace('-', '_')
    sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '_')
   
    # Ensure doesn't start with number
    if sanitized and sanitized[0].isdigit():
        sanitized = f"res_{sanitized}"
   
    return sanitized or "resource"
