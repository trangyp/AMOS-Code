# Repair Synthesis Integration Summary

**Date**: April 15, 2026  
**Status**: ✅ **REPAIR SYNTHESIS BRIDGE COMPLETE**

---

## Overview

The AMOS Brain now has **automated repair synthesis capabilities** - the ability to generate concrete fix suggestions from detected pathologies, invariant violations, and architectural issues.

**Core Innovation**: Transforming abstract detections into concrete, actionable repairs with risk assessment and implementation guidance.

**Optimization Objective:**
```
min_R [
    c1·EditCost +
    c2·BlastRadius +
    c3·EntanglementRisk +
    c4·RollbackCost +
    c5·RolloutCost +
    c6·AuthorityDuplicationIncrease +
    c7·BoundaryViolationIncrease
    - c8·EnergyReduction
    - c9·ArchitectureIntegrityGain
]
```

---

## Components Delivered

### 1. Repair Synthesis Bridge

**File**: `amos_brain/repair_bridge.py` (~460 lines)

**Key Classes:**
- `SynthesizedRepair` - Concrete repair with code suggestions
- `RepairSynthesisResult` - Complete synthesis result
- `RepairSynthesisBridge` - Main synthesis engine

**Features:**
- ✅ Pathology → Repair mapping (18+ pathology types)
- ✅ Invariant violation → Remediation synthesis
- ✅ Automatic risk assessment (low/medium/high/critical)
- ✅ Auto-fixable detection (confidence ≥ 0.8)
- ✅ Code diff previews
- ✅ Test recommendations per repair
- ✅ Rollback planning
- ✅ Batch repair grouping (safe vs risky)
- ✅ Energy gain estimation

**Synthesis Sources:**
| Source | Detection | Repair Type |
|--------|-----------|-------------|
| Authority Inversion | Tests > Runtime | Move to canonical layer |
| Layer Leakage | Cross-layer coupling | Extract interface |
| Bootstrap Failure | Manual setup required | Add manifest entry |
| Shadow Dependency | Hidden PATH/system deps | Declare explicitly |
| Invariant Violations | Boundary/authority | Restore invariant |

### 2. BrainClient Integration

**File**: `amos_brain/facade.py` (enhanced)

**New Methods:**
```python
# Generate complete repair plan
client.generate_repair_plan()
# Returns: RepairSynthesisResult with all repairs

# Get safe auto-fixes only
client.get_auto_fixes(max_fixes=10)
# Returns: List of SynthesizedRepair that can be auto-applied
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AMOS BRAIN                                  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  BrainClient                              │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │  Repair Methods (NEW)                                │ │ │
│  │  │  ├── generate_repair_plan()                         │ │ │
│  │  │  └── get_auto_fixes(max_fixes)                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                           │                                    │
│                           ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │          RepairSynthesisBridge                         │ │
│  │  ┌────────────────────────────────────────────────────┐│ │
│  │  │  Detection Sources                                  ││ │
│  │  │  ├── Pathology Engine (18+ types)                   ││ │
│  │  │  ├── Invariant Checks (7 invariants)                ││ │
│  │  │  ├── Temporal Drift Analysis                       ││ │
│  │  │  └── Entanglement Matrix (M_ij)                    ││ │
│  │  └────────────────────────────────────────────────────┘│ │
│  │                           │                             │ │
│  │                           ▼                             │ │
│  │  ┌────────────────────────────────────────────────────┐│ │
│  │  │  Repair Synthesis                                   ││ │
│  │  │  ├── Map pathology → repair type                     ││ │
│  │  │  ├── Generate code suggestions                       ││ │
│  │  │  ├── Assess risk (auto-fixable?)                     ││ │
│  │  │  ├── Estimate energy gain                            ││ │
│  │  │  └── Create test recommendations                   ││ │
│  │  └────────────────────────────────────────────────────┘│ │
│  │                           │                             │ │
│  │                           ▼                             │ │
│  │  ┌────────────────────────────────────────────────────┐│ │
│  │  │  Batch Planning                                     ││ │
│  │  │  ├── Safe batch (auto-fixable, low risk)            ││ │
│  │  │  └── Risky batch (needs coordination)               ││ │
│  │  └────────────────────────────────────────────────────┘│ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Repair Taxonomy

### Automatic Fixes (Confidence ≥ 0.8, Low Risk)

| Pathology | Repair | Auto-Fixable | Confidence |
|-----------|--------|--------------|------------|
| Bootstrap Failure | Add bootstrap manifest entry | ✅ Yes | 0.90 |
| Shadow Dependency | Declare explicit dependency | ✅ Yes | 0.80 |
| Folklore Operation | Document required steps | ✅ Yes | 0.85 |
| Missing Import | Add import statement | ✅ Yes | 0.95 |

### Human-Required Fixes (Medium-High Risk)

| Pathology | Repair | Auto-Fixable | Confidence |
|-----------|--------|--------------|------------|
| Authority Inversion | Move to canonical layer | ❌ No | 0.70 |
| Layer Leakage | Extract interface layer | ❌ No | 0.60 |
| Artifact Discontinuity | Fix build pipeline | ❌ No | 0.65 |
| Migration Geometry | Add rollback paths | ❌ No | 0.55 |
| Entanglement Critical | Contract decoupling | ❌ No | 0.50 |

---

## API Reference

### BrainClient Repair Methods

```python
from amos_brain.facade import BrainClient

