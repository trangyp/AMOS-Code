# AMOS 5-Repository Full Integration Assessment

## Executive Summary

All 5 repositories have been successfully cloned and assessed. This document provides a complete integration analysis including current state, cross-repo dependencies, and implementation roadmap.

**Assessment Date**: April 19, 2026  
**Repositories**: 5/5 accessible  
**Total Code Files**: ~4,500+ (Python/JS/TS)

---

## Repository Overview

| Repository | Role | Package Name | Files | Tech Stack | Status |
|------------|------|--------------|-------|------------|--------|
| **AMOS-Code** | Core library | `amos-brain` | ~816 | Python | Extensive (28 phases) |
| **AMOS-Consulting** | Backend hub | `amos-platform` | 1,703 | Python | Production-ready |
| **Mailinhconect** | Product frontend | `biologic-os` | 522 | Python/JS | 20-layer organism |
| **AMOS-Invest** | Investor dashboard | N/A | 1,940 | Python | Skills/equations |
| **AMOS-Claws** | Operator frontend | `openclaw-control-ui` | 202 | Python/JS | OpenClaw UI |

---

## Detailed Repository Assessment

### 1. AMOS-Code (Already Assessed)

**Location**: `/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code`

**Package**: `amos-brain` (v14.0.0)

**Purpose**: Shared core library with cognitive architecture

**Key Features** (28 phases):
- Security (JWT, RBAC, API keys)
- Database (SQLAlchemy 2.0 async)
- Multi-tenancy (workspace isolation)
- Event streaming (Kafka/Redis)
- Service mesh (mTLS, circuit breakers)
- Vector search (pgvector, RAG)
- Local LLM support (Ollama, LM Studio, vLLM)

**⚠️ Critical Issues**:
- Contains server code that should move to AMOS-Consulting
- `backend/` directory, `amos_fastapi_gateway.py`, etc.
- Multiple `sys.path.insert()` hacks
- Server/library boundary violation

---

### 2. AMOS-Consulting (Backend Hub)

**Location**: `/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-Consulting`

**Files**: 1,703 (Python/JS/TS)

**Purpose**: Central API gateway and orchestration hub

**Key Components**:
- UCOS 10.x integration
- AMOS Brain HTTP API v2.0
- REST API endpoints (`/api/status`, `/api/health`, `/api/skills`)
- Skill registration bridge
- Presentation skill integration

**Cross-Repo Dependencies**:
```python
# Direct AMOS-Code imports found:
from amos_production_core import AMOSProductionCore
from amos_brain_activator import activate_brain
from amos_shared_utils import Colors, print_header
from amos_brain_quick import AMOSBrainQuick, get_brain_quick
```

**Integration Status**:
- Already has API integration guide
- UCOS 10.x + AMOS Brain v2.12 integration complete
- 8/8 tests passed
- 24 equations + 20 invariants available

**⚠️ Issues**:
- Imports from `amos_brain_*` modules directly
- Should use SDK instead
- No clear package name in pyproject.toml

---

### 3. Mailinhconect (Product Frontend)

**Location**: `/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/Mailinhconect`

**Files**: 522 (Python/JS)

**Package**: `biologic-os` (v2.0.0)

**Purpose**: 20-layer biologic operating system - product-facing

**Architecture**: 20-layer organism system
```
01_genome - Permanent laws
02_identity - Self-model
03_nervous_system - Signals and routing
04_brain - Decisions
05_memory - Stable intelligence
06_senses - Inputs and perception
07_language - AMOS-L, symbols, equations
08_motor_system - Action planning
09_effectors - Execution
10_homeostasis - Stability
11_immune_system - Protection and policy
12_metabolism - Resource economy
13_circulation - Queues and transport
14_skeleton - Interfaces and contracts
15_skin - UI/API/CLI boundary
16_reproduction - Packaging and deployment
17_learning - Improvement and patterns
18_dreaming - Sandboxed simulation
19_observatory - Metrics, traces, truth
20_world_interface - External systems
```

**API Endpoints**:
- `GET /health` - Health check
- `GET /status` - System status
- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Chat completions

**Cross-Repo Dependencies**:
```python
# Direct AMOS-Code imports found:
from amos_organism_bridge import OrganismBridge
from amos_tensor_runtime import AMOSKernel
from amos_brain_decision_layers import AMOSBrainDecisionLayers
from amos_l_core import AMOSLCore
from amos_organism_core import get_organism
```

**⚠️ Issues**:
- Direct imports from AMOS-Code modules
- Should use AMOS-Consulting API instead
- Has its own backend (`amos-backend/`)
- Duplicates functionality that should be in AMOS-Consulting

---

### 4. AMOS-Invest (Investor Dashboard)

**Location**: `/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-Invest`

**Files**: 1,940 (Python)

