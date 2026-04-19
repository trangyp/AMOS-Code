# AMOS Thinking Kernel Integration Guide

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AMOS SYSTEM WITH THINKING                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │  Input   │───▶│  Read    │───▶│  Think   │───▶│  Verify  │           │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘           │
│         │              │              │              │                   │
│         │              │              │              │                   │
│         ▼              ▼              ▼              ▼                   │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │                    Thinking Kernel (NEW)                    │         │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │         │
│  │  │  Workspace   │  │   Belief     │  │    Goal      │      │         │
│  │  │    W_t       │  │   State H_t  │  │   State G_t  │      │         │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │         │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │         │
│  │  │  Constraint  │  │    Error     │  │   Control    │      │         │
│  │  │   State C_t  │  │   State E_t  │  │   State Π_t  │      │         │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │         │
│  │                                                              │         │
│  │  S_{t+1} = T(S_t, Input_t)  [State Transformation]           │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │  Select  │───▶│   Act    │───▶│  Render  │───▶│  Output  │           │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Integration Points

### 1. Reading Kernel → Thinking Kernel

**Current:** Reading kernel outputs structured text
**NEW:** Reading kernel outputs populate Thinking State workspace

```python
# OLD: Reading returns text
read_result = reading_kernel.read(input_data)

# NEW: Reading populates thinking state workspace
thinking_state = thinking_kernel.initialize_state(
    initial_workspace=[read_result.structured_content]
)
```

### 2. Thinking Kernel → AMOS Core

**Current:** AMOS processes equations directly
**NEW:** AMOS receives committed thinking state

```python
# After thinking converges
t hinking_result = thinking_kernel.think(initial_state, max_iterations=10)

# Extract committed hypothesis for AMOS processing
best_hypothesis = thinking_result.final_state.belief_state.active_model.get('best_hypothesis_id')
amos.process_hypothesis(best_hypothesis)
```

### 3. Meta-Thinking → Self-Healing

**Integration:** Meta-thinking failure signals trigger self-healing

```python
if thinking_result.meta_state and thinking_result.meta_state.failure_signals:
    for signal in thinking_result.meta_state.failure_signals:
        if signal.severity == "high":
            # Trigger AMOS self-healing
            amos_self_healing.initiate_recovery(
                component="thinking_kernel",
                failure_type=signal.type.value
            )
```

## Implementation Steps

### Step 1: Import Thinking Kernel

```python
from amos_thinking_kernel import (
    ThinkingKernel,
    ThinkingState,
    Goal,
    Constraint,
    get_thinking_kernel,
    quick_think
)
```

### Step 2: Wrap Existing AMOS Functions

```python
class AMOSWithThinking:
    """AMOS system enhanced with thinking kernel."""
    
    def __init__(self):
        self.amos_core = get_amos_core()
        self.thinking_kernel = get_thinking_kernel(enable_meta=True)
    
    def process_with_thinking(self, problem: str, context: dict = None):
        """
        Process input through thinking before AMOS execution.
        
        Pipeline: Input → Read → Think → Verify → AMOS
        """
        # Step 1: Create goals from problem
        goals = [Goal(
            id="solve_problem",
            description=problem,
            priority=1.0
        )]
        
        # Step 2: Add constraints from context
        constraints = []
        if context and 'constraints' in context:
            for c in context['constraints']:
                constraints.append(Constraint(
                    id=f"ctx_{c['type']}",
                    type=c['type'],
                    description=c['description'],
                    hard=c.get('hard', True)
                ))
        
        # Step 3: Initialize thinking state
        initial_state = self.thinking_kernel.initialize_state(
            goals=goals,
            constraints=constraints,
            initial_workspace=[{"problem": problem, "context": context}]
        )
        
        # Step 4: Think
        thinking_result = self.thinking_kernel.think(
            initial_state,
            max_iterations=10,
            convergence_threshold=0.02
        )
        
        # Step 5: Extract solution from thinking state
        final_state = thinking_result.final_state
        best_hyp_id = final_state.belief_state.active_model.get('best_hypothesis_id')
        
        if best_hyp_id:
            best_hyp = next(
                h for h in final_state.belief_state.hypotheses
                if h.id == best_hyp_id
            )
            solution = best_hyp.content
        else:
            solution = {"thinking_result": "no_convergence"}
        
        # Step 6: Pass to AMOS for execution
        amos_result = self.amos_core.execute(solution)
        
        return {
            "thinking": {
                "converged": thinking_result.converged,
                "iterations": thinking_result.iterations,
                "quality_progression": thinking_result.quality_progression,
                "meta_signals": [
                    s.type.value for s in (thinking_result.meta_state.failure_signals if thinking_result.meta_state else [])
                ]
            },
            "amos_result": amos_result
        }
```

