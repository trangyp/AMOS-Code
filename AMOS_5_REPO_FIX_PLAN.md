# AMOS 5-Repository Integration Fix Plan

## Overview

This document provides a prioritized, actionable fix plan to integrate the 5 AMOS repositories into a unified platform.

**Current State**: Only AMOS-Code is accessible and extensively developed. Other 4 repos need to be located and assessed.

---

## Phase 1: AMOS-Code Cleanup (Library-Only Role)

### Goal
Transform AMOS-Code into a clean library that can be installed via `pip install amos-brain` and used by other repos without confusion.

### 1.1 Critical Blockers (Must Fix First)

#### Issue: Server Code in Library
**Files to Move to AMOS-Consulting**:
```
Priority 1 (Immediate):
- backend/ (entire directory)
- amos_fastapi_gateway.py
- amos_api_gateway.py
- amos_api_gateway_enterprise.py
- amos_api_server.py
- amos_api_enhanced.py
- amos_production_runtime.py
- amos_production_server.py
- amos_fast_web_runtime.py
- admin-dashboard/ (if it contains server code)

Priority 2 (After migration):
- amos_local.py (entry point - keep example, move runner)
- amos_brain_launcher.py (move orchestration logic)
- amos_websocket_manager.py (move to Consulting)
- amos_circuit_breaker_middleware.py (move to Consulting if server-only)
```

**Action**:
1. Create list of files that must move
2. Document what each file does
3. Prepare migration patches

#### Issue: Path/Import Hacks
**Files with `sys.path.insert` patterns**:
```bash
# Find all occurrences
grep -r "sys.path.insert" --include="*.py" . | head -50
```

**Fix Strategy**:
1. Replace all `sys.path.insert` with proper package imports
2. Add `__init__.py` where missing
3. Test `pip install -e .` in clean venv

### 1.2 Safe Autofixes (Can Apply Automatically)

#### Add Missing __init__.py Files
```bash
# Directories that need __init__.py:
find . -type d -name "*" | grep -E "(amos_|backend|clawspring)" | while read dir; do
    if [ ! -f "$dir/__init__.py" ]; then
        touch "$dir/__init__.py"
    fi
done
```

#### Fix Import Patterns
**Before**:
```python
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from amos_brain import something
```

**After**:
```python
from amos_brain import something  # Proper package import
```

### 1.3 Medium-Risk Fixes (Need Testing)

#### Verify Package Structure
```bash
# Test in clean environment
python -m venv /tmp/test_venv
source /tmp/test_venv/bin/activate
pip install -e .
python -c "import amos_brain; print('OK')"
python -c "from amos_brain.local_runtime import create_local_runtime; print('OK')"
python -c "from amos_model_fabric.gateway import LiteLLMRouter; print('OK')"
```

#### SDK Verification
```bash
cd sdk/python
pip install -e .
python -c "import amos_sdk; print('SDK OK')"
```

### 1.4 High-Risk/Manual Decisions

#### Keep or Remove Decision Needed

**Keep in AMOS-Code (Library)**:
- Core cognitive architecture (amos_brain/)
- Equation engine (amosl/, amos_equation_*.py)
- Model fabric (amos_model_fabric/ - gateway client)
- Event bus client (amos_event_bus.py)
- Memory systems (memory/, amos_memory*.py)
- Knowledge systems (amos_knowledge*.py)
- Self-evolution (amos_self_evolution/)
- Utilities (logging, config, etc.)

**Move to AMOS-Consulting (Server)**:
- All FastAPI/Flask server files
- API endpoint handlers
- WebSocket servers
- Database migration scripts
- Production runtime orchestrators
- Middleware (rate limiting, auth)

---

## Phase 2: SDK Standardization

### Goal
Create working SDKs that match the OpenAPI spec for all client repos to use.

### 2.1 Python SDK

**Current Location**: `sdk/python/amos_sdk/`

**Actions**:
1. Compare SDK methods with `AMOS_OPENAPI_SPEC.yaml`
2. Add missing endpoints
3. Ensure async client is complete
4. Add event bus client wrapper