**Purpose**: Planetary-scale intelligence infrastructure for investment analysis

**Key Features**:
- 5 Claude Skills (validated, operational)
- 100+ core engines (canonical layer)
- 124+ MEGA engines (SUPER layer)
- 10 CLI tools
- Skills: McKinsey Consultant, Mimeng Writing, US Gov Shutdown Tracker, Code Architect, Data Analyst

**Cross-Repo Dependencies**:
```python
# Direct AMOS-Code imports found:
from amos_brain_permanent import AMOSBrainPermanent
from amos_capital_universe_engine import CapitalUniverseEngine
from amos_representation_engine import RepresentationEngine
from amos_capital_time_engine import CapitalTimeEngine
from amos_event_ledger import log_capital_event, EventLedger
from amos_executable_core import AMOSExecutableCore
from amos.brain_cli import AMOSBrainCLI
```

**⚠️ Issues**:
- Heavy direct coupling to AMOS-Code
- Uses internal modules (`amos_brain_permanent`, `amos_executable_core`)
- Should migrate to API calls via AMOS-Consulting
- Most complex migration due to deep integration

---

### 5. AMOS-Claws (Operator Frontend)

**Location**: `/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-Claws`

**Files**: 202 (Python/JS)

**UI Package**: `openclaw-control-ui` (Vite + Lit)

**Purpose**: OpenClaw-facing operator interface

**Tech Stack**:
- Python backend (skills/, test/, vendor/)
- JavaScript/TypeScript frontend (ui/)
- Vite build system
- Lit web components
- Vitest testing

**Dependencies**:
```json
{
  "@noble/ed25519": "3.0.1",
  "dompurify": "^3.3.3",
  "lit": "^3.3.2",
  "marked": "^18.0.0"
}
```

**Cross-Repo Dependencies**:
```python
# Found in repo_doctor_omega:
"repo": "trangyp/AMOS-Code",
"callee": "amos_brain.cookbook.ProjectPlanner.run"

from amos_bridge import (
    # bridge imports
)
```

**Status**:
- Has Swabble/ component
- QA scenarios defined
- Security validation documented
- ACP (Agent Capability Protocol) docs

**⚠️ Issues**:
- References AMOS-Code directly
- Needs to migrate to AMOS-Consulting API
- UI should use SDK for backend communication

---

## Cross-Repo Dependency Analysis

### Direct Import Violations

All 4 client repos have **direct imports** from AMOS-Code, violating the architecture principle:

```
❌ Mailinhconect: from amos_organism_bridge import OrganismBridge
❌ AMOS-Invest: from amos_brain_permanent import AMOSBrainPermanent  
❌ AMOS-Claws: references amos_brain.cookbook.ProjectPlanner
❌ AMOS-Consulting: from amos_brain_activator import activate_brain
```

### Import Categories

| Repo | Import Type | Count | Severity |
|------|-------------|-------|----------|
| Mailinhconect | organism modules | 5+ | High |
| AMOS-Invest | brain permanent/core | 10+ | Critical |
| AMOS-Claws | bridge/cookbook | 2+ | Medium |
| AMOS-Consulting | production/activator | 5+ | High |

### Required Migration Strategy

1. **Phase 1**: Create SDK with all needed methods
2. **Phase 2**: Add SDK dependency to each repo
3. **Phase 3**: Replace direct imports with SDK calls
4. **Phase 4**: Test and validate

---

## Integration Architecture

### Target State

```
┌─────────────────────────────────────────────────────────────────┐
│                      AMOS-Consulting                            │
│                    (Central Hub)                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  REST API   │  │  WebSocket  │  │     Event Bus           │  │
│  │  /v1/*      │  │  /ws/*      │  │  Redis Streams/NATS     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│         │                                        │              │
│         │    ┌──────────────────────────┐         │              │
│         └───▶│  amos-platform package   │◀────────┘              │
│              │  (FastAPI + Business)  │                        │
│              └──────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
           │                                    │
           ▼                                    ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │AMOS-Claws│   │Mailinh-  │   │AMOS-     │
    │  (UI)    │   │connect   │   │Invest    │
    │ 202 files│   │522 files │   │1940 files│
    └──────────┘   └──────────┘   └──────────┘
           │                                    │
           └────────────┬───────────────────────┘
                        ▼
               ┌─────────────────┐
               │   AMOS-Code     │
               │  (amos-brain)   │
               │  Core Library   │
               │  ~816 files     │
               └─────────────────┘
```

### Package Dependencies

