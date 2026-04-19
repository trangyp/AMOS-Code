# AMOS 5-Repository Integration Plan

## Executive Summary

This document provides the exact integration plan for connecting 5 AMOS repositories through one shared protocol. It includes:
- File-by-file implementation details
- Package renaming instructions
- API endpoint specifications
- Event topic mappings
- Deployment configurations

## Phase 1: Package Name Resolution (Week 1)

### Problem
Both AMOS-Code and AMOS-Consulting currently use `amos-brain` as package name, causing Python environment collisions.

### Solution

| Repository | Current Name | New Name | Action |
|------------|--------------|----------|--------|
| AMOS-Code | `amos-brain` | `amos-brain` (keep) | No change needed |
| AMOS-Consulting | `amos-brain` | `amos-platform` | **Rename required** |
| AMOS-Claws | `amos` | `amos-claws-ui` | Optional rename |
| Mailinhconect | N/A | `mailinh-web` | N/A (frontend) |
| AMOS-Invest | N/A | `amos-invest-web` | N/A (frontend) |

### AMOS-Consulting Rename Steps

**File: `AMOS-Consulting/pyproject.toml`**
```toml
[project]
name = "amos-platform"  # Change from "amos-brain"
version = "1.0.0"
description = "AMOS Platform - Central API Gateway and Orchestration Hub"
```

**Update imports in AMOS-Consulting:**
```bash
# Find and replace in all Python files
sed -i 's/from amos_brain/from amos_platform/g' AMOS-Consulting/**/*.py
sed -i 's/import amos_brain/import amos_platform/g' AMOS-Consulting/**/*.py
```

**Directory structure change:**
```
AMOS-Consulting/
├── pyproject.toml          # Update name to amos-platform
├── amos_platform/          # Rename from amos_brain/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── gateway.py      # Main API gateway
│   │   ├── websocket.py    # WebSocket handler
│   │   └── models.py       # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── brain_bridge.py # Bridge to amos-brain
│   │   └── config.py
│   ├── events/
│   │   ├── __init__.py
│   │   ├── bus.py          # Event bus implementation
│   │   └── handlers.py     # Event handlers
│   └── cli/
       └── __init__.py
```

## Phase 2: AMOS-Code as Shared Library (Week 1-2)

### Role Definition
**AMOS-Code** becomes a pure Python library, not a server.

### What AMOS-Code Provides
```python
# amos_brain/__init__.py
"""AMOS Brain - Core cognitive library."""

from .cognitive_runtime import get_cognitive_runtime
from .equation_registry import get_equation_registry
from .reasoning_engine import ReasoningEngine
from .knowledge_graph import KnowledgeGraph
from .agent_framework import AgentFramework

__version__ = "14.0.0"

__all__ = [
    "get_cognitive_runtime",
    "get_equation_registry", 
    "ReasoningEngine",
    "KnowledgeGraph",
    "AgentFramework",
]
```

### No Server Components
Remove or disable in AMOS-Code:
- ❌ FastAPI server
- ❌ WebSocket endpoints
- ❌ Direct HTTP handlers
- ❌ Standalone execution modes

Keep only:
- ✅ Core logic functions
- ✅ Reasoning engines
- ✅ Equation execution
- ✅ Knowledge graph operations
- ✅ Agent framework

### How AMOS-Consulting Uses AMOS-Code
```python
# amos_platform/core/brain_bridge.py
from amos_brain import get_cognitive_runtime, ReasoningEngine

class BrainBridge:
    """Bridge between Platform API and Brain Library."""
    
    def __init__(self):
        self._runtime = get_cognitive_runtime()
        self._reasoning = ReasoningEngine()
    
    async def process_chat(self, message: str, context: list) -> str:
        """Process chat message through brain."""
        return await self._runtime.process_message(message, context)
    
    async def execute_equation(self, name: str, params: dict) -> dict:
        """Execute equation via brain."""
        return await self._runtime.execute_equation(name, params)
```

## Phase 3: AMOS-Consulting as Platform Hub (Week 2-4)

### New Files to Create

**1. `amos_platform/api/gateway.py`** (~800 lines)
```python
"""AMOS Platform API Gateway - Central HTTP API."""

from fastapi import FastAPI, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from amos_platform.core.brain_bridge import BrainBridge
from amos_platform.events.bus import EventBus

app = FastAPI(title="AMOS Platform API", version="1.0.0")

# Add CORS for frontend repos
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://claws.amos.io",
        "https://app.amos.io", 
        "https://invest.amos.io",
        "http://localhost:3000",  # Dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import all route modules
from .routes import chat, agents, repo, workflow, models, tasks, health
```

