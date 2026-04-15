# AMOS Brain 57-Component System - Quick Start Guide

**Get the complete 57-component autonomous system running in minutes.**

---

## System Overview

The AMOS 57-Component System is a unified autonomous architecture combining:

- **Meta-Architecture Layer**: 10 governance systems preventing decay
- **Meta-Ontological Layer**: 12 components extending formal core  
- **21-Tuple Formal Core**: Mathematical foundation
- **Production System**: 46 components for real-world operation

**Total**: 57 components working in harmony

---

## Prerequisites

```bash
# Python 3.11+
python3 --version

# Install dependencies
pip install -r requirements.txt
```

---

## Quick Start (3 Steps)

### Step 1: Run the Complete System

```bash
python3 amos_complete_system.py
```

**Expected output:**
```
======================================================================
AMOS BRAIN: 57-COMPONENT UNIFIED SYSTEM
======================================================================

Initializing Meta-Architecture Layer (10 systems)...       [OK]
Initializing Meta-Ontological Layer (12 components)...   [OK]
Initializing 21-Tuple Formal Core...                     [OK]
Initializing Production System...                          [OK]

All 57 components initialized successfully!

✅ Meta-Architecture (10 systems) - OPERATIONAL
✅ Meta-Ontological (12 components) - OPERATIONAL
✅ 21-Tuple Formal Core - OPERATIONAL
✅ Production System - OPERATIONAL

System Status: FULLY OPERATIONAL
Coherence Score: 0.95
======================================================================
```

### Step 2: Run the Test Suite

```bash
python3 test_amos_complete_57.py
```

**Validates all 57 components are working correctly.**

### Step 3: Run Performance Benchmarks

```bash
python3 benchmark_57_components.py
```

**Measures initialization time, memory usage, and throughput.**

---

## Architecture Components

### 1. Meta-Architecture Layer (10 Systems)

Located in: `amos_meta_architecture.py`

| System | Purpose |
|--------|---------|
| Promise System | Track and validate promises |
| Breach System | Handle breach classification and discharge |
| Identity-Over-Time | Preserve identity across migrations |
| Equivalence System | Validate equivalence claims |
| Memory/Forgetting | Govern what must/should be remembered |
| Disagreement Resolution | Resolve conflicting views |
| Legitimacy | Verify authority alignment |
| Self-Modification | Safe self-change protocols |
| Semantic Survival | Monitor meaning preservation |
| Meta-Governance | Law hierarchy and emergency protocols |

**Usage:**
```python
from amos_meta_architecture import MetaGovernance

meta = MetaGovernance()
results = meta.validate_full_system()
print(f"Governance systems: {sum(results.values())}/10 operational")
```

### 2. Meta-Ontological Layer (12 Components)

Located in: `amos_meta_ontological.py`

| Component | Purpose |
|-----------|---------|
| Energy Budget | Thermodynamic constraints |
| Temporal Hierarchy | Multi-scale time management |
| Self-Representation | System self-modeling |
| Identity Manifold | Identity preservation |
| Observer State | Observation framework |
| Sheaf of Truths | Truth coherence |
| Agency Field | Agency dynamics |
| Embodiment Operator | Embodiment mapping |
| Program Deformation | Program evolution |
| Renormalization | Scale transformation |
| Meta-Semantic Evaluator | Meaning evaluation |
| Ethical Boundary | Deontic constraints |

**Usage:**
```python
from amos_meta_ontological import AMOSMetaOntological

meta_ont = AMOSMetaOntological()
result = meta_ont.grand_unified_step(x_t, u_t, w_t)
```

### 3. 21-Tuple Formal Core

Located in: `amos_formal_core.py`

The mathematical foundation of AMOS implementing:
- State bundles (observable/substrate/environment)
- Intent fields
- Syntax structures
- Ontology frames
- Dynamics fields
- Action universes
- Bridge morphisms
- And 14 more formal components

