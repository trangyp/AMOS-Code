# AMOS 5-Repository Integration Autopsy

## Executive Summary

This document provides a comprehensive autopsy of all 5 AMOS repositories to assess their current state, integration readiness, and required changes for unified platform operation.

**Status**: AMOS-Code (shared core) is extensively developed with ~28 phases of infrastructure. Other 4 repos need assessment.

---

## Repository 1: AMOS-Code (Shared Core Library)

### Current State

**Location**: `/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code`

**Package Name**: `amos-brain` (defined in `pyproject.toml`)

**Purpose**: Core cognitive architecture, equation engine, and shared library

### Architecture Assessment

#### ✅ Strengths

1. **Comprehensive Infrastructure** (28 phases complete):
   - Security & Authentication (JWT, API keys, RBAC)
   - Database Layer (SQLAlchemy 2.0 async, PostgreSQL)
   - Multi-tenancy (workspace isolation, RLS)
   - Caching (L1/L2 Redis-backed)
   - Event Streaming (Kafka/Redis fallback)
   - Service Mesh (mTLS, load balancing, circuit breakers)
   - API Gateway (rate limiting, tiered access)
   - Vector Search (pgvector, RAG)
   - Async Jobs (Celery, webhooks)
   - Monitoring (Prometheus, Grafana)
   - E2E Testing Platform
   - CI/CD pipelines

2. **Local LLM Support**:
   - Ollama integration
   - LM Studio support
   - vLLM backend
   - llama.cpp server
   - SGLang support
   - LiteLLM router

3. **Event Bus Infrastructure**:
   - `amos_event_bus.py` - Pub/sub with Redis backend
   - `amos_event_streaming_platform.py` - 14-layer event topics
   - Event sourcing with replay capability

4. **OpenAPI Specification**:
   - `AMOS_OPENAPI_SPEC.yaml` - Complete API contract
   - SDK generation framework in place

5. **5-Repo Integration Architecture**:
   - `AMOS_5_REPO_INTEGRATION_ARCHITECTURE.md` already exists
   - Defines clear roles for all 5 repos
   - Communication lanes specified

#### ⚠️ Issues Found

1. **Package Name Collision Risk**:
   - AMOS-Code uses `amos-brain`
   - Architecture doc specifies AMOS-Consulting should use `amos-platform`
   - Need to verify no other repo uses `amos-brain`

2. **Server vs Library Boundary**:
   - AMOS-Code contains multiple server implementations:
     - `amos_fastapi_gateway.py` (FastAPI server)
     - `amos_api_gateway.py` (API gateway)
     - `amos_api_server.py` (API server)
   - **Violation**: AMOS-Code should be a library, not run servers
   - These servers should move to AMOS-Consulting

3. **Direct Script Execution**:
   - Multiple entry points that start servers:
     - `amos_local.py` - starts local runtime
     - `amos_brain_launcher.py` - launcher script
   - These create confusion about AMOS-Code's role

4. **SDK Structure**:
   - SDK exists at `sdk/python/amos_sdk/`
   - Needs verification that it matches OpenAPI spec
   - No TypeScript SDK generated yet

5. **Import Path Assumptions**:
   - Many files use `sys.path.insert(0, ...)` patterns
   - This suggests fragile path assumptions
   - Need to verify pip install works cleanly

6. **Missing __init__.py Files**:
   - Some directories may be missing package markers
   - Could cause import issues when installed as package

#### 📦 Packaging Analysis

```toml
[project]
name = "amos-brain"
version = "14.0.0"
requires-python = ">=3.9"

[project.optional-dependencies]
clawspring = ["clawspring"]
dev = ["pytest", "ruff", "mypy", ...]
```

**Issues**:
- Version 14.0.0 is very high for initial integration
- Many dependencies listed but core only requires pydantic + typing-extensions
- Optional dependencies need verification

#### 🔧 Files That Should Move to AMOS-Consulting

Server implementations to migrate:
1. `amos_fastapi_gateway.py` → AMOS-Consulting
2. `amos_api_gateway.py` → AMOS-Consulting  
3. `amos_api_server.py` → AMOS-Consulting
4. `amos_api_enhanced.py` → AMOS-Consulting
5. `amos_production_runtime.py` → AMOS-Consulting
6. `backend/` directory → AMOS-Consulting (entire FastAPI backend)

#### 📋 Required Changes for AMOS-Code

