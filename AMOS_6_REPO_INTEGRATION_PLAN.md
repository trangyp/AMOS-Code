# AMOS 6-Repository Integration Plan

## Executive Summary

This document provides the exact integration plan for connecting **6 AMOS repositories** through one shared protocol. It includes:
- File-by-file implementation details
- Package renaming instructions
- API endpoint specifications
- Event topic mappings (with AMOS-UNIVERSE events)
- Deployment configurations
- AMOS-UNIVERSE as the canonical knowledge/ontology layer

---

## Repository Roles (Updated for 6-Repo Architecture)

| Repository | Role | Package Name | Public Endpoint | Purpose |
|------------|------|--------------|-----------------|---------|
| **AMOS-Code** | Shared core library | `amos-brain` | None (library) | Core cognitive architecture, equation engine |
| **AMOS-Consulting** | Central backend hub | `amos-platform` | `api.amos.io` | API gateway, orchestration, model gateway |
| **AMOS-Claws** | Agent/operator frontend | `amos-claws` | `claws.amos.io` | OpenClaw-facing operator interface |
| **Mailinhconect** | Product frontend | `mailinh-web` | `app.amos.io` | End-user product interface |
| **AMOS-Invest** | Investor frontend | `amos-invest` | `invest.amos.io` | Investor dashboard, reporting |
| **AMOS-UNIVERSE** | **Canonical universe layer** | `amos-universe` | `universe.amos.io` | **Ontology, schemas, contracts, specs, ADRs** |

---

## 6-Repo Integration Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AMOS-UNIVERSE (Canonical Layer)                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │  - Ontology (domain models, vocabulary)                                   │  │
│  │  - API Contracts (shared schemas)                                       │  │
│  │  - Event Definitions (canonical event types)                              │  │
│  │  - Architecture ADRs (decision records)                                  │  │
│  │  - System Maps (repo roles, dependencies)                                │  │
│  │  - Generated Clients (from OpenAPI specs)                                │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                 ┌─────────────────────┼─────────────────────┐
                 │                     │                     │
        Consumes contracts    Consumes schemas       Consumes ontology
                 │                     │                     │
                 ▼                     ▼                     ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│   AMOS-Consulting     │  │      AMOS-Code        │  │   All Frontend Repos  │
