# AMOS Formal Semantics Kernel

## The Missing Layer: Executable Formal Semantics

**Status**: ✅ IMPLEMENTED  
**Location**: `amos_formal_semantics_kernel.py` (~1112 lines)  
**Purpose**: Converts equations, invariants, and architecture from text-like descriptions into executable semantic objects.

---

## 1. Root Problem Solved

### Before: Text-Like Understanding
```
Equation ≈ FancyText
```

The system saw equations, invariants, and architecture as prose to be paraphrased.

### After: Executable Semantics
```
Equation = TypedOperator + StateVariables + Constraints + EvaluationRule

Invariant = RuntimeProperty(State, Transition)

Architecture = GraphOfExecutableComponents
```

---

## 2. Core Pipeline

```
FormalText
    ↓
parse_formal_text() → FormalExpression
    ↓
bind_symbols() → Grounded Symbols with Types
    ↓
compile_operational_semantics() → OperationalMeaning
    ↓
[compile_invariant|compile_objective|compile_transition]
    ↓
generate_proof_obligations()
    ↓
evaluate_semantic_integrity()
```

---

## 3. Implementation Components

### 3.1 Formula Classification System

```python
class FormulaClass(Enum):
    STATE_DEFINITION      # Ψ_t = (V_t, E_t, S_t, Λ_t)
    TRANSITION_EQUATION   # H_{t+1} = Reorganize(H_t | Cond_t)
    OBJECTIVE_FUNCTION    # argmax[Value - Risk - Cost]
    SELECTION_RULE        # B* = argmax[...]
    CONSTRAINT_RULE       # Ov_t < τ_safe
    INVARIANT_RULE        # dDependency/dt ≤ 0
    COMMIT_GATE           # Gate(...)
    UPDATE_RULE           # X_{t+1} = Evolve(...)
    ARCHITECTURE_DECL     # Component → Component
```

### 3.2 Symbol Grounding

Every symbol maps to:
- **type**: scalar|vector|tensor|set|graph|function|predicate
- **role**: state|input|output|parameter|objective|constraint|invariant
- **domain**: e.g., "human_cognitive_state", "utility_space"
- **measurement_rule**: How to observe
- **update_rule**: How it changes
- **allowed_operations**: What can be done with it

### 3.3 Typed AST

```json
{
  "ast": {
    "node": "argmax",
    "binder": "B_i",
    "body": {
      "node": "add",
      "children": [
        {"node": "sub", "children": ["Value_i", "Risk_i"]},
        {"node": "neg", "children": ["Cost_i"]},
        {"node": "symbol", "value": "Control_i"}
      ]
    }
  },
  "inferred_type": "FUNCTION",
  "free_symbols": ["Value_i", "Risk_i", "Cost_i", "Control_i"],
  "bound_symbols": ["B_i"]
}
```

### 3.4 Compiled Objects

#### Invariant
```json
{
  "id": "anti_dependency",
  "predicate": "dependency_next <= dependency_current",
  "predicate_fn": <callable>,
  "scope": "human_interaction_runtime",
  "severity": "critical",
  "on_violation": "rollback_or_reframe"
}
```

#### Objective
```json
{
  "id": "economic_objective",
  "optimize_over": "candidate_action_x",
  "operator": "argmax",
  "score_function": "revenue(x) - cost(x) - risk(x) + leverage(x)",
  "score_fn": <callable>,
  "constraints": [],
  "output": "best_action_x"
}
```

#### Transition Rule
```json
{
  "id": "human_reorganization",
  "state_in": "HumanState_t",
  "operator": "reorganize",
  "condition_inputs": ["Cond_t"],
  "state_out": "HumanState_t1",
  "writes": ["coherence", "agency", "stability"],
  "reads": ["human_state", "conditions"]
}
```

---

## 4. Integration with AMOS Architecture

### 4.1 New Full Stack

