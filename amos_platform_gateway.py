#!/usr/bin/env python3
"""AMOS Platform Gateway - Central API Hub for 5-Repository Integration
====================================================================

This is the unified API gateway for the AMOS ecosystem. It serves as
the central communication hub for all 5 repositories:

- AMOS-Code: Core brain package (imported as library)
- AMOS-Consulting: This service - platform hub
- AMOS-Claws: Operator frontend client
- Mailinhconect: Product frontend client  
- AMOS-Invest: Investor dashboard client

Communication Lanes:
- Sync: REST API (this file) + WebSocket
- Async: Redis Streams / NATS (event bus)

Architecture:
```
┌─────────────────────────────────────────────────────────────┐
│                    AMOS Platform Gateway                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  REST API   │  │  WebSocket  │  │   Event Publisher   │  │
│  │  /v1/*      │  │  /ws/*      │  │   Redis/NATS        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
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

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, TypeVar

# FastAPI
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator

# Try to import AMOS-Code (core brain package)
try:
    from amos_brain import get_cognitive_runtime
    AMOS_BRAIN_AVAILABLE = True
except ImportError:
    AMOS_BRAIN_AVAILABLE = False
    logging.warning("amos-brain not available. Running in mock mode.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

T = TypeVar('T')

# =============================================================================
# Pydantic Models (from OpenAPI Spec)
# =============================================================================

class Message(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str
    timestamp: str | None = None

class ChatRequest(BaseModel):
    message: str
    context: list[Message] = Field(default_factory=list)
    model: str | None = None
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int | None = Field(default=None, ge=1, le=8192)
    workspace_id: str

class ChatResponse(BaseModel):
    id: str
    message: str
    model: str
    usage: dict[str, int]
    timestamp: str

class AgentRunRequest(BaseModel):
    agent_type: str = Field(..., pattern="^(code_review|repo_scan|fix_generator|security_audit|performance_check|custom)$")
    target_repo: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    callback_url: str | None = None

class AgentRunAccepted(BaseModel):
    task_id: str
    status: str
    estimated_duration_seconds: int
    queue_position: int

class AgentRunResult(BaseModel):
    task_id: str
    status: str
    agent_type: str
    result: dict[str, Any] | None = None
    error: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    duration_ms: int | None = None

class RepoScanRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    scan_types: list[str] = Field(default_factory=lambda: ["security", "style"])
    depth: str = Field(default="standard", pattern="^(quick|standard|deep)$")

class RepoScanResult(BaseModel):
    scan_id: str
    repo_url: str
    status: str
    findings: list[dict[str, Any]]
    summary: dict[str, int]
    report_url: str

class RepoFixRequest(BaseModel):
    repo_url: str
    scan_id: str
    fix_types: list[str] = Field(default_factory=list)
    create_pr: bool = True

class WorkflowRunRequest(BaseModel):
    workflow_id: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    trigger: str = Field(default="manual", pattern="^(manual|scheduled|webhook|event)$")

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    status: str
    capabilities: list[str]
    context_window: int
    loaded_at: str | None = None

class TaskStatus(BaseModel):
    id: str
    type: str
    status: str
    progress: float | None = Field(default=None, ge=0, le=100)
    message: str | None = None
    created_at: str
    updated_at: str
    completed_at: str | None = None
    error: str | None = None

# =============================================================================
# Mock Data Stores (replace with real implementations)
# =============================================================================

class TaskStore:
    """In-memory task store. Replace with Redis/DB in production."""
    
    def __init__(self):
        self._tasks: dict[str, dict[str, Any]] = {}
    
    def create(self, task_type: str, params: dict[str, Any]) -> str:
        task_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        self._tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "status": "pending",
            "params": params,
            "progress": 0,
            "created_at": now,
            "updated_at": now,
            "result": None,
            "error": None,
        }
        return task_id
    
    def get(self, task_id: str) -> dict[str, Any] | None:
        return self._tasks.get(task_id)
    
    def update(self, task_id: str, **kwargs) -> None:
        if task_id in self._tasks:
            self._tasks[task_id].update(kwargs)
            self._tasks[task_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    def list(self, status: str | None = None, limit: int = 20, offset: int = 0) -> list[dict[str, Any]]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        tasks.sort(key=lambda x: x["created_at"], reverse=True)
        return tasks[offset:offset + limit]

task_store = TaskStore()

# =============================================================================
# Authentication
# =============================================================================

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict[str, Any]:
    """Validate JWT token and return user info."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # TODO: Implement real JWT validation
    # For now, mock authentication
    if credentials.credentials == "test-token":
        return {"id": "user-1", "email": "test@amos.io", "role": "admin"}
    
    # In production, validate against auth service
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token",
    )