│   (API Hub)           │  │   (Core Library)      │  │   (Clients)           │
│  ┌─────────────────┐  │  │  ┌─────────────────┐  │  │  ┌─────────────────┐  │
│  │ REST API /v1/*  │  │  │  │ Core brain fns  │  │  │  │ AMOSClient SDK  │  │
│  │ WebSocket /ws/* │  │  │  │ Equations       │  │  │  │ WebSocket conn  │  │
│  │ Event Bus       │  │  │  │ Reasoning       │  │  │  │ Event handlers  │  │
│  └─────────────────┘  │  │  └─────────────────┘  │  │  └─────────────────┘  │
└───────────────────────┘  └───────────────────────┘  └───────────────────────┘
          │                           │                           │
          │ Uses library              │                           │
          ▼                           │                           ▼
┌───────────────────────┐             │                  ┌───────────────────────┐
│   AMOS-Code         │◄────────────┘                  │  AMOS-Claws          │
│   (amos-brain)      │                               │  (Operator UI)       │
│   Core Library      │                               └───────────────────────┘
└───────────────────────┘                                          │
                                                                   │
┌───────────────────────┐                               ┌───────────────────────┐
│  Mailinhconect       │                               │  AMOS-Invest         │
│  (Product UI)        │                               │  (Investor UI)       │
└───────────────────────┘                               └───────────────────────┘
```

---

## AMOS-UNIVERSE: Canonical Knowledge Layer

### Purpose

AMOS-UNIVERSE is the **source of truth** for:

1. **Ontology** - Domain vocabulary, concept definitions, relationships
2. **API Contracts** - Shared Pydantic models, OpenAPI specifications
3. **Event Schemas** - Canonical event type definitions
4. **Architecture** - ADRs, system topology, repo role definitions
5. **Generated Artifacts** - Client SDKs, server stubs, type definitions

### Key Principle

> AMOS-UNIVERSE owns the **what** (contracts, schemas, definitions).  
> Implementation repos own the **how** (runtime behavior, business logic).

### Directory Structure

```
AMOS-UNIVERSE/
├── ontology/                    # Domain ontology
│   ├── core-concepts.yaml       # Core AMOS concepts
│   ├── repo-roles.yaml          # Repository role definitions
│   └── event-ontology.yaml      # Event type taxonomy
│
├── contracts/                   # API contracts
│   ├── openapi/                 # OpenAPI specifications
│   │   ├── amos-core-api.yaml
│   │   └── amos-consulting-api.yaml
│   ├── schemas/                 # JSON Schema definitions
│   │   ├── event-schemas/
│   │   ├── model-schemas/
│   │   └── request-response/
│   └── pydantic/                # Python contract models (source)
│       ├── chat.py
│       ├── repo.py
│       └── events.py
│
├── specs/                       # System specifications
│   ├── integration/             # Integration specs
│   │   ├── 6-repo-architecture.md
│   │   ├── event-topics.md
│   │   └── dependency-rules.md
│   ├── llm-gateway/             # LLM gateway spec
│   └── security/                # Security requirements
│
├── adrs/                        # Architecture Decision Records
│   ├── 001-6-repo-architecture.md
│   ├── 002-amos-universe-role.md
│   └── 003-event-bus-selection.md
│
├── generated/                   # Auto-generated artifacts
│   ├── python-client/           # Python SDK
│   ├── typescript-client/       # TypeScript SDK
│   └── server-stubs/            # FastAPI stubs
│
└── docs/                        # Universe documentation
    ├── system-map.md
    ├── getting-started.md
    └── contributing.md
```

### Dependency Direction

```
AMOS-UNIVERSE → shared contracts/specs only (no runtime dependencies)
      │
      ├──► AMOS-Code → may consume contracts if needed
      │
      ├──► AMOS-Consulting → consumes contracts + schemas
      │
      ├──► AMOS-Claws → consumes generated clients + schemas
      │
      ├──► Mailinhconect → consumes generated clients + schemas
      │
      └──► AMOS-Invest → consumes generated clients + schemas
```

**Critical Rule**: No reverse dependency from AMOS-UNIVERSE into runtime repos.

---

## Phase 1: AMOS-UNIVERSE Setup (Week 1)

### 1.1 Create Repository Structure

```bash
# AMOS-UNIVERSE repository
git init AMOS-UNIVERSE
cd AMOS-UNIVERSE

# Create directory structure
mkdir -p ontology contracts/openapi contracts/schemas contracts/pydantic
mkdir -p specs/integration specs/llm-gateway specs/security
mkdir -p adrs generated/python-client generated/typescript-client
mkdir -p docs

# Initialize Python package for contracts
touch contracts/pydantic/__init__.py
```

### 1.2 Migrate Contracts from AMOS-Code

Move `amos_brain/api_contracts/` from AMOS-Code to AMOS-UNIVERSE:

```
AMOS-UNIVERSE/contracts/pydantic/
├── __init__.py
├── base.py              # BaseAMOSModel, TimestampsMixin
├── chat.py              # ChatRequest, ChatResponse, etc.
├── repo.py              # RepoScanRequest, RepoFixResult, etc.
├── models.py            # ModelInfo, ModelCapabilities, etc.
├── session.py           # User, Workspace, SessionContext
├── brain.py             # BrainRunRequest, BrainRunResponse
├── workflow.py          # WorkflowRunRequest, WorkflowRunResponse
├── errors.py            # ApiError, ErrorCode, etc.
└── events.py            # NEW: Canonical event definitions
```

### 1.3 Create Package Configuration

**File: `AMOS-UNIVERSE/pyproject.toml`**

```toml
[project]
name = "amos-universe"
version = "1.0.0"
description = "AMOS Universe - Canonical ontology, contracts, and schemas"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Trang", email = "trang@amos.io"}
]

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "typing-extensions>=4.0.0",
]

[project.optional-dependencies]
generated = [
    "httpx>=0.25.0",           # For generated Python client
    "websockets>=12.0",       # For generated WebSocket client
]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
    "openapi-generator-cli",
]

[project.urls]
Homepage = "https://github.com/trangyp/AMOS-UNIVERSE"
Documentation = "https://docs.amos.io/universe"
Repository = "https://github.com/trangyp/AMOS-UNIVERSE"

[tool.setuptools.packages.find]
where = ["contracts/pydantic"]
```

### 1.4 Create Event Definitions

**File: `AMOS-UNIVERSE/contracts/pydantic/events.py`**

```python
"""Canonical event definitions for the AMOS 6-repo ecosystem.

This module defines all event types that flow through the event bus.
Each event has a canonical schema that all publishers/subscribers must follow.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

from .base import BaseAMOSModel


class EventType(str, Enum):
    """Canonical event types for the AMOS ecosystem."""
    
    # CLAWS events (Layer 09 - Social/Agent)
    CLAWS_SESSION_STARTED = "claws.session.started"
    CLAWS_SESSION_ENDED = "claws.session.ended"
    CLAWS_AGENT_REQUESTED = "claws.agent.requested"
    CLAWS_AGENT_COMPLETED = "claws.agent.completed"
    CLAWS_TOOL_INVOKED = "claws.tool.invoked"
    
    # MAILINH events (Layer 14 - Interfaces)
    MAILINH_LEAD_CREATED = "mailinh.lead.created"
    MAILINH_CONTACT_SUBMITTED = "mailinh.contact.submitted"
    MAILINH_USER_REGISTERED = "mailinh.user.registered"
    
    # INVEST events (Layer 14 - Interfaces)
    INVEST_REPORT_REQUESTED = "invest.report.requested"
    INVEST_SIGNAL_GENERATED = "invest.signal.generated"
    INVEST_ANALYTICS_VIEWED = "invest.analytics.viewed"
    
    # REPO events (Layer 01 - Brain)
    REPO_SCAN_COMPLETED = "repo.scan.completed"
    REPO_SCAN_FAILED = "repo.scan.failed"
    REPO_FIX_COMPLETED = "repo.fix.completed"
    REPO_FIX_FAILED = "repo.fix.failed"
    
    # MODEL events (Layer 10 - Memory)
    MODEL_RUN_COMPLETED = "model.run.completed"
    MODEL_RUN_FAILED = "model.run.failed"
    MODEL_LOADED = "model.loaded"
    MODEL_UNLOADED = "model.unloaded"
    
    # WORKFLOW events (Layer 06 - Muscle)
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_STEP_COMPLETED = "workflow.step.completed"
    
    # UNIVERSE events (NEW - Layer 11 - Canon)
    UNIVERSE_SCHEMA_UPDATED = "universe.schema.updated"
    UNIVERSE_CONTRACT_PUBLISHED = "universe.contract.published"
    UNIVERSE_ONTOLOGY_CHANGED = "universe.ontology.changed"
    
    # CONSULTING events (Layer 00 - Root)
    CONSULTING_WORKFLOW_COMPLETED = "consulting.workflow.completed"
    CONSULTING_TASK_CREATED = "consulting.task.created"
    CONSULTING_TASK_UPDATED = "consulting.task.updated"
    
    # SYSTEM events (Layer 00 - Root)
    SYSTEM_ALERT = "system.alert"
    SYSTEM_HEALTH_CHANGED = "system.health.changed"
    SYSTEM_MAINTENANCE_SCHEDULED = "system.maintenance.scheduled"


class EventMetadata(BaseModel):
    """Metadata attached to all events."""
    
    event_id: str = Field(..., description="Unique event identifier (UUID)")
    timestamp: datetime = Field(..., description="Event timestamp (ISO 8601 UTC)")
    source: str = Field(..., description="Source repository (e.g., 'amos-claws')")
    version: str = Field(default="1.0", description="Event schema version")
    trace_id: str | None = Field(None, description="Distributed trace ID")
    tenant_id: str | None = Field(None, description="Multi-tenant workspace ID")
    
    # Priority for event processing
    priority: Literal["low", "normal", "high", "urgent"] = "normal"


class BaseEvent(BaseAMOSModel):
    """Base class for all AMOS events."""
    
    event_type: EventType
    metadata: EventMetadata
    payload: dict[str, Any] = Field(default_factory=dict)
    
    def get_routing_key(self) -> str:
        """Get the routing key for this event type."""
        return self.event_type.value


# =============================================================================
# Specific Event Payloads
# =============================================================================

class ClawsSessionPayload(BaseModel):
    """Payload for claws.session.* events."""
    session_id: str
    user_id: str | None = None
    workspace_id: str | None = None
    client_info: dict[str, Any] | None = None


class ClawsAgentPayload(BaseModel):
    """Payload for claws.agent.* events."""
    task_id: str
    agent_type: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    priority: Literal["low", "normal", "high", "urgent"] = "normal"
    target_repo: str | None = None


class MailinhLeadPayload(BaseModel):
    """Payload for mailinh.lead.* events."""
    lead_id: str
    source: str  # 'website', 'api', 'import', etc.
    email: str | None = None
    phone: str | None = None
    name: str | None = None
    form_data: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class RepoScanPayload(BaseModel):
    """Payload for repo.scan.* events."""
    scan_id: str
    repo_url: str
    repo_name: str | None = None
    branch: str = "main"
    scan_types: list[str] = Field(default_factory=list)
    findings_count: int = 0
    findings_by_severity: dict[str, int] = Field(default_factory=dict)
    duration_seconds: float | None = None
    report_url: str | None = None


class RepoFixPayload(BaseModel):
    """Payload for repo.fix.* events."""
    fix_id: str
    scan_id: str
    repo_url: str
    files_changed: list[str] = Field(default_factory=list)
    pr_url: str | None = None
    commit_sha: str | None = None
    fixes_applied: int = 0
    fixes_failed: int = 0


class ModelRunPayload(BaseModel):
    """Payload for model.run.* events."""
    run_id: str
    model_id: str
    provider: str  # 'ollama', 'lmstudio', 'vllm', etc.
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    duration_ms: float | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)


class UniverseSchemaPayload(BaseModel):
    """Payload for universe.schema.* events."""
    schema_name: str
    schema_version: str
    change_type: Literal["created", "updated", "deprecated"]
    affected_repos: list[str] = Field(default_factory=list)
    migration_guide_url: str | None = None


# =============================================================================
# Event Definitions with Typed Payloads
# =============================================================================

class ClawsSessionStartedEvent(BaseEvent):
    """Event: claws.session.started"""
    event_type: EventType = EventType.CLAWS_SESSION_STARTED
    payload: ClawsSessionPayload


class ClawsAgentRequestedEvent(BaseEvent):
    """Event: claws.agent.requested"""
    event_type: EventType = EventType.CLAWS_AGENT_REQUESTED
    payload: ClawsAgentPayload


class MailinhLeadCreatedEvent(BaseEvent):
    """Event: mailinh.lead.created"""
    event_type: EventType = EventType.MAILINH_LEAD_CREATED
    payload: MailinhLeadPayload


class RepoScanCompletedEvent(BaseEvent):
    """Event: repo.scan.completed"""
    event_type: EventType = EventType.REPO_SCAN_COMPLETED
    payload: RepoScanPayload


class RepoFixCompletedEvent(BaseEvent):
    """Event: repo.fix.completed"""
    event_type: EventType = EventType.REPO_FIX_COMPLETED
    payload: RepoFixPayload


class ModelRunCompletedEvent(BaseEvent):
    """Event: model.run.completed"""
    event_type: EventType = EventType.MODEL_RUN_COMPLETED
    payload: ModelRunPayload


class UniverseSchemaUpdatedEvent(BaseEvent):
    """Event: universe.schema.updated"""
    event_type: EventType = EventType.UNIVERSE_SCHEMA_UPDATED
    payload: UniverseSchemaPayload


# Event type to class mapping for deserialization
EVENT_REGISTRY: dict[EventType, type[BaseEvent]] = {
    EventType.CLAWS_SESSION_STARTED: ClawsSessionStartedEvent,
    EventType.CLAWS_AGENT_REQUESTED: ClawsAgentRequestedEvent,
    EventType.MAILINH_LEAD_CREATED: MailinhLeadCreatedEvent,
    EventType.REPO_SCAN_COMPLETED: RepoScanCompletedEvent,
    EventType.REPO_FIX_COMPLETED: RepoFixCompletedEvent,
    EventType.MODEL_RUN_COMPLETED: ModelRunCompletedEvent,
    EventType.UNIVERSE_SCHEMA_UPDATED: UniverseSchemaUpdatedEvent,
}


def deserialize_event(data: dict[str, Any]) -> BaseEvent:
    """Deserialize an event from dictionary data."""
    event_type = EventType(data.get("event_type"))
    event_class = EVENT_REGISTRY.get(event_type, BaseEvent)
    return event_class.model_validate(data)
```

---

## Phase 2: Package Name Resolution (Week 1-2)

### 2.1 AMOS-Consulting Rename

**File: `AMOS-Consulting/pyproject.toml`**

```toml
[project]
name = "amos-platform"  # Change from "amos-brain"
version = "1.0.0"
description = "AMOS Platform - Central API Gateway and Orchestration Hub"

[dependencies]
amos-brain = { git = "https://github.com/trangyp/AMOS-Code.git", tag = "v14.0.0" }
amos-universe = { git = "https://github.com/trangyp/AMOS-UNIVERSE.git", tag = "v1.0.0" }
```

### 2.2 Update Imports in AMOS-Consulting

```bash
# Find and replace in all Python files
sed -i 's/from amos_brain.api_contracts/from amos_universe.contracts.pydantic/g' AMOS-Consulting/**/*.py
sed -i 's/import amos_brain.api_contracts/import amos_universe.contracts.pydantic/g' AMOS-Consulting/**/*.py
```

### 2.3 AMOS-Code as Pure Library

**File: `AMOS-Code/pyproject.toml`** (update to reference universe)

```toml
[project.optional-dependencies]
universe = ["amos-universe>=1.0.0"]  # Optional contracts integration
```

---

## Phase 3: AMOS-Consulting as Platform Hub (Week 2-4)

### 3.1 Create API Gateway

**File: `AMOS-Consulting/amos_platform/api/gateway.py`**

```python
"""AMOS Platform API Gateway - Central HTTP API for 6-repo ecosystem."""

