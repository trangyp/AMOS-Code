# AMOSL Quickstart Guide
**Get started with AMOSL in 5 minutes**

---

## Installation

```bash
git clone https://github.com/neurosyncai/AMOS-code.git
cd AMOS-code
pip install -e .
```

## Your First AMOSL Program

### 1. Classical Computation

```python
from amosl.runtime import RuntimeKernel

# Initialize
kernel = RuntimeKernel()

# Run 5 steps
for i in range(5):
    kernel.step(action_bundle={
        "classical": {"set": {"counter": i}, "emit": f"step_{i}"}
    })

print(f"Executed {kernel.state.time.t} steps")
print(f"History: {kernel.state.time.history}")
```

**Output:**
```
Executed 5.0 steps
History: ['step_0', 'step_1', 'step_2', 'step_3', 'step_4']
```

### 2. Verify Invariants

```python
from amosl.prover import TheoremProver

prover = TheoremProver()
proof = prover.prove_valid(kernel.state)

print(f"Verification: {proof.status.name}")
print(f"Invariants checked: {proof.metadata['checked']}")
```

**Output:**
```
Verification: PROVEN
Invariants checked: 8
```

### 3. Record to Ledger

```python
from amosl.ledger import Ledger

ledger = Ledger()

for i in range(5):
    ledger.record(
        step=i,
        state=kernel.state,
        outcome={"step": i, "status": "ok"},
        uncertainty={"classical": 0.01}
    )

print(f"Recorded {len(ledger.entries)} entries")
print(f"Chain valid: {ledger.verify_chain()[0]}")
```

**Output:**
```
Recorded 5 entries
Chain valid: True
```

### 4. Cross-Substrate Bridge

```python
from amosl.bridge import BridgeExecutor, BridgeType

bridge = BridgeExecutor()

# Classical → Quantum
result = bridge.execute(BridgeType.C_TO_Q, 1, qubit=0)
print(f"Encoded: {result['input']} → {result['output']['value']}")

# Quantum → Classical
result = bridge.execute(BridgeType.Q_TO_C, {"outcome": 0})
print(f"Measured: {result['output']}")
```

**Output:**
```
Encoded: 1 → |1⟩
Measured: False
```

### 5. Full End-to-End

```bash
python examples/demo_full_amOSL.py
```

**Output:**
```
======================================================================
  AMOSL END-TO-END EXECUTION DEMO
======================================================================

STEP 1: Initialize Runtime
  State manifold: 0 classical values

STEP 2: Execute 10 Steps
  Executed 10 steps, t=10.0

STEP 3: Verify Invariants
  Verification: PROVEN

STEP 4: Record to Ledger
  Recorded 10 entries

STEP 5: Cross-Substrate Bridges
  Executed 3 bridges

STEP 6: Block Matrix Evolution
  Evolved 5 steps

======================================================================
  EXECUTION COMPLETE
======================================================================
```

## Next Steps

- Read the [Master Specification](AMOSL_MASTER_SPEC.md)
- Explore [Theorem Prover Demo](../examples/demo_theorem_prover.py)
- Try the [Python SDK](../sdk/python/)
- Use the [MCP Server](../amos_mcp_server.py)

## Architecture Overview

```
AMOSL = ⟨O, S, D, C, Obs, U, A, V, R⟩

O: Ontology (classical, quantum, biological, hybrid)
S: Syntax
D: Denotational semantics
C: Compiler (CIR, QIR, BIR, HIR)
Obs: Observation operators
U: Uncertainty propagation
A: Action/effect system
V: Verification (8 invariants)
R: Runtime execution
```

## Key Features

| Feature | Traditional PL | AMOSL |
|---------|----------------|-------|
| Substrates | 1 | 4 (C, Q, B, H) |
| Formalism | Ad-hoc | 16-tuple + Category theory |
| Verification | Testing | Theorem proving |
| Audit | Logs | Immutable ledger |
| Effects | Implicit | Explicit tracking |

## Support

- GitHub: [AMOS-code](https://github.com/neurosyncai/AMOS-code)
- Domain: neurosyncai.tech
- Author: Trang Phan

---

**Ready to build with AMOSL! 🚀**