**Required SDK Methods**:
```python
# Core API
client.chat(message, context=None, model=None)
client.run_agent(agent_type, parameters, priority)
client.get_agent_status(task_id)
client.cancel_agent(task_id)

# Repository
client.scan_repo(repo_url, scan_types, depth)
client.fix_repo(scan_id)
client.get_scan_status(scan_id)

# Workflow
client.run_workflow(workflow_type, parameters)
client.get_workflow_status(workflow_id)

# Models
client.list_models()
client.get_model_status(model_id)
client.load_model(model_id)  # Admin only

# Tasks
client.list_tasks()
client.get_task(task_id)
client.delete_task(task_id)

# Real-time (WebSocket)
async for event in client.subscribe(channel):
    handle(event)
```

### 2.2 TypeScript SDK

**Current State**: `sdk/javascript/` exists but needs verification

**Actions**:
1. Generate from OpenAPI spec using openapi-generator
2. Verify all endpoints covered
3. Add WebSocket client
4. Create npm package structure

**Generate Command**:
```bash
cd sdk
openapi-generator generate \
  -i ../AMOS_OPENAPI_SPEC.yaml \
  -g typescript-axios \
  -o javascript/amos-sdk-ts \
  -c openapi-generator-config.json
```

### 2.3 Event Bus Client

**New File**: `sdk/python/amos_sdk/events.py`

**Interface**:
```python
from amos_sdk.events import EventBusClient

# Connect to event bus
client = EventBusClient(redis_url="redis://localhost:6379")

# Subscribe to topics
@client.subscribe("claws.agent.requested")
async def on_agent_requested(event):
    print(f"Agent requested: {event.payload}")

# Publish events
await client.publish("mailinh.lead.created", {
    "lead_id": "123",
    "source": "website"
})
```

---

## Phase 3: AMOS-Consulting Setup (Backend Hub)

### Goal
Create the central backend hub that other repos connect to.

### 3.1 Repository Structure

```
AMOS-Consulting/
├── pyproject.toml              # Package: amos-platform
├── src/
│   └── amos_platform/
│       ├── __init__.py
│       ├── api/                # FastAPI app
│       │   ├── __init__.py
│       │   ├── main.py         # FastAPI entry
│       │   ├── routes/
│       │   │   ├── chat.py
│       │   │   ├── agent.py
│       │   │   ├── repo.py
│       │   │   ├── workflow.py
│       │   │   ├── models.py
│       │   │   └── tasks.py
│       │   └── websocket/
│       │       └── stream.py
│       ├── core/               # Business logic
│       │   ├── __init__.py
│       │   ├── model_gateway.py    # LLM routing
│       │   ├── event_bus.py        # Event coordination
│       │   └── auth.py             # Auth middleware
│       └── config/
│           └── settings.py
├── migrations/                 # Alembic migrations
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/
└── docs/
```

### 3.2 Server Migration from AMOS-Code

**Files to Copy** (from AMOS-Code to AMOS-Consulting):

```bash
# API Infrastructure
AMOS-Code/backend/ → AMOS-Consulting/src/amos_platform/api/
AMOS-Code/amos_fastapi_gateway.py → AMOS-Consulting/src/amos_platform/api/main.py
AMOS-Code/amos_websocket_manager.py → AMOS-Consulting/src/amos_platform/api/websocket/

# Configuration
AMOS-Code/amos_config.py → AMOS-Consulting/src/amos_platform/config/
AMOS-Code/amos_multitenancy.py → AMOS-Consulting/src/amos_platform/core/

# Database
AMOS-Code/amos_db_sqlalchemy.py → AMOS-Consulting/src/amos_platform/core/db.py
AMOS-Code/alembic/ → AMOS-Consulting/migrations/

# Security
AMOS-Code/amos_auth_manager.py → AMOS-Consulting/src/amos_platform/core/auth.py
AMOS-Code/amos_security_compliance.py → AMOS-Consulting/src/amos_platform/core/security.py

# Middleware
AMOS-Code/amos_rate_limiting.py → AMOS-Consulting/src/amos_platform/api/middleware/
AMOS-Code/amos_circuit_breaker_middleware.py → AMOS-Consulting/src/amos_platform/api/middleware/
```

