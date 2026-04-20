"""AMOS MCP FastAPI Bridge — HTTP REST API for MCP Tools.

Exposes MCP tools via FastAPI HTTP endpoints with RESTful API, SSE streaming,
authentication, rate limiting, and OpenAPI documentation.

Owner: Trang
Version: 1.0.0
"""

import time
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone

UTC = UTC
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from amos_cognitive_bridge_v2 import AMOSCognitiveBridge, CognitiveResponse

# ============================================================================
# Pydantic Models
# ============================================================================


class ToolCallRequest(BaseModel):
    tool: str = Field(..., description="MCP tool name")
    arguments: dict[str, Any] = Field(default_factory=dict)
    request_id: str = None


class ToolCallResponse(BaseModel):
    request_id: str
    tool: str
    success: bool
    result: dict[str, Any]
    execution_time_ms: float
    health_score: float
    timestamp: str


class ToolInfo(BaseModel):
    name: str
    description: str
    subsystem: str
    parameters: dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    health_score: float
    bootstrap_phase: str
    equations_available: int
    timestamp: str


# ============================================================================
# Rate Limiting
# ============================================================================


@dataclass
class RateLimitEntry:
    requests: int = 0
    window_start: float = field(default_factory=time.time)
    blocked_until: float = None


class RateLimiter:
    def __init__(self, requests_per_minute: int = 60, burst_size: int = 10):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self._limits: dict[str, RateLimitEntry] = {}
        self._window_seconds = 60.0

    def is_allowed(self, api_key: str) -> tuple[bool, dict[str, Any]]:
        now = time.time()
        entry = self._limits.get(api_key, RateLimitEntry())

        if now - entry.window_start > self._window_seconds:
            entry = RateLimitEntry(window_start=now)

        if entry.blocked_until and now < entry.blocked_until:
            return False, {
                "error": "Rate limit exceeded",
                "retry_after": int(entry.blocked_until - now),
            }

        if entry.requests >= self.burst_size:
            entry.blocked_until = now + self._window_seconds
            self._limits[api_key] = entry
            return False, {"error": "Burst limit exceeded", "retry_after": 60}

        if entry.requests >= self.requests_per_minute:
            entry.blocked_until = now + self._window_seconds
            self._limits[api_key] = entry
            return False, {"error": "Rate limit exceeded", "retry_after": 60}

        entry.requests += 1
        self._limits[api_key] = entry
        return True, {
            "limit": self.requests_per_minute,
            "remaining": self.requests_per_minute - entry.requests,
        }


# ============================================================================
# Authentication
# ============================================================================

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

API_KEYS: dict[str, dict[str, Any]] = {
    "amos-dev-key-001": {
        "name": "Development",
        "rate_limit": 100,
        "permissions": ["read", "write", "execute"],
    },
    "amos-prod-key-001": {
        "name": "Production",
        "rate_limit": 1000,
        "permissions": ["read", "write", "execute", "admin"],
    },
}

rate_limiter = RateLimiter()


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")
    if api_key not in API_KEYS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")

    allowed, info = rate_limiter.is_allowed(api_key)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=info["error"],
            headers={"Retry-After": str(info["retry_after"])},
        )
    return api_key


# ============================================================================
# FastAPI Application
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting AMOS MCP FastAPI Bridge...")
    bridge = AMOSCognitiveBridge()
    await bridge.initialize()
    app.state.cognitive_bridge = bridge
    app.state.startup_time = time.time()
    print("MCP FastAPI Bridge ready")
    yield
    print("Shutting down MCP FastAPI Bridge...")


