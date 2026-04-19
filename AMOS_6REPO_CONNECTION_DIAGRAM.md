# AMOS 6-Repository Connection Diagram

## Hub-and-Spoke Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              AMOS ECOSYSTEM ARCHITECTURE                                  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                               │
│    │  AMOS-Claws │     │Mailinhconect│     │ AMOS-Invest │        CLIENTS (Spokes)       │
│    │  (Agent UI) │     │  (Product)  │     │ (Investor)  │                               │
│    └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                               │
│           │                   │                   │                                      │
│           │  amos_client_sdk  │  amos_client_sdk  │  amos_client_sdk                      │
│           │  (httpx/async)    │  (httpx/async)    │  (httpx/async)                        │
│           ▼                   ▼                   ▼                                      │
│    ┌─────────────────────────────────────────────────────────────────────────┐          │
│    │                      AMOS-Consulting (HUB)                              │          │
│    │                    ┌─────────────────────┐                              │          │
│    │                    │   amos_api_hub.py   │                              │          │
│    │                    │   FastAPI Server    │◄── Port 8000                │          │
│    │                    └─────────────────────┘                              │          │
│    │                              │                                          │          │
│    │    ┌─────────────────────────┼─────────────────────────┐                  │          │
│    │    │         Internal Connections                    │                  │          │
│    │    ▼                         ▼                       ▼                  │          │
│    │ ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐        │          │
│    │ │ AMOS-Code    │    │ AMOS-UNIVERSE│    │   Model Gateway      │        │          │
│    │ │ (Core Logic) │    │ (Schemas/    │    │  ┌────────────────┐  │        │          │
│    │ │              │    │  Contracts)  │    │  │ Ollama:11434   │  │        │          │
│    │ └──────────────┘    └──────────────┘    │  │ LM Studio      │  │        │          │
│    │                                         │  │ vLLM           │  │        │          │
│    │  Imports: from amos_brain import X      │  │ llama.cpp      │  │        │          │
│    │  Imports: from amos_universe import Y   │  └────────────────┘  │        │          │
│    │                                         └──────────────────────┘        │          │
│    └─────────────────────────────────────────────────────────────────────────┘          │
│                                          │                                               │
│                                          │ WebSocket / Event Bus                        │
│                                          ▼                                               │
│    ┌─────────────────────────────────────────────────────────────────────────┐          │
│    │                    OpenClaw Integration Layer                           │          │
│    │  ┌─────────────────────────────────────────────────────────────────┐   │          │
│    │  │  amos_openclaw_connector.py (Port 8888)                         │   │          │
│    │  │  ├── MCP Server (stdio)                                         │   │          │
│    │  │  ├── API Bridge (HTTP)                                        │   │          │
│    │  │  └── State Sync (filesystem)                                  │   │          │
│    │  └─────────────────────────────────────────────────────────────────┘   │          │
│    │                              │                                          │          │
│    │                              │ Direct Ollama (native API)                 │          │
│    │                              ▼ (for tool calling)                        │          │
│    │  ┌─────────────────────────────────────────────────────────────────┐   │          │
│    │  │                    OpenClaw (TypeScript)                        │   │          │
│    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │   │          │
│    │  │  │ Agent Layer │  │  SDK/Plugin │  │  Multi-Channel Runtime  │  │   │          │
│    │  │  └─────────────┘  └─────────────┘  └─────────────────────────┘  │   │          │
│    │  └─────────────────────────────────────────────────────────────────┘   │          │
│    └─────────────────────────────────────────────────────────────────────────┘          │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Repository Details

### 1. AMOS-Consulting (HUB) ⭐
**Role:** Central API server that all other repos connect to

| Property | Value |
|----------|-------|
| **File** | `amos_api_hub.py` |
| **Port** | 8000 |
| **Framework** | FastAPI |
| **Purpose** | REST API, WebSocket, event bus, task queue, model gateway, auth |