### 3.3 Dependencies

**AMOS-Consulting pyproject.toml**:
```toml
[project]
name = "amos-platform"
version = "1.0.0"
dependencies = [
    "amos-brain>=14.0.0",  # Core library
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    "redis>=4.6.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.28.0",
    "alembic>=1.11.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.0",
    "httpx>=0.24.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
]
```

### 3.4 Model Gateway Configuration

**File**: `AMOS-Consulting/src/amos_platform/core/model_gateway.py`

**Responsibilities**:
- Discover available local LLM providers
- Route requests based on model capabilities
- Handle load balancing across providers
- Provide unified API to frontends

**Supported Backends**:
- Ollama (default local)
- LM Studio
- vLLM
- llama.cpp server
- SGLang
- LiteLLM (optional router)

---

## Phase 4: Frontend Integration (Claws, Mailinh, Invest)

### Goal
Update all 3 frontend repos to use the SDK and connect through AMOS-Consulting.

### 4.1 AMOS-Claws (Operator Frontend)

**Changes Required**:

1. **Add SDK Dependency**:
   ```bash
   pip install amos-sdk
   ```

2. **Replace Direct Imports**:
   ```python
   # Before (WRONG - direct import)
   from amos_brain import something
   
   # After (CORRECT - via SDK)
   from amos_sdk import Client
   client = Client(api_key="...", base_url="https://api.amos.io")
   result = client.chat(message)
   ```

3. **Add WebSocket Connection**:
   ```python
   from amos_sdk import AsyncClient
   
   async with AsyncClient() as client:
       async for event in client.subscribe("claws.session.started"):
           update_ui(event)
   ```

4. **OpenClaw Integration**:
   - Use SDK to call AMOS-Consulting
   - AMOS-Consulting routes to appropriate LLM
   - Keep OpenClaw-specific UI logic in Claws

### 4.2 Mailinhconect (Product Frontend)

**Changes Required**:

1. **Remove Backend Logic**:
   - Identify all backend code
   - Move to AMOS-Consulting API endpoints
   - Keep only frontend presentation

2. **Event Publishing**:
   ```python
   from amos_sdk.events import EventBusClient
   
   events = EventBusClient()
   await events.publish("mailinh.lead.created", {
       "lead_id": lead.id,
       "source": "contact_form",
       "timestamp": datetime.now(timezone.utc).isoformat()
   })
   ```

3. **API Integration Points**:
   - Contact form → POST /v1/mailinh/contact
   - Lead capture → POST /v1/mailinh/lead
   - User dashboard → GET /v1/mailinh/user/{id}

### 4.3 AMOS-Invest (Investor Frontend)

**Changes Required**:

1. **API Integration**:
   ```python
   from amos_sdk import Client
   
   client = Client()
   
   # Get analytics
   reports = client.list_reports()
   signals = client.get_signals()
   
   # Request new report
   task_id = client.run_agent(
       agent_type="investment_report",
       parameters={"date_range": "Q1-2026"}
   )
   ```

2. **Event Subscriptions**:
   ```python
   @client.subscribe("invest.signal.generated")
   async def on_signal(event):
       notify_investor(event.payload)
   ```

---

## Phase 5: Event Bus Setup

### Goal
Configure Redis Streams or NATS for cross-repo async communication.

### 5.1 Infrastructure

**Redis Setup** (if using Redis Streams):
```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  redis-streams:
    image: redis:7-alpine
    depends_on:
      - redis
```

**NATS Setup** (alternative):
```yaml
services:
  nats:
    image: nats:latest
    ports:
      - "4222:4222"
      - "8222:8222"
    command: "--js --store_dir /data"
```

### 5.2 Event Schema

**Standard Event Structure**:
```json
{
  "event_id": "uuid",
  "event_type": "mailinh.lead.created",
  "timestamp": "2026-01-19T10:30:00Z",
  "source": "mailinhconect",
  "payload": {
    "lead_id": "123",
    "email": "user@example.com"
  },
  "metadata": {
    "version": "1.0",
    "trace_id": "uuid",
    "workspace_id": "ws-123"
  }
}
```

