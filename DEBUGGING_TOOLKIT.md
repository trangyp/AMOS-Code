# AMOS Debugging Toolkit - Professional Edition

## ✅ Installed Python Debugging Tools

| Tool | Purpose | Quick Use |
|------|---------|-----------|
| **debugpy** | VS Code remote debugging | `python -m debugpy --listen 5678 script.py` |
| **pudb** | Visual console debugger | `python -m pudb script.py` |
| **ipdb** | Enhanced pdb with IPython | `import ipdb; ipdb.set_trace()` |
| **icecream** | Elegant print debugging | `from icecream import ic; ic(var)` |
| **rich** | Beautiful output/tracebacks | `from rich import traceback; traceback.install()` |
| **traceback-with-variables** | Verbose error context | Auto-shows locals in tracebacks |
| **py-spy** | Sampling profiler (no code changes) | `py-spy top --pid <pid>` |
| **memray** | Memory profiler | `python -m memray run script.py` |
| **line_profiler** | Line-by-line profiling | `@profile` decorator |
| **pytest** | Testing framework | `pytest -v --tb=short` |
| **pytest-cov** | Test coverage | `pytest --cov=amos --cov-report=html` |
| **hypothesis** | Property-based testing | `@given(st.integers())` |
| **loguru** | Modern logging | `from loguru import logger` |
| **structlog** | Structured logging | `structlog.get_logger()` |
| **bandit** | Security linter | `bandit -r amos/` |
| **mypy** | Static type checker | `mypy amos/` |
| **black** | Code formatter | `black amos/` |
| **isort** | Import sorter | `isort amos/` |

---

## 🔥 Quick Start Examples

### 1. Print Debugging (icecream)
```python
from icecream import ic
ic.configureOutput(prefix='[AMOS] ', includeContext=True)

# Use anywhere:
ic(variable_name)  # [AMOS] variable_name: value
ic()  # Shows file:line and current function
```

### 2. Interactive Debugging (ipdb)
```python
# Add breakpoint anywhere:
import ipdb; ipdb.set_trace()

# Commands: n (next), s (step), c (continue), 
#           l (list), p var (print), q (quit)
```

### 3. Visual Debugging (pudb)
```bash
# Run entire script with visual debugger:
python -m pudb amos_coherence_engine.py

# Or inline:
import pudb; pudb.set_trace()
```

### 4. Production Debugging (loguru)
```python
from loguru import logger

logger.add("amos_debug.log", rotation="500 MB", level="DEBUG")
logger.debug("Coherence state: {}", coherence_state)
logger.info("Decision made: {}", decision)
```

### 5. Performance Profiling
```bash
# Real-time CPU profiling (no code changes!)
py-spy top -- python amos_coherence_engine.py

# Memory profiling
python -m memray run amos_coherence_engine.py
python -m memray flamegraph memray-*.bin

# Line-by-line profiling
kernprof -l -v amos_coherence_engine.py
```

### 6. Beautiful Errors (rich)
```python
from rich.traceback import install
install(show_locals=True, width=120)

# All exceptions now show:
# - Full stack trace with syntax highlighting
# - Local variable values at each frame
# - Clean, readable formatting
```

---

## 🧪 Testing & Quality

### Run tests with coverage:
```bash
pytest amos/ -v --tb=short --cov=amos --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Property-based testing (hypothesis):
```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=0), st.integers(min_value=0))
def test_coherence_metrics(x, y):
    result = calculate_coherence(x, y)
    assert 0 <= result <= 1
```

### Security scan:
```bash
bandit -r amos/ -f html -o security_report.html
```

### Type checking:
```bash
mypy amos/ --ignore-missing-imports
```

---

## 🖥️ VS Code Configuration

### launch.json:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: AMOS Debug",
      "type": "debugpy",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": false,
      "env": { "PYTHONPATH": "${workspaceFolder}" }
    },
    {
      "name": "Python: Remote Attach",
      "type": "debugpy",
      "request": "attach",
      "connect": { "host": "localhost", "port": 5678 }
    }
  ]
}
```

### settings.json:
```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.autoTestDiscoverOnSaveEnabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.provider": "isort",
  "python.linting.mypyEnabled": true,
  "python.linting.banditEnabled": true
}
```

---

## 🔧 System Debugging (macOS Built-in)

### GUI Tools:
- **Instruments** (`Cmd+Space` → "Instruments") - CPU, Memory, Network profiling
- **Console** - System logs
- **Activity Monitor** - Process monitoring

### Command Line:
```bash
# File system activity
sudo fs_usage -w | grep -i amos

# Network debugging
sudo tcpdump -i any port 8080
nettop
lsof -i :8080

# Performance analysis
sample <pid> 10 1        # 10-second CPU sample
spindump <pid>           # Full stack trace
sudo dtrace -n 'syscall::open*:entry { printf("%s %s", execname, copyinstr(arg0)); }'

# Memory analysis
sudo vmmap <pid>
leaks <pid>
```

---

## 🎯 AMOS-Specific Debugging

### Coherence Engine Debugging:
```python
from icecream import ic
from amos_coherence_engine import get_coherence_state

# Monitor coherence decisions:
ic.configureOutput(prefix='[AMOS-COHERENCE] ')

def debug_coherence(input_data):
    state = get_coherence_state()
    ic(state.confidence, state.metrics)
    return process_coherence(input_data)
```

