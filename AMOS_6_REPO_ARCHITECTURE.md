# AMOS 6-Repository System Architecture

## Complete Integration Design for 6-Repo Ecosystem

---

## Executive Summary

This document defines the unified system architecture for integrating **6 AMOS repositories** into one coherent platform:

| # | Repository | Role | Package | Endpoint |
|---|------------|------|---------|----------|
| 1 | **AMOS-Code** | Shared core library | `amos-brain` | None (library) |
| 2 | **AMOS-Consulting** | Backend hub / API | `amos-platform` | `api.amos.io` |
| 3 | **AMOS-Claws** | Operator frontend | `amos-claws` | `claws.amos.io` |
| 4 | **Mailinhconect** | Product frontend | `mailinh-web` | `app.amos.io` |
| 5 | **AMOS-Invest** | Investor frontend | `amos-invest` | `invest.amos.io` |
| 6 | **AMOS-UNIVERSE** | **Canonical knowledge** | `amos-universe` | `universe.amos.io` |

---

## System Topology

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           AMOS-UNIVERSE                                      │
│                    Canonical Knowledge Layer                                   │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  Ontology        API Contracts        Event Schemas        ADRs         │  │
│  │  ─────────       ────────────         ─────────────        ────         │  │
│  │  Domain models   Pydantic models      JSON schemas         Decisions    │  │
│  │  Vocabulary      OpenAPI specs        Canonical events     Records      │  │
│  │  Relationships   Type definitions   Version registry     Specs        │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
           ┌──────────────────────────┼──────────────────────────┐
           │                          │                          │
  Consumes │ ontology         Consumes│ contracts        Consumes│ schemas
           │                          │                          │
           ▼                          ▼                          ▼
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│ AMOS-Consulting  │         │   AMOS-Code      │         │ 3 Frontend Repos │
│ (API Hub)        │         │   (Core Library) │         │ (Clients)        │
│ ─────────────    │         │   ────────────   │         │ ─────────────    │
│ FastAPI gateway  │         │ Brain runtime    │         │ React/TS apps    │
│ WebSocket server │         │ Equations        │         │ SDK generated    │
│ Event bus (Redis)│         │ Reasoning        │         │ from universe    │
│ LLM router       │         │ Knowledge graph  │         │                  │
│ Auth/tenancy     │         │                  │         │                  │
└────────┬─────────┘         └────────┬─────────┘         └────────┬─────────┘
         │                            │                            │
         │ Uses library               │                            │
         ▼                            │                            ▼
┌──────────────────┐                  │                  ┌──────────────────┐
│   AMOS-Code      │◄─────────────────┘                  │   AMOS-Claws     │
│   (amos-brain)   │                                     │   (Operator)     │
│   Core Library   │                                     └────────┬─────────┘
└──────────────────┘                                              │
                                                                  │
                         ┌────────────────────────────────────────┼────────┐
                         │                                        │        │
                         ▼                                        ▼        ▼
               ┌──────────────────┐                     ┌──────────────────┐
               │  Mailinhconect   │                     │  AMOS-Invest     │
               │  (Product)       │                     │  (Investor)      │
               └──────────────────┘                     └──────────────────┘
```

---

## Communication Lanes

### Lane 1: Synchronous (Request/Response)

**Protocol**: HTTP REST API + WebSocket

**Flow**:
```
Frontend ──HTTP──► AMOS-Consulting ──Library Call──► AMOS-Code
      ◄──Response──│                      │
                   │◄──Result─────────────┘
                   │
                   └──WebSocket──► Frontend (real-time)
