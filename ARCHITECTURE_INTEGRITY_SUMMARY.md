# Architectural Integrity Engine - Implementation Summary

## Overview

The Repo Doctor has been extended with a higher-order **Architectural Integrity Engine** that models repository health at the architecture level, not just at the code level.

## Core Equation

The state vector now includes architectural dimensions:

```
Ψ_repo(t) = [
    s(t),       # syntax integrity
    i(t),       # import integrity
    b(t),       # build integrity
    τ(t),       # test integrity
    p(t),       # packaging integrity
    a(t),       # API integrity
    d(t),       # dependency integrity
    c(t),       # config integrity
    h(t),       # history stability
    σ(t),       # security integrity
    αArch(t),   # architectural integrity (NEW)
    αHidden(t)  # hidden state integrity (NEW)
]
```

## New Components

### 1. Architecture Graph (`architecture.py`)

Models the system as a graph G_arch = (V_arch, E_arch, Φ_arch):

**Node Types (V_arch):**
- `ServiceNode` - Runtime services
- `LibraryNode` - Code libraries
- `SchemaAuthorityNode` - Schema truth owners
- `PolicyNode` - Policy engines
- `LauncherNode` - Launch mechanisms
- `MigrationChainNode` - Migration sequences
- `ObservabilityNode` - Monitoring components
- ...and 12 more

**Edge Types (E_arch):**
- `owns_truth_of` - Canonical authority
- `derives_from` - Mechanical derivation
- `generates` - Codegen/production
- `must_rollout_with` - Coupled rollouts
- `crosses_boundary` - Boundary crossings
- `observes` - Observability attachment
- ...and 10 more

**Four Planes:**
- `ControlPlane` - Declarative policy/state
- `DataPlane` - Operational data
- `ExecutionPlane` - Runtime execution
- `ObservationPlane` - Monitoring/observability

### 2. Architectural Invariants (`arch_invariants.py`)

Seven higher-order invariants:

| Invariant | Description | Failure Mode |
|-----------|-------------|--------------|
| `I_boundary` | Components enforce policy only within declared boundary | Launcher activating policy |
| `I_authority` | Every fact has exactly one authoritative owner | Version in both pyproject.toml and __init__.py |
| `I_plane_separation` | Control/data/execution/observation don't substitute | Control deriving from execution |
| `I_interface_visibility` | All significant interfaces are explicit | Hidden env var dependencies |
| `I_folklore_free` | No correctness-critical operation needs folklore | "Run migration before starting" |
| `I_arch_commute` | [A_declared, A_actual] = 0 (no architecture drift) | Declared docs don't match implementation |
| `I_upgrade` | All upgrade paths preserve validity | Rollback corrupts state |

### 3. Extended State Vector (`state_vector.py`)

Two new dimensions added:

| Dimension | Symbol | Weight | Penalty |
|-----------|--------|--------|---------|
| Architecture | αArch | 0.85 | 15 |
| Hidden State | αHidden | 0.60 | 5 |

### 4. Architecture-Aware Repair (`repair_plan.py`)

Repair actions now include architecture constraints:

```python
@dataclass
class RepairAction:
    # ... existing fields ...
    
    # Architecture-aware constraints
    restores_arch_invariants: bool = True
    reduces_authority_duplication: bool = True
    preserves_boundary_integrity: bool = True
    preserves_upgrade_admissibility: bool = True
    preserves_rollout_safety: bool = True
    preserves_observability: bool = True
    
    arch_violation_type: str | None = None
```

New planning objective:
```
min_R [
    c1·EditCost +
    c2·BlastRadius +
    c3·EntanglementRisk +
    c4·AuthorityDuplicationIncrease +
    c5·BoundaryViolationIncrease
    - c6·ArchitectureIntegrityGain
]
```

## Usage

```python
from repo_doctor import (
    ArchitectureInvariantEngine,
    ArchitectureGraph,
    RepairPlanner,
    StateDimension,
)

# Build and analyze architecture graph
graph = build_architecture_graph("./my_repo")
print(f"Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}")

# Run architectural invariants
engine = ArchitectureInvariantEngine("./my_repo")
arch_score, hidden_score, results = engine.get_architectural_state()
print(f"αArch: {arch_score}, αHidden: {hidden_score}")

# Generate architecture-aware repair plan
planner = RepairPlanner("./my_repo")
plan = planner.generate_architecture_plan(state, results)
```

## Demo Output

Running `python repo_doctor/arch_demo.py` on this repo produces:

```
======================================================================
ARCHITECTURAL INTEGRITY ENGINE DEMO
======================================================================

1. Building Architecture Graph...
   - Nodes discovered: 2
   - Edges discovered: 1
   - Authority claims: 2

2. Running Architectural Invariants...
   - Invariants checked: 7
   - Passed: 4
   - Failed: 3
   
   Failed invariants:
     ✗ single_authority: 1 authority issues detected
       - Authority duplication: 'package_version' claimed by config:pyproject, file:repo_doctor/__init__.py
     ✗ hidden_interfaces: 121 hidden interfaces detected
     ✗ folklore_free: 1 folklore dependencies detected

3. Computing Architectural State Dimensions...
   - αArch(t) (Architectural Integrity): 0.57
   - αHidden(t) (Hidden State): 0.50

4. Architecture-Aware Repair Planning...
   - Total actions: 3
   - Total risk: high
   - Estimated time: 3-8 hours
```

## Files Added/Modified

### New Files
- `repo_doctor/architecture.py` - Architecture graph model
- `repo_doctor/arch_invariants.py` - Architectural invariants
- `repo_doctor/arch_demo.py` - Demo script

### Modified Files
- `repo_doctor/state_vector.py` - Added ARCHITECTURE and HIDDEN_STATE dimensions
- `repo_doctor/repair_plan.py` - Added architecture-aware repair constraints
- `repo_doctor/__init__.py` - Exported new architectural components
- `repo_doctor/bisect_engine.py` - Fixed imports
- `repo_doctor/cli.py` - Fixed imports
- `repo_doctor/history.py` - Fixed imports

## Version

Updated to `0.2.0-arch` to reflect the architectural integrity layer addition.

## Next Steps

1. **Integration**: Connect architecture analysis with the main CLI
2. **Visualization**: Add graph visualization for architecture nodes/edges
3. **CI/CD**: Add architectural invariants to release gates
4. **Documentation**: Document architecture patterns for your specific repos
