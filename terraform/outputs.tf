"""
Terraform Outputs
"""

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.app.repository_url
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.app.name
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.app.name
}

output "ssm_parameter_db_password" {
  description = "SSM parameter name for DB password"
  value       = aws_ssm_parameter.db_password.name
}

output "ssm_parameter_jwt_secret" {
  description = "SSM parameter name for JWT secret"
  value       = aws_ssm_parameter.jwt_secret.name
}

output "ssm_parameter_api_key" {
  description = "SSM parameter name for API key"
  value       = aws_ssm_parameter.api_key.name
}

# =============================================================================
# SuperBrain Monitoring Outputs
# =============================================================================

output "superbrain_health_endpoint" {
  description = "SuperBrain health check endpoint"
  value       = "${aws_lb.main.dns_name}/health"
}

output "superbrain_governance_status" {
  description = "SuperBrain governance integration status"
  value       = "enabled"
}

output "superbrain_audit_endpoint" {
  description = "SuperBrain audit trail endpoint"
  value       = "${aws_lb.main.dns_name}/api/v1/audit"
}

output "amos_dashboard_url" {
  description = "AMOS Unified Dashboard URL"
  value       = "${aws_lb.main.dns_name}/dashboard"
}

output "api_gateway_url" {
  description = "AMOS API Gateway URL"
  value       = "${aws_lb.main.dns_name}/api/v1"
}
