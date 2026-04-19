#!/bin/bash
# AMOS-OpenClaw Connection Script
# Usage: ./connect_openclaw.sh [mcp|api|sync|full]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔗 AMOS-OpenClaw Connector${NC}"
echo "================================"

# Check paths
AMOS_HOME="/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code"
OPENCLAW_HOME="/Users/nguyenxuanlinh/Documents/Trang Phan/openclaw-main"

echo -e "${BLUE}📁 Checking repositories...${NC}"

if [ ! -d "$AMOS_HOME" ]; then
    echo -e "${YELLOW}❌ AMOS-code not found at $AMOS_HOME${NC}"
    exit 1
fi

if [ ! -d "$OPENCLAW_HOME" ]; then
    echo -e "${YELLOW}❌ openclaw-main not found at $OPENCLAW_HOME${NC}"
    exit 1
fi

echo -e "${GREEN}✅ AMOS-code: $AMOS_HOME${NC}"
echo -e "${GREEN}✅ OpenClaw: $OPENCLAW_HOME${NC}"

# Create bridge directory
BRIDGE_DIR="$HOME/.amos-openclaw-bridge"
mkdir -p "$BRIDGE_DIR/state"
echo -e "${GREEN}✅ Bridge directory: $BRIDGE_DIR${NC}"

# Set environment
export AMOS_HOME="$AMOS_HOME"
export OPENCLAW_HOME="$OPENCLAW_HOME"
export AMOS_OPENCLAW_MODE="${1:-full}"
export PYTHONPATH="$AMOS_HOME:$PYTHONPATH"

cd "$AMOS_HOME"

MODE="${1:-full}"

case "$MODE" in
    mcp)
        echo -e "${BLUE}🚀 Starting MCP Server...${NC}"
        echo "OpenClaw can now call AMOS tools via Model Context Protocol"
        python3 amos_openclaw_connector.py --mcp
        ;;
    api)
        echo -e "${BLUE}🚀 Starting API Bridge on port 8888...${NC}"
        echo "REST API available at http://localhost:8888"
        python3 amos_openclaw_connector.py --api --port 8888
        ;;
    sync)
        echo -e "${BLUE}🔄 Syncing state...${NC}"
        python3 amos_openclaw_connector.py --sync
        echo -e "${GREEN}✅ State synchronized${NC}"
        ;;
    plugin)
        echo -e "${BLUE}🔌 Generating OpenClaw plugin...${NC}"
        python3 amos_openclaw_connector.py --generate-plugin
        echo -e "${GREEN}✅ Plugin generated in openclaw-main/extensions/amos-brain-plugin/${NC}"
        echo "To activate: cd $OPENCLAW_HOME && openclaw plugins enable amos-brain"
        ;;
    full)
        echo -e "${BLUE}🚀 Starting full bridge (MCP + API + Sync)...${NC}"
        echo "This will run all connection methods simultaneously"
        echo ""
        echo -e "${YELLOW}Connection endpoints:${NC}"
        echo "  • MCP: stdio (for OpenClaw tools)"
        echo "  • API: http://localhost:8888"
        echo "  • State: $BRIDGE_DIR/state/"
        echo ""
        python3 amos_openclaw_connector.py --full
        ;;
    *)
        echo "Usage: $0 [mcp|api|sync|plugin|full]"
        echo ""
        echo "Modes:"
        echo "  mcp     - Start MCP server for tool calling"
        echo "  api     - Start REST API bridge"
        echo "  sync    - One-time state synchronization"
        echo "  plugin  - Generate OpenClaw plugin files"
        echo "  full    - Start all connection methods (default)"
        exit 1
        ;;
esac
