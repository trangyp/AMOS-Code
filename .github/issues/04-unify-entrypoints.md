---
title: "P1-2: Move all published entrypoints into package modules"
labels: ["stabilization", "phase-1", "critical", "refactor"]
assignees: []
---

## Problem

The brain is "thinking through five mouths." Multiple entrypoints create confusion:

```toml
[project.scripts]
amos-brain = "amos_brain.cli:main"      # Keep
amos-cli = "amos_brain.cli:main"         # DUPLICATE - remove
amos-launcher = "amos_brain.launcher:main"  # Shell spaghetti - remove
amos-tutorial = "amos_brain.tutorial:main"  # Merge into cli
amos-cookbook = "amos_brain.examples.cookbook_runner:main"  # Merge into cli
```

## Proposed Canonical Entrypoint

### Primary: `amos-brain`
```bash
amos-brain --help          # Show all commands
amos-brain status          # Brain health
amos-brain doctor          # Self-diagnosis
amos-brain tutorial        # Interactive tutorial (merged)
amos-brain cookbook        # Run cookbook (merged)
```

### Secondary: `python -m amos_brain`
```bash
python -m amos_brain       # Same as amos-brain
python -m amos_brain.cli    # Explicit CLI module
```

### Separate: `amosl` (DSL)
Keep as separate console script for the AMOSL language.

## Migration Plan

| Current Entrypoint | Action | New Location |
|-------------------|--------|--------------|
| `amos-brain` | Keep | `amos_brain.cli:main` |
| `amos-cli` | **Remove** | Use `amos-brain` |
| `amos-launcher` | **Remove** | Merge into `amos-brain` subcommands |
| `amos-tutorial` | **Merge** | `amos-brain tutorial` subcommand |
| `amos-cookbook` | **Merge** | `amos-brain cookbook` subcommand |
| `amosl` | Keep separate | `amosl.cli:main` |

## Implementation

### 1. Merge Tutorial into CLI

```python
# amos_brain/cli.py
def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    # Existing commands
    subparsers.add_parser('status', help='Show brain status')
    subparsers.add_parser('doctor', help='Self-diagnosis')
    
    # NEW: Merged from amos-tutorial
    tutorial_parser = subparsers.add_parser('tutorial', help='Interactive tutorial')
    
    # NEW: Merged from amos-cookbook  
    cookbook_parser = subparsers.add_parser('cookbook', help='Run cookbook examples')
```

### 2. Deprecate Duplicate Entrypoints

```python
# amos_brain/_deprecated.py
def amos_cli_deprecated():
    """Warn and redirect to amos-brain."""
    print("WARNING: amos-cli is deprecated. Use amos-brain instead.")
    from amos_brain.cli import main
    main()
```

### 3. Update pyproject.toml

```toml
[project.scripts]
amos-brain = "amos_brain.cli:main"
amosl = "amosl.cli:main"
# REMOVED: amos-cli, amos-launcher, amos-tutorial, amos-cookbook
```

## Done When

- [ ] One primary entrypoint documented: `amos-brain`
- [ ] Duplicate entrypoints removed from pyproject.toml
- [ ] Tutorial merged as `amos-brain tutorial` subcommand
- [ ] Cookbook merged as `amos-brain cookbook` subcommand
- [ ] Launcher subprocess calls use entrypoints not filenames
- [ ] README shows one primary command
- [ ] Backwards compatibility: deprecated entrypoints show warning

## Related

- Depends on: #1 (runtime contract), #3 (path hacks)
- Related: #5 (launcher subprocess fixes)
