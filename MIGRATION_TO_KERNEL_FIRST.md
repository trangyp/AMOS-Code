# AMOS Kernel-First Migration Map

## Executive Summary

Migration from 28-phase sprawling architecture to 6-layer kernel-first architecture.

| Metric | Current | Target | Reduction |
|--------|---------|--------|-----------|
| Python Files | 731+ | ~45 | 94% |
| Lines of Code | ~150K | ~8K | 95% |
| Entry Points | 50+ | 2 (`amos-brain`, `amos-brain doctor`) | 96% |
| Dependencies | 200+ | 20 core | 90% |

---

## Phase 0: Kernel Foundation (Week 1)

### New Directory Structure

```
amos_kernel/
├── core/
│   ├── law/
│   │   ├── __init__.py
│   │   ├── invariants.py      ← From: amos_brain/laws.py
│   │   ├── constraints.py     ← From: amos_brain/action_gate.py
│   │   ├── validators.py      ← From: amos_brain/config_validator.py
│   │   ├── collapse.py        ← NEW
│   │   └── types.py           ← NEW
│   │
│   ├── state/
│   │   ├── __init__.py
│   │   ├── tensor.py          ← From: amos_brain/memory.py (TensorState)
│   │   ├── normalize.py       ← From: amos_brain/state_manager.py
│   │   ├── projection.py      ← From: amos_brain/reasoning.py
│   │   ├── integrity.py       ← From: amos_brain/health.py
│   │   ├── load.py            ← NEW
│   │   └── types.py           ← NEW
│   │
│   ├── interaction/
│   │   ├── __init__.py
│   │   ├── operator.py        ← From: amos_brain/cognitive_engine.py
│   │   ├── feedback.py        ← From: amos_brain/meta_cognitive_reflection.py
│   │   ├── coupling.py        ← NEW
│   │   └── transforms.py      ← NEW
│   │
│   ├── deterministic/
│   │   ├── __init__.py
│   │   ├── engine.py          ← From: amos_brain/thinking_engine.py
│   │   ├── transition.py      ← From: amos_brain/task_processor.py
│   │   ├── prediction.py      ← From: amos_brain/predictive_bridge.py
│   │   ├── correction.py      ← From: amos_brain/repair_bridge.py
│   │   ├── policy.py          ← NEW
│   │   └── types.py           ← NEW
│   │
│   ├── observe/
│   │   ├── __init__.py
│   │   ├── drift.py           ← From: amos_brain/monitor.py
│   │   ├── mismatch.py        ← From: amos_brain/doctor.py
│   │   ├── diagnostics.py     ← From: amos_brain/pathology_bridge.py
│   │   ├── reports.py         ← NEW
│   │   └── types.py           ← NEW
│   │
│   └── repair/
│       ├── __init__.py
│       ├── planner.py         ← From: amos_brain/repair_bridge.py
│       ├── simulation.py      ← From: amos_brain/simulation_engine.py
│       ├── executor.py        ← From: amos_brain/execution_bridge.py
│       ├── codemods.py        ← NEW
│       ├── verification.py    ← From: amos_brain/equation_bridge_integration.py
│       └── types.py           ← NEW
│
├── contracts/
│   ├── runtime_contract.py    ← From: AMOS_ORGANISM_OS/00_ROOT/
│   ├── package_contract.py    ← NEW
│   ├── build_contract.py      ← NEW
│   ├── release_contract.py    ← NEW
│   └── forbidden_patterns.py  ← NEW
│
├── runtime/
│   ├── __init__.py
│   ├── bootstrap.py           ← From: AMOS_ORGANISM_OS/00_ROOT/root_kernel.py
│   ├── cli.py                 ← From: amos_brain/cli.py (simplified)
│   ├── doctor.py              ← From: amos_brain/doctor.py
│   ├── config.py              ← From: amos_brain/config.py
│   └── main.py                ← NEW
│
├── adapters/                  ← NEW (minimal)
│   ├── __init__.py
│   ├── repo.py                ← From: repo_doctor/
│   └── filesystem.py          ← NEW
│
├── workflows/                 ← NEW
│   ├── stabilize.py
│   ├── diagnose.py
│   ├── repair.py
│   └── verify.py
│
├── tests/
│   ├── test_law_kernel.py
│   ├── test_deterministic_core.py
│   ├── test_state_model.py
│   ├── test_interaction_engine.py
│   ├── test_self_observer.py
│   ├── test_repair_executor.py
│   ├── test_runtime_contract.py
│   ├── test_build_contract.py
│   └── test_brain_health.py     ← From: amos_brain/health.py tests
│
└── entrypoints/
    ├── brain                    ← NEW (executable)
    └── doctor                   ← NEW (executable)
```

