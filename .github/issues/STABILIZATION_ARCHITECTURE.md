# AMOS Brain Stabilization Architecture v1.0

## Executive Summary

Before feature work continues, the brain needs a **self-healing core**. This document defines the phased approach to achieve a coherent, inspectable, and self-correcting intelligence layer.

**Core Principle**: Do not ask the brain to "fix itself" while it has no stable self-model. First give it: one identity, one runtime path, one import graph, one build truth, one diagnostic interface.

---

## Phase 0: Stop Further Damage

### P0-1: Freeze Feature Merges Until Canonical Runtime is Defined

**Problem**: The repo has multiple conflicting runtime contracts:
- Source-tree scripts (48+ root-level .py files)
- Package entrypoints (6 console scripts, some duplicates)
- CI smoke imports (test individual files)
- Docker startup (uses `amos-brain` entrypoint)
- Legacy Make targets (if any)

**Fix**:
1. Block new feature PRs except stabilization work
2. Define one canonical contract:
   - Either `installable library` (import amos_brain)
   - Or `deployable app` (amos-brain CLI)
3. Mark all others as legacy until removed

**Done When**:
- One document defines the canonical runtime/import/build path
- CI enforces only that path

---

### P0-2: Add "Brain Health" Gate That Fails on Structural Drift

**Problem**: The repo can look green while core assumptions are broken.

**Fix**: Create required CI job `brain-health` that checks:

| Check | Description | Failure Mode |
|-------|-------------|--------------|
| Wheel Install | Built wheel installs in fresh venv | Package metadata broken |
| Public Imports | `import amos_brain` works without sys.path hacks | Package structure broken |
| Entrypoints | Console scripts execute from outside repo root | Entrypoint misconfigured |
| Docker Startup | Container uses same canonical module path | Docker/Package drift |
| CI Alignment | CI imports match published package contents | CI testing wrong surface |
| No Root Scripts | No execution requires root-level .py files | Legacy pattern persists |

**Done When**:
- `brain-health` is required on main
- Any contract drift fails PRs immediately

---

## Phase 1: Stabilize the Brain's Nervous System

### P1-1: Remove All Path-Hack Cognition

**Problem**: `sys.path.insert(...)` is compensating for broken package structure.

**Fix**:
1. Remove every runtime `sys.path.insert(...)`
2. Move all executable logic into package modules
3. Change imports to absolute package imports only

**Current State**: Ruff E402 exceptions exist for many files:
- `amos_*.py`, `backend/**/*.py`, `clawspring/**/*.py`, `_AMOS_BRAIN/**/*.py`

**Done When**:
- `grep -r "sys.path.insert" --include="*.py" .` finds only fix scripts
- Ruff no longer needs E402 exceptions for production code

---

### P1-2: Collapse to One Canonical Entrypoint Surface

**Problem**: The brain is "thinking through five mouths."

**Current Entrypoints**:
```toml
[project.scripts]
amos-brain = "amos_brain.cli:main"      # Keep this
amos-cli = "amos_brain.cli:main"         # REMOVE (duplicate)
amos-launcher = "amos_brain.launcher:main"  # REMOVE (subprocess spaghetti)
amos-tutorial = "amos_brain.tutorial:main"  # MERGE into cli
amos-cookbook = "amos_brain.examples.cookbook_runner:main"  # MERGE into cli
amosl = "amosl.cli:main"                 # SEPARATE package
```

**Fix**: Choose one:
- `python -m amos_brain` (module execution)
- `amos-brain` (console script)
- `amos-brain-cli` (explicit CLI name)

Make all others wrappers or remove them.

**Done When**:
- README shows one primary command
- Docker, CI, and local usage all call the same path
- Launcher no longer shells out to raw filenames

---

### P1-3: Separate Core Brain from Body/Organs

**Problem**: Library logic, backend runtime, infra, dashboards, and ops content are mixed.

**Current Package Structure**:
```toml
[tool.setuptools.packages.find]
include = [
    "amos_brain", "amos_brain.*",
    "amosl", "amosl.*",
    "amos_model_fabric", "amos_model_fabric.*",
    "amos_self_evolution",
    "amos_platform",
    "multi_agent",
    "skill",
    "search",
    "streaming",
    "memory",
    "analytics",
    "repo_doctor", "repo_doctor.*",
    "clawspring", "clawspring.*",
]
exclude = ["tests", "tests.*", "server", "server.*", "backend", "backend.*"]
```

**Fix**: Keep only brain/core package code in the package repo. Move app/server/deploy/ops elsewhere.