### 5.3 Required Event Topics

| Topic | Publisher | Subscribers | Payload Schema |
|-------|-----------|-------------|----------------|
| `claws.session.started` | AMOS-Claws | AMOS-Consulting | `{session_id, user_id}` |
| `claws.agent.requested` | AMOS-Claws | AMOS-Consulting | `{agent_type, params}` |
| `mailinh.lead.created` | Mailinhconect | AMOS-Consulting, Invest | `{lead_id, source}` |
| `mailinh.contact.submitted` | Mailinhconect | AMOS-Consulting | `{contact_id, form}` |
| `invest.report.requested` | AMOS-Invest | AMOS-Consulting | `{report_type, range}` |
| `invest.signal.generated` | AMOS-Consulting | AMOS-Invest | `{signal_type, confidence}` |
| `repo.scan.completed` | AMOS-Consulting | AMOS-Claws, Invest | `{scan_id, summary}` |
| `repo.fix.completed` | AMOS-Consulting | AMOS-Claws | `{fix_id, pr_url}` |
| `model.run.completed` | AMOS-Consulting | AMOS-Claws, Invest | `{run_id, metrics}` |
| `system.alert` | AMOS-Consulting | All | `{severity, message}` |

---

## Phase 6: Local/Offline LLM Gateway

### Goal
Centralize all local LLM access in AMOS-Consulting.

### 6.1 Provider Discovery

**Auto-Discovery Logic**:
```python
class LLMProviderDiscovery:
    """Discover available local LLM providers."""
    
    async def discover(self) -> list[ProviderInfo]:
        providers = []
        
        # Check Ollama
        if await self._check_ollama():
            providers.append(ProviderInfo(
                type="ollama",
                endpoint="http://localhost:11434",
                models=await self._list_ollama_models()
            ))
        
        # Check LM Studio
        if await self._check_lmstudio():
            providers.append(ProviderInfo(
                type="lmstudio",
                endpoint="http://localhost:1234/v1",
                models=await self._list_lmstudio_models()
            ))
        
        # Check vLLM
        if await self._check_vllm():
            providers.append(ProviderInfo(
                type="vllm",
                endpoint="http://localhost:8000/v1",
                models=await self._list_vllm_models()
            ))
        
        return providers
```

### 6.2 Routing Rules

**Configuration**:
```yaml
model_routing:
  rules:
    - pattern: "llama*"
      backend: ollama
      priority: 1
    
    - pattern: "qwen*"
      backend: vllm
      priority: 2
    
    - pattern: "gpt*"
      backend: openai
      priority: 3
      requires_api_key: true
    
    - pattern: "*"
      backend: ollama
      priority: 99  # Fallback
```

### 6.3 OpenAI-Compatible API

**Endpoint**: `POST /v1/chat/completions`

**Request**:
```json
{
  "model": "llama3.2:latest",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "stream": true
}
```

**Response**:
```json
{
  "id": "chatcmp-123",
  "model": "llama3.2:latest",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help you today?"
    }
  }]
}
```

---

## Phase 7: Testing & Verification

### 7.1 Install Tests

```bash
# Test AMOS-Code as library
python -m venv /tmp/test_lib
source /tmp/test_lib/bin/activate
pip install /path/to/AMOS-Code
python -c "import amos_brain; print('Library OK')"

# Test AMOS-Consulting
python -m venv /tmp/test_platform
source /tmp/test_platform/bin/activate
pip install /path/to/AMOS-Consulting
amos-platform-server &  # Should start API server
curl http://localhost:8000/v1/health

# Test SDK
pip install /path/to/AMOS-Code/sdk/python
python -c "from amos_sdk import Client; print('SDK OK')"
```

### 7.2 Integration Tests

