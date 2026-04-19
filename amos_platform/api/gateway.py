"""AMOS Platform API Gateway - Central HTTP API for 6-repo ecosystem.

This is the production FastAPI gateway for AMOS-Consulting (amos-platform).
It provides:
- REST API endpoints for all AMOS operations
- WebSocket support for real-time events
- Integration with amos-brain for cognitive operations
- Integration with amos-universe for contracts
"""

from __future__ import annotations

import asyncio
import json
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

# Use amos-universe contracts
from amos_universe.contracts.pydantic import (
    ChatRequest, ChatResponse,
    RepoScanRequest, RepoScanResult,
    RepoFixRequest, RepoFixResult,
    ModelRequest, ModelResponse, ModelInfo,
    WorkflowRunRequest, WorkflowRunResponse,
    BrainRunRequest, BrainRunResponse,
    ApiError, ErrorCode,
    BaseEvent, EventType,
)

# Import LLM router
from amos_platform.core.llm_router import LLMRouter, LLMBackend

# Import event bus
from amos_platform.events.bus import EventBus

# Version
__version__ = "1.0.0"


class GatewayState:
    """Shared state for the API gateway."""
    
    def __init__(self):
        self.llm_router: LLMRouter | None = None
        self.event_bus: EventBus | None = None
        self.active_connections: list[WebSocket] = []
        self.startup_time: float = 0.0


state = GatewayState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    print("🚀 AMOS Platform API Gateway starting...")
    
    # Initialize LLM router
    state.llm_router = LLMRouter()
    await state.llm_router.initialize()
    
    # Initialize event bus
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    state.event_bus = EventBus(redis_url=redis_url)
    await state.event_bus.connect()
    
    # Start event listener in background
    asyncio.create_task(_listen_for_events())
    
    import time
    state.startup_time = time.time()
    
    print(f"✅ Gateway ready - {__version__}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down gateway...")
    if state.event_bus:
        await state.event_bus.disconnect()
    print("✅ Shutdown complete")


async def _listen_for_events():
    """Background task to listen for events and broadcast to WebSockets."""
    if not state.event_bus:
        return
    
    async for event in state.event_bus.listen():
        # Broadcast to all connected WebSockets
        disconnected = []
        for ws in state.active_connections:
            try:
                await ws.send_json(event.to_dict())
            except Exception:
                disconnected.append(ws)
        
        # Clean up disconnected clients
        for ws in disconnected:
            if ws in state.active_connections:
                state.active_connections.remove(ws)