async def require_workspace(request: Request, user: dict[str, Any] = Depends(get_current_user)) -> str:
    """Extract workspace ID from header or user context."""
    workspace_id = request.headers.get("X-Workspace-ID")
    if not workspace_id:
        # Use user's default workspace
        workspace_id = user.get("default_workspace", "default")
    return workspace_id

# =============================================================================
# Event Bus (Redis Streams / NATS)
# =============================================================================

class EventBus:
    """Async event bus for cross-repo communication."""
    
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}
        self._redis: Any | None = None
    
    async def connect(self, redis_url: str = "redis://localhost:6379") -> None:
        """Connect to Redis for event streaming."""
        try:
            import redis.asyncio as redis
            self._redis = redis.from_url(redis_url)
            logger.info(f"Connected to Redis at {redis_url}")
        except ImportError:
            logger.warning("redis not installed. Event bus running in local mode.")
    
    async def publish(self, topic: str, payload: dict[str, Any]) -> None:
        """Publish event to topic."""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": topic,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
            "metadata": {"version": "1.0"}
        }
        
        if self._redis:
            await self._redis.xadd(topic, {"data": json.dumps(event)})
        
        # Local subscribers
        for callback in self._subscribers.get(topic, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(event))
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
        
        logger.info(f"Published event to {topic}: {event['event_id']}")
    
    def subscribe(self, topic: str, callback: Callable) -> None:
        """Subscribe to topic."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)

event_bus = EventBus()

# =============================================================================
# WebSocket Manager
# =============================================================================

class WebSocketManager:
    """Manage WebSocket connections for real-time updates."""
    
    def __init__(self):
        self._connections: dict[str, WebSocket] = {}
        self._subscriptions: dict[str, set[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        await websocket.accept()
        self._connections[client_id] = websocket
        logger.info(f"WebSocket client connected: {client_id}")
    
    def disconnect(self, client_id: str) -> None:
        if client_id in self._connections:
            del self._connections[client_id]
        # Remove from all subscriptions
        for channel in self._subscriptions.values():
            channel.discard(client_id)
        logger.info(f"WebSocket client disconnected: {client_id}")
    
    async def subscribe(self, client_id: str, channel: str) -> None:
        if channel not in self._subscriptions:
            self._subscriptions[channel] = set()
        self._subscriptions[channel].add(client_id)
        logger.info(f"Client {client_id} subscribed to {channel}")
    
    async def unsubscribe(self, client_id: str, channel: str) -> None:
        if channel in self._subscriptions:
            self._subscriptions[channel].discard(client_id)
    
    async def broadcast(self, channel: str, message: dict[str, Any]) -> None:
        """Broadcast message to all subscribers of a channel."""
        if channel not in self._subscriptions:
            return
        
        disconnected = []
        for client_id in self._subscriptions[channel]:
            if client_id in self._connections:
                try:
                    await self._connections[client_id].send_json(message)
                except Exception:
                    disconnected.append(client_id)
            else:
                disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    async def send_to_client(self, client_id: str, message: dict[str, Any]) -> None:
        """Send message to specific client."""
        if client_id in self._connections:
            await self._connections[client_id].send_json(message)

ws_manager = WebSocketManager()

# =============================================================================
# FastAPI Application
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting AMOS Platform Gateway...")
    await event_bus.connect()
    
    # Subscribe to events for WebSocket broadcasting
    async def broadcast_to_ws(event: dict[str, Any]) -> None:
        await ws_manager.broadcast("events", event)
    
    event_bus.subscribe("#", broadcast_to_ws)  # Subscribe to all topics
    
    yield
    
    # Shutdown
    logger.info("Shutting down AMOS Platform Gateway...")

app = FastAPI(
    title="AMOS Platform API",
    description="Central API Gateway for the AMOS 5-Repository Integration",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# =============================================================================
# API Routes
# =============================================================================

@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint - no auth required."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "api": {"status": "healthy", "response_time_ms": 1.0},
            "brain": {"status": "healthy" if AMOS_BRAIN_AVAILABLE else "unavailable", "response_time_ms": 0},
        }
    }

@app.get("/status")
async def system_status(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    """Detailed system status."""
    return {
        "version": "1.0.0",
        "uptime_seconds": int(time.time()),  # TODO: Track actual uptime
        "user": user["email"],
        "components": {
            "api": {"status": "healthy", "latency_ms": 1.0, "last_check": datetime.now(timezone.utc).isoformat()},
            "brain": {"status": "healthy" if AMOS_BRAIN_AVAILABLE else "unavailable", "latency_ms": 0},
        },
        "queue_depth": 0,
        "active_tasks": len([t for t in task_store._tasks.values() if t["status"] == "running"]),
    }

# Chat Routes
@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: dict[str, Any] = Depends(get_current_user),
) -> ChatResponse:
    """Send chat message and get AI response."""
    request_id = str(uuid.uuid4())
    
    # TODO: Integrate with actual AMOS brain
    # For now, return mock response
    response = ChatResponse(
        id=request_id,
        message=f"Echo: {request.message}",
        model=request.model or "default",
        usage={"prompt_tokens": len(request.message), "completion_tokens": 10, "total_tokens": 10 + len(request.message)},
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    
    # Publish event
    await event_bus.publish("chat.message.sent", {
        "request_id": request_id,
        "workspace_id": request.workspace_id,
        "user_id": user["id"],
    })
    
    return response

# Agent Routes
@app.post("/agent/run", response_model=AgentRunAccepted, status_code=202)
async def run_agent(
    request: AgentRunRequest,
    user: dict[str, Any] = Depends(get_current_user),
) -> AgentRunAccepted:
    """Execute an agent task asynchronously."""
    task_id = task_store.create("agent", request.model_dump())
    
    # Update to running
    task_store.update(task_id, status="running")
    
    # Publish event
    await event_bus.publish("claws.agent.requested", {
        "task_id": task_id,
        "agent_type": request.agent_type,
        "target_repo": request.target_repo,
        "priority": request.priority,
        "user_id": user["id"],
    })
    
    return AgentRunAccepted(
        task_id=task_id,
        status="running",
        estimated_duration_seconds=300,
        queue_position=0,
    )

@app.get("/agent/status/{task_id}", response_model=AgentRunResult)
async def get_agent_status(
    task_id: str,
    user: dict[str, Any] = Depends(get_current_user),
) -> AgentRunResult:
    """Get agent task status."""
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return AgentRunResult(
        task_id=task["id"],
        status=task["status"],
        agent_type=task["params"]["agent_type"],
        result=task.get("result"),
        error=task.get("error"),
        started_at=task["created_at"],
        completed_at=task.get("completed_at"),
    )

@app.post("/agent/cancel/{task_id}")
async def cancel_agent(
    task_id: str,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Cancel a running agent task."""
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_store.update(task_id, status="cancelled")
    
    await event_bus.publish("agent.cancelled", {
        "task_id": task_id,
        "user_id": user["id"],
    })
    
    return {"success": True, "message": "Task cancelled"}

