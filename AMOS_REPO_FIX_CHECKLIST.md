# AMOS Repository Fix Checklist

**Generated**: April 2026  
**Priority Order**: Critical → High → Medium → Low  
**Estimated Effort**: 2-3 days focused work

---

## 🔴 CRITICAL - Fix First (Blocks Installation/Usage)

### 1. License Metadata Conflict
**Issue**: README implies MIT, pyproject.toml says Apache-2.0  
**Action**: Choose one license and make all files consistent

| File | Current | Change To |
|------|---------|-----------|
| `pyproject.toml:10` | `license = {text = "Apache-2.0"}` | Decide: MIT **OR** Apache-2.0 |
| `README.md` | No explicit license statement | Add license badge + statement |
| `LICENSE` | Apache-2.0 text | Keep or replace with MIT |

**Decision Required**: Pick ONE:
- [ ] **Option A**: Apache-2.0 (current file, keep pyproject.toml, update README)
- [ ] **Option B**: MIT (replace LICENSE file, update pyproject.toml, update README)

---

### 2. Fix Brittle Console Scripts
**Issue**: `amos_brain_launcher.py` shells out to raw filenames that won't exist after pip install

| File | Line | Current | Fix |
|------|------|---------|-----|
| `amos_brain_launcher.py:74` | `subprocess.run([sys.executable, "amos_brain_tutorial.py"])` | Use `python -m amos_brain.tutorial` or entrypoint |
| `amos_brain_launcher.py:82` | `subprocess.run([sys.executable, os.path.join("clawspring", "clawspring.py"), "--amos"])` | Use `amos-claws` entrypoint |
| `amos_brain_launcher.py:90` | `subprocess.run([sys.executable, "-m", "pytest", "tests/test_amos_brain.py", "-v"])` | Use `pytest --pyargs amos_brain` |
| `amos_brain_launcher.py:105` | `subprocess.run([sys.executable, "demo_cookbook.py"])` | Move to `amos_brain.examples` module |

**Implementation**:
```python
# Instead of:
subprocess.run([sys.executable, "amos_brain_tutorial.py"])

# Use module execution:
subprocess.run([sys.executable, "-m", "amos_brain.tutorial"])
```

---

### 3. Add Missing Package Directories to pyproject.toml
**Issue**: Many Python directories not included in package discovery

**Current** (`pyproject.toml:96`):
```toml
include = ["amos_brain", "amos_brain.*", "amosl", "amosl.*", "amos_model_fabric", "amos_model_fabric.*"]
```

**Add Missing Directories**:
```toml
include = [
    "amos_brain", "amos_brain.*",
    "amosl", "amosl.*",
    "amos_model_fabric", "amos_model_fabric.*",
    "amos_self_evolution",          # ← ADD
    "amos_platform",                # ← ADD
    "clawspring", "clawspring.*",   # ← ADD (if part of this package)
    "multi_agent",                  # ← ADD
    "skill",                        # ← ADD
    "search",                       # ← ADD
    "streaming",                    # ← ADD
    "memory",                       # ← ADD
    "analytics",                    # ← ADD
    "repo_doctor", "repo_doctor.*", # ← ADD
]
```

---

### 4. Fix Dependencies in pyproject.toml
**Issue**: `dependencies = []` is nearly empty, but code clearly imports FastAPI, SQLAlchemy, etc.

**Current** (`pyproject.toml:41-44`):
```toml
dependencies = [
    "pydantic>=2.0.0",
    "typing-extensions>=4.0.0",
]
```

**Add Core Dependencies** (based on actual imports found):
```toml
dependencies = [
    "pydantic>=2.0.0",
    "typing-extensions>=4.0.0",
    # Core runtime
    "structlog>=23.0.0",
    "prometheus-client>=0.19.0",
    # Optional but commonly used
    "numpy>=1.24.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
server = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.29.0",
    "redis>=5.0.0",
    "celery>=5.3.0",
]
database = [
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.29.0",
    "alembic>=1.12.0",
    "pgvector>=0.2.0",
]
security = [
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "slowapi>=0.1.0",
]
ml = [
    "torch>=2.0.0",
    "transformers>=4.35.0",
    "sentence-transformers>=2.2.0",
]
clawspring = ["clawspring"]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "coverage[toml]>=7.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "pyright>=1.1.350",
    "black>=23.0.0",
    "pre-commit>=3.5.0",
]
```

---

## 🟠 HIGH - Fix Before Release

### 5. Server/Library Boundary - Move Server Files
**Issue**: AMOS-Code should be library-only, but contains servers

**Files to Move to AMOS-Consulting (DO NOT DELETE - preserve git history)**:

| File | Destination in AMOS-Consulting | Notes |
|------|-------------------------------|-------|
| `amos_fastapi_gateway.py` | `amos_platform/gateway/fastapi.py` | Full FastAPI server |
| `amos_api_gateway.py` | `amos_platform/gateway/api.py` | API gateway implementation |
| `amos_api_server.py` | `amos_platform/server/api_server.py` | API server |
| `amos_api_enhanced.py` | `amos_platform/gateway/enhanced.py` | Enhanced API |
| `amos_api_hub.py` | `amos_platform/hub/api_hub.py` | API hub |
| `amos_production_runtime.py` | `amos_platform/runtime/production.py` | Runtime orchestrator |
| `amos_websocket_manager.py` | `amos_platform/websocket/manager.py` | WebSocket handler |
| `backend/` (entire dir) | `amos_platform/backend/` | Full FastAPI backend |