from fastapi import FastAPI, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from amos_platform.core.brain_bridge import BrainBridge
from amos_platform.events.bus import EventBus
from amos_universe.contracts.pydantic import (
    ChatRequest, ChatResponse,
    RepoScanRequest, RepoScanResult,
    EventType, EventMetadata, BaseEvent
)

app = FastAPI(
    title="AMOS Platform API",
    version="1.0.0",
    description="Central API gateway for AMOS 6-repository ecosystem"
)

# CORS for all frontend repos
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://claws.amos.io",
        "https://app.amos.io",
        "https://invest.amos.io",
        "https://universe.amos.io",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import route modules
from .routes import chat, agents, repo, workflow, models, tasks, health, universe

app.include_router(chat.router, prefix="/v1")
app.include_router(agents.router, prefix="/v1")
app.include_router(repo.router, prefix="/v1")
app.include_router(workflow.router, prefix="/v1")
app.include_router(models.router, prefix="/v1")
app.include_router(tasks.router, prefix="/v1")
app.include_router(health.router, prefix="/v1")
app.include_router(universe.router, prefix="/v1")  # NEW: Universe endpoints
```

### 3.2 Add Universe Endpoints

**File: `AMOS-Consulting/amos_platform/api/routes/universe.py`**

```python
"""Universe API endpoints - access to canonical knowledge."""

