# AMOS Runtime Contract

**Version:** 1.0.0  
**Date:** 2026-04-20  
**Package:** amos-brain  

## Canonical Runtime Path

The single supported execution surface for AMOS is:

```bash
amos-brain [command] [options]
```

Alternative: `python -m amos_brain [command] [options]`

## Installation

```bash
pip install amos-brain
# Or with all extras
pip install "amos-brain[all]"
```

## Public Entrypoints

| Command | Module | Description |
|---------|--------|-------------|
| `amos-brain` | `amos_brain.cli:main` | Primary CLI |
| `amosl` | `amosl.cli:main` | Domain-specific language |

## Public API Surface

### Core Exports (from `amos_brain`)

```python
from amos_brain import (
    get_brain,           # Brain instance
    process_task,        # Task processing
    GlobalLaws,          # L1-L6 law enforcement
    KernelRouter,        # Task routing
    get_agent_bridge,    # Agent validation
    get_state_manager,   # Reasoning memory
    get_meta_controller, # Orchestration
)
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `amos-brain status` | Show 8-layer architecture status |
| `amos-brain think <task>` | Process task through brain |
| `amos-brain orchestrate` | Run meta-cognitive workflow |
| `amos-brain doctor` | Self-diagnosis and health check |

## Forbidden Patterns

The following patterns are prohibited in production code:

- `sys.path.insert` - Use proper package imports
- `except:` - Use explicit exception types
- `datetime.utcnow()` - Use `datetime.now(timezone.utc)`

## Contract Validation

Run the contract validator:

```bash
amos-brain doctor --contract
```

## Legacy Deprecation

The following are deprecated and will be removed:

- `python amos_brain_launcher.py` → Use `amos-brain`
- `python amos_brain_cli.py` → Use `amos-brain`
- `python amos_brain_tutorial.py` → Use `amos-brain --tutorial`

## Docker

```bash
docker run -p 8000:8000 amos-brain:14.0.0
```

The Docker image uses the installed package entrypoint, not source files.