---

## Phase 1: Core Law Layer (Days 1-2)

### Source File Mappings

| New File | Primary Source | Secondary Sources | Lines Target |
|----------|---------------|-------------------|--------------|
| `core/law/types.py` | NEW | - | ~60 |
| `core/law/invariants.py` | `amos_brain/laws.py` (lines 1-150) | `amos_brain/action_gate.py` | ~50 |
| `core/law/constraints.py` | `amos_brain/action_gate.py` (Constraint classes) | `amos_brain/config_validator.py` | ~40 |
| `core/law/validators.py` | `amos_brain/config_validator.py` (validate_*) | `amos_brain/laws.py` | ~80 |
| `core/law/collapse.py` | NEW (collapse_risk formula) | - | ~30 |

### Migration Steps

1. **Extract invariants** from `amos_brain/laws.py`:
   - `L1_LEGAL` → `no_contradiction()`
   - `L2_LAWFUL` → `dual_interaction_present()`
   - `L3_EVOLUTION` → `feedback_exists()`

2. **Extract constraints** from `amos_brain/action_gate.py`:
   - `Constraint` dataclass → `StabilityConstraint`
   - Add `BiologicalConstraint` from health metrics

3. **Create validators** combining:
   - `amos_brain/config_validator.py` validation logic
   - `amos_brain/laws.py` law enforcement

### Deletions After Migration

```bash
# Remove after code migrated
rm amos_brain/laws.py           # Superseded by core/law/
rm amos_brain/action_gate.py    # Superseded by core/law/constraints.py
```

---

## Phase 2: State Tensor Layer (Days 2-3)

### Source File Mappings

| New File | Primary Source | Secondary Sources | Lines Target |
|----------|---------------|-------------------|--------------|
| `core/state/types.py` | `amos_brain/memory.py` (TensorState) | `amos_brain/state_manager.py` | ~50 |
| `core/state/tensor.py` | `amos_brain/memory.py` | - | ~40 |
| `core/state/normalize.py` | `amos_brain/state_manager.py` (normalize methods) | - | ~60 |
| `core/state/projection.py` | `amos_brain/reasoning.py` (projection logic) | - | ~50 |
| `core/state/integrity.py` | `amos_brain/health.py` (health scoring) | - | ~40 |
| `core/state/load.py` | `amos_brain/task_processor.py` (load metrics) | - | ~30 |

### Migration Steps

1. **Extract TensorState** from `amos_brain/memory.py`:
   - Preserve biological/cognitive/system/environment quadrants
   - Remove all persistence logic (SQLAlchemy, etc.)
   - Keep only in-memory tensor representation

2. **Extract normalization** from `amos_brain/state_manager.py`:
   - Keep state validation logic
   - Remove session management
   - Remove persistence

3. **Extract integrity scoring** from `amos_brain/health.py`:
   - Keep `HealthScore` calculation
   - Map to `IntegrityTensor`

### Deletions After Migration

```bash
rm amos_brain/memory.py         # Remove SQLAlchemy, keep TensorState
rm amos_brain/state_manager.py  # Remove persistence, keep normalization
```

---

## Phase 3: Interaction Layer (Days 3-4)

### Source File Mappings

| New File | Primary Source | Secondary Sources | Lines Target |
|----------|---------------|-------------------|--------------|
| `core/interaction/types.py` | NEW | - | ~20 |
| `core/interaction/operator.py` | `amos_brain/cognitive_engine.py` | `amos_brain/interaction.py` | ~60 |
| `core/interaction/feedback.py` | `amos_brain/meta_cognitive_reflection.py` | - | ~50 |
| `core/interaction/coupling.py` | NEW | - | ~40 |
| `core/interaction/transforms.py` | `amos_brain/reasoning.py` (transforms) | - | ~50 |

### Migration Steps

1. **Extract interaction logic** from `amos_brain/cognitive_engine.py`:
   - Keep operator application
   - Remove LLM-specific code
   - Make generic `apply(internal, external)`

2. **Extract feedback** from `amos_brain/meta_cognitive_reflection.py`:
   - Keep reflection loop
   - Remove persistence
   - Extract as pure function

3. **Create coupling** (NEW):
   - Cross-domain pattern detection
   - From `amos_superbrain_equation_bridge.py` pattern matching

---

## Phase 4: Deterministic Core (Days 4-5)

### Source File Mappings

