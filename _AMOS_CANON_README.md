# AMOS Canonical Structure

The canonical AMOS directory structure as defined in `AMOS_CANONICAL_GLOSSARY.json`.

## Core Directories

- `AMOS_OS/` - Operating System interface (AMOS_OS.py)
- `AMOS_WORKERS/` - Task execution units (worker registry)
- `AMOS_ORGANISM_OS/` - 15-layer biological organism
- `AMOS_UNIVERSE/` - Canonical knowledge layer
- `_AMOS_REPORTS/` - System reports and audits
- `_AMOS_STATE_LOG/` - State logs and checkpoints

## Core Files

- `AMOS_OS.py` - OS singleton with 6-repo integration
- `AMOS_RUNTIME.py` - Master execution engine
- `AMOS_GODMODE.py` - Executive controller (OMEGA/GAMMA/SIGMA modes)
- `start_godmode_full.sh` - Full system activation script
- `vision_run.py` - Vision task execution

## Usage

```bash
# Activate full system
./start_godmode_full.sh

# Run vision task
python vision_run.py "analyze system status"

# Heal system
python vision_run.py --task heal
```

## 6 Repository Integration

All repos linked under `AMOS_REPOS/`:
- AMOS-Code (core)
- AMOS-Consulting (API hub)
- AMOS-Claws (operator interface)
- Mailinhconect (product layer)
- AMOS-Invest (analytics)
- AMOS-UNIVERSE (knowledge)
