# AMOS Stabilization Status

**Date:** 2026-04-20  
**Target:** One coherent brain with unified contracts

## Current State

### ✅ Completed (Aligned)

| Component | Status | Notes |
|-----------|--------|-------|
| `pyproject.toml` | ✅ | Package `amos-brain`, entrypoints correct |
| `amos_brain_launcher.py` | ✅ | Now a deprecation shim |
| `Dockerfile` | ✅ | Uses `pip install`, no source copy |
| `Makefile` | ✅ | Uses `amos-brain` commands |
| `amos_brain/cli.py` | ✅ | Has `doctor` command |
| `amos_brain/doctor.py` | ✅ | Self-diagnosis implemented |
| `amos_brain_contract.json` | ✅ | Generated and versioned |
| `docs/runtime-contract.md` | ✅ | Documentation created |
| `README.MD` quick-start | ✅ | Updated to use `amos-brain` |

### ⚠️ In Progress (Partial)

| Component | Status | Action Needed |
|-----------|--------|---------------|
| CI workflow | ⚠️ | Tests source tree, not wheel |
| `sys.path.insert` | ⚠️ | 461 matches across 321 files |
| Backend imports | ⚠️ | Some still use path hacks |

### ❌ Not Started

| Component | Status | Action Needed |
|-----------|--------|---------------|
| `|| true` in CI | ❌ | Remove failure suppression |
| Release workflow | ❌ | Fail on PyPI upload failure |
| `brain-health` CI job | ❌ | Add contract validation gate |

## Stabilization Issues

### P0 (Critical)

1. **Issue 1:** Define single canonical runtime contract ✅ DONE
   - Runtime contract documented in `docs/runtime-contract.md`
   - Contract file: `amos_brain_contract.json`

2. **Issue 2:** Move published entrypoints into package modules ✅ DONE
   - Entrypoints already in `pyproject.toml` point to `amos_brain.cli:main`

3. **Issue 3:** Remove runtime `sys.path.insert` hacks ⚠️ IN PROGRESS
   - 461 matches across 321 files
   - Prioritize `amos_brain/` package files first

4. **Issue 4:** Replace launcher subprocess filename execution ✅ DONE
   - `amos_brain_launcher.py` now a shim

5. **Issue 5:** Make CI test the built package ❌ NOT STARTED
   - Current CI tests source tree
   - Need to build wheel and test installed package

6. **Issue 6:** Remove `|| true` from required CI checks ❌ NOT STARTED
   - Review `.github/workflows/*.yml`

7. **Issue 7:** Fail release when package publish fails ❌ NOT STARTED
   - Review `.github/workflows/release.yml`

### P1 (High)

8. **Issue 8:** Align Docker and Make with package contract ✅ DONE
   - Both already use `amos-brain` commands

9. **Issue 9:** Split core package dependencies from app/runtime ⚠️ PARTIAL
   - `pyproject.toml` has extras, but core deps may still be too broad

10. **Issue 10:** Create `brain-health` CI job ❌ NOT STARTED
    - Job should validate contract file
    - Fail on drift from canonical state

### P2 (Medium)

11. **Issue 11:** Add `amos-brain doctor` self-diagnosis ✅ DONE
    - Already implemented with all subchecks

12. **Issue 12:** Remove source-tree execution from README ✅ DONE
    - README updated to use `amos-brain` commands

## Next Steps

1. **Immediate:** Fix remaining `sys.path.insert` in `amos_brain/` package
2. **Short-term:** Update CI to build and test wheel
3. **Medium-term:** Add `brain-health` required CI job
4. **Long-term:** Systematically remove path hacks from entire codebase

## Verification Commands

```bash
# Validate contract
amos-brain doctor --contract

# Check all diagnostics
amos-brain doctor -v

# Build and verify wheel
python -m build
pip install dist/amos_brain-*.whl
amos-brain doctor
```
