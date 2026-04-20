#!/bin/bash
# ============================================================================
# AMOS Tool Lattice - Installation Script
# Six-Kernel Architecture Setup
# ============================================================================

set -e

echo "🔧 AMOS Tool Lattice Installation"
echo "=================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Install Python 3.11
uv python install 3.11

# Create virtual environment
echo "🐍 Creating virtual environment..."
uv venv --python 3.11
source .venv/bin/activate

# Install first-order tools (non-negotiables)
echo "🎯 Installing first-order tools..."
uv pip install pre-commit ruff pydantic pytest pytest-asyncio hypothesis

# Install enforcement layer
echo "🔒 Installing enforcement tools..."
uv pip install import-linter jscpd deptry bandit pip-audit

# Install numeric kernel
echo "⚡ Installing numeric kernel..."
uv pip install numba numpy polars

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install --install-hooks

echo ""
echo "✅ AMOS Tool Lattice installed successfully!"
echo ""
echo "Available commands:"
echo "  pre-commit run --all-files     # Run all checks"
echo "  ruff check .                   # Lint code"
echo "  ruff format .                  # Format code"
echo "  mypy .                         # Type check"
echo "  pytest -q                      # Run tests"
echo "  lint-imports                   # Check architecture"
echo "  deptry .                       # Check dependencies"
echo "  bandit -r .                    # Security scan"
echo ""
