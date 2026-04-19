# AMOS 6-Repository Integration Autopsy

## Executive Summary

This document provides a comprehensive autopsy of all **6 AMOS repositories** to assess their current state, integration readiness, and required changes for unified platform operation.

**Status**: 
- AMOS-Code: Extensively developed (~28 phases of infrastructure)
- AMOS-Consulting, AMOS-Claws, Mailinhconect, AMOS-Invest: Need assessment
- **AMOS-UNIVERSE**: NEW - To be created as canonical knowledge layer

---

## Repository 1: AMOS-Code (Shared Core Library)

### Current State

**Location**: `/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code`

**Package Name**: `amos-brain` (defined in `pyproject.toml`)

**Purpose**: Core cognitive architecture, equation engine, and shared library

### Architecture Assessment

#### Strengths

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

2. **API Contracts Package** (`amos_brain/api_contracts/`):
   - Shared Pydantic models for hub-and-spoke
   - Chat, Repo, Model, Session, Brain, Workflow contracts
   - Used by AMOS-Consulting and client repos

3. **Local LLM Support**:
   - Ollama integration
   - LM Studio support
   - vLLM backend
   - llama.cpp server
   - SGLang support
   - LiteLLM router

4. **Existing Integration Docs**:
   - `AMOS_5_REPO_INTEGRATION_ARCHITECTURE.md`
   - `AMOS_REPO_INTEGRATION_PLAN.md`
   - `AMOS_API_CONTRACTS.md`

#### Issues Found

1. **Package Name Collision Risk**:
   - AMOS-Code uses `amos-brain`
   - Architecture doc specifies AMOS-Consulting should use `amos-platform`
   - AMOS-UNIVERSE should use `amos-universe`

2. **Server vs Library Boundary**:
   - AMOS-Code contains multiple server implementations
   - These should move to AMOS-Consulting OR be removed

3. **Contracts Location**:
   - API contracts currently in AMOS-Code
   - Should migrate to AMOS-UNIVERSE for clearer separation

### Required Changes for AMOS-Code

**Priority 1 - Critical**:
1. Remove server-only code (move to AMOS-Consulting)
2. Ensure clean `pip install amos-brain` works
3. Fix all `sys.path.insert` hacks
4. Prepare contracts for migration to AMOS-UNIVERSE

---

## Repository 2: AMOS-Consulting (Backend Hub)

### Expected State

**Package Name**: `amos-platform`

**Purpose**: Central API gateway, orchestration, model hub

**Subdomain**: `api.amos.io`

### Expected Responsibilities

1. **API Gateway**: REST API, WebSocket, auth, rate limiting
2. **Model Gateway**: Centralized LLM access, provider routing
3. **Orchestration**: Agent tasks, workflows, cross-repo coordination
4. **Event Bus**: Redis Streams/NATS for async messaging

### Required Changes

1. Rename package from `amos-brain` to `amos-platform`
2. Import `amos-brain` as library dependency
3. Import `amos-universe` for contracts/schemas
4. Move server code from AMOS-Code
5. Implement all API endpoints per spec

---

## Repository 3: AMOS-Claws (Operator Frontend)

### Expected State

**Package Name**: `amos-claws`

**Purpose**: Agent/chat/operator frontend interface

**Subdomain**: `claws.amos.io`

### Expected Responsibilities

1. **Operator Interface**: Chat with agents, task management
2. **OpenClaw Integration**: OpenClaw/OpenClaws tool integration
3. **Communication**: Connect ONLY to AMOS-Consulting API

### Required Changes

1. Remove any direct AMOS-Code imports
2. Use generated SDK from AMOS-UNIVERSE
3. Configure API base URL to AMOS-Consulting
4. Implement WebSocket client for real-time updates

---

## Repository 4: Mailinhconect (Product Frontend)

### Expected State

**Package Name**: `mailinh-web`

**Purpose**: Product-facing frontend for end users

**Subdomain**: `app.amos.io`

### Expected Responsibilities

1. **Product Interface**: End user features, contact forms, lead capture
2. **Communication**: Connect ONLY to AMOS-Consulting API

### Required Changes

1. Remove any backend logic
2. Move all backend to AMOS-Consulting
3. Use generated SDK from AMOS-UNIVERSE
4. Configure event publishing

---

## Repository 5: AMOS-Invest (Investor Frontend)

### Expected State

**Package Name**: `amos-invest`

**Purpose**: Investor dashboard and reporting

**Subdomain**: `invest.amos.io`

### Expected Responsibilities

1. **Investor Interface**: Analytics dashboards, reporting, signals
2. **Communication**: Connect ONLY to AMOS-Consulting API

### Required Changes

1. Remove any direct data access
2. Use generated SDK from AMOS-UNIVERSE
3. Configure event subscriptions

