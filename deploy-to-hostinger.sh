#!/bin/bash
#
# Deploy AMOS Brain to Hostinger
# Usage: ./deploy-to-hostinger.sh
#

set -e

echo "=================================="
echo "AMOS Brain Deployment to Hostinger"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Using .env.example${NC}"
    cp .env.example .env
    echo "Please edit .env with your actual values before deploying."
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

echo "Step 1: Building Docker image..."
docker build -t amos-brain:latest .

echo ""
echo "Step 2: Testing locally..."
docker run --rm -p 5000:5000 -d --name amos-test amos-brain:latest
sleep 5

if curl -s http://localhost:5000/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ Local health check passed${NC}"
else
    echo "✗ Health check failed"
    docker stop amos-test
    exit 1
fi

docker stop amos-test
echo ""

echo "Step 3: Saving image..."
docker save amos-brain:latest > amos-brain.tar
echo "✓ Image saved to amos-brain.tar"

echo ""
echo "Step 4: Preparing deployment package..."
tar -czf deploy-package.tar.gz amos-brain.tar docker-compose.yml .env

echo ""
echo "=================================="
echo "Deployment package created: deploy-package.tar.gz"
echo ""
echo "Next steps:"
echo "1. Upload deploy-package.tar.gz to Hostinger"
echo "2. Extract and run: docker load < amos-brain.tar"
echo "3. Start: docker-compose up -d"
echo ""
echo "Or use Hostinger's Git deployment feature:"
echo "- Connect GitHub repo in Hostinger panel"
echo "- Set deploy branch to 'main'"
echo "- Add HOSTINGER_API_KEY to GitHub secrets"
echo "=================================="
