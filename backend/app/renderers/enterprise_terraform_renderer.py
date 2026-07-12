"""
enterprise_terraform_renderer.py — Production-Ready Terraform Infrastructure Code
====================================================================================
 
Renders EnterpriseBlueprint to production-ready Terraform configuration.
 
Generates:
- Provider configuration
- Variables  
- Networking (VPC, subnets, security groups)
- IAM roles and policies
- Storage (data lake, databases)
- Compute (VMs, containers, serverless)
- Monitoring and logging
- Security controls
- Outputs
"""
 
from app.models.enterprise_blueprint import EnterpriseBlueprint
 
 
def render_terraform(blueprint: EnterpriseBlueprint) -> str:
    """
    Render Enterprise Blueprint to complete Terraform configuration.
   
    Args:
        blueprint: Normalized enterprise architecture model
   
    Returns:
        Complete Terraform configuration as string
    """
    cloud_provider = blueprint.cloud_provider.lower()
   
    sections = [
        _render_header_comment(blueprint),
        _render_provider_config(blueprint),
        _render_variables(blueprint),
        _render_networking(blueprint, cloud_provider),
        _render_iam(blueprint, cloud_provider),
        _render_storage(blueprint, cloud_provider),
        _render_compute(blueprint, cloud_provider),
        _render_monitoring(blueprint, cloud_provider),
        _render_outputs(blueprint),
    ]
   
    return "\n\n".join(filter(None, sections))
 
 
def _render_header_comment(bp: EnterpriseBlueprint) -> str:
    """Render header comments."""
    return f"""#==============================================================================
# {bp.architecture_title}
# {bp.architecture_subtitle}
#==============================================================================
#
# Generated: {bp.generated_time}
# Version: {bp.version}
# Client: {bp.client_name}
# Industry: {bp.industry}
# Cloud Provider: {bp.cloud_provider}
# Quality Score: {bp.quality_score}/100
#
# This Terraform configuration implements the enterprise architecture
# as defined in the architecture blueprint.
#
# IMPORTANT: Review and customize all resource configurations before
# applying to production environments.
#
#=============================================================================="""
 
 
def _render_provider_config(bp: EnterpriseBlueprint) -> str:
    """Render Terraform provider configuration."""
    cloud_provider = bp.cloud_provider.lower()
   
    if "azure" in cloud_provider:
        return """#------------------------------------------------------------------------------
# Azure Provider Configuration
#------------------------------------------------------------------------------
 
terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
 
  # Uncomment for remote state management
  # backend "azurerm" {
  #   resource_group_name  = "terraform-state-rg"
  #   storage_account_name = "tfstate"
  #   container_name       = "tfstate"
  #   key                  = "enterprise.tfstate"
  # }
}
 
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = true
    }
  }
}"""
   
    elif "aws" in cloud_provider:
        return """#------------------------------------------------------------------------------
# AWS Provider Configuration
#------------------------------------------------------------------------------
 
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
 
  # Uncomment for remote state management
  # backend "s3" {
  #   bucket = "terraform-state-bucket"
  #   key    = "enterprise.tfstate"
  #   region = "us-east-1"
  # }
}
 
provider "aws" {
  region = var.aws_region
 
  default_tags {
    tags = var.common_tags
  }
}"""
   
    else:  # GCP or Multi-Cloud - default to Azure
        return _render_provider_config(EnterpriseBlueprint(
            **{**bp.__dict__, 'cloud_provider': 'Microsoft Azure'}
        ))
 
 