| New File | Primary Source | Secondary Sources | Lines Target |
|----------|---------------|-------------------|--------------|
| `core/deterministic/types.py` | NEW | - | ~30 |
| `core/deterministic/engine.py` | `amos_brain/thinking_engine.py` | - | ~80 |
| `core/deterministic/transition.py` | `amos_brain/task_processor.py` | - | ~60 |
| `core/deterministic/prediction.py` | `amos_brain/predictive_bridge.py` | - | ~50 |
| `core/deterministic/correction.py` | `amos_brain/repair_bridge.py` (correction) | - | ~40 |
| `core/deterministic/policy.py` | NEW | - | ~50 |

### Migration Steps

1. **Extract thinking engine** from `amos_brain/thinking_engine.py`:
   - Keep prediction/correction loop
   - Remove LLM dependencies
   - Make deterministic

2. **Extract transitions** from `amos_brain/task_processor.py`:
   - Keep state transition logic
   - Remove async task queue
   - Make synchronous

3. **Extract prediction** from `amos_brain/predictive_bridge.py`:
   - Keep prediction comparison
   - Remove ML model dependencies
   - Use deterministic formulas

---

## Phase 5: Observe Layer (Days 5-6)

### Source File Mappings

| New File | Primary Source | Secondary Sources | Lines Target |
|----------|---------------|-------------------|--------------|
| `core/observe/types.py` | NEW | - | ~30 |
| `core/observe/drift.py` | `amos_brain/monitor.py` | - | ~70 |
| `core/observe/mismatch.py` | `amos_brain/doctor.py` (diagnostics) | - | ~60 |
| `core/observe/diagnostics.py` | `amos_brain/pathology_bridge.py` | - | ~80 |
| `core/observe/reports.py` | NEW | - | ~50 |

### Migration Steps

1. **Extract monitoring** from `amos_brain/monitor.py`:
   - Keep anomaly detection
   - Remove alerting infrastructure
   - Make pure diagnostic functions

2. **Extract diagnostics** from `amos_brain/doctor.py`:
   - Keep health check logic
   - Remove repair orchestration
   - Separate observation from action

3. **Extract pathology** from `amos_brain/pathology_bridge.py`:
   - Keep error classification
   - Remove recovery logic
   - Pure observation only

---

## Phase 6: Repair Layer (Days 6-7)

### Source File Mappings

| New File | Primary Source | Secondary Sources | Lines Target |
|----------|---------------|-------------------|--------------|
| `core/repair/types.py` | NEW | - | ~40 |
| `core/repair/planner.py` | `amos_brain/repair_bridge.py` (planning) | - | ~80 |
| `core/repair/simulation.py` | `amos_brain/simulation_engine.py` | - | ~70 |
| `core/repair/executor.py` | `amos_brain/execution_bridge.py` | - | ~90 |
| `core/repair/codemods.py` | NEW | - | ~100 |
| `core/repair/verification.py` | `amos_brain/equation_bridge_integration.py` | - | ~60 |

### Migration Steps

1. **Extract repair planning** from `amos_brain/repair_bridge.py`:
   - Keep action sequencing
   - Remove execution
   - Pure planning only

2. **Extract simulation** from `amos_brain/simulation_engine.py`:
   - Keep "what-if" logic
   - Remove external dependencies
   - Deterministic simulation

3. **Extract execution** from `amos_brain/execution_bridge.py`:
   - Keep execution loop
   - Remove async complexity
   - Synchronous execution

---

## Phase 7: Runtime Integration (Week 2, Days 1-3)

### Source File Mappings

| New File | Primary Source | Lines Target |
|----------|---------------|--------------|
| `runtime/bootstrap.py` | `AMOS_ORGANISM_OS/00_ROOT/root_kernel.py` | ~100 |
| `runtime/doctor.py` | `amos_brain/doctor.py` (simplified) | ~80 |
| `runtime/cli.py` | `amos_brain/cli.py` (simplified) | ~60 |
| `runtime/config.py` | `amos_brain/config.py` (simplified) | ~50 |
| `runtime/main.py` | NEW | ~30 |

### Bootstrap Sequence

