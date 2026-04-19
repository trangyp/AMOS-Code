# AXIOM One - Technical Operating System

The next-generation AI coding platform that surpasses Claude Code and Devin through superior architecture.

## Core Architecture

AXIOM One is built on 4 tightly coupled systems:

```
┌─────────────────────────────────────────────────────────────┐
│                    AXIOM One                                │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│   Operator  │   Swarm     │    Twin     │    Ledger       │
│  (Local)    │(Multi-Agent)│(Digital Twin)│ (Governance)   │
├─────────────┴─────────────┴─────────────┴─────────────────┤
│              Execution Slot Primitive                       │
└─────────────────────────────────────────────────────────────┘
```

### 1. Execution Slot (Core Primitive)
The fundamental unit of work - replaces "conversation" with a structured, reproducible, verifiable execution context.

**Components:**
- `RepoSnapshot`: Git state, file hashes, dependencies
- `EnvironmentSnapshot`: Env vars, feature flags, secrets hash
- `ToolPermissions`: What tools this slot can use
- `SlotBudget`: Time, cost, token limits
- `AcceptanceCriteria`: How to verify success
- `RollbackPath`: How to undo if needed
- `EventLog`: Immutable history of actions

**3 Operating Modes:**
- `LOCAL`: Terminal/editor native (beats Claude Code on speed)
- `MANAGED`: Isolated workspace (beats Devin on reproducibility)
- `ORCHESTRATION`: Multi-agent swarm execution

### 2. Operator (Local-First Developer Surface)
Beats Claude Code on:
- Terminal-native speed (no latency to cloud)
- Editor-native integration (VS Code, vim, emacs)
- Scriptability (composable Unix-style workflows)
- Local model support (no API keys needed)
- Branch-aware operations
- Policy-aware from the start

**Tools:**
- `read`: File reading with offset/limit
- `write`: File writing with change tracking
- `edit`: String replacement with rollback tracking
- `bash`: Shell command execution
- `grep`: Pattern search across files
- `glob`: File pattern matching
- `git`: Git operations
- `test`: Test runner
- `lint`: Linter execution

### 3. Swarm (Multi-Agent Scheduler)
Beats Devin on:
- True parallel execution (not just managed sessions)
- Planner/Worker/Critic/Verifier/Integrator architecture
- DAG-based task decomposition
- Branch-per-subtask isolation
- Merge-safe integration

**Agent Roles:**
- `Planner`: Decomposes tasks into DAG of subtasks
- `Workers`: Execute in parallel on isolated branches
- `Critic`: Checks for contradictions and spec drift
- `Verifier`: Runs tests, benchmarks, policy checks
- `Integrator`: Merges only validated outputs

### 4. Twin (Digital Twin of Codebase and Runtime)
Captures and replays environment states:
- Repo graph: Files, imports, dependencies
- Runtime graph: Services, endpoints, databases
- Incident graph: Failures and their causes
- Cost graph: Resource attribution

**Capabilities:**
- Environment state capture with signatures
- Failure replay for debugging
- State comparison for change detection
- Environment reproduction

### 5. Ledger (Governance and Economics Layer)
Permissions, approvals, policy checks, audit receipts:
- Policy rules with severity levels
- Audit receipts with immutable hashes
- Spend tracking and cost attribution
- Risk scoring
- Rollout control

## Usage

### Basic Execution
```python
from axiom_one import AxiomOne, OrchestratorConfig, SlotMode

# Initialize
axiom = AxiomOne(OrchestratorConfig(repo_path="/path/to/repo"))

# Execute in local mode
slot = axiom.execute("Refactor authentication module", mode=SlotMode.LOCAL)

print(f"Slot: {slot.slot_id}")
print(f"Status: {slot.status}")
print(f"Receipt: {slot.verification_bundle}")
```

### Brain-Powered Execution
```python
from axiom_one import BrainPoweredOrchestrator, BrainExecutionConfig

# Initialize with brain integration
orchestrator = BrainPoweredOrchestrator(
    BrainExecutionConfig(
        enable_cognitive_planning=True,
        enable_repo_doctor=True,
    )
)

# Execute with full brain integration
slot = orchestrator.execute_intelligent(
    objective="Build new API endpoint with tests",
    mode=SlotMode.ORCHESTRATION
)
```

### CLI Usage
```bash
# Execute with brain power
python -m axiom_one execute "Fix bug in user auth" --brain --mode orch

# Capture environment state
python -m axiom_one twin capture --label before_changes

# Compare states
python -m axiom_one twin compare --state-a before --state-b after

# Show status
python -m axiom_one status --json
```

## File Structure

```
axiom_one/
├── __init__.py              # Public API exports
├── execution_slot.py        # Core primitive
├── operator.py              # Local developer surface
├── swarm.py                 # Multi-agent scheduler
├── twin.py                  # Digital twin
├── ledger.py                # Governance layer
├── orchestrator.py          # Integration layer
├── brain_integration.py     # AMOS Brain integration
└── cli.py                   # Command line interface
```

## Integration with AMOS Brain

AXIOM One integrates with existing AMOS components:

| AXIOM One | AMOS Component | Purpose |
|-----------|---------------|---------|
| BrainPoweredOrchestrator | `amos_brain.super_brain` | Cognitive execution |
| BrainPoweredOrchestrator | `amos_brain.cognitive_engine` | Task decomposition |
| BrainPoweredOrchestrator | `amos_brain.kernel_router` | Engine routing |
| Ledger | `repo_doctor` | Verification & invariants |
| Twin | `amos_brain.memory` | State persistence |
| Swarm | `multi_agent.subagent` | Agent definitions |

## Architecture Mapping: AMOS → AXIOM One

| AMOS Component | AXIOM One Role | Action |
|---------------|----------------|--------|
| `amos_brain` | Brain integration | **Keep** - Core cognitive layer |
| `repo_doctor` | Verification layer | **Keep** - Invariant checking |
| `multi_agent` | Swarm workers | **Merge** - Agent definitions |
| `amos_execution_platform` | Managed mode | **Merge** - Sandbox providers |
| `amos_muscle_executor` | Operator tools | **Merge** - Tool implementations |
| `AMOS_ORGANISM_OS` | All systems | **Integrate** - 14-layer organism |

## License

MIT License - AMOS System