from fastapi import APIRouter, HTTPException
from amos_universe.contracts.pydantic import EventType

router = APIRouter(prefix="/universe", tags=["universe"])

@router.get("/event-types")
async def list_event_types():
    """List all canonical event types."""
    return {
        "event_types": [
            {
                "value": e.value,
                "category": e.value.split(".")[0],
                "name": e.name
            }
            for e in EventType
        ]
    }

@router.get("/schemas/{schema_name}")
async def get_schema(schema_name: str):
    """Get a JSON schema by name."""
    # Serve schemas from amos-universe package
    pass

@router.get("/ontology/{concept}")
async def get_ontology(concept: str):
    """Get ontology definition for a concept."""
    pass
```

### 3.3 Event Bus Integration

**File: `AMOS-Consulting/amos_platform/events/bus.py`**

```python
"""Event bus for 6-repo cross-communication via Redis Streams."""

import json
import asyncio
from typing import Callable, Any
from datetime import datetime, timezone

import redis.asyncio as redis

from amos_universe.contracts.pydantic import (
    BaseEvent, EventMetadata, EventType, deserialize_event
)

class EventBus:
    """Async event bus using Redis Streams for 6-repo ecosystem."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self._redis_url = redis_url
        self._redis: redis.Redis | None = None
        self._subscribers: dict[EventType, list[Callable]] = {}
    
    async def connect(self):
        """Connect to Redis."""
        self._redis = redis.from_url(self._redis_url)
    
    async def publish(self, event: BaseEvent):
        """Publish event to the bus."""
        topic = event.event_type.value
        
        # Serialize to JSON
        data = event.model_dump_json()
        
        # Add to Redis Stream
        await self._redis.xadd(
            topic,
            {"data": data},
            maxlen=10000  # Keep last 10k events per topic
        )
        
        # Notify local subscribers
        for callback in self._subscribers.get(event.event_type, []):
            asyncio.create_task(callback(event))
    
    async def subscribe(self, event_type: EventType, callback: Callable[[BaseEvent], Any]):
        """Subscribe to specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    async def listen(self, event_types: list[EventType]):
        """Listen for events (consumer)."""
        topics = [et.value for et in event_types]
        
        # Create consumer group
        for topic in topics:
            try:
                await self._redis.xgroup_create(
                    topic, "platform", id="0", mkstream=True
                )
            except redis.ResponseError:
                pass  # Group exists
        
        while True:
            for topic in topics:
                messages = await self._redis.xreadgroup(
                    groupname="platform",
                    consumername="consumer-1",
                    streams={topic: ">"},
                    count=10,
                    block=1000,
                )
                
                for stream, msgs in messages:
                    for msg_id, fields in msgs:
                        data = json.loads(fields["data"])
                        event = deserialize_event(data)
                        
                        # Broadcast to WebSocket subscribers
                        await self._broadcast_to_ws(event)
                        
                        # Acknowledge
                        await self._redis.xack(topic, "platform", msg_id)
            
            await asyncio.sleep(0.1)
    
    async def _broadcast_to_ws(self, event: BaseEvent):
        """Broadcast event to WebSocket subscribers."""
        # Implementation in WebSocket manager
        pass
