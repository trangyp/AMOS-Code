# AMOS Thinking Kernel Specification

## Version 1.0 - Formal Machine-Readable Model

---

## 1. Core Thesis

```
Thinking ≠ TextGeneration
Thinking ≠ Parsing
Thinking ≠ Retrieval
Thinking ≠ SearchOnly
```

**Real Definition:**
```
Thinking = controlled internal state transformation under goals, constraints, uncertainty, and error correction
```

Or shorter:
```
Thinking = state transition over latent structure
```

---

## 2. Core Law

```
Thinking: S_t → S_{t+1}
```

Where S_t is **internal structured state**, not text.

### State Composition

```
S_t = (W_t, M_t, H_t, G_t, C_t, U_t, E_t, Π_t)
```

| Component | Symbol | Description |
|-----------|--------|-------------|
| Active Workspace | W_t | Currently held information units |
| Memory Activation | M_t | Retrieved relevant memories |
| Hypotheses | H_t | Active candidate explanations/solutions |
| Goals | G_t | Objective functions and targets |
| Constraints | C_t | Hard and soft boundaries |
| Uncertainty | U_t | Confidence and entropy measures |
| Error State | E_t | Detected inconsistencies |
| Policy | Π_t | Current control mode |

### Thinking Operator

```
S_{t+1} = T(S_t, Input_t)
```

Where T is the **thinking operator**.

---

## 3. Thinking Loop (The 6-Stage Pipeline)

```
Think(S_t, x_t) = Control(
    Revise(
        Evaluate(
            Transform(
                Compare(
                    Represent(S_t, x_t)
                )
            )
        )
    )
)
```

### Stage Details

| Stage | Function | Purpose |
|-------|----------|---------|
| 1. Represent | `Represent(S_t, x_t)` | Encode input into internal structure |
| 2. Compare | `Compare(H_t)` | Evaluate hypotheses against each other |
| 3. Transform | `Transform(R_t)` | Rewrite into more useful form |
| 4. Evaluate | `Evaluate(S_t)` | Score against goals and constraints |
| 5. Revise | `Revise(S_t, E_t)` | Fix defects and errors |
| 6. Control | `Control(S_t)` | Select next operation or commit |

---

## 4. Thinking Objective

**Reduce internal problem distance:**

```
Δ_t = Distance(S_t, S_t*)
```

Where S_t* is a better internal state.

**Good thinking satisfies:**

```
Δ_{t+1} < Δ_t
```

**Optimal thinking:**

```
T* = argmin_T Distance(T(S_t), S_t*)
```

---

## 5. State Quality Function

```
Q(S_t) = α·Coherence_t + β·GoalAlignment_t + γ·ConstraintSatisfaction_t + δ·PredictivePower_t - ε·Error_t - ζ·Waste_t
```

**Thinking quality constraint:**

```
Q(S_{t+1}) > Q(S_t)
```

If not satisfied, the system is "just moving" - not thinking.

---

## 6. Thinking Operators (Ω)

```
Ω = {ω_1, ω_2, ..., ω_n}
```

Each operator: `ω_i : S_t → S_{t+1}`

### Core Operators

| Operator | Definition | Purpose |
|----------|------------|---------|
| **hold** | `ω_hold(S_t) = S_t` | Preserve state without collapse |
| **focus** | `ω_focus(S_t) = Reweight(S_t, FocusMask)` | Increase weight on selected components |
| **compare** | `ω_compare(H_t) = PairwiseEval(H_t)` | Create contrast between hypotheses |
| **transform** | `ω_transform(R_t) = R'_t` | Rewrite representation |
| **simulate** | `ω_simulate(S_t) = Ŝ_{t+h}` | Project consequences |
| **evaluate** | `ω_eval(S_t) = Score_t` | Score against goals |
| **repair** | `ω_repair(S_t) = S'_t` | Fix state defects |
| **commit** | `ω_commit(S_t) = S_{t+1}` | Make transition official |

---

## 7. Thinking Modes

The machine must choose **how** to think:

```json
{
  "thinking_modes": [
    "hold",
    "clarify", 
    "decompose",
    "compare",
    "simulate",
    "verify",
    "repair",
    "commit",
    "defer"
  ]
}
```

### Mode Selection

```
Mode* = argmax_m [ ExpectedImprovement(m) · Cost(m) · Risk(m) ]
```

---

## 8. Machine-Readable State Schema

