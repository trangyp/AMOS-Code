# Repo Doctor

A **deterministic repository diagnostic system** with a quantum-inspired state-space model.

## Core Model

Repository state is defined as:

```
Ψ_repo(t) = [
    s(t),   # syntax integrity
    i(t),   # import / module integrity
    b(t),   # build integrity
    τ(t),   # test integrity
    p(t),   # packaging integrity
    a(t),   # API contract integrity
    d(t),   # dependency integrity
    c(t),   # config / entrypoint integrity
    h(t),   # history stability
    σ(t)    # security integrity
]
```

Each term is normalized to [0, 1].

## Invariant Law

A repo is valid only if:

```
∀ I_n ∈ I : I_n(Ψ_repo) = 1
```

Not "mostly good." **Pass or fail.**

## Repo Energy

```
E_repo = Σ w_k · (1 - Ψ_k)^2
```

- Low `E_repo` = stable
- High `E_repo` = structurally degraded

## Installation

```bash
pip install -e .
```

## Usage

### Full Scan

```bash
repo-doctor scan .
```

With all analyses:

```bash
repo-doctor scan . --contracts --packaging --entanglement --json
```

### Check Contracts

```bash
repo-doctor contracts .
```

### Find First Bad Commit

```bash
repo-doctor bisect packaging . --good v1.0.0 --bad HEAD
```

### Generate Repair Plan

```bash
repo-doctor fix-plan . --export repair.sh
```

## Architecture

```
repo_doctor/
├── state_vector.py      # Quantum repo state model
├── invariants.py        # Hard invariant engine
├── contracts.py         # API contract commutator
├── packaging.py         # Packaging invariant
├── entrypoints.py       # Entrypoint invariant
├── persistence.py       # Persistence invariant
├── entanglement.py      # Dependency matrix
├── history.py           # Temporal analysis
├── bisect_engine.py     # Temporal debugger
├── repair_plan.py       # Repair planning
└── cli.py               # Command interface
```

## Invariants

1. **Parse**: All source files parse
2. **Import**: Every import resolves
3. **Build**: Package builds from metadata
4. **Test**: Critical tests pass
5. **Packaging**: pyproject.toml/setup.py valid
6. **API**: Public contract matches runtime
7. **Persistence**: Serialize/deserialize roundtrips
8. **Status**: State labels reflect reality
9. **Entrypoint**: Every launcher points to real code
10. **Security**: No known vulnerabilities

## Scoring Model

```
Score_repo = 100
    - 20·fail(parse)
    - 20·fail(import)
    - 20·fail(packaging)
    - 15·fail(api)
    - 10·fail(entrypoints)
    - 10·fail(persistence)
    - 5·fail(status)
```

Hard-fail classes: parse, import, packaging, API, entrypoints.

If any fail: `releaseable = false`

## License

MIT
