# AMOS Hub-and-Spoke Architecture Restructure

## Goal
Transform five separate repos into one hub + four clients architecture.

## Target Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    AMOS-Consulting                           │
│              (API Hub / Control Plane)                        │
│         Package: amos-consulting (renamed)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   API Layer │  │  LLM Router │  │  Session/Auth       │  │
│  │  /v1/chat   │  │  Ollama     │  │  Repo Doctor        │  │
│  │  /v1/brain  │  │  LM Studio  │  │  Task Execution     │  │
│  │  /v1/repo   │  │  vLLM       │  │  Dashboard          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                           │                                   │
│                    imports │                                   │
│                           ▼                                   │
│              ┌─────────────────────┐                         │
│              │     AMOS-Code       │                         │
│              │  (Core Library)     │                         │
│              │ Package: amos-brain │                         │
│              └─────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
         │              │              │
         │ HTTP API     │ HTTP API     │ HTTP API
         ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌────────────────┐
│ AMOS-Claws   │ │Mailinhconect │ │  AMOS-Invest   │
│ (Agent UI)   │ │(Product)     │ │  (Investor)    │
│              │ │              │ │                │
│ Chat/Agent   │ │ Public Site  │ │  Dashboards    │
│ Workflows    │ │ Forms        │ │  Reports       │
└──────────────┘ └──────────────┘ └────────────────┘
```

## Repository Roles

| Repository | Role | Package Name | Talks To |
|------------|------|--------------|----------|
| AMOS-Code | Core brain library | `amos-brain` | Imported by AMOS-Consulting |
| AMOS-Consulting | API hub / control plane | `amos-consulting` | Imports AMOS-Code, serves HTTP |
| AMOS-Claws | Agent frontend | `amos-claws` | HTTP to AMOS-Consulting |
| Mailinhconect | Product frontend | `mailinh-connect` | HTTP to AMOS-Consulting |
| AMOS-Invest | Investor frontend | `amos-invest` | HTTP to AMOS-Consulting |

## Domain Structure

```
api.yourdomain.com      → AMOS-Consulting API
claws.yourdomain.com    → AMOS-Claws UI
mailinh.yourdomain.com  → Mailinhconect UI
invest.yourdomain.com   → AMOS-Invest UI
```

## Phase 1: Fix Package Name Collision (Immediate)

### AMOS-Code (Current Repo)
- **Keep** as `amos-brain` ✓
- **Remove** any FastAPI/main runtime code (move to AMOS-Consulting)
- **Expose** clean library interface

### AMOS-Consulting (External Repo)
**Change in `pyproject.toml`:**
```toml
[project]
name = "amos-consulting"  # Changed from "amos-brain"
# ... rest stays same
```

**Change in imports:**
```python
# Before (wrong - internal code)
from amos_brain import something

# After (correct - library dependency)
from amos_brain import something  # This still works - imports the library
```

**Add dependency:**
```toml
dependencies = [
    "amos-brain>=14.0.0",  # Depends on core library
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
    # ... etc
]
```

## Phase 2: API Contract Definition (In AMOS-Code)

The shared API contracts live in AMOS-Code so all clients can import them.

### Files Created:
- `amos_brain/api_contracts/` - Pydantic models for API
- `amos_brain/api_contracts/chat.py` - ChatRequest, ChatResponse
- `amos_brain/api_contracts/repo.py` - RepoScanRequest, RepoScanResult
- `amos_brain/api_contracts/models.py` - ModelInfo, ModelCapabilities
- `amos_brain/api_contracts/session.py` - UserSession, SessionContext
- `amos_brain/api_contracts/errors.py` - ApiError, ErrorCode
- `AMOS_API_CONTRACTS.md` - Documentation

## Phase 3: Clean Library Interface

### AMOS-Code Public API
```python
# What AMOS-Consulting imports from AMOS-Code
from amos_brain import (
    # Core reasoning
    BrainKernel,
    CollapseKernel,
    CascadeKernel,
    
    # Models
    StateGraph,
    Branch,
    Morph,
    
    # Equations
    EquationRegistry,
    execute_equation,
    
    # Contracts (for API validation)
    ChatRequest,
    ChatResponse,
    RepoScanRequest,
    RepoScanResult,
    ModelInfo,
    UserSession,
    ApiError,
)
```

## Phase 4: AMOS-Consulting API Endpoints

### Implementation Required (in AMOS-Consulting repo)
```python
# AMOS-Consulting main.py
from fastapi import FastAPI
from amos_brain import BrainKernel, ChatRequest, ChatResponse

app = FastAPI(title="AMOS Consulting API")

@app.post("/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for all clients."""
    brain = BrainKernel()
    # ... process
    return ChatResponse(...)

@app.post("/v1/brain/run")
async def brain_run(request: BrainRunRequest):
    """Direct brain execution."""
    pass

@app.post("/v1/repo/scan")
async def repo_scan(request: RepoScanRequest):
    """Repo doctor scanning."""
    pass

@app.post("/v1/repo/fix")
async def repo_fix(request: RepoFixRequest):
    """Repo doctor fixes."""
    pass

@app.get("/v1/models")
async def list_models():
    """Available LLM models."""
    # Query Ollama, LM Studio, etc
    pass

@app.get("/v1/health")
async def health():
    """Health check."""
    pass
```

## Phase 5: Client Integration

### AMOS-Claws (calls AMOS-Consulting)
```python
import httpx

AMOS_API = "https://api.yourdomain.com/v1"

async def chat_with_amos(message: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AMOS_API}/chat",
            json={"message": message, "session_id": "..."}
        )
        return response.json()
```

### Mailinhconect (calls AMOS-Consulting)
Same pattern - HTTP calls to API.

### AMOS-Invest (calls AMOS-Consulting)
Same pattern - HTTP calls to API.

## What NOT To Do

❌ **Don't** let all repos import each other
❌ **Don't** let each repo talk to Ollama separately
❌ **Don't** keep two packages named `amos-brain`
❌ **Don't** put business logic in HTML frontends

## Migration Checklist

- [ ] 1. Rename AMOS-Consulting package to `amos-consulting`
- [ ] 2. Add `amos-brain>=14.0.0` dependency to AMOS-Consulting
- [ ] 3. Create API contracts in AMOS-Code (this PR)
- [ ] 4. Implement AMOS-Consulting API endpoints
- [ ] 5. Update AMOS-Claws to use HTTP API
- [ ] 6. Update Mailinhconect to use HTTP API
- [ ] 7. Update AMOS-Invest to use HTTP API
- [ ] 8. Document domain setup (subdomains)
- [ ] 9. Test end-to-end flow
- [ ] 10. Remove direct imports between repos

## Files Created in This PR

1. `amos_brain/api_contracts/__init__.py` - Package init
2. `amos_brain/api_contracts/base.py` - Base models
3. `amos_brain/api_contracts/chat.py` - Chat contracts
4. `amos_brain/api_contracts/repo.py` - Repo doctor contracts
5. `amos_brain/api_contracts/models.py` - LLM model contracts
6. `amos_brain/api_contracts/session.py` - Session contracts
7. `amos_brain/api_contracts/errors.py` - Error contracts
8. `AMOS_API_CONTRACTS.md` - API documentation
9. `AMOS_ARCHITECTURE_RESTRUCTURE.md` - This file

## Next Steps

1. Review and merge this PR to AMOS-Code
2. In AMOS-Consulting repo: rename package, add dependency
3. In AMOS-Consulting: implement API endpoints using these contracts
4. In client repos: switch to HTTP API calls
