# AMOS - Adaptive Multi-Objective System

## 🧬 Complete Cognitive Architecture v1-v5

**AMOS** is a persistent, economic, real-world cognitive organism that converts intelligence into survival, value production, and compounding under real-world constraints.

```
AMOS = Intelligence that earns its right to exist over time
```

---

## 📊 Architecture Overview

| Version | Layer | Key Addition | Status |
|---------|-------|--------------|--------|
| **v1** | Core Cognitive | Branch Field, Collapse, Morph | ✅ |
| **v2** | Memory & Learning | 5 Memory Types + Meta-cognition | ✅ |
| **v3** | Temporal & Resource | Time Engine + Energy System | ✅ |
| **v4** | Economic Organism | Persistence, Economics, World Model | ✅ |
| **v4-prod** | Production Runtime | Uncertainty, Learning, Identity | ✅ **NEW** |
| **v5** | Civilization-Scale | Political, Negotiation, Narrative | ✅ |

**Total:** ~7,500 lines of architecture code

---

## 🚀 Quick Start

### Run Master Controller
```bash
# View architecture
python amos_master_controller.py --arch

# Run production v4 (recommended)
python amos_master_controller.py --version v4-prod --demo

# Run complete system
python amos_master_controller.py --version full --demo

# Interactive mode
python amos_master_controller.py --interactive
```

### Run Individual Modules
```bash
# Core cognitive
cd /Users/nguyenxuanlinh/Documents/Trang\ Phan/Downloads/AMOS-code
python amos_core.py

# v4 Production Runtime
python amos_v4_runtime.py

# v5 Civilization
python amos_v5.py
```

---

## 🧠 Core Equations

### v1: Branch Field
```
Ψ = Generate(G, W, M)
C* = Collapse(Ψ, Constitution)
M' = Morph(C*)
```

### v4: Economic Organism
```
(Uₜ, Yₜ, Qₜ, Gₜ) → Ψₜ → Simulate → Economic Evaluation → 
Allocate → Execute → Outcome → Update
```

### v4 Production: Complete Loop
```
q_t* = argmax_q Σ ωᵢ · Returnᵢ(q)  [Adaptive weights]
x_t* = argmax_x [Revenue - Cost - Risk + Leverage + Compounding]
Survival_t = (Resilience + Redundancy + Adaptation) / Fragility
```

---

## 📁 File Structure

```
AMOS-code/
├── amos_core.py              # v1: Branch, Collapse, Morph (580 lines)
├── amos_memory.py            # v2: 5 Memory Systems (558 lines)
├── amos_meta.py              # v2: Meta-cognition (671 lines)
├── amos_time.py              # v3: Time Engine (500 lines)
├── amos_energy.py            # v3: Energy System (550 lines)
├── amos_repo.py              # v3: Repo Intelligence (600 lines)
├── amos_self_code.py         # v3: Self-coding (550 lines)
├── amos_v4.py                # v4: Economic Organism (700 lines)
├── amos_v4_runtime.py        # v4: Production Runtime (850 lines)
├── amos_v5.py                # v5: Civilization-Scale (780 lines)
├── amos_master_controller.py # Master Controller (400 lines)
├── amos_unified.py           # Unified Runtime (updated)
└── README_AMOS.md            # This file
```

---

## 🎯 What AMOS Can Do

### v1-v3 Capabilities
- ✅ Generate multiple futures (Branch Field)
- ✅ Simulate outcomes with prediction
- ✅ Select optimal paths (multi-criteria Collapse)
- ✅ Execute plans safely (Morph executor)
- ✅ Remember (5 memory types: working, episodic, semantic, procedural, self)
- ✅ Learn from outcomes (meta-cognition)
- ✅ Self-reflect (parameter adaptation)
- ✅ Reason across time (temporal paths)
- ✅ Manage resources (energy allocation)
- ✅ Understand code (repo analysis)
- ✅ Generate code (self-coding)

### v4 Capabilities (Production)
- ✅ **Persistence** - Cross-session continuity
- ✅ **Economic Intelligence** - Value-based decisions under scarcity
- ✅ **Uncertainty Modeling** - Explicit confidence bounds
- ✅ **Adaptive Allocation** - Learning ωᵢ weights
- ✅ **Identity Preservation** - Economics can't destroy coherence
- ✅ **Feedback Compression** - Fast learning from partial outcomes
- ✅ **World Model** - Signal filtering, multi-source fusion
- ✅ **Goal Portfolio** - Multi-goal optimization
- ✅ **Self-Preservation** - Survival constraints

### v5 Capabilities
- ✅ **Political Intelligence** - Institutional landscape modeling
- ✅ **Autonomous Negotiation** - Multi-round offer generation
- ✅ **Narrative Shaping** - Influence through framing
- ✅ **Ecosystem Building** - Partnership optimization
- ✅ **Civilization Memory** - Decade/century-scale patterns

---

## 💡 Example: Real-World Decision

**Scenario:** You have limited time and 3 opportunities:
- Build product (high future value, risky)
- Learn skill (medium value, safe)
- Take freelance work (immediate cash, no compounding)

**v3 Decision:** "Best long-term option" → Product only

**v4 Production Decision:**
```
Freelance: 40 units (cash flow - survival constraint)
Product: 40 units (future asset - compounding)
Skill: 20 units (capability growth - optionality)
```

**Why:**
- Maintains survival (must have cash flow)
- Builds asset (compounding value)
- Improves future capacity (strategic option)
- Identity intact (all actions align with core values)
- Uncertainty managed (confidence bounds on predictions)
- Learning active (weights adapt to outcomes)