**2. `amos_platform/api/routes/chat.py`**
```python
"""Chat API endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from amos_platform.core.brain_bridge import BrainBridge
from amos_platform.auth.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    workspace_id: str
    context: list[dict] = []
    model: str | None = None

class ChatResponse(BaseModel):
    id: str
    message: str
    model: str
    usage: dict

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: dict = Depends(get_current_user),
    brain: BrainBridge = Depends(get_brain_bridge),
):
    """Process chat message."""
    result = await brain.process_chat(
        message=request.message,
        context=request.context,
    )
    return ChatResponse(
        id=str(uuid.uuid4()),
        message=result,
        model=request.model or "default",
        usage={"tokens": len(result)},
    )
```

**3. `amos_platform/api/routes/agents.py`**
```python
"""Agent execution API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from amos_platform.core.task_queue import TaskQueue
from amos_platform.events.bus import EventBus

router = APIRouter(prefix="/agent", tags=["agents"])
task_queue = TaskQueue()
event_bus = EventBus()

class AgentRunRequest(BaseModel):
    agent_type: str  # code_review, repo_scan, fix_generator, etc.
    target_repo: str | None = None
    parameters: dict = {}
    priority: str = "normal"  # low, normal, high, urgent
    callback_url: str | None = None

@router.post("/run", status_code=202)
async def run_agent(
    request: AgentRunRequest,
    user: dict = Depends(get_current_user),
):
    """Start agent task."""
    task_id = await task_queue.submit(
        type="agent",
        agent_type=request.agent_type,
        target_repo=request.target_repo,
        params=request.parameters,
        priority=request.priority,
        user_id=user["id"],
    )
    
    # Publish event for other repos
    await event_bus.publish("claws.agent.requested", {
        "task_id": task_id,
        "agent_type": request.agent_type,
        "target_repo": request.target_repo,
        "priority": request.priority,
        "user_id": user["id"],
    })
    
    return {
        "task_id": task_id,
        "status": "queued",
        "estimated_duration": 300,
    }

@router.get("/status/{task_id}")
async def get_agent_status(task_id: str):
    """Get agent task status."""
    status = await task_queue.get_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status

@router.post("/cancel/{task_id}")
async def cancel_agent(task_id: str, user: dict = Depends(get_current_user)):
    """Cancel running agent."""
    await task_queue.cancel(task_id, user_id=user["id"])
    return {"success": True}
```

**4. `amos_platform/api/routes/repo.py`**
```python
"""Repository scan and fix API endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from amos_platform.core.repo_scanner import RepoScanner
from amos_platform.core.fix_engine import FixEngine

router = APIRouter(prefix="/repo", tags=["repository"])

class RepoScanRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    scan_types: list[str] = ["security", "style", "architecture"]
    depth: str = "standard"  # quick, standard, deep

@router.post("/scan", status_code=202)
async def scan_repo(
    request: RepoScanRequest,
    user: dict = Depends(get_current_user),
):
    """Start repository scan."""
    scanner = RepoScanner()
    scan_id = await scanner.start(
        repo_url=request.repo_url,
        branch=request.branch,
        scan_types=request.scan_types,
        depth=request.depth,
        user_id=user["id"],
    )
    return {"scan_id": scan_id, "status": "started"}

@router.get("/status/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get scan status and results."""
    scanner = RepoScanner()
    return await scanner.get_status(scan_id)
```

**5. `amos_platform/api/routes/workflow.py`**
```python
"""Workflow execution API endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from amos_platform.core.workflow_engine import WorkflowEngine

router = APIRouter(prefix="/workflow", tags=["workflows"])

@router.post("/run", status_code=202)
async def run_workflow(
    request: WorkflowRunRequest,
    user: dict = Depends(get_current_user),
):
    """Execute workflow."""
    engine = WorkflowEngine()
    execution_id = await engine.start(
        workflow_id=request.workflow_id,
        params=request.parameters,
        trigger=request.trigger,
        user_id=user["id"],
    )
    return {"execution_id": execution_id, "status": "started"}
```