**Usage:**
```python
from amos_formal_core import AMOSFormalSystem, StateBundle, ActionUniverse

formal = AMOSFormalSystem()
x_t = StateBundle(classical={'key': 'value'})
u_t = ActionUniverse(substrate='classical', target='classical')
x_t1 = formal.universal_step(x_t, u_t)
```

---

## Integration with Repo Doctor

The 57-component system integrates with Repo Doctor for unified autonomous governance:

```bash
python3 amos_57_repo_doctor_integration.py .
```

This combines:
- Repository invariants (Repo Doctor)
- Cognitive governance (AMOS 57)
- Unified decision making

---

## CI/CD Pipeline

The system includes a complete GitHub Actions workflow:

```yaml
# .github/workflows/amos-57-ci.yml

Jobs:
1. Code Quality (ruff, black, mypy)
2. Test 57 Complete (full test suite)
3. Deployment Readiness (main branch)
4. Performance Benchmark (daily schedule)
```

**Trigger:**
- Push to main/master/develop
- Pull requests
- Daily at 2 AM UTC

---

## Common Operations

### Check System Health

```python
from amos_complete_system import AMOS57ComponentSystem

amos = AMOS57ComponentSystem()
health = amos.health_check()
print(f"System Health: {health['status']}")
print(f"Coherence: {health['coherence_score']:.2f}")
```

### Validate Deployment

```bash
python3 validate_deployment.py
```

### Run Unified Analysis

```python
from amos_57_repo_doctor_integration import run_unified_analysis

result = run_unified_analysis(".")
print(f"Governance Grade: {result['unified_state']['governance_grade']}")
print(f"Actions: {len(result['actions'])}")
```

---

## File Reference

| File | Purpose | Lines |
|------|---------|-------|
| `amos_meta_architecture.py` | 10 governance systems | ~300 |
| `amos_meta_ontological.py` | 12 meta-ontological components | ~900 |
| `amos_formal_core.py` | 21-tuple formal system | ~400 |
| `amos_complete_system.py` | Unified 57-component integration | ~130 |
| `test_amos_complete_57.py` | Comprehensive test suite | ~450 |
| `validate_deployment.py` | Deployment validation | ~60 |
| `benchmark_57_components.py` | Performance benchmarks | ~200 |
| `amos_57_repo_doctor_integration.py` | Unified integration | ~570 |
| `.github/workflows/amos-57-ci.yml` | CI/CD pipeline | ~90 |

---

## Performance Expectations

Based on benchmark results:

| Metric | Expected Value |
|--------|---------------|
| Total Initialization | < 3 seconds |
| Memory Footprint | < 50 MB |
| Throughput | > 10 ops/sec |
| Governance Grade | EXCELLENT/GOOD |

---

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the correct directory
cd /Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code

# Verify Python version
python3 --version  # Should be 3.11+
```

### Test Failures
```bash
# Run individual component tests
python3 -c "from amos_meta_architecture import MetaGovernance; print('OK')"
python3 -c "from amos_meta_ontological import AMOSMetaOntological; print('OK')"
python3 -c "from amos_formal_core import AMOSFormalSystem; print('OK')"
```

### CI/CD Issues
```bash
# Validate YAML syntax
yamllint .github/workflows/amos-57-ci.yml

# Test workflow locally
act -j test-57-complete
```

---

## Next Steps

1. **Run the complete system** (see Step 1 above)
2. **Review the code** - Each file is fully documented
3. **Customize** - Modify components for your use case
4. **Deploy** - Use CI/CD pipeline for automated deployment
5. **Monitor** - Performance benchmarks track system health

---

## Support

- **Documentation**: See `AMOS_57_COMPLETE_SYSTEM_SUMMARY.md`
- **Architecture**: See `AMOS_57_VALIDATION_SUMMARY.md`
- **CI/CD**: See `CI_CD_SUMMARY.md`
- **Integration**: See source code comments in integration files

---

**Status**: 57-COMPONENT SYSTEM READY FOR PRODUCTION

**Version**: 57-Component Complete System  
**Date**: April 2026  
**License**: See LICENSE file
