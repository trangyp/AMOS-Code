# AMOS-UNIVERSE Specification

## Canonical Knowledge / Ontology / Universe Layer

---

## Executive Summary

AMOS-UNIVERSE is the **sixth repository** in the AMOS ecosystem, serving as the **canonical source of truth** for:

- **Ontology**: Domain vocabulary, concept definitions, relationships
- **API Contracts**: Shared Pydantic models, OpenAPI specifications  
- **Event Schemas**: Canonical event type definitions
- **Architecture**: ADRs, system topology, repo role definitions
- **Generated Artifacts**: Client SDKs, server stubs, type definitions

> **Core Principle**: AMOS-UNIVERSE owns the **what** (contracts, schemas, definitions). Implementation repos own the **how** (runtime behavior, business logic).

---

## Repository Identity

| Property | Value |
|----------|-------|
| **Repository** | AMOS-UNIVERSE |
| **Package Name** | `amos-universe` |
| **Public Endpoint** | `universe.amos.io` |
| **Role** | Canonical knowledge / ontology / universe layer |
| **Language** | Python (contracts), YAML/JSON (schemas), Markdown (docs) |

---

## Directory Structure

```
AMOS-UNIVERSE/
├── README.md                      # Main documentation
├── pyproject.toml                 # Package configuration
├── LICENSE                        # MIT License
│
├── ontology/                      # Domain ontology
│   ├── README.md
│   ├── core-concepts.yaml        # Core AMOS concepts
│   ├── repo-roles.yaml           # Repository role definitions
│   ├── event-ontology.yaml       # Event type taxonomy
│   └── domain-models.yaml        # Domain entity definitions
│
├── contracts/                     # API contracts
│   ├── pydantic/                 # Python Pydantic models
│   │   ├── __init__.py
│   │   ├── base.py               # BaseAMOSModel, TimestampsMixin
│   │   ├── chat.py               # ChatRequest, ChatResponse
│   │   ├── repo.py               # RepoScanRequest, RepoFixResult
│   │   ├── models.py             # ModelInfo, ModelCapabilities
│   │   ├── session.py            # User, Workspace, SessionContext
│   │   ├── brain.py              # BrainRunRequest, BrainRunResponse
│   │   ├── workflow.py           # WorkflowRunRequest
│   │   ├── errors.py             # ApiError, ErrorCode
│   │   └── events.py             # EventType, BaseEvent, payloads
│   │
│   ├── schemas/                  # JSON Schema definitions
│   │   ├── event-schemas/        # Event payload schemas
│   │   ├── request-schemas/      # API request schemas
│   │   └── response-schemas/     # API response schemas
│   │
│   └── openapi/                  # OpenAPI specifications
│       ├── amos-core-api.yaml    # Core AMOS API spec
│       └── amos-consulting-api.yaml # Consulting API spec
│
├── specs/                        # System specifications
│   ├── integration/              # Integration specs
│   │   ├── 6-repo-architecture.md
│   │   ├── event-topics.md
│   │   ├── dependency-rules.md
│   │   └── communication-lanes.md
│   │
│   ├── llm-gateway/              # LLM gateway specification
│   │   ├── providers.md          # Ollama, LM Studio, vLLM, etc.
│   │   ├── routing.md            # Model routing rules
│   │   └── capabilities.md       # Supported features per provider
│   │
│   └── security/                 # Security requirements
│       ├── auth.md               # Authentication spec
│       ├── authorization.md      # RBAC spec
│       └── compliance.md         # GDPR, SOC2 requirements
│
├── adrs/                         # Architecture Decision Records
│   ├── 001-6-repo-architecture.md
│   ├── 002-amos-universe-role.md
│   ├── 003-event-bus-selection.md
│   ├── 004-llm-gateway-design.md
│   ├── 005-openclaw-integration.md
│   ├── 006-contract-versioning.md
│   └── 007-ontology-management.md
│
├── generated/                    # Auto-generated artifacts
│   ├── python-client/            # Generated Python SDK
│   │   ├── amos_client/
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   ├── models.py
│   │   │   └── websocket.py
│   │   └── setup.py
│   │
│   ├── typescript-client/        # Generated TypeScript SDK
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── client.ts
│   │   │   ├── models.ts
│   │   │   └── websocket.ts
│   │   └── package.json
│   │
│   └── server-stubs/             # Generated server stubs
│       ├── fastapi-stubs/        # FastAPI route stubs
│       └── tests/                # Contract validation tests
│
├── scripts/                      # Build and generation scripts
│   ├── generate_openapi.py       # Generate OpenAPI from Pydantic
│   ├── generate_clients.py       # Generate SDKs from OpenAPI
│   ├── validate_contracts.py     # Validate contract consistency
│   └── publish_schemas.py        # Publish to schema registry
│
├── tests/                        # Test suite
│   ├── test_contracts.py         # Contract validation tests
│   ├── test_events.py            # Event serialization tests
│   └── test_ontology.py          # Ontology validation tests
│
└── docs/                         # Documentation
    ├── system-map.md             # Visual system architecture
    ├── getting-started.md        # Quick start guide
    ├── contributing.md           # Contribution guidelines
    ├── api-reference/            # API documentation
    └── ontology-reference/       # Ontology documentation
```

