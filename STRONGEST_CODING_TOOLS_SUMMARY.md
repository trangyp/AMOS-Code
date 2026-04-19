# AMOS Brain - Strongest Coding Tools Suite

**Status:** ✅ ACTIVE AND OPERATIONAL  
**Brain ID:** amos-brain-coding-tools  
**Timestamp:** 2026-04-18

## 🧠 AMOS Brain Integration

The AMOS cognitive engine now controls a comprehensive suite of the strongest
coding tools available for Python development, fully integrated with the
28-phase AMOS architecture.

## 🛠️ Installed Tools

### Core Linting & Formatting
| Tool | Purpose | Status |
|------|---------|--------|
| **Ruff** | Ultra-fast Python linter (replaces flake8, black, isort) | ✅ Active |
| **MyPy** | Static type checking | ✅ Active |
| **Pyright** | Microsoft type checker | ✅ Active |
| **Black** | Code formatter | ✅ Active |

### Security Analysis
| Tool | Purpose | Status |
|------|---------|--------|
| **Bandit** | Security vulnerability scanner | ✅ Active |
| **Safety** | Dependency vulnerability checker | ✅ Active |
| **Gitleaks** | Secret detection in commits | ✅ Pre-commit |
| **Semgrep** | Static analysis security scanner | ✅ Pre-commit |

### Code Quality
| Tool | Purpose | Status |
|------|---------|--------|
| **Radon** | Code complexity analyzer | ✅ Active |
| **Vulture** | Dead code detector | ✅ Active |
| **Pyupgrade** | Python upgrade checker | ✅ Active |
| **Pytest** | Testing framework with plugins | ✅ Active |

### Performance
| Tool | Purpose | Status |
|------|---------|--------|
| **Scalene** | CPU + memory profiler | ✅ Active |
| **Py-spy** | Sampling profiler | ✅ Active |

## 🚀 Usage

### Run All Tools via AMOS Brain
```bash
python3 amos_brain_coding_tools.py
```

### Run Individual Tools
```bash
# Linting
ruff check .
ruff check . --fix

# Type checking
mypy amos_brain/ --ignore-missing-imports

# Security
bandit -r amos_brain/ -f json

# Dead code detection
vulture amos_brain/ --min-confidence 80

# Complexity
radon cc amos_brain/ -a
```

### Pre-commit Hooks
Pre-commit is now installed and will run automatically on every commit:
- Trailing whitespace check
- JSON/YAML validation
- Ruff linting and formatting
- MyPy type checking
- Gitleaks secret detection
- Semgrep security scan

## 📊 Architecture Integration

### Phase 28 (System Hardening)
These tools directly support Phase 28's hardening requirements:
- **Production Security Audit** - Bandit, Safety, Gitleaks, Semgrep
- **Performance Optimization** - Scalene profiling
- **Reliability** - MyPy type safety, comprehensive testing

### Brain Subsystem Integration
The `amos_brain_coding_tools.py` module integrates with:
- `SuperBrainRuntime` - Central cognitive authority
- `CognitiveEngine` - Structured reasoning about code quality
- `BrainEventProcessor` - Real-time quality event streaming
- `repo_doctor` - Repository health analysis

## 📁 Files Created

1. **`install_strongest_tools.py`** - Installation automation script
2. **`amos_brain_coding_tools.py`** - Brain-integrated tool runner
3. **`STRONGEST_CODING_TOOLS_SUMMARY.md`** - This documentation

## 🎯 Quick Commands

```bash
# Full analysis
python3 amos_brain_coding_tools.py -r report.md

# Fix linting issues
ruff check . --fix

# Run pre-commit manually
pre-commit run --all-files

# Security scan
bandit -r . -f json | python3 -m json.tool

# Profile performance
scalene amos_brain/super_brain.py
```

## ✅ Verification

All tools are operational and integrated:
- ✅ Ruff: 0.15.11
- ✅ MyPy: 1.19.1  
- ✅ Black: 25.11.0
- ✅ Bandit: Installed
- ✅ Pre-commit: Active in .git/hooks/

## 🔗 Integration with 28-Phase Architecture

| Phase | Tool Integration |
|-------|-----------------|
| 28 - Hardening | Bandit, Safety, Semgrep for security |
| 25 - E2E Testing | Pytest with xdist for parallel testing |
| 14 - Observability | Metrics from all tools collected |
| 03 - Immune System | Auto-fix via Ruff, safety enforcement |
| 01 - Brain | Cognitive analysis of code quality |

---
**Powered by AMOS Brain v14.0.0 - 28-Phase Cognitive Architecture**