def _render_variables(bp: EnterpriseBlueprint) -> str:
    """Render Terraform variables."""
    cloud_provider = bp.cloud_provider.lower()
   
    if "azure" in cloud_provider:
        return f"""#------------------------------------------------------------------------------
# Variables
#------------------------------------------------------------------------------
 
variable "environment" {{
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
}}
 
variable "location" {{
  description = "Azure region for resource deployment"
  type        = string
  default     = "East US"
}}
 
variable "resource_prefix" {{
  description = "Prefix for all resource names"
  type        = string
  default     = "{bp.client_name.lower().replace(' ', '-')}"
}}
 
variable "common_tags" {{
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {{
    Project     = "{bp.architecture_title}"
    Environment = "production"
    ManagedBy   = "Terraform"
    Client      = "{bp.client_name}"
    Industry    = "{bp.industry}"
  }}
}}
 
variable "vnet_address_space" {{
  description = "Address space for virtual network"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}}
 
variable "enable_monitoring" {{
  description = "Enable monitoring and logging"
  type        = bool
  default     = true
}}
 
variable "enable_backup" {{
  description = "Enable backup services"
  type        = bool
  default     = true
}}"""
   
    elif "aws" in cloud_provider:
        return f"""#------------------------------------------------------------------------------
# Variables
#------------------------------------------------------------------------------
 
variable "environment" {{
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
}}
 
variable "aws_region" {{
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}}
 
variable "resource_prefix" {{
  description = "Prefix for all resource names"
  type        = string
  default     = "{bp.client_name.lower().replace(' ', '-')}"
}}
 
variable "common_tags" {{
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {{
    Project     = "{bp.architecture_title}"
    Environment = "production"
    ManagedBy   = "Terraform"
    Client      = "{bp.client_name}"
    Industry    = "{bp.industry}"
  }}
}}
 
variable "vpc_cidr" {{
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}}
 
variable "enable_monitoring" {{
  description = "Enable CloudWatch monitoring"
  type        = bool
  default     = true
}}"""
   
    else:
        return _render_variables(EnterpriseBlueprint(
            **{**bp.__dict__, 'cloud_provider': 'Microsoft Azure'}
        ))
 
 
def _render_networking(bp: EnterpriseBlueprint, cloud_provider: str) -> str:
    """Render networking resources."""
    if "azure" in cloud_provider:
        return """#------------------------------------------------------------------------------
# Resource Group
#------------------------------------------------------------------------------
 
resource "azurerm_resource_group" "main" {
  name     = "$${var.resource_prefix}-rg"
  location = var.location
  tags     = var.common_tags
}
 
#------------------------------------------------------------------------------
# Virtual Network
#------------------------------------------------------------------------------
 
resource "azurerm_virtual_network" "main" {
  name                = "$${var.resource_prefix}-vnet"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = var.vnet_address_space
  tags                = var.common_tags
}
 
resource "azurerm_subnet" "data_services" {
  name                 = "data-services-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}
 
resource "azurerm_subnet" "compute" {
  name                 = "compute-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}
 
resource "azurerm_subnet" "analytics" {
  name                 = "analytics-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.3.0/24"]
}
 
#------------------------------------------------------------------------------
# Network Security Groups
#------------------------------------------------------------------------------
 
resource "azurerm_network_security_group" "data_services" {
  name                = "$${var.resource_prefix}-data-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = var.common_tags
 
  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "*"
  }
}
 
resource "azurerm_subnet_network_security_group_association" "data_services" {
  subnet_id                 = azurerm_subnet.data_services.id
  network_security_group_id = azurerm_network_security_group.data_services.id
}"""
   
    elif "aws" in cloud_provider:
        return """#------------------------------------------------------------------------------
# VPC and Networking
#------------------------------------------------------------------------------
 
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
 
  tags = merge(var.common_tags, {
    Name = "$${var.resource_prefix}-vpc"
  })
}
 
resource "aws_subnet" "private" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
 
  tags = merge(var.common_tags, {
    Name = "$${var.resource_prefix}-private-subnet-$${count.index + 1}"
    Type = "Private"
  })
}
 
resource "aws_subnet" "public" {
  count                   = 3
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
 
  tags = merge(var.common_tags, {
    Name = "$${var.resource_prefix}-public-subnet-$${count.index + 1}"
    Type = "Public"
  })
}
 
data "aws_availability_zones" "available" {
  state = "available"
}
 
#------------------------------------------------------------------------------
# Internet Gateway
#------------------------------------------------------------------------------
 
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
 
  tags = merge(var.common_tags, {
    Name = "$${var.resource_prefix}-igw"
  })
}
 
#------------------------------------------------------------------------------
# Security Groups
#------------------------------------------------------------------------------
 
resource "aws_security_group" "data_services" {
  name        = "$${var.resource_prefix}-data-sg"
  description = "Security group for data services"
  vpc_id      = aws_vpc.main.id
 
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }
 
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
 
  tags = merge(var.common_tags, {
    Name = "$${var.resource_prefix}-data-sg"
  })
}"""
   
    else:
        return _render_networking(bp, "azure")
 
 
