# Repo Doctor Ω∞∞∞

**Repository Operating Physics** - A formal framework for repository health analysis using quantum-inspired state mechanics.

## Overview

Repo Doctor Ω∞∞∞ treats your repository as a physical system with a wavefunction |Ψ_repo⟩ that evolves over time. The system provides:

- **Hard Invariants** (7) - Binary checks that must pass for release
- **State Vector** (12-dim) - Amplitudes representing subsystem integrity  
- **Energy Function** - E_repo = Σ λk (1 - αk)² quantifies repository health
- **Z3 Solver** - SMT-based repair optimization
- **Temporal Mechanics** - Drift tracking and first-bad-commit detection

## Quick Start

```bash
# Full repository scan
python -m repo_doctor_omega.cli scan

# Check API contracts
python -m repo_doctor_omega.cli contracts --strict

# Analyze temporal drift
python -m repo_doctor_omega.cli drift --since HEAD~20

# Generate repair plan
python -m repo_doctor_omega.cli repair-plan --output markdown
```

## Architecture

### Ingest Layer (7 Substrates)

| Substrate | Purpose | Invariant |
|-----------|---------|-----------|
| `TreeSitterSubstrate` | Syntax analysis | I_parse |
| `ImportSubstrate` | Import resolution | I_import |
| `APISubstrate` | API surface analysis | I_api |
| `EntrypointSubstrate` | Launcher validation | I_entry |
| `PackagingSubstrate` | Metadata verification | I_pack |
| `StatusSubstrate` | Boolean flag tracking | I_status |
| `TestSubstrate` | pytest execution | I_tests |

### Hard Invariants (7)

| Invariant | Definition | Severity |
|-----------|-----------|----------|
| I_parse | Every source yields acceptable parse tree | 0.7 |
| I_import | Every import resolves to real symbol | 0.8 |
| I_api | [A_public, A_runtime] = 0 (commutator) | 0.9 |
| I_entry | Every launcher points to runnable target | 0.6 |
| I_pack | Metadata == shipped surface | 0.7 |
| I_status | Status labels imply actual state | 0.5 |
| I_tests | Contract-critical tests pass | 1.0 |

### State Layer

12 basis vectors represent repository subsystems:

```python
|S⟩   - Syntax integrity
|I⟩   - Import resolution
|Ty⟩  - Type system
|A⟩   - API surface
|E⟩   - Entrypoints
|Pk⟩  - Packaging
|Rt⟩  - Runtime
|Ps⟩  - Persistence
|St⟩  - Status labels
|T⟩   - Tests
|D⟩   - Documentation
|Sec⟩ - Security
|H⟩   - Hamiltonian (computed)
```

Amplitudes αk ∈ [0,1] with confidence levels.

Energy computation:
```
E_repo = Σ λk (1 - αk)²
```

### Solver Layer

**Z3Model** - SMT constraint solving:
- Constraint encoding (e.g., `Initialized=true -> LoadedSpecsCount > 0`)
- Satisfiability checking
- Unsat core extraction (minimum contradictory facts)
- Multi-objective optimization (cost + blast radius)

**RepairOptimizer** - Generates minimum-cost repair plans:
```python
optimizer = RepairOptimizer()
plan = optimizer.optimize_repairs(violations, repo_path)
# Returns sequenced repairs by priority order
```

Repair priority order:
1. parse → 2. import → 3. entrypoint → 4. packaging
5. api → 6. persistence → 7. runtime → 8. tests
9. security → 10. performance

### Temporal Layer

**DriftTracker** - Measures repository evolution:
```python
tracker = DriftTracker("/path/to/repo")
report = tracker.analyze_drift(commits=100)
# Returns drift_norm, trends, destabilizing commits
```

**BisectRunner** - Finds first-bad-commit with invariant oracle:
```bash
repo-doctor bisect --invariant I_api --good v1.0.0 --bad HEAD
```

## Python API

### Basic Usage

```python
from repo_doctor_omega.engine import RepoDoctorEngine
from repo_doctor_omega.state.basis import BasisVector

# Create engine
engine = RepoDoctorEngine("/path/to/repo")

# Compute state
state = engine.compute_state()
print(f"Energy: {state.compute_energy():.2f}")

# Evaluate invariants
results = engine.evaluate_invariants()
for result in results:
    status = "✓" if result.passed else "✗"
    print(f"{status} {result.invariant}")

# Check releaseability
if state.is_releaseable(threshold=10.0):
    print("Repository is releaseable")
```

### Advanced: Repair Planning

```python
from repo_doctor_omega.solver import RepairOptimizer

# Collect violations from failed invariants
violations = []
for result in results:
    if not result.passed:
        violations.extend(result.violations)

# Generate optimized repair plan
optimizer = RepairOptimizer()
plan = optimizer.optimize_repairs(violations, repo_path)

print(f"Total cost: {plan.total_cost}")
print(f"Energy drop: {plan.energy_drop}")
for action in plan.actions:
    print(f"  {action.step}. {action.action} -> {action.target}")
```

### Temporal Analysis

```python
from repo_doctor_omega.temporal import DriftTracker, BisectRunner

# Track drift over time
tracker = DriftTracker("/path/to/repo")
report = tracker.analyze_drift(commits=50)

print(f"Total drift: {report.total_drift:.2f}")
for trend in report.trends:
    print(f"  {trend.subsystem}: {trend.trend_direction}")

# Find first bad commit for an invariant
runner = BisectRunner("/path/to/repo")
result = runner.run_bisect_simple(
    invariant_checker=lambda c: check_invariant_at_commit(c, "I_api"),
    good_commit="v1.0.0",
    bad_commit="HEAD",
    invariant_name="I_api",
)
print(f"First bad: {result.first_bad_commit}")
```

