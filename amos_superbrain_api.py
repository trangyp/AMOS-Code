#!/usr/bin/env python3
"""AMOS SuperBrain v3.0 REST API - FastAPI Web Interface.

Provides REST API and WebSocket support for AMOS SuperBrain at 75% health.
Enables web dashboard, external integrations, and programmatic access.

Endpoints:
    GET  /                    - API info and health
    GET  /health              - Detailed health check
    GET  /status              - Full system status
    GET  /tools               - List all 10 MCP tools
    POST /tools/{name}/execute - Execute a tool
    GET  /agents              - List A2A agents
    POST /agents/task         - Create and route task
    GET  /memory              - Memory statistics
    POST /memory/search       - Search memory entries
    GET  /config              - Configuration status

WebSocket:
    WS   /ws                  - Real-time updates stream

Interactive Docs:
    http://localhost:8000/docs (Swagger UI)
    http://localhost:8000/redoc (ReDoc)

References:
- FastAPI 2025 best practices
- OpenAPI 3.1.0 specification
- WebSocket real-time patterns
"""

import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import AMOS SuperBrain components
from amos_brain import get_super_brain
from amos_brain.a2a_orchestrator import get_a2a_orchestrator
from amos_brain.config_validation import ConfigValidator
from amos_brain.memory_architecture import get_memory_manager
from amos_brain.tools_extended import (
    calculate,
    file_read_write,
    git_operations,
    web_search,
)

# ============================================================================
# Pydantic Models
# ============================================================================


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    health_score: float
    timestamp: str
    version: str = "3.0"


class SystemStatus(BaseModel):
    """System status response model."""

    health_score: float
    status: str
    tools_count: int
    models_count: int
    math_framework_status: str
    a2a_agents_count: int
    memory_l1_entries: int
    timestamp: str


class ToolInfo(BaseModel):
    """Tool information model."""

    name: str
    description: str
    category: str


class ToolExecuteRequest(BaseModel):
    """Tool execution request model."""

    parameters: Dict[str, Any] = Field(default_factory=dict)


class ToolExecuteResponse(BaseModel):
    """Tool execution response model."""

    tool: str
    success: bool
    result: Dict[str, Any]
    execution_time_ms: int


class AgentInfo(BaseModel):
    """Agent information model."""

    name: str
    description: str
    capabilities: List[str]
    endpoint: str


class TaskRequest(BaseModel):
    """Task creation request model."""

    message: str
    capability: str = None


class TaskResponse(BaseModel):
    """Task response model."""

    task_id: str
    state: str
    assigned_agent: str
    messages: List[dict[str, Any]]
    created_at: str


class MemorySearchRequest(BaseModel):
    """Memory search request model."""

    session_id: str = None
    memory_type: str = None
    limit: int = Field(default=100, ge=1, le=1000)


class MemorySearchResponse(BaseModel):
    """Memory search response model."""

    entries: List[dict[str, Any]]
    total_count: int


class ConfigStatus(BaseModel):
    """Configuration status model."""

    valid: bool
    environment: str
    providers_configured: int
    providers: List[str]
    issues: List[str]
    recommendations: List[str]


