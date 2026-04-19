#!/bin/bash
# AMOS Production Deployment Script (Phase 11)
# ===============================================
#
# Automates deployment of the AMOS production stack
# including FastAPI Gateway, Runtime, and Monitoring
#
# Usage:
#   ./deploy_production.sh [command] [options]
#
# Commands:
#   deploy      - Deploy full stack
#   start       - Start services
#   stop        - Stop services
#   restart     - Restart services
#   status      - Check service status
#   logs        - View logs
#   update      - Update and redeploy
#   health      - Run health checks
#   clean       - Clean up volumes and images
#
# Examples:
#   ./deploy_production.sh deploy
#   ./deploy_production.sh logs gateway
#   ./deploy_production.sh health

set -e

# Configuration
COMPOSE_FILE="docker-compose.production-runtime.yml"
PROJECT_NAME="amos-production"
VERSION="1.0.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if docker and docker-compose are installed
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check if docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Build images
build_images() {
    log_info "Building Docker images..."

    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME build --no-cache

    log_success "Images built successfully"
}

# Deploy full stack
deploy() {
    log_info "Deploying AMOS Production Stack v$VERSION..."

    check_prerequisites

    # Create network if it doesn't exist
    docker network create amos-production-network 2>/dev/null || true

    # Build images
    build_images

    # Start services
    log_info "Starting services..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d

    # Wait for health checks
    log_info "Waiting for services to be healthy..."
    sleep 10

    # Check health
    if check_health; then
        log_success "Deployment completed successfully!"
        show_endpoints
    else
        log_warn "Some services may not be fully healthy yet. Check logs with: $0 logs"
    fi
}

# Start services
start() {
    log_info "Starting AMOS services..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME start
    log_success "Services started"
}

# Stop services
stop() {
    log_info "Stopping AMOS services..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME stop
    log_success "Services stopped"
}

# Restart services
restart() {
    log_info "Restarting AMOS services..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME restart
    log_success "Services restarted"
}

# Show status
status() {
    echo "=========================================="
    echo "  AMOS Production Stack Status"
    echo "=========================================="
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps

    echo ""
    echo "=========================================="
    echo "  Container Health"
    echo "=========================================="
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps | grep -E "(Name|amos)" || echo "No containers running"
}

# View logs
logs() {
    local service=$1

    if [ -z "$service" ]; then
        log_info "Showing logs for all services..."
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f
    else
        log_info "Showing logs for $service..."
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f $service
    fi
}

# Check health
health() {
    log_info "Running health checks..."

    # Check gateway health
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        log_success "Gateway is healthy"
    else
        log_error "Gateway health check failed"
    fi

    # Check if containers are running
    running=$(docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps -q | wc -l)
    if [ "$running" -gt 0 ]; then
        log_success "$running container(s) running"
    else
        log_error "No containers running"
    fi
}

# Update and redeploy
update() {
    log_info "Updating AMOS stack..."

    # Pull latest changes (if using git)
    if [ -d ".git" ]; then
        git pull origin main || log_warn "Could not pull latest changes"
    fi

    # Rebuild and restart
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down
    deploy
}

# Clean up
clean() {
    log_warn "This will remove all containers, volumes, and images. Are you sure? (y/N)"
    read -r response

    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "Cleaning up..."
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down -v --rmi all
        docker network rm amos-production-network 2>/dev/null || true
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Show endpoints
show_endpoints() {
    echo ""
    echo "=========================================="
    echo "  AMOS Production Stack Endpoints"
    echo "=========================================="
    echo "  API Gateway:     http://localhost:8000"
    echo "  API Docs:        http://localhost:8000/docs"
    echo "  Health Check:    http://localhost:8000/health"
    echo "  WebSocket:       ws://localhost:8000/ws/health"
    echo "  Redis:           localhost:6379"
    echo "=========================================="
}

# Show help
show_help() {
    cat << EOF
AMOS Production Deployment Script v$VERSION
=========================================

Usage: $0 [command] [options]

Commands:
  deploy              Deploy full production stack
  start               Start services
  stop                Stop services
  restart             Restart services
  status              Show service status
  logs [service]      View logs (optionally for specific service)
  health              Run health checks
  update              Update and redeploy
  clean               Clean up all containers, volumes, and images
  help                Show this help message

Examples:
  $0 deploy              # Deploy full stack
  $0 logs gateway        # View gateway logs
  $0 status              # Check service status
  $0 health              # Run health checks

EOF
}

# Main command handler
case "${1:-help}" in
    deploy)
        deploy
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    health)
        health
        ;;
    update)
        update
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
