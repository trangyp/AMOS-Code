# AMOS Claw Code

<p align="center">
  <strong>Python Implementation of Agent Harness Tools</strong>
</p>

---

## Overview

This is the Python implementation of agent harness tools within the AMOS ecosystem. It provides the core framework for agent orchestration, tool management, and runtime context handling.

## Repository Layout

```text
.
├── src/                                # Python workspace
│   ├── __init__.py
│   ├── commands.py
│   ├── main.py
│   ├── models.py
│   ├── port_manifest.py
│   ├── query_engine.py
│   ├── task.py
│   └── tools.py
├── tests/                              # Python verification
└── README.md
```

## Python Workspace Overview

The Python `src/` tree provides:

- **`port_manifest.py`** — summarizes the current Python workspace structure
- **`models.py`** — dataclasses for subsystems, modules, and backlog state
- **`commands.py`** — command port metadata
- **`tools.py`** — tool port metadata
- **`query_engine.py`** — renders a porting summary from the active workspace
- **`main.py`** — a CLI entrypoint for manifest and summary output

## Quickstart

Render the Python workspace summary:

```bash
python3 -m src.main summary
```

Print the current Python workspace manifest:

```bash
python3 -m src.main manifest
```

List the current Python modules:

```bash
python3 -m src.main subsystems --limit 16
```

Run verification:

```bash
python3 -m unittest discover -s tests -v
```

Inspect command/tool inventories:

```bash
python3 -m src.main commands --limit 10
python3 -m src.main tools --limit 10
```

## License

MIT License - See LICENSE file for details.

---

**AMOS Project** - Building the future of AI cognition.
