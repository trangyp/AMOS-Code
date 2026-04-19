# Multi-Region AMOS Equation System Deployment
# Provides DR capability and global latency optimization

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "amos-terraform-state-multi-region"
    key            = "multi-region/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "amos-terraform-locks"
  }
}

# Primary Region Provider
provider "aws" {
  alias  = "primary"
  region = var.primary_region
}

# Secondary Region Provider
provider "aws" {
  alias  = "secondary"
  region = var.secondary_region
}

# Global Route53 Provider
provider "aws" {
  alias  = "dns"
  region = "us-east-1"  # Route53 is global
}

# Primary Region Infrastructure
module "primary_region" {
  source = "../modules/amos-app"
  providers = {
    aws = aws.primary
  }

  environment     = var.environment
  app_name        = "amos-equation"
  vpc_cidr        = var.primary_vpc_cidr
  cluster_name    = "${var.environment}-primary"
  is_primary      = true

  # Database - Primary RDS
  db_instance_class = var.db_instance_class
  db_name           = var.db_name
  db_username       = var.db_username
  db_password       = var.db_password

  # ElastiCache - Primary Redis
  redis_node_type = var.redis_node_type

  # ECS Configuration
  ecs_task_cpu    = var.ecs_task_cpu
  ecs_task_memory = var.ecs_task_memory
  app_image       = var.app_image
  app_count       = var.primary_app_count

  tags = {
    Region      = var.primary_region
    Role        = "primary"
    MultiRegion = "true"
  }
}

# Secondary Region Infrastructure
module "secondary_region" {
  source = "../modules/amos-app"
  providers = {
    aws = aws.secondary
  }

  environment     = var.environment
  app_name        = "amos-equation"
  vpc_cidr        = var.secondary_vpc_cidr
  cluster_name    = "${var.environment}-secondary"
  is_primary      = false

  # Database - Read Replica
  db_instance_class = var.db_instance_class
  db_name           = var.db_name
  db_username       = var.db_username
  db_password       = var.db_password
  replicate_source_db = module.primary_region.db_instance_arn

  # ElastiCache - Standalone (not replicated)
  redis_node_type = var.redis_node_type

  # ECS Configuration
  ecs_task_cpu    = var.ecs_task_cpu
  ecs_task_memory = var.ecs_task_memory
  app_image       = var.app_image
  app_count       = var.secondary_app_count

  tags = {
    Region      = var.secondary_region
    Role        = "secondary"
    MultiRegion = "true"
  }
}

# Global Accelerator for Multi-Region Traffic Management
resource "aws_globalaccelerator_accelerator" "amos" {
  provider         = aws.dns
  name             = "amos-${var.environment}"
  ip_address_type  = "IPV4"
  enabled          = true

  attributes {
    flow_logs_enabled   = true
    flow_logs_s3_bucket = aws_s3_bucket.flow_logs.id
    flow_logs_s3_prefix = "global-accelerator/"
  }
}

resource "aws_globalaccelerator_listener" "https" {
  provider        = aws.dns
  accelerator_arn = aws_globalaccelerator_accelerator.amos.id
  client_affinity = "SOURCE_IP"
  protocol        = "TCP"

  port_range {
    from_port = 443
    to_port   = 443
  }
}

# Primary Region Endpoint Group
resource "aws_globalaccelerator_endpoint_group" "primary" {
  provider       = aws.dns
  listener_arn   = aws_globalaccelerator_listener.https.id
  endpoint_group_region = var.primary_region

  health_check_protocol          = "HTTPS"
  health_check_port             = 443
  health_check_path             = "/health/ready"
  health_check_interval_seconds = 30
  threshold_count               = 2

  traffic_dial_percentage = var.primary_traffic_percentage

  endpoint_configuration {
    endpoint_id                    = module.primary_region.alb_arn
    weight                        = var.primary_weight
    client_ip_preservation_enabled = true
  }
}

