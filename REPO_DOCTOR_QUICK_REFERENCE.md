# Repo Doctor Ω∞ - Quick Reference Guide

**One-page reference for the maximum-strength repository mechanics engine.**

---

## Installation

```bash
# No installation needed - pure Python
# Optional: Install Z3 for SMT solving
pip install z3-solver

# Optional: Install Tree-sitter for parsing
pip install tree-sitter tree-sitter-python
```

---

## CLI Commands

```bash
# Full repository diagnosis
python -m repo_doctor.omega_infinity scan

# Show state vector and energy
python -m repo_doctor.omega_infinity state

# Check 12 hard invariants
python -m repo_doctor.omega_infinity invariants

# Get optimized repair plan
python -m repo_doctor.omega_infinity repair-plan

# Analyze module entanglement
python -m repo_doctor.omega_infinity entanglement --module <name>

# System status
python -m repo_doctor.omega_infinity status

# Markdown output
python -m repo_doctor.omega_infinity scan --format markdown
```

---

## Python API

### Basic Usage

```python
from repo_doctor.omega_infinity import RepoDoctorOmegaInfinity

# Initialize
doctor = RepoDoctorOmegaInfinity('/path/to/repo')

# Full scan
report = doctor.scan()
data = report.to_dict()

print(f"Energy: {data['energy']}")
print(f"Valid: {data['repo_valid']}")
print(f"Failing: {data['hard_invariant_failures']}")
```

### State Vector

```python
from repo_doctor.omega_infinity import StateVector, StateDimension

# Create custom state
sv = StateVector(amplitudes={
    StateDimension.SYNTAX: 0.95,
    StateDimension.API: 0.80,
    StateDimension.SECURITY: 1.0,
})

# Compute energy
energy = sv.compute_energy()
print(f"Repository energy: {energy}")

# Check health
if sv.is_healthy:
    print("Repository is healthy")
elif sv.is_collapsed:
    print("Repository has collapsed invariants")
```

### Hard Invariants

```python
from repo_doctor.omega_infinity import HardInvariantChecker

checker = HardInvariantChecker('/path/to/repo')
results = checker.check_all()

for result in results:
    status = "✓" if result.passed else "✗"
    print(f"{status} {result.name}: {result.message}")

# Check overall validity
if checker.repo_valid:
    print("All 12 invariants pass")
else:
    failing = checker.get_failing()
    print(f"{len(failing)} invariants need repair")
```

### Entanglement Analysis

```python
# Find coupled modules
entangled = doctor.compute_entanglement('core_module')

for module, coupling in entangled:
    print(f"{module}: {coupling:.2f}")
```

### Repair Optimization

```python
# Get repair plan
repairs = doctor.get_repair_plan()

for action in repairs:
    print(f"{action.target}")
    print(f"  Cost: {action.edit_cost}")
    print(f"  Blast radius: {action.blast_radius}")
    print(f"  Energy reduction: {action.energy_reduction}")
```

### Fleet Analysis

```python
from repo_doctor.omega_infinity import FleetState, StateVector, StateDimension

# Build fleet
fleet = FleetState()

for repo_id in ['service-a', 'service-b', 'service-c']:
    sv = StateVector()
    # ... configure state
    fleet.add_repository(repo_id, sv, weight=1.0)

# Analyze
energy = fleet.compute_fleet_energy()
print(f"Fleet energy: {energy}")

# Find class defects
defects = fleet.find_class_defects()
for inv, repos in defects.items():
    print(f"{inv}: affects {len(repos)} repos")
```

### Z3 SMT Solver

```python
from repo_doctor.solver.z3_model import Z3Model

z3 = Z3Model()

if z3.is_available():
    # Prove invariants
    repo_state = {
        "entrypoints": ["cli", "server"],
        "modules": ["main", "api"],
        "initialized": True,
        "specs_count": 5,
    }
    
    result = z3.prove_invariant("entrypoint", repo_state)
    print(f"Satisfiable: {result.satisfiable}")
    
    if not result.satisfiable:
        print(f"Unsat core: {result.unsat_core}")
```

