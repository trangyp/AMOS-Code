# AMOS Tool Lattice - Concrete Deliverables

Six-Kernel Architecture Implementation

---

## Summary

The AMOS tool lattice has been implemented across all projects with the exact enforcement order:
1. **Syntax & Formatting** (Ruff)
2. **Tests** (pytest, pytest-asyncio)
3. **Architecture** (import-linter)
4. **Duplication/Dependency/Security** (jscpd, deptry, Bandit, pip-audit)

---

## Files Created/Modified

### 1. Installation Script
**File**: `AMOS_TOOL_LATTICE_INSTALL.sh`

One-command setup:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.11
uv venv --python 3.11
source .venv/bin/activate
uv pip install pre-commit ruff pydantic pytest pytest-asyncio hypothesis
uv pip install import-linter jscpd deptry bandit pip-audit
uv pip install numba numpy polars
pre-commit install --install-hooks
```

---

### 2. Root `pyproject.toml` - Tool Lattice Extras

New extras added to `/pyproject.toml`:

```toml
# Kernel 2: Schema & Deterministic Core
schema = ["pydantic>=2.5.0", "hypothesis>=6.92.0"]

# Kernel 3: Numeric Speed
numeric = ["numpy>=1.26.0", "polars>=0.20.0", "numba>=0.59.0"]
numeric-gpu = ["numpy>=1.26.0", "polars>=0.20.0", "numba>=0.59.0", "jax[cuda12_pip]>=0.4.20", "jaxlib>=0.4.20"]

# Kernel 4: Code-Agent
agent = ["aider-chat>=0.24.0"]

# Kernel 5: Enforcement
enforcement = [
    "ruff>=0.1.0", "mypy>=1.7.0", "bandit[toml]>=1.7.7",
    "pip-audit>=2.7.0", "import-linter>=2.0.0", "jscpd>=3.5.0",
    "deptry>=0.15.0", "pre-commit>=3.6.0"
]

# Kernel 6: Test & Async
test = ["pytest>=7.4.0", "pytest-asyncio>=0.21.0", "pytest-cov>=4.1.0"]

# Layer-based extras (L0-L15)
l0-l1 = ["pydantic>=2.5.0", "hypothesis>=6.92.0", "import-linter>=2.0.0"]  # Law, Invariants
l2-l3 = ["pydantic>=2.5.0", "ruff>=0.1.0", "mypy>=1.7.0", "deptry>=0.15.0"]  # State, Semantics
l4-l5 = ["numpy>=1.26.0", "polars>=0.20.0", "numba>=0.59.0"]  # Dynamics, Math
l6-l7 = ["pytest>=7.4.0", "pytest-asyncio>=0.21.0", "polars>=0.20.0"]  # Observation
l8-l9 = ["hypothesis>=6.92.0", "pytest>=7.4.0", "import-linter>=2.0.0"]  # Constraints
l10-l11 = ["aider-chat>=0.24.0"]  # Planning, Code-Agent
l12-l15 = ["pydantic>=2.5.0", "hypothesis>=6.92.0", "pytest>=7.4.0", "bandit[toml]>=1.7.7"]  # Governance

# Full tool lattice
tool-lattice = ["amos-brain[schema,numeric,test,enforcement]"]
tool-lattice-full = ["amos-brain[schema,numeric,test,enforcement,agent]"]
```

---

### 3. Clawspring `pyproject.toml`

Updated `/clawspring/pyproject.toml` with:

```toml
[project.optional-dependencies]
# Kernel 1: Bootstrap
bootstrap = []

# Kernel 2: Schema & Deterministic Core
schema = ["pydantic>=2.5.0", "hypothesis>=6.92.0"]

# Kernel 3: Numeric Speed
numeric = ["numpy>=1.26.0", "polars>=0.20.0", "numba>=0.59.0"]

# Kernel 4: Code-Agent
agent = ["aider-chat>=0.24.0"]

# Kernel 5: Enforcement
enforcement = [
    "ruff>=0.1.0", "mypy>=1.7.0", "bandit>=1.7.7",
    "pip-audit>=2.7.0", "import-linter>=2.0.0", "jscpd>=3.5.0",
    "deptry>=0.15.0", "pre-commit>=3.6.0"
]

# Kernel 6: Test & Async
test = ["pytest>=7.4.0", "pytest-asyncio>=0.21.0", "pytest-cov>=4.1.0"]

# Layer-based extras (L0-L15)
l0-l1 = ["pydantic>=2.5.0", "hypothesis>=6.92.0", "import-linter>=2.0.0"]
l2-l3 = ["pydantic>=2.5.0", "ruff>=0.1.0", "mypy>=1.7.0", "deptry>=0.15.0"]
l4-l5 = ["numpy>=1.26.0", "polars>=0.20.0", "numba>=0.59.0"]
l6-l7 = ["pytest>=7.4.0", "pytest-asyncio>=0.21.0", "polars>=0.20.0"]
l8-l9 = ["hypothesis>=6.92.0", "pytest>=7.4.0", "import-linter>=2.0.0"]
l10-l11 = ["aider-chat>=0.24.0"]
l12-l15 = ["pydantic>=2.5.0", "hypothesis>=6.92.0", "pytest>=7.4.0", "bandit>=1.7.7"]

