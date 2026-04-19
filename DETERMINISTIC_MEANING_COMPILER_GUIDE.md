# AMOS Deterministic Meaning Compiler (DMC)
## Anti-Rubbish Architecture Implementation

---

## Overview

The **Deterministic Meaning Compiler** replaces free text generation with a structured compilation pipeline:

```
Input → Read → Compile → TypeCheck → ConstraintCheck → Verify → Commit → Render
```

**Root Law**: `FreeGeneration = PrimaryFailureMode`

**Invariant**: No free text before stable typed meaning.

---

## Core Architecture

### DMC_AMOS = (RK, MC, TC, CC, VK, CK, RR)

| Component | Name | Purpose |
|-----------|------|---------|
| RK | Reading Kernel | Stable reading of input into structured representation |
| MC | Meaning Compiler | Converts StableRead → TypedMeaningGraph |
| TC | Type Checker | Verifies semantic type safety |
| CC | Constraint Checker | Ensures constraint preservation |
| VK | Verification Kernel | Proves internal adequacy |
| CK | Commit Kernel | Controls commitment modes |
| RR | Restricted Renderer | Deterministic projection (not free completion) |

---

## Usage

### Basic Usage

```python
from amos_meaning_compiler import compile_input, RenderMode

# Compile a clear instruction
result = compile_input(
    "Implement a Python function 'calculate_softmax' that takes a list of floats",
    render_mode=RenderMode.JSON_PROJECTION
)

print(result["commit_mode"])  # commit_final | clarify | defer | block
print(result["final_output"])
```

### With Required Constraints

```python
result = compile_input(
    "Deploy the application",
    required_constraints=[
        "Must pass CI/CD pipeline",
        "Must have approval from security team",
        "Cannot deploy during peak hours"
    ]
)

# Check constraint preservation
print(result["stages"]["constraint_check"]["preservation_score"])
```

### Multi-Turn Clarification

```python
from amos_meaning_compiler import compile_with_clarification

# First attempt - ambiguous
result1 = compile_input("Fix it")
# → commit_mode: clarify

# Second attempt with clarification
result2 = compile_with_clarification(
    "Fix it",
    clarification_response="Fix the bug in amos_api.py where the import fails",
    previous_context=result1
)
# → commit_mode: commit_final
```

---

## Integration with AMOS Brain

### Option 1: Pre-Processing Layer

```python
from amos_brain_working import think
from amos_meaning_compiler import DeterministicMeaningCompiler

class AMOSBrainWithDMC:
    def __init__(self):
        self.dmc = DeterministicMeaningCompiler()
        self.brain = WorkingBrain()
    
    def process(self, request: str, context: dict = None):
        # First: Compile meaning
        compiled = self.dmc.process(request)
        
        if compiled["commit_mode"] == "commit_final":
            # Safe to use brain with structured goal
            goal = compiled["final_output"]["output"]
            return self.brain.think_with_goal(goal, context)
        elif compiled["commit_mode"] == "clarify":
            return {
                "status": "clarification_required",
                "questions": compiled["final_output"]["clarifications_needed"]
            }
        else:
            return {
                "status": "blocked",
                "reason": compiled["final_output"]["reason"]
            }
```

### Option 2: Kernel Integration

```python
# In amos_kernel_runtime.py
from amos_meaning_compiler import DeterministicMeaningCompiler

class AMOSKernelRuntime:
    def __init__(self):
        self.dmc = DeterministicMeaningCompiler()
        # ... existing init
    
    def execute_cycle(self, observation: dict, goal: dict) -> dict:
        # Compile the goal before execution
        if "input_data" in observation:
            compiled = self.dmc.process(observation["input_data"])
            
            if compiled["commit_mode"] != "commit_final":
                return {
                    "status": "compilation_failed",
                    "mode": compiled["commit_mode"],
                    "output": compiled["final_output"]
                }
            
            # Use compiled machine goal
            goal = compiled["final_output"]["output"]
        
        # Continue with normal kernel execution
        # ...
```

---

## Anti-Rubbish Metrics

The DMC tracks metrics to monitor "rubbish" generation:

