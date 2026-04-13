#!/bin/bash
# AMOS Brain + ClawSpring Quick Setup Script
# Usage: ./install.sh [--dev] [--mcp]

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        AMOS Brain + ClawSpring Setup                      ║"
echo "║   Artificial Mind Operating System Installer               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.9"

if [ -z "$PYTHON_VERSION" ]; then
    echo -e "${RED}Error: Python 3 not found${NC}"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "✓ Python version: $PYTHON_VERSION"

# Parse arguments
DEV_MODE=false
MCP_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            DEV_MODE=true
            shift
            ;;
        --mcp)
            MCP_MODE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./install.sh [--dev] [--mcp]"
            exit 1
            ;;
    esac
done

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "→ Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "→ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "→ Upgrading pip..."
pip install --quiet --upgrade pip

# Install AMOS Brain
echo "→ Installing AMOS Brain..."
pip install --quiet -e .

# Install dev dependencies if requested
if [ "$DEV_MODE" = true ]; then
    echo "→ Installing development dependencies..."
    pip install --quiet -e ".[dev]"
fi

# Install MCP server if requested
if [ "$MCP_MODE" = true ]; then
    echo "→ Installing MCP server dependencies..."
    pip install --quiet -e ".[mcp]"
fi

# Verify installation
echo ""
echo "→ Verifying installation..."
python3 -c "from amos_brain import get_amos_integration; a = get_amos_integration(); print(f'✓ Brain initialized: {a.get_status()[\"initialized\"]}')"

echo ""
echo -e "${GREEN}✓ AMOS Brain installation complete!${NC}"
echo ""
echo "Available commands:"
echo "  amos status          - Check brain status"
echo "  amos decide <text>   - Analyze a decision"
echo "  amos laws            - Show Global Laws"
echo "  amos demo            - Run interactive demo"
echo "  amos-clawspring      - Run AMOS-enhanced agent"
echo ""
echo "Quick start:"
echo "  source venv/bin/activate"
echo "  amos status"
echo ""