# Create FastAPI app
app = FastAPI(
    title="AMOS Platform API",
    description="Central API gateway for the AMOS 6-repository ecosystem",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS for frontend repos
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
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# =============================================================================
# Health & Status Endpoints
# =============================================================================

@app.get("/", tags=["root"])
async def root() -> dict[str, Any]:
    """API information."""
    return {
        "name": "AMOS Platform API",
        "version": __version__,
        "docs": "/docs",
        "health": "/v1/health",
    }


@app.get("/v1/health", tags=["health"])
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    import time
    
    health = {
        "status": "healthy",
        "version": __version__,
        "uptime_seconds": time.time() - state.startup_time if state.startup_time else 0,
        "services": {
            "llm_router": "healthy" if state.llm_router else "unavailable",
            "event_bus": "healthy" if state.event_bus and state.event_bus.is_connected else "unavailable",
        },
        "active_websocket_connections": len(state.active_connections),
    }
    
    # Check if any service is unhealthy
    if any(s != "healthy" for s in health["services"].values()):
        health["status"] = "degraded"
        return JSONResponse(content=health, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    return health


@app.get("/v1/status", tags=["status"])
async def system_status() -> dict[str, Any]:
    """Detailed system status."""
    return {
        "gateway": {
            "version": __version__,
            "active_connections": len(state.active_connections),
        },
        "llm": {
            "backends_discovered": list(state.llm_router._backends.keys()) if state.llm_router else [],
        },
        "events": {
            "bus_connected": state.event_bus.is_connected if state.event_bus else False,
        },
    }


# =============================================================================
# Chat Endpoints
# =============================================================================

@app.post("/v1/chat", response_model=ChatResponse, tags=["chat"])
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Chat completion endpoint.
    
    Processes chat messages and returns AI-generated responses.
    """
    try:
        # Route to appropriate model via LLM router
        if not state.llm_router:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM router not available"
            )
        
        # Get available models
        models = await state.llm_router.list_models()
        if not models:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No LLM models available"
            )
        
        # Select model (auto or specified)
        model_id = request.model or models[0].model_id
        
        # Execute chat
        response = await state.llm_router.chat(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are AMOS, an AI assistant."},
                {"role": "user", "content": request.message},
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False,
        )
        
        return ChatResponse(
            message=response.get("content", ""),
            conversation_id=request.context.conversation_id or "new",
            session_id=request.context.session_id,
            model=model_id,
            usage=response.get("usage", {}),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )


# =============================================================================
# Model/LLM Endpoints
# =============================================================================

@app.get("/v1/models", response_model=list[ModelInfo], tags=["models"])
async def list_models() -> list[ModelInfo]:
    """List available LLM models."""
    if not state.llm_router:
        return []
    
    return await state.llm_router.list_models()


@app.post("/v1/models/run", response_model=ModelResponse, tags=["models"])
async def run_model(request: ModelRequest) -> ModelResponse:
    """Run inference on a specific model."""
    if not state.llm_router:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM router not available"
        )
    
    try:
        response = await state.llm_router.chat(
            model=request.model_id,
            messages=[{"role": "user", "content": request.prompt}],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream,
        )
        
        return ModelResponse(
            model_id=request.model_id,
            content=response.get("content", ""),
            usage=response.get("usage", {}),
            finish_reason=response.get("finish_reason", "stop"),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model execution failed: {str(e)}"
        )


# =============================================================================
# Repository Endpoints
# =============================================================================

@app.post("/v1/repo/scan", response_model=RepoScanResult, tags=["repo"])
async def scan_repository(request: RepoScanRequest) -> RepoScanResult:
    """Scan a repository for issues.
    
    This is a placeholder implementation. In production, this would:
    - Queue the scan as an async job
    - Use repo-doctor or similar tools
    - Publish events as scan progresses
    """
    import uuid
    from datetime import datetime, timezone
    
    scan_id = f"scan_{uuid.uuid4().hex[:8]}"
    
    # Publish event
    if state.event_bus:
        await state.event_bus.publish(BaseEvent(
            event_type=EventType.REPO_SCAN_STARTED,
            metadata={
                "event_id": f"evt_{uuid.uuid4().hex}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "amos-platform",
            },
            payload={
                "scan_id": scan_id,
                "repo_url": request.repo_path,
            }
        ))
    
    # Return initial result (async processing would continue in background)
    return RepoScanResult(
        scan_id=scan_id,
        repo_path=request.repo_path,
        status="pending",
        issues=[],
        summary={"status": "pending"},
        workspace_id=request.workspace_id,
    )


@app.post("/v1/repo/fix", response_model=RepoFixResult, tags=["repo"])
async def fix_repository(request: RepoFixRequest) -> RepoFixResult:
    """Apply fixes to a repository.
    
    Placeholder for automated fix application.
    """
    import uuid
    
    return RepoFixResult(
        fix_id=f"fix_{uuid.uuid4().hex[:8]}",
        scan_id=request.scan_id,
        repo_path=request.repo_path,
        status="pending",
        changes=[],
        summary={"status": "pending"},
    )


# =============================================================================
# Workflow Endpoints
# =============================================================================

@app.post("/v1/workflow/run", response_model=WorkflowRunResponse, tags=["workflow"])
async def run_workflow(request: WorkflowRunRequest) -> WorkflowRunResponse:
    """Execute a workflow.
    
    Placeholder for workflow orchestration.
    """
    import uuid
    
    return WorkflowRunResponse(
        workflow_id=request.workflow_id,
        execution_id=f"exec_{uuid.uuid4().hex[:8]}",
        status="pending",
        results=[],
        started_at=datetime.now(timezone.utc),
    )


# =============================================================================
# Brain/Cognitive Endpoints
# =============================================================================

@app.post("/v1/brain/run", response_model=BrainRunResponse, tags=["brain"])
async def run_brain(request: BrainRunRequest) -> BrainRunResponse:
    """Execute AMOS brain cycle.
    
    Placeholder for cognitive processing.
    """
    import uuid
    
    return BrainRunResponse(
        execution_id=f"brain_{uuid.uuid4().hex[:8]}",
        status="completed",
        branches=[],
        selected_branch=None,
        execution_time_ms=0.0,
    )


# =============================================================================
# Universe/Contract Endpoints
# =============================================================================

@app.get("/v1/universe/event-types", tags=["universe"])
async def list_event_types() -> dict[str, Any]:
    """List all canonical event types."""
    return {
        "event_types": [
            {
                "value": e.value,
                "category": e.value.split(".")[0] if "." in e.value else "system",
                "name": e.name,
            }
            for e in EventType
        ]
    }


# =============================================================================
# WebSocket Endpoint
# =============================================================================

@app.websocket("/v1/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time event streaming."""
    await websocket.accept()
    state.active_connections.append(websocket)
    
    try:
        while True:
            # Receive client messages (subscriptions, etc.)
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle subscription requests
            if message.get("action") == "subscribe":
                event_types = message.get("event_types", [])
                await websocket.send_json({
                    "type": "subscribed",
                    "event_types": event_types,
                })
            
            # Handle ping
            elif message.get("action") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()})
                
    except WebSocketDisconnect:
        if websocket in state.active_connections:
            state.active_connections.remove(websocket)
    except Exception:
        if websocket in state.active_connections:
            state.active_connections.remove(websocket)


# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiError(
            code=ErrorCode.INTERNAL_ERROR if exc.status_code >= 500 else ErrorCode.VALIDATION_ERROR,
            message=exc.detail,
            request_id=getattr(request.state, "request_id", None),
        ).to_dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiError(
            code=ErrorCode.INTERNAL_ERROR,
            message=str(exc),
            request_id=getattr(request.state, "request_id", None),
        ).to_dict(),
    )


# Import routes
from datetime import datetime, timezone

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "amos_platform.api.gateway:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info",
    )