# Repository Routes
@app.post("/repo/scan", status_code=202)
async def scan_repo(
    request: RepoScanRequest,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Initiate repository scan."""
    scan_id = task_store.create("repo_scan", request.model_dump())
    task_store.update(scan_id, status="running")
    
    await event_bus.publish("repo.scan.started", {
        "scan_id": scan_id,
        "repo_url": request.repo_url,
        "user_id": user["id"],
    })
    
    return {"scan_id": scan_id, "status": "running"}

@app.post("/repo/fix", status_code=202)
async def fix_repo(
    request: RepoFixRequest,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Apply fixes to repository."""
    fix_id = task_store.create("repo_fix", request.model_dump())
    task_store.update(fix_id, status="running")
    
    await event_bus.publish("repo.fix.started", {
        "fix_id": fix_id,
        "repo_url": request.repo_url,
        "scan_id": request.scan_id,
        "user_id": user["id"],
    })
    
    return {"fix_id": fix_id, "status": "running"}

@app.get("/repo/status/{scan_id}")
async def get_repo_status(
    scan_id: str,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Get repository scan status."""
    task = task_store.get(scan_id)
    if not task:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {
        "scan_id": task["id"],
        "repo_url": task["params"]["repo_url"],
        "status": task["status"],
        "progress": task.get("progress", 0),
        "findings": task.get("result", {}).get("findings", []),
        "summary": task.get("result", {}).get("summary", {}),
    }

# Workflow Routes
@app.post("/workflow/run", status_code=202)
async def run_workflow(
    request: WorkflowRunRequest,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Execute a workflow."""
    execution_id = task_store.create("workflow", request.model_dump())
    task_store.update(execution_id, status="running")
    
    await event_bus.publish("workflow.started", {
        "execution_id": execution_id,
        "workflow_id": request.workflow_id,
        "user_id": user["id"],
    })
    
    return {
        "workflow_id": request.workflow_id,
        "execution_id": execution_id,
        "status": "running",
    }

@app.get("/workflow/status/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Get workflow status."""
    task = task_store.get(workflow_id)
    if not task:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return {
        "execution_id": task["id"],
        "workflow_id": task["params"]["workflow_id"],
        "status": task["status"],
        "progress_percent": task.get("progress", 0),
        "started_at": task["created_at"],
    }

# Model Routes
@app.get("/models")
async def list_models(
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """List available AI models."""
    # Mock models - in production, query Ollama/LM Studio/etc.
    models = [
        ModelInfo(
            id="llama3.1",
            name="Llama 3.1",
            provider="ollama",
            status="available",
            capabilities=["chat", "completion"],
            context_window=8192,
        ),
        ModelInfo(
            id="qwen2.5",
            name="Qwen 2.5",
            provider="vllm",
            status="available",
            capabilities=["chat", "completion", "code"],
            context_window=32768,
        ),
    ]
    
    return {"models": [m.model_dump() for m in models]}

# Task Routes
@app.get("/tasks")
async def list_tasks(
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """List user tasks."""
    tasks = task_store.list(status=status, limit=limit, offset=offset)
    return {
        "tasks": tasks,
        "total": len(task_store._tasks),
    }

@app.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Get task details."""
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    user: dict[str, Any] = Depends(get_current_user),
) -> None:
    """Delete a task."""
    if task_id in task_store._tasks:
        del task_store._tasks[task_id]

# WebSocket Route
@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time updates."""
    client_id = str(uuid.uuid4())
    await ws_manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            
            if msg_type == "auth":
                # Handle authentication
                token = data.get("token")
                # Validate token
                await ws_manager.send_to_client(client_id, {
                    "type": "auth_result",
                    "success": token == "test-token",
                })
            
            elif msg_type == "subscribe":
                channel = data.get("channel")
                await ws_manager.subscribe(client_id, channel)
                await ws_manager.send_to_client(client_id, {
                    "type": "subscribed",
                    "channel": channel,
                })
            
            elif msg_type == "unsubscribe":
                channel = data.get("channel")
                await ws_manager.unsubscribe(client_id, channel)
            
            elif msg_type == "ping":
                await ws_manager.send_to_client(client_id, {"type": "pong"})
    
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)

# =============================================================================
# Event Handlers (for async processing)
# =============================================================================

async def handle_repo_scan_completed(event: dict[str, Any]) -> None:
    """Handle repo scan completion."""
    payload = event.get("payload", {})
    scan_id = payload.get("scan_id")
    
    if scan_id:
        task_store.update(scan_id, status="completed", result=payload.get("result"))
        
        # Broadcast to WebSocket
        await ws_manager.broadcast("repo.scans", {
            "type": "repo.scan.completed",
            "scan_id": scan_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

# Subscribe to events
event_bus.subscribe("repo.scan.completed", handle_repo_scan_completed)

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
