# Repo Doctor Architecture

## Core Theory: Quantum State-Space Model

Repo Doctor models repository health as a **quantum state vector** in a 10-dimensional Hilbert space.

### State Vector Definition

```
Ψ_repo(t) = [s(t), i(t), b(t), τ(t), p(t), a(t), d(t), c(t), h(t), σ(t)]
```

Where each dimension represents:

| Symbol | Dimension | Description | Invariant |
|--------|-----------|-------------|-----------|
| s | Syntax | All source files parse | I_parse |
| i | Imports | No broken import links | I_import |
| b | Build | Package builds successfully | I_build |
| τ | Tests | All tests pass | I_test |
| p | Packaging | Metadata valid | I_packaging |
| a | API | Contracts consistent | I_api |
| d | Dependencies | No version conflicts | I_deps |
| c | Entrypoints | All launchers valid | I_entry |
| h | History | Clean git state | I_history |
| σ | Security | No vulnerabilities | I_security |

### State Vector Properties

Each dimension value ∈ [0.0, 1.0]:
- `1.0` = Perfect (no issues)
- `0.0` = Collapsed (critical failure)
- Values in between indicate partial degradation

### Energy Equation

The "energy" of a repository state measures deviation from ideal:

```
E(Ψ_repo) = Σ (1 - d_n) * w_n

Where:
- d_n = dimension value
- w_n = dimension weight (severity coefficient)
```

**Interpretation:**
- E = 0: Perfect repository
- E < 2: Healthy, releaseable
- E > 5: Critical issues, investigate immediately

### Drift Score (Temporal)

Measures how much the repository changed between commits:

```
ΔΨ(t1, t2) = ||Ψ(t2) - Ψ(t1)||
           = √[Σ (d_n(t2) - d_n(t1))²]
```

High drift indicates significant structural changes.

## Invariant Engine

### Hard Invariants

Hard invariants are **pass/fail** checks that gate release:

```
I = {I_parse, I_import, I_build, I_test, I_packaging, I_api, I_entry, I_security}

Repository is valid iff:
    ∀ I_n ∈ I : I_n(Ψ_repo) = 1
```

**Not "mostly good." Pass or fail.**

### Invariant Classes

#### 1. Parse Invariant (I_parse)
**Check:** All Python files parse without SyntaxError
**Hard-fail:** Yes
**Weight:** 1.0

#### 2. Import Invariant (I_import)
**Check:** All imports resolve to real modules
**Hard-fail:** Yes
**Weight:** 1.0

#### 3. Build Invariant (I_build)
**Check:** `pip install -e .` succeeds
**Hard-fail:** Yes
**Weight:** 1.0

#### 4. Test Invariant (I_test)
**Check:** `pytest --collect-only` succeeds
**Hard-fail:** No (soft)
**Weight:** 1.5

#### 5. Packaging Invariant (I_packaging)
**Check:** pyproject.toml valid, version declared
**Hard-fail:** Yes
**Weight:** 2.0

#### 6. API Invariant (I_api)
**Check:** Public exports match documentation
**Hard-fail:** Yes
**Weight:** 1.0

#### 7. Entrypoint Invariant (I_entry)
**Check:** All console scripts point to real functions
**Hard-fail:** Yes
**Weight:** 2.0

#### 8. Security Invariant (I_security)
**Check:** No eval/exec, no known vulnerabilities
**Hard-fail:** No (soft)
**Weight:** 2.0

## System Layers

### Layer 1: Sensors (Fact Collection)

Sensors collect raw data from the repository:

```
Sensors:
├── ASTSensor: Parse all Python files
├── ImportSensor: Build import graph
├── ExportSensor: Find public API surface
├── BuildSensor: Attempt package build
├── TestSensor: Collect test suite
├── CLISensor: Validate CLI commands
├── DocSensor: Extract doc examples
├── GitSensor: Analyze commit history
├── DepSensor: Check dependency graph
├── SecuritySensor: Scan for vulnerabilities
└── ExternalSensor: Run pip-audit, ruff, pyright
```

### Layer 2: Invariant Engine (Validation)

The invariant engine applies hard rules:

```
InvariantEngine:
├── ParseInvariant
├── ImportInvariant
├── BuildInvariant
├── TestInvariant
├── PackagingInvariant
├── APIInvariant
├── EntrypointInvariant
└── SecurityInvariant
```

Each invariant returns:
```python
InvariantResult(
    passed: bool,           # Hard pass/fail
    dimension: StateDimension,
    message: str,           # Human-readable summary
    details: List[str],     # Specific issues found
    files_affected: List[str]
)
```

### Layer 3: Temporal Debugger (Bisect)

Finds commits that broke invariants:

```
BisectEngine:
1. Find regression range (good_commit, bad_commit)
2. Run git bisect with invariant check
3. Identify first bad commit
4. Analyze changes in that commit
5. Suggest repair actions
```

### Layer 4: Repair Planner