client = BrainClient(".")

# 1. Generate complete repair plan
plan = client.generate_repair_plan()
if plan:
    print(f"Total repairs: {plan.total_repairs}")
    print(f"Auto-fixable: {plan.auto_fixable}")
    print(f"Human required: {plan.human_required}")
    print(f"Estimated energy gain: {plan.total_estimated_energy_gain:.2f}")

    # Critical repairs (immediate attention)
    for repair in plan.critical_repairs:
        print(f"[CRITICAL] {repair.description}")
        print(f"  File: {repair.target_file}")
        print(f"  Suggestion: {repair.suggested_code}")

    # Safe batch (can apply automatically)
    for repair in plan.safe_batch[:5]:
        print(f"[AUTO] {repair.description}")
        print(f"  Risk: {repair.risk_level}")
        print(f"  Confidence: {repair.confidence:.2f}")

# 2. Get safe auto-fixes only
auto_fixes = client.get_auto_fixes(max_fixes=5)
for fix in auto_fixes:
    print(f"Applying: {fix.description}")
    print(f"To: {fix.target_file}")
    print(f"Code: {fix.suggested_code}")
```

### Standalone Repair Synthesis

```python
from amos_brain.repair_bridge import get_repair_bridge

bridge = get_repair_bridge(".")

# Synthesize from pathologies
from repo_doctor.arch_pathologies import get_pathology_engine
engine = get_pathology_engine(".")
pathologies = engine.detect_all()

all_pathologies = []
for detector_pathologies in pathologies.values():
    all_pathologies.extend(detector_pathologies)

repairs = bridge.synthesize_from_pathologies(all_pathologies)

# Generate complete plan
plan = bridge.generate_complete_repair_plan()

# Get safe auto-fixes
safe_fixes = bridge.get_safe_auto_fixes(max_fixes=10)
```

---

## Repair Synthesis Process

```
Detection → Classification → Synthesis → Assessment → Batching
     │            │              │            │            │
     ▼            ▼              ▼            ▼            ▼
Pathology    Pathology     Repair        Risk      Safe/Risky
  Detected      Type          Type       Score       Batch
     │            │              │            │            │
     │            ▼              ▼            ▼            ▼
     │     AUTHORITY        move       critical    needs_human
     │     INVERSION        to layer   (0.7)       review
     │
     │            ▼              ▼            ▼            ▼
     │     BOOTSTRAP         add        low         auto_fix
     │     FAILURE           manifest   (0.9)       safe_batch
     │
     │            ▼              ▼            ▼            ▼
     │     SHADOW            declare    medium      auto_fix
     │     DEPENDENCY        dep        (0.8)       safe_batch