---

## Repository 6: AMOS-UNIVERSE (Canonical Knowledge Layer) ⭐ NEW

### Purpose

AMOS-UNIVERSE is the **canonical source of truth** for:

1. **Ontology** - Domain vocabulary, concept definitions, relationships
2. **API Contracts** - Shared Pydantic models, OpenAPI specs
3. **Event Schemas** - Canonical event type definitions
4. **Architecture** - ADRs, system topology, repo role definitions
5. **Generated Artifacts** - Client SDKs, server stubs

### Key Principle

> AMOS-UNIVERSE owns the **what** (contracts, schemas, definitions).  
> Implementation repos own the **how** (runtime behavior, business logic).

### Package Name

`amos-universe` - pure contracts/schemas, no runtime dependencies

### Subdomain

`universe.amos.io` - Documentation and schema registry

### Directory Structure

```
AMOS-UNIVERSE/
├── ontology/              # Domain ontology
├── contracts/             # API contracts
│   ├── openapi/          # OpenAPI specifications
│   ├── schemas/          # JSON Schema definitions
│   └── pydantic/         # Python contract models
├── specs/                # System specifications
├── adrs/                 # Architecture Decision Records
├── generated/            # Auto-generated artifacts
│   ├── python-client/
│   ├── typescript-client/
│   └── server-stubs/
└── docs/                 # Universe documentation
```

### Dependencies

- NO runtime dependencies on other repos
- Other repos depend ON AMOS-UNIVERSE for contracts
- Uses: pydantic, pydantic-settings, typing-extensions

### Content to Migrate from AMOS-Code

1. `amos_brain/api_contracts/` → `contracts/pydantic/`
2. `AMOS_API_CONTRACTS.md` → `docs/api-contracts.md`
3. `AMOS_5_REPO_INTEGRATION_ARCHITECTURE.md` → `specs/integration/`
4. Event definitions → `contracts/pydantic/events.py`

### New Content to Create

1. **Ontology definitions** (`ontology/`)
   - Core concepts (Agent, Task, Repository, etc.)
   - Relationships between concepts
   - Vocabulary definitions

2. **Event schema registry** (`contracts/schemas/event-schemas/`)
   - JSON Schema for each event type
   - Versioning strategy

3. **ADR documents** (`adrs/`)
   - 001-6-repo-architecture.md
   - 002-amos-universe-role.md
   - 003-event-bus-selection.md
   - 004-llm-gateway-design.md
   - 005-openclaw-integration.md

4. **Generated SDKs** (`generated/`)
   - Python client (from OpenAPI spec)
   - TypeScript client (from OpenAPI spec)
   - Server stubs for FastAPI

### Integration Pattern

```python
# In AMOS-Consulting
from amos_universe.contracts.pydantic import ChatRequest, ChatResponse
from amos_universe.contracts.pydantic.events import EventType, BaseEvent

# In AMOS-Claws (using generated client)
from amos_universe.generated.typescript_client import AMOSClient, EventType

# Event type safety
if event.event_type == EventType.REPO_SCAN_COMPLETED:
    handle_scan_completion(event.payload)
```

---

## 6-Repo Integration Architecture

### Communication Lanes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AMOS-UNIVERSE (Canonical Layer)                       │
│                    Source of truth for contracts/schemas                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
           Consumes contracts  Consumes schemas   Consumes ontology
                    │                 │                 │
                    ▼                 ▼                 ▼
┌───────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   AMOS-Consulting     │  │     AMOS-Code       │  │   Frontend Repos    │
│   (API Hub)           │  │   (Core Library)    │  │   (3 clients)       │
│  ┌─────────────────┐  │  │  ┌───────────────┐  │  │  ┌───────────────┐   │
│  │ REST API       │  │  │  │ Brain logic   │  │  │  │ AMOSClient    │   │
│  │ WebSocket      │  │  │  │ Equations     │  │  │  │ WebSocket     │   │
│  │ Event Bus      │  │  │  │ Reasoning     │  │  │  │ Events        │   │
│  └─────────────────┘  │  │  └───────────────┘  │  │  └───────────────┘   │
└───────────────────────┘  └─────────────────────┘  └─────────────────────┘
          │                                              │
          │ Uses library                                 │
          ▼                                              ▼
┌───────────────────────┐                    ┌─────────────────────┐
│   AMOS-Code         │◄───────────────────│  AMOS-Claws         │
│   (amos-brain)      │                    └─────────────────────┘
│   Core Library      │                              │
└───────────────────────┘                    ┌─────────────────────┐
                                             │  Mailinhconect      │
                                             └─────────────────────┘
                                             ┌─────────────────────┐
                                             │  AMOS-Invest        │
                                             └─────────────────────┘