```python
# test_integration.py
import pytest
from amos_sdk import Client

@pytest.fixture
def client():
    return Client(
        api_key="test-key",
        base_url="http://localhost:8000"
    )

def test_health_check(client):
    status = client.health()
    assert status["status"] == "healthy"

def test_chat_endpoint(client):
    response = client.chat(message="Hello")
    assert "content" in response

def test_model_listing(client):
    models = client.list_models()
    assert len(models) > 0

def test_event_bus():
    from amos_sdk.events import EventBusClient
    
    client = EventBusClient(redis_url="redis://localhost:6379")
    
    received = []
    @client.subscribe("test.event")
    async def handler(event):
        received.append(event)
    
    await client.publish("test.event", {"test": True})
    await asyncio.sleep(0.1)
    
    assert len(received) == 1
```

### 7.3 Cross-Repo Communication Test

```python
# test_cross_repo.py
async def test_cross_repo_event_flow():
    """Test that events flow between repos correctly."""
    
    # AMOS-Claws publishes
    claws_client = EventBusClient()
    await claws_client.publish("claws.agent.requested", {
        "agent_type": "code_review",
        "priority": "high"
    })
    
    # AMOS-Consulting receives and processes
    consulting_client = EventBusClient()
    
    received_events = []
    @consulting_client.subscribe("claws.agent.requested")
    async def on_agent_request(event):
        received_events.append(event)
        # Start agent task
        task_id = await start_agent_task(event.payload)
        # Publish completion
        await consulting_client.publish("model.run.completed", {
            "task_id": task_id,
            "status": "success"
        })
    
    # AMOS-Invest receives completion
    invest_client = EventBusClient()
    
    @invest_client.subscribe("model.run.completed")
    async def on_complete(event):
        assert event.payload["status"] == "success"
    
    await asyncio.sleep(0.5)
    assert len(received_events) == 1
```

---

## Implementation Timeline

### Week 1: AMOS-Code Cleanup
- Day 1-2: Identify server files to move
- Day 3-4: Fix import/path issues
- Day 5: Verify package installation

### Week 2: SDK & AMOS-Consulting Setup
- Day 1-2: Update Python SDK
- Day 3-4: Generate TypeScript SDK
- Day 5: Set up AMOS-Consulting structure

### Week 3: Server Migration
- Day 1-3: Move server code from AMOS-Code
- Day 4-5: Configure model gateway

### Week 4: Event Bus & Integration
- Day 1-2: Set up Redis Streams/NATS
- Day 3-4: Configure event topics
- Day 5: Test event flow

### Week 5: Frontend Updates
- Day 1-2: Update AMOS-Claws
- Day 3: Update Mailinhconect
- Day 4: Update AMOS-Invest
- Day 5: Integration testing

### Week 6: Testing & Deployment
- Day 1-3: End-to-end testing
- Day 4: Performance testing
- Day 5: Documentation

---

## Success Metrics

| Metric | Target | Verification |
|--------|--------|--------------|
| Package Install | `pip install amos-brain` works | Manual test |
| Import Cleanliness | No `sys.path` hacks | Grep check |
| API Response Time | < 200ms p95 | Load test |
| WebSocket Latency | < 50ms | Ping test |
| Event Delivery | < 100ms | Time measurement |
| Cross-repo Imports | 0 | Static analysis |
| SDK Coverage | 100% of OpenAPI | Comparison |
| Local LLM Support | 5+ providers | Discovery test |

---

## Rollback Plan

If issues arise:

1. **Keep AMOS-Code working** during migration
2. **Branch-based migration** - work in feature branches
3. **Dual-mode operation** - support old and new during transition
4. **Database compatibility** - ensure migrations are reversible
5. **Version pinning** - frontends can pin to last working version

---

## Next Actions

### Immediate (You)
1. ✅ Review this fix plan
2. ⏳ Provide access to other 4 repos (clone URLs or paths)
3. ⏳ Approve or modify architecture decisions

### Next (This Session)
1. Create branches for migration
2. Start AMOS-Code cleanup
3. Generate SDK updates
4. Document findings for other repos

### Follow-up
1. Set up AMOS-Consulting repository
2. Migrate server code
3. Configure event bus
4. Update all frontends
5. Integration testing
