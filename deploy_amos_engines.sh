#!/bin/bash
# AMOS Engines Deployment Script
# Automates deployment to Docker, Kubernetes, or local

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_TYPE="${1:-docker}"
ENVIRONMENT="${2:-development}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    case $DEPLOYMENT_TYPE in
        docker)
            if ! command -v docker &> /dev/null; then
                log_error "Docker is not installed"
                exit 1
            fi
            if ! command -v docker-compose &> /dev/null; then
                log_error "Docker Compose is not installed"
                exit 1
            fi
            ;;
        k8s|kubernetes)
            if ! command -v kubectl &> /dev/null; then
                log_error "kubectl is not installed"
                exit 1
            fi
            if ! command -v helm &> /dev/null; then
                log_warn "Helm is not installed (optional)"
            fi
            ;;
        local)
            if ! command -v python3 &> /dev/null; then
                log_error "Python 3 is not installed"
                exit 1
            fi
            ;;
    esac

    log_info "Prerequisites check passed"
}

# Validate configuration
validate_config() {
    log_info "Validating configuration..."

    # Check required files exist
    local required_files=(
        "amos_temporal_engine.py"
        "amos_field_dynamics.py"
        "amos_self_evolution_test_suite.py"
        "amos_engine_integration.py"
        "amos_api_v2.py"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "$SCRIPT_DIR/$file" ]]; then
            log_error "Required file not found: $file"
            exit 1
        fi
    done

    # Run syntax check
    log_info "Running syntax validation..."
    for file in "${required_files[@]}"; do
        if ! python3 -m py_compile "$SCRIPT_DIR/$file" 2>/dev/null; then
            log_error "Syntax error in $file"
            exit 1
        fi
    done

    log_info "Configuration validation passed"
}

# Run performance benchmarks
run_benchmarks() {
    log_info "Running performance benchmarks..."

    if [[ -f "$SCRIPT_DIR/amos_performance_benchmark.py" ]]; then
        cd "$SCRIPT_DIR"
        if ! python3 amos_performance_benchmark.py --samples 50; then
            log_warn "Some benchmarks failed - review before production deployment"
        else
            log_info "All benchmarks passed"
        fi
    else
        log_warn "Benchmark script not found - skipping"
    fi
}

# Deploy with Docker
deploy_docker() {
    log_info "Deploying with Docker Compose..."

    cd "$SCRIPT_DIR"

    # Build and start services
    log_info "Building images..."
    docker-compose -f docker-compose.amos-engines.yml build

    log_info "Starting services..."
    docker-compose -f docker-compose.amos-engines.yml up -d

    # Wait for health checks
    log_info "Waiting for services to be healthy..."
    sleep 10

    # Check health
    if docker-compose -f docker-compose.amos-engines.yml ps | grep -q "healthy\|Up"; then
        log_info "Services are running"

        echo ""
        echo "AMOS Engines deployed successfully!"
        echo ""
        echo "Access points:"
        echo "  API:       http://localhost:8000"
        echo "  Health:    http://localhost:8080/health"
        echo "  Metrics:   http://localhost:9090"
        echo "  Grafana:   http://localhost:3000 (admin/admin)"
        echo ""
        echo "Commands:"
        echo "  View logs: docker-compose -f docker-compose.amos-engines.yml logs -f"
        echo "  Stop:      docker-compose -f docker-compose.amos-engines.yml down"
    else
        log_error "Services failed to start properly"
        docker-compose -f docker-compose.amos-engines.yml logs
        exit 1
    fi
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."

    cd "$SCRIPT_DIR"

    # Validate K8s manifests
    if [[ ! -f "$SCRIPT_DIR/k8s/amos-engines-deployment.yaml" ]]; then
        log_error "Kubernetes manifests not found"
        exit 1
    fi

    # Create namespace if it doesn't exist
    kubectl create namespace amos-engines --dry-run=client -o yaml | kubectl apply -f -

    # Apply manifests
    log_info "Applying Kubernetes manifests..."
    kubectl apply -f k8s/amos-engines-deployment.yaml

    # Wait for deployment
    log_info "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/amos-temporal-engine -n amos-engines || true
    kubectl wait --for=condition=available --timeout=300s deployment/amos-field-engine -n amos-engines || true

    # Check status
    log_info "Deployment status:"
    kubectl get pods -n amos-engines
    kubectl get svc -n amos-engines

    echo ""
    echo "AMOS Engines deployed to Kubernetes!"
    echo ""
    echo "Commands:"
    echo "  View pods:   kubectl get pods -n amos-engines"
    echo "  View logs:   kubectl logs -n amos-engines deployment/amos-temporal-engine"
    echo "  Port forward: kubectl port-forward -n amos-engines svc/amos-temporal-service 8000:8000"
}

