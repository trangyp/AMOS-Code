# AMOS Tool Lattice

**Five-Kernel Architecture for High-Performance AMOS Systems**

The Tool Lattice splits work into five specialized kernels, each with purpose-built tools. The mistake is treating all tooling as one pile. AMOS-style systems need a **tool lattice** where each tool accelerates one layer.

---

## The Five Kernels

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 5: PROFILING KERNEL                                  │
│  Tools: cProfile → py-spy → Scalene                        │
│  Purpose: Find what is actually slow                        │
├─────────────────────────────────────────────────────────────┤
│  LAYER 4: REPO-ENFORCEMENT KERNEL                           │
│  Tools: pre-commit, Import Linter, jscpd, deptry, Bandit   │
│  Purpose: Drift prevention, architecture enforcement        │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: CODE-AGENT KERNEL                                 │
│  Tools: Aider, Continue, OpenHands, Cascade/Brain           │
│  Purpose: Editing, debugging, patch generation              │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: SCHEMA KERNEL                                     │
│  Tools: Pydantic v2                                         │
│  Purpose: State, validation, invariants, serialization      │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: NUMERIC KERNEL                                    │
│  Tools: NumPy → Polars → Numba → JAX                        │
│  Purpose: Math, P&L, routing, signals, risk                │
└─────────────────────────────────────────────────────────────┘
```

---

## Kernel 1: Numeric Kernel

**Tools:** NumPy → Polars → Numba → JAX

**Use for:** Vectorized portfolio math, exposure aggregation, covariance transforms, matrix/tensor state operations, time-series pipelines, fast tabular analytics, JIT-compiled hot loops.

### Installation

```bash
# CPU-only numeric kernel
pip install -e ".[numeric]"

# With GPU support (CUDA 12)
pip install -e ".[numeric-gpu]"
```

### Quick Validation

```bash
make -f Makefile.amos_lattice numeric
```

### When to Use What

| Tool | Use When | Speedup |
|------|----------|---------|
| **NumPy** | Baseline vectorized operations | 10-100x vs Python loops |
| **Polars** | Time-series, joins, tabular data | 5-50x vs pandas |
| **Numba** | Hot loops already in Python | 10-1000x with `@jit` |
| **JAX** | JIT + autodiff + GPU portability | Compile to XLA |

### Example: NumPy Softmax

```python
import numpy as np

def softmax(x: np.ndarray) -> np.ndarray:
    """Vectorized softmax - runs at C speed."""
    exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)
```

### Example: Numba JIT Route Scoring

```python
from numba import jit
import numpy as np

