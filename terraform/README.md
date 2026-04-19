# AMOS Equation System - Terraform Infrastructure

Infrastructure as Code for deploying AMOS Equation System on AWS ECS Fargate with RDS PostgreSQL and ElastiCache Redis.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 VPC (10.0.0.0/16)                   │   │
│  │  ┌─────────────┐         ┌─────────────────────┐   │   │
│  │  │  Public     │         │      Private        │   │   │
│  │  │  Subnets    │         │      Subnets        │   │   │
│  │  │             │         │                     │   │   │
│  │  │ ┌─────────┐ │         │ ┌─────────────────┐ │   │   │
│  │  │ │   ALB   │ │         │ │   ECS Fargate   │ │   │   │
│  │  │ │  (HTTP) │ │─────────│ │   (FastAPI)     │ │   │   │
│  │  │ └─────────┘ │         │ └─────────────────┘ │   │   │
│  │  └─────────────┘         │         │          │   │   │
│  │                          │         │          │   │   │
│  │                          │    ┌────┴────┐     │   │   │
│  │                          │    │         │     │   │   │
│  │                          │ ┌──┴──┐   ┌─┴────┐│   │   │
│  │                          │ │ RDS │   │Redis ││   │   │
│  │                          │ │PGSQL│   │Cache ││   │   │
│  │                          │ └─────┘   └──────┘│   │   │
│  │                          └─────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Components

| Component | Service | Purpose |
|-----------|---------|---------|
| Compute | ECS Fargate | FastAPI application containers |
| Database | RDS PostgreSQL 15 | Primary data storage |
| Cache | ElastiCache Redis 7 | Session & caching layer |
| Load Balancer | ALB | Traffic distribution |
| Networking | VPC with NAT | Secure network isolation |
| Secrets | AWS SSM | Secure parameter storage |
| Logs | CloudWatch | Centralized logging |

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.5.0
- S3 bucket for Terraform state (configure in `main.tf`)
- DynamoDB table for state locking (optional but recommended)

## Quick Start

```bash
cd terraform

# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the infrastructure
terraform apply

# Destroy (when needed)
terraform destroy
```

## Configuration

### Environment-Specific Variables

Create `terraform.tfvars` for environment-specific configuration:

```hcl
environment = "production"
aws_region  = "us-east-1"

# Scaling
app_count    = 3
fargate_cpu  = 1024
fargate_memory = 2048

# Database
db_instance_class    = "db.t3.small"
db_allocated_storage = 50

# Redis
redis_node_type = "cache.t3.small"
```

### Available Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `environment` | Environment name (dev/staging/production) | `dev` |
| `aws_region` | AWS region | `us-east-1` |
| `app_count` | Number of ECS tasks | `2` |
| `fargate_cpu` | Fargate CPU units | `512` |
| `fargate_memory` | Fargate memory (MB) | `1024` |
| `db_instance_class` | RDS instance class | `db.t3.micro` |
| `db_allocated_storage` | RDS storage (GB) | `20` |
| `redis_node_type` | ElastiCache node type | `cache.t3.micro` |

## Deployment Workflow

1. **Build and push Docker image:**
   ```bash
   make build
   docker tag amos-equation:latest $ECR_URL:latest
   docker push $ECR_URL:latest
   ```

2. **Run database migrations:**
   ```bash
   make db-upgrade
   ```

3. **Deploy ECS service:**
   ```bash
   terraform apply
   ```

## Outputs

After deployment, Terraform provides:

- `alb_dns_name` - Application URL
- `ecr_repository_url` - Container registry URL
- `rds_endpoint` - Database connection string
- `redis_endpoint` - Cache connection string
- `cloudwatch_log_group` - Log group name

## Security Features

- **VPC Isolation**: Private subnets for application and data
- **NAT Gateway**: Outbound internet for updates only
- **Security Groups**: Least privilege access between services
- **Encryption**: 
  - RDS storage encrypted at rest
  - Redis encryption enabled
  - Secrets stored in AWS SSM Parameter Store
- **Auto-scaling**: CPU/memory-based with circuit breaker

## Cost Optimization

Default configuration uses:
- Fargate Spot for non-production workloads
- t3.micro instances for dev/staging
- Single Redis node for dev

Production recommendations:
- Enable Multi-AZ for RDS
- Redis cluster mode with 2+ nodes
- Fargate On-Demand for critical workloads

## Monitoring

- **CloudWatch Logs**: Application logs at `/ecs/amos-equation-{env}`
- **CloudWatch Metrics**: ECS service metrics and ALB metrics
- **RDS Enhanced Monitoring**: Database performance insights
- **ElastiCache Metrics**: Redis metrics and alarms

## Troubleshooting

### ECS Service Not Starting

1. Check CloudWatch logs for container errors
2. Verify task execution role permissions
3. Confirm ECR image exists and is accessible

### Database Connection Issues

1. Check security group rules allow ECS → RDS
2. Verify DATABASE_URL environment variable
3. Confirm RDS instance is available

### High Latency

1. Review ALB target group health checks
2. Check ECS service auto-scaling policies
3. Monitor RDS performance insights