```json
{
  "ThinkingState": {
    "version": "1.0",
    "timestamp": "ISO8601",
    "workspace": {
      "active_items": ["item_id"],
      "focus_items": ["item_id"],
      "suppressed_items": ["item_id"],
      "capacity_limit": 7
    },
    "belief_state": {
      "hypotheses": [
        {
          "id": "string",
          "content": "any",
          "confidence": 0.0,
          "evidence": ["string"],
          "status": "active|rejected|committed"
        }
      ],
      "active_model": {},
      "confidence": 0.0,
      "uncertainty": 0.0,
      "entropy": 0.0
    },
    "goal_state": {
      "primary_goal": {
        "id": "string",
        "description": "string",
        "priority": 1.0,
        "deadline": "ISO8601|null"
      },
      "secondary_goals": [],
      "priority_weights": {},
      "satisfied_goals": []
    },
    "constraint_state": {
      "hard_constraints": [
        {
          "id": "string",
          "type": "resource|time|logic|safety",
          "description": "string",
          "check_fn": "reference"
        }
      ],
      "soft_constraints": [],
      "violations": [
        {
          "constraint_id": "string",
          "severity": "critical|warning",
          "message": "string"
        }
      ]
    },
    "error_state": {
      "prediction_error": 0.0,
      "coherence_error": 0.0,
      "constraint_error": 0.0,
      "reasoning_error": 0.0,
      "detected_anomalies": []
    },
    "control_state": {
      "mode": "hold|explore|compare|simulate|verify|repair|commit|defer",
      "depth": "low|medium|high",
      "search_budget": 100,
      "time_budget_ms": 5000,
      "iteration_count": 0,
      "max_iterations": 10
    },
    "transition_state": {
      "last_operation": "string|null",
      "next_operation": "string|null",
      "improvement_score": 0.0,
      "convergence_detected": false
    },
    "quality_metrics": {
      "coherence": 0.0,
      "goal_alignment": 0.0,
      "constraint_satisfaction": 0.0,
      "predictive_power": 0.0,
      "overall_quality": 0.0
    }
  }
}
```

---

## 9. Thinking Invariants

| ID | Rule |
|----|------|
| THI01 | Thinking must operate on internal state, not directly on text |
| THI02 | Every thinking step must be a state transformation |
| THI03 | State quality should improve across successful thinking transitions |
| THI04 | Language rendering is downstream of thinking, not identical to thinking |
| THI05 | Thinking mode must be explicitly selected |
| THI06 | Error detection and repair are mandatory parts of thinking |
| THI07 | Uncommitted hypotheses must remain distinct until evaluated |

---

## 10. Tensor Representation

### State Tensor
```
S_t ∈ ℝ^{N×F}
```
- N: state units
- F: state features

### Hypothesis Tensor  
```
H_t ∈ ℝ^{K×F_h}
```
- K: active hypotheses

### Goal Tensor
```
G_t ∈ ℝ^J
```
- J: goal channels

### Constraint Tensor
```
C_t ∈ ℝ^L
```
- L: constraint channels

### Error Tensor
```
E_t ∈ ℝ^M
```
- M: error channels

### Control Tensor
```
Π_t ∈ ℝ^R
```
- R: mode/control channels

### Complete Update

```
S_{t+1} = Commit(Repair(Evaluate(Simulate(Transform(Compare(Focus(S_t, G_t, C_t, E_t, Π_t)))))))
```

---

## 11. Meta-Thinking Layer

```
Meta_t = Model(T_t)
```

### Meta-Thinking Loop

```
MetaThink = ObserveThinking → DetectFailure → SelectBetterOperator → UpdatePolicy
```

### Meta-State Schema

```json
{
  "MetaThinkingState": {
    "current_operator": "string",
    "operator_quality_history": [
      {
        "operator": "string",
        "quality_score": 0.0,
        "timestamp": "ISO8601"
      }
    ],
    "failure_signals": [
      {
        "type": "stagnation|oscillation|error_accumulation",
        "severity": "low|medium|high",
        "description": "string"
      }
    ],
    "repair_candidate": {
      "operator": "string",
      "reason": "string"
    },
    "policy_update_required": false,
    "policy_version": 1,
    "learning_rate": 0.1
  }
}
```

---

## 12. Corrected System Stack

```
Input → Read → Think → Verify → Select → Act → Render
```

### Expanded

```
Input → BrainReadingKernel → StableRead → ThinkingKernel → VerifiedState → ControlSelection → Commit → RestrictedRenderer
```

### Data Flow

1. **Input** - External stimulus
2. **Read** - Structured ingestion (not thinking yet)
3. **Think** - Internal state transformation (this kernel)
4. **Verify** - Validate against reality/constraints
5. **Select** - Choose action/control mode
6. **Act** - Execute decision
7. **Render** - Convert internal state to language (output)

---

## 13. API Specification