```

---

## Phase 4: Frontend Repo Integration (Week 4-6)

### 4.1 Generated SDK Usage

All frontend repos use the **generated SDK** from AMOS-UNIVERSE:

**File: `AMOS-Claws/src/api/client.ts`**

```typescript
// Generated client from AMOS-UNIVERSE/generated/typescript-client/
import { AMOSClient, EventType } from '@amos/universe-client';

const client = new AMOSClient({
  baseUrl: process.env.AMOS_API_URL || 'https://api.amos.io',
  apiKey: process.env.AMOS_API_KEY,
});

export default client;
```

### 4.2 Event Subscription

```typescript
import { useEffect } from 'react';
import { client, EventType } from '@amos/universe-client';

export function useAMOSEvents() {
  useEffect(() => {
    const ws = client.websocket.connect({
      channels: [
        EventType.REPO_SCAN_COMPLETED,
        EventType.MODEL_RUN_COMPLETED,
        EventType.CLAWS_AGENT_COMPLETED,
      ]
    });
    
    ws.onEvent((event) => {
      console.log('Received:', event.event_type, event.payload);
    });
    
    return () => ws.disconnect();
  }, []);
}
```

---

## Phase 5: Event Topics Reference (6-Repo)

| Topic | Publisher | Subscribers | Payload Schema | Description |
|-------|-----------|-------------|----------------|-------------|
| `claws.session.started` | AMOS-Claws | AMOS-Consulting, Invest | `ClawsSessionPayload` | Operator session start |
| `claws.session.ended` | AMOS-Claws | AMOS-Consulting | `ClawsSessionPayload` | Operator session end |
| `claws.agent.requested` | AMOS-Claws | AMOS-Consulting | `ClawsAgentPayload` | Agent task request |
| `claws.agent.completed` | AMOS-Consulting | AMOS-Claws | `ClawsAgentPayload` | Agent task complete |
| `mailinh.lead.created` | Mailinhconect | AMOS-Consulting, Invest | `MailinhLeadPayload` | New lead captured |
| `mailinh.contact.submitted` | Mailinhconect | AMOS-Consulting | `MailinhLeadPayload` | Contact form submission |
| `invest.report.requested` | AMOS-Invest | AMOS-Consulting | - | Report generation request |
| `invest.signal.generated` | AMOS-Consulting | AMOS-Invest | - | Investment signal |
| `repo.scan.completed` | AMOS-Consulting | Claws, Invest | `RepoScanPayload` | Repository scan done |
| `repo.scan.failed` | AMOS-Consulting | Claws | `RepoScanPayload` | Repository scan failed |
| `repo.fix.completed` | AMOS-Consulting | Claws | `RepoFixPayload` | Fix application done |
| `model.run.completed` | AMOS-Consulting | Claws, Invest | `ModelRunPayload` | Model execution done |
| `workflow.completed` | AMOS-Consulting | All | - | Workflow finished |
| `universe.schema.updated` | AMOS-UNIVERSE | All | `UniverseSchemaPayload` | Schema contract change |
| `universe.contract.published` | AMOS-UNIVERSE | All | - | New API contract version |
| `universe.ontology.changed` | AMOS-UNIVERSE | All | - | Ontology update |
| `system.alert` | AMOS-Consulting | All | - | System alert broadcast |

---

## Phase 6: Local/Offline LLM Gateway (Week 5-6)

### 6.1 Centralized LLM Router

**File: `AMOS-Consulting/amos_platform/core/llm_router.py`**

```python
"""Centralized LLM routing - single gateway for all local model providers."""