```

**Endpoints** (AMOS-Consulting):
- `GET /v1/health` - Health check
- `POST /v1/chat` - Chat completion
- `POST /v1/agent/run` - Run agent task
- `POST /v1/repo/scan` - Scan repository
- `POST /v1/repo/fix` - Apply fixes
- `GET /v1/models` - List LLM models
- `POST /v1/models/run` - Run model inference
- `GET /v1/tasks/{id}` - Get task status
- `GET /v1/universe/schemas` - List schemas (NEW)
- `WS /v1/stream` - WebSocket events

### Lane 2: Asynchronous (Cross-Repo Events)

**Protocol**: Redis Streams

**Flow**:
```
Publisher ──► Redis Stream ──► Subscribers
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
Consulting    Claws       Invest
```

**Event Topics**:
- `claws.session.started` / `claws.session.ended`
- `claws.agent.requested` / `claws.agent.completed`
- `mailinh.lead.created` / `mailinh.contact.submitted`
- `invest.report.requested` / `invest.signal.generated`
- `repo.scan.completed` / `repo.scan.failed`
- `repo.fix.completed` / `repo.fix.failed`
- `model.run.completed` / `model.run.failed`
- `workflow.completed`
- `universe.schema.updated` ⭐ NEW
- `system.alert`

---

## AMOS-UNIVERSE: Canonical Layer Design

### Purpose

AMOS-UNIVERSE is the **single source of truth** for:
1. **Ontology** - Domain vocabulary, concept definitions
2. **API Contracts** - Shared Pydantic models
3. **Event Schemas** - Canonical event definitions
4. **Architecture** - ADRs, system topology
5. **Generated SDKs** - Client libraries

### Position in Architecture

```
┌─────────────────────────────────────────┐
│         AMOS-UNIVERSE                   │
│    (owns: what - contracts/schemas)     │
└─────────────────────────────────────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
      ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│Consulting│  │  Code   │  │ Frontends│
│(how: API)│  │(how: lib)│  │(how: UI) │
└─────────┘  └─────────┘  └─────────┘
```

### Contract Flow

```python
# 1. Define in AMOS-UNIVERSE
# contracts/pydantic/chat.py
class ChatRequest(BaseModel):
    message: str
    workspace_id: str

# 2. Use in AMOS-Consulting
# amos_platform/api/routes/chat.py
from amos_universe.contracts.pydantic import ChatRequest

@app.post("/v1/chat")
async def chat(request: ChatRequest):
    ...

# 3. Use in AMOS-Claws (via generated SDK)
# TypeScript client generated from OpenAPI
import { ChatRequest, AMOSClient } from '@amos/universe-client';