**Done When**:
- `pyproject.toml` describes exactly the code shipped
- Wheel contents are predictable
- No backend-only dependency is required for core imports

---

## Phase 2: Maximize Brain Function

### P2-1: Build a Self-Model of the Repo

**Problem**: The brain cannot fix itself if it cannot describe itself.

**Fix**: Generate machine-readable contract file `amos_brain_contract.json`:

```json
{
  "contract_version": "1.0.0",
  "package": {
    "name": "amos-brain",
    "version": "14.0.0",
    "canonical_module": "amos_brain",
    "canonical_entrypoint": "amos_brain.cli:main"
  },
  "public_api": {
    "modules": ["amos_brain", "amos_brain.api_contracts"],
    "entrypoints": ["amos-brain"],
    "exports": ["get_brain", "process_task", "GlobalLaws"]
  },
  "dependencies": {
    "required": ["pydantic>=2.0.0", "numpy>=1.24.0"],
    "optional": {
      "server": ["fastapi>=0.104.0"],
      "database": ["sqlalchemy[asyncio]>=2.0.0"]
    }
  },
  "runtime": {
    "python_versions": ["3.10", "3.11", "3.12", "3.13"],
    "health_check": "amos_brain.health:check"
  },
  "forbidden_patterns": [
    "sys.path.insert",
    "except:",
    "datetime.utcnow()"
  ],
  "allowed_root_files": ["pyproject.toml", "README.md", "Dockerfile"]
}
```

Use CI to compare actual repo state against this contract.

**Done When**:
- PR that adds undeclared entrypoint/package/dependency fails automatically

---

### P2-2: Add Self-Diagnosis Commands

Add package-native commands:

```bash
amos-brain doctor
amos-brain doctor --imports     # Check import graph
amos-brain doctor --build       # Check package build
amos-brain doctor --entrypoints # Check console scripts
amos-brain doctor --contract    # Validate against contract
```

These test:
- Import graph (no circular deps, all public imports work)
- Missing modules
- Packaging contents
- Broken console scripts
- Version mismatches
- Dependency mismatches
- Stale docs references

**Done When**:
- Maintainers can detect breakage locally before CI

---

### P2-3: Add Self-Repair Suggestions (Not Autonomous Mutation)

**Problem**: Uncontrolled self-editing is dangerous.

**Fix**: `doctor` outputs bounded repair proposals:

```text
Issue: console script points to repo-root module
Files: pyproject.toml, amos_brain_launcher.py
Fix: move launcher into amos_brain/launcher.py and repoint entrypoint
Confidence: high
Suggested codemod: entrypoint_to_package
```

**Done When**:
- System can explain its own failures precisely

---

## Phase 3: Let the Brain Fix Itself Safely

### P3-1: Add Codemod-Based Repair Tools

Only after stabilization.

Create internal repair commands for deterministic fixes:

| Codemod | Description |
|---------|-------------|
| `entrypoint_to_package` | Rewrite repo-root entrypoints to package entrypoints |
| `absolute_imports` | Replace relative imports with absolute imports |
| `remove_path_hacks` | Remove deprecated launcher patterns |
| `readme_sync` | Update README commands from legacy to canonical |
| `ci_alignment` | Sync CI targets with package metadata |

These are **explicit tools**, not free-form AI edits.

**Done When**:
- Common structural issues can be repaired repeatably

---

### P3-2: Add Contract-Driven Refactor Mode

Refactors checked against:
- Package contract
- Public API contract
- Build contract
- CLI contract

No refactor accepted unless all four still hold.

**Done When**:
- Brain can evolve without identity drift

---

## Exact First 10 Issues to Open

1. **Define canonical AMOS runtime contract** (P0-1)
2. **Create required `brain-health` CI job** (P0-2)
3. **Remove all runtime `sys.path.insert(...)` usage** (P1-1)
4. **Move all published entrypoints into package modules** (P1-2)
5. **Replace launcher subprocess filename execution with module/direct dispatch** (P1-2)
6. **Align CI smoke tests with published package surface** (P0-2)
7. **Make required lint/type/security checks blocking** (P0-2)
8. **Fail release when package publish fails** (P0-2)
9. **Create machine-readable package/runtime contract file** (P2-1)
10. **Add `amos-brain doctor` self-diagnosis command** (P2-2)

---

## Success Sequence

```
canonical contract
    ↓
brain-health CI
    ↓
remove path hacks
    ↓
unify entrypoints
    ↓
align package/CI/Docker
    ↓
add doctor
    ↓
add codemod repair tools
    ↓
FEATURE WORK RESUMES
```

**The brain will be ready to fix itself when it has one stable identity.**
