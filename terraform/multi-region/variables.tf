# Variables for Multi-Region AMOS Deployment

variable "primary_region" {
  description = "Primary AWS region"
  type        = string
  default     = "us-east-1"
}

variable "secondary_region" {
  description = "Secondary AWS region for DR"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "primary_vpc_cidr" {
  description = "VPC CIDR for primary region"
  type        = string
  default     = "10.0.0.0/16"
}

variable "secondary_vpc_cidr" {
  description = "VPC CIDR for secondary region"
  type        = string
  default     = "10.1.0.0/16"
}

variable "primary_app_count" {
  description = "Number of app instances in primary region"
  type        = number
  default     = 3
}

variable "secondary_app_count" {
  description = "Number of app instances in secondary region"
  type        = number
  default     = 1
}

variable "primary_traffic_percentage" {
  description = "Traffic percentage to primary region (0-100)"
  type        = number
  default     = 90
}

variable "secondary_traffic_percentage" {
  description = "Traffic percentage to secondary region (0-100)"
  type        = number
  default     = 10
}

variable "primary_weight" {
  description = "Endpoint weight for primary region"
  type        = number
  default     = 100
}

variable "secondary_weight" {
  description = "Endpoint weight for secondary region"
  type        = number
  default     = 50
}

# Database Variables
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "amos_equations"
}

variable "db_username" {
  description = "Database username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Redis Variables
variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

# ECS Variables
variable "ecs_task_cpu" {
  description = "ECS task CPU units"
  type        = string
  default     = "512"
}

variable "ecs_task_memory" {
  description = "ECS task memory (MiB)"
  type        = string
  default     = "1024"
}

variable "app_image" {
  description = "Docker image URL for application"
  type        = string
}