---

## Architecture Formulas

### State Space
```
|Ψ_repo(t)⟩ = Σ(k=1 to 12) αk(t)|ψk⟩

αk(t) ∈ [0, 1]:
  1 = intact
  0 = collapsed
  intermediate = degraded
```

### Energy
```
E_repo(t) = Σ(k=1 to 12) λk (1 - αk(t))²

Severity Weights λk:
  λ_syntax = 100    λ_imports = 95
  λ_api = 95        λ_entrypoints = 90
  λ_packaging = 90  λ_runtime = 85
  λ_security = 100  λ_types = 75
  λ_persistence = 70 λ_status = 70
  λ_history = 60    λ_docs_tests = 40
```

### Hard Invariants
```
RepoValid = I_parse ∧ I_import ∧ I_type ∧ I_api ∧ I_entry ∧ I_pack ∧
            I_runtime ∧ I_persist ∧ I_status ∧ I_tests ∧ I_security ∧ I_history
```

### Mixed State
```
ρ_repo(t) = Σi pi |Ψ_i(t)⟩⟨Ψ_i(t)|
```

### Entanglement
```
M_ij = α·Import(i,j) + β·Call(i,j) + γ·SharedTests(i,j) +
       δ·DocCoupling(i,j) + ε·GitCoChange(i,j)
```

---

## Output Schema

### JSON Format

```json
{
  "repository": "/path/to/repo",
  "timestamp": "2026-04-15T10:30:00",
  "state_vector": {
    "syntax": 0.99,
    "imports": 0.86,
    "api": 0.19,
    ...
  },
  "energy": 312.5,
  "critical_dimensions": ["api", "entrypoints"],
  "hard_invariant_failures": [
    {
      "name": "I_api",
      "severity": "critical",
      "message": "docs/runtime mismatch"
    }
  ],
  "repo_valid": false,
  "minimal_failing_cut": [...],
  "unsat_core": [...]
}
```

---

## Integration Guide

### Tree-sitter

```python
from repo_doctor.ingest.treesitter_ingest import TreeSitterIngest

ingest = TreeSitterIngest('/path/to/repo')
result = ingest.parse_file('module.py')

print(f"Language: {result.language}")
print(f"Imports: {result.imports}")
print(f"Exports: {result.exports}")
```

### CodeQL

```python
from repo_doctor.ingest.codeql_bridge import CodeQLBridge

bridge = CodeQLBridge('/path/to/repo')

# Create database
bridge.create_database('python-db')

# Run queries
results = bridge.run_queries(['security', 'api'])
```

### Joern

```python
from repo_doctor.ingest.joern_bridge import JoernBridge

bridge = JoernBridge('/path/to/repo')
bridge.import_code()

# Query CPG
flows = bridge.find_data_flows('source', 'sink')
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Z3 not available | `pip install z3-solver` |
| Tree-sitter fails | `pip install tree-sitter-python` |
| Parse errors | Check file encoding (UTF-8 recommended) |
| High energy | Run `repair-plan` to get optimization |
| Missing invariants | Check external tool installations |

---

## Performance Tips

1. **Use caching**: Results are cached in `ParsedFile` objects
2. **Incremental parsing**: Tree-sitter only re-parses changed regions
3. **Parallel analysis**: Fleet analysis can run across repos concurrently
4. **Z3 timeout**: Set solver timeout for large verification tasks

---

## Resources

- **Architecture**: `REPO_DOCTOR_OMEGA_DESIGN_DOCUMENT.md`
- **Implementation**: `REPO_DOCTOR_OMEGA_INFINITY_IMPLEMENTATION.md`
- **Complete Guide**: `REPO_DOCTOR_OMEGA_INFINITY_COMPLETE.md`
- **Demo**: `demo_omega_infinity.py`

---

**Repo Doctor Ω∞ - Maximum Strength Repository Mechanics**