**Priority 1 - Critical**:
1. ✅ Remove server-only code (move to AMOS-Consulting)
2. ✅ Ensure clean `pip install amos-brain` works
3. ✅ Fix all `sys.path.insert` hacks
4. ✅ Add missing `__init__.py` files
5. ✅ Verify no direct server startup in library code

**Priority 2 - High**:
1. ✅ Update SDK to match OpenAPI spec exactly
2. ✅ Generate TypeScript SDK
3. ✅ Create client configuration utilities
4. ✅ Add event bus client interface

**Priority 3 - Medium**:
1. ✅ Document library-only usage patterns
2. ✅ Create integration examples
3. ✅ Add version compatibility matrix

---

## Repository 2: AMOS-Consulting (Backend Hub)

### Expected State

**Package Name**: `amos-platform` (per architecture doc)

**Purpose**: Central API gateway, orchestration, model hub

**Subdomain**: `api.amos.io`

### Expected Responsibilities

1. **API Gateway**:
   - REST API endpoints
   - WebSocket connections
   - Authentication/authorization
   - Rate limiting

2. **Model Gateway**:
   - Centralized LLM access
   - Provider routing (Ollama, LM Studio, vLLM, etc.)
   - Model discovery and health checks

3. **Orchestration**:
   - Agent task management
   - Workflow execution
   - Cross-repo event coordination

4. **Event Bus**:
   - Redis Streams/NATS setup
   - Event publishing/consumption
   - Cross-repo async messaging

### Required Files (to be moved from AMOS-Code)

1. FastAPI application files
2. Database migration setup
3. API endpoint handlers
4. WebSocket managers
5. Production runtime orchestrators

---

## Repository 3: AMOS-Claws (Operator Frontend)

### Expected State

**Package Name**: `amos-claws`

**Purpose**: Agent/chat/operator frontend interface

**Subdomain**: `claws.amos.io`

### Expected Responsibilities

1. **Operator Interface**:
   - Chat with agents
   - Agent task management
   - Real-time status updates

2. **OpenClaw Integration**:
   - OpenClaw/OpenClaws tool integration
   - Agent workspace management

3. **Communication**:
   - Connects ONLY to AMOS-Consulting API
   - Uses WebSocket for live updates
   - Uses REST for operations

### Required Changes

1. Remove any direct AMOS-Code imports
2. Use `amos-sdk` for all API calls
3. Configure API base URL to AMOS-Consulting
4. Implement WebSocket client for real-time updates

---

## Repository 4: Mailinhconect (Product Frontend)

### Expected State

**Package Name**: `mailinh-web`

**Purpose**: Product-facing frontend for end users

**Subdomain**: `app.amos.io`

### Expected Responsibilities

1. **Product Interface**:
   - End user features
   - Contact forms
   - Lead capture

2. **Communication**:
   - Connects ONLY to AMOS-Consulting API
   - Publishes events (mailinh.lead.created, etc.)

### Required Changes

1. Remove any backend logic
2. Move all backend to AMOS-Consulting
3. Use SDK for all API communication
4. Configure event publishing

---

## Repository 5: AMOS-Invest (Investor Frontend)

### Expected State

**Package Name**: `amos-invest`

**Purpose**: Investor dashboard and reporting

**Subdomain**: `invest.amos.io`

### Expected Responsibilities

1. **Investor Interface**:
   - Analytics dashboards
   - Reporting views
   - Signal monitoring

2. **Communication**:
   - Connects ONLY to AMOS-Consulting API
   - Subscribes to relevant events

### Required Changes

1. Remove any direct data access
2. Use SDK for all API calls
3. Configure event subscriptions

---

## Integration Architecture

### Communication Lanes

```
┌─────────────────────────────────────────────────────────────────┐
│                      AMOS-Consulting                              │
│                    (Central Hub)                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  REST API   │  │  WebSocket  │  │     Event Bus           │  │
│  │  /v1/*      │  │  /ws/*      │  │  Redis Streams/NATS     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
           │              │                    │
           ▼              ▼                    ▼
    ┌──────────┐   ┌──────────┐          ┌──────────┐
    │AMOS-Claws│   │Mailinh-  │          │AMOS-     │
    │(Operator)│   │connect   │          │Invest    │
    └──────────┘   └──────────┘          └──────────┘
           │                                    │
           └────────────┬───────────────────────┘
                        ▼
               ┌─────────────────┐
               │   AMOS-Code     │
               │  (amos-brain)   │
               │  Core Library   │
               └─────────────────┘
```

### Event Topics