Generates minimal patches:

```
RepairPlanner:
1. Analyze invariant failures
2. Generate repair actions
3. Prioritize by impact
4. Create executable patch script
5. Validate patch restores invariants
```

## Dependency Entanglement

### Entanglement Matrix

Models coupling between modules:

```
E_ij = α * import_coupling(i,j)
     + β * test_coupling(i,j)
     + γ * git_cochange(i,j)
```

Where:
- `import_coupling`: Module i imports from module j
- `test_coupling`: Tests for i import j
- `git_cochange`: i and j change together in commits

### Interface Commutator

Measures API drift between commits:

```
[A, B] = AB - BA ≠ 0  →  API changed
```

Non-zero commutator indicates breaking changes.

## Scoring Model

### Dimension Weights

```python
WEIGHTS = {
    StateDimension.SYNTAX: 1.0,      # Code must parse
    StateDimension.IMPORT: 1.0,      # Imports must resolve
    StateDimension.BUILD: 1.0,      # Must build
    StateDimension.TEST: 1.5,       # Tests should pass
    StateDimension.PACKAGING: 2.0,  # Critical for release
    StateDimension.API: 1.0,        # Contracts matter
    StateDimension.DEPS: 1.0,       # Dependencies
    StateDimension.CONFIG: 2.0,      # Entrypoints critical
    StateDimension.HISTORY: 0.5,    # Git nice-to-have
    StateDimension.SECURITY: 2.0,    # Security critical
}
```

### Release Criteria

A repository is **releaseable** iff:

1. All hard-fail invariants pass
2. Score >= 70/100
3. Energy < 3.0
4. No collapsed subsystems

## Implementation Details

### State Vector Calculation

```python
class RepoStateVector:
    def __init__(self):
        self.values = {dim: 1.0 for dim in StateDimension}

    def apply_collapse(self, dimension: StateDimension, severity: float):
        """Apply failure to a dimension."""
        self.values[dimension] = max(0.0, 1.0 - severity)

    def energy(self) -> float:
        """Calculate total energy."""
        return sum(
            (1.0 - self.values[dim]) * WEIGHTS[dim]
            for dim in StateDimension
        )

    def score(self) -> int:
        """Calculate 0-100 score."""
        return int(100 - self.energy() * 10)
```

### External Sensor Integration

```python
class SensorSuite:
    """Runs external tools and aggregates results."""

    def __init__(self, repo_path: Path):
        self.sensors = [
            PipAuditSensor(repo_path),
            RuffSensor(repo_path),
            PyrightSensor(repo_path),
            DeptrySensor(repo_path),
        ]

    def run_all(self) -> List[SensorResult]:
        """Execute all available sensors."""
        return [s.run() for s in self.sensors if s.is_available()]
```

## Extending Repo Doctor

### Adding a Custom Invariant

```python
from repo_doctor.invariants import Invariant, InvariantResult
from repo_doctor.state_vector import StateDimension

class MyInvariant(Invariant):
    name = "my_check"
    dimension = StateDimension.CUSTOM

    def check(self, repo_path: Path) -> InvariantResult:
        errors = []

        # Your validation logic
        if some_condition_fails:
            errors.append("Description of issue")

        return InvariantResult(
            passed=len(errors) == 0,
            dimension=self.dimension,
            message="Check passed" if not errors else f"{len(errors)} issues",
            details=errors
        )

# Register in InvariantEngine
InvariantEngine.DEFAULT_INVARIANTS.append(MyInvariant)
```

### Adding a Custom Sensor

```python
from repo_doctor.sensors import ExternalSensor, SensorResult

class MySensor(ExternalSensor):
    def is_available(self) -> bool:
        return shutil.which("my_tool") is not None

    def run(self) -> SensorResult:
        if not self.is_available():
            return SensorResult(
                tool_name="my_tool",
                available=False,
                passed=True,
                error_message="my_tool not installed"
            )

        # Run tool and parse output
        result = subprocess.run(
            ["my_tool", "."],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        findings = self._parse_output(result.stdout)

        return SensorResult(
            tool_name="my_tool",
            available=True,
            passed=len(findings) == 0,
            findings=findings
        )
```

## Performance Considerations

### Caching

- Parse results cached by file hash
- Import graph cached per session
- Git history cached for temporal analysis

### Parallel Execution

- Sensors run in parallel (I/O bound)
- Invariants run sequentially (CPU bound)
- File parsing parallelized by directory

### Incremental Analysis

```python
# Only check changed files
changed_files = get_git_changed_files()
engine.run_incremental(changed_files)
```

## Future Work

1. **ML-based anomaly detection**: Learn normal patterns, flag outliers
2. **Auto-fix generation**: Use LLMs to generate repair patches
3. **Cross-repo analysis**: Compare health across organization
4. **Real-time monitoring**: Continuous health tracking
5. **Integration marketplace**: Plugin system for custom sensors