@jit(nopython=True, cache=True)
def score_routes(routes: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """JIT-compiled route scoring - 100-1000x speedup."""
    n = routes.shape[0]
    scores = np.empty(n)
    for i in range(n):
        scores[i] = np.dot(routes[i], weights)
    return scores
```

---

## Kernel 2: Schema Kernel

**Tool:** Pydantic v2 (with pydantic-core in Rust)

**Use for:** Canonical state `X_t`, decision schemas, portfolio snapshots, audit schemas, mode schemas, invariant I/O models.

### Why Pydantic

AMOS does not need "more dicts." It needs:
- One state authority
- One transition authority  
- One invariant authority
- One commit authority

Pydantic v2 provides these with Rust-backed validation speed.

### Installation

Already included in base: `pydantic>=2.0.0`

### Quick Validation

```bash
make -f Makefile.amos_lattice schema
```

### Example: AMOS State Schema

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class SystemState(BaseModel):
    """Canonical X_t state for AMOS kernel."""
    timestamp: datetime
    mode: Literal["observation", "analysis", "action", "rest"]
    health_score: float = Field(ge=0.0, le=1.0)
    active_equations: list[str]
    
    class Config:
        frozen = True  # Immutable state
```

### Hot Path Optimization

```python
from pydantic import TypeAdapter

# Reuse TypeAdapter for hot paths
state_adapter = TypeAdapter(SystemState)

# Fast validation without full model construction
validated = state_adapter.validate_python(raw_data)
```

---

## Kernel 3: Code-Agent Kernel

**Tools:** Aider, Continue, OpenHands, Cascade/Brain

**Use for:** Terminal-first repo edits, iterative fixes, schema migrations, repetitive refactors, SSOT moves.

### When to Use What

| Tool | Best For | Integration |
|------|----------|-------------|
| **Aider** | Terminal edits, Git-aware patches, file-by-file remediation | `pip install aider-chat` |
| **Continue** | IDE + terminal + CI/CD, automated PR checks | VS Code extension + CLI |
| **OpenHands** | Heavy delegated work, headless scripted resolution | Docker/local runtime |
| **Cascade/Brain** | Architectural decisions, multi-file coordinated changes | Windsurf IDE |

### Installation

```bash
# Aider (terminal-first)
pip install aider-chat

# Continue (already in IDE)
# OpenHands (if needed)
pip install openhands
```

### Quick Validation

```bash
make -f Makefile.amos_lattice code-agent
```

---

## Kernel 4: Repo-Enforcement Kernel

**Tools:** pre-commit, Import Linter, jscpd, deptry, Bandit, pip-audit

**Use for:** Drift prevention, architecture enforcement, duplicate detection, dependency audit, security scanning.

### Why This Matters

Speed compounds when the repo cannot drift. The enforcement kernel ensures:
- No circular imports between layers
- No code duplication >5%
- No missing/unused dependencies
- No known vulnerabilities in deps
- No security anti-patterns

### Installation

```bash
make -f Makefile.amos_lattice install-dev
pre-commit install
```

### Quick Validation

```bash
make -f Makefile.amos_lattice enforce
```

### Architecture Enforcement

```bash
# Check layer dependencies
lint-imports

# Reports:
# - Contract: AMOS Five-Kernel Architecture
# - Status: KEPT / BROKEN
# - Details: Import graph violations
```

### Duplicate Detection

```bash
# Detect code clones
jscpd --config .jscpd.json

# Reports to ./reports/jscpd/
```

### Dependency Audit

```bash
# Find missing/unused deps
deptry .

# Security scan
bandit -c pyproject.toml -r .
pip-audit --requirement requirements.txt
```

---

## Kernel 5: Profiling Kernel

**Tools:** cProfile → py-spy → Scalene

**Use for:** Finding what is actually slow, not what looks slow.

### When to Use What

| Tool | Use When | Overhead |
|------|----------|----------|
| **cProfile** | First pass, function-level hotspots | ~10% |
| **py-spy** | Production, sampling profiler, no restart | ~1% |
| **Scalene** | CPU + GPU + memory deep dive | 10-20% |

### Installation

```bash
# Included in dev dependencies
pip install scalene py-spy
```

### Quick Start

```bash
# cProfile (fast first pass)
make -f Makefile.amos_lattice profile

# py-spy (production-safe)
make -f Makefile.amos_lattice profile-spy

# Scalene (deep analysis)
make -f Makefile.amos_lattice profile-scalene
```

### Viewing Results

```bash
# cProfile
python -m pstats /tmp/amos_profile.prof
> sort cumulative
> stats 20

# py-spy (SVG flamegraph)
open /tmp/amos_spy.svg

# Scalene (HTML report)
open /tmp/amos_scalene.html
```

---

## The Practical Stack

### Installation (One Command)

```bash
# Full tool lattice
make -f Makefile.amos_lattice install

# Or manual:
pip install -e ".[numeric,dev]"
pre-commit install
npm install -g jscpd
```

### Daily Workflow

```bash
# 1. Profile before optimizing
make -f Makefile.amos_lattice profile

# 2. Move hot paths to NumPy/Numba
#    (edit with Aider/Continue)

# 3. Validate schema changes
make -f Makefile.amos_lattice schema

# 4. Run enforcement before commit
make -f Makefile.amos_lattice enforce

# 5. Full CI pipeline
make -f Makefile.amos_lattice ci
```

### High-Return Sequence

If your goal is **faster calculations and faster fixing right now**:

1. **Profile** with `cProfile` or `py-spy`
2. **Move** numeric hot paths to NumPy/Numba
3. **Define** canonical state in Pydantic
4. **Use** Aider or Continue for repetitive refactors
5. **Enforce** architecture with Import Linter
6. **Enforce** duplicates with jscpd
7. **Keep** all of it behind pre-commit and uv

---

## Configuration Files

| File | Purpose | Kernel |
|------|---------|--------|
| `importlinter.toml` | Layer architecture enforcement | Repo-Enforcement |
| `.jscpd.json` | Duplicate detection config | Repo-Enforcement |
| `Makefile.amos_lattice` | Automation commands | All |
| `.pre-commit-config.yaml` | Pre-commit hooks (sections added) | Repo-Enforcement |
| `pyproject.toml` | Numeric + dev deps | Numeric, Schema, Repo |

---

## Commands Reference

### Kernel-Specific

```bash
make -f Makefile.amos_lattice numeric        # Validate numeric kernel
make -f Makefile.amos_lattice schema         # Validate schema kernel
make -f Makefile.amos_lattice code-agent     # Check code-agent tools
make -f Makefile.amos_lattice enforce        # Run repo enforcement
make -f Makefile.amos_lattice profile        # Run profiling
```

### Combined Workflows

```bash
make -f Makefile.amos_lattice ci             # Full CI pipeline
make -f Makefile.amos_lattice harden         # Production hardening
make -f Makefile.amos_lattice all            # Everything
```

---

## The Non-Basic Answer

Yes, there are tools. But the deepest improvement comes from putting them in the right layer:

- **NumPy / Numba / JAX** make the **numeric kernel** fast
- **Pydantic** makes the **state kernel** lawful
- **Aider / Continue / OpenHands** make the **editing kernel** fast
- **Import Linter / jscpd / deptry** make the **architecture kernel** stable
- **pytest / Hypothesis** make the **invariant kernel** trustworthy
- **pre-commit / uv** make the whole stack repeatable

That is the AMOS way to think about tooling.

---

## Links & References

| Tool | Documentation |
|------|---------------|
| NumPy | https://numpy.org |
| Polars | https://pola.rs |
| Numba | https://numba.readthedocs.io |
| JAX | https://jax.readthedocs.io |
| Pydantic | https://docs.pydantic.dev |
| Aider | https://aider.chat |
| Continue | https://docs.continue.dev |
| Import Linter | https://import-linter.readthedocs.io |
| jscpd | https://jscpd.dev |
| deptry | https://deptry.com |
| Bandit | https://bandit.readthedocs.io |
| pip-audit | https://pypi.org/project/pip-audit |
| Scalene | https://github.com/plasma-umass/scalene |
| py-spy | https://github.com/benfred/py-spy |
| Hypothesis | https://hypothesis.readthedocs.io |