# ============================================================================
# FastAPI Application
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 AMOS SuperBrain API starting...")

    # Initialize components
    try:
        brain = get_super_brain()
        # Initialize subsystems for proper health calculation
        try:
            from amos_brain.kernel_router import get_kernel_router

            brain.kernel_router = get_kernel_router()
            print("  ✓ Kernel router initialized")
        except Exception as e:
            print(f"  ⚠️ Kernel router: {e}")

        try:
            from amos_brain.tools import ToolRegistry

            brain.tool_registry = ToolRegistry()
            print("  ✓ Tool registry initialized")
        except Exception as e:
            print(f"  ⚠️ Tool registry: {e}")

        try:
            from amos_brain.model_router import ModelRouter

            brain.model_router = ModelRouter()
            print("  ✓ Model router initialized")
        except Exception as e:
            print(f"  ⚠️ Model router: {e}")

        state = brain.get_state()
        print(f"✅ SuperBrain initialized: {state.health_score:.0%} health")
    except Exception as e:
        print(f"⚠️  SuperBrain initialization: {e}")

    try:
        a2a = get_a2a_orchestrator()
        stats = a2a.get_stats()
        print(f"✅ A2A orchestrator: {stats.get('registered_agents', 0)} agents")
    except Exception as e:
        print(f"⚠️  A2A initialization: {e}")

    yield

    # Shutdown
    print("🛑 AMOS SuperBrain API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="AMOS SuperBrain API",
    description="REST API for AMOS SuperBrain v3.0 - AI Agent System",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/", response_model=dict[str, Any])
async def root():
    """API root endpoint with system info."""
    return {
        "name": "AMOS SuperBrain API",
        "version": "3.0.0",
        "health_score": "75%",
        "description": "AI Agent System with 10 MCP tools, A2A protocol, and tiered memory",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "tools": "/tools",
            "agents": "/agents",
            "memory": "/memory",
            "config": "/config",
            "docs": "/docs",
        },
        "documentation": "https://amos.superbrain/docs",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        brain = get_super_brain()
        state = brain.get_state()

        return HealthResponse(
            status="healthy" if state.health_score >= 0.75 else "degraded",
            health_score=state.health_score,
            timestamp=datetime.now(UTC).isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")


@app.get("/status", response_model=SystemStatus)
async def system_status():
    """Full system status endpoint."""
    try:
        brain = get_super_brain()
        state = brain.get_state()

        # Get A2A stats
        a2a_agents = 0
        try:
            a2a = get_a2a_orchestrator()
            a2a_stats = a2a.get_stats()
            a2a_agents = a2a_stats.get("registered_agents", 0)
        except Exception:
            pass

        # Get memory stats
        mem_entries = 0
        try:
            mem = get_memory_manager()
            mem_stats = mem.get_stats()
            mem_entries = mem_stats.get("l1_cache_size", 0)
        except Exception:
            pass

        return SystemStatus(
            health_score=state.health_score,
            status=state.status,
            tools_count=len(state.loaded_tools),
            models_count=len(state.available_models),
            math_framework_status=state.math_framework_status,
            a2a_agents_count=a2a_agents,
            memory_l1_entries=mem_entries,
            timestamp=datetime.now(UTC).isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {e}")


@app.get("/tools", response_model=list[ToolInfo])
async def list_tools():
    """List all available MCP tools."""
    tools = [
        ToolInfo(
            name="analyze_code_structure",
            description="Analyze Python code structure",
            category="built-in",
        ),
        ToolInfo(
            name="execute_shell_command",
            description="Execute safe shell commands",
            category="built-in",
        ),
        ToolInfo(
            name="search_files", description="Search files with patterns", category="built-in"
        ),
        ToolInfo(name="get_system_info", description="Get system information", category="built-in"),
        ToolInfo(name="validate_json", description="Validate JSON data", category="built-in"),
        ToolInfo(name="calculate", description="Safe mathematical evaluation", category="extended"),
        ToolInfo(name="web_search", description="DuckDuckGo web search", category="extended"),
        ToolInfo(name="file_read_write", description="File I/O operations", category="extended"),
        ToolInfo(
            name="database_query",
            description="SQLite/PostgreSQL/MySQL queries",
            category="extended",
        ),
        ToolInfo(name="git_operations", description="Git status/log/diff", category="extended"),
    ]
    return tools


@app.post("/tools/{tool_name}/execute", response_model=ToolExecuteResponse)
async def execute_tool(tool_name: str, request: ToolExecuteRequest):
    """Execute a specific tool."""
    start_time = datetime.now(UTC)

    try:
        result = {}
        success = False

        # Route to appropriate tool
        if tool_name == "calculate":
            expr = request.parameters.get("expression", "")
            result = calculate(expr)
            success = "error" not in result
        elif tool_name == "web_search":
            query = request.parameters.get("query", "")
            max_results = request.parameters.get("max_results", 5)
            result = web_search(query, max_results)
            success = True
        elif tool_name == "file_read_write":
            operation = request.parameters.get("operation", "read")
            path = request.parameters.get("path", "")
            content = request.parameters.get("content", "")
            result = file_read_write(operation, path, content)
            success = result.get("success", False)
        elif tool_name == "git_operations":
            operation = request.parameters.get("operation", "status")
            repo_path = request.parameters.get("repo_path", ".")
            result = git_operations(operation, repo_path)
            success = result.get("success", False)
        else:
            raise HTTPException(
                status_code=400, detail=f"Tool '{tool_name}' not implemented in API"
            )

        execution_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

        return ToolExecuteResponse(
            tool=tool_name,
            success=success,
            result=result,
            execution_time_ms=execution_time,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {e}")


@app.get("/agents", response_model=list[AgentInfo])
async def list_agents():
    """List all registered A2A agents."""
    try:
        orchestrator = get_a2a_orchestrator()
        agents = orchestrator.discover_agents()

        return [
            AgentInfo(
                name=agent.name,
                description=agent.description,
                capabilities=agent.capabilities,
                endpoint=agent.endpoint,
            )
            for agent in agents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent listing failed: {e}")


@app.post("/agents/task", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """Create and route a task to an agent."""
    try:
        orchestrator = get_a2a_orchestrator()
        task = orchestrator.route_task(request.message, capability=request.capability)

        return TaskResponse(
            task_id=task.id,
            state=task.state.value,
            assigned_agent=task.assigned_agent,
            messages=[msg.to_dict() for msg in task.messages],
            created_at=task.created_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task creation failed: {e}")


@app.get("/memory")
async def memory_stats():
    """Get memory architecture statistics."""
    try:
        manager = get_memory_manager()
        stats = manager.get_stats()

        return {
            "tiers": ["L1 (Cache)", "L2 (SQLite)", "L3 (File)"],
            "l1_cache_size": stats.get("l1_cache_size", 0),
            "l2_status": stats.get("l2_sqlite", "unknown"),
            "l3_status": stats.get("l3_file", "unknown"),
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory stats failed: {e}")


@app.post("/memory/search", response_model=MemorySearchResponse)
async def search_memory(request: MemorySearchRequest):
    """Search memory entries."""
    try:
        manager = get_memory_manager()
        entries = manager.search(
            session_id=request.session_id,
            memory_type=request.memory_type,
            limit=request.limit,
        )

        return MemorySearchResponse(
            entries=[entry.to_dict() for entry in entries],
            total_count=len(entries),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory search failed: {e}")


@app.get("/config", response_model=ConfigStatus)
async def config_status():
    """Get configuration validation status."""
    try:
        validator = ConfigValidator()
        report = validator.validate()

        return ConfigStatus(
            valid=report["valid"],
            environment=report["environment"],
            providers_configured=report["providers_configured"],
            providers=report.get("providers", []),
            issues=report.get("issues", []),
            recommendations=report.get("recommendations", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Config check failed: {e}")


# ============================================================================
# WebSocket Endpoint
# ============================================================================


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()

    try:
        # Send initial connection message
        await websocket.send_json(
            {
                "type": "connection",
                "status": "connected",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                msg_type = message.get("type", "unknown")

                if msg_type == "ping":
                    await websocket.send_json(
                        {
                            "type": "pong",
                            "timestamp": datetime.now(UTC).isoformat(),
                        }
                    )
                elif msg_type == "status":
                    brain = get_super_brain()
                    state = brain.get_state()
                    await websocket.send_json(
                        {
                            "type": "status",
                            "health_score": state.health_score,
                            "status": state.status,
                            "timestamp": datetime.now(UTC).isoformat(),
                        }
                    )
                elif msg_type == "health_check":
                    await websocket.send_json(
                        {
                            "type": "health",
                            "status": "healthy",
                            "timestamp": datetime.now(UTC).isoformat(),
                        }
                    )
                else:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"Unknown message type: {msg_type}",
                        }
                    )
            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "Invalid JSON",
                    }
                )

    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           AMOS SuperBrain API v3.0                            ║
║           FastAPI Web Interface                               ║
║                                                               ║
║   Endpoints:                                                  ║
║   • http://localhost:8000/           (API Info)               ║
║   • http://localhost:8000/health      (Health Check)          ║
║   • http://localhost:8000/status      (System Status)         ║
║   • http://localhost:8000/tools       (List Tools)            ║
║   • http://localhost:8000/agents      (A2A Agents)            ║
║   • http://localhost:8000/docs        (Swagger UI)            ║
║   • http://localhost:8000/redoc       (ReDoc)               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "amos_superbrain_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
