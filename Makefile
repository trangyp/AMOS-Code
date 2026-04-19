# AMOS Equation System v2.0 - Makefile
#
# Production-grade commands for development, testing, and deployment.
# Python 3.10+ | FastAPI | PostgreSQL | Redis | Celery
#
# Quick Start:
#   make install      - Install dependencies
#   make dev          - Start development with docker-compose
#   make test         - Run all tests
#   make build        - Build production Docker image
#
# Creator: Trang Phan
# Version: 2.0.0

.PHONY: help dev build test deploy clean lint format install

# Default target
help:
	@echo "AMOS Equation System v2.0 - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Start full stack with docker-compose"
	@echo "  make dev-api          - Run API locally (uvicorn)"
	@echo "  make dev-worker       - Run Celery worker locally"
	@echo "  make dev-beat         - Run Celery beat scheduler locally"
	@echo ""
	@echo "Building:"
	@echo "  make build            - Build production Docker image"
	@echo "  make build-no-cache   - Build without cache"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-coverage    - Run with coverage report"
	@echo "  make lint             - Run linters (ruff, mypy)"
	@echo "  make format           - Format code (black)"
	@echo "  make security         - Security scan (bandit, safety)"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate       - Run Alembic migrations"
	@echo "  make db-upgrade       - Upgrade database to latest"
	@echo "  make db-downgrade     - Downgrade database"
	@echo "  make db-seed          - Seed development data"
	@echo ""
	@echo "Deployment:"
	@echo "  make up               - Start with docker-compose"
	@echo "  make down             - Stop docker-compose"
	@echo "  make logs             - View logs"
	@echo "  make k8s-deploy       - Deploy to Kubernetes"
	@echo "  make k8s-delete       - Remove from Kubernetes"
	@echo ""
	@echo "SuperBrain Governance (v2.0.0):"
	@echo "  make sb-deploy-dev    - Deploy to dev environment"
	@echo "  make sb-deploy-stg    - Deploy to staging"
	@echo "  make sb-deploy-prod   - Deploy to production"
	@echo "  make sb-verify        - Verify all integrations"
	@echo "  make sb-health        - Check SuperBrain health"
	@echo "  make sb-dashboard     - Open CloudWatch dashboard"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            - Clean build artifacts"
	@echo "  make install          - Install dependencies"
	@echo "  make health           - Check API health"
	@echo "  make version          - Show version info"

# ============================================
# Development
# ============================================

dev:
	@echo "Starting AMOS Equation System..."
	@docker-compose up -d
	@echo ""
	@echo "Services available:"
	@echo "  API:        http://localhost:8000"
	@echo "  API Docs:   http://localhost:8000/docs"
	@echo "  Flower:     http://localhost:5555"
	@echo "  Prometheus: http://localhost:9090"
	@echo "  Grafana:    http://localhost:3000"

dev-api:
	@echo "Starting API server locally..."
	@uvicorn equation_app:create_app --reload --host 0.0.0.0 --port 8000

dev-worker:
	@echo "Starting Celery worker locally..."
	@celery -A equation_tasks worker --loglevel=info --concurrency=4

dev-beat:
	@echo "Starting Celery beat scheduler locally..."
	@celery -A equation_tasks beat --loglevel=info

# ============================================
# Building
# ============================================

build:
	@echo "Building AMOS Equation System Docker image..."
	@docker build -t amos-equation-system:latest .

build-no-cache:
	@echo "Building AMOS Equation System (no cache)..."
	@docker build --no-cache -t amos-equation-system:latest .

# ============================================
# Testing
# ============================================

test:
	@echo "Running all tests..."
	@python test_production_stack.py || python -m pytest tests/ -v --tb=short

test-integration:
	@echo "Running integration tests..."
	@python test_production_stack.py

test-coverage:
	@echo "Running tests with coverage..."
	@python -m pytest tests/ -v --cov=equation_ --cov-report=html --cov-report=term

# ============================================
# Deployment
# ============================================

up:
	@docker-compose up -d

down:
	@docker-compose down

logs:
	@docker-compose logs -f

logs-api:
	@docker-compose logs -f api

logs-worker:
	@docker-compose logs -f celery-worker

k8s-deploy:
	@echo "Deploying to Kubernetes..."
	@kubectl apply -k k8s/
	@echo "Deployment complete!"

k8s-delete:
	@echo "Removing from Kubernetes..."
	@kubectl delete -k k8s/
	@echo "Removed!"

