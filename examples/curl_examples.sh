#!/bin/bash
#
# AMOS Brain API - cURL Examples
# Domain: neurosyncai.tech
#

API_URL="https://neurosyncai.tech"

echo "AMOS Brain API Examples"
echo "======================="
echo ""

# Health check
echo "1. Health Check"
echo "---------------"
curl -s "$API_URL/health" | python3 -m json.tool
echo ""

# Status
echo "2. Brain Status"
echo "---------------"
curl -s "$API_URL/status" | python3 -m json.tool
echo ""

# Think
echo "3. Think Endpoint"
echo "-----------------"
curl -s -X POST "$API_URL/think" \
  -H "Content-Type: application/json" \
  -d '{"query": "Benefits of TypeScript?", "domain": "software"}' | \
  python3 -m json.tool
echo ""

# Decide
echo "4. Decide Endpoint"
echo "------------------"
curl -s -X POST "$API_URL/decide" \
  -H "Content-Type: application/json" \
  -d '{"question": "Which framework?", "options": ["React", "Vue", "Svelte"]}' | \
  python3 -m json.tool
echo ""

# Validate
echo "5. Validate Endpoint"
echo "--------------------"
curl -s -X POST "$API_URL/validate" \
  -H "Content-Type: application/json" \
  -d '{"action": "Implement comprehensive logging"}' | \
  python3 -m json.tool
echo ""

echo "Done!"
