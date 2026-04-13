#!/bin/bash
#
# AMOS Brain - FINAL PRODUCTION DEPLOYMENT
# Complete deployment with SSL automation
#

set -e

DOMAIN="neurosyncai.tech"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       AMOS BRAIN - FINAL PRODUCTION DEPLOYMENT              ║"
echo "║                     $DOMAIN                                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
print_info "Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    print_error "Docker not found"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose not found"
    exit 1
fi

print_status "Prerequisites OK"
echo ""

# Check environment
if [ ! -f .env ]; then
    print_warning ".env not found, creating from template"
    cp .env.example .env
    print_warning "Edit .env with your production values before continuing"
    exit 1
fi

# Ask for deployment mode
print_info "Select deployment mode:"
echo "  1) Standard HTTP (port 80) - For testing"
echo "  2) Production HTTPS (port 443) - Requires SSL certificate"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        print_info "Deploying in STANDARD mode (HTTP)"
        echo ""
        
        # Build and deploy
        print_info "Building images..."
        docker-compose build --parallel
        
        print_info "Starting services..."
        docker-compose up -d
        
        # Health check
        sleep 5
        if curl -s http://localhost:5000/health | grep -q "healthy"; then
            print_status "Deployment successful!"
            echo ""
            echo "Access points:"
            echo "  API:      http://localhost:5000"
            echo "  Dashboard: http://localhost:8080"
            echo "  WebSocket: ws://localhost:8765"
        else
            print_error "Health check failed"
            docker-compose logs amos-api
            exit 1
        fi
        ;;
        
    2)
        print_info "Deploying in PRODUCTION mode (HTTPS)"
        echo ""
        
        # Check for SSL certificates
        if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
            print_warning "SSL certificates not found for $DOMAIN"
            print_info "Run ./setup-ssl.sh first to obtain certificates"
            echo ""
            read -p "Run SSL setup now? [y/N]: " ssl_setup
            
            if [[ $ssl_setup =~ ^[Yy]$ ]]; then
                sudo ./setup-ssl.sh
            else
                print_error "SSL setup required for HTTPS deployment"
                exit 1
            fi
        fi
        
        # Deploy with SSL
        print_info "Building images..."
        docker-compose -f docker-compose.ssl.yml build --parallel
        
        print_info "Starting services with SSL..."
        docker-compose -f docker-compose.ssl.yml up -d
        
        # Health check
        sleep 5
        if curl -s http://localhost:5000/health | grep -q "healthy"; then
            print_status "Production deployment successful!"
            echo ""
            echo "╔══════════════════════════════════════════════════════════════╗"
            echo "║                   🎉 DEPLOYMENT COMPLETE 🎉                  ║"
            echo "╚══════════════════════════════════════════════════════════════╝"
            echo ""
            echo "HTTPS Access:"
            echo "  🌐 Main:     https://$DOMAIN"
            echo "  📊 Dashboard: https://$DOMAIN/admin"
            echo "  🔌 API:      https://$DOMAIN"
            echo "  📡 WebSocket: wss://$DOMAIN/ws"
            echo ""
            echo "Management:"
            echo "  python amos-cli.py status"
            echo "  python amos-cli.py logs"
            echo "  python amos-cli.py backup"
        else
            print_error "Health check failed"
            docker-compose -f docker-compose.ssl.yml logs amos-api
            exit 1
        fi
        ;;
        
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

echo ""
print_status "All systems operational!"