# ============================================
# Maintenance
# ============================================

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf __pycache__ */__pycache__ */*/__pycache__
	@rm -rf .pytest_cache .mypy_cache .ruff_cache
	@rm -rf htmlcov *.egg-info dist build
	@docker-compose down -v 2>/dev/null || true
	@echo "Clean complete!"

docker-clean:
	@docker system prune -f
	@docker volume prune -f

lint:
	@echo "Running linters..."
	@ruff check equation_*.py amos_api_gateway.py || true
	@mypy equation_*.py --ignore-missing-imports || true

lint-strict:
	@echo "Running strict linting..."
	@ruff check equation_*.py amos_api_gateway.py
	@mypy equation_*.py --ignore-missing-imports

format:
	@echo "Formatting code..."
	@black equation_*.py amos_api_gateway.py || echo "Install black: pip install black"

format-check:
	@echo "Checking formatting..."
	@black --check equation_*.py amos_api_gateway.py

security:
	@echo "Running security scans..."
	@bandit -r equation_*.py -f screen || true
	@safety check || true

install:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt -r requirements-dev.txt

install-prod:
	@echo "Installing production dependencies..."
	@pip install -r requirements.txt

update:
	@echo "Updating dependencies..."
	@pip install --upgrade -r requirements.txt -r requirements-dev.txt

# ============================================
# Database (optional)
# ============================================

db-init:
	@echo "Initializing database..."
	@python equation_migrations.py init

db-migrate:
	@echo "Creating migration..."
	@python equation_migrations.py revision --autogenerate -m "$(message)"

db-upgrade:
	@echo "Upgrading database..."
	@python equation_migrations.py upgrade head

db-downgrade:
	@echo "Downgrading database..."
	@python equation_migrations.py downgrade -1

db-seed:
	@echo "Seeding development data..."
	@python equation_seeder.py --users 10 --equations 50

db-reset:
	@echo "Resetting database..."
	@python equation_migrations.py downgrade base
	@python equation_migrations.py upgrade head
	@python equation_seeder.py --users 5 --equations 20

# ============================================
# Utilities
# ============================================

health:
	@echo "Checking API health..."
	@curl -s http://localhost:8000/health/live | jq . 2>/dev/null || echo "API not running at localhost:8000"
	@curl -s http://localhost:8000/health/ready | jq . 2>/dev/null || echo "API not ready"

api-docs:
	@echo "API Documentation URLs:"
	@echo "  Swagger UI: http://localhost:8000/docs"
	@echo "  ReDoc:      http://localhost:8000/redoc"

admin:
	@echo "Admin CLI Commands:"
	@echo "  python equation_admin.py --help"

seed:
	@echo "Seeding data..."
	@python equation_seeder.py --users 20 --equations 100 --clear

version:
	@echo "AMOS Equation System v2.0.0"
	@echo "Python 3.10+ | FastAPI | PostgreSQL | Redis | Celery"
	@echo "Architecture: 7-Layer Enterprise Design (35 Modules)"
	@echo "SuperBrain Governance: v2.0.0 (10 systems, 4,644 features)"

# ============================================
# SuperBrain Governance v2.0.0
# ============================================

sb-deploy-dev:
	@echo "Deploying SuperBrain to dev environment..."
	@bash scripts/deploy.sh dev

sb-deploy-stg:
	@echo "Deploying SuperBrain to staging environment..."
	@bash scripts/deploy.sh staging

sb-deploy-prod:
	@echo "Deploying SuperBrain to production environment..."
	@echo "WARNING: This will deploy to production!"
	@read -p "Continue? (yes/no): " confirm && [ "$$confirm" = "yes" ] && bash scripts/deploy.sh prod

sb-verify:
	@echo "Verifying SuperBrain integration..."
	@bash scripts/verify-integration.sh dev

sb-verify-stg:
	@echo "Verifying SuperBrain integration (staging)..."
	@bash scripts/verify-integration.sh staging

sb-verify-prod:
	@echo "Verifying SuperBrain integration (production)..."
	@bash scripts/verify-integration.sh prod

sb-health:
	@echo "Checking SuperBrain health..."
	@cd terraform && SUPERBRAIN_HEALTH=$$(terraform output -raw superbrain_health_endpoint 2>/dev/null) && \
	curl -s "http://$$SUPERBRAIN_HEALTH/superbrain" | python -m json.tool 2>/dev/null || \
	echo "SuperBrain health endpoint not available. Run 'make sb-deploy-dev' first."

sb-dashboard:
	@echo "Opening CloudWatch dashboard..."
	@cd terraform && DASHBOARD=$$(terraform output -raw amos_dashboard_url 2>/dev/null) && \
	if [ -n "$$DASHBOARD" ]; then \
		open "$$DASHBOARD" 2>/dev/null || echo "Dashboard URL: $$DASHBOARD"; \
	else \
		echo "Dashboard URL not available. Run 'make sb-deploy-dev' first."; \
	fi

sb-status:
	@echo "SuperBrain Governance Status:"
	@echo "  Version: 2.0.0"
	@echo "  Systems Governed: 12"
	@echo "  Features: 4,644"
	@echo "  Health Check: /health/superbrain"
	@echo "  Documentation: docs/SUPERBRAIN_INTEGRATION_GUIDE.md"

sb-validate:
	@./scripts/validate-architecture.sh