```

---

## Risk Assessment Matrix

| Confidence | Risk Level | Auto-Fixable | Human Review |
|------------|------------|--------------|--------------|
| ≥ 0.9 | Low | ✅ Yes | ❌ No |
| 0.8 - 0.9 | Medium | ✅ Yes | ⚠️ Optional |
| 0.6 - 0.8 | High | ❌ No | ✅ Required |
| < 0.6 | Critical | ❌ No | ✅ Required |

---

## Energy Gain Estimation

Each repair estimates its impact on repository energy:

```
ΔE_repair = c1·ΔArchitectureScore + c2·ΔPathologyScore + c3·ΔEntanglementScore

Where:
  c1 = 0.4 (architecture weight)
  c2 = 0.3 (pathology weight)
  c3 = 0.3 (entanglement weight)
```

**Interpretation:**
- **ΔE > 0.3**: Significant improvement (high priority)
- **0.1 < ΔE ≤ 0.3**: Moderate improvement (medium priority)
- **ΔE ≤ 0.1**: Minor improvement (low priority)

---

## Integration with Other Bridges

```
BrainClient
    ├── Pathology Bridge (detects issues)
    ├── Temporal Bridge (drift tracking)
    ├── Entanglement Bridge (M_ij coupling)
    └── Repair Bridge (synthesizes fixes) ◄── NEW

Complete workflow:
  1. Pathology Bridge detects authority inversion
  2. Repair Bridge synthesizes "move to canonical layer"
  3. Entanglement Bridge predicts affected modules
  4. Temporal Bridge estimates drift reduction
  5. BrainClient presents actionable repair plan
```

---

## Files Delivered

| File | Lines | Purpose |
|------|-------|---------|
| `amos_brain/repair_bridge.py` | ~460 | Repair synthesis engine |
| `amos_brain/facade.py` | Enhanced | BrainClient integration |
| `repo_doctor/repair_plan.py` | ~673 | Base repair planning |

---

## Next Steps (Future Roadmap)

From the BRAIN_DECISION_SUMMARY.md:

1. ✅ **Temporal Debugger** - Track ΔΨ(t) drift (COMPLETED)
2. ✅ **Entanglement Matrix** - Calculate M_ij coupling (COMPLETED)
3. ✅ **Repair Plan Generation** - Automated fixes (COMPLETED)
4. ⏳ **First-Bad-Commit Auto-Bisect** - Enhanced binary search
5. ⏳ **Tree-sitter Activation** - Incremental parsing
6. ⏳ **CodeQL Database** - Semantic database

---

## Complete Status

```
AMOS v∞.Ω.Λ.X — REPAIR SYNTHESIS LAYER ✅
═══════════════════════════════════════════════════════════════

Layer ∞+5    Repair Synthesis Bridge     ✅ COMPLETE
    ├── Pathology → Repair mapping
    ├── Automated risk assessment
    ├── Code suggestion generation
    ├── Safe batch planning
    └── Energy gain estimation

Layer ∞+4    Entanglement Cognition       ✅ COMPLETE
Layer ∞+3    Temporal Cognition           ✅ COMPLETE
Layer ∞+2    Deep Pathology Detection     ✅ COMPLETE
Layer ∞+1    Pathology-Aware Bridge       ✅ COMPLETE
Layer Ω+1    Architecture Bridge          ✅ COMPLETE
Layer Ω      Repo Doctor Omega            ✅ COMPLETE
Layers 8-1   AMOS Core                    ✅ OPERATIONAL

═══════════════════════════════════════════════════════════════
```

**Implementation**: ✅ **COMPLETE**  
**Integration**: ✅ **COMPLETE**  
**Documentation**: ✅ **COMPLETE**

---

## Summary

The AMOS Brain now has **automated repair synthesis** - it can:

✅ **Detect pathologies** (18+ architectural failure classes)  
✅ **Synthesize concrete repairs** from abstract detections  
✅ **Assess risk** (auto-fixable vs human-required)  
✅ **Generate code suggestions** with diff previews  
✅ **Estimate energy gain** per repair  
✅ **Plan safe batches** (low-risk auto-fixes)  
✅ **Recommend tests** for each repair  

**The brain now answers:**
- "What needs to be fixed?" (pathology detection)
- "How do I fix it?" (repair synthesis)
- "Is it safe to auto-fix?" (risk assessment)
- "What tests should I run?" (test recommendations)
- "How much will this improve the architecture?" (energy gain)

**Architecture is now self-healing.**