### Core Functions

```python
# Initialize thinking state
def initialize_thinking_state(
    goals: list[Goal],
    constraints: list[Constraint],
    initial_workspace: list[Item]
) -> ThinkingState

# Execute single thinking step
def think_step(
    state: ThinkingState,
    input_data: any,
    mode: ThinkingMode
) -> ThinkingState

# Execute full thinking loop
def think(
    state: ThinkingState,
    input_data: any,
    max_iterations: int = 10,
    convergence_threshold: float = 0.01
) -> ThinkingResult

# Evaluate state quality
def evaluate_state_quality(state: ThinkingState) -> QualityMetrics

# Select thinking mode
def select_thinking_mode(
    state: ThinkingState,
    error_state: ErrorState,
    goals: list[Goal]
) -> ThinkingMode

# Meta-think about thinking
def meta_think(meta_state: MetaThinkingState, thinking_history: list[ThinkingState]) -> MetaThinkingState
```

### Operator Functions

```python
def hold_state(state: ThinkingState) -> ThinkingState
def select_focus(state: ThinkingState, mask: FocusMask) -> ThinkingState
def activate_memory(state: ThinkingState, memory_query: str) -> ThinkingState
def form_hypothesis(state: ThinkingState) -> ThinkingState
def compare_hypotheses(state: ThinkingState) -> ThinkingState
def transform_representation(state: ThinkingState, transform_type: str) -> ThinkingState
def simulate_consequence(state: ThinkingState, horizon: int) -> ThinkingState
def evaluate_state(state: ThinkingState) -> tuple[ThinkingState, EvaluationScore]
def detect_error(state: ThinkingState, expected: any) -> ErrorState
def repair_structure(state: ThinkingState, error_state: ErrorState) -> ThinkingState
def commit_state_update(state: ThinkingState) -> ThinkingState
```

---

## 14. Integration Points

### With Reading Kernel
- Reading kernel provides `Input_t` → Thinking kernel operates on `S_t`
- Reading stabilizes input, thinking transforms internal state

### With AMOS Core
- Thinking kernel outputs feed into AMOS decision engine
- AMOS health monitoring tracks thinking quality metrics
- Self-healing can reset thinking state on convergence failure

### With Output/Render
- Thinking state is **never** directly rendered
- A separate renderer converts `S_t` to language
- Renderer is downstream, not part of thinking

---

## 15. Success Metrics

A machine is thinking successfully when:

1. **State Improvement** - Q(S_{t+1}) > Q(S_t) consistently
2. **Convergence** - Reaches stable internal state
3. **Goal Alignment** - Higher alignment with each iteration
4. **Error Reduction** - Fewer errors over time
5. **Mode Appropriateness** - Correct mode selection for problem type
6. **Meta-Learning** - Improves operator selection over time

---

## 16. Implementation Requirements

### Core Module: `amos_thinking_kernel.py`

```python
class ThinkingState:
    """Immutable internal thinking state."""
    workspace: Workspace
    belief_state: BeliefState
    goal_state: GoalState
    constraint_state: ConstraintState
    error_state: ErrorState
    control_state: ControlState
    transition_state: TransitionState
    quality_metrics: QualityMetrics

class ThinkingKernel:
    """Core thinking engine."""
    
    def think(self, state: ThinkingState, input_data: any) -> ThinkingState
    def evaluate_quality(self, state: ThinkingState) -> float
    def select_mode(self, state: ThinkingState) -> ThinkingMode
    def check_convergence(self, history: list[ThinkingState]) -> bool

class ThinkingOperators:
    """Primitive thinking operations."""
    
    @staticmethod
    def hold(state: ThinkingState) -> ThinkingState
    @staticmethod
    def focus(state: ThinkingState, mask: FocusMask) -> ThinkingState
    @staticmethod
    def compare(state: ThinkingState) -> ThinkingState
    @staticmethod
    def transform(state: ThinkingState, transform_type: str) -> ThinkingState
    @staticmethod
    def simulate(state: ThinkingState, horizon: int) -> ThinkingState
    @staticmethod
    def evaluate(state: ThinkingState) -> tuple[ThinkingState, float]
    @staticmethod
    def repair(state: ThinkingState, errors: ErrorState) -> ThinkingState
    @staticmethod
    def commit(state: ThinkingState) -> ThinkingState
```

---

## 17. References

- AMOS Core Architecture (28 phases)
- Brain Reading Kernel Specification
- Superintelligence Core Requirements
- Cognitive Science: Working Memory (Baddeley), Global Workspace Theory (Baars)
- AI: ACT-R, SOAR, Leabra architectures

---

*End of Specification*
