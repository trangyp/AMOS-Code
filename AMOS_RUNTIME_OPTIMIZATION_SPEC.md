# AMOS Runtime Optimization Specification
## From FullLoop to FastLoop Architecture

**Version**: 1.0  
**Date**: 2026-04-18  
**Status**: Architecture Specification

---

## 1. The Problem Statement

Current AMOS runtime follows:

$$
\text{FullLoop(Input)} = \text{Observe} \rightarrow \text{Model} \rightarrow \text{Simulate} \rightarrow \text{Verify} \rightarrow \text{Render}
$$

**Result**: Latency proportional to full recomputation.

Target AMOS runtime must follow:

$$
\text{FastLoop(Input)} = \text{InterruptClassify} \rightarrow \text{Route} \rightarrow \text{FastCommit} \rightarrow \text{EscalateIfNeeded}
$$

**Result**: Latency proportional to active set only.

---

## 2. Speed Equation

Real speed is determined by:

$$
\text{Speed}_{\text{real}} = f(
\underbrace{\text{Routing}}_{\text{O(1) classification}},
\underbrace{\text{StateSize}_{\text{active}}}_{\text{sparse}},
\underbrace{\text{MemoryAccess}_{\text{cached}}}_{\text{hot path}},
\underbrace{\text{VerificationCost}_{\text{selective}}}_{\text{bounded depth}},
\underbrace{\text{SearchWidth}_{\text{bounded}}}_{\text{B ≤ 3}},
\underbrace{\text{SearchDepth}_{\text{bounded}}}_{\text{H ≤ 2}},
\underbrace{\text{Serialization}_{\text{compact}}}_{\text{JSON/objects}},
\underbrace{\text{ToolLatency}_{\text{async}}}_{\text{fire-and-forget}},
\underbrace{\text{RepairLoops}_{\text{local}}}_{\text{not global}},
\underbrace{\text{RendererOverhead}_{\text{minimal}}}_{\text{structured output}}
)
$$

---

## 3. The FastLoop Architecture

### 3.1 Interrupt Classification Layer

**Purpose**: O(1) classification of input intent—no full parsing.

```python
class InterruptClassifier:
    """
    Fast path classification without full semantic parsing.
    Uses pattern matching + embedding cache for sub-millisecond classification.
    """
    
    CLASSES = {
        "QUERY": "information_retrieval",      # Simple lookup
        "ACTION": "state_mutation",            # Direct execution
        "REASONING": "cognition_required",     # Full loop needed
        "ESCALATION": "human_handoff",         # Immediate redirect
        "ECHO": "identity_function",           # Passthrough
    }
    
    async def classify(self, input_hash: str, raw_input: str) -> InterruptClass:
        """
        Target: < 1ms latency
        
        Strategy:
        1. Check hash cache (exact match)
        2. Check embedding similarity (approximate match)
        3. Fast regex pattern matching
        4. Return classification + confidence
        """
        pass
```

**Key Constraint**: Classification must happen in < 1ms. No LLM calls here.

### 3.2 Sparse Routing Matrix

**Purpose**: Route to minimal active module set.

```python
class SparseRouter:
    """
    Activates only required modules based on classification.
    
    From: RuntimeCost ∝ Σᵢ ModuleCostᵢ (all modules)
    To:   RuntimeCost ∝ Σᵢ∈ActiveSet ModuleCostᵢ (active only)
    """
    
    ROUTING_TABLE = {
        "QUERY": ["memory", "retrieval"],
        "ACTION": ["state", "executor"],
        "REASONING": ["brain", "simulator", "verifier"],  # Full set
        "ESCALATION": ["interface"],
        "ECHO": ["passthrough"],
    }
    
    async def route(self, classification: InterruptClass) -> ActiveModuleSet:
        """
        Returns only the modules needed for this request class.
        Typical active set size: 1-3 modules (not 15+)
        """
        pass
```

### 3.3 Delta State Updates

**Purpose**: State_{t+1} = State_t + Δ_t (not full rebuild).