| Metric | Description | Target |
|--------|-------------|--------|
| Type Safety Rate | % of outputs passing type check | >95% |
| Constraint Preservation | % of constraints preserved | 100% |
| Binding Completion | % of required bindings resolved | >90% |
| Verification Pass Rate | % passing all verification checks | >85% |
| Renderer Drift Rate | % drift between structure and output | <5% |
| Rubbish Rate | Composite: FreeFill × ConstraintDrop × BindingInvention × Drift | <0.01 |

---

## Error Classes (Rubbish Bugs)

| Code | Name | Definition |
|------|------|------------|
| RB01 | Free Fill | Missing structure replaced by fluent text |
| RB02 | Constraint Drop | Explicit constraint omitted in output |
| RB03 | Binding Invention | Unresolved reference silently guessed |
| RB04 | Type Confusion | Question rendered as instruction |
| RB05 | Conflict Smoothing | Internal conflict hidden by smooth language |
| RB06 | Confidence Hallucination | Output sounds certain despite low verification |
| RB07 | Renderer Drift | Rendered text contains content absent from verified structure |

---

## Render Modes

| Mode | Use Case |
|------|----------|
| `JSON_PROJECTION` | API responses, structured data |
| `SCHEMA_PROJECTION` | Schema-validated output |
| `STEP_PROJECTION` | Step-by-step plans |
| `CLARIFICATION_PROJECTION` | Asking for clarification |
| `REFUSAL_PROJECTION` | Blocking unsafe requests |
| `BOUNDED_TEXT_PROJECTION` | Constrained natural language (last resort) |

---

## State Machine

```
RAW_INPUT → READ → COMPILED → TYPECHECKED → CONSTRAINT_CHECKED → VERIFIED → COMMITTED → RENDERED
                ↓           ↓                ↓                  ↓
                CLARIFY   CLARIFY          CLARIFY            DEFER/BLOCK
```

---

## Configuration

```python
from amos_meaning_compiler import (
    DeterministicMeaningCompiler,
    VerificationKernel,
    CommitKernel,
)

# Create customized compiler
dmc = DeterministicMeaningCompiler()

# Adjust verification thresholds
dmc.verification_kernel.conflict_threshold = 0.2  # Stricter
dmc.verification_kernel.ambiguity_threshold = 0.2
dmc.verification_kernel.min_confidence = 0.6

# Adjust commit requirements
dmc.commit_kernel.min_confidence_for_final = 0.8  # Higher bar
```

---

## Testing

### Run Self-Test

```bash
python amos_meaning_compiler.py
```

### Test Cases

```python
# Test 1: Clear instruction (should commit)
result = compile_input("Write a Python function called 'add' that takes two integers")
assert result["commit_mode"] == "commit_final"

# Test 2: Ambiguous (should clarify)
result = compile_input("Fix it")
assert result["commit_mode"] == "clarify"

# Test 3: Missing constraints (should defer or block)
result = compile_input(
    "Deploy to production",
    required_constraints=["Must have passed tests"]
)
assert result["stages"]["constraint_check"]["preservation_score"] < 1.0
```

---

## Migration from Generation-First

### Old Pattern (Generation-First)

```python
# ANTI-PATTERN: Free generation
def process_request(input_text):
    return generate_text(input_text)  # May produce rubbish
```

### New Pattern (Compiler-First)

```python
# CORRECT: Structured compilation
def process_request(input_text):
    dmc = DeterministicMeaningCompiler()
    result = dmc.process(input_text)
    
    if result["commit_mode"] == "commit_final":
        return result["final_output"]["output"]
    elif result["commit_mode"] == "clarify":
        return ask_for_clarification(result["final_output"])
    else:
        return refuse_with_reason(result["final_output"])
```

---

## Verification

The strongest invariant:

> **If it cannot be compiled, typed, checked, and verified, it must not be said as fact.**

---

## Files

- `amos_meaning_compiler.py` - Main implementation (~2000 lines)
- `DETERMINISTIC_MEANING_COMPILER_GUIDE.md` - This guide

---

## Status

**Architecture**: ✅ Anti-rubbish compiler implemented  
**Integration**: Ready for AMOS brain integration  
**Testing**: Self-test passing  
**Status**: Ready for production use