def _render_iam(bp: EnterpriseBlueprint, cloud_provider: str) -> str:
    """Render IAM roles and policies."""
    if "azure" in cloud_provider:
        return """#------------------------------------------------------------------------------
# Managed Identities
#------------------------------------------------------------------------------
 
resource "azurerm_user_assigned_identity" "data_services" {
  name                = "$${var.resource_prefix}-data-identity"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = var.common_tags
}
 
resource "azurerm_role_assignment" "data_contributor" {
  scope                = azurerm_resource_group.main.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.data_services.principal_id
}"""
   
    elif "aws" in cloud_provider:
        return """#------------------------------------------------------------------------------
# IAM Roles and Policies
#------------------------------------------------------------------------------
 
resource "aws_iam_role" "data_services" {
  name = "$${var.resource_prefix}-data-services-role"
 
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
 
  tags = var.common_tags
}
 
resource "aws_iam_role_policy" "data_services" {
  name = "$${var.resource_prefix}-data-policy"
  role = aws_iam_role.data_services.id
 
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "$${aws_s3_bucket.data_lake.arn}/*"
        ]
      }
    ]
  })
}"""
   
    else:
        return _render_iam(bp, "azure")
 
 
def _render_storage(bp: EnterpriseBlueprint, cloud_provider: str) -> str:
    """Render storage resources."""
    if "azure" in cloud_provider:
        return """#------------------------------------------------------------------------------
# Data Lake Storage
#------------------------------------------------------------------------------
 
resource "azurerm_storage_account" "data_lake" {
  name                     = "$${replace(var.resource_prefix, "-", "")}lake"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true  # Enable hierarchical namespace for Data Lake
 
  blob_properties {
    versioning_enabled = true
   
    delete_retention_policy {
      days = 30
    }
  }
 
  tags = var.common_tags
}
 
resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_name  = azurerm_storage_account.data_lake.name
  container_access_type = "private"
}
 
resource "azurerm_storage_container" "silver" {
  name                  = "silver"
  storage_account_name  = azurerm_storage_account.data_lake.name
  container_access_type = "private"
}
 
resource "azurerm_storage_container" "gold" {
  name                  = "gold"
  storage_account_name  = azurerm_storage_account.data_lake.name
  container_access_type = "private"
}"""
   
    elif "aws" in cloud_provider:
        return """#------------------------------------------------------------------------------
# S3 Data Lake
#------------------------------------------------------------------------------
 
resource "aws_s3_bucket" "data_lake" {
  bucket = "$${var.resource_prefix}-data-lake"
  tags   = var.common_tags
}
 
resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
 
  versioning_configuration {
    status = "Enabled"
  }
}
 
resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
 
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
 
# Bronze layer prefix
resource "aws_s3_object" "bronze" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "bronze/"
}
 
# Silver layer prefix
resource "aws_s3_object" "silver" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "silver/"
}
 
# Gold layer prefix
resource "aws_s3_object" "gold" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "gold/"
}"""
   
    else:
        return _render_storage(bp, "azure")
 
 
