# AMOS API Contracts

Shared Pydantic models for the hub-and-spoke architecture.

## Overview

The API contracts package (`amos_brain.api_contracts`) defines all request/response models used between:
- **AMOS-Consulting** (API hub/backend)
- **AMOS-Claws** (agent frontend)
- **Mailinhconect** (product frontend)
- **AMOS-Invest** (investor frontend)

By centralizing these contracts in `AMOS-Code`, all repositories can import them for type-safe API communication.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 AMOS-Consulting API Hub                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Imports: amos_brain.api_contracts.*                  │  │
│  │  Provides: /v1/chat, /v1/brain, /v1/repo, etc.      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
           ▲                        ▲
           │ HTTP + Pydantic        │ HTTP + Pydantic
     ┌─────┴──────┐           ┌─────┴──────┐
     │ AMOS-Claws │           │ Mailinhconect│
     └────────────┘           └──────────────┘
```

## Installation

### For AMOS-Consulting (backend)
```toml
[project]
name = "amos-consulting"  # Renamed from amos-brain

dependencies = [
    "amos-brain>=14.0.0",  # Core library + contracts
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
]
```

### For Client Repos
```toml
[project]
name = "amos-claws"  # or mailinh-connect, amos-invest

dependencies = [
    "amos-brain>=14.0.0",  # For contracts only
    "httpx>=0.25.0",  # For API calls
]
```

Or install contracts only (no heavy dependencies):
```bash
pip install amos-brain
```

## Usage

### In AMOS-Consulting (Backend)
```python
from fastapi import FastAPI
from amos_brain.api_contracts import ChatRequest, ChatResponse

app = FastAPI()

@app.post("/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Process chat
    return ChatResponse(
        message="Hello!",
        conversation_id=request.context.conversation_id or "new",
        session_id=request.context.session_id,
        model="llama3.1:8b"
    )
```

### In AMOS-Claws (Client)
```python
import httpx
from amos_brain.api_contracts import ChatRequest, ChatContext

async def send_chat(message: str, session_id: str):
    request = ChatRequest(
        message=message,
        context=ChatContext(session_id=session_id)
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.yourdomain.com/v1/chat",
            json=request.model_dump()
        )
        return response.json()
```

## Contract Categories

### Chat Contracts (`chat.py`)
| Model | Purpose |
|-------|---------|
| `ChatRequest` | Send a message to the assistant |
| `ChatResponse` | Receive assistant response |
| `ChatMessage` | Individual message in history |
| `ChatContext` | Session/workspace context |
| `ConversationSummary` | Conversation metadata |

### Repo Contracts (`repo.py`)
| Model | Purpose |
|-------|---------|
| `RepoScanRequest` | Request repository scan |
| `RepoScanResult` | Scan results with issues |
| `RepoFixRequest` | Request fixes for issues |
| `RepoFixResult` | Applied/previewed changes |
| `ScanIssue` | Individual issue found |
| `FileChange` | Proposed file modification |

### Model Contracts (`models.py`)
| Model | Purpose |
|-------|---------|
| `ModelInfo` | Available LLM information |
| `ModelCapabilities` | Model features (tools, vision, etc) |
| `ModelProvider` | Provider enum (Ollama, vLLM, etc) |
| `ModelRequest` | Direct model inference request |
| `ModelResponse` | Model inference response |

### Session Contracts (`session.py`)
| Model | Purpose |
|-------|---------|
| `User` | User account information |
| `Workspace` | Workspace/tenant information |
| `SessionContext` | API session context |
| `UserSession` | Combined session data |

### Brain Contracts (`brain.py`)
| Model | Purpose |
|-------|---------|
| `BrainRunRequest` | Execute AMOS brain cycle |
| `BrainRunResponse` | Brain execution results |
| `StateGraphInput` | Initial state variables |
| `BranchResult` | Generated branch data |
| `MorphExecution` | Morph execution result |

### Workflow Contracts (`workflow.py`)
| Model | Purpose |
|-------|---------|
| `WorkflowRunRequest` | Execute workflow |
| `WorkflowRunResponse` | Workflow results |
| `WorkflowStatus` | Status enum |
| `TaskResult` | Individual task result |

### Error Contracts (`errors.py`)
| Model | Purpose |
|-------|---------|
| `ApiError` | Standard error response |
| `ErrorCode` | Error code enum |
| `ValidationError` | Field-level validation errors |
| `AuthenticationError` | Auth failure |
| `NotFoundError` | Resource not found |

## API Endpoints Reference

### Chat
```
POST /v1/chat
  Request: ChatRequest
  Response: ChatResponse
```

### Brain
```
POST /v1/brain/run
  Request: BrainRunRequest
  Response: BrainRunResponse
```

### Repo Doctor
```
POST /v1/repo/scan
  Request: RepoScanRequest
  Response: RepoScanResult

POST /v1/repo/fix
  Request: RepoFixRequest
  Response: RepoFixResult
```

### Models
```
GET /v1/models
  Response: list[ModelInfo]

POST /v1/models/run
  Request: ModelRequest
  Response: ModelResponse
```

### Workflows
```
POST /v1/workflow/run
  Request: WorkflowRunRequest
  Response: WorkflowRunResponse
```

### Health
```
GET /v1/health
  Response: {"status": "healthy", ...}
```

## Domain Structure

Recommended subdomain setup:

```
api.yourdomain.com      → AMOS-Consulting API
claws.yourdomain.com    → AMOS-Claws UI
mailinh.yourdomain.com  → Mailinhconect UI
invest.yourdomain.com   → AMOS-Invest UI
```

## Migration Guide

### Step 1: Fix Package Name Collision
In `AMOS-Consulting/pyproject.toml`:
```toml
[project]
name = "amos-consulting"  # NOT amos-brain
```

### Step 2: Add Dependency
In `AMOS-Consulting/pyproject.toml`:
```toml
dependencies = [
    "amos-brain>=14.0.0",
    ...
]
```

### Step 3: Import Contracts
```python
# Instead of copying models, import from core
from amos_brain.api_contracts import ChatRequest, ChatResponse
```

### Step 4: Update Clients
Replace direct function calls with HTTP API:
```python
# OLD (spaghetti):
from amos_brain import some_function
result = some_function()

# NEW (hub-and-spoke):
import httpx
response = await client.post("https://api.../v1/...", json=data)
```

## Validation

All contracts use Pydantic v2 for:
- Type validation
- Field constraints (min/max length, ranges)
- JSON serialization
- OpenAPI schema generation

Example validation:
```python
# This will raise ValidationError
ChatRequest(message="", context=ChatContext(session_id="test"))
# Error: message must be at least 1 character

# This will pass
ChatRequest(message="Hello", context=ChatContext(session_id="test"))
```

## Versioning

API contracts follow semantic versioning:
- **Major**: Breaking changes to existing models
- **Minor**: New models/fields (backward compatible)
- **Patch**: Bug fixes, documentation

When upgrading:
1. Update `amos-brain` version in client repos
2. Test for any breaking changes
3. Deploy backend first, then clients
