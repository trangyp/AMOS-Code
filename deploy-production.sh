#!/bin/bash
# AMOS Production Deployment Script
# Deploys AMOS Brain API to neurosyncai.tech

set -e

echo "=============================================="
echo "  AMOS Production Deployment"
echo "  Domain: neurosyncai.tech"
echo "=============================================="
echo ""

# Configuration
DOMAIN="neurosyncai.tech"
APP_NAME="amos-brain"
PORT="${PORT:-5000}"

echo "📦 Step 1: Build Application"
echo "   - Installing dependencies..."
pip install -q -r requirements-deploy.txt

echo ""
echo "🧠 Step 2: Test AMOS Brain"
python3 -c "
from amos_brain import BrainClient
from amosl import parse, compile_program
print('   ✓ AMOS Brain imported')
print('   ✓ AMOSL compiler imported')
"

echo ""
echo "🐳 Step 3: Build Docker Image"
docker build -t $APP_NAME:latest .
docker tag $APP_NAME:latest $APP_NAME:$(date +%Y%m%d)

echo ""
echo "🚀 Step 4: Deployment Ready"
echo "   Image: $APP_NAME:latest"
echo "   Port: $PORT"
echo "   Domain: $DOMAIN"
echo ""
echo "To deploy:"
echo "   docker run -d -p $PORT:$PORT --name $APP_NAME $APP_NAME:latest"
echo ""
echo "=============================================="
echo "  Deployment artifact ready"
echo "=============================================="
