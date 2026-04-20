# AMOS Kernel - Universal Law Kernel Architecture

Kernel-first stabilization for the AMOS system.

## Architecture

```
ULK → DeterministicCore → UniversalState → SelfObserver → RepairExecutor
(L0)      (L1)               (L2)            (L3/L4)        (L5)
```

All runtime, build, and repair paths must validate through this stack.

## Five Layers

### L0 - Universal Law Kernel (K0)
**File:** `L0_universal_law_kernel.py`

Hard rules only. No app logic. No UX logic.

**Responsibilities:**
- Law precedence
- Contradiction detection: `¬(A ∧ ¬A)`
- Dual-check enforcement: `S = (x_int, x_ext), x_ext ≠ ∅`
- Quadrant completeness: `∏ I(Q_i) > 0`
- Collapse thresholding: `dC/dt ≤ dR/dt`

**Core Constraints:**
- Non-contradiction
- Correction rate
- Dual interaction
- Quadrant completeness
- Determinism

### L1 - Deterministic Core (K1)
**File:** `L1_deterministic_core.py`

The reasoning engine. The brain stem.

**Core Equation:**
```
S_{t+1} = F((i_A ⊗ i_B), Feedback, Constraints, Integrity)
```

**Deterministic Rule:**
Same state + same inputs + same constraints = same output class.

**Responsibilities:**
- State transition
- Prediction update
- Correction loop
- Consistency-preserving execution
- Bounded adaptation

### L2 - Universal State Model (K2)
**File:** `L2_universal_state_model.py`

One normalized internal representation.

**State Tensor:** `T^{μναβ}`

**Axes:**
- `μ`: biological / load / regulation
- `ν`: cognition / prediction / contradiction
- `α`: org-system / policy / coordination
- `β`: environment / context / external pressure

**Why this matters:** The repo has too many disconnected surfaces. This tensor becomes the one internal state object every layer reads and updates.

### L3 - Interaction Engine (K3)
**File:** `L3_interaction_engine.py`

Implements the interaction operator.

**Core Equation:**
```
E = i_A ⊗ i_B
```

**Responsibilities:**
- Interaction operator
- Internal/external state coupling
- Feedback extraction
- Signal transformation

### L4 - Self Observer (K4)
**File:** `L4_self_observer.py`

Where the "brain fixes itself" begins. But it only proposes.

**Core Loop:**
```
system → observe self → detect drift → propose correction
→ validate via ULK → apply via RepairExecutor
```

**Responsibilities:**
- Drift detection
- Mismatch detection
- Contract violations
- Structural audits
- Correction proposals

**Rule:** No direct mutation without validation.

### L5 - Repair Executor (K5)
**File:** `L5_repair_executor.py`

Bounded self-healing. Can only act after validation.

**Responsibilities:**
- Deterministic codemods
- Package contract sync
- Entrypoint rewrites
- Import normalization
- CI contract correction

**Execution Rule:**
1. Observer detects issue
2. ULK validates repair
3. Deterministic core confirms no invariant break
4. THEN repair executes

## Usage

### Initialize the Kernel

```python
from amos_kernel import initialize_kernel

result = initialize_kernel()
if result.success:
    print("Kernel ready")
    print(f"All layers: {result.value.all_ready}")
else:
    print(f"Kernel failed: {result.errors}")
```

### Validate Through ULK

```python
from amos_kernel import (
    UniversalLawKernel,
    UniversalStateModel,
)

ulk = UniversalLawKernel()
state_model = UniversalStateModel()

# Normalize state
state = state_model.normalize({
    "system_load": 50.0,
    "health_score": 0.9,
    "paths": {
        "claimed": "/api/v1",
        "actual": "/api/v1"
    }
})

# Validate action
action = {"type": "deploy", "target": "production"}
result = ulk.validate_invariants(state, action)

if result.success:
    print("Action validated")
else:
    print(f"Violations: {result.errors}")
```

### Detect Drift

```python
from amos_kernel import SelfObserver, UniversalStateModel

observer = SelfObserver()
state_model = UniversalStateModel()

state = state_model.normalize({...})
drift_reports = observer.detect_drift(state)

for drift in drift_reports:
    print(f"{drift.drift_type}: severity={drift.severity}")
```

### Propose and Execute Repairs

```python
from amos_kernel import RepairExecutor

repair = RepairExecutor()

# Create repair plan
plan = repair.create_codemod_repair(
    target_file="module.py",
    modifications=[{"type": "typing", "old": "List", "new": "list"}]
)

# Simulate first
sim_result = repair.simulate(plan)
if sim_result.value.would_succeed:
    # Apply with validation chain
    apply_result = repair.apply(plan)
    if apply_result.success:
        verify_result = repair.verify(plan.plan_id)
```

## Minimal Invariants

### Invariant A - No Contradiction
A package cannot claim one runtime path while CI tests another.

### Invariant B - Dual Interaction
Every decision must reference:
- Internal state
- External state

No isolated reasoning.

### Invariant C - Quadrant Completeness
Every major repair must score four quadrants:
- Code correctness
- Build/release correctness
- Operational correctness
- Environment/dependency correctness

### Invariant D - Correction Rate
If drift is appearing faster than repair is landing, freeze feature development.

## File Structure