### Step 3: Replace Direct Processing

**BEFORE:**
```python
# Direct text → AMOS (no thinking)
result = amos.process(user_input)
```

**AFTER:**
```python
# Input → Think → AMOS
amos_with_thinking = AMOSWithThinking()
result = amos_with_thinking.process_with_thinking(user_input, context)
```

### Step 4: Add Thinking to API Gateway

```python
from fastapi import FastAPI
from amos_thinking_kernel import quick_think

app = FastAPI()

@app.post("/think-and-solve")
async def think_and_solve(problem: str):
    """
    API endpoint that thinks before solving.
    """
    # Quick thinking cycle
    result = quick_think(
        problem=problem,
        goal="analyze_and_solve",
        max_iterations=5
    )
    
    return {
        "converged": result.converged,
        "iterations": result.iterations,
        "quality": result.final_state.quality_metrics.overall_quality,
        "solution_model": result.final_state.belief_state.active_model,
        "confidence": result.final_state.belief_state.confidence
    }
```

## Migration Examples

### Example 1: Architecture Decision

**BEFORE (No Thinking):**
```python
# Direct processing
question = "Should we use microservices or monolith?"
analysis = amos.analyze(question)
recommendation = amos.recommend(analysis)
```

**AFTER (With Thinking):**
```python
# Structured thinking first
question = "Should we use microservices or monolith?"

# Define structured problem
problem = {
    "type": "architecture_decision",
    "question": question,
    "alternatives": ["microservices", "monolith"],
    "criteria": ["maintainability", "development_speed", "scalability"]
}

# Think about it
result = quick_think(
    problem=problem,
    goal="select_best_architecture",
    max_iterations=8
)

# Extract reasoning
best_hypothesis = result.final_state.belief_state.active_model
confidence = result.final_state.belief_state.confidence

# Only then execute AMOS commands
if confidence > 0.7:
    amos.execute_decision(best_hypothesis)
else:
    amos.request_more_info(best_hypothesis)
```

### Example 2: Code Analysis

**BEFORE:**
```python
# Direct code analysis
code = read_file("script.py")
issues = amos.analyze_code(code)  # Pattern matching only
```

**AFTER:**
```python
# Thinking-driven analysis
code = read_file("script.py")

# Form hypothesis about code structure
kernel = get_thinking_kernel()
state = kernel.initialize_state(
    goals=[Goal(id="analyze", description="Find code issues and improvements", priority=1.0)],
    initial_workspace=[{"code": code, "language": "python"}]
)

# Think about the code
result = kernel.think(state, max_iterations=6)

# Extract structured understanding
understanding = result.final_state.belief_state.active_model.get("abstractions", {})
potential_issues = result.final_state.error_state.detected_anomalies

# Now do targeted AMOS analysis
issues = amos.analyze_with_understanding(code, understanding)
```

## Configuration

### Environment Variables

```bash
# Thinking Kernel Configuration
THINKING_ENABLED=true
THINKING_MAX_ITERATIONS=10
THINKING_CONVERGENCE_THRESHOLD=0.02
THINKING_META_ENABLED=true
THINKING_WORKSPACE_CAPACITY=7

# Integration Settings
THINKING_BEFORE_AMOS=true
THINKING_LOG_STATE=true
THINKING_INVARIANT_CHECK=true
```

### Thinking Modes by Use Case