**6. `amos_platform/api/routes/models.py`**
```python
"""LLM model management API endpoints."""

from fastapi import APIRouter, Depends

from amos_platform.core.llm_router import LLMRouter

router = APIRouter(prefix="/models", tags=["models"])
llm_router = LLMRouter()

@router.get("")
async def list_models():
    """List available models from all backends."""
    return {
        "models": await llm_router.list_models()
    }

@router.get("/{model_id}/status")
async def get_model_status(model_id: str):
    """Get model load status."""
    return await llm_router.get_status(model_id)

@router.post("/{model_id}/load")
async def load_model(model_id: str, admin: dict = Depends(require_admin)):
    """Load model into memory (admin only)."""
    return await llm_router.load(model_id)
```

**7. `amos_platform/api/routes/tasks.py`**
```python
"""Task management API endpoints."""

from fastapi import APIRouter, Depends

from amos_platform.core.task_queue import TaskQueue

router = APIRouter(prefix="/tasks", tags=["tasks"])
task_queue = TaskQueue()

@router.get("")
async def list_tasks(
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    user: dict = Depends(get_current_user),
):
    """List user tasks."""
    return await task_queue.list(
        user_id=user["id"],
        status=status,
        limit=limit,
        offset=offset,
    )

@router.get("/{task_id}")
async def get_task(task_id: str, user: dict = Depends(get_current_user)):
    """Get task details."""
    return await task_queue.get(task_id, user_id=user["id"])

@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: str, user: dict = Depends(get_current_user)):
    """Delete task."""
    await task_queue.delete(task_id, user_id=user["id"])
```

**8. `amos_platform/api/websocket.py`**
```python
"""WebSocket handler for real-time updates."""

from fastapi import WebSocket, WebSocketDisconnect
import json

from amos_platform.auth.jwt import verify_token
from amos_platform.events.bus import EventBus

class WebSocketManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self._connections: dict[str, WebSocket] = {}
        self._subscriptions: dict[str, set[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self._connections[client_id] = websocket
        print(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        del self._connections[client_id]
        for subs in self._subscriptions.values():
            subs.discard(client_id)
    
    async def handle(self, websocket: WebSocket):
        """Handle WebSocket connection."""
        client_id = str(uuid.uuid4())
        await self.connect(websocket, client_id)
        
        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type")
                
                if msg_type == "auth":
                    # Verify JWT
                    token = data.get("token")
                    try:
                        user = verify_token(token)
                        await websocket.send_json({
                            "type": "auth_result",
                            "success": True,
                            "user_id": user["id"],
                        })
                    except Exception as e:
                        await websocket.send_json({
                            "type": "auth_result",
                            "success": False,
                            "error": str(e),
                        })
                
                elif msg_type == "subscribe":
                    channel = data.get("channel")
                    if channel not in self._subscriptions:
                        self._subscriptions[channel] = set()
                    self._subscriptions[channel].add(client_id)
                    await websocket.send_json({
                        "type": "subscribed",
                        "channel": channel,
                    })
                
                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
        
        except WebSocketDisconnect:
            self.disconnect(client_id)

ws_manager = WebSocketManager()

# FastAPI route
from fastapi import APIRouter

ws_router = APIRouter()

@ws_router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.handle(websocket)
```

**9. `amos_platform/events/bus.py`**
```python
"""Event bus for cross-repo communication via Redis Streams."""

import json
import asyncio
from typing import Callable, Any
from datetime import datetime

import redis.asyncio as redis

class EventBus:
    """Async event bus using Redis Streams."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self._redis_url = redis_url
        self._redis: redis.Redis | None = None
        self._subscribers: dict[str, list[Callable]] = {}
    
    async def connect(self):
        """Connect to Redis."""
        self._redis = redis.from_url(self._redis_url)
    
    async def publish(self, topic: str, payload: dict[str, Any]):
        """Publish event to topic."""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": topic,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "amos-platform",
            "payload": payload,
        }
        
        await self._redis.xadd(topic, {"data": json.dumps(event)})
        
        # Notify local subscribers
        for callback in self._subscribers.get(topic, []):
            asyncio.create_task(callback(event))
    
    def subscribe(self, topic: str, callback: Callable[[dict], Any]):
        """Subscribe to topic."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)
    
    async def listen(self, topics: list[str]):
        """Listen for events (consumer)."""
        # Create consumer group if not exists
        for topic in topics:
            try:
                await self._redis.xgroup_create(topic, "platform", id="0", mkstream=True)
            except redis.ResponseError:
                pass  # Group already exists
        
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
                        # Process and broadcast to WebSocket
                        await self._broadcast_to_ws(data)
                        await self._redis.xack(topic, "platform", msg_id)
            
            await asyncio.sleep(0.1)

# Global event bus instance
event_bus = EventBus()
```