app = FastAPI(
    title="AMOS MCP API",
    description="HTTP REST API for AMOS Model Context Protocol tools",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/")
async def root():
    return {
        "name": "AMOS MCP API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "tools": "/mcp/tools",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(api_key: str = Depends(verify_api_key)):
    bridge: AMOSCognitiveBridge = app.state.cognitive_bridge
    stats = bridge.get_stats()
    return HealthResponse(
        status="healthy" if stats["initialized"] else "initializing",
        health_score=stats.get("health_score", 0.0),
        bootstrap_phase=stats.get("bootstrap_phase", "unknown"),
        equations_available=stats.get("equations_available", 0),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/mcp/tools", response_model=list[ToolInfo])
async def list_tools(api_key: str = Depends(verify_api_key)):
    tools = [
        ToolInfo(
            name="brain_think",
            description="Process a thought",
            subsystem="brain",
            parameters={"thought": "string", "thought_type": "string (optional)"},
        ),
        ToolInfo(
            name="brain_plan",
            description="Create a plan",
            subsystem="brain",
            parameters={"goal": "string", "horizon": "string (optional)"},
        ),
        ToolInfo(
            name="brain_remember",
            description="Store in memory",
            subsystem="brain",
            parameters={"key": "string", "value": "any"},
        ),
        ToolInfo(
            name="senses_scan",
            description="Scan environment",
            subsystem="senses",
            parameters={"path": "string (optional)", "depth": "integer (optional)"},
        ),
        ToolInfo(
            name="senses_gather",
            description="Gather context",
            subsystem="senses",
            parameters={
                "topic": "string",
                "sources": "list (optional)",
                "max_items": "integer (optional)",
            },
        ),
        ToolInfo(
            name="muscle_execute",
            description="Execute command",
            subsystem="muscle",
            parameters={"command": "string", "timeout_seconds": "integer (optional)"},
        ),
        ToolInfo(
            name="muscle_code",
            description="Run code",
            subsystem="muscle",
            parameters={"code": "string", "language": "string (optional)"},
        ),
        ToolInfo(
            name="immune_validate",
            description="Validate action",
            subsystem="immune",
            parameters={"action": "string", "context": "dict (optional)"},
        ),
    ]
    return tools


@app.post("/mcp/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest, api_key: str = Depends(verify_api_key)):
    bridge: AMOSCognitiveBridge = app.state.cognitive_bridge
    if not bridge._initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cognitive bridge not initialized",
        )

    request_id = request.request_id or str(uuid.uuid4())[:8]
    start_time = time.time()

    try:
        response: CognitiveResponse = await bridge.process_tool_call(
            tool_name=request.tool, arguments=request.arguments
        )
        execution_time = (time.time() - start_time) * 1000
        return ToolCallResponse(
            request_id=request_id,
            tool=request.tool,
            success=response.success,
            result=response.result,
            execution_time_ms=execution_time,
            health_score=bridge.get_stats().get("health_score", 0.0),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return ToolCallResponse(
            request_id=request_id,
            tool=request.tool,
            success=False,
            result={"error": str(e)},
            execution_time_ms=execution_time,
            health_score=bridge.get_stats().get("health_score", 0.0),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


@app.post("/mcp/tools/call/stream")
async def call_tool_stream(request: ToolCallRequest, api_key: str = Depends(verify_api_key)):
    bridge: AMOSCognitiveBridge = app.state.cognitive_bridge
    if not bridge._initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cognitive bridge not initialized",
        )

    async def event_generator() -> AsyncGenerator[str, None]:
        request_id = request.request_id or str(uuid.uuid4())[:8]
        yield f'data: {{"event": "init", "request_id": "{request_id}"}}\n\n'
        start_time = time.time()

        try:
            response: CognitiveResponse = await bridge.process_tool_call(
                tool_name=request.tool, arguments=request.arguments
            )
            execution_time = (time.time() - start_time) * 1000
            result = {
                "event": "complete",
                "request_id": request_id,
                "tool": request.tool,
                "success": response.success,
                "result": response.result,
                "execution_time_ms": execution_time,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            yield f"data: {result}\n\n"
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error = {
                "event": "error",
                "request_id": request_id,
                "tool": request.tool,
                "error": str(e),
                "execution_time_ms": execution_time,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            yield f"data: {error}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.get("/mcp/stats")
async def get_stats(api_key: str = Depends(verify_api_key)):
    bridge: AMOSCognitiveBridge = app.state.cognitive_bridge
    stats = bridge.get_stats()
    stats["uptime_seconds"] = time.time() - app.state.startup_time
    return stats


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