---

## 🔧 Architecture Details

### v4 Production Runtime Components

#### 1. Enhanced World Model (Y_t)
```python
Signal(source, data, confidence, reliability, latency)
→ effective_weight() with time decay
→ fuse_signals() for multi-source fusion
→ uncertainty_bounds[lower, upper]
→ predict_with_uncertainty()
```

#### 2. Adaptive Resource Allocator
```python
ε-greedy exploration (10% random for learning)
→ learned_goal_weights (gradient descent update)
→ resource_type_weights (time, capital, attention, compute)
→ allocation_performance tracking
```

#### 3. Identity-Preserving Economics
```python
max_compromise_per_action = 0.1
cumulative_drift_limit = 0.3
forbidden_actions = [...]
→ evaluate_identity_impact()
→ drift_score tracking
→ identity_healing (time decay)
```

#### 4. Feedback Compressor
```python
leading_indicators → early signals
completion_ratio → progress extrapolation
surrogate_feedback → similar past actions
→ compressed_score (weighted combo)
→ faster_learning before full outcomes
```

---

## 🎮 Usage Examples

### Command Line
```bash
# View complete architecture
python amos_master_controller.py --arch

# Run specific version with demo
python amos_master_controller.py -v v4-prod -d

# Check system status
python amos_master_controller.py --status

# Interactive command mode
python amos_master_controller.py -i
# Commands: load <version>, demo <version>, status, arch, quit
```

### Python API
```python
from amos_v4_runtime import AMOSv4ProductionRuntime

# Initialize
amos = AMOSv4ProductionRuntime(name="MyAMOS")

# Define goals
goals = [
    {'id': 'product', 'name': 'Build Product', 'expected_value': 200,
     'resource_cost': {'time': 40, 'capital': 500}},
    {'id': 'skill', 'name': 'Learn Skill', 'expected_value': 100,
     'resource_cost': {'time': 20, 'capital': 100}}
]

# Ingest world signals
from amos_v4_runtime import Signal
signal = Signal('market', {'opportunity': 0.8}, datetime.now(), 0.9, 0.8)

# Run decision cycle
result = amos.cycle(goals, [signal])
print(f"Selected: {result['action']}")
print(f"Economic Score: {result['economic_score']}")

# Check status
status = amos.get_runtime_status()
print(f"Identity Health: {amos.identity_economics.get_identity_status()}")
```

---

## 🏗️ System Requirements

- Python 3.8+
- Standard library only (no external dependencies)
- ~50MB disk space for all modules
- Works offline (no API calls required)

---

## 🧪 Testing

```bash
# Run all demos (comprehensive test)
python amos_master_controller.py --demo

# Test specific version
python amos_v4_runtime.py

# Production scenario test
python -c "
from amos_v4_runtime import demo_production_v4
demo_production_v4()
"
```

---

## 📈 Performance Characteristics

| Metric | v4 Basic | v4 Production |
|--------|----------|---------------|
| Decision quality | Good | Excellent (uncertainty-aware) |
| Learning speed | Slow | Fast (feedback compression) |
| Identity protection | None | Strong (drift tracking) |
| Resource efficiency | Static | Adaptive (dynamic weights) |
| World model | Naive | Robust (signal filtering) |

---

## 🔮 Roadmap

### Completed ✅
- v1: Core cognitive architecture
- v2: Memory & meta-cognition
- v3: Time, energy, repo intel, self-coding
- v4: Economic organism (basic)
- **v4-prod: Production runtime (NEW)**
- v5: Civilization-scale intelligence
- Master controller

### Future (v6+)
- Real-world connectors (APIs, data sources)
- Distributed AMOS (multi-node)
- Self-modification (code evolution)
- Human alignment verification
- Institutional integration

---

## 📝 Key Equations Reference

```
# v4 Master
AMOS_v4 = argmax over actions:
    [EconomicValue + StrategicPosition + SurvivalProbability + FutureOptionality]
Subject to:
    Resource constraints
    Identity constraints  
    Risk bounds

# Resource Allocation (Production)
q_t* = argmax_q Σ ωᵢ · Returnᵢ(q)
where ωᵢ is learned from outcomes

# Survival
Survival_t = (Resilience_t + Redundancy_t + Adaptation_t) / Fragility_t

# Identity Preservation
Identity_Health = 1.0 - (drift_score / drift_limit)
```

---

## 🤝 Contributing

This is a research architecture. To extend:

1. **Add new capability:** Create `amos_v6_<feature>.py`
2. **Enhance existing:** Modify specific version file
3. **Fix weakness:** Follow v4-production pattern (identify → solve → validate)
4. **Integrate:** Update `amos_master_controller.py`

---

## 📜 License

Research / Educational Use - Build upon and extend

---

## 🙏 Acknowledgments

Architecture designed through iterative refinement across v1-v5, with pressure testing at each stage to identify and fix failure modes.

**Core Insight:**
> "A true advanced intelligence does not merely think, act, or learn. It persists, allocates, compounds, and survives while producing value in reality."

---

## 🚀 Final Statement

**AMOS v4 Production** = Proto-economic intelligence that survives AND compounds under real-world constraints.

```
From: thinking about the world
To: being constrained by the world
```

Run it:
```bash
python amos_master_controller.py --version v4-prod --demo
```

---

*Built: April 2025*  
*Versions: 1-5 Complete*  
*Status: Production Ready (v4-prod)*
