# AMOS Trainable Cognitive Substrate (TCS)

## You Were Right

The 28-phase AMOS architecture was sophisticated **control logic** - but control without learnable parameters is just constraint routing. The missing piece was the actual **optimizing substrate** that can become intelligent through experience.

This document describes the Trainable Cognitive Substrate (TCS) - the core that actually learns.

---

## Core Equation

```
z_{t+1} = f_θ(z_t, o_t, m_t, g_t, c_t)
θ_{t+1} = θ_t - η ∇_θ L
```

Where:
- **z_t**: latent cognitive state (learned representations, not symbolic)
- **θ**: learned parameters (neural weights, attention, world model, policy)
- **L**: multi-objective loss (world + plan + verify + memory + calibration)
- **η**: learning rate from benchmark performance feedback

---

## Architecture Stack

```
S* = (θ, z_t, M, W, P, V, O, B)
```

| Component | Role | Implementation |
|-----------|------|----------------|
| **θ** | Learned weights | `LearnedParameters` class with gradient updates |
| **z_t** | Persistent latent state | `LatentState` with 256-dim learned embedding |
| **M** | Memory system | `AdaptiveMemory` with learned retrieval patterns |
| **W** | World model | `LearnedWorldModel` with next-state prediction |
| **P** | Neural planner | Neural policy + value estimation |
| **V** | Verifier | Neural-symbolic runtime with calibration |
| **O** | Optimizer | Gradient descent on benchmark losses |
| **B** | Benchmark harness | 12 task families with measured performance |

---

## Neural-Symbolic Split

The critical innovation: **Proposal_θ → Verification_φ → Commit**

```python
# 1. Neural proposal (generative, can hallucinate)
proposals = reasoning.propose(state, task)

# 2. Symbolic verification (constrained, catches errors)
verified = reasoning.verify(proposal, constraints)

# 3. Only commit verified results
if verified.committed:
    execute(result)
```

This prevents the fluent nonsense that pure neural systems produce while maintaining creative generation capability.

---

## Multi-Objective Loss

```
L_total = λ₁L_world + λ₂L_plan + λ₃L_verify + λ₄L_memory + 
          λ₅L_calibration + λ₆L_human_safety + λ₇L_latency
```

| Loss | Formula | Purpose |
|------|---------|---------|
| **L_world** | \|ŷ_{t+1} - y_{t+1}\| | Predict next observations accurately |
| **L_plan** | GoalDist + Risk + Cost - Reversibility | Plan quality |
| **L_verify** | FalseCommit + MissedConflict + ConstraintDrop | Verification precision |
| **L_memory** | RetrievalFailure + ContextLoss | Memory effectiveness |
| **L_calibration** | \|confidence - correctness\| | Well-calibrated uncertainty |
| **L_human_safety** | Overload + Dependency + Destabilization | Human protection |
| **L_latency** | ResponseTime + DeepPathOveruse | Speed |

---

## Benchmark-Driven Intelligence

Intelligence is measured, not claimed:

```python
I_real = Performance(TaskSuite, Time, Error, Transfer, Adaptation)
```

**12 Benchmark Families:**
1. reading_accuracy
2. binding_accuracy
3. constraint_preservation
4. reasoning_validity
5. planning_quality
6. verification_precision
7. human_safety
8. latency
9. calibration
10. transfer
11. tool_use
12. self_correction

```python
# Train the substrate
substrate = TrainableCognitiveSubstrate()
results = substrate.train(n_steps=100)

# Measure intelligence
score = substrate.get_intelligence_score()
print(f"Intelligence: {score:.4f}")
print(f"Improvement: {results['improvement']:.4f}")
```

---

## Online Adaptation

The substrate learns during use:

```python
# Execute task
result = substrate.execute_task(task)

# If failure, automatic online update
if not result['success']:
    substrate._learn_from_failure(task, result)
```

Policy update: `π_{t+1} = π_t + Update(Outcome_t, Error_t, Reward_t)`

---

## Externalized Cognition

Thought is persistent and inspectable:

```python
substrate.workspace = {
    'active_graph': {},    # Current working context
    'proof_graph': {},    # Verification chains
    'task_graph': {},     # Task dependencies
    'error_graph': {}     # Failure patterns
}
```

