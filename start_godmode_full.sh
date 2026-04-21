#!/bin/bash
# AMOS GODMODE Full System Startup
# =================================
# Activates all AMOS subsystems in OMEGA mode

set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

echo "======================================================================"
echo "AMOS GODMODE - FULL SYSTEM ACTIVATION"
echo "======================================================================"
echo "Root: $REPO_ROOT"
echo "Mode: OMEGA (Full System)"
echo "======================================================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi
echo "✓ Python3: $(python3 --version)"

# Check 6 repos
echo ""
echo "Checking 6 Repository Links..."
for repo in AMOS-Code AMOS-Consulting AMOS-Claws Mailinhconect AMOS-Invest AMOS-UNIVERSE; do
    if [ -d "AMOS_REPOS/$repo" ]; then
        echo "  ✓ $repo"
    else
        echo "  ✗ $repo (missing)"
    fi
done

# Check Organism OS
if [ -d "AMOS_ORGANISM_OS" ]; then
    echo ""
    echo "✓ Organism OS: 15 subsystems available"
fi

# Check Canon
echo ""
echo "Checking Canonical Structure..."
if [ -d "_00_AMOS_CANON" ]; then
    echo "  ✓ _00_AMOS_CANON: $(ls _00_AMOS_CANON | wc -l) items"
fi

# Initialize environment
echo ""
echo "Initializing Environment..."
export PYTHONPATH="${REPO_ROOT}:${PYTHONPATH}"
export AMOS_MODE="omega"
export AMOS_ROOT="$REPO_ROOT"

# Launch GODMODE
echo ""
echo "======================================================================"
echo "🔱 LAUNCHING GODMODE CONTROLLER"
echo "======================================================================"
python3 AMOS_GODMODE.py --mode omega "$@"
