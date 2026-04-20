---
title: "P0-1: Define canonical AMOS runtime contract"
labels: ["stabilization", "phase-0", "critical", "architecture"]
assignees: []
---

## Problem

The repo currently has multiple conflicting runtime contracts:
- **Source-tree scripts**: 48+ root-level `.py` files executable directly
- **Package entrypoints**: 6 console scripts (some duplicates)
- **CI smoke imports**: Tests individual files directly
- **Docker startup**: Uses `amos-brain` entrypoint after pip install
- **Legacy patterns**: `sys.path.insert` compensates for broken structure

This creates confusion about the "correct" way to run AMOS.

## Current State

### Entrypoints (pyproject.toml)
```toml
[project.scripts]
amos-brain = "amos_brain.cli:main"      # Primary
amos-cli = "amos_brain.cli:main"         # DUPLICATE - remove
amos-launcher = "amos_brain.launcher:main"  # Shells out to filenames - remove
amos-tutorial = "amos_brain.tutorial:main"  # Merge into CLI
amos-cookbook = "amos_brain.examples.cookbook_runner:main"  # Merge into CLI
amosl = "amosl.cli:main"                 # Separate DSL - keep but separate
```

### Root-Level Scripts (competing execution)
```
ACTIVATE_BRAIN.py
AMOS_BRAIN_CASCADE_FINAL.py
amos_*.py (50+ files)
...
```

## Proposed Canonical Contract

### Option A: Installable Library (Recommended)
```python
# Primary usage
import amos_brain
brain = amos_brain.get_brain()

# CLI as secondary
amos-brain --help
```

### Option B: Deployable App
```bash
# Primary usage
amos-brain serve
amos-brain status
amos-brain doctor

# Library usage secondary
python -c "import amos_brain; ..."
```

## Decision Required

| Aspect | Option A (Library) | Option B (App) |
|--------|-------------------|----------------|
| Primary use | `import amos_brain` | `amos-brain` CLI |
| Entrypoints | Minimal (1) | Full feature set |
| CI focus | Import tests | CLI tests |
| Docker CMD | `python -c "import amos_brain; ..."` | `amos-brain serve` |

## Done When

- [ ] Document `AMOS_RUNTIME_CONTRACT.md` defining canonical path
- [ ] Decision recorded: Library-first OR App-first
- [ ] All entrypoints reconciled with decision
- [ ] README updated to show ONE primary command
- [ ] Backwards compatibility plan for removed entrypoints

## Related

- Blocks: #2 (brain-health CI gate)
- Precedes: #3 (remove path hacks), #4 (unify entrypoints)