---

## Package Configuration

### pyproject.toml

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
keywords = ["amos", "contracts", "schemas", "ontology", "api"]

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

# Core dependencies - minimal, lightweight
dependencies = [
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "typing-extensions>=4.0.0",
]

# Optional dependencies for generated clients
[project.optional-dependencies]
generated-python = [
    "httpx>=0.25.0",
    "websockets>=12.0",
]
generated-ts = [
    "openapi-typescript",  # For TypeScript generation
]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
    "openapi-generator-cli",
]

[project.urls]
Homepage = "https://github.com/trangyp/AMOS-UNIVERSE"
Documentation = "https://docs.amos.io/universe"
Repository = "https://github.com/trangyp/AMOS-UNIVERSE"
Issues = "https://github.com/trangyp/AMOS-UNIVERSE/issues"

[tool.setuptools.packages.find]
where = ["."]
include = ["contracts*", "ontology*"]
exclude = ["tests*", "scripts*", "generated*"]

[tool.black]
line-length = 100
target-version = ['py310', 'py311', 'py312']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W", "UP", "B", "C4"]

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

---

## Ontology Specification

### Core Concepts

```yaml
# ontology/core-concepts.yaml

ontology:
  version: "1.0.0"
  description: "Core concepts in the AMOS ecosystem"

concepts:
  Repository:
    description: "A code repository in the AMOS ecosystem"
    attributes:
      - name: id
        type: string
        description: "Unique identifier"
      - name: name
        type: string
        description: "Repository name"
      - name: role
        type: enum[core, platform, frontend, universe]
        description: "Repository role in ecosystem"
      - name: package_name
        type: string
        description: "Python package name"

  Agent:
    description: "An autonomous agent that performs tasks"
    attributes:
      - name: id
        type: string
      - name: type
        type: enum[repo_scanner, code_fixer, model_runner]
      - name: status
        type: enum[idle, running, completed, failed]
      - name: task_queue
        type: reference[TaskQueue]

  Task:
    description: "A unit of work to be performed"
    attributes:
      - name: id
        type: string
      - name: type
        type: string
      - name: status
        type: enum[pending, running, completed, failed, cancelled]
      - name: priority
        type: enum[low, normal, high, urgent]
      - name: payload
        type: object

  Event:
    description: "A domain event in the event bus"
    attributes:
      - name: event_id
        type: string
      - name: event_type
        type: reference[EventType]
      - name: timestamp
        type: datetime
      - name: source
        type: reference[Repository]
      - name: payload
        type: object
      - name: metadata
        type: EventMetadata

  EventType:
    description: "Canonical event type taxonomy"
    values:
      - claws.session.started
      - claws.session.ended
      - claws.agent.requested
      - claws.agent.completed
      - mailinh.lead.created
      - mailinh.contact.submitted
      - invest.report.requested
      - invest.signal.generated
      - repo.scan.completed
      - repo.scan.failed
      - repo.fix.completed
      - repo.fix.failed
      - model.run.completed
      - model.run.failed
      - workflow.started
      - workflow.completed
      - workflow.failed
      - universe.schema.updated
      - universe.contract.published
      - universe.ontology.changed
      - system.alert
      - system.health.changed

  Model:
    description: "A machine learning model"
    attributes:
      - name: id
        type: string
      - name: name
        type: string
      - name: provider
        type: enum[ollama, lmstudio, vllm, llama_cpp, sglang, litellm]
      - name: capabilities
        type: array[Capability]
      - name: status
        type: enum[available, loading, loaded, unavailable]

  Workspace:
    description: "A multi-tenant workspace"
    attributes:
      - name: id
        type: string
      - name: name
        type: string
      - name: slug
        type: string
      - name: plan
        type: enum[free, starter, professional, enterprise]

relationships:
  - from: Repository
    to: Event
    type: publishes
    description: "A repository publishes events"

  - from: Repository
    to: Event
    type: subscribes
    description: "A repository subscribes to events"

  - from: Agent
    to: Task
    type: executes
    description: "An agent executes tasks"

  - from: Task
    to: Event
    type: generates
    description: "Task execution generates events"

  - from: Model
    to: Task
    type: processes
    description: "A model processes inference tasks"
```

