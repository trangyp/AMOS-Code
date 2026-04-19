#!/bin/bash
# AMOS SuperBrain API Key Configuration Script
# Usage: ./configure_api_keys.sh
# Following security best practices from 2025 LLM deployment patterns

set -e

echo "=========================================="
echo "AMOS SuperBrain API Key Configuration"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo ""
echo "----------------------------------------"
echo "LLM Provider Configuration"
echo "----------------------------------------"
echo ""
echo "At least one provider required for 100% health"
echo ""

# Function to prompt for API key
prompt_key() {
    local provider=$1
    local env_var=$2
    local example=$3

    echo -n "Configure $provider? (y/n): "
    read -r response

    if [[ $response =~ ^[Yy]$ ]]; then
        echo -n "Enter $provider API key [$example]: "
        read -r -s api_key
        echo ""

        if [ -n "$api_key" ]; then
            # Update .env file
            if grep -q "^$env_var=" .env; then
                # Update existing
                sed -i.bak "s|^$env_var=.*|$env_var=$api_key|" .env
                rm -f .env.bak
            else
                # Add new
                echo "$env_var=$api_key" >> .env
            fi
            echo -e "${GREEN}✓ $provider configured${NC}"
        else
            echo -e "${YELLOW}⚠ Skipped $provider (empty key)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Skipped $provider${NC}"
    fi
    echo ""
}

# Configure providers
prompt_key "OpenAI" "OPENAI_API_KEY" "sk-..."
prompt_key "Anthropic" "ANTHROPIC_API_KEY" "sk-ant-..."
prompt_key "Kimi (Moonshot)" "KIMI_API_KEY" "..."

echo "----------------------------------------"
echo "Configuration Complete"
echo "----------------------------------------"
echo ""

# Verify configuration
echo "Verifying configuration..."
source .env 2>/dev/null || true

configured=0
if [ -n "$OPENAI_API_KEY" ]; then
    echo -e "${GREEN}✓ OpenAI: Configured${NC}"
    configured=$((configured + 1))
else
    echo -e "${YELLOW}⚠ OpenAI: Not configured${NC}"
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo -e "${GREEN}✓ Anthropic: Configured${NC}"
    configured=$((configured + 1))
else
    echo -e "${YELLOW}⚠ Anthropic: Not configured${NC}"
fi

if [ -n "$KIMI_API_KEY" ]; then
    echo -e "${GREEN}✓ Kimi: Configured${NC}"
    configured=$((configured + 1))
else
    echo -e "${YELLOW}⚠ Kimi: Not configured${NC}"
fi

echo ""
echo "=========================================="
if [ $configured -gt 0 ]; then
    echo -e "${GREEN}✓ $configured provider(s) configured${NC}"
    echo -e "${GREEN}✓ AMOS SuperBrain ready for 100% health${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Restart AMOS SuperBrain"
    echo "2. Run: python -c 'from amos_brain import initialize_super_brain; initialize_super_brain()'"
    echo "3. Verify health score reaches 100%"
else
    echo -e "${YELLOW}⚠ No providers configured${NC}"
    echo ""
    echo "To configure later:"
    echo "1. Edit .env file directly"
    echo "2. Or re-run this script"
fi
echo "=========================================="