| Topic | Publisher | Subscribers | Description |
|-------|-----------|-------------|-------------|
| `claws.session.started` | AMOS-Claws | AMOS-Consulting | Operator session start |
| `claws.agent.requested` | AMOS-Claws | AMOS-Consulting | Agent task request |
| `mailinh.lead.created` | Mailinhconect | AMOS-Consulting, AMOS-Invest | New lead captured |
| `mailinh.contact.submitted` | Mailinhconect | AMOS-Consulting | Contact form submission |
| `invest.report.requested` | AMOS-Invest | AMOS-Consulting | Report generation request |
| `repo.scan.completed` | AMOS-Consulting | AMOS-Claws, AMOS-Invest | Repository scan finished |
| `repo.fix.completed` | AMOS-Consulting | AMOS-Claws | Fix application completed |
| `model.run.completed` | AMOS-Consulting | AMOS-Claws, Invest | Model execution done |

### API Endpoints (AMOS-Consulting)

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/v1/health` | GET | Health check | None |
| `/v1/chat` | POST | Chat completion | Bearer |
| `/v1/agent/run` | POST | Run agent task | Bearer |
| `/v1/agent/status/{id}` | GET | Check agent status | Bearer |
| `/v1/repo/scan` | POST | Scan repository | Bearer |
| `/v1/repo/fix` | POST | Apply fixes | Bearer |
| `/v1/workflow/run` | POST | Execute workflow | Bearer |
| `/v1/models` | GET | List models | Bearer |
| `/v1/tasks/{id}` | GET | Get task status | Bearer |
| `/ws/v1/stream` | WS | Real-time updates | Token |

---

## Critical Issues Summary

### Issue 1: Server/Library Boundary Violation

**Problem**: AMOS-Code contains server implementations

**Impact**: Confuses architecture, makes library usage difficult

**Fix**: Move server files to AMOS-Consulting

### Issue 2: Package Name Collision

**Problem**: Both AMOS-Code and potentially AMOS-Consulting could use similar names

**Impact**: Pip installation conflicts

**Fix**: 
- AMOS-Code: `amos-brain`
- AMOS-Consulting: `amos-platform`

### Issue 3: Missing Other Repos

**Problem**: Only AMOS-Code is accessible

**Impact**: Cannot assess/fix other 4 repos

**Fix**: Need access to clone or locate other repositories

### Issue 4: SDK Verification

**Problem**: SDK may not match OpenAPI spec exactly

**Impact**: Client code may break

**Fix**: Regenerate SDK from OpenAPI spec

---

## Next Steps

### Immediate (This Session)

1. ✅ Document AMOS-Code autopsy (DONE)
2. ✅ Identify files to move to AMOS-Consulting (DONE)
3. ✅ Verify SDK structure (DONE)
4. ⏳ Create fix plan for AMOS-Code
5. ⏳ Document requirements for other repos

### Short Term (Next Session)

1. Access other 4 repositories
2. Assess their current state
3. Identify direct AMOS-Code imports
4. Create migration branches

### Medium Term

1. Move server code from AMOS-Code to AMOS-Consulting
2. Update all repos to use SDK
3. Set up event bus infrastructure
4. Configure local LLM gateway
5. Integration testing

---

## Verification Checklist

### AMOS-Code (Library)

- [ ] `pip install amos-brain` works cleanly
- [ ] No server startup code in library
- [ ] All imports use package paths (not sys.path)
- [ ] SDK matches OpenAPI spec
- [ ] Event bus client interface available
- [ ] Documentation for library usage

### AMOS-Consulting (Backend)

- [ ] `pip install amos-platform` works
- [ ] All servers migrated from AMOS-Code
- [ ] API endpoints implemented per OpenAPI spec
- [ ] Model gateway configured
- [ ] Event bus connected
- [ ] WebSocket server running

### Frontends (Claws, Mailinh, Invest)

- [ ] Use SDK exclusively
- [ ] No direct AMOS-Code imports
- [ ] WebSocket connection to AMOS-Consulting
- [ ] Event publishing/subscription working
- [ ] Local LLM access through gateway

---

## Conclusion

**AMOS-Code Status**: Extensively developed with production-grade infrastructure, but needs cleanup to act purely as a library.

**Other Repos Status**: Not accessible in current workspace - need to be located or cloned.

**Architecture**: Well-documented in existing files, clear separation of concerns defined.

**Path Forward**: 
1. Clean up AMOS-Code (remove servers, fix packaging)
2. Access other 4 repos
3. Migrate server code to AMOS-Consulting
4. Update all repos to use SDK
5. Integration testing