import httpx
from enum import Enum
from typing import Literal, AsyncIterator

from amos_universe.contracts.pydantic import ModelInfo, ModelProvider


class LLMBackend(str, Enum):
    """Supported local LLM backends."""
    OLLAMA = "ollama"
    LM_STUDIO = "lmstudio"
    VLLM = "vllm"
    LLAMA_CPP = "llama-cpp"
    SGLANG = "sglang"
    LITELLM = "litellm"


class LLMRouter:
    """Route LLM requests to appropriate local backend.
    
    This is the ONLY place that connects directly to Ollama, LM Studio, etc.
    All frontend repos go through this router via AMOS-Consulting API.
    """
    
    # Default ports for local backends
    DEFAULT_PORTS = {
        LLMBackend.OLLAMA: 11434,
        LLMBackend.LM_STUDIO: 1234,
        LLMBackend.VLLM: 8000,
        LLMBackend.LLAMA_CPP: 8080,
        LLMBackend.SGLANG: 30000,
        LLMBackend.LITELLM: 4000,
    }
    
    def __init__(self):
        self._backends: dict[LLMBackend, str] = {}
        self._client = httpx.AsyncClient(timeout=30.0)
    
    async def discover_backends(self) -> list[LLMBackend]:
        """Auto-discover available local backends."""
        available = []
        
        for backend, port in self.DEFAULT_PORTS.items():
            try:
                url = f"http://localhost:{port}"
                response = await self._client.get(f"{url}/health", timeout=2.0)
                if response.status_code == 200:
                    self._backends[backend] = url
                    available.append(backend)
            except httpx.ConnectError:
                pass  # Backend not running
        
        return available
    
    async def list_models(self) -> list[ModelInfo]:
        """List models from all discovered backends."""
        models = []
        
        for backend, url in self._backends.items():
            try:
                backend_models = await self._list_for_backend(backend, url)
                models.extend(backend_models)
            except Exception as e:
                print(f"Failed to list models from {backend}: {e}")
        
        return models
    
    async def _list_for_backend(self, backend: LLMBackend, url: str) -> list[ModelInfo]:
        """List models for a specific backend."""
        if backend == LLMBackend.OLLAMA:
            resp = await self._client.get(f"{url}/api/tags")
            data = resp.json()
            return [
                ModelInfo(
                    id=f"ollama/{m['name']}",
                    name=m['name'],
                    provider=ModelProvider.OLLAMA,
                    status="available"
                )
                for m in data.get('models', [])
            ]
        # ... other backends
        return []
    
    async def chat(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False
    ) -> dict | AsyncIterator[str]:
        """Send chat request to appropriate backend."""
        provider, model_name = model.split("/", 1)
        backend = LLMBackend(provider)
        backend_url = self._backends.get(backend)
        
        if not backend_url:
            raise ValueError(f"Backend {backend} not available")
        
        if backend == LLMBackend.OLLAMA:
            return await self._chat_ollama(backend_url, model_name, messages, temperature, max_tokens, stream)
        elif backend in (LLMBackend.LM_STUDIO, LLMBackend.VLLM):
            return await self._chat_openai_compatible(backend_url, model_name, messages, temperature, max_tokens, stream)
        # ... other backends
    
    async def _chat_ollama(
        self, url: str, model: str, messages: list[dict],
        temperature: float, max_tokens: int | None, stream: bool
    ) -> dict:
        """Chat with Ollama backend."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
            }
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        resp = await self._client.post(
            f"{url}/api/chat",
            json=payload
        )
        return resp.json()
    
    async def _chat_openai_compatible(
        self, url: str, model: str, messages: list[dict],
        temperature: float, max_tokens: int | None, stream: bool
    ) -> dict:
        """Chat with OpenAI-compatible backend (LM Studio, vLLM)."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        resp = await self._client.post(
            f"{url}/v1/chat/completions",
            json=payload
        )
        return resp.json()
