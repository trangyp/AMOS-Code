#!/bin/bash
#
# AMOS Brain - Production Deployment Script
# One command to deploy everything to neurosyncai.tech
#

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║               AMOS BRAIN PRODUCTION DEPLOYMENT               ║"
echo "║                     neurosyncai.tech                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose not found. Please install Docker Compose."
    exit 1
fi

print_status "Prerequisites OK"
echo ""

# Step 2: Check environment
echo "Step 2: Checking environment configuration..."
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    print_warning "Please edit .env with your production values before continuing."
    exit 1
fi

print_status "Environment OK"
echo ""

# Step 3: Build images
echo "Step 3: Building Docker images..."
docker-compose build --parallel
print_status "Images built"
echo ""

# Step 4: Start services
echo "Step 4: Starting services..."
docker-compose up -d
print_status "Services started"
echo ""

# Step 5: Health check
echo "Step 5: Health check..."
sleep 5

if curl -s http://localhost:5000/health | grep -q "healthy"; then
    print_status "API is healthy"
else
    print_error "API health check failed"
    docker-compose logs amos-api
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                 DEPLOYMENT SUCCESSFUL!                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Access Points:"
echo "  🌐 Main Site:    http://neurosyncai.tech"
echo "  📊 Dashboard:    http://neurosyncai.tech:8080"
echo "  🔌 API:          http://neurosyncai.tech:5000"
echo "  📡 WebSocket:    ws://neurosyncai.tech:8765"
echo ""
echo "Management:"
echo "  View logs:      docker-compose logs -f"
echo "  Check status:   python amos-cli.py status"
echo "  Stop:           docker-compose down"
echo "  Backup:         python amos-cli.py backup"
echo ""
echo "Documentation:"
echo "  📖 API Docs:     API_README.md"
echo "  🚀 Quick Start:  QUICKSTART.md"
echo "  📋 Deployment:   DEPLOYMENT_GUIDE.md"
echo "  ✅ Complete:     SYSTEM_COMPLETE.md"
echo ""