```
amos_kernel/
├── __init__.py                    # Package exports
├── __main__.py                    # CLI entry point
├── cli.py                         # CLI implementation
├── api.py                         # FastAPI server
├── contracts/
│   └── __init__.py                # Formal contracts
├── core/                          # Six-layer kernel core
│   ├── __init__.py
│   ├── law.py                     # Universal Law Kernel (K0)
│   ├── state.py                   # State tensor (K1)
│   ├── deterministic.py           # Deterministic engine (K2)
│   ├── interaction.py             # Interaction operator (K3)
│   ├── observe.py                 # Self-observer (K4)
│   └── repair.py                  # Repair executor (K5)
├── workflows/
│   ├── __init__.py                # Workflow engine
│   └── engine.py                  # Execution engine
├── tasks/
│   ├── __init__.py                # Task queue module
│   └── queue.py                   # SQLite-backed queue
├── plugins/
│   ├── __init__.py                # Plugin system
│   └── registry.py                # Plugin registry
├── equations/
│   ├── __init__.py                # Equation module
│   └── executor.py                # 145+ equations
├── adapters/
│   ├── __init__.py                # Integration adapters
│   ├── legacy_bridge.py           # Legacy amos_brain bridge
│   └── equation_bridge.py         # Equation system bridge
├── observability/
│   ├── __init__.py                # Metrics module
│   └── metrics.py                 # Prometheus metrics
├── tests/
│   └── test_kernel_stack.py       # Kernel tests
└── README.md                      # This file
```

## CLI Commands

```bash
# Run kernel doctor
python -m amos_kernel doctor

# Check kernel health
python -m amos_kernel health

# Execute equation
python -m amos_kernel execute softmax --logits 1.0,2.0,3.0

# List all equations
python -m amos_kernel equations

# Show version
python -m amos_kernel version
```

## Workflow Engine

Execute workflows through the kernel with law validation:

```python
from amos_kernel.workflows import get_workflow_engine

engine = get_workflow_engine()
result = engine.execute(
    workflow_id='deploy-pipeline',
    raw_input={
        'biological': {'load': 0.5},
        'cognitive': {'focus': 0.8},
        'system': {'cpu': 0.3, 'memory': 0.4},
        'environment': {'risk': 0.1, 'temperature': 0.5},
    },
    validate_laws=True,
)

print(f"Workflow passed: {result.law_validation.passed}")
print(f"Collapse risk: {result.collapse_risk:.2%}")
```

## Task Queue

Async task execution with SQLite persistence:

```python
from amos_kernel.tasks import get_task_queue, TaskProcessor

queue = get_task_queue(db_path="./kernel_tasks.db")

# Submit task
task_id = queue.submit_task(
    task_type="process_data",
    payload={"data": "input"},
    priority=5
)

# Process with worker
async def run_worker():
    processor = TaskProcessor()
    await queue.process_tasks(processor)
```

## Plugin Registry

Extensible plugin system with lifecycle hooks:

```python
from amos_kernel.plugins import Plugin, get_plugin_registry

class MyPlugin(Plugin):
    def on_load(self) -> None:
        self.logger.info("Plugin loaded")

    def on_kernel_start(self) -> None:
        self.register_hook("workflow_start", self.on_workflow)

    def on_workflow(self, context):
        print(f"Workflow {context.workflow_id} starting")

# Register
registry = get_plugin_registry()
registry.register("my-plugin", MyPlugin)
registry.load_all()
```

## Equation Executor

Execute 145+ mathematical equations with kernel validation:

```python
from amos_kernel.equations import get_executor

executor = get_executor()

# ML equations
result = executor.execute('softmax', {'logits': [1.0, 2.0, 3.0]})
result = executor.execute('sigmoid', {'x': 0.0})
result = executor.execute('attention', {
    'queries': [[1.0, 0.0]],
    'keys': [[0.5, 0.5]],
    'values': [[1.0, 2.0]],
})

# Physics
result = executor.execute('noether_conservation', {'symmetry': 'time'})

# Queueing theory
result = executor.execute('mm1_queue', {
    'arrival_rate': 0.8,
    'service_rate': 1.0,
})

# Quantum computing
result = executor.execute('quantum_volume', {
    'num_qubits': 8,
    'depth': 8,
    'success_prob': 0.7,
})

# Check kernel validation
assert result.law_passed
assert result.collapse_risk < 0.5
```

## API Server

FastAPI server for kernel REST endpoints:

```python
from amos_kernel.api import create_kernel_api
from fastapi import FastAPI

app: FastAPI = create_kernel_api()

# Endpoints:
# POST /v1/kernel/execute - Execute workflow
# POST /v1/kernel/validate - Validate laws
# GET  /v1/kernel/health - Health check
# GET  /v1/metrics - Prometheus metrics
```

Run server:
```bash
python -m amos_kernel.api
# or
uvicorn amos_kernel.api:app --host 0.0.0.0 --port 8000
```

## Testing

```bash
# Run all kernel tests
pytest tests/kernel/ -v

# Run with coverage
pytest tests/kernel/ --cov=amos_kernel --cov-report=term

# Run specific tests
pytest tests/kernel/test_kernel_core.py::TestUniversalLawKernel -v
pytest tests/kernel/test_kernel_core.py::TestEquationExecutor -v
```

## Integration with Existing AMOS

The kernel becomes the **root dependency** of all critical paths:

1. **Build validation** → routes through ULK
2. **Runtime entry validation** → routes through ULK
3. **Self-repair validation** → routes through ULK
4. **CI gate validation** → routes through ULK

No launcher, CLI, workflow, or repair tool should bypass the kernel.

## Success Criteria

**Kernel-first stabilization** means:
- [x] One ULK exists
- [x] One deterministic core exists
- [x] One universal state model exists
- [x] One self-observer exists
- [x] One repair executor exists
- [ ] All runtime/build paths validated through them (in progress)

## Version

`1.0.0-kernel` - Initial kernel architecture implementation