```python
class DeltaStateManager:
    """
    Maintains state as deltas, not full snapshots.
    
    From: FullStateRebuild every turn
    To:   ApplyDelta only
    """
    
    def apply_delta(self, state_id: str, delta: StateDelta) -> State:
        """
        Target: O(|Δ|) not O(|State|)
        
        Uses structural sharing (persistent data structures)
        to make delta application O(1) for most operations.
        """
        pass
    
    def get_state_view(self, state_id: str, projection: Projection) -> View:
        """
        Returns projected view without materializing full state.
        """
        pass
```

### 3.4 Bounded Search Executor

**Purpose**: Enforce strict limits on branch generation.

```python
class BoundedSearchExecutor:
    """
    Constrained branch simulation with hard limits.
    
    From: Cost ~ O(B · H · V) unbounded
    To:   Cost ~ O(B_max · H_max · V_active)
    """
    
    DEFAULT_LIMITS = {
        "QUERY": {"B": 1, "H": 1},        # No search
        "ACTION": {"B": 2, "H": 1},      # Minimal
        "REASONING": {"B": 3, "H": 2},   # Still bounded
    }
    
    async def execute_bounded(
        self, 
        intent: str,
        limits: SearchLimits
    ) -> BranchResult:
        """
        Hard cutoffs:
        - Max branches: 3
        - Max horizon: 2 steps
        - Max verification depth: 1 level
        
        Escalation trigger: If limits exceeded → full reasoning
        """
        pass
```

### 3.5 Selective Verification

**Purpose**: Verify only what's necessary, not everything.

```python
class SelectiveVerifier:
    """
    Tiered verification based on risk classification.
    
    From: Latency = Cognition + Verification + Repair (always full)
    To:   Latency = Cognition + Verification_selective + Repair_local
    """
    
    VERIFICATION_TIERS = {
        "none": 0,           # Echo, simple queries
        "syntax": 1,         # Basic validation
        "local": 2,          # Affected subsystem only
        "full": 3,           # Global constraint check
    }
    
    async def verify(
        self, 
        action: Action,
        tier: VerificationTier
    ) -> VerificationResult:
        """
        Fast path: syntax/local only (~5ms)
        Slow path: full verification (~200ms) - escalated only
        """
        pass
```

### 3.6 Compact Serialization

**Purpose**: Structure-first, minimal rendering.

```python
class CompactSerializer:
    """
    Default to typed objects, not natural language.
    
    From: Architecture_deep → LanguageBottleneck → SlowOutput
    To:   Architecture_deep → StructuredOutput → FastRender
    """
    
    SERIALIZATION_MODES = {
        "json": "application/json",           # Default
        "compact": "application/vnd.amos+compact",  # Binary-efficient
        "proto": "application/protobuf",        # Max speed
        "render": "text/markdown",              # Optional
    }
    
    def serialize(self, result: Any, mode: str = "json") -> bytes:
        """
        Default: JSON/typed objects (no LLM generation)
        Optional: Markdown only when explicitly requested
        """
        pass
```

### 3.7 Async Fire-and-Forget Tools

**Purpose**: Don't block on tool latency.

```python
class AsyncToolExecutor:
    """
    Non-blocking tool integration.
    
    Tool latency removed from critical path.
    """
    
    async def execute_async(
        self, 
        tool_call: ToolCall,
        blocking: bool = False
    ) -> Union[Result, TaskHandle]:
        """
        Default: Return handle immediately, execute in background
        Optional: Block only for critical path tools
        """
        pass
```

---

