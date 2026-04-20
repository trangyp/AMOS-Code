---
title: "P1-1: Remove all runtime sys.path.insert usage"
labels: ["stabilization", "phase-1", "critical", "refactor"]
assignees: []
---

## Problem

`sys.path.insert(...)` is compensating for broken package structure. It's a symptom, not a solution. The pyproject.toml shows Ruff E402 exceptions for many file patterns:

```toml
[tool.ruff.lint.per-file-ignores]
"amos_*.py" = ["E402", "F401"]
"backend/**/*.py" = ["E402", "F401"]
"clawspring/**/*.py" = ["E402", "F401"]
```

## Current State

### Path Hacks Found

Search for patterns:
```bash
grep -r "sys.path.insert" --include="*.py" . | grep -v "fix_" | grep -v "batch_"
```

Expected in production code:
- None (or minimal legacy)

### Files with E402 Exceptions

These files have imports that aren't at the top of the file (usually due to path manipulation):

1. `amos_*.py` files at root
2. `backend/**/*.py`
3. `clawspring/**/*.py`
4. `_AMOS_BRAIN/**/*.py`

## Fix Strategy

### 1. Identify Root-Cause Files

For each E402 exception, determine:
- Is it importing from repo root?
- Is it importing from sibling directories outside package?
- Is it a test file that should be in `tests/`?

### 2. Restructure

```
Before:                    After:
amos_cli.py                amos_brain/cli.py (exists!)
  sys.path.insert             from amos_brain import ...
  from amos_brain import ...
```

### 3. Fix Launchers

Current launcher shells out to filenames:
```python
# amos_brain/launcher.py
def run_cli():
    subprocess.run(["amos-cli"])  # OK - uses entrypoint
    # OR (bad)
    subprocess.run([sys.executable, "amos-cli.py"])  # REMOVE
```

## Done When

- [ ] `grep -r "sys.path.insert" --include="*.py" .` finds only fix scripts
- [ ] All E402 per-file ignores removed from pyproject.toml
- [ ] Ruff passes on all production code without exceptions
- [ ] All imports are absolute package imports (`from amos_brain import ...`)
- [ ] Documentation in `docs/IMPORTS.md`

## Related

- Depends on: #1 (runtime contract), #2 (brain-health)
- Blocks: #4 (unify entrypoints)
- Related: #5 (launcher subprocess fixes)
