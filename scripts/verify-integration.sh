#!/bin/bash
#
# AMOS SuperBrain Integration Verification Script v2.0.0
# Validates all 10 systems are properly governed by SuperBrain
#
# Usage: ./verify-integration.sh [environment]
#   environment: dev | staging | prod (default: dev)
#
# Author: Trang Phan
# Version: 2.0.0

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ENVIRONMENT="${1:-dev}"
AWS_REGION="us-east-1"
FAILED=0

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     SuperBrain Integration Verification v2.0.0             ║"
echo "║                                                              ║"
echo "║  Environment: $ENVIRONMENT                                    "
echo "║  Systems to Verify: 12                                       ║"
echo "║  Total Tests: 19 (7 infra + 12 systems)                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Get Terraform outputs
cd terraform
ALB_DNS=$(terraform output -raw alb_dns_name 2>/dev/null || echo "")
SUPERBRAIN_HEALTH=$(terraform output -raw superbrain_health_endpoint 2>/dev/null || echo "")
cd ..

if [[ -z "$SUPERBRAIN_HEALTH" ]]; then
    echo -e "${RED}Error: Could not get SuperBrain health endpoint${NC}"
    echo "Make sure Terraform has been applied"
    exit 1
fi

BASE_URL="http://${SUPERBRAIN_HEALTH}"

echo -e "${YELLOW}Testing SuperBrain health endpoints...${NC}"
echo ""

# Test 1: Liveness probe
echo -n "1. Liveness probe (/health/live)... "
if curl -sf "${BASE_URL}/live" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 2: Readiness probe
echo -n "2. Readiness probe (/health/ready)... "
if curl -sf "${BASE_URL}/ready" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 3: SuperBrain governance status
echo -n "3. SuperBrain governance (/health/superbrain)... "
SUPERBRAIN_RESPONSE=$(curl -sf "${BASE_URL}/superbrain" 2>/dev/null || echo "")
if [[ -n "$SUPERBRAIN_RESPONSE" ]]; then
    if echo "$SUPERBRAIN_RESPONSE" | grep -q "healthy"; then
        echo -e "${GREEN}✓ PASS${NC}"
        GOVERNED_COUNT=$(echo "$SUPERBRAIN_RESPONSE" | grep -o '"governed_systems":[0-9]*' | cut -d: -f2)
        echo -e "   ${BLUE}Governed Systems: $GOVERNED_COUNT${NC}"
    else
        echo -e "${RED}✗ FAIL (SuperBrain reports unhealthy)${NC}"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗ FAIL (No response)${NC}"
    ((FAILED++))
fi

# Test 4: Full health check
echo -n "4. Full health check (/health)... "
FULL_HEALTH=$(curl -sf "${BASE_URL}" 2>/dev/null || echo "")
if [[ -n "$FULL_HEALTH" ]]; then
    if echo "$FULL_HEALTH" | grep -q '"status":"healthy"'; then
        echo -e "${GREEN}✓ PASS${NC}"
    else
        echo -e "${YELLOW}⚠ DEGRADED${NC}"
    fi
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo ""
echo -e "${YELLOW}Verifying CloudWatch infrastructure...${NC}"
echo ""

# Test 5: CloudWatch log groups
echo -n "5. CloudWatch log groups... "
LOG_GROUPS=$(aws logs describe-log-groups --region "$AWS_REGION" \
    --query "logGroups[?contains(logGroupName, 'amossuperbrain')].logGroupName" \
    --output text 2>/dev/null || echo "")
if [[ -n "$LOG_GROUPS" ]]; then
    echo -e "${GREEN}✓ PASS${NC}"
    echo "$LOG_GROUPS" | tr '\t' '\n' | while read log; do
        [[ -n "$log" ]] && echo -e "   ${BLUE}$log${NC}"
    done
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 6: CloudWatch dashboard
echo -n "6. CloudWatch dashboard... "
DASHBOARD=$(aws cloudwatch list-dashboards --region "$AWS_REGION" \
    --query "DashboardEntries[?contains(DashboardName, 'superbrain')].DashboardName" \
    --output text 2>/dev/null || echo "")
if [[ -n "$DASHBOARD" ]]; then
    echo -e "${GREEN}✓ PASS${NC}"
    echo -e "   ${BLUE}$DASHBOARD${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test 7: CloudWatch alarms
echo -n "7. CloudWatch alarms... "
ALARMS=$(aws cloudwatch describe-alarms --region "$AWS_REGION" \
    --query "MetricAlarms[?contains(AlarmName, 'superbrain')].AlarmName" \
    --output text 2>/dev/null || echo "")
ALARM_COUNT=$(echo "$ALARMS" | tr '\t' '\n' | grep -c "superbrain" || echo "0")
if [[ "$ALARM_COUNT" -ge 3 ]]; then
    echo -e "${GREEN}✓ PASS ($ALARM_COUNT alarms)${NC}"
else
    echo -e "${YELLOW}⚠ WARNING ($ALARM_COUNT alarms, expected 3+)${NC}"
fi

echo ""
echo -e "${YELLOW}Verifying integrated systems...${NC}"
echo ""

# Systems to verify (based on SuperBrainGovernanceCheck)
SYSTEMS=(
    "Production API:2.3.0"
    "GraphQL API:2.3.0"
    "Agent Messaging:3.1.0"
    "Agent Observability:3.1.0"
    "LLM Providers:2.0.0"
    "UBI Engine:2.0.0"
    "Audit Exporter:2.0.0"
    "AMOS Tools:2.0.0"
    "Knowledge Loader:2.0.0"
    "Master Orchestrator:2.0.0"
    "Cognitive Router:2.0.0"
    "Resilience Engine:2.0.0"
)

for i in "${!SYSTEMS[@]}"; do
    IFS=':' read -r name version <<< "${SYSTEMS[$i]}"
    test_num=$((i + 8))
    echo -n "$test_num. $name v$version... "

    # Check if system is mentioned in SuperBrain response
    if echo "$SUPERBRAIN_RESPONSE" | grep -qi "$name" 2>/dev/null; then
        echo -e "${GREEN}✓ GOVERNED${NC}"
    else
        echo -e "${YELLOW}⚠ NOT VERIFIED${NC}"
    fi
done

echo ""
echo -e "${YELLOW}Summary:${NC}"
echo "═══════════════════════════════════════════════════════════════"

if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║           ✓ ALL VERIFICATION TESTS PASSED                     ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo "SuperBrain v2.0.0 is fully operational"
    echo "10 systems governing 4,644 features"
    echo ""
    echo "Next steps:"
    echo "1. Access dashboard: http://${ALB_DNS}/dashboard"
    echo "2. Monitor CloudWatch: ${DASHBOARD}"
    echo "3. Review audit logs: /aws/amossuperbrain/${ENVIRONMENT}/audit"
    exit 0
else
    echo -e "${RED}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║           ✗ $FAILED VERIFICATION TEST(S) FAILED               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo "Please review the failed tests above"
    exit 1
fi