**Key Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/health` | GET | Health check |
| `/v1/chat` | POST | Chat with AMOS brain |
| `/v1/brain/run` | POST | Execute brain cycle |
| `/v1/repo/scan` | POST | Scan repository |
| `/v1/repo/fix` | POST | Apply fixes |
| `/v1/models` | GET | List available LLMs |
| `/v1/models/run` | POST | Run model inference |
| `/v1/workflow/run` | POST | Execute workflow |

**Imports:**
```python
from amos_brain.api_contracts import ChatRequest, ChatResponse, ...
from amos_brain import get_brain  # AMOS-Code core
from amos_llm_router import llm_router  # Model gateway
```

---

### 2. AMOS-Claws (SPOKE)
**Role:** Agent/operator layer - connects to hub AND directly to Ollama for tool calling

| Property | Value |
|----------|-------|
| **Client File** | `amos_client_sdk.py` |
| **Direct Ollama** | `http://localhost:11434` (native API) |
| **Purpose** | Agent workflows, repo scan/fix, custom tools |

**Two Connection Modes:**
```python
# Mode 1: Platform workflows via AMOS-Consulting
from amos_client_sdk import AMOSClient
client = AMOSClient(api_url="https://api.yourdomain.com")
response = await client.chat("Hello", session_id="sess-123")

# Mode 2: Direct Ollama for native tool calling (OpenClaw recommendation)
# Uses http://localhost:11434 directly (NOT /v1 path)
```

---

### 3. Mailinhconect (SPOKE)
**Role:** Product frontend - connects only to hub

| Property | Value |
|----------|-------|
| **Client File** | `amos_client_sdk.py` |
| **API URL** | `https://api.yourdomain.com` |
| **Purpose** | Product features, user workflows |

**Connection:**
```python
from amos_client_sdk import AMOSClient
client = AMOSClient(api_url="https://api.yourdomain.com")
```

---

### 4. AMOS-Invest (SPOKE)
**Role:** Investor frontend - connects only to hub

| Property | Value |
|----------|-------|
| **Client File** | `amos_client_sdk.py` |
| **API URL** | `https://api.yourdomain.com` |
| **Purpose** | Investment analysis, dashboards |

**Connection:** Same as Mailinhconect

---

### 5. AMOS-Code (SHARED CORE)
**Role:** Python core imported by the hub (not a service)

| Property | Value |
|----------|-------|
| **Location** | `/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code` |
| **Key Files** | `amos_brain/`, `amos_kernel_runtime.py` |
| **Purpose** | Core logic, equations, brain runtime |

**Usage in Hub:**
```python
# In amos_api_hub.py
sys.path.insert(0, '/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code')
from amos_brain import get_brain
from amos_kernel_runtime import AMOSKernelRuntime
```

---

### 6. AMOS-UNIVERSE (SHARED SCHEMAS)
**Role:** Pydantic models/contracts shared across all repos

| Property | Value |
|----------|-------|
| **Location** | `amos_brain/api_contracts/` |
| **Key Files** | `chat.py`, `brain.py`, `repo.py`, `models.py`, `workflow.py` |
| **Purpose** | Type-safe API contracts |

**Example Contract:**
```python
# amos_brain/api_contracts/chat.py
class ChatRequest(BaseModel):
    message: str
    context: ChatContext
    history: list[ChatMessage]
    model: str | None = None
```

---

## Connection Map Summary

```
┌─────────────────┐         ┌─────────────────┐
│   AMOS-Claws    │────────▶│  AMOS-Consulting│ (port 8000)
│   (TypeScript)  │   SDK   │   (FastAPI Hub) │
└────────┬────────┘         └────────┬────────┘
         │                         │
         │ Direct Ollama           │ Imports
         │ (port 11434)            │ AMOS-Code
         │                         │ AMOS-UNIVERSE
         ▼                         ▼
┌─────────────────┐         ┌─────────────────┐
│     Ollama      │         │  Local Models   │
│  (native API)   │         │  (via LLM Router)│
└─────────────────┘         └─────────────────┘
                                    │
┌─────────────────┐                 │
│ Mailinhconect   │─────────────────┘
│   (SDK)         │
└─────────────────┘

┌─────────────────┐
│  AMOS-Invest    │──────────────────┐
│    (SDK)        │                  │
└─────────────────┘                  │
                                      │
                              ┌───────┴───────┐
                              │ AMOS-Consulting│
                              └───────────────┘
```