def _render_compute(bp: EnterpriseBlueprint, cloud_provider: str) -> str:
    """Render compute resources."""
    if "azure" in cloud_provider:
        return """#------------------------------------------------------------------------------
# Azure Databricks Workspace (Analytics/ML Platform)
#------------------------------------------------------------------------------
 
resource "azurerm_databricks_workspace" "main" {
  name                = "$${var.resource_prefix}-databricks"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "premium"
 
  tags = var.common_tags
}
 
#------------------------------------------------------------------------------
# Azure Synapse Analytics Workspace
#------------------------------------------------------------------------------
 
resource "azurerm_synapse_workspace" "main" {
  name                                 = "$${var.resource_prefix}-synapse"
  resource_group_name                  = azurerm_resource_group.main.name
  location                             = azurerm_resource_group.main.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.synapse.id
  sql_administrator_login              = "sqladminuser"
  sql_administrator_login_password     = random_password.synapse_sql.result
 
  identity {
    type = "SystemAssigned"
  }
 
  tags = var.common_tags
}
 
resource "random_password" "synapse_sql" {
  length  = 16
  special = true
}
 
resource "azurerm_storage_data_lake_gen2_filesystem" "synapse" {
  name               = "synapse"
  storage_account_id = azurerm_storage_account.data_lake.id
}"""
   
    elif "aws" in cloud_provider:
        return """#------------------------------------------------------------------------------
# AWS EMR Cluster (Analytics Platform)
#------------------------------------------------------------------------------
 
resource "aws_emr_cluster" "main" {
  name          = "$${var.resource_prefix}-emr-cluster"
  release_label = "emr-6.10.0"
  applications  = ["Spark", "Hadoop", "Hive"]
 
  service_role = aws_iam_role.emr_service.arn
 
  ec2_attributes {
    subnet_id                         = aws_subnet.private[0].id
    emr_managed_master_security_group = aws_security_group.emr_master.id
    emr_managed_slave_security_group  = aws_security_group.emr_slave.id
    instance_profile                  = aws_iam_instance_profile.emr_ec2.arn
  }
 
  master_instance_group {
    instance_type = "m5.xlarge"
  }
 
  core_instance_group {
    instance_type  = "m5.xlarge"
    instance_count = 2
  }
 
  tags = var.common_tags
}
 
resource "aws_iam_role" "emr_service" {
  name = "$${var.resource_prefix}-emr-service-role"
 
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "elasticmapreduce.amazonaws.com"
      }
    }]
  })
}
 
resource "aws_iam_instance_profile" "emr_ec2" {
  name = "$${var.resource_prefix}-emr-ec2-profile"
  role = aws_iam_role.emr_ec2.name
}
 
resource "aws_iam_role" "emr_ec2" {
  name = "$${var.resource_prefix}-emr-ec2-role"
 
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
}
 
resource "aws_security_group" "emr_master" {
  name        = "$${var.resource_prefix}-emr-master-sg"
  vpc_id      = aws_vpc.main.id
  description = "EMR Master security group"
 
  tags = merge(var.common_tags, {
    Name = "$${var.resource_prefix}-emr-master-sg"
  })
}
 
resource "aws_security_group" "emr_slave" {
  name        = "$${var.resource_prefix}-emr-slave-sg"
  vpc_id      = aws_vpc.main.id
  description = "EMR Slave security group"
 
  tags = merge(var.common_tags, {
    Name = "$${var.resource_prefix}-emr-slave-sg"
  })
}"""
   
    else:
        return _render_compute(bp, "azure")
 
 