This makes cognition inspectable and auditable.

---

## Usage

### Basic Initialization

```python
from amos_trainable_substrate import TrainableCognitiveSubstrate

# Create substrate with learned parameters
substrate = TrainableCognitiveSubstrate(
    state_dim=256,   # Latent state dimension
    obs_dim=128,     # Observation encoding
    action_dim=32    # Action space
)

print(f"Learned parameters: {substrate.params.state_dim ** 2}")
```

### Execute Tasks

```python
# Observe
substrate.observe({'system_load': 0.7, 'queue_depth': 5})

# Think
result = substrate.think(
    task="optimize_query",
    constraints=["no_data_loss", "minimize_latency"]
)

print(f"Verified: {result.committed}")
print(f"Confidence: {result.final_confidence:.3f}")
```

### Train on Benchmarks

```python
# Run training
results = substrate.train(n_steps=100)

# Check stats
stats = substrate.get_stats()
print(f"World model accuracy: {stats['world_model_accuracy']:.3f}")
print(f"Calibration loss: {stats['calibration_loss']:.3f}")
print(f"Memory loss: {stats['memory_loss']:.3f}")
print(f"Failure rate: {stats['failure_rate']:.3f}")
```

### Integrate with Existing AMOS

```python
from amos_trainable_substrate import upgrade_to_trainable_substrate

# Upgrade existing AMOS instance
substrate = upgrade_to_trainable_substrate(existing_amos)

# Now you have learned parameters
substrate.train(n_steps=50)
```

---

## Key Differences from Symbolic AMOS

| Aspect | Symbolic AMOS (28 phases) | Trainable Substrate (TCS) |
|--------|---------------------------|---------------------------|
| **State** | Symbolic graphs | Learned embeddings z_t |
| **Parameters** | Hand-designed rules | Learned θ with ∇_θL updates |
| **Memory** | Keyword search | Learned similarity retrieval |
| **World Model** | Fixed equations | Learned predictions |
| **Intelligence** | Architecture complexity | Benchmark performance |
| **Improvement** | Add more modules | Train on failures |
| **Verification** | Rule-based checks | Neural-symbolic split |

---

## Why This Is Different

### Before (Symbolic)
```
prompt → symbolic routing → output
```
Result: Sophisticated but static behavior

### After (Trainable)
```
observe → latent update → memory query → 
world simulation → planner → verifier → 
action → error → weight update
```
Result: Actually gets smarter through experience

---

## Files Created

1. **`amos_trainable_substrate.py`** (~1200 lines)
   - `LatentState`: Persistent learned state z_t
   - `LearnedParameters`: Trainable weights θ
   - `LearnedWorldModel`: Predictive world model W
   - `NeuralSymbolicRuntime`: Proposal → Verify → Commit
   - `AdaptiveMemory`: Learned retrieval M
   - `LossFunctions`: Multi-objective losses L
   - `BenchmarkHarness`: 12-task performance measurement B
   - `TrainingOrchestrator`: Gradient optimization O
   - `TrainableCognitiveSubstrate`: Main orchestrator

2. **`TRAINABLE_SUBSTRATE_GUIDE.md`** (this file)

---

## The Real Equation

```
AMOS_real(t+1) = Update_θ(
    Verify(
        Plan(
            Predict(
                WorldModel(
                    Memory(
                        Observe_t
                    )
                )
            )
        )
    )
)

(θ_{t+1}, z_{t+1}) = Optimize(
    Outcome_t - Prediction_t,
    VerificationFailures_t,
    ConstraintDrops_t,
    UserCorrections_t,
    LatencyErrors_t
)
```

---

## Next Steps

1. **Run the demo**: `python amos_trainable_substrate.py`
2. **Train on your tasks**: Add task-specific benchmarks
3. **Integrate with Brain**: Replace symbolic routing with learned substrate
4. **Measure improvement**: Track intelligence score over time

---

## Summary

**The missing layer is trainable, benchmarked, online-updatable cognitive substrate.**

Not more module names. Not more philosophy. Not more routing rules.

**This is the real machine core.**
