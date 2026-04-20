# AMOS Brain v14.0.0 - Makefile
#
# Production-grade commands for development, testing, and deployment.
# Python 3.10+ | FastAPI | PostgreSQL | Redis | Celery
#
# Quick Start:
#   make install      - Install package with all extras
#   make dev          - Start development with docker-compose
#   make test         - Run all tests
#   make build        - Build production Docker image
#
# Creator: Trang Phan
# Version: 14.0.0

.PHONY: help dev build test deploy clean lint format install

# Default target
help:
	@echo "AMOS Brain v14.0.0 - Available Commands"
	@echo "======================================="
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
	@echo "  make lint             - Run linters (ruff, mypy) - STRICT"
	@echo "  make lint-check       - Check linting without fixing"
	@echo "  make format           - Format code (black)"
	@echo "  make security         - Security scan (bandit, safety) - STRICT"
	@echo ""
	@echo "Package:"
	@echo "  make install          - Install package with all extras"
	@echo "  make install-dev      - Install package with dev extras"
	@echo "  make build-wheel      - Build wheel distribution"
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
	@echo "Utilities:"
	@echo "  make clean            - Clean build artifacts"
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
	@amos-brain --server --reload --host 0.0.0.0 --port 8000

dev-worker:
	@echo "Starting Celery worker locally..."
	@celery -A amos_brain.celery_app worker --loglevel=info --concurrency=4

dev-beat:
	@echo "Starting Celery beat scheduler locally..."
	@celery -A amos_brain.celery_app beat --loglevel=info

# ============================================
# Building
# ============================================

build:
	@echo "Building AMOS Brain Docker image..."
	@docker build -t amos-brain:14.0.0 -t amos-brain:latest .

build-no-cache:
	@echo "Building AMOS Brain (no cache)..."
	@docker build --no-cache -t amos-brain:14.0.0 -t amos-brain:latest .

# ============================================
# Testing
# ============================================

test:
	@echo "Running all tests..."
	@python -m pytest tests/ -v --tb=short

test-integration:
	@echo "Running integration tests..."
	@python -m pytest tests/integration/ -v --tb=short -m integration

test-coverage:
	@echo "Running tests with coverage..."
	@python -m pytest tests/ -v --cov=amos_brain --cov=amosl --cov-report=html --cov-report=term

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
	@echo "Running linters (strict - will fail on errors)..."
	@ruff check amos_brain amosl amos_model_fabric
	@mypy amos_brain amosl --ignore-missing-imports

lint-check:
	@echo "Checking linting without fixing..."
	@ruff check amos_brain amosl amos_model_fabric --no-fix

format:
	@echo "Formatting code..."
	@black amos_brain amosl amos_model_fabric

format-check:
	@echo "Checking formatting..."
	@black --check amos_brain amosl amos_model_fabric

security:
	@echo "Running security scans (strict - will fail on issues)..."
	@bandit -r amos_brain amosl -f screen
	@safety check

install:
	@echo "Installing AMOS Brain with all extras..."
	@pip install -e ".[all]"

install-dev:
	@echo "Installing AMOS Brain with dev extras..."
	@pip install -e ".[dev]"

install-prod:
	@echo "Installing production dependencies..."
	@pip install -e ".[server,database,security,events,ml]"

build-wheel:
	@echo "Building wheel distribution..."
	@python -m build

update:
	@echo "Updating dependencies..."
	@pip install --upgrade -e ".[all]"

# ============================================
# Database (optional)
# ============================================

db-init:
	@echo "Initializing database..."
	@amos-brain db init

db-migrate:
	@echo "Creating migration..."
	@amos-brain db migrate -m "$(message)"

db-upgrade:
	@echo "Upgrading database..."
	@amos-brain db upgrade

db-downgrade:
	@echo "Downgrading database..."
	@amos-brain db downgrade

db-seed:
	@echo "Seeding development data..."
	@amos-brain db seed --users 10 --equations 50

db-reset:
	@echo "Resetting database..."
	@amos-brain db reset

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
	@echo "AMOS Brain v14.0.0"
	@echo "Python 3.10+ | FastAPI | PostgreSQL | Redis | Celery"
	@echo "Architecture: 14-Layer Cognitive OS"
	@echo "Package: amos-brain"
	@echo "Entrypoints: amos-brain, amos-cli, amos-launcher"

# ============================================
# Deployment Helpers
# ============================================

deploy-dev:
	@echo "Deploying to dev environment..."
	@bash scripts/deploy.sh dev

deploy-staging:
	@echo "Deploying to staging environment..."
	@bash scripts/deploy.sh staging

deploy-prod:
	@echo "Deploying to production environment..."
	@echo "WARNING: This will deploy to production!"
	@read -p "Continue? (yes/no): " confirm && [ "$$confirm" = "yes" ] && bash scripts/deploy.sh prod