# Deploy locally
deploy_local() {
    log_info "Deploying locally..."

    cd "$SCRIPT_DIR"

    # Install dependencies
    log_info "Installing dependencies..."
    pip install -q fastapi uvicorn numpy pytest

    # Run validation
    log_info "Running production validation..."
    if ! python3 amos_production_validation.py; then
        log_error "Production validation failed"
        exit 1
    fi

    # Start API server
    log_info "Starting API server..."
    echo ""
    echo "Starting server on http://localhost:8000"
    echo "Press Ctrl+C to stop"
    echo ""

    python3 -m uvicorn amos_api_v2:app --host 0.0.0.0 --port 8000 --reload
}

# Smoke test after deployment
run_smoke_tests() {
    log_info "Running smoke tests..."

    local base_url="http://localhost:8000"
    if [[ "$DEPLOYMENT_TYPE" == "k8s" ]] || [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]]; then
        base_url="http://amos-engines.local"
    fi

    # Test health endpoint
    if curl -s "$base_url/health" | grep -q "healthy"; then
        log_info "Health check passed"
    else
        log_warn "Health check failed or not yet available"
    fi

    # Run demo if available
    if [[ -f "$SCRIPT_DIR/amos_demo_multi_engine.py" ]]; then
        log_info "Running multi-engine demo..."
        python3 "$SCRIPT_DIR/amos_demo_multi_engine.py" || true
    fi
}

# Main deployment flow
main() {
    echo "======================================"
    echo "AMOS Engines Deployment Script"
    echo "======================================"
    echo ""

    if [[ "$1" == "help" ]] || [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        echo "Usage: $0 [deployment_type] [environment]"
        echo ""
        echo "Deployment types:"
        echo "  docker      - Deploy with Docker Compose (default)"
        echo "  k8s         - Deploy to Kubernetes"
        echo "  kubernetes  - Alias for k8s"
        echo "  local       - Run locally for development"
        echo ""
        echo "Environments:"
        echo "  development - Development mode (default)"
        echo "  production  - Production mode"
        echo ""
        echo "Examples:"
        echo "  $0 docker           # Docker deployment"
        echo "  $0 k8s production  # Kubernetes production"
        echo "  $0 local           # Local development"
        exit 0
    fi

    log_info "Deployment type: $DEPLOYMENT_TYPE"
    log_info "Environment: $ENVIRONMENT"
    echo ""

    # Execute deployment steps
    check_prerequisites
    validate_config

    if [[ "$ENVIRONMENT" == "production" ]]; then
        run_benchmarks
    fi

    case $DEPLOYMENT_TYPE in
        docker)
            deploy_docker
            ;;
        k8s|kubernetes)
            deploy_kubernetes
            ;;
        local)
            deploy_local
            ;;
        *)
            log_error "Unknown deployment type: $DEPLOYMENT_TYPE"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac

    if [[ "$DEPLOYMENT_TYPE" != "local" ]]; then
        run_smoke_tests
    fi

    echo ""
    log_info "Deployment complete!"
}

main "$@"
