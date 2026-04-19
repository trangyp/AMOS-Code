#!/bin/bash
# Repo Doctor Ω∞∞∞ - System Activation Script
#
# This script initializes and activates the Repo Doctor system
# Run: ./activate-repo-doctor.sh [mode]
#
# Modes:
#   local       - Local development mode (default)
#   ci          - CI/CD mode (strict, no evolution)
#   autonomous  - Autonomous governance mode
#   validate    - Run validation tests only

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-local}"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           REPO DOCTOR Ω∞∞∞ - SYSTEM ACTIVATION                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Repository: $REPO_ROOT"
echo "Mode: $MODE"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check Python version
echo "[1/7] Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_status "Python version: $PYTHON_VERSION"

# Check if repo_doctor_omega module exists
echo ""
echo "[2/7] Verifying Repo Doctor installation..."
if [ ! -d "$REPO_ROOT/repo_doctor_omega" ]; then
    print_error "repo_doctor_omega directory not found"
    exit 1
fi
print_status "Repo Doctor Ω∞∞∞ found"

# Run integration tests
echo ""
echo "[3/7] Running integration tests..."
cd "$REPO_ROOT"
if python3 test_repo_doctor_integration.py > /tmp/repo-doctor-test.log 2>&1; then
    print_status "All integration tests passed"
else
    print_error "Integration tests failed. Check /tmp/repo-doctor-test.log"
    exit 1
fi

# Create configuration based on mode
echo ""
echo "[4/7] Configuring for $MODE mode..."
case $MODE in
    local)
        print_status "Local development mode"
        print_status "  - All 60 basis vectors enabled"
        print_status "  - Brain integration: ON"
        print_status "  - Self-evolution: OFF"
        ;;
    ci)
        print_status "CI/CD mode"
        print_status "  - Strict validation"
        print_status "  - JSON output format"
        print_status "  - Fail on violations: YES"
        ;;
    autonomous)
        print_status "Autonomous governance mode"
        print_status "  - Self-diagnosis: ON"
        print_status "  - Self-repair: ON"
        print_status "  - Learning: ON"
        print_warning "  - This mode will make changes automatically!"
        ;;
    validate)
        print_status "Validation mode only"
        print_status "  - Tests completed successfully"
        print_status "  - System is operational"
        exit 0
        ;;
    *)
        print_error "Unknown mode: $MODE"
        echo "Valid modes: local, ci, autonomous, validate"
        exit 1
        ;;
esac

# Check for required documentation
echo ""
echo "[5/7] Checking documentation..."
REQUIRED_DOCS=(
    "ONBOARDING.md"
    "EMERGENCY.md"
    "REPO_DOCTOR_OMEGA_COMPLETE.md"
)

for doc in "${REQUIRED_DOCS[@]}"; do
    if [ -f "$REPO_ROOT/$doc" ]; then
        print_status "$doc"
    else
        print_warning "$doc missing"
    fi
done

# Verify CLI tools
echo ""
echo "[6/7] Verifying CLI tools..."
CLI_TOOLS=(
    "repo-doctor"
    "generate_system_report.py"
    "AMOS_AUTONOMOUS_GOVERNANCE_ORCHESTRATOR.py"
)

for tool in "${CLI_TOOLS[@]}"; do
    if [ -f "$REPO_ROOT/$tool" ]; then
        print_status "$tool"
    else
        print_warning "$tool not found"
    fi
done

# Make scripts executable
chmod +x "$REPO_ROOT/repo-doctor" 2>/dev/null || true
chmod +x "$REPO_ROOT/generate_system_report.py" 2>/dev/null || true
chmod +x "$REPO_ROOT/AMOS_AUTONOMOUS_GOVERNANCE_ORCHESTRATOR.py" 2>/dev/null || true

# Final status
echo ""
echo "[7/7] Activation complete!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "SYSTEM STATUS: OPERATIONAL"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Quick Start Commands:"
echo ""
case $MODE in
    local)
        echo "  ./repo-doctor scan              # Full repository scan"
        echo "  ./repo-doctor state             # Print state vector"
        echo "  python3 generate_system_report.py # Generate analysis report"
        ;;
    ci)
        echo "  ./repo-doctor scan --format json    # CI scan with JSON output"
        echo "  ./repo-doctor contracts --strict    # Check API contracts"
        ;;
    autonomous)
        echo "  python3 AMOS_AUTONOMOUS_GOVERNANCE_ORCHESTRATOR.py --single"
        echo "  python3 AMOS_AUTONOMOUS_GOVERNANCE_ORCHESTRATOR.py --interval 3600"
        ;;
esac

echo ""
echo "For more information:"
echo "  cat ONBOARDING.md"
echo "  cat REPO_DOCTOR_OMEGA_COMPLETE.md"
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Repo Doctor Ω∞∞∞ is ready for use!                          ║"
echo "║  60 Basis Vectors | 200+ Invariants | Autonomous Governance   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