```
amos-brain (library)
    ▲
    │ (pip install)
    │
amos-platform (backend)
    │    ┌─────────────────────────────┐
    │    │ FastAPI + Business Logic    │
    │    │ - API endpoints             │
    │    │ - Model gateway             │
    │    │ - Event bus                 │
    │    └─────────────────────────────┘
    │
    │ (HTTP/WebSocket/Event Bus)
    ▼
amos-sdk (client library)
    │    ┌─────────────────────────────┐
    │    │ - REST client               │
    │    │ - WebSocket client          │
    │    │ - Event bus client          │
    │    └─────────────────────────────┘
    ▲
    │ (pip install amos-sdk)
    │
┌───┴────┬───────────┬──────────┐
│        │           │          │
▼        ▼           ▼          ▼
Claws  Mailinh    Invest    (others)
(UI)   (Product)  (Investor)
```

---

## Migration Requirements by Repository

### AMOS-Code → Clean Library

**Priority 1 - Critical**:
1. ✅ Remove server-only code
2. ✅ Fix all `sys.path.insert()` hacks
3. ✅ Add missing `__init__.py` files
4. ✅ Verify clean `pip install amos-brain`

**Files to Move to AMOS-Consulting**:
```
backend/                           → AMOS-Consulting/src/api/
amos_fastapi_gateway.py            → AMOS-Consulting/src/api/main.py
amos_api_gateway.py              → AMOS-Consulting/src/api/gateway.py
amos_api_gateway_enterprise.py   → AMOS-Consulting/src/api/enterprise.py
amos_api_server.py               → AMOS-Consulting/src/api/server.py
amos_production_runtime.py       → AMOS-Consulting/src/core/runtime.py
amos_websocket_manager.py        → AMOS-Consulting/src/api/websocket/
```

### AMOS-Consulting → Backend Hub

**Priority 1**:
1. ✅ Define package name: `amos-platform`
2. ✅ Create `pyproject.toml` with proper metadata
3. ✅ Import `amos-brain` as dependency
4. ✅ Move server code from AMOS-Code

**Priority 2**:
1. ✅ Replace direct imports with library calls
2. ✅ Set up model gateway
3. ✅ Configure event bus
4. ✅ Create API endpoints per OpenAPI spec

### Mailinhconect → Product Frontend

**Priority 1**:
1. ✅ Remove `amos-backend/` server code (or merge into AMOS-Consulting)
2. ✅ Add `amos-sdk` dependency
3. ✅ Replace direct imports with SDK calls

**Migration Example**:
```python
# Before (WRONG):
from amos_organism_bridge import OrganismBridge
bridge = OrganismBridge()
result = bridge.process_task(task)

# After (CORRECT):
from amos_sdk import Client
client = Client(api_key="...", base_url="https://api.amos.io")
result = client.run_agent("process_task", task)
```

### AMOS-Invest → Investor Dashboard

**Priority 1**:
1. ✅ Add `amos-sdk` dependency
2. ✅ Replace brain imports with SDK

**Complex Migrations**:
```python
# Before (10+ imports):
from amos_brain_permanent import AMOSBrainPermanent
from amos_capital_universe_engine import CapitalUniverseEngine
from amos_executable_core import AMOSExecutableCore

# After:
from amos_sdk import Client
client = Client()
result = client.run_skill("capital_analysis", params)
```

### AMOS-Claws → Operator Frontend

**Priority 1**:
1. ✅ Update `repo_doctor_omega` to use SDK
2. ✅ Modify UI to call API instead of direct imports
3. ✅ Use WebSocket for real-time updates

---

## SDK Requirements

### Python SDK (`amos-sdk`)

**Current Location**: `AMOS-Code/sdk/python/amos_sdk/`

**Required Methods**:

```python
class Client:
    # Chat/Completion
    def chat(self, message: str, context=None, model=None) -> ChatResponse
    
    # Agent Operations
    def run_agent(self, agent_type: str, parameters: dict, priority: str = "normal") -> Task
    def get_agent_status(self, task_id: str) -> TaskStatus
    def cancel_agent(self, task_id: str) -> bool
    
    # Repository Operations
    def scan_repo(self, repo_url: str, scan_types: list) -> ScanResult
    def fix_repo(self, scan_id: str) -> FixResult
    
    # Workflow Operations
    def run_workflow(self, workflow_type: str, parameters: dict) -> Workflow
    
    # Model Operations
    def list_models(self) -> list[ModelInfo]
    def get_model_status(self, model_id: str) -> ModelStatus
    
    # Task Management
    def list_tasks(self) -> list[Task]
    def get_task(self, task_id: str) -> Task
    
    # Health
    def health(self) -> HealthStatus

class AsyncClient:
    # All methods as async
    async def chat(self, ...) -> ChatResponse
    
    # WebSocket support
    async def subscribe(self, channel: str) -> AsyncIterator[Event]

class EventBusClient:
    def subscribe(self, topic: str, callback: Callable)
    def publish(self, topic: str, payload: dict)
```

### TypeScript SDK (`amos-sdk-ts`)