**10. `amos_platform/core/llm_router.py`**
```python
"""Centralized LLM routing - only AMOS-Consulting talks to Ollama/LM Studio."""

import httpx
from typing import Literal

class LLMRouter:
    """Route LLM requests to appropriate backend."""
    
    BACKENDS = {
        "ollama": "http://localhost:11434",
        "lmstudio": "http://localhost:1234/v1",
        "vllm": "http://localhost:8000/v1",
    }
    
    async def list_models(self) -> list[dict]:
        """List models from all backends."""
        models = []
        
        # Query Ollama
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.BACKENDS['ollama']}/api/tags")
                if resp.status_code == 200:
                    for m in resp.json()["models"]:
                        models.append({
                            "id": f"ollama/{m['name']}",
                            "name": m["name"],
                            "provider": "ollama",
                            "status": "available",
                        })
        except Exception:
            pass
        
        # Query other backends...
        return models
    
    async def chat(self, model: str, messages: list[dict], **kwargs) -> dict:
        """Send chat request to appropriate backend."""
        provider, model_name = model.split("/", 1)
        backend_url = self.BACKENDS.get(provider)
        
        if not backend_url:
            raise ValueError(f"Unknown provider: {provider}")
        
        if provider == "ollama":
            return await self._chat_ollama(backend_url, model_name, messages, **kwargs)
        elif provider == "lmstudio":
            return await self._chat_openai_compatible(backend_url, model_name, messages, **kwargs)
        # ...
    
    async def _chat_ollama(self, url: str, model: str, messages: list[dict], **kwargs):
        """Chat with Ollama backend."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    **kwargs,
                },
            )
            return resp.json()

# Global instance
llm_router = LLMRouter()
```

## Phase 4: Frontend Repo Integration (Week 4-6)

### AMOS-Claws Integration

**File: `AMOS-Claws/src/api/client.ts`**
```typescript
import { AMOSClient } from '@amos/platform-client';

const client = new AMOSClient({
  baseUrl: process.env.AMOS_API_URL || 'https://api.amos.io',
  apiKey: process.env.AMOS_API_KEY,
});

export default client;
```

**File: `AMOS-Claws/src/hooks/useChat.ts`**
```typescript
import { useState } from 'react';
import client from '../api/client';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const sendMessage = async (content: string) => {
    setLoading(true);
    try {
      const response = await client.chat({
        message: content,
        workspace_id: 'claws-default',
        context: messages,
      });
      
      setMessages(prev => [
        ...prev,
        { role: 'user', content },
        { role: 'assistant', content: response.message },
      ]);
    } finally {
      setLoading(false);
    }
  };
  
  return { messages, sendMessage, loading };
}
```

**File: `AMOS-Claws/src/hooks/useWebSocket.ts`**
```typescript
import { useEffect, useRef, useState } from 'react';

export function useWebSocket() {
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState([]);
  const ws = useRef<WebSocket | null>(null);
  
  useEffect(() => {
    const socket = new WebSocket('wss://api.amos.io/v1/ws/stream');
    ws.current = socket;
    
    socket.onopen = () => {
      setConnected(true);
      // Authenticate
      socket.send(JSON.stringify({
        type: 'auth',
        token: localStorage.getItem('jwt_token'),
      }));
      // Subscribe to channels
      socket.send(JSON.stringify({
        type: 'subscribe',
        channel: 'tasks',
      }));
    };
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents(prev => [...prev, data]);
    };
    
    socket.onclose = () => setConnected(false);
    
    return () => socket.close();
  }, []);
  
  return { connected, events };
}
```

### Mailinhconect Integration

**File: `Mailinhconect/src/api/amos.ts`**
```typescript
import { AMOSClient } from '@amos/platform-client';

export const amosClient = new AMOSClient({
  baseUrl: 'https://api.amos.io',
  apiKey: process.env.REACT_APP_AMOS_API_KEY,
});

// Lead submission
export async function submitLead(leadData: LeadFormData) {
  // Submit to Mailinhconect backend
  const result = await submitToBackend(leadData);
  
  // Also notify AMOS platform
  await amosClient.publishEvent('mailinh.lead.created', {
    lead_id: result.id,
    source: 'website',
    email: leadData.email,
  });
  
  return result;
}
```

### AMOS-Invest Integration