```

### Event Topics (6-Repo)

| Topic | Publisher | Subscribers | Description |
|-------|-----------|-------------|-------------|
| `claws.session.started` | AMOS-Claws | Consulting, Invest | Operator session |
| `mailinh.lead.created` | Mailinhconect | Consulting, Invest | New lead |
| `invest.report.requested` | AMOS-Invest | Consulting | Report request |
| `repo.scan.completed` | Consulting | Claws, Invest | Repo scan done |
| `model.run.completed` | Consulting | Claws, Invest | Model execution |
| `universe.schema.updated` | AMOS-UNIVERSE | All | Schema change |
| `system.alert` | Consulting | All | System alert |

### API Endpoints (AMOS-Consulting)

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/v1/health` | GET | Health check | None |
| `/v1/chat` | POST | Chat completion | Bearer |
| `/v1/agent/run` | POST | Run agent | Bearer |
| `/v1/repo/scan` | POST | Scan repo | Bearer |
| `/v1/models` | GET | List models | Bearer |
| `/v1/universe/event-types` | GET | Event types | Bearer |
| `/v1/universe/schemas/{name}` | GET | Get schema | Bearer |
| `/ws/v1/stream` | WS | Real-time updates | Token |

---

## Critical Issues Summary

### Issue 1: Server/Library Boundary Violation

**Problem**: AMOS-Code contains server implementations

**Impact**: Confuses architecture, contracts in wrong place

**Fix**: 
- Move servers to AMOS-Consulting
- Move contracts to AMOS-UNIVERSE
- AMOS-Code = pure library

### Issue 2: Package Name Collisions

**Problem**: 6 repos need clear package names

**Solution**:
- AMOS-Code: `amos-brain`
- AMOS-Consulting: `amos-platform`
- AMOS-UNIVERSE: `amos-universe`
- AMOS-Claws: `amos-claws`
- Mailinhconect: `mailinh-web`
- AMOS-Invest: `amos-invest`

### Issue 3: Missing AMOS-UNIVERSE

**Problem**: No canonical knowledge layer exists

**Impact**: Contracts scattered, no ontology source

**Fix**: Create AMOS-UNIVERSE repository

### Issue 4: Direct Imports Between Repos

**Problem**: Frontend repos may import AMOS-Code directly

**Impact**: Spaghetti architecture

**Fix**: All frontend repos use SDK from AMOS-UNIVERSE

---

## Migration Plan

### Phase 1: Create AMOS-UNIVERSE (Week 1)

1. Create new repository
2. Migrate contracts from AMOS-Code
3. Add event definitions
4. Create ontology stubs
5. Publish package

### Phase 2: Update AMOS-Code (Week 1-2)

1. Remove server code
2. Fix packaging
3. Add optional universe dependency
4. Clean up imports

### Phase 3: Update AMOS-Consulting (Week 2-3)

1. Rename to `amos-platform`
2. Import universe contracts
3. Move server code from AMOS-Code
4. Implement all endpoints

### Phase 4: Update Frontend Repos (Week 3-4)

1. Remove direct AMOS-Code imports
2. Use generated SDK from AMOS-UNIVERSE
3. Update API client configuration

### Phase 5: Integration Testing (Week 4-5)

1. Test all 6 repos together
2. Verify event bus flow
3. Test LLM gateway
4. Validate contracts

---

## Verification Checklist

### AMOS-UNIVERSE

- [ ] `pip install amos-universe` works
- [ ] All contracts importable
- [ ] Event types defined
- [ ] Ontology documents created
- [ ] Generated SDKs work
- [ ] Documentation complete

### AMOS-Code

- [ ] `pip install amos-brain` works
- [ ] No server startup code
- [ ] No sys.path hacks
- [ ] Clean library interface

### AMOS-Consulting

- [ ] `pip install amos-platform` works
- [ ] All API endpoints implemented
- [ ] Model gateway configured
- [ ] Event bus connected
- [ ] WebSocket server running

### Frontend Repos (3)

- [ ] Use SDK exclusively
- [ ] No direct AMOS-Code imports
- [ ] WebSocket connection to Consulting
- [ ] Event publishing/subscription working

---

## Conclusion

**AMOS-Code Status**: Extensive infrastructure, needs cleanup for pure library role

**AMOS-Consulting Status**: Not accessible - needs server code from AMOS-Code

**AMOS-Claws, Mailinhconect, AMOS-Invest**: Not accessible - need SDK integration

**AMOS-UNIVERSE Status**: NEW - Must be created as canonical knowledge layer

**Path Forward**:
1. Create AMOS-UNIVERSE with contracts, events, ontology
2. Clean up AMOS-Code (remove servers, fix packaging)
3. Set up AMOS-Consulting as API hub
4. Update all frontend repos to use SDK
5. Integration testing across all 6 repos