```python
# runtime/bootstrap.py
class Bootstrap:
    def __init__(self):
        self.law = UniversalLawKernel()          # Phase 1
        self.state = UniversalStateModel()       # Phase 2
        self.interaction = InteractionOperator() # Phase 3
        self.core = DeterministicCore()          # Phase 4
        self.observer = SelfObserver()           # Phase 5
        self.repair = RepairExecutor()           # Phase 6

    def execute_cycle(self, raw_input: dict) -> dict:
        # Mandatory execution path from kernel spec
        state = self.state.normalize(raw_input)           # L1
        interaction = self.interaction.apply(              # L2
            state.biological, state.environment
        )
        law_result = self.law.validate_invariants(         # L0
            contradictions=0,
            has_internal=bool(state.biological),
            has_external=bool(state.environment),
            has_feedback=interaction.feedback,
            stability=StabilityConstraint(0.1, 0.2),
            bio=BiologicalConstraint(
                state.biological.get("load", 0),
                state.biological.get("capacity", 100)
            ),
            quadrants=integrity(state).to_quadrant()
        )
        transition = self.core.transition(                   # L3
            state, interaction, law_result.passed
        )
        drift = self.observer.detect_drift({                 # L4
            "transition_valid": transition.changed,
            "law_passed": law_result.passed
        })
        repairs = self.repair.propose_repairs(drift)         # L5
        return {
            "state": transition.next_state,
            "law": law_result,
            "drift": drift,
            "repairs": repairs
        }
```

---

## Phase 8: Contracts & Testing (Week 2, Days 4-5)

### Contracts

```python
# contracts/runtime_contract.py
RUNTIME_CONTRACT = {
    "canonical_runtime": "amos-brain",
    "canonical_module": "amos_kernel.runtime.main",
    "public_entrypoints": ["amos-brain", "amos-brain doctor"],
    "forbidden_patterns": [
        "sys.path.insert",
        "repo_root_script_execution",
        "silent_required_ci_failures",
        "import *",
        "bare_except",
    ],
    "mandatory_dependencies": [
        "core.law",
        "core.state",
        "core.interaction",
        "core.deterministic",
        "core.observe",
        "core.repair",
    ],
    "dependency_order": [
        "law",      # L0
        "state",    # L1
        "interaction",  # L2
        "deterministic",  # L3
        "observe",  # L4
        "repair",   # L5
    ]
}
```

### Test Migration

| New Test | Tests From | Coverage |
|----------|-----------|----------|
| `test_law_kernel.py` | `amos_brain/test_laws.py` | 100% |
| `test_state_model.py` | `amos_brain/test_memory.py`, `test_state_manager.py` | 100% |
| `test_deterministic_core.py` | `amos_brain/test_thinking_engine.py` | 100% |
| `test_self_observer.py` | `amos_brain/test_monitor.py`, `test_doctor.py` | 100% |
| `test_repair_executor.py` | `amos_brain/test_repair_bridge.py` | 100% |
| `test_brain_health.py` | `amos_brain/health.py` | 100% |

---

## Phase 9: Legacy Deletion (Week 2, Days 5-7)

### Complete Deletions