---

## Port Reference

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| AMOS-Consulting API | 8000 | HTTP/REST | Main API hub |
| AMOS-Consulting WS | 8000 | WebSocket | Real-time updates |
| AMOS-OpenClaw Bridge | 8888 | HTTP/REST | MCP/API bridge |
| Ollama (native) | 11434 | HTTP | Local LLM (native API) |
| Ollama (OpenAI-compat) | 11434 | HTTP | `/v1/chat/completions` |
| LM Studio | 1234 | HTTP | Local LLM server |
| Redis | 6379 | TCP | Cache/Event bus |
| PostgreSQL | 5432 | TCP | Database |

---

## File-to-File Connection Reference

### Client → Hub
```
amos_client_sdk.py ──httpx──▶ amos_api_hub.py:8000
    │
    └── AMOSClient._post("/v1/chat")
    └── AMOSClient._get("/v1/models")
```

### Hub → AMOS-Code
```
amos_api_hub.py ──import──▶ amos_brain/
    │
    └── from amos_brain import get_brain
    └── from amos_kernel_runtime import AMOSKernelRuntime
```

### Hub → Model Gateway
```
amos_api_hub.py ──import──▶ amos_llm_router.py
    │
    └── llm_router.route_request() → Ollama/LM Studio/vLLM
```

### OpenClaw → Dual Connection
```
OpenClaw ──SDK──▶ AMOS-Consulting:8000 (workflows)
    │
    └── Direct: http://localhost:11434 (tool calling)
```

---

## Environment Configuration

### For Client Repos (AMOS-Claws, Mailinhconect, AMOS-Invest)
```bash
# .env
AMOS_API_URL=https://api.yourdomain.com  # or http://localhost:8000
AMOS_API_KEY=amos_key_xxxxxxxx

# For OpenClaw direct Ollama (tool calling)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:14b
```

### For AMOS-Consulting Server
```bash
# .env
PORT=8000
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://...

# Model backends
OLLAMA_URL=http://localhost:11434
LMSTUDIO_URL=http://localhost:1234
VLLM_URL=http://localhost:8001
```

---

## Domain Structure (Production)

```
api.yourdomain.com      ──▶ AMOS-Consulting:8000
claws.yourdomain.com    ──▶ AMOS-Claws UI
mailinh.yourdomain.com  ──▶ Mailinhconect UI
invest.yourdomain.com   ──▶ AMOS-Invest UI
```

---

## Quick Start Commands

### Start Hub
```bash
cd /Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code
uvicorn amos_api_hub:app --host 0.0.0.0 --port 8000
```

### Start Ollama
```bash
ollama serve  # Port 11434
```

### Test Client
```python
from amos_client_sdk import AMOSClient
import asyncio

async def test():
    client = AMOSClient(api_url="http://localhost:8000")
    
    # Health check
    health = await client.health()
    print(f"Health: {health}")
    
    # List models
    models = await client.list_models()
    print(f"Models: {models}")
    
    await client.close()

asyncio.run(test())
```

### Connect OpenClaw
```bash
cd /Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code
./connect_openclaw.sh full
```

---

## Summary

| Repo | Type | Connection | Port/File |
|------|------|------------|-----------|
| **AMOS-Consulting** | Hub | Server | `amos_api_hub.py:8000` |
| **AMOS-Claws** | Spoke + Agent | SDK + Direct Ollama | `amos_client_sdk.py` + `localhost:11434` |
| **Mailinhconect** | Spoke | SDK only | `amos_client_sdk.py` |
| **AMOS-Invest** | Spoke | SDK only | `amos_client_sdk.py` |
| **AMOS-Code** | Shared Core | Imported | `amos_brain/` directory |
| **AMOS-UNIVERSE** | Shared Schemas | Imported | `amos_brain/api_contracts/` |

**Architecture Rule:**
- **Frontends** → Talk to **AMOS-Consulting**
- **AMOS-Consulting** → Talks to **offline LLMs**
- **OpenClaw** → Talks to **AMOS-Consulting** AND **Ollama native** (for tool calling)