all = ["amos[schema,numeric,test,enforcement,agent]"]
dev = ["amos[all]"]

# Tool configurations
[tool.ruff]
target-version = "py310"
line-length = 100

[tool.mypy]
python_version = "3.10"
strict = true

[tool.pytest.ini_options]
asyncio_mode = "auto"

[tool.importlinter]
root_package = "openclaws"

[[tool.importlinter.contracts]]
name = "OpenClaws layers"
type = "layers"
layers = [
    "frontends", "api", "orchestration", "tools",
    "memory", "runtimes", "protocols", "core", "config"
]
containers = ["openclaws"]
exhaustive = true
exhaustive_ignores = ["tests", "examples"]
```

---

### 4. Pre-commit Config Updated

Updated `.pre-commit-config.yaml` with AMOS tool lattice enforcement order:

```yaml
# KERNEL 1: Syntax & Formatting (Ruff) - runs on commit
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.14.1
  hooks:
    - id: ruff
      args: [--fix, --exit-non-zero-on-fix]
    - id: ruff-format

# KERNEL 6: Tests & Async - runs on push
- repo: local
  hooks:
    - id: pytest
      name: AMOS Test Runner (pytest + asyncio)
      entry: python -m pytest
      args: ["-q", "--tb=short", "--strict-markers"]
      stages: [pre-push]

# Architecture: Import Linter
- repo: local
  hooks:
    - id: import-linter
      name: AMOS Architecture Enforcement
      entry: lint-imports
      stages: [pre-push]

# Duplicate: jscpd
- repo: local
  hooks:
    - id: jscpd
      entry: jscpd --config .jscpd.json
      stages: [pre-push]

# Dependencies: deptry
- repo: local
  hooks:
    - id: deptry
      entry: deptry .
      stages: [pre-push]

# Security: Bandit
- repo: https://github.com/PyCQA/bandit
  rev: 1.7.7
  hooks:
    - id: bandit
      args: ["-c", "pyproject.toml", "-r", "."]
      stages: [pre-push]

# Security: pip-audit
- repo: https://github.com/pypa/pip-audit
  rev: v2.7.0
  hooks:
    - id: pip-audit
      args: ["--requirement", "requirements.txt"]
      stages: [pre-push]
```

---

### 5. Import Linter Config - OpenClaws

**File**: `/clawspring/importlinter.toml`

```toml
[importlinter]
root_package = "openclaws"

[[importlinter.contracts]]
name = "OpenClaws layers"
type = "layers"
layers = [
    "frontends", "api", "orchestration", "tools",
    "memory", "runtimes", "protocols", "core", "config"
]
containers = ["openclaws"]
exhaustive = true
exhaustive_ignores = ["tests", "examples"]

[[importlinter.contracts]]
name = "Core isolation"
type = "forbidden"
source_modules = ["openclaws.core"]
forbidden_modules = ["openclaws.frontends", "openclaws.api"]
```

---

### 6. Import Linter Config - AMOS-Invest

**File**: `/amos_invest/importlinter.toml`

```toml
[importlinter]
root_package = "amos_invest"

[[importlinter.contracts]]
name = "Invest layers"
type = "layers"
layers = [
    "cli", "interfaces", "runtime", "execution",
    "portfolio", "market", "decision", "core", "config"
]
containers = ["amos_invest"]
exhaustive = true
exhaustive_ignores = ["tests", "examples"]

[[importlinter.contracts]]
name = "Core isolation"
type = "forbidden"
source_modules = ["amos_invest.core"]
forbidden_modules = ["amos_invest.cli", "amos_invest.interfaces"]
```

---

## Quick Commands Reference

```bash
# Install full tool lattice
./AMOS_TOOL_LATTICE_INSTALL.sh

# Install via pip
pip install -e ".[tool-lattice]"

# Run all checks
pre-commit run --all-files

# Individual tools
ruff check .                    # Lint
ruff format .                   # Format
mypy .                          # Type check
pytest -q                       # Tests
lint-imports                    # Architecture check
deptry .                        # Dependencies
jscpd .                         # Duplication
bandit -r .                     # Security
pip-audit                       # Vulnerabilities
```

---

## Layer-to-Tool Mapping

| Layer | Purpose | Tools |
|-------|---------|-------|
| L0-L1 | Law, Invariants | Pydantic, Hypothesis, Import Linter |
| L2-L3 | State, Semantics | Pydantic, Ruff, mypy, deptry |
| L4-L5 | Dynamics, Math | NumPy, Polars, Numba, JAX |
| L6-L7 | Observation, Async | pytest, pytest-asyncio, Polars |
| L8-L9 | Constraints | Hypothesis, pytest, Import Linter |
| L10-L11 | Planning | Aider |
| L12-L15 | Governance | Pydantic, Hypothesis, pytest, Bandit |

---

## Status

- ✅ Clawspring `pyproject.toml` - Updated with tool lattice extras and tool configs
- ✅ Root `pyproject.toml` - Added tool lattice extras
- ✅ `.pre-commit-config.yaml` - Updated with enforcement order
- ✅ `clawspring/importlinter.toml` - Created with layer contracts
- ✅ `amos_invest/importlinter.toml` - Created with layer contracts
- ✅ `AMOS_TOOL_LATTICE_INSTALL.sh` - Installation script ready