```

---

## Phase 7: OpenClaw Integration (Week 6-7)

### 7.1 OpenClaw Configuration

**File: `AMOS-Claws/config/openclaw.yaml`**

```yaml
openclaw:
  enabled: true
  
  # Tool definitions from AMOS-Consulting
  tool_discovery_endpoint: "https://api.amos.io/v1/tools"
  
  # Agent configuration
  agents:
    repo_scanner:
      description: "Scan repositories for issues"
      endpoint: "https://api.amos.io/v1/repo/scan"
      events:
        - "repo.scan.completed"
        - "repo.scan.failed"
    
    code_fixer:
      description: "Apply fixes to repositories"
      endpoint: "https://api.amos.io/v1/repo/fix"
      events:
        - "repo.fix.completed"
        - "repo.fix.failed"
    
    model_runner:
      description: "Run local LLM models"
      endpoint: "https://api.amos.io/v1/models/run"
      events:
        - "model.run.completed"

  # WebSocket for real-time tool feedback
  websocket:
    url: "wss://api.amos.io/v1/ws/stream"
    auto_reconnect: true
    channels:
      - "claws.agent.*"
      - "repo.scan.*"
      - "repo.fix.*"
```

---

## Phase 8: Testing & Validation (Week 7-8)

### 8.1 Integration Tests

**File: `tests/integration/test_6_repo_integration.py`**

```python
"""Integration tests for 6-repo architecture."""

import pytest
import asyncio

from amos_integration_client import AMOSClient
from amos_universe.contracts.pydantic import (
    ChatRequest, RepoScanRequest,
    EventType, ClawsAgentPayload
)


@pytest.mark.asyncio
async def test_universe_contracts_import():
    """Test that all repos can import universe contracts."""
    from amos_universe.contracts.pydantic import (
        ChatRequest, ChatResponse,
        EventType, BaseEvent
    )
    
    # Should be able to create instances
    request = ChatRequest(
        message="Hello",
        context={"session_id": "test"}
    )
    assert request.message == "Hello"


@pytest.mark.asyncio
async def test_event_serialization():
    """Test event serialization/deserialization."""
    from amos_universe.contracts.pydantic import (
        BaseEvent, EventMetadata, EventType,
        ClawsAgentPayload, ClawsAgentRequestedEvent
    )
    
    payload = ClawsAgentPayload(
        task_id="task-123",
        agent_type="repo_scan",
        target_repo="https://github.com/test/repo"
    )
    
    event = ClawsAgentRequestedEvent(
        event_type=EventType.CLAWS_AGENT_REQUESTED,
        metadata=EventMetadata(
            event_id="evt-123",
            timestamp=datetime.now(timezone.utc),
            source="amos-claws"
        ),
        payload=payload
    )
    
    # Serialize and deserialize
    data = event.model_dump()
    restored = deserialize_event(data)
    
    assert restored.event_type == EventType.CLAWS_AGENT_REQUESTED
    assert restored.payload.task_id == "task-123"