**Migration Strategy** (preserve git history):
```bash
# In AMOS-Code repo - use git filter-branch or git subtree
# Option 1: Git subtree split
mkdir -p ../amos-consulting-migration
git subtree split -P backend -b backend-migration

# Option 2: Manual copy with attribution
cp -r backend/ ../AMOS-Consulting/amos_platform/
cp amos_fastapi_gateway.py ../AMOS-Consulting/amos_platform/gateway/
```

---

### 6. Fix sys.path.insert Hacks
**Issue**: Import path assumptions that break after pip install

**Files Found with sys.path.insert**:
| File | Lines | Context |
|------|-------|---------|
| `fix_sys_path_comprehensive.py` | Multiple | Fix script (ignore) |
| `batch_fix_remaining.py` | 1 | Fix script (ignore) |

**Search for Import Pattern Violations**:
```bash
# Search for manual path manipulation in non-fix files
grep -r "sys.path.insert" --include="*.py" . | grep -v fix_ | grep -v batch_
```

**If Found in Core Files**:
Replace with proper package imports:
```python
# BAD:
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from amos_brain import get_amos_integration

# GOOD:
from amos_brain import get_amos_integration
```

---

### 7. Verify All Packages Have __init__.py
**Issue**: Missing package markers cause import failures

**Check These Directories** (verify __init__.py exists):
```bash
# Core library packages
amos_brain/           # ✓ Has __init__.py
amosl/                # CHECK - verify all subdirs
amos_model_fabric/    # CHECK
amos_self_evolution/  # CHECK
amos_platform/        # CHECK (but moving anyway)
multi_agent/          # CHECK
skill/                # CHECK
search/               # CHECK
streaming/            # CHECK
memory/               # CHECK
analytics/            # CHECK
backend/              # Moving to AMOS-Consulting
```

**Create Missing __init__.py**:
```bash
# For any directory missing __init__.py
touch {package}/__init__.py
```

---

## 🟡 MEDIUM - Polish & Documentation

### 8. Verify SDK Matches OpenAPI Spec
**Issue**: SDK may be out of sync with `AMOS_OPENAPI_SPEC.yaml`

**Check Files**:
| File | Purpose |
|------|---------|
| `sdk/python/amos_sdk/` | Python SDK |
| `sdk/typescript/` | TypeScript SDK (may not exist) |
| `AMOS_OPENAPI_SPEC.yaml` | Source of truth |

**Actions**:
1. [ ] Verify Python SDK endpoints match OpenAPI spec
2. [ ] Generate TypeScript SDK if missing:
   ```bash
   npm install -g openapi-generator-cli
   openapi-generator-cli generate -i AMOS_OPENAPI_SPEC.yaml -g typescript-fetch -o sdk/typescript/
   ```
3. [ ] Add SDK generation to CI/CD

---

### 9. Fix Version Consistency
**Issue**: Documentation mentions conflicting versions

**Current State**:
- `pyproject.toml`: 14.0.0 (correct)
- Audit mentions: 3.05.5 (outdated reference)

**Action**: Update all docs to reflect 14.0.0

| File | Find | Replace |
|------|------|---------|
| Any doc with "3.05.5" | `3.05.5` | `14.0.0` |
| Any doc with "14.0.0" | Verify | Keep as is |

---

### 10. Add CI Checks for Clean Install
**Issue**: No automated verification that `pip install` works

**Add to `.github/workflows/`**:
```yaml
# .github/workflows/install-test.yml
name: Installation Test

on: [push, pull_request]

jobs:
  install-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install package
        run: pip install -e ".[dev]"
      
      - name: Test imports
        run: |
          python -c "import amos_brain; print('amos_brain OK')"
          python -c "import amosl; print('amosl OK')"
          python -c "import amos_model_fabric; print('amos_model_fabric OK')"
      
      - name: Test entry points
        run: |
          amos-brain --help || true
          amos-cli --help || true
```

---

## Implementation Order

### Phase 1: Critical (Day 1)
1. ☐ Fix license conflict (decide MIT vs Apache-2.0)
2. ☐ Fix brittle console scripts
3. ☐ Add missing dependencies to pyproject.toml
4. ☐ Add missing packages to pyproject.toml

### Phase 2: High (Day 2)
5. ☐ Move server files to AMOS-Consulting
6. ☐ Fix any sys.path.insert in core files
7. ☐ Verify/create all __init__.py files

### Phase 3: Medium (Day 3)
8. ☐ Verify/regenerate SDKs
9. ☐ Fix version consistency in docs
10. ☐ Add CI install checks

---

## Verification Commands

```bash
# 1. Clean install test
pip install -e ".[dev]"

# 2. Import test
python -c "import amos_brain; import amosl; import amos_model_fabric; print('All imports OK')"

# 3. Entry point test
amos-brain --help
amos-cli --help

# 4. Build test
python -m build

# 5. Check for server code in library
find . -name "*gateway*.py" -o -name "*server*.py" | grep -v test | grep -v __pycache__

# 6. Verify no sys.path.insert in core
grep -r "sys.path.insert" amos_brain/ amosl/ amos_model_fabric/ 2>/dev/null || echo "No sys.path.insert found in core"
```

---

## Success Criteria

- [ ] `pip install -e .` works on fresh environment
- [ ] `import amos_brain` works without errors
- [ ] `amos-brain --help` shows usage
- [ ] No FastAPI/Flask imports in core library modules
- [ ] All packages have __init__.py
- [ ] License consistent across all files
- [ ] SDK matches OpenAPI spec
- [ ] CI passes install test

---

**Next Steps**: Execute Phase 1 (Critical) fixes immediately. The server migration (Phase 2) requires coordination with AMOS-Consulting repository.
