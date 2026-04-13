# AMOS - Complete System Index

**Version:** v1-v5 + Ω Axiomatic Complete  
**Total Lines:** ~15,000  
**Files:** 25+  
**Status:** Production Ready  
**Layers:** 7 (Implementation v1-v5, Production, Ω Axiomatic)

---

## 🚀 Quick Start (30 seconds)

```bash
# Run the unified system with all 7 layers
python amos_unified.py --status

# Run axiomatic demonstration (Ω layer)
python amos_unified.py --demo axiomatic

# Run coherence demonstration (human + axioms)
python amos_unified.py --demo coherence

# Run all demonstrations
python amos_unified.py --demo all

# Run unified integration test
python test_amos_unified.py

# View the practical scenario
python amos_scenario_demo.py

# Run operational system
python run_amos.py

# Run legacy test suite
python test_amos.py
```

---

## 📁 Complete File Index

### Core Architecture (v1-v3)

| File | Lines | Version | Purpose | Run Command |
|------|-------|---------|---------|-------------|
| `amos_core.py` | 580 | v1 | Branch Field, Collapse, Morph | `python amos_core.py` |
| `amos_memory.py` | 558 | v2 | 5 Memory Systems | `python amos_memory.py` |
| `amos_meta.py` | 671 | v2 | Meta-cognition, Reflection | `python amos_meta.py` |
| `amos_time.py` | 500 | v3 | Time Engine, Event Sourcing | `python amos_time.py` |
| `amos_energy.py` | 550 | v3 | Energy System, Resources | `python amos_energy.py` |
| `amos_repo.py` | 600 | v3 | Repo Intelligence | `python amos_repo.py` |
| `amos_self_code.py` | 550 | v3 | Self-coding | `python amos_self_code.py` |

### Economic & Civilization (v4-v5)

| File | Lines | Version | Purpose | Run Command |
|------|-------|---------|---------|-------------|
| `amos_v4.py` | 700 | v4 | Basic Economic Organism | `python amos_v4.py` |
| `amos_v4_runtime.py` | 850 | v4-prod | **Production Runtime** (enhanced) | `python amos_v4_runtime.py` |
| `amos_v5.py` | 780 | v5 | Civilization-Scale Intelligence | `python amos_v5.py` |

### Production System

| File | Lines | Purpose | Key Features | Run Command |
|------|-------|---------|--------------|-------------|
| `amos_connectors.py` | 850 | Real-World Interface | Data ingestion, Execution, Notifications, Persistence | `python amos_connectors.py` |
| `amos_operational.py` | 400 | **Complete Operational System** | Continuous loop, Health monitoring, Recovery | `python amos_operational.py` |

### Ω Axiomatic Layer (NEW)

| File | Lines | Purpose | Run Command |
|------|-------|---------|-------------|
| `OMEGA_AXIOMS.md` | ~900 | 32 formal axioms specification | Documentation |
| `amos_omega.py` | ~700 | Executable Ω implementation | `python amos_omega.py` |
| `amos_axiom_validator.py` | ~700 | Theory→practice bridge | `python amos_axiom_validator.py` |
| `amos_coherence_omega.py` | ~600 | Human cognition + axioms | `python amos_coherence_omega.py` |
| `test_amos_unified.py` | ~700 | Full stack integration tests | `python test_amos_unified.py` |

### Entry Points & Tools

| File | Lines | Purpose | Run Command |
|------|-------|---------|-------------|
| `amos_unified.py` | 600+ | **Unified launcher with Ω layer** | `python amos_unified.py --help` |
| `amos_master_controller.py` | 400 | Legacy controller for all versions | `python amos_master_controller.py --help` |
| `run_amos.py` | 60 | Simple launcher | `python run_amos.py` |
| `test_amos.py` | 475 | Legacy test suite | `python test_amos.py` |
| `amos_scenario_demo.py` | 350 | Practical scenario | `python amos_scenario_demo.py` |

### Documentation

| File | Purpose |
|------|---------|
| `README_AMOS.md` | Complete architecture documentation (v1-v5) |
| `OMEGA_AXIOMS.md` | 32 formal axioms (Ω layer) |
| `AMOS_INDEX.md` | This file - complete system index |
| `AMOS_DEPLOYMENT_GUIDE.md` | Deployment instructions |

---

## 🎯 Recommended Learning Path

