# AMOS ORGANISM OS v1.0.0

## 14-Subsystem Digital Organism

The AMOS (Advanced Machine Organism System) is a deterministic, auditable,
humane intelligence system for high-risk operations.

### Architecture

Based on the AMOS 7-System Organism Blueprint, this implementation provides:

**Primary Loop (Circulation):**
```
01_BRAIN -> 02_SENSES -> 05_SKELETON -> 08_WORLD_MODEL ->
12_QUANTUM_LAYER -> 06_MUSCLE -> 07_METABOLISM -> 01_BRAIN
```

**Core Subsystems Implemented:**

| Code | Name | Role | Status |
|------|------|------|--------|
| 01_BRAIN | Brain | Reasoning, planning, memory, routing | ✅ Active |
| 06_MUSCLE | Muscle | Execute commands, write code, deploy | ✅ Active |
| 14_INTERFACES | Interfaces | CLI, API, dashboard | ✅ Active |

### File Structure

```
AMOS_ORGANISM_OS/
├── 01_BRAIN/               # Brain subsystem implementation
│   ├── brain_os.py        # Core reasoning engine (7-layer model)
│   ├── router.py          # System routing decisions
│   └── memory_layer.py    # 7-layer memory system
├── 06_MUSCLE/              # Muscle subsystem implementation
│   ├── executor.py        # Command execution engine
│   ├── code_runner.py     # Multi-language code runner
│   └── workflow_engine.py # Workflow orchestration
├── 14_INTERFACES/          # Interface subsystem
│   ├── cli.py            # Command-line interface
│   └── api_server.py     # HTTP API server
├── BRAIN/                  # Import alias for 01_BRAIN
├── MUSCLE/                 # Import alias for 06_MUSCLE
├── INTERFACES/             # Import alias for 14_INTERFACES
├── organism.py            # Main orchestrator
├── run.py                 # CLI runner
└── system_registry.json   # Subsystem registry
```

### Usage

**Run the demo:**
```bash
python3 organism.py
# or
python3 run.py demo
```

**Check status:**
```bash
python3 run.py status
```

**Interactive CLI:**
```bash
python3 run.py cli
```

**Start API server:**
```bash
python3 run.py api
```

### Brain 7-Layer Model

1. **Sensory Layer**: Raw inputs
2. **Perceptual Layer**: Pattern detection
3. **Concept Layer**: Stable concepts
4. **Narrative Layer**: Stories, scenarios
5. **Causal Layer**: Cause-effect chains
6. **Systemic Layer**: Multi-system reasoning
7. **Meta Layer**: Self-audit, ethics, risk

### Memory 7-Layer System

- **sensory**: Immediate buffer (100ms retention)
- **working**: Active processing (seconds)
- **short_term**: Recent context (minutes-hours)
- **episodic**: Event sequences (days)
- **semantic**: Facts/concepts (persistent)
- **procedural**: Skills/how-to (persistent)
- **long_term**: Consolidated storage (years)

### Integration with AMOS Brain

This organism implementation connects to the AMOS brain specification
located in `/_AMOS_BRAIN/` and uses:

- `system_registry.json` for subsystem definitions
- Core cognitive engines from `_AMOS_BRAIN/Core/`
- Kernels from `_AMOS_BRAIN/Kernels/`

### License

Academic research and educational purposes only.
Built by Trang based on AMOS architecture.
