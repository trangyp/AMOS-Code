#!/bin/bash
# Security Scanner Installation Script for AMOS Platform
# Installs: Semgrep, Trivy, Gitleaks, OSV-Scanner, Ruff, Pyright, act

set -e

echo "Installing AMOS Security Scanners..."
echo "===================================="

# Detect OS
OS=""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    if command -v apt-get &> /dev/null; then
        DISTRO="debian"
    elif command -v yum &> /dev/null; then
        DISTRO="rhel"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
fi

echo "Detected OS: $OS"

# Install Python tools first
echo ""
echo "Installing Python security tools..."
pip install --user semgrep ruff pyright pre-commit 2>/dev/null || pip install semgrep ruff pyright pre-commit

# Install Semgrep (if pip install didn't work)
if ! command -v semgrep &> /dev/null; then
    echo "Installing Semgrep via official installer..."
    if [[ "$OS" == "macos" ]]; then
        brew install semgrep 2>/dev/null || pip install semgrep
    elif [[ "$OS" == "linux" ]]; then
        pip install semgrep || {
            curl -fsSL https://get.semgrep.dev | sh
            export PATH="$HOME/.semgrep/bin:$PATH"
        }
    fi
fi

# Install Trivy
echo ""
echo "Installing Trivy..."
if ! command -v trivy &> /dev/null; then
    if [[ "$OS" == "macos" ]]; then
        brew install aquasecurity/trivy/trivy 2>/dev/null || brew install trivy
    elif [[ "$OS" == "linux" ]]; then
        # Official Trivy install script
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
    fi
else
    echo "Trivy already installed: $(trivy version)"
fi

# Install Gitleaks
echo ""
echo "Installing Gitleaks..."
if ! command -v gitleaks &> /dev/null; then
    if [[ "$OS" == "macos" ]]; then
        brew install gitleaks
    elif [[ "$OS" == "linux" ]]; then
        # Download latest release
        GITLEAKS_VERSION="8.18.2"
        curl -sSL "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz" | \
            tar -xz -C /tmp && \
            sudo mv /tmp/gitleaks /usr/local/bin/
    fi
else
    echo "Gitleaks already installed: $(gitleaks version)"
fi

# Install OSV-Scanner
echo ""
echo "Installing OSV-Scanner..."
if ! command -v osv-scanner &> /dev/null; then
    if [[ "$OS" == "macos" ]]; then
        brew install osv-scanner
    elif [[ "$OS" == "linux" ]]; then
        # Download from GitHub releases
        OSV_VERSION="1.4.3"
        curl -sSL "https://github.com/google/osv-scanner/releases/download/v${OSV_VERSION}/osv-scanner_${OSV_VERSION}_linux_amd64" -o /tmp/osv-scanner && \
            chmod +x /tmp/osv-scanner && \
            sudo mv /tmp/osv-scanner /usr/local/bin/
    fi
else
    echo "OSV-Scanner already installed"
fi

# Install act (for GitHub Actions testing)
echo ""
echo "Installing act (GitHub Actions local runner)..."
if ! command -v act &> /dev/null; then
    if [[ "$OS" == "macos" ]]; then
        brew install act
    elif [[ "$OS" == "linux" ]]; then
        curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
    fi
else
    echo "act already installed: $(act --version)"
fi

# Verify installations
echo ""
echo "===================================="
echo "Verifying installations..."
echo "===================================="

TOOLS=("semgrep" "trivy" "gitleaks" "osv-scanner" "ruff" "pyright" "act")
ALL_INSTALLED=true

for tool in "${TOOLS[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo "✅ $tool: $(which $tool)"
    else
        echo "❌ $tool: NOT FOUND"
        ALL_INSTALLED=false
    fi
done

echo ""
if [ "$ALL_INSTALLED" = true ]; then
    echo "✅ All security scanners installed successfully!"
    echo ""
    echo "Usage:"
    echo "  semgrep --config=auto .              # Static analysis"
    echo "  trivy fs .                           # Vulnerability scan"
    echo "  gitleaks detect .                    # Secret detection"
    echo "  osv-scanner scan .                   # Dependency check"
    echo "  ruff check .                         # Python linting"
    echo "  pyright .                            # Type checking"
    echo "  act                                  # Test GitHub Actions"
else
    echo "⚠️  Some tools failed to install. Check error messages above."
    exit 1
fi