### Async Debugging:
```python
import asyncio
import logging

# Enable asyncio debug mode:
asyncio.get_event_loop().set_debug(True)
logging.basicConfig(level=logging.DEBUG)

# Or set environment variable:
# PYTHONASYNCIODEBUG=1 python script.py
```

### Decision Flow Tracing:
```python
import functools
from icecream import ic

def trace_decisions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ic(func.__name__, args, kwargs)
        result = func(*args, **kwargs)
        ic(result)
        return result
    return wrapper

# Use decorator:
@trace_decisions
def make_decision(context):
    # ... decision logic ...
    pass
```

---

## 📊 Network Debugging

### HTTP Debugging:
```bash
# If you install httpie:
pip3 install --user httpie

# Then use:
http GET localhost:8080/api/status
http POST localhost:8080/api/decision context=test
```

### Built-in alternatives:
```bash
# Quick HTTP server
python3 -m http.server 8080

# Test with curl
curl -v http://localhost:8080
```

---

## 🚀 One-Liner Debug Setup

Add to your `~/.zshrc` or `~/.bashrc`:
```bash
# Quick debug aliases
alias pydb='python -m pudb'
alias pyprofile='python -m cProfile -s cumulative'
alias pycov='pytest --cov --cov-report=html && open htmlcov/index.html'
alias amos-debug='PYTHONASYNCIODEBUG=1 python -m pudb'
```

---

## 🔒 Open-Source Security Scanning Stack

AMOS uses a fully open-source (Apache-2.0/MIT licensed) security toolchain with no proprietary dependencies.

### Security Tools Overview

| Tool | License | Purpose | Coverage |
|------|---------|---------|----------|
| **Semgrep CE** | LGPL-2.1 | Static analysis | 30+ languages, custom rules |
| **Trivy** | Apache-2.0 | Vulnerability scanning | Code, containers, K8s |
| **Gitleaks** | MIT | Secret detection | Git history & files |
| **OSV-Scanner** | Apache-2.0 | Dependency audit | Lockfiles, SBOMs |
| **Bandit** | Apache-2.0 | Python security | Python-specific issues |
| **Ruff** | MIT | Python lint/format | Replaces black/flake8/isort |

### Installation

```bash
# Install all tools at once
pip install ruff mypy pyright pytest pytest-cov coverage[toml] pre-commit bandit

# Install OSV-Scanner (requires Go)
go install github.com/google/osv-scanner/cmd/osv-scanner@v1

# Install Trivy (macOS)
brew install trivy

# Install Gitleaks (macOS)
brew install gitleaks

# Install Semgrep (all platforms)
pip install semgrep

# Install pre-commit hooks
pre-commit install
```

### Quick Run Commands

```bash
# --- Security Scans ---
semgrep --config=auto --error                      # Static analysis
semgrep --config=p/security-audit .               # Security audit
semgrep --config=p/cwe-top-25 .                   # CWE Top 25
trivy fs .                                         # Filesystem vulnerability scan
gitleaks detect --source .                         # Secret detection
osv-scanner -r .                                   # Dependency vulnerability scan
bandit -r . -ll                                    # Python security scan

# --- Python Quality ---
ruff check . --fix                                 # Linting with auto-fix
ruff format .                                      # Code formatting
mypy . --ignore-missing-imports                    # Type checking
pyright                                            # Alternative type checker

# --- Testing ---
pytest -q                                          # Run tests quietly
pytest --tb=short                                  # Short traceback
coverage run -m pytest                             # Run with coverage
coverage report -m                                 # Show missing lines
coverage html && open htmlcov/index.html           # HTML report

# --- All-in-One Local Scan ---
ruff check . && mypy . && bandit -r . && pytest -q

# --- Pre-commit (runs all checks) ---
pre-commit run --all-files                         # Run all hooks
pre-commit run --all-files --hook-stage pre-push   # Include heavy checks
```

### CI/CD Integration

All security scans run automatically on:
- Every push to `main`, `master`, `develop`
- Every pull request
- Daily scheduled runs (00:00 UTC)

View results in:
- **GitHub Security tab** → Code scanning alerts
- **PR checks** → Security scan summary
- **Actions tab** → Detailed logs

### Configuration Files

| File | Purpose |
|------|---------|
| `.github/workflows/security-scan.yml` | CI workflow for all security tools |
| `.pre-commit-config.yaml` | Pre-commit hooks (runs locally) |
| `pyproject.toml` | Ruff, mypy, pytest, coverage settings |
| `.gitleaks.toml` | (Optional) Custom secret patterns |

### GitHub Actions Local Testing

```bash
# Install act (run GitHub Actions locally)
brew install act

# Run security workflow locally
act -j semgrep
act -j trivy
act -j gitleaks

# Run full security scan
act -j security-summary
```

### Exit Codes & CI Behavior

| Tool | Exit on Issues | Config Location |
|------|----------------|-----------------|
| Semgrep | `--error` | CLI flag |
| Trivy | `exit-code: 1` | workflow file |
| Gitleaks | `exit 1` | default |
| OSV-Scanner | `continue-on-error: true` | workflow file |
| Bandit | `-ii` | CLI flag |

---

**All tools are installed and ready to use!** Start with `icecream` for quick debugging and `ipdb` for deep investigation.