---

## Contract Specifications

### Pydantic Models

All contracts use **Pydantic v2** for:
- Type validation
- Field constraints
- JSON serialization
- OpenAPI schema generation

### Base Model

```python
# contracts/pydantic/base.py

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class BaseAMOSModel(BaseModel):
    """Base model for all AMOS contracts."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",  # Reject unknown fields
    )
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json()
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return self.model_dump()


class TimestampsMixin(BaseModel):
    """Mixin for models with created/updated timestamps."""
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp (UTC)"
    )
```

### Event System

```python
# contracts/pydantic/events.py (excerpt)

class EventType(str, Enum):
    """Canonical event types for the AMOS 6-repo ecosystem."""
    
    # Layer 09 - Social/Agent (AMOS-Claws)
    CLAWS_SESSION_STARTED = "claws.session.started"
    CLAWS_SESSION_ENDED = "claws.session.ended"
    CLAWS_AGENT_REQUESTED = "claws.agent.requested"
    CLAWS_AGENT_COMPLETED = "claws.agent.completed"
    CLAWS_TOOL_INVOKED = "claws.tool.invoked"
    
    # Layer 14 - Interfaces (Mailinhconect)
    MAILINH_LEAD_CREATED = "mailinh.lead.created"
    MAILINH_CONTACT_SUBMITTED = "mailinh.contact.submitted"
    MAILINH_USER_REGISTERED = "mailinh.user.registered"
    
    # Layer 14 - Interfaces (AMOS-Invest)
    INVEST_REPORT_REQUESTED = "invest.report.requested"
    INVEST_SIGNAL_GENERATED = "invest.signal.generated"
    INVEST_ANALYTICS_VIEWED = "invest.analytics.viewed"
    
    # Layer 01 - Brain (Repository operations)
    REPO_SCAN_COMPLETED = "repo.scan.completed"
    REPO_SCAN_FAILED = "repo.scan.failed"
    REPO_FIX_COMPLETED = "repo.fix.completed"
    REPO_FIX_FAILED = "repo.fix.failed"
    
    # Layer 10 - Memory (Model operations)
    MODEL_RUN_COMPLETED = "model.run.completed"
    MODEL_RUN_FAILED = "model.run.failed"
    MODEL_LOADED = "model.loaded"
    MODEL_UNLOADED = "model.unloaded"
    
    # Layer 06 - Muscle (Workflow operations)
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_STEP_COMPLETED = "workflow.step.completed"
    
    # Layer 11 - Canon (AMOS-UNIVERSE events) ⭐ NEW
    UNIVERSE_SCHEMA_UPDATED = "universe.schema.updated"
    UNIVERSE_CONTRACT_PUBLISHED = "universe.contract.published"
    UNIVERSE_ONTOLOGY_CHANGED = "universe.ontology.changed"
    UNIVERSE_ADR_PUBLISHED = "universe.adr.published"
    
    # Layer 00 - Root (System events)
    SYSTEM_ALERT = "system.alert"
    SYSTEM_HEALTH_CHANGED = "system.health.changed"
    SYSTEM_MAINTENANCE_SCHEDULED = "system.maintenance.scheduled"


class EventMetadata(BaseAMOSModel):
    """Metadata attached to all events."""
    
    event_id: str = Field(..., description="Unique event UUID")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Event timestamp (UTC)"
    )
    source: str = Field(..., description="Source repository name")
    version: str = Field(default="1.0", description="Event schema version")
    trace_id: str | None = Field(None, description="Distributed trace ID")
    tenant_id: str | None = Field(None, description="Multi-tenant workspace ID")
    priority: Literal["low", "normal", "high", "urgent"] = "normal"


class BaseEvent(BaseAMOSModel):
    """Base class for all AMOS events."""
    
    event_type: EventType
    metadata: EventMetadata
    payload: dict[str, Any] = Field(default_factory=dict)
```