## 4. The FastLoop Execution Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    FASTLOOP PIPELINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. INTERRUPT CLASSIFY (< 1ms)                                  │
│     ├── Hash cache lookup                                       │
│     ├── Embedding similarity (approximate)                      │
│     └── Regex pattern match                                     │
│                           ↓                                     │
│  2. SPARSE ROUTE (< 1ms)                                        │
│     ├── Map class → ActiveModuleSet (1-3 modules)               │
│     └── Activate only hot modules                               │
│                           ↓                                     │
│  3. DELTA RETRIEVAL (< 5ms)                                     │
│     ├── Fetch State_{t} from hot cache                          │
│     └── Apply Δ_pending if exists                               │
│                           ↓                                     │
│  4. FAST COMMIT (< 10ms for QUERY/ACTION)                       │
│     ├── Bounded search (B ≤ 3, H ≤ 2)                           │
│     ├── Selective verification (syntax/local)                   │
│     └── Delta compute (State_{t+1} = State_t + Δ)               │
│                           ↓                                     │
│  5. COMPACT OUTPUT (< 1ms)                                      │
│     ├── Serialize to JSON/typed object                        │
│     └── Stream response                                         │
│                           ↓                                     │
│  6. BACKGROUND (async, non-blocking)                            │
│     ├── Persist state delta                                     │
│     ├── Update caches                                           │
│     └── Full verification (if flagged)                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ ESCALATION GATE                                         │    │
│  │ If confidence < threshold OR complexity > limits:       │    │
│  │ → Handoff to FullLoop (cognition_required)              │    │
│  │ → Return: "Thinking..." with async promise              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Target Performance Budgets

| Operation | Target Latency | Modules Active | Verification |
|-----------|---------------|----------------|--------------|
| **QUERY** | < 10ms | memory, retrieval | none |
| **ACTION** | < 50ms | state, executor | syntax |
| **REASONING** | < 200ms | brain, simulator | local |
| **FULL_LOOP** | < 2s | all | full |

---

## 6. Implementation Phases

### Phase 1: Interrupt + Router (Week 1)
- [ ] Build InterruptClassifier with hash cache
- [ ] Implement SparseRouter
- [ ] Define routing table for existing request types
- [ ] Measure: classification time < 1ms

### Phase 2: Delta State (Week 2)
- [ ] Implement DeltaStateManager
- [ ] Convert state storage to delta format
- [ ] Add structural sharing for O(1) updates
- [ ] Measure: state retrieval < 5ms

### Phase 3: Bounded Search (Week 3)
- [ ] Add search limits to BranchSimulator
- [ ] Implement escalation detection
- [ ] Build fast commit path
- [ ] Measure: query path < 10ms

### Phase 4: Selective Verification (Week 4)
- [ ] Implement verification tiers
- [ ] Add risk classification
- [ ] Integrate with fast path
- [ ] Measure: verification overhead < 5ms for fast path

### Phase 5: Serialization + Async (Week 5)
- [ ] Default to JSON output
- [ ] Add protobuf support
- [ ] Make tool calls async by default
- [ ] Measure: end-to-end QUERY < 10ms

---

## 7. Success Metrics

```
Before (FullLoop):
├── Median latency: 2-5 seconds
├── P99 latency: 10+ seconds  
├── Active modules per request: 15+
└── State recomputation: 100%

After (FastLoop):
├── Median latency: < 50ms for 80% of requests
├── P99 latency: < 2s (escalations only)
├── Active modules per request: 2-3 (avg)
└── State recomputation: < 10% (deltas only)
```

---

## 8. The Core Insight

```
CoreEquation ≠ RuntimePerformance

RuntimePerformance = ExecutionDiscipline
                   + SparseRouting
                   + DeltaUpdates  
                   + BoundedSearch
                   + LocalRepair
                   + MinimalRendering
```

The AMOS universal equation defines **what** the system can do.
The FastLoop runtime defines **how fast** it does it.

Both are required for production intelligence.

---

## 9. Files to Create

1. `amos_fastloop_classifier.py` - Interrupt classification
2. `amos_sparse_router.py` - Module routing
3. `amos_delta_state.py` - Delta state management
4. `amos_bounded_search.py` - Constrained search
5. `amos_selective_verifier.py` - Tiered verification
6. `amos_fastloop_runtime.py` - Integrated runtime

---

**Author**: AMOS Architecture Team  
**Status**: Specification Ready for Implementation