| Use Case | Mode | Iterations | Rationale |
|----------|------|------------|-----------|
| Quick Answer | CLARIFY | 2-3 | Fast classification |
| Deep Analysis | COMPARE/SIMULATE | 8-10 | Evaluate alternatives |
| Error Recovery | REPAIR | 3-5 | Fix and converge |
| Creative Task | DECOMPOSE | 5-7 | Generate options |
| Verification | VERIFY | 2-3 | Validate against constraints |

## Quality Monitoring

### Metrics to Track

```python
from amos_metrics_exporter import get_metrics_exporter

metrics = get_metrics_exporter()

# Track thinking quality
def record_thinking_result(result: ThinkingResult):
    metrics.gauge(
        "thinking_quality",
        result.final_state.quality_metrics.overall_quality,
        tags={"converged": str(result.converged)}
    )
    
    metrics.counter(
        "thinking_iterations",
        result.iterations
    )
    
    if result.meta_state and result.meta_state.failure_signals:
        for signal in result.meta_state.failure_signals:
            metrics.counter(
                "thinking_failure_signals",
                1,
                tags={"type": signal.type.value, "severity": signal.severity}
            )
```

### Alerting Rules

```yaml
# Alert when thinking fails to converge
- alert: ThinkingNotConverging
  expr: thinking_quality < 0.3 and thinking_iterations > 8
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Thinking kernel not converging"
    
# Alert on high error rates
- alert: ThinkingErrors
  expr: rate(thinking_failure_signals[5m]) > 0.5
  for: 2m
  labels:
    severity: critical
```

## Testing

### Unit Tests

```python
import pytest
from amos_thinking_kernel import (
    ThinkingKernel, Goal, Constraint,
    ThinkingInvariants
)

def test_thinking_converges():
    kernel = ThinkingKernel()
    state = kernel.initialize_state(
        goals=[Goal(id="test", description="Simple test", priority=1.0)],
        initial_workspace=[{"data": "test"}]
    )
    
    result = kernel.think(state, max_iterations=5)
    
    # Invariant: Quality should improve or stay stable
    assert result.quality_progression[-1] >= result.quality_progression[0] * 0.9
    
    # Invariant: THI03 - State quality check
    validations = ThinkingInvariants.validate_all(result.final_state, result.history)
    assert validations["THI03"][0], "Quality should not degrade"

def test_thinking_operators():
    kernel = ThinkingKernel()
    state = kernel.initialize_state()
    
    # Test hold operator
    new_state = kernel.operators.hold(state)
    assert new_state.control_state.mode.value == "hold"
    
    # Test form_hypothesis
    new_state = kernel.operators.form_hypothesis(state, {"test": "hypothesis"})
    assert len(new_state.belief_state.hypotheses) == 1
```

### Integration Tests

```python
def test_thinking_amos_integration():
    """Test full pipeline: Input → Think → AMOS"""
    amos_with_thinking = AMOSWithThinking()
    
    result = amos_with_thinking.process_with_thinking(
        "What is the best approach for caching?"
    )
    
    assert "thinking" in result
    assert "amos_result" in result
    assert result["thinking"]["converged"] is True
```

## Rollout Strategy

### Phase 1: Shadow Mode (Week 1)
- Run thinking kernel alongside existing AMOS
- Log thinking results, don't use them
- Compare thinking-assisted vs. direct results

### Phase 2: Opt-In (Week 2-3)
- Add `/think` endpoints to API
- Users can choose thinking-enhanced processing
- Monitor quality metrics

### Phase 3: Default (Week 4+)
- Make thinking the default path
- Direct processing becomes "quick mode" opt-out
- Full monitoring and alerting

## Summary

The Thinking Kernel adds true cognitive capability to AMOS:

1. **Internal State**: Structured workspace, not just text
2. **State Transformation**: S_t → S_{t+1} with quality improvement
3. **Meta-Cognition**: Thinking about thinking quality
4. **Integration**: Seamlessly connects to existing AMOS pipeline

**Result:** AMOS now thinks before it acts, leading to more intelligent, goal-directed behavior.

---

*See also:*
- `AMOS_THINKING_KERNEL_SPEC.md` - Formal specification
- `amos_thinking_kernel.py` - Implementation
- `amos_brain/` - Existing brain modules for integration points
