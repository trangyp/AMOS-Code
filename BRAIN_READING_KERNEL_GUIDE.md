# AMOS Brain-Reading Kernel

## The Deepest Reading Architecture

> **Reading ≠ Decoding Text**
> 
> Real reading is: **Predict → Sample → Compare → Update → Bind → Compress → Stabilize**

---

## Overview

The Brain-Reading Kernel is a cognitive reading architecture that implements predictive, chunk-based, multi-pass reading with binding, salience computation, and coherence verification. This is not language parsing—it is brain-level reading.

### Key Innovation

Traditional systems read like: `Text → Meaning`

The Brain-Reading Kernel reads like:
```
BrainState → PredictiveModel → InputSampling → PredictionError → AttentionUpdate → MeaningAssembly → ReadState
```

---

## Core Equations

### 1. The Reading Loop

```
R_{t+1} = U(B(A(C(S(P(R_t))))))
```

Where:
- **P**: Predict likely meaning structure
- **S**: Sample actual input features
- **C**: Compute prediction error
- **A**: Reallocate attention
- **B**: Bind references and relations
- **U**: Update global read state

### 2. Predictive Processing

```
m̂_t = Predict(Input_{<t}, Memory_t, Goal_t, Context_t)
s_t = Sample(Input_t)
ε_t = s_t - m̂_t
Attention_{t+1} = Reweight(Attention_t, ε_t, Goal_t, Risk_t)
Meaning_{t+1} = Meaning_t + η·ε_t
```

### 3. Multi-Pass Reading

```
Read* = Pass_5(Pass_4(Pass_3(Pass_2(Pass_1(U_t)))))
```

| Pass | Goal |
|------|------|
| Pass 1 | Segment and anchor |
| Pass 2 | Detect what matters and what is dangerous |
| Pass 3 | Resolve entities, scope, and omitted structure |
| Pass 4 | Infer actual request and preserved constraints |
| Pass 5 | Check whether the full reading is stable |

### 4. Salience Computation

```
Salience_i = α·GoalRelevance_i + β·ConstraintWeight_i + γ·ErrorWeight_i + δ·RiskWeight_i + ε·Novelty_i + ζ·Recurrence_i
```

### 5. Global Coherence

```
ReadCoherence = α·ConstraintCoverage + β·BindingCompleteness + γ·HypothesisConsistency + δ·SalienceCoverage - ε·Conflict - ζ·Ambiguity

StableRead = 𝟙[ReadCoherence ≥ τ_read]
```

---

## Architecture

### Data Structures

#### BrainReadState
The complete cognitive state during reading:
```json
{
  "global_state": {
    "mode": "scan|read|resolve|reflect|stabilize|execute",
    "arousal": 0.0,
    "cognitive_load": 0.0,
    "uncertainty": 0.0,
    "prediction_stability": 0.0
  },
  "priors": {
    "topic_priors": [],
    "intent_priors": [],
    "reference_priors": [],
    "structure_priors": [],
    "risk_priors": []
  },
  "attention": {
    "focus_units": [],
    "suppressed_units": [],
    "salience_map": []
  },
  "working_memory": [],
  "binding_workspace": {
    "entities": [],
    "relations": [],
    "open_bindings": []
  },
  "error_state": {
    "prediction_errors": [],
    "conflicts": [],
    "ambiguities": []
  }
}
```

#### MemoryChunk
Cognitive chunks (not tokens):
```json
{
  "id": "chunk_hash",
  "content": "text content",
  "chunk_type": "claim|question|constraint|goal|reference_group|emotional_burst|instruction|narrative_frame|meta_comment",
  "coherence": 0.0,
  "salience": 0.0,
  "binding_requirements": [],
  "risk_weight": 0.0
}
```

#### StableRead
The final output:
```json
{
  "utterance_id": "unique_id",
  "primary_intent": ["REQUEST", 0.85],
  "goal_structure": [],
  "constraint_structure": [],
  "reference_structure": [],
  "coherence_score": 0.92,
  "stable": true,
  "compiled_goal": {
    "goal_type": "design|plan|respond|simulate|clarify|defer|block",
    "objective": "...",
    "constraints": []
  }
}
```

---

## Components