## CLI Reference

### `scan` - Full Repository Analysis

```bash
repo-doctor scan [options]

Options:
  --threshold FLOAT   Energy threshold for releaseability (default: 10.0)
  --format {text,json}  Output format
  --repo-path PATH    Repository path (default: .)

Output:
  - State vector (12 amplitudes)
  - Repository energy E_repo
  - Invariant results (7 checks)
  - Releaseability status
  - Violation details
```

### `contracts` - API Contract Check

```bash
repo-doctor contracts [options]

Options:
  --strict           Flag all discrepancies
  --format {text,json}

Checks:
  - Public API claims (__all__, module exports)
  - Runtime API reality (actual callables)
  - Commutator [A_public, A_runtime] = 0
```

### `state` - State Vector Details

```bash
repo-doctor state [options]

Output:
  Detailed amplitude values for all 12 basis vectors
  Confidence levels for each measurement
```

### `drift` - Temporal Analysis

```bash
repo-doctor drift [options]

Options:
  --since COMMIT     Reference commit (default: HEAD~10)
  --format {text,json}

Output:
  - Drift norm ||ΔΨ(t)||
  - Per-subsystem trends
  - Destabilizing commits
  - Energy evolution
```

### `repair-plan` - Automated Repair

```bash
repo-doctor repair-plan [options]

Options:
  --output {text,json,markdown}

Output:
  - Sequenced repair actions
  - Cost estimates
  - Blast radius assessment
  - Expected energy drop
  - Risk warnings
```

## Configuration

Repo Doctor uses sensible defaults but can be configured via environment variables:

```bash
# Z3 solver timeout (seconds)
export REPO_DOCTOR_Z3_TIMEOUT=30

# Energy threshold for releaseability
export REPO_DOCTOR_ENERGY_THRESHOLD=10.0

# Default output format
export REPO_DOCTOR_FORMAT=json

# Pytest timeout (seconds)
export REPO_DOCTOR_PYTEST_TIMEOUT=60
```

## Extending Repo Doctor

### Adding a New Invariant

```python
from repo_doctor_omega.invariants.base import HardInvariant, InvariantKind, InvariantResult
from repo_doctor_omega.state.basis import BasisVector

class CustomInvariant(HardInvariant):
    """Custom repository invariant."""
    
    def __init__(self):
        super().__init__(InvariantKind.CUSTOM, BasisVector.CUSTOM)
    
    def check(self, repo_path: str, context: dict | None = None) -> InvariantResult:
        violations = []
        
        # Custom validation logic
        # ...
        
        return InvariantResult(
            invariant=self.name,
            passed=len(violations) == 0,
            basis=self.basis,
            violations=violations,
            metadata={"custom": "data"},
        )
```

### Adding a New Substrate

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CustomFact:
    """Fact extracted by custom substrate."""
    name: str
    value: Any

class CustomSubstrate:
    """Custom analysis substrate."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
    
    def analyze(self) -> list[CustomFact]:
        """Extract facts from repository."""
        facts = []
        # Custom analysis logic
        return facts
```

## Theory

### Repository as Physical System

Repo Doctor applies concepts from quantum mechanics to software repositories:

1. **Wavefunction** |Ψ_repo⟩ - Superposition of all possible repository states
2. **Basis Vectors** - Orthogonal dimensions of repository integrity
3. **Amplitudes** αk - Probability-like measures of subsystem health
4. **Hamiltonian** H - Operator measuring "energy" (cost of being wrong)
5. **Measurement** - Collapsing superposition via invariant evaluation

### Hard vs Soft Invariants

**Hard Invariants** (binary, gate release):
- Must be satisfied for release
- Violations have severity scores
- Example: I_tests (contract tests must pass)

**Soft Invariants** (continuous, advisory):
- Contribute to energy but don't block
- Represent "code smells" or technical debt
- Example: Documentation coverage

### Temporal Evolution

Repository state evolves via unitary operations (commits):

```
|Ψ(t+1)⟩ = U_commit |Ψ(t)⟩
```

Drift measures change magnitude:
```
||ΔΨ(t)|| = √Σ (Δαk)²
```

### Repair as Energy Minimization

The Z3 solver finds repairs that minimize:

```
min Σ (cost_i + λ · blast_radius_i)
```

Subject to:
- All hard invariants satisfied
- Dependencies respected (priority order)
- Budget constraints (optional)

## Troubleshooting

### Import Errors

If you see `ImportError` for tree_sitter or z3:

```bash
# Tree-sitter is optional (falls back to ast)
pip install tree-sitter tree-sitter-python

# Z3 is optional (solver uses fallback)
pip install z3-solver
```

### Performance

For large repositories:

```bash
# Limit analysis scope
repo-doctor scan --max-files 1000

# Use faster substrates only
export REPO_DOCTOR_FAST_MODE=1

# Parallel processing (if implemented)
export REPO_DOCTOR_WORKERS=4
```

### Git Integration

For temporal features:

```bash
# Ensure git is available
which git

# For bisect, need clean working directory
git status  # should be clean
```

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Areas of interest:

- Additional substrates (CodeQL, Joern, semgrep)
- More invariants (security, performance, accessibility)
- Fleet layer (multi-repo analysis)
- Visualization tools
- IDE integrations

## References

1. "Repository Operating Physics" - Original architecture specification
2. Z3 Theorem Prover - https://github.com/Z3Prover/z3
3. Tree-sitter - https://tree-sitter.github.io/
4. Git bisect run - https://git-scm.com/docs/git-bisect
