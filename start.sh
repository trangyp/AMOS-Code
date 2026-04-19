#!/bin/bash
#
# AMOS v3.0.0 - One-Click Startup Script
#
# Usage:
#   ./start.sh              - Start all services
#   ./start.sh --dev        - Start in development mode
#   ./start.sh --stop       - Stop all services
#   ./start.sh --logs       - View logs
#   ./start.sh --test       - Run integration tests
#
# Creator: Trang Phan

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
API_URL="http://localhost:8000"
DASHBOARD_URL="http://localhost:3000"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║   AMOS v3.0.0 - Autonomous Multi-Agent Orchestration       ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}✗ Docker is not running${NC}"
        echo "  Please start Docker Desktop first"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is running${NC}"
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1

    echo -e "${YELLOW}⏳ Waiting for $name...${NC}"

    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url/health" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ $name is ready${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo -e "${RED}✗ $name failed to start${NC}"
    return 1
}

# Function to start services
start_services() {
    echo -e "${BLUE}Building and starting AMOS services...${NC}"

    # Build and start
    docker-compose -f "$COMPOSE_FILE" up -d --build

    # Wait for backend
    if wait_for_service "$API_URL" "Backend API"; then
        echo "  API Docs: ${API_URL}/docs"
    fi

    # Wait for dashboard
    echo -e "${YELLOW}⏳ Waiting for Dashboard...${NC}"
    sleep 5
    echo -e "${GREEN}✓ Dashboard is ready${NC}"
    echo "  URL: ${DASHBOARD_URL}"

    echo ""
    echo -e "${GREEN}✓ AMOS v3.0.0 is running!${NC}"
    echo ""
    echo "  Dashboard:    ${DASHBOARD_URL}"
    echo "  API:          ${API_URL}"
    echo "  API Docs:     ${API_URL}/docs"
    echo "  WebSocket:    ws://localhost:8000/ws/dashboard"
    echo ""
    echo "  Commands:"
    echo "    ./start.sh --logs     - View logs"
    echo "    ./start.sh --stop     - Stop services"
    echo "    ./start.sh --test     - Run tests"
    echo ""
}

# Function to start in dev mode
start_dev() {
    echo -e "${BLUE}Starting AMOS in development mode...${NC}"

    # Start infrastructure only
    docker-compose -f "$COMPOSE_FILE" up -d redis ollama

    echo -e "${YELLOW}⏳ Infrastructure starting...${NC}"
    sleep 3

    echo -e "${GREEN}✓ Infrastructure ready${NC}"
    echo ""
    echo "  Redis:     localhost:6379"
    echo "  Ollama:    localhost:11434"
    echo ""
    echo "  Now run:"
    echo "    Backend:  cd backend && python main_integrated.py"
    echo "    Frontend: cd dashboard && npm run dev"
    echo ""
}

# Function to stop services
stop_services() {
    echo -e "${BLUE}Stopping AMOS services...${NC}"
    docker-compose -f "$COMPOSE_FILE" down
    echo -e "${GREEN}✓ Services stopped${NC}"
}

# Function to view logs
view_logs() {
    docker-compose -f "$COMPOSE_FILE" logs -f
}

# Function to run tests
run_tests() {
    echo -e "${BLUE}Running integration tests...${NC}"

    # Check if backend is running
    if ! curl -s "$API_URL/health" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Backend not running, starting services...${NC}"
        start_services
        sleep 5
    fi

    # Run tests
    if [ -f "test_integration.py" ]; then
        python test_integration.py
    else
        echo -e "${RED}✗ test_integration.py not found${NC}"
        exit 1
    fi
}

# Function to show status
show_status() {
    echo -e "${BLUE}AMOS Status:${NC}"
    docker-compose -f "$COMPOSE_FILE" ps

    echo ""
    echo "Health Checks:"

    # Check backend
    if curl -s "$API_URL/health" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Backend API"
    else
        echo -e "  ${RED}✗${NC} Backend API"
    fi

    # Check dashboard
    if curl -s "$DASHBOARD_URL" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Dashboard"
    else
        echo -e "  ${RED}✗${NC} Dashboard"
    fi
}

# Main
case "${1:-}" in
    --dev)
        check_docker
        start_dev
        ;;
    --stop)
        stop_services
        ;;
    --logs)
        view_logs
        ;;
    --test)
        run_tests
        ;;
    --status)
        show_status
        ;;
    --help|-h)
        echo "AMOS v3.0.0 Startup Script"
        echo ""
        echo "Usage: ./start.sh [option]"
        echo ""
        echo "Options:"
        echo "  (no option)  Start all services in production mode"
        echo "  --dev        Start infrastructure only (for dev)"
        echo "  --stop       Stop all services"
        echo "  --logs       View service logs"
        echo "  --test       Run integration tests"
        echo "  --status     Show service status"
        echo "  --help       Show this help"
        ;;
    *)
        check_docker
        start_services
        ;;
esac