### 1. ChunkingEngine
Segments input into cognitive chunks using boundary markers:
- Sentence boundaries (`.`, `!`, `?`)
- Contrast markers (`however`, `but`, `although`)
- Causal markers (`because`, `therefore`, `thus`)
- Structural markers (`first`, `second`, `finally`)
- Formatting markers (`**`, `__`, `` ` ``)

### 2. PredictiveModel
Implements predictive processing:
- `predict(chunks, priors, goals, memory)`: Generate predictions
- `sample(text, chunk)`: Sample input features
- `compute_error(prediction, sample, chunk)`: Calculate ε_t

### 3. BindingEngine
Resolves references ("it", "that", "the problem"):
- Extracts entities by patterns
- Builds entity relations
- Identifies open binding slots
- **Law**: `StableRead = 0 if OpenCriticalBindings > 0`

### 4. SalienceEngine
Computes multi-factor salience:
- Goal relevance
- Constraint weight
- Error weight
- Risk weight
- Novelty
- Recurrence

### 5. ConflictDetector
Detects conflicts that block stable reading:
- Goal conflicts
- Constraint conflicts
- Scope conflicts
- Instruction conflicts

### 6. CoherenceVerifier
Verifies global coherence:
- Constraint coverage
- Binding completeness
- Hypothesis consistency
- Salience coverage
- Conflict penalty
- Ambiguity penalty

### 7. DepthController
Controls reading depth:
- `SKIM`: Fast scan
- `NORMAL`: Standard comprehension
- `DEEP`: Deep analysis
- `FORENSIC`: Detailed investigation

### 8. MultiPassReader
Orchestrates 5-pass reading:
1. Surface structure (segment and anchor)
2. Signal and risk detection
3. Binding and reference resolution
4. Intent and constraint inference
5. Global coherence verification

---

## Invariants

### BRI01: No Raw Text Consumption
No module may consume raw natural language directly. All input must pass through the Brain-Reading Kernel.

### BRI02: Chunk-Based Reading
All reading must be chunk-based, not token-only. The chunk tensor C_t ∈ R^{N_c × F_c} is the primary representation.

### BRI03: Binding Before Stable Read
All high-salience units must be reference-bound before stable read.

### BRI04: Predictive Reading
Reading must be predictive, not purely reactive. The system must generate predictions before sampling input.

### BRI05: Multiple Hypotheses
Multiple interpretation hypotheses must be maintained until resolution.

### BRI06: Conflict Blocking
Global conflict above threshold blocks stable read: `HighConflict ⇒ NoStableRead`

### BRI07: Coherence Verification
Stable read requires global coherence verification: `StableRead = 𝟙[ReadCoherence ≥ τ_read]`

---

## Usage

### Basic Usage

```python
import asyncio
from amos_brain_reading_kernel import get_brain_reading_kernel

async def main():
    kernel = get_brain_reading_kernel()
    
    # Read text
    result = await kernel.read(
        text="The system is too shallow. Implement a Brain-Reading Kernel.",
        active_goals=["improve architecture"]
    )
    
    print(f"Intent: {result.primary_intent[0].name}")
    print(f"Stable: {result.stable}")
    print(f"Coherence: {result.coherence_score}")
    print(f"Goal: {result.compiled_goal.goal_type}")

asyncio.run(main())
```

### With Diagnostics

```python
result = await kernel.read_with_diagnostics(
    text="Your text here",
    active_goals=["goal1", "goal2"]
)

print(result["diagnostics"])
print(result["chunks"])
```

### Integration with AMOS

```python
from amos_brain_reading_integration import BrainReadingIntegrator

integrator = BrainReadingIntegrator()

# Process through full pipeline
result = await integrator.process_input(
    text="Your text here",
    amos_context={"health_score": 0.95},
    active_goals=["improve system"]
)

# Check routing decision
print(f"Routed to: {result.routing_decision}")
print(f"Priority: {result.priority_score}")
print(f"Execution plan: {result.execution_plan}")
```

### FastAPI Endpoint

```python
from fastapi import FastAPI
from amos_brain_reading_integration import create_brain_reading_router

app = FastAPI()
app.include_router(create_brain_reading_router())

# Endpoints:
# POST /brain-reading/read
# GET /brain-reading/stats
```

---

## API Reference

### BrainReadingKernel

#### `read(text, **context) -> StableRead`
Execute brain-level reading on input text.

**Parameters:**
- `text`: Raw input text
- `dialogue_context`: Previous conversation context
- `memory_context`: System memory
- `world_context`: World knowledge
- `active_goals`: Current goals

**Returns:** `StableRead` object

#### `read_with_diagnostics(text, **context) -> dict`
Read with full diagnostic output including chunks, errors, and conflicts.

#### `validate_invariants(stable_read) -> list`
Validate brain reading invariants and return violations.

### BrainReadingIntegrator

#### `process_input(text, amos_context, **kwargs) -> IntegratedBrainRead`
Process input through brain-reading and integrate with AMOS ecosystem.

**Returns:** `IntegratedBrainRead` with routing decision and execution plan.

#### `get_reading_stats() -> dict`
Get statistics on reading history.

---

## Files

| File | Description |
|------|-------------|
| `amos_brain_reading_kernel.py` | Core brain-reading implementation (~1300 lines) |
| `amos_brain_reading_integration.py` | AMOS ecosystem integration layer |
| `BRAIN_READING_KERNEL_GUIDE.md` | This documentation |

---

## Architecture Integration

### Input Flow
```
Raw Text → BrainReadingKernel → StableRead
                ↓
         ChunkingEngine
         PredictiveModel
         BindingEngine
         SalienceEngine
         ConflictDetector
         CoherenceVerifier
                ↓
         BrainReadingIntegrator
                ↓
    ┌──────────┼──────────┐
    ↓          ↓          ↓
  Brain      Agent    Self-Heal
(Design)   (Tasks)   (Fixes)
```

### Routing Logic

| Intent | Goal Type | Route |
|--------|-----------|-------|
| DESIGN | - | brain |
| SPECIFICATION | - | brain |
| REQUEST | design/plan | brain |
| REQUEST | respond/execute | agent |
| CORRECTION | - | self_heal (if high priority) |
| DISTRESS | - | self_heal |
| QUESTION | - | clarification |
| Unstable/Coherence < 0.5 | - | clarification |

---

## Testing

Run the example:

```bash
cd /Users/nguyenxuanlinh/Documents/Trang\ Phan/Downloads/AMOS-code
python amos_brain_reading_kernel.py
python amos_brain_reading_integration.py
```

---

## Future Enhancements

1. **Neural Predictive Model**: Replace rule-based predictions with transformer-based prediction
2. **World Model Integration**: Connect to external knowledge graphs for better entity resolution
3. **Multi-Modal Reading**: Extend to images, code, structured data
4. **Learning**: Learn user-specific priors from interaction history
5. **Distributed Reading**: Parallel pass execution for large texts

---

## Summary

The Brain-Reading Kernel transforms AMOS from a text-processing system into a **cognitive reading system** that:

- **Predicts** before interpreting
- **Chunks** instead of token-drifting
- **Binds** references explicitly
- **Computes salience** multi-factorially
- **Detects conflicts** before commitment
- **Verifies coherence** globally
- **Routes** to appropriate subsystems

This is the deepest reading architecture in the AMOS ecosystem.