```bash
# Delete entire directories
rm -rf AMOS_ORGANISM_OS/          # Superseded by kernel layers
rm -rf _AMOS_BRAIN/                # Superseded by kernel
rm -rf _00_AMOS_CANON/             # Superseded by contracts/
rm -rf backend/                    # Superseded by consulting repo
rm -rf dashboard/                  # Superseded by frontend repos
rm -rf repo_doctor/                # Migrated to adapters/repo.py
rm -rf repo_doctor_omega/          # Migrated to adapters/repo.py
rm -rf vscode-repo-doctor/         # Externalized

# Delete amos_brain modules (after migration)
cd amos_brain
rm -f a2a_orchestrator.py          # External protocol
rm -f a2a_protocol.py              # External protocol
rm -f agent_fabric_kernel.py       # Superseded by core/interaction
rm -f architecture_bridge.py       # Superseded by contracts
rm -f brain_event_*.py             # External event system
rm -f canon_*.py                   # Superseded by core/law
rm -f causal_bridge.py             # Superseded by core/deterministic
rm -f cognitive_engine.py          # Superseded by core/interaction
rm -f cognitive_stack.py           # Simplified in kernel
rm -f dashboard.py                 # Externalized
rm -f digital_twin_bridge.py       # Externalized
rm -f distributed_physics_bridge.py # Externalized
rm -f entanglement_bridge.py       # Externalized
rm -f epistemic_kernel.py          # Superseded by core/law
rm -f equation_bridge_integration.py # Superseded by core/repair
rm -f execution_bridge.py            # Superseded by core/repair
rm -f explanatory_bridge.py         # Superseded by core/observe
rm -f facade.py                    # Superseded by runtime/bootstrap
rm -f fleet_bridge.py              # Externalized
rm -f governance_bridge.py         # Externalized
rm -f integration.py               # Superseded by runtime
rm -f knowledge_loader.py          # Superseded by core/state
rm -f launcher.py                  # Superseded by runtime/main
rm -f llm_providers.py             # Externalized to consulting
rm -f master_orchestrator.py       # Superseded by runtime/bootstrap
rm -f mathematical_framework_engine.py # Migrated to core/interaction
rm -f mcp_tools_bridge.py          # External protocol
rm -f memory_architecture.py       # Simplified to core/state
rm -f memory_governance.py         # Superseded by core/state
rm -f meta_*_bridge.py             # Superseded by core/observe
rm -f model_*.py                   # Externalized to consulting
rm -f multi_agent_orchestrator.py  # Externalized
rm -f operational_architecture_bridge.py # Superseded by runtime
rm -f organism_bridge.py           # Superseded by core/state
rm -f pathology_bridge.py          # Superseded by core/observe
rm -f performance_engine.py        # Superseded by core/state/load.py
rm -f predictive_bridge.py         # Superseded by core/deterministic
rm -f real_learning_engine.py      # Simplified in kernel
rm -f reasoning.py                 # Superseded by core/deterministic
rm -f reasoning_engine.py          # Superseded by core/deterministic
rm -f recovery_resilience_bridge.py # Superseded by core/repair
rm -f repo_autopsy_engine.py       # Migrated to adapters/repo.py
rm -f server_stub.py                # Externalized
rm -f simulation_engine.py         # Superseded by core/repair
rm -f skill.py                     # Simplified in kernel
rm -f source_registry.py           # Simplified in kernel
rm -f super_brain.py               # Superseded by runtime/bootstrap
rm -f superbrain_equation_bridge.py # Migrated to core/interaction/coupling.py
rm -f task_queue.py                # Removed (synchronous kernel)
rm -f temporal_*_bridge.py         # Externalized
rm -f thinking_engine.py           # Superseded by core/deterministic
rm -f tracing.py                   # Externalized
rm -f tutorial.py                  # Externalized
rm -f unified_orchestrator_bridge.py # Superseded by runtime
rm -f vector_memory.py             # Simplified to core/state

# Keep only (after migration):
# - __init__.py (simplified)
# - __main__.py (entry point)
# - cli.py (simplified)
# - config.py (simplified)
# - doctor.py (simplified)
# - health.py (simplified)
# - laws.py (until migrated)
# - memory.py (until migrated)
# - monitor.py (until migrated)
# - repair_bridge.py (until migrated)
# - state_manager.py (until migrated)
# - task_processor.py (until migrated)
# - api_contracts/ (for universe integration)
```

---

## Phase 10: Verification (Week 2, Day 7)

### Final Verification Checklist

```bash
# 1. Kernel boots
python -m amos_kernel.runtime.main

# 2. Doctor runs
amos-brain doctor

# 3. All tests pass
pytest amos_kernel/tests/ -v

# 4. Contracts verified
python -c "from amos_kernel.contracts.runtime_contract import RUNTIME_CONTRACT; print('OK')"

# 5. No forbidden imports
python -c "
import amos_kernel.core.law
import amos_kernel.core.state
import amos_kernel.core.interaction
import amos_kernel.core.deterministic
import amos_kernel.core.observe
import amos_kernel.core.repair
print('All core layers importable')
"

# 6. Dependency order respected
python -c "
from amos_kernel.core import law, state, interaction, deterministic, observe, repair
print('Dependency order validated')
"
```

---

## Migration Timeline

| Week | Phase | Deliverable | Risk |
|------|-------|-------------|------|
| 1 | 0-6 | Kernel core (6 layers) | Low |
| 2 | 7-10 | Runtime + contracts + tests | Low |
| 3 | 11 | Legacy deletion + verification | Medium |
| 4 | 12 | Integration testing | Low |

---

## Success Criteria

1. **Functional Parity**: All existing `amos_brain` tests pass with kernel
2. **Size Reduction**: 90% fewer files (731 → ~45)
3. **Boot Time**: <100ms from import to ready
4. **Test Coverage**: >95% for kernel/core/
5. **Contract Compliance**: 100% pass rate on `amos-brain doctor`
6. **No Regressions**: All 6 repos continue working

---

## Rollback Plan

If migration fails:

1. Keep `amos_brain/` intact until Phase 10
2. Use git tags: `pre-kernel-migration`
3. Parallel import paths during transition
4. Feature flags: `USE_KERNEL_FIRST = False`

---

## Next Steps

1. Approve migration plan
2. Create `amos_kernel/` directory
3. Begin Phase 0: Kernel Foundation
4. Weekly progress reviews