**File: `AMOS-Invest/src/api/client.ts`**
```typescript
import { AMOSClient } from '@amos/platform-client';

export const api = new AMOSClient({
  baseUrl: 'https://api.amos.io',
  apiKey: process.env.VITE_AMOS_API_KEY,
});

// Subscribe to signals
export async function subscribeToSignals(callback: (signal: Signal) => void) {
  const ws = new WebSocket('wss://api.amos.io/v1/ws/stream');
  
  ws.onopen = () => {
    ws.send(JSON.stringify({ type: 'subscribe', channel: 'signals' }));
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'invest.signal.generated') {
      callback(data.payload);
    }
  };
  
  return () => ws.close();
}
```

## Phase 5: Event Topic Configuration (Week 5)

### Event Topics Reference

| Topic | Publisher | Subscribers | Payload Schema |
|-------|-----------|-------------|----------------|
| `mailinh.lead.created` | Mailinhconect | AMOS-Consulting, Invest | `{lead_id, source, email, timestamp}` |
| `mailinh.contact.submitted` | Mailinhconect | AMOS-Consulting | `{contact_id, form_data, timestamp}` |
| `claws.session.started` | AMOS-Claws | AMOS-Consulting, Invest | `{session_id, user_id, timestamp}` |
| `claws.agent.requested` | AMOS-Claws | AMOS-Consulting | `{task_id, agent_type, params}` |
| `invest.report.requested` | AMOS-Invest | AMOS-Consulting | `{report_type, date_range, user_id}` |
| `invest.signal.generated` | AMOS-Consulting | AMOS-Invest | `{signal_type, confidence, data, timestamp}` |
| `repo.scan.completed` | AMOS-Consulting | Claws, Invest | `{scan_id, repo_url, findings_count}` |
| `repo.fix.completed` | AMOS-Consulting | Claws | `{fix_id, pr_url, files_changed}` |
| `model.run.completed` | AMOS-Consulting | Claws, Invest | `{run_id, model_id, metrics}` |
| `system.alert` | AMOS-Consulting | All | `{severity, component, message, timestamp}` |

### Event Payload Standard

```json
{
  "event_id": "uuid",
  "event_type": "topic.name",
  "timestamp": "2026-01-19T10:30:00Z",
  "source": "repo-name",
  "payload": {
    // Event-specific data
  },
  "metadata": {
    "version": "1.0",
    "trace_id": "uuid"
  }
}
```

## Phase 6: Deployment Configuration (Week 6-8)

### Subdomain Routing

```yaml
# Traefik or Nginx configuration
routes:
  # API Gateway
  - host: api.amos.io
    service: amos-consulting
    port: 8000
    
  # Frontend: Operator UI
  - host: claws.amos.io
    service: amos-claws
    port: 3000
    
  # Frontend: Product UI  
  - host: app.amos.io
    service: mailinhconect
    port: 3000
    
  # Frontend: Investor Dashboard
  - host: invest.amos.io
    service: amos-invest
    port: 3000
```

### Docker Compose (Development)

```yaml
# docker-compose.integration.yml
version: '3.8'

services:
  # AMOS Platform (Consulting)
  amos-platform:
    build: ./AMOS-Consulting
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=dev-secret
      - AMOS_BRAIN_PATH=/app/amos-brain
    volumes:
      - ./AMOS-Code:/app/amos-brain:ro  # Mount brain as read-only
    depends_on:
      - redis
      - ollama
  
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
  
  # AMOS-Claws (Operator UI)
  amos-claws:
    build: ./AMOS-Claws
    ports:
      - "3001:3000"
    environment:
      - AMOS_API_URL=http://amos-platform:8000
  
  # Mailinhconect (Product UI)
  mailinhconect:
    build: ./Mailinhconect
    ports:
      - "3002:3000"
    environment:
      - AMOS_API_URL=http://amos-platform:8000
  
  # AMOS-Invest (Investor UI)
  amos-invest:
    build: ./AMOS-Invest
    ports:
      - "3003:3000"
    environment:
      - AMOS_API_URL=http://amos-platform:8000

volumes:
  ollama-data:
```

### Environment Variables

**AMOS-Consulting (.env)**
```bash
# Server
AMOS_API_HOST=0.0.0.0
AMOS_API_PORT=8000

# Security
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
API_KEY_SALT=your-salt

# Redis (Event Bus)
REDIS_URL=redis://localhost:6379/0

# LLM Backends
OLLAMA_URL=http://localhost:11434
LMSTUDIO_URL=http://localhost:1234/v1
VLLM_URL=http://localhost:8000/v1

# AMOS-Code (Brain) - mounted as library
AMOS_BRAIN_PACKAGE=amos-brain

# Database (for tasks, users)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/amos
```

