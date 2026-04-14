# Repo Doctor - Quick Start Guide

## Installation

```bash
# Clone or copy the repo_doctor package
cd repo_doctor

# Install in development mode
pip install -e .

# Install external sensors (optional but recommended)
pip install pip-audit ruff deptry tomli
npm install -g pyright
```

## Basic Usage

### 1. Full Repository Scan

```bash
# Scan current directory
repo-doctor scan .

# Scan with all sensors
repo-doctor scan . --sensors

# Scan with JSON output
repo-doctor scan . --json --output report.json
```

### 2. Check Specific Areas

```bash
# Check API contracts
repo-doctor scan . --contracts

# Check packaging
repo-doctor scan . --packaging

# Check entanglement (module coupling)
repo-doctor scan . --entanglement
```

### 3. Find Regressions

```bash
# Bisect to find first bad commit
repo-doctor bisect packaging . --good v1.0.0 --bad HEAD

# Auto-detect regression range
repo-doctor bisect tests .
```

### 4. Generate Repair Plan

```bash
# Generate fix plan
repo-doctor fix-plan . --export fixes.sh

# Apply fixes
bash fixes.sh
```

## Understanding the Output

### State Vector Report

```
Ψ_repo(t) = [s, i, b, τ, p, a, d, c, h, σ]

[✓] s      = 1.000   (Syntax - all files parse)
[✓] i      = 1.000   (Imports - no broken imports)
[✓] b      = 1.000   (Build - builds successfully)
[✓] τ      = 1.000   (Tests - all pass)
[✓] p      = 1.000   (Packaging - valid metadata)
[✓] a      = 1.000   (API - contracts valid)
[✗] d      = 0.000   (Dependencies - issues found)
[✓] c      = 1.000   (Entrypoints - all valid)
[✗] h      = 0.000   (History - git issues)
[✗] σ      = 0.000   (Security - vulnerabilities)

Score: 70/100
Releaseable: False
Collapsed Subsystem: dependencies
```

### Metrics

- **Score**: 0-100 based on weighted dimension values
- **Energy**: Lower is better (0 = perfect state)
- **Releaseable**: True if all hard-fail dimensions pass

## CI/CD Integration

### GitHub Actions

```yaml
name: Repo Health Check
on: [push, pull_request]

jobs:
  health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install repo-doctor
        run: pip install -e ./repo_doctor
      
      - name: Run health check
        run: repo-doctor scan . --sensors
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: repo-doctor
        name: Repository Health Check
        entry: repo-doctor scan .
        language: system
        pass_filenames: false
        always_run: true
```

## Configuration

### pyproject.toml

```toml
[tool.repo-doctor]
# Exclude patterns
exclude = ["tests/fixtures", "*.pyc", "__pycache__"]

# Dimension weights (for scoring)
[tool.repo-doctor.weights]
syntax = 1.0
imports = 1.0
build = 1.0
tests = 1.5
packaging = 2.0
api = 1.0
dependencies = 1.0
entrypoints = 2.0
history = 0.5
security = 2.0

# Hard-fail dimensions (must pass for release)
[tool.repo-doctor.hard_fail]
packaging = true
entrypoints = true
```

## Troubleshooting

### "Module not found" errors

If running from within the package directory, the entrypoint checker looks for modules relative to the current directory. For packages like `repo_doctor.cli`, it checks:
1. `repo_doctor/cli.py` (standard)
2. `cli.py` (if current dir is `repo_doctor`)

### tomllib errors on Python < 3.11

Install `tomli`:
```bash
pip install tomli
```

### Sensor not available

External sensors are optional. Install them:
```bash
pip install pip-audit ruff deptry
npm install -g pyright
```

## Next Steps

1. Run `repo-doctor scan . --sensors` to get baseline
2. Fix critical issues (Releaseable = False)
3. Set up CI/CD integration
4. Configure thresholds in pyproject.toml
5. Use `bisect` to find regression commits