const client = new AMOSClient({ baseUrl: 'https://api.amos.io' });
await client.chat({ message: 'Hello', workspace_id: 'ws-123' });
```

---

## Repository Detailed Specifications

### 1. AMOS-Code (Shared Core Library)

**Role**: Reusable brain library

**Package**: `amos-brain`

**What it provides**:
```python
from amos_brain import (
    get_cognitive_runtime,
    get_equation_registry,
    ReasoningEngine,
    KnowledgeGraph,
    AgentFramework,
)
```

**What it does NOT provide**:
- FastAPI servers
- WebSocket endpoints
- Direct HTTP handlers
- Standalone execution

**Dependencies**:
- `pydantic>=2.0`
- `numpy`, `scipy` (equations)
- Optional: `amos-universe` (for contracts)

### 2. AMOS-Consulting (Backend Hub)

**Role**: Central API gateway and orchestration

**Package**: `amos-platform`

**Responsibilities**:
```python
# API Gateway
- REST API endpoints (/v1/*)
- WebSocket server (/ws/*)
- Authentication/authorization
- Rate limiting, tiered access

# Model Gateway
- LLM provider routing
- Ollama, LM Studio, vLLM support
- Model discovery and health

# Event Bus
- Redis Streams integration
- Cross-repo event coordination

# Orchestration
- Agent task management
- Workflow execution
```

**Dependencies**:
```toml
[dependencies]
amos-brain = { git = "https://github.com/trangyp/AMOS-Code.git" }
amos-universe = { git = "https://github.com/trangyp/AMOS-UNIVERSE.git" }
fastapi = "^0.100"
redis = "^5.0"
```

### 3. AMOS-Claws (Operator Frontend)

**Role**: Agent/chat/operator interface

**Package**: `amos-claws`

**Responsibilities**:
- OpenClaw/OpenClaws integration
- Agent workspace management
- Real-time operator interface

**Communication**:
```typescript
// Only connects to AMOS-Consulting
import { AMOSClient } from '@amos/universe-client';

const client = new AMOSClient({
  baseUrl: 'https://api.amos.io',
  apiKey: process.env.AMOS_API_KEY,
});

// REST API calls
await client.agents.run({ agent_type: 'repo_scan' });

// WebSocket events
client.websocket.on('repo.scan.completed', handler);
```

### 4. Mailinhconect (Product Frontend)

**Role**: Product-facing end user interface

**Package**: `mailinh-web`

**Responsibilities**:
- End user features
- Lead capture forms
- Contact management

**Communication**:
- HTTP API to AMOS-Consulting
- Event publishing (mailinh.lead.created)

### 5. AMOS-Invest (Investor Frontend)

**Role**: Investor dashboard and reporting

**Package**: `amos-invest`

**Responsibilities**:
- Analytics dashboards
- Reporting views
- Signal monitoring

**Communication**:
- HTTP API to AMOS-Consulting
- Event subscription (invest.signal.generated)

### 6. AMOS-UNIVERSE (Canonical Knowledge)

**Role**: Ontology, contracts, schemas, specs

**Package**: `amos-universe`

**Responsibilities**:
```
ontology/              # Domain vocabulary
  - core-concepts.yaml
  - repo-roles.yaml
  - event-ontology.yaml

contracts/pydantic/    # Python contracts
  - chat.py
  - repo.py
  - events.py
  - models.py

contracts/schemas/     # JSON Schemas
  - event-schemas/
  - request-schemas/

contracts/openapi/     # OpenAPI specs
  - amos-core-api.yaml

specs/                 # Specifications
  - integration/
  - llm-gateway/

adrs/                  # Architecture decisions
  - 001-6-repo-architecture.md

generated/             # Auto-generated
  - python-client/
  - typescript-client/
```

**No Runtime Dependencies**:
- Pure contract package
- Only depends on `pydantic`, `typing-extensions`
- Other repos depend ON it

---

## LLM Gateway Design

### Centralized Access

Only **AMOS-Consulting** connects directly to local LLM providers:

```
┌─────────────────────────────────────────┐
│         AMOS-Consulting                 │
│  ┌─────────────────────────────────┐    │
│  │         LLM Router              │    │
│  │  ┌─────────┐ ┌─────────┐        │    │
│  │  │ Ollama  │ │LM Studio│        │    │
│  │  │ :11434  │ │ :1234   │        │    │
│  │  └────┬────┘ └────┬────┘        │    │
│  │       │          │             │    │
│  │  ┌────┴──────────┴────┐         │    │
│  │  │    Auto-Discovery  │         │    │
│  │  │    Health Checks   │         │    │
│  │  │    Request Routing │         │    │
│  │  └────────────────────┘         │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
           │
           │ Single API
           │ /v1/models/*
           │ /v1/chat
           ▼
    ┌──────────────┐
    │   Frontends  │
    │   (3 repos)  │
    └──────────────┘
```

### Supported Providers

| Provider | Endpoint | Capabilities |
|----------|----------|--------------|
| Ollama | `localhost:11434` | Chat, embeddings, models |
| LM Studio | `localhost:1234/v1` | OpenAI-compatible |
| vLLM | `localhost:8000/v1` | OpenAI-compatible, batched |
| llama.cpp | `localhost:8080` | GGUF models |
| SGLang | `localhost:30000` | Structured output |
| LiteLLM | `localhost:4000` | Router/gateway |

### API Interface

```python
# List available models
GET /v1/models
Response: [ModelInfo]

# Chat completion
POST /v1/chat
Request: {
    "model": "ollama/llama3.1:8b",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7
}
Response: ChatResponse

# Model management (admin)
POST /v1/models/{id}/load
POST /v1/models/{id}/unload
GET /v1/models/{id}/status
```

---

## Event Bus Design

### Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Claws     │    │   Mailinh   │    │   Invest    │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │ Publish
                          ▼
               ┌─────────────────────┐
               │   Redis Streams     │
               │   ─────────────     │
               │   claws.agent.*     │
               │   mailinh.lead.*    │
               │   repo.scan.*       │
               │   model.run.*       │
               │   universe.schema.* │
               └──────────┬──────────┘
                          │ Consume
                          ▼
               ┌─────────────────────┐
               │  AMOS-Consulting    │
               │  (Event Coordinator)  │
               └─────────────────────┘
```

### Event Structure

```python
{
    "event_id": "uuid",
    "event_type": "repo.scan.completed",
    "timestamp": "2026-01-19T10:30:00Z",
    "source": "amos-consulting",
    "version": "1.0",
    "trace_id": "uuid",
    "tenant_id": "ws-123",
    "priority": "normal",
    "payload": {
        "scan_id": "scan-456",
        "repo_url": "https://github.com/user/repo",
        "findings_count": 12,
        "duration_seconds": 45.2
    }
}
```

### Consumer Groups

| Group | Subscribers | Topics |
|-------|-------------|--------|
| `platform` | Consulting | `*` (all) |
| `claws` | AMOS-Claws | `claws.*`, `repo.*`, `model.*` |
| `invest` | AMOS-Invest | `invest.*`, `mailinh.lead.*`, `model.*` |
| `mailinh` | Mailinhconect | `mailinh.*` |

---

## OpenClaw Integration

### Design

AMOS-Claws serves as the **OpenClaw-facing layer**:

```
┌─────────────────────────────────────────┐
│           OpenClaw/OpenClaws            │
│         (External Tool Standard)        │
└─────────────────┬───────────────────────┘
                  │
                  │ Tool Definitions
                  ▼
┌─────────────────────────────────────────┐
│           AMOS-Claws                    │
│    (Operator Frontend / Agent Layer)    │
│  ┌─────────────────────────────────┐    │
│  │  Tool Adapter                   │    │
│  │  - repo_scanner                 │    │
│  │  - code_fixer                   │    │
│  │  - model_runner                 │    │
│  └─────────────────────────────────┘    │
└─────────────────┬───────────────────────┘
                  │
                  │ API Calls
                  ▼
┌─────────────────────────────────────────┐
│         AMOS-Consulting                 │
│      (Tool Execution Backend)             │
└─────────────────────────────────────────┘
```

### Tool Definitions

```yaml
# AMOS-Claws/config/tools.yaml
tools:
  repo_scanner:
    name: "Repository Scanner"
    description: "Scan repositories for issues"
    endpoint: "https://api.amos.io/v1/repo/scan"
    method: POST
    events:
      - "repo.scan.completed"
      - "repo.scan.failed"
    
  code_fixer:
    name: "Code Fixer"
    description: "Apply fixes to repositories"
    endpoint: "https://api.amos.io/v1/repo/fix"
    method: POST
    events:
      - "repo.fix.completed"
      - "repo.fix.failed"
```

---

## Dependency Rules

### Direction

```
AMOS-UNIVERSE ───► AMOS-Code ───► AMOS-Consulting ◄─── Frontends
        │                               │
        └───────────────────────────────┘
        (Consulting also imports Universe directly)
```

### Rule 1: Universe has NO runtime dependencies

```python
# AMOS-UNIVERSE/contracts/pydantic/chat.py
from pydantic import BaseModel  # OK
# NO imports from AMOS-Code or AMOS-Consulting
```

### Rule 2: Code may optionally use Universe

```python
# AMOS-Code optional integration
from amos_universe.contracts.pydantic import ChatRequest  # Optional
```

### Rule 3: Consulting uses both

```python
# AMOS-Consulting
from amos_brain import get_cognitive_runtime  # Core logic
from amos_universe.contracts.pydantic import ChatRequest  # Contracts
```

### Rule 4: Frontends only use Universe (generated SDK)

```typescript
// AMOS-Claws
import { AMOSClient, ChatRequest } from '@amos/universe-client';
// NO direct imports from AMOS-Code or AMOS-Consulting
```

---

## Deployment Architecture

### Subdomains

| Subdomain | Service | Port | Repository |
|-----------|---------|------|------------|
| `api.amos.io` | AMOS-Consulting | 8000 | AMOS-Consulting |
| `claws.amos.io` | AMOS-Claws UI | 3000 | AMOS-Claws |
| `app.amos.io` | Mailinhconect UI | 3000 | Mailinhconect |
| `invest.amos.io` | AMOS-Invest UI | 3000 | AMOS-Invest |
| `universe.amos.io` | AMOS-UNIVERSE Docs | 80 | AMOS-UNIVERSE |

### Docker Compose (Development)

```yaml
version: '3.8'

services:
  # AMOS-UNIVERSE (Schema Registry)
  amos-universe:
    build: ./AMOS-UNIVERSE
    ports:
      - "8080:8080"
    volumes:
      - ./AMOS-UNIVERSE:/app

  # AMOS Platform (Consulting)
  amos-platform:
    build: ./AMOS-Consulting
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - UNIVERSE_URL=http://amos-universe:8080
    depends_on:
      - redis
      - amos-universe

  # Redis for event bus
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # Ollama for local LLM
  ollama:
    image: ollama/ollama
    volumes:
      - ollama-data:/root/.ollama
    ports:
      - "11434:11434"

  # Frontend: AMOS-Claws
  amos-claws:
    build: ./AMOS-Claws
    ports:
      - "3001:3000"
    environment:
      - AMOS_API_URL=http://amos-platform:8000

  # Frontend: Mailinhconect
  mailinhconect:
    build: ./Mailinhconect
    ports:
      - "3002:3000"
    environment:
      - AMOS_API_URL=http://amos-platform:8000

  # Frontend: AMOS-Invest
  amos-invest:
    build: ./AMOS-Invest
    ports:
      - "3003:3000"
    environment:
      - AMOS_API_URL=http://amos-platform:8000

volumes:
  ollama-data:
```

---

## Success Criteria

The 6-repo integration is successful when:

| # | Criterion | Measurement |
|---|-----------|-------------|
| 1 | All repos have clear, separated roles | Architecture review |
| 2 | Communication through defined contracts | Integration tests |
| 3 | Local LLM access centralized | Provider connectivity |
| 4 | OpenClaw integrated intentionally | Tool execution tests |
| 5 | Packaging/import/path issues fixed | `pip install` tests |
| 6 | AMOS-UNIVERSE is canonical source | Schema registry validation |
| 7 | System explained simply as one platform | Documentation review |
| 8 | Event bus flows correctly | Event delivery tests |
| 9 | Generated SDKs work in all frontends | Client tests |
| 10 | No reverse dependencies into Universe | Static analysis |

---

## Implementation Phases

### Phase 1: AMOS-UNIVERSE (Week 1)
- Create repository
- Migrate contracts from AMOS-Code
- Add event definitions
- Create ontology stubs
- Set up package

### Phase 2: AMOS-Code Cleanup (Week 1-2)
- Remove server code
- Fix packaging
- Add optional universe dependency
- Clean imports

### Phase 3: AMOS-Consulting Setup (Week 2-3)
- Rename to amos-platform
- Import universe contracts
- Move server code
- Implement all endpoints

### Phase 4: Frontend Updates (Week 3-4)
- Remove direct AMOS-Code imports
- Use generated SDK
- Update API configuration
- Add WebSocket connections

### Phase 5: Integration Testing (Week 4-5)
- Test all 6 repos together
- Verify event bus
- Test LLM gateway
- Validate contracts
- Performance testing

### Phase 6: Deployment (Week 5-6)
- Configure subdomains
- Set up SSL
- Deploy to staging
- Production release