# Secondary Region Endpoint Group
resource "aws_globalaccelerator_endpoint_group" "secondary" {
  provider       = aws.dns
  listener_arn   = aws_globalaccelerator_listener.https.id
  endpoint_group_region = var.secondary_region

  health_check_protocol          = "HTTPS"
  health_check_port             = 443
  health_check_path             = "/health/ready"
  health_check_interval_seconds = 30
  threshold_count               = 2

  traffic_dial_percentage = var.secondary_traffic_percentage

  endpoint_configuration {
    endpoint_id                    = module.secondary_region.alb_arn
    weight                        = var.secondary_weight
    client_ip_preservation_enabled = true
  }
}

# Route53 Health Checks for DNS Failover
resource "aws_route53_health_check" "primary" {
  provider = aws.dns

  fqdn              = module.primary_region.alb_dns_name
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health/ready"
  failure_threshold = 3
  request_interval  = 30

  regions = ["us-east-1", "us-west-2", "eu-west-1"]

  tags = {
    Name = "amos-primary-health-check"
  }
}

# S3 Bucket for Global Accelerator Flow Logs
resource "aws_s3_bucket" "flow_logs" {
  provider = aws.dns
  bucket   = "amos-globalaccelerator-flowlogs-${var.environment}"
}

resource "aws_s3_bucket_versioning" "flow_logs" {
  provider = aws.dns
  bucket   = aws_s3_bucket.flow_logs.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "flow_logs" {
  provider = aws.dns
  bucket   = aws_s3_bucket.flow_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# RDS Cross-Region Read Replica
resource "aws_db_instance_automated_backups_replication" "secondary" {
  provider = aws.secondary

  source_db_instance_arn = module.primary_region.db_instance_arn
  kms_key_id            = aws_kms_key.secondary.arn
}

# KMS Key for Secondary Region
resource "aws_kms_key" "secondary" {
  provider = aws.secondary

  description             = "KMS key for secondary region RDS replication"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name = "amos-secondary-kms"
  }
}

# DynamoDB Global Tables for Session State
resource "aws_dynamodb_global_table" "sessions" {
  provider = aws.dns
  name     = "amos-sessions"

  replica {
    region_name = var.primary_region
  }

  replica {
    region_name = var.secondary_region
  }
}

# CloudWatch Cross-Region Dashboard
resource "aws_cloudwatch_dashboard" "multi_region" {
  provider       = aws.dns
  dashboard_name = "AMOS-Multi-Region-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Primary Region - Request Count"
          region = var.primary_region
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", module.primary_region.alb_arn_suffix]
          ]
          period = 300
          stat   = "Sum"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Secondary Region - Request Count"
          region = var.secondary_region
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", module.secondary_region.alb_arn_suffix]
          ]
          period = 300
          stat   = "Sum"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 24
        height = 6
        properties = {
          title  = "Global Accelerator Traffic Distribution"
          region = "us-west-2"
          metrics = [
            ["AWS/GlobalAccelerator", "TrafficDialPercentage", "Accelerator", aws_globalaccelerator_accelerator.amos.id]
          ]
          period = 60
          stat   = "Average"
        }
      }
    ]
  })
}

# SNS Topic for Multi-Region Alerts
resource "aws_sns_topic" "multi_region_alerts" {
  provider = aws.dns
  name     = "amos-multi-region-alerts"
}

# Outputs
output "global_accelerator_dns" {
  description = "Global Accelerator DNS name"
  value       = aws_globalaccelerator_accelerator.amos.dns_name
}

output "primary_alb_dns" {
  description = "Primary region ALB DNS"
  value       = module.primary_region.alb_dns_name
}

output "secondary_alb_dns" {
  description = "Secondary region ALB DNS"
  value       = module.secondary_region.alb_dns_name
}

output "primary_rds_endpoint" {
  description = "Primary RDS endpoint"
  value       = module.primary_region.db_endpoint
  sensitive   = true
}

output "secondary_rds_endpoint" {
  description = "Secondary RDS endpoint (read replica)"
  value       = module.secondary_region.db_endpoint
  sensitive   = true
}