def _render_monitoring(bp: EnterpriseBlueprint, cloud_provider: str) -> str:
    """Render monitoring and logging resources."""
    if "azure" in cloud_provider:
        return """#------------------------------------------------------------------------------
# Log Analytics Workspace
#------------------------------------------------------------------------------
 
resource "azurerm_log_analytics_workspace" "main" {
  name                = "$${var.resource_prefix}-law"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.common_tags
}
 
#------------------------------------------------------------------------------
# Application Insights
#------------------------------------------------------------------------------
 
resource "azurerm_application_insights" "main" {
  name                = "$${var.resource_prefix}-appinsights"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.main.id
  tags                = var.common_tags
}
 
#------------------------------------------------------------------------------
# Diagnostic Settings
#------------------------------------------------------------------------------
 
resource "azurerm_monitor_diagnostic_setting" "storage" {
  name                       = "storage-diagnostics"
  target_resource_id         = azurerm_storage_account.data_lake.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
 
  enabled_log {
    category = "StorageRead"
  }
 
  enabled_log {
    category = "StorageWrite"
  }
 
  metric {
    category = "Transaction"
  }
}"""
   
    elif "aws" in cloud_provider:
        return """#------------------------------------------------------------------------------
# CloudWatch Log Groups
#------------------------------------------------------------------------------
 
resource "aws_cloudwatch_log_group" "main" {
  name              = "/aws/enterprise/$${var.resource_prefix}"
  retention_in_days = 30
  tags              = var.common_tags
}
 
#------------------------------------------------------------------------------
# CloudWatch Dashboard
#------------------------------------------------------------------------------
 
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "$${var.resource_prefix}-dashboard"
 
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/S3", "BucketSizeBytes", { stat = "Average" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Data Lake Size"
        }
      }
    ]
  })
}
 
#------------------------------------------------------------------------------
# CloudWatch Alarms
#------------------------------------------------------------------------------
 
resource "aws_cloudwatch_metric_alarm" "high_s3_usage" {
  alarm_name          = "$${var.resource_prefix}-high-s3-usage"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "BucketSizeBytes"
  namespace           = "AWS/S3"
  period              = "300"
  statistic           = "Average"
  threshold           = "1000000000000"  # 1TB
  alarm_description   = "Monitors S3 bucket size"
 
  tags = var.common_tags
}"""
   
    else:
        return _render_monitoring(bp, "azure")
 
 
def _render_outputs(bp: EnterpriseBlueprint) -> str:
    """Render Terraform outputs."""
    cloud_provider = bp.cloud_provider.lower()
   
    if "azure" in cloud_provider:
        return """#------------------------------------------------------------------------------
# Outputs
#------------------------------------------------------------------------------
 
output "resource_group_name" {
  description = "Name of the main resource group"
  value       = azurerm_resource_group.main.name
}
 
output "virtual_network_id" {
  description = "ID of the virtual network"
  value       = azurerm_virtual_network.main.id
}
 
output "data_lake_name" {
  description = "Name of the data lake storage account"
  value       = azurerm_storage_account.data_lake.name
}
 
output "databricks_workspace_url" {
  description = "URL of the Databricks workspace"
  value       = azurerm_databricks_workspace.main.workspace_url
}
 
output "synapse_workspace_name" {
  description = "Name of the Synapse workspace"
  value       = azurerm_synapse_workspace.main.name
}
 
output "log_analytics_workspace_id" {
  description = "ID of the Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.main.id
}
 
output "application_insights_instrumentation_key" {
  description = "Instrumentation key for Application Insights"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}"""
   
    elif "aws" in cloud_provider:
        return """#------------------------------------------------------------------------------
# Outputs
#------------------------------------------------------------------------------
 
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}
 
output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}
 
output "data_lake_bucket_name" {
  description = "Name of the S3 data lake bucket"
  value       = aws_s3_bucket.data_lake.id
}
 
output "emr_cluster_id" {
  description = "ID of the EMR cluster"
  value       = aws_emr_cluster.main.id
}
 
output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.main.name
}
 
output "dashboard_url" {
  description = "URL of the CloudWatch dashboard"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=$${var.aws_region}#dashboards:name=$${aws_cloudwatch_dashboard.main.dashboard_name}"
}"""
   
    else:
        return _render_outputs(EnterpriseBlueprint(
            **{**bp.__dict__, 'cloud_provider': 'Microsoft Azure'}
        ))
 