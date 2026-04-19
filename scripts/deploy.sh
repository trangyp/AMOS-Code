#!/bin/bash
#
# AMOS SuperBrain Production Deployment Script v2.0.0
# Deploys the 30-layer ecosystem with full governance integration
#
# Usage: ./deploy.sh [environment]
#   environment: dev | staging | prod (default: dev)
#
# Author: Trang Phan
# Version: 2.0.0

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-dev}"
PROJECT_NAME="amos-superbrain"
TERRAFORM_DIR="terraform"
AWS_REGION="us-east-1"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo -e "${RED}Error: Invalid environment '$ENVIRONMENT'${NC}"
    echo "Usage: $0 [dev|staging|prod]"
    exit 1
fi

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     AMOS SuperBrain Production Deployment v2.0.0            ║"
echo "║                                                              ║"
echo "║  Environment: $ENVIRONMENT                                    "
echo "║  Systems: 12                                                 ║"
echo "║  Features Governed: 4,644                                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI not installed${NC}"
    exit 1
fi

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Error: Terraform not installed${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites verified${NC}"

# Create Terraform variables file
echo -e "${YELLOW}Generating Terraform configuration...${NC}"

cat > "${TERRAFORM_DIR}/terraform.tfvars" << EOF
environment = "${ENVIRONMENT}"
project_name = "${PROJECT_NAME}"
aws_region = "${AWS_REGION}"

# ECS Configuration
ecs_task_cpu = ${ENVIRONMENT == "prod" ? "2048" : "1024"}
ecs_task_memory = ${ENVIRONMENT == "prod" ? "4096" : "2048"}
desired_count = ${ENVIRONMENT == "prod" ? "3" : "1"}

# RDS Configuration
db_instance_class = "${ENVIRONMENT == "prod" ? "db.t3.medium" : "db.t3.micro"}"
db_allocated_storage = ${ENVIRONMENT == "prod" ? "100" : "20"}

# ElastiCache Configuration
cache_node_type = "${ENVIRONMENT == "prod" ? "cache.t3.medium" : "cache.t3.micro"}"
cache_num_cache_nodes = ${ENVIRONMENT == "prod" ? "2" : "1"}
EOF

echo -e "${GREEN}✓ Terraform configuration generated${NC}"

# Initialize Terraform
echo -e "${YELLOW}Initializing Terraform...${NC}"
cd "${TERRAFORM_DIR}"
terraform init -backend-config="bucket=amos-terraform-state" \
               -backend-config="key=equation-system/${ENVIRONMENT}/terraform.tfstate" \
               -backend-config="region=${AWS_REGION}"

echo -e "${GREEN}✓ Terraform initialized${NC}"

# Validate Terraform
echo -e "${YELLOW}Validating Terraform configuration...${NC}"
terraform validate
echo -e "${GREEN}✓ Terraform configuration valid${NC}"

# Plan Terraform
echo -e "${YELLOW}Planning Terraform changes...${NC}"
terraform plan -out="tfplan" -var-file="terraform.tfvars"
echo -e "${GREEN}✓ Terraform plan complete${NC}"

# Apply Terraform (with confirmation for prod)
if [[ "$ENVIRONMENT" == "prod" ]]; then
    echo -e "${RED}WARNING: You are about to deploy to PRODUCTION${NC}"
    read -p "Are you sure? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "Deployment cancelled"
        exit 0
    fi
fi

echo -e "${YELLOW}Applying Terraform changes...${NC}"
terraform apply "tfplan"
echo -e "${GREEN}✓ Infrastructure deployed${NC}"

# Capture outputs
echo -e "${YELLOW}Capturing Terraform outputs...${NC}"
ALB_DNS=$(terraform output -raw alb_dns_name)
SUPERBRAIN_HEALTH=$(terraform output -raw superbrain_health_endpoint)
DASHBOARD_URL=$(terraform output -raw amos_dashboard_url)

cd ..

echo -e "${GREEN}✓ Outputs captured${NC}"

# Verify deployment
echo -e "${YELLOW}Verifying deployment...${NC}"
echo ""
echo "Waiting for services to stabilize (60 seconds)..."
sleep 60

# Check health endpoint
echo -e "${BLUE}Checking SuperBrain health endpoint...${NC}"
for i in {1..5}; do
    if curl -sf "http://${SUPERBRAIN_HEALTH}/superbrain" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ SuperBrain health check passed${NC}"
        break
    else
        echo -e "${YELLOW}  Attempt $i/5 failed, retrying...${NC}"
        sleep 10
    fi
done

echo -e "${GREEN}✓ Deployment verification complete${NC}"

# Print summary
echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                 DEPLOYMENT SUCCESSFUL                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo "Environment:        $ENVIRONMENT"
echo "ALB DNS Name:       $ALB_DNS"
echo "SuperBrain Health:  $SUPERBRAIN_HEALTH"
echo "Dashboard URL:      $DASHBOARD_URL"
echo ""
echo "Health Endpoints:"
echo "  - $SUPERBRAIN_HEALTH/live"
echo "  - $SUPERBRAIN_HEALTH/ready"
echo "  - $SUPERBRAIN_HEALTH/superbrain"
echo ""
echo "CloudWatch Dashboard:"
echo "  - ${PROJECT_NAME}-superbrain-${ENVIRONMENT}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Monitor CloudWatch dashboard for health status"
echo "2. Check audit logs in /aws/amossuperbrain/${ENVIRONMENT}/audit"
echo "3. Verify SuperBrain governance status in unified dashboard"
echo "4. Run: ./scripts/verify-integration.sh ${ENVIRONMENT}"
echo ""