**Frontend Repos (.env)**
```bash
# AMOS-Claws, Mailinhconect, AMOS-Invest
AMOS_API_URL=https://api.amos.io
AMOS_WS_URL=wss://api.amos.io
AMOS_API_KEY=your-api-key
```

## Phase 7: Testing & Validation (Week 8-10)

### Integration Tests

**File: `tests/integration/test_5_repo_integration.py`**
```python
"""Integration tests for 5-repo architecture."""

import pytest
import asyncio
from amos_integration_client import AMOSClient

@pytest.mark.asyncio
async def test_chat_through_platform():
    """Test chat flows through AMOS-Consulting to AMOS-Code."""
    client = AMOSClient(base_url="http://localhost:8000")
    
    response = await client.chat.send_message(
        message="Hello, AMOS!",
        workspace_id="test-ws",
    )
    
    assert response.message is not None
    assert response.id is not None
    
    await client.close()

@pytest.mark.asyncio
async def test_agent_execution():
    """Test agent runs through platform."""
    client = AMOSClient(base_url="http://localhost:8000")
    
    # Start agent
    task = await client.agents.run(
        agent_type="repo_scan",
        target_repo="https://github.com/test/repo",
    )
    
    assert task.task_id is not None
    assert task.status == "running"
    
    # Check status
    status = await client.agents.get_status(task.task_id)
    assert status.task_id == task.task_id
    
    await client.close()

@pytest.mark.asyncio
async def test_websocket_events():
    """Test WebSocket event flow."""
    events = []
    
    client = AMOSClient(base_url="http://localhost:8000")
    
    async for event in client.websocket.connect():
        events.append(event)
        if len(events) >= 3:
            break
    
    assert len(events) > 0
    
    await client.close()

@pytest.mark.asyncio  
async def test_event_bus_pub_sub():
    """Test Redis event bus."""
    from amos_platform.events.bus import EventBus
    
    bus = EventBus(redis_url="redis://localhost:6379")
    await bus.connect()
    
    received = []
    
    def handler(event):
        received.append(event)
    
    bus.subscribe("test.topic", handler)
    
    await bus.publish("test.topic", {"message": "hello"})
    
    await asyncio.sleep(0.1)  # Allow async processing
    
    assert len(received) == 1
    assert received[0]["payload"]["message"] == "hello"
```

## Implementation Checklist

### Phase 1: Package Rename
- [ ] Rename AMOS-Consulting package to `amos-platform`
- [ ] Update all imports in AMOS-Consulting
- [ ] Test package installation
- [ ] Update CI/CD pipelines

### Phase 2: Core Library Setup
- [ ] Remove server components from AMOS-Code
- [ ] Create brain bridge in AMOS-Consulting
- [ ] Test library import

### Phase 3: API Gateway
- [ ] Create FastAPI gateway
- [ ] Implement all REST endpoints
- [ ] Add authentication/authorization
- [ ] Create OpenAPI spec

### Phase 4: WebSocket
- [ ] Implement WebSocket handler
- [ ] Add channel subscription
- [ ] Test real-time updates

### Phase 5: Event Bus
- [ ] Set up Redis Streams
- [ ] Implement publish/subscribe
- [ ] Create event handlers
- [ ] Test cross-repo events

### Phase 6: LLM Router
- [ ] Create centralized LLM router
- [ ] Add Ollama integration
- [ ] Add LM Studio integration
- [ ] Test model routing

### Phase 7: Frontend Integration
- [ ] Update AMOS-Claws to use API
- [ ] Update Mailinhconect to use API
- [ ] Update AMOS-Invest to use API
- [ ] Add WebSocket to all frontends

### Phase 8: Deployment
- [ ] Configure subdomains
- [ ] Set up SSL certificates
- [ ] Deploy to staging
- [ ] Deploy to production

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (p95) | < 200ms | Prometheus metrics |
| WebSocket Latency | < 50ms | Client-side timing |
| Event Delivery Time | < 100ms | Redis latency |
| Cross-repo Import Count | 0 | Static analysis |
| Package Name Conflicts | 0 | pip install test |
| System Availability | 99.9% | Uptime monitoring |

## Support & Documentation

- **API Documentation**: https://docs.amos.io/api
- **OpenAPI Spec**: https://api.amos.io/openapi.json
- **SDK Repository**: https://github.com/amos-project/platform-client
- **Integration Guide**: This document
- **Support Channel**: #amos-platform on Slack