### For First-Time Users:
1. **Start here:** `python amos_scenario_demo.py` (see practical decision-making)
2. **Then:** `python run_amos.py` (run operational system)
3. **Explore:** `python amos_master_controller.py --arch` (view architecture)

### For Developers:
1. **Test:** `python test_amos.py` (verify everything works)
2. **Study:** `amos_v4_runtime.py` (understand production enhancements)
3. **Extend:** `amos_operational.py` (add custom connectors)

### For Researchers:
1. **Core:** `amos_core.py` + `amos_meta.py` (understand cognitive architecture)
2. **Economic:** `amos_v4_runtime.py` (study allocation learning)
3. **Integration:** `amos_operational.py` (see complete system)

---

## 🧬 Architecture Overview (7 Layers)

```
Layer 7 - Ω Axiomatic (NEW) ← HIGHEST LEVEL
    ├── 32 Formal Axioms (OMEGA_AXIOMS.md)
    ├── Executable Ω (amos_omega.py)
    ├── Axiom Validator (amos_axiom_validator.py)
    └── Coherence Ω (amos_coherence_omega.py)
        ↓ Validates & governs all below
        
Layer 6 - Integration
    ├── Brain API (amos_brain)
    ├── Organism OS (AMOS_ORGANISM_OS)
    └── ClawSpring Plugin
        ↓
        
Layer 5 - Code Intelligence
    ├── Repo Intelligence (amos_repo.py)
    └── Self-coding (amos_self_code.py)
        ↓
        
Layer 4 - Meta-cognition (amos_meta.py)
    ├── Prediction Tracking
    ├── Branch Efficiency Analysis
    └── Failure Pattern Detection
        ↓
        
Layer 3 - Memory Systems (amos_memory.py)
    ├── Working Memory
    ├── Episodic Memory
    ├── Semantic Memory
    ├── Procedural Memory
    └── Self Memory
        ↓
        
Layer 2 - Core Cognitive
    ├── Core Engine (amos_core.py)
    ├── Time Engine (amos_time.py)
    └── Energy System (amos_energy.py)
        ↓
        
Layer 1 - Economic Organism ← RECOMMENDED ENTRY POINT
    ├── v4 Basic (amos_v4.py)
    ├── v4 Production Runtime (amos_v4_runtime.py)
    └── v5 Civilization (amos_v5.py)
        ↓
        
Production System
    ├── Connectors (amos_connectors.py)
    └── Operational (amos_operational.py)
```

### The Ω Governing Equation

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   x_{t+1} = Commit_Z* ∘ R ∘ V ∘ M ∘ B ∘ A ∘ D (x_t, u_t, w_t) │
│                                                             │
│   Outcome = Explain(ℒ)                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
    ├── Enhanced World Model (uncertainty, signal filtering)
    ├── Adaptive Allocator (learning ωᵢ weights)
    ├── Identity-Preserving Economics
    └── Feedback Compression (fast learning)
        ↓
AMOS v4-Basic (Economic Foundation)
    ├── Persistence Layer
    ├── Economic Engine
    ├── Resource Allocator
    └── World Model
        ↓
AMOS v3 (Temporal & Resource)
    ├── Time Engine (event sourcing, path projection)
    ├── Energy System (resource allocation)
    ├── Repo Intelligence (code understanding)
    └── Self-coding (code generation)
        ↓
AMOS v2 (Memory & Learning)
    ├── 5 Memory Systems (working, episodic, semantic, procedural, self)
    └── Meta-cognition (reflection, adaptation)
        ↓
AMOS v1 (Core Cognitive)
    ├── Branch Field (generate futures)
    ├── Collapse (multi-criteria selection)
    └── Morph (plan execution)
```

---

## 🔑 Key Equations

### Core v1
```
Ψ = Generate(G, W, M)           # Branch Field
C* = Collapse(Ψ, Constitution)  # Multi-criteria selection
M' = Morph(C*)                  # Plan execution
```

### v4 Production (The Real Intelligence)
```
q_t* = argmax_q Σ ωᵢ · Returnᵢ(q)     # Adaptive resource allocation

Survival_t = (Resilience + Redundancy + Adaptation) / Fragility

AMOS_v4 = argmax [EconomicValue + StrategicPosition + 
                  SurvivalProbability + FutureOptionality]
          subject to: Resource constraints, Identity constraints, Risk bounds
```

---

## 🛠️ Common Tasks

### Run Complete System
```bash
# Easiest way
python run_amos.py