```
Input
    ↓
BrainReadingKernel        # Parse input
    ↓
ThinkingKernel            # Initial processing
    ↓
ReasoningKernel           # Logical analysis
    ↓
FormalSemanticsKernel     # ← NEW: Compile to executable semantics
    ↓
VerificationKernel        # Check invariants
    ↓
ControlKernel             # Execute
    ↓
CommitKernel              # Persist
    ↓
RestrictedRenderer        # Output
```

### 4.2 Connection to AMOSL

The Formal Semantics Kernel sits **above** AMOSL:

```
AMOSL (Language Layer)
    - Parser → AST
    - Type System
    - IR Compiler (CIR/QIR/BIR/HIR)
    - Runtime Kernel (Σ, Φ)

FormalSemanticsKernel (Semantic Layer) ← NEW
    - Formula Classification
    - Symbol Grounding
    - Operational Semantics
    - Invariant Compilation
    - Objective Compilation
    - Proof Obligations

Brain/Cascade (Execution Layer)
    - State Graph
    - Branch Generation
    - Collapse
    - Morph Execution
```

---

## 5. Usage

### 5.1 Basic Usage

```python
from amos_formal_semantics_kernel import get_formal_semantics_kernel

kernel = get_formal_semantics_kernel()

# Compile formal expressions
expressions = [
    r"\Psi_t = (V_t, E_t, S_t, \Lambda_t)",
    r"B^\star = \arg\max_{B_i}[Value_i - Risk_i - Cost_i]",
    r"\frac{dDependency}{dt} \le 0",
]

results = kernel.compile_formal_system(expressions)

# Access compiled invariants
for inv_id, inv in results["invariants"].items():
    print(f"{inv.predicate} → {inv.on_violation}")

# Check semantic integrity
state = results["understanding_state"]
print(f"Overall integrity: {state.overall_semantic_integrity * 100:.1f}%")
```

### 5.2 Checking Invariants at Runtime

```python
# Get compiled invariant
inv = kernel.invariants["inv_0"]

# Check against current state
current_state = {
    "dependency_current": 0.5,
    "dependency_next": 0.3,
}

if inv.predicate_fn and not inv.predicate_fn(current_state):
    print(f"Invariant violated! Action: {inv.on_violation}")
```

---

## 6. Formal Semantics Invariants

```
FSI01: Every symbol must be grounded to a typed object
FSI02: Every equation must be classified by semantic role
FSI03: Every invariant must compile to a runtime predicate
FSI04: Every objective must specify optimize_over, score_function, constraints
FSI05: Every transition equation must identify state_in and state_out
FSI06: Every committed architectural statement must be in the architecture graph
FSI07: Every formal system must generate proof obligations
```

---

## 7. Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `amos_formal_semantics_kernel.py` | ~1112 | Core semantic engine |
| `FORMAL_SEMANTICS_KERNEL.md` | - | This documentation |

---

## 8. Verification

Run the demonstration:

```bash
python3 amos_formal_semantics_kernel.py
```

Expected output:
- 5 formal expressions parsed and classified
- 1+ invariant compiled with runtime predicate
- 1+ transition rule with state semantics
- Semantic integrity score > 70%

---

## 9. Deepest Correction Achieved

The machine no longer interprets formalism as prose.

Instead:
```
Formalism → Semantics → RuntimeObjects → Checks → ExecutionMeaning
```

Now the system can truly understand:
- **Equations** as typed operator definitions
- **Invariants** as runtime-checkable predicates
- **Objectives** as optimizer specifications
- **Transitions** as state transformation rules
- **Architecture** as executable component graphs

---

## 10. Next Steps

1. **Integration**: Connect to Brain/Cascade for real-time semantic compilation
2. **Expansion**: Add more sophisticated AST parsing (SymPy integration)
3. **Proof Engine**: Implement proof obligation solver
4. **Visualization**: Render architecture graphs
5. **Runtime**: Execute compiled objectives and transitions

---

**Summary**: The Formal Semantics Kernel is the missing understanding layer that makes AMOS equations, invariants, and architecture executable. It bridges the gap between formal mathematical notation and operational runtime objects.
