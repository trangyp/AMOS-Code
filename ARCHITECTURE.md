# AMOS Architecture

## Authority Hierarchy

```
┌─────────────────────────────────────────┐
│           AMOS Brain (Facade)           │
│    Single source of truth for cognition │
└──────────────────┬──────────────────────┘
                   │
    ┌──────────────┼──────────────┬──────────────┐
    │              │              │              │
┌───▼───┐    ┌────▼───┐    ┌─────▼───┐    ┌──────▼────┐
│ Laws  │    │ Agent  │    │  State  │    │  Monitor  │
│       │    │ Bridge │    │ Manager │    │           │
└───────┘    └────────┘    └─────────┘    └───────────┘
```

## Layer Responsibilities

### 1. Brain Layer (amos_brain/)
- **Authority**: Primary cognitive orchestration
- **Exports**: BrainClient, get_brain(), think(), decide()
- **Dependencies**: None (root authority)

### 2. Laws Layer (amos_brain/laws.py)
- **Authority**: Validation and compliance
- **Exports**: GlobalLaws, validate_action()
- **Dependencies**: None (standalone rules)

### 3. Agent Bridge (amos_brain/agent_bridge.py)
- **Authority**: External system integration
- **Exports**: AgentBridge, get_agent_bridge()
- **Dependencies**: Brain, Laws

### 4. State Manager (amos_brain/state_manager.py)
- **Authority**: Persistent state
- **Exports**: StateManager, get_state_manager()
- **Dependencies**: None (storage layer)

### 5. Monitor (amos_brain/monitor.py)
- **Authority**: Runtime observation
- **Exports**: Monitor, get_monitor()
- **Dependencies**: StateManager

## Interface Contracts

### Public API Surface
```python
# Primary entry point
from amos_brain.facade import BrainClient

# Law validation
from amos_brain.laws import GlobalLaws

# State management
from amos_brain.state_manager import get_state_manager
```

### Hidden Interfaces (to be documented)
- Environment variables via `os.environ`
- Filesystem paths for state storage
- Network endpoints for agent communication

## Dependency Graph

```mermaid
amos_brain/facade.py
├── amos_brain/laws.py
├── amos_brain/agent_bridge.py
├── amos_brain/state_manager.py
├── amos_brain/monitor.py
└── amos_brain/meta_controller.py
```

## Singleton Pattern

All major components use singleton pattern via `get_*()` functions:

```python
@lru_cache(maxsize=1)
def get_brain() -> Brain:
    """Singleton brain instance."""
    return Brain()
```

This prevents authority duplication.

## Known Issues

### Authority Inversion
- **Location**: `amos_brain/facade.py`
- **Issue**: 7 getter functions without caching
- **Fix**: Add `@lru_cache` decorators

### Hidden Interfaces (138 found)
- **Pattern**: Direct `os.environ` access
- **Files**: `amos_mcp_server.py`, `amos_clawspring.py`, etc.
- **Fix**: Centralize in `config.py`

### Folklore Dependencies (2 found)
- **Issue**: Imports not documented in README
- **Fix**: Add to ARCHITECTURE.md imports section