@pytest.mark.asyncio
async def test_chat_through_platform():
    """Test chat flows through AMOS-Consulting."""
    client = AMOSClient(base_url="http://localhost:8000")
    
    response = await client.chat.send_message(
        message="Hello, AMOS!",
        workspace_id="test-ws"
    )
    
    assert response.message is not None
    assert response.id is not None


@pytest.mark.asyncio
async def test_local_llm_gateway():
    """Test local LLM routing."""
    from amos_platform.core.llm_router import LLMRouter
    
    router = LLMRouter()
    backends = await router.discover_backends()
    
    # Should discover Ollama if running
    if backends:
        models = await router.list_models()
        assert isinstance(models, list)


@pytest.mark.asyncio
async def test_cross_repo_events():
    """Test event bus across repos."""
    from amos_platform.events.bus import EventBus
    from amos_universe.contracts.pydantic import EventType
    
    bus = EventBus(redis_url="redis://localhost:6379")
    await bus.connect()
    
    received = []
    
    async def handler(event):
        received.append(event)
    
    await bus.subscribe(EventType.CLAWS_AGENT_REQUESTED, handler)
    
    # Publish event
    from amos_universe.contracts.pydantic import (
        ClawsAgentRequestedEvent, ClawsAgentPayload,
        EventMetadata
    )
    
    event = ClawsAgentRequestedEvent(
        event_type=EventType.CLAWS_AGENT_REQUESTED,
        metadata=EventMetadata(
            event_id="test-123",
            timestamp=datetime.now(timezone.utc),
            source="test"
        ),
        payload=ClawsAgentPayload(
            task_id="task-123",
            agent_type="test"
        )
    )
    
    await bus.publish(event)
    await asyncio.sleep(0.1)
    
    assert len(received) == 1
```

---

## Implementation Checklist

### Phase 1: AMOS-UNIVERSE Setup
- [ ] Create AMOS-UNIVERSE repository
- [ ] Migrate contracts from AMOS-Code
- [ ] Add event definitions (EventType, payloads)
- [ ] Create package configuration
- [ ] Publish to GitHub

### Phase 2: Package Resolution
- [ ] Rename AMOS-Consulting to `amos-platform`
- [ ] Update imports to use `amos_universe`
- [ ] Update AMOS-Code to reference universe optionally

### Phase 3: API Gateway
- [ ] Create FastAPI gateway in AMOS-Consulting
- [ ] Implement all REST endpoints
- [ ] Add universe endpoints (/v1/universe/*)
- [ ] Add authentication/authorization

### Phase 4: WebSocket
- [ ] Implement WebSocket server
- [ ] Add channel subscription
- [ ] Test real-time updates

### Phase 5: Event Bus
- [ ] Set up Redis Streams
- [ ] Implement 6-repo event topics
- [ ] Add universe schema change events
- [ ] Test cross-repo events

### Phase 6: LLM Router
- [ ] Create centralized LLM router
- [ ] Add Ollama integration
- [ ] Add LM Studio integration
- [ ] Add vLLM integration
- [ ] Test model routing

### Phase 7: OpenClaw Integration
- [ ] Configure OpenClaw tool definitions
- [ ] Connect to AMOS-Consulting API
- [ ] Test agent workflows

### Phase 8: Frontend Integration
- [ ] Update AMOS-Claws to use API
- [ ] Update Mailinhconect to use API
- [ ] Update AMOS-Invest to use API
- [ ] Add WebSocket to all frontends
- [ ] Use generated SDK from AMOS-UNIVERSE

### Phase 9: Deployment
- [ ] Configure subdomains (add universe.amos.io)
- [ ] Set up SSL certificates
- [ ] Deploy to staging
- [ ] Deploy to production

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (p95) | < 200ms | Prometheus metrics |
| WebSocket Latency | < 50ms | Client-side timing |
| Event Delivery Time | < 100ms | Redis latency |
| Cross-repo Import Count | 0 | Static analysis |
| Package Name Conflicts | 0 | Pip installation |
| Universe Contract Changes | Tracked | Schema registry |
| System Availability | 99.9% | Uptime monitoring |

---

## Conclusion

This 6-repository architecture provides:

- **AMOS-UNIVERSE**: Single source of truth for ontology, contracts, schemas
- **AMOS-Consulting**: Central API hub for all operational traffic
- **AMOS-Code**: Pure library for core cognitive functions
- **Frontends (3)**: Clean clients connecting through standardized API
- **Type Safety**: Generated clients from shared OpenAPI specs
- **Event-Driven**: Real-time cross-repo communication via event bus
- **Local LLM**: Centralized access to Ollama, LM Studio, etc.
- **OpenClaw**: Explicit integration for agent workflows

The result is **one coherent platform** with 6 well-defined repositories, each with a single responsibility.
