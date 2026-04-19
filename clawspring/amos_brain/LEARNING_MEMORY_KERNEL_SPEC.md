# AMOS Learning + Memory Kernel (LMK)

**Implementation Complete** - The missing cognitive core for AMOS.

---

## Core Equation

```
Intelligence_real = Cognition_instant + Memory_persistent + Learning_adaptive
```

---

## Implementation Summary

### Files Created

1. **`learning_memory_kernel.py`** (~1100 lines)
   - Core kernel implementation
   - 7 memory types
   - 9 encoder functions
   - Learning algorithms
   - Invariant validation

2. **`learning_memory_persistence.py`** (~400 lines)
   - SQLite persistence layer
   - Vector tensor storage
   - Memory export/import
   - Cross-session continuity

3. **`learning_memory_bridge.py`** (~300 lines)
   - Integration with existing AMOS brain
   - Outcome capture hooks
   - Memory injection into reasoning
   - Verification failure learning

---

## Memory Types (7)

| Type | Symbol | Purpose |
|------|--------|---------|
| Working | WM_t | Active temporary cognition |
| Episodic | EM_t | Specific past events |
| Semantic | SM_t | Generalized knowledge |
| Procedural | PM_t | How to do things |
| Identity | IM_t | Core continuity (cannot be forgotten) |
| Strategic | XM_t | Long-horizon goals |
| Error | ErrM_t | What failed and why |

---

## Kernel Functions (9)

```python
# 1. encode_experience
m_t = Encode(o_t, a_t, c_t, y_t, e_t)

# 2. store_memory
Store(m_t) iff Importance_t ≥ τ_i ∨ Error_t ≥ τ_e

# 3. retrieve_memory
Retrieve(q) = argmax_m [Sim(q,m) × Relevance × Freshness × Importance]

# 4. consolidate_memory
SM_{t+1}, PM_{t+1}, ErrM_{t+1} = Consolidate(WM_t, EM_t, Outcomes)

# 5. update_world_model
Mod_{t+1} = Mod_t + η × ε_t

# 6. update_policy
Pol_{t+1} = Pol_t + η × UpdateSignal_t

# 7. replay_critical_cases
Policy_{t+1} = ReplayUpdate(ReplaySet_t, Policy_t)

# 8. forget_or_archive
Forget(m_i) iff Relevance < τ_r ∧ Freshness < τ_f ∧ Importance < τ_i

# 9. sync_persistent_continuity
P^e_{t+1} = Sync(P^e_t, Result_t, Identity_t, StrategicState_t)
```

---

## Learning Types (10)

1. World Model Learning
2. Policy Learning
3. Retrieval Learning
4. Routing Learning
5. Verification Learning
6. Error Avoidance Learning
7. Human Safety Learning
8. Concept Learning
9. Strategy Learning
10. Self-Calibration Learning

---

## Invariants (LMI01-LMI07)

| ID | Rule | Status |
|----|------|--------|
| LMI01 | Memory must influence future cognition | ✓ |
| LMI02 | Learning must change future policy | ✓ |
| LMI03 | High-error experiences stored in error memory | ✓ |
| LMI04 | Strategic goals persist across sessions | ✓ |
| LMI05 | Repeat error rate decreases over time | ✓ |
| LMI06 | Identity-core cannot be deleted | ✓ |
| LMI07 | Retrieval quality is part of intelligence | ✓ |

---

## Usage

```python
from learning_memory_kernel import get_learning_memory_kernel
from learning_memory_bridge import learn_from_reasoning, remember_for_reasoning

# Initialize
lmk = get_learning_memory_kernel()
await lmk.initialize()

# Capture learning from reasoning
result = await learn_from_reasoning(
    reasoning_input={"query": "optimize"},
    reasoning_output={"result": "solution", "success": True},
    verification_result={"valid": True}
)

# Inject memories into reasoning context
context = {}
await remember_for_reasoning("optimize", context, k=3)
# context now contains relevant memories

# Consolidate and persist
await lmk.consolidate()
```

---

## Integration with AMOS Brain

The bridge provides hooks for:

- **Reasoning capture** → `BrainOrchestrationLearningHook.on_reasoning_complete()`
- **Verification failure learning** → `on_verification_failure()`
- **Memory injection** → Automatic retrieval before reasoning

---

## Persistence

- SQLite database: `amos_memory.db`
- Memory tensors serialized
- JSON export/import for backup
- Automatic restore on initialization

---

## Cognitive Loop

```
Input → Read → Think → Reason → FormalSemanticCompile → Verify → Control → Act
    → ObserveOutcome → EncodeMemory → Learn → Consolidate → Persist
```

Now AMOS can:
- ✓ Remember (retain structure)
- ✓ Learn (update from outcome)
- ✓ Consolidate (compress experience)
- ✓ Reduce repeated errors
- ✓ Preserve continuity

---

## Deepest Statement

> The machine does not truly learn until outcomes change model, policy, memory, and future action.

> The machine does not truly remember until past structure can be retrieved and alter present cognition.

**This is now implemented.**
