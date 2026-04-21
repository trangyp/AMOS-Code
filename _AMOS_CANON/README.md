# AMOS Canonical System (_00_AMOS_CANON)

The One Source of Truth for AMOS Architecture.

## Structure

```
_00_AMOS_CANON/
├── Core/
│   └── Cognitive_Stack/
│       ├── canonical_identity.py    # Identity management
│       ├── law_engine.py            # Constitutional law enforcement
│       ├── evolution_controller.py  # Evolution management
│       └── state_manager.py         # Canonical state management
├── Core/7_Intelligents/
│   ├── perception_engine.json
│   ├── reasoning_engine.json
│   ├── learning_engine.json
│   ├── memory_engine.json
│   ├── action_engine.json
│   ├── communication_engine.json
│   └── metacognition_engine.json
├── Integration/
│   ├── canon_integration_layer.py  # Central integration hub
│   ├── repository_bridge.py        # Repository connectivity
│   └── system_orchestrator.py      # System coordination
└── Registry/
    ├── component_registry.json     # Component catalog
    ├── equation_registry.json      # Canonical equations
    └── invariant_registry.json     # System invariants
```

## Principles

1. **Single Source of Truth**: Each concept has exactly one canonical representation
2. **Immutable Contracts**: All interfaces are versioned and explicit
3. **Lazy Loading**: Components initialize on first access
4. **Singleton Pattern**: One instance per canonical component

## Usage

```python
from _00_AMOS_CANON.Core.Cognitive_Stack.law_engine import get_law_engine

law_engine = get_law_engine()
law_engine.initialize()
violations = law_engine.check_compliance("my_component", "action")
```

## Integration

All AMOS repositories should reference canonical definitions from this directory.