---

## Dependency Rules

### Direction

```
AMOS-UNIVERSE
      │
      ├──► AMOS-Code (optional)
      │
      ├──► AMOS-Consulting (required)
      │
      ├──► AMOS-Claws (via generated SDK)
      │
      ├──► Mailinhconect (via generated SDK)
      │
      └──► AMOS-Invest (via generated SDK)
```

### Critical Rule

**NO reverse dependency from AMOS-UNIVERSE into runtime repos.**

AMOS-UNIVERSE is a **pure contract/schema package** with no runtime dependencies.

### Implementation Example

```python
# In AMOS-Consulting
from amos_universe.contracts.pydantic import (
    ChatRequest,
    ChatResponse,
    EventType,
    RepoScanRequest,
)

@app.post("/v1/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    # Use universe contracts for type safety
    ...
```

```typescript
// In AMOS-Claws (using generated TypeScript SDK)
import { AMOSClient, ChatRequest, EventType } from '@amos/universe-client';

const client = new AMOSClient({ baseUrl: 'https://api.amos.io' });

await client.chat({
    message: 'Hello',
    workspace_id: 'ws-123'
});

// Type-safe event handling
client.websocket.onEvent(EventType.REPO_SCAN_COMPLETED, (event) => {
    console.log('Scan completed:', event.payload.scan_id);
});
```

---

## Schema Registry

### Versioning Strategy

Events and contracts follow **semantic versioning**:

- **Major**: Breaking changes to existing models
- **Minor**: New models/fields (backward compatible)
- **Patch**: Bug fixes, documentation

### Schema Publication

When schemas change in AMOS-UNIVERSE:

1. **Version bump** in package version
2. **Generate new SDKs** (Python, TypeScript)
3. **Publish event** `universe.schema.updated`
4. **Notify all repos** via event bus
5. **Repos update** their universe dependency

### Example Schema Change Flow

```
1. Developer updates ChatRequest in AMOS-UNIVERSE
2. PR merged, version bumped to 1.1.0
3. CI generates new SDKs
4. Event published: universe.schema.updated
   payload: {
       schema_name: "ChatRequest",
       schema_version: "1.1.0",
       change_type: "updated",
       affected_repos: ["AMOS-Consulting", "AMOS-Claws"]
   }
5. Repos receive notification, update dependency
```

---

## ADR Format

### Architecture Decision Records

```markdown
# ADR-002: AMOS-UNIVERSE Role

## Status
Accepted

## Context
The 6-repo AMOS ecosystem needs a canonical source of truth for:
- API contracts (shared between repos)
- Event schemas (cross-repo communication)
- Ontology (domain vocabulary)
- Architecture decisions (ADRs)

## Decision
Create AMOS-UNIVERSE as a dedicated repository for:
1. Pydantic contract models
2. JSON Schema definitions
3. OpenAPI specifications
4. Domain ontology (YAML)
5. Architecture Decision Records
6. Generated client SDKs

## Consequences

### Positive
- Single source of truth for contracts
- Type-safe cross-repo communication
- Versioned schema evolution
- Auto-generated SDKs

### Negative
- Additional repository to maintain
- Need to coordinate changes across repos
- Potential version drift if not managed

## Related
- ADR-001: 6-Repo Architecture
- ADR-003: Event Bus Selection
```

---

## Success Criteria

AMOS-UNIVERSE is successful when:

1. ✅ **All 6 repos can import contracts** without conflicts
2. ✅ **Events flow** through the bus with type safety
3. ✅ **Generated SDKs** work in frontend repos
4. ✅ **Schema changes** are tracked and versioned
5. ✅ **Ontology is documented** and queryable
6. ✅ **No reverse dependencies** into runtime repos
7. ✅ **ADRs are accessible** and up to date
8. ✅ **Documentation** explains the system clearly

---

## Next Steps

1. **Create repository** `trangyp/AMOS-UNIVERSE`
2. **Migrate contracts** from AMOS-Code
3. **Add event definitions** with payloads
4. **Create ontology** YAML files
5. **Write ADRs** for key decisions
6. **Set up CI** for SDK generation
7. **Publish package** to PyPI (or internal registry)
8. **Update all repos** to use universe contracts