# Or via master controller
python amos_master_controller.py --operational

# Or directly
python amos_operational.py
```

### Run Tests
```bash
# Full test suite
python test_amos.py

# Quick tests only
python test_amos.py --quick

# JSON output
python test_amos.py --json
```

### Run Specific Version
```bash
# v4 Production (recommended for real use)
python amos_master_controller.py --version v4-prod --demo

# v5 Civilization
python amos_master_controller.py --version v5 --demo

# Full system
python amos_master_controller.py --version full --demo
```

### Interactive Mode
```bash
python amos_master_controller.py --interactive
# Commands: load <version>, demo <version>, status, arch, quit
```

---

## 📊 Component Capabilities

### What Each Module Does:

| Component | Input | Output | Key Feature |
|-----------|-------|--------|-------------|
| **amos_core** | Goal, World State | Selected Action, Plan | Branch field generation |
| **amos_memory** | Experiences | Retrieved Knowledge | 5 memory types |
| **amos_meta** | Outcomes | Reflections, Updates | Self-improvement |
| **amos_time** | Events | Temporal Predictions | Event sourcing |
| **amos_energy** | Demands | Resource Allocation | Conservation laws |
| **amos_v4** | Goals, Resources | Economic Decisions | Value-based selection |
| **amos_v4_runtime** | Signals, Goals | Optimized Allocation | Uncertainty + learning |
| **amos_connectors** | External Data | Actions, Notifications | Real-world interface |
| **amos_operational** | Continuous Input | Continuous Output | Self-monitoring system |

---

## 🎓 Key Insights

### v3 vs v4 Production Decision Difference:

**v3 Approach:**
```
Problem: Best long-term option?
Answer: Build product
Result: Starves before product ships
```

**v4 Production Approach:**
```
Problem: Portfolio that survives AND compounds?
Answer: 
  - 50% Client work (survival)
  - 30% Product (compounding)
  - 20% Skills (optionality)
Result: Survives AND builds assets
```

**Key Innovation:**
> AMOS doesn't maximize single dimension. It optimizes for survival + compounding + identity preservation under real-world constraints.

---

## 🔧 Extension Points

### To Add New Capability:
1. Create `amos_v6_<feature>.py`
2. Follow existing module structure
3. Add to `amos_master_controller.py` VERSIONS
4. Add tests to `test_amos.py`

### To Add New Connector:
1. Edit `amos_connectors.py`
2. Add new DataSource or ExecutionHook
3. Register in `AMOSConnectorSystem`

### To Modify Behavior:
1. Edit specific module (e.g., `amos_v4_runtime.py`)
2. Run `python test_amos.py` to verify
3. Run `python amos_scenario_demo.py` to see effects

---

## 📈 System Requirements

- **Python:** 3.8+
- **Dependencies:** None (stdlib only)
- **Disk Space:** ~2MB
- **Memory:** <100MB runtime
- **Network:** Optional (for real connectors)

---

## 🐛 Troubleshooting

### Import Errors:
```bash
# Make sure you're in the AMOS-code directory
cd /Users/nguyenxuanlinh/Documents/Trang\ Phan/Downloads/AMOS-code
python run_amos.py
```

### Test Failures:
```bash
# Run quick tests first
python test_amos.py --quick

# Check specific module
python amos_v4_runtime.py  # Should run without errors
```

### No Output:
```bash
# Check Python version
python --version  # Should be 3.8+

# Run with verbose
python amos_master_controller.py --version operational --demo
```

---

## 🎯 Success Metrics

**AMOS is working when:**
- ✅ `python test_amos.py` passes all tests
- ✅ `python amos_scenario_demo.py` shows portfolio allocation
- ✅ `python run_amos.py` runs operational cycle
- ✅ Identity drift stays below 0.3
- ✅ Survival constraints are met

---

## 📚 Further Reading

- `README_AMOS.md` - Complete architecture documentation
- Individual module docstrings - API details
- `amos_scenario_demo.py` - Practical examples

---

## 🏆 Summary

**AMOS v1-v5 Complete Architecture:**
- 16 files, ~10,000 lines
- Production-ready cognitive organism
- Survives AND compounds under real-world constraints
- Tested and operational

**Run it now:**
```bash
python amos_scenario_demo.py
```

---

*Built: April 2025*  
*Status: Production Ready*  
*Architecture: Complete*