**Generate from OpenAPI**:
```bash
openapi-generator generate \
  -i AMOS_OPENAPI_SPEC.yaml \
  -g typescript-axios \
  -o sdk/typescript/
```

---

## Implementation Timeline

### Week 1: Foundation
- **Day 1-2**: Clean up AMOS-Code (remove servers)
- **Day 3-4**: Set up AMOS-Consulting structure
- **Day 5**: Move server code, verify imports

### Week 2: SDK & API
- **Day 1-2**: Update Python SDK to match OpenAPI
- **Day 3**: Generate TypeScript SDK
- **Day 4**: Add event bus client
- **Day 5**: SDK testing

### Week 3: Backend Migration
- **Day 1-2**: Configure model gateway
- **Day 3-4**: Set up event bus infrastructure
- **Day 5**: API endpoint implementation

### Week 4: Frontend Migration - Mailinhconect
- **Day 1-2**: Remove backend code
- **Day 3**: Add SDK, migrate imports
- **Day 4**: Testing
- **Day 5**: Documentation

### Week 5: Frontend Migration - AMOS-Invest
- **Day 1-3**: Migrate heavy brain imports
- **Day 4**: Testing
- **Day 5**: Documentation

### Week 6: Frontend Migration - AMOS-Claws
- **Day 1-2**: Update repo_doctor_omega
- **Day 3**: UI API integration
- **Day 4-5**: Testing & WebSocket

### Week 7: Integration Testing
- **Day 1-3**: End-to-end testing
- **Day 4**: Performance testing
- **Day 5**: Bug fixes

### Week 8: Deployment
- **Day 1-2**: Staging deployment
- **Day 3**: Production preparation
- **Day 4-5**: Production deployment

---

## Verification Checklist

### Package Installation
- [ ] `pip install amos-brain` works cleanly
- [ ] `pip install amos-platform` works cleanly
- [ ] `pip install amos-sdk` works cleanly

### Import Verification
- [ ] No `sys.path.insert()` in AMOS-Code
- [ ] No direct `amos_brain_*` imports in client repos
- [ ] All imports use SDK or API

### API Verification
- [ ] All OpenAPI endpoints implemented
- [ ] Model gateway discovers local LLMs
- [ ] Event bus delivers messages < 100ms

### Cross-Repo Communication
- [ ] Mailinhconect → AMOS-Consulting ✓
- [ ] AMOS-Invest → AMOS-Consulting ✓
- [ ] AMOS-Claws → AMOS-Consulting ✓
- [ ] Events flow between all repos ✓

### Local LLM Support
- [ ] Ollama auto-discovery
- [ ] LM Studio connection
- [ ] vLLM routing
- [ ] Model health checks

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking changes in AMOS-Invest | High | High | Gradual migration, feature flags |
| SDK doesn't cover all use cases | Medium | High | Extensive testing before migration |
| Performance degradation | Medium | Medium | Load testing, caching strategy |
| Event bus reliability | Low | High | Retry logic, dead letter queues |
| Package conflicts | Medium | Medium | Virtual env testing, version pinning |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cross-repo imports | 0 | `grep -r "from amos\|import amos"` |
| SDK coverage | 100% | Compare to OpenAPI spec |
| API response time | < 200ms p95 | Load test |
| Event delivery | < 100ms | Time measurement |
| Package install time | < 30s | `time pip install` |
| Integration test pass | 100% | CI/CD pipeline |

---

## Next Actions

### Immediate (Priority 1)

1. ✅ **Review this assessment** - Approve architecture decisions
2. ⏳ **Start AMOS-Code cleanup** - Remove server code
3. ⏳ **Set up AMOS-Consulting package** - Create `pyproject.toml`
4. ⏳ **Begin SDK updates** - Add missing methods

### Short-term (Priority 2)

1. ⏳ **Create integration branches** in all 5 repos
2. ⏳ **Move server code** from AMOS-Code to AMOS-Consulting
3. ⏳ **Update Mailinhconect** - Remove backend, add SDK
4. ⏳ **Configure model gateway**

### Follow-up (Priority 3)

1. ⏳ **Migrate AMOS-Invest** (most complex)
2. ⏳ **Update AMOS-Claws UI**
3. ⏳ **Set up event bus**
4. ⏳ **Integration testing**

---

## Conclusion

**Current State**: 
- ✅ All 5 repositories accessible
- ✅ AMOS-Code extensively developed
- ⚠️ All 4 client repos have direct AMOS-Code imports
- ⚠️ Server/library boundary violation

**Path Forward**:
1. Clean up AMOS-Code (library-only)
2. Set up AMOS-Consulting as backend hub
3. Create/update SDK
4. Migrate all client repos to use SDK
5. Integration testing and deployment

**Estimated Effort**: 8 weeks (with 1-2 developers)

**Ready to proceed** with implementation once you approve the plan.
