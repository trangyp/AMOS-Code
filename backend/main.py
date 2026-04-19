"""AMOS Backend API - FastAPI Application

The cognitive engine powering the AMOS Dashboard.

Architecture:
- FastAPI for high-performance async API
- Pydantic for type-safe data models
- PostgreSQL with SQLAlchemy 2.0 async
- WebSocket for real-time frontend updates
- REST endpoints for all 11 cognitive subsystems
- Structured logging with structlog
- Prometheus metrics instrumentation

Creator: Trang Phan
Version: 3.0.0
"""

import json
import sys
import uuid
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

# Import database and config first
from backend.config import settings
from backend.database import check_connection, engine, init_database

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("amos.api")

# Import AMOS Brain - PERMANENT ACTIVATION
_AMOS_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(_AMOS_ROOT / "clawspring" / "amos_brain"))

try:
    from amos_brain_working import think as brain_think

    _BRAIN_AVAILABLE = True
except ImportError:
    brain_think = None
    _BRAIN_AVAILABLE = False
    logger.warning("amos_brain_working not available, brain features disabled")

# Import modular API routers
from backend.api.agents import router as agents_router
from backend.api.auth import router as auth_router
from backend.api.brain import router as brain_router
from backend.api.brain_auto_heal import router as brain_auto_heal_router
from backend.api.brain_cognitive_analysis import router as brain_cognitive_router
from backend.api.brain_self_healing import router as brain_self_healing_router
from backend.api.brain_websocket import router as brain_websocket_router
from backend.api.canon import router as canon_router
from backend.api.health import router as health_router
from backend.api.llm import router as llm_router
from backend.api.math import router as math_router
from backend.api.streaming import router as streaming_router
from backend.api.superbrain import router as superbrain_router
from backend.api.system import router as system_router

try:
    from backend.api.axiom_one import router as axiom_one_router

    _AXIOM_ONE_AVAILABLE = True
except ImportError:
    axiom_one_router = None
    _AXIOM_ONE_AVAILABLE = False

try:
    from backend.api.axiom_one_slots import router as axiom_one_slots_router

    _AXIOM_ONE_SLOTS_AVAILABLE = True
except ImportError:
    axiom_one_slots_router = None
    _AXIOM_ONE_SLOTS_AVAILABLE = False

try:
    from backend.api.cognitive_websocket import router as cognitive_ws_router

    _COGNITIVE_WS_AVAILABLE = True
except ImportError:
    cognitive_ws_router = None
    _COGNITIVE_WS_AVAILABLE = False

try:
    from backend.api.agent_monitor import router as agent_monitor_router

    _AGENT_MONITOR_AVAILABLE = True
except ImportError:
    agent_monitor_router = None
    _AGENT_MONITOR_AVAILABLE = False

try:
    from backend.api.simulation_dashboard import router as simulation_dashboard_router

    _SIMULATION_DASHBOARD_AVAILABLE = True
except ImportError:
    simulation_dashboard_router = None
    _SIMULATION_DASHBOARD_AVAILABLE = False

try:
    from backend.api.unified_orchestrator import router as unified_orchestrator_router

    _UNIFIED_ORCH_AVAILABLE = True
except ImportError:
    unified_orchestrator_router = None
    _UNIFIED_ORCH_AVAILABLE = False

try:
    from backend.api.brain_task_execution import router as brain_task_router

    _BRAIN_TASK_AVAILABLE = True
except ImportError:
    brain_task_router = None
    _BRAIN_TASK_AVAILABLE = False

try:
    from backend.api.brain_unified_api import router as brain_unified_router

    _BRAIN_UNIFIED_AVAILABLE = True
except ImportError:
    brain_unified_router = None
    _BRAIN_UNIFIED_AVAILABLE = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager.

    Handles startup and shutdown events with proper resource management.
    """
    # Startup
    logger.info("amos_api_starting", version="3.0.0")

    # Initialize brain
    if _BRAIN_AVAILABLE and brain_think:
        try:
            _brain_result = brain_think("Initialize AMOS brain", {"startup": True})
            logger.info(
                "brain_initialized",
                status=_brain_result.get("status"),
                legality=_brain_result.get("legality"),
            )
        except Exception as e:
            logger.error("brain_init_failed", error=str(e))

    # Also initialize super_brain if available
    try:
        from amos_brain import get_super_brain

        brain = get_super_brain()
        print(f"✅ Brain initialized: {brain.get_state().health_score:.0%} health")
    except Exception as e:
        print(f"⚠️ Brain init: {e}")

    # Initialize database
    try:
        db_ok = await check_connection()
        if db_ok:
            await init_database()
            logger.info("database_initialized")
        else:
            logger.error("database_connection_failed")
    except Exception as e:
        logger.error("database_init_failed", error=str(e))

    # Initialize Prometheus instrumentation
    Instrumentator().instrument(app).expose(app)
    logger.info("metrics_instrumentation_enabled")

    logger.info("amos_api_ready")

    print("=" * 60)
    print("🧠 AMOS Backend API Starting...")
    print("=" * 60)
    print("Version: 3.0.0")
    print("Creator: Trang Phan")
    print("Architecture: 14-Layer Cognitive System")
    print(f"Mode: {cognitive_state['mode']}")
    print(f"Active Layers: {cognitive_state['layers']}")
    print("=" * 60)
    print("📡 API Endpoints:")
    print("  - GET  /")
    print("  - GET  /health")
    print("  - GET  /api/cognitive/mode")
    print("  - GET  /api/reasoning/levels")
    print("  - GET  /api/mcp/servers")
    print("  - GET  /api/agents/tasks")
    print("  - GET  /api/memory/entries")
    print("  - GET  /api/checkpoints")
    print("  - GET  /api/orchestra/agents")
    print("  - GET  /api/agents-md/files")
    print("  - GET  /api/system/status")
    print("  - WS   /ws")
    print("=" * 60)
    print("🚀 Ready for connections!")
    print("=" * 60)

    yield

    # Shutdown
    logger.info("amos_api_shutting_down")
    await engine.dispose()
    logger.info("amos_api_shutdown_complete")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="AMOS API",
    description="Absolute Meta Operating System - Cognitive Backend",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Request ID middleware for tracing
@app.middleware("http")
async def add_request_id(request: Request, call_next: Callable[[Request], Awaitable[Any]]) -> Any:
    """Add request ID for distributed tracing."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    start_time = datetime.now(timezone.utc)
    response = await call_next(request)
    end_time = datetime.now(timezone.utc)

    duration_ms = (end_time - start_time).total_seconds() * 1000

    response.headers["X-Request-ID"] = request_id

    # Structured access log
    logger.info(
        "http_request",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 3),
    )

    return response


# Enable CORS with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# Include modular API routers
app.include_router(agents_router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(brain_router, prefix="/api/v1/brain", tags=["Brain"])
app.include_router(
    brain_auto_heal_router, prefix="/api/v1/brain-auto-heal", tags=["Brain Auto-Heal"]
)
app.include_router(
    brain_cognitive_router, prefix="/api/v1/brain-cognitive", tags=["Brain Cognitive"]
)
app.include_router(
    brain_self_healing_router, prefix="/api/v1/brain-healing", tags=["Brain Self-Healing"]
)
app.include_router(brain_websocket_router, prefix="/api/v1", tags=["Brain WebSocket"])
app.include_router(canon_router, prefix="/api/v1/canon", tags=["Canon"])
app.include_router(health_router)
app.include_router(llm_router, prefix="/api/v1/llm", tags=["LLM"])
app.include_router(math_router, prefix="/api/v1/math", tags=["Math"])
app.include_router(streaming_router, prefix="/api/v1/streaming", tags=["Streaming"])
app.include_router(superbrain_router, prefix="/api/v1/superbrain", tags=["SuperBrain"])
app.include_router(system_router, prefix="/api/v1/system", tags=["System"])
if _AXIOM_ONE_AVAILABLE and axiom_one_router:
    app.include_router(axiom_one_router, prefix="/api/v1")
if _AXIOM_ONE_SLOTS_AVAILABLE and axiom_one_slots_router:
    app.include_router(axiom_one_slots_router)
if _COGNITIVE_WS_AVAILABLE and cognitive_ws_router:
    app.include_router(cognitive_ws_router)
if _AGENT_MONITOR_AVAILABLE and agent_monitor_router:
    app.include_router(agent_monitor_router)
if _SIMULATION_DASHBOARD_AVAILABLE and simulation_dashboard_router:
    app.include_router(simulation_dashboard_router)
if _UNIFIED_ORCH_AVAILABLE and unified_orchestrator_router:
    app.include_router(unified_orchestrator_router)
if _BRAIN_TASK_AVAILABLE and brain_task_router:
    app.include_router(brain_task_router)
if _BRAIN_UNIFIED_AVAILABLE and brain_unified_router:
    app.include_router(brain_unified_router)

# Brain Smart Gateway
from backend.api.brain_smart_gateway import router as brain_smart_gateway_router

app.include_router(brain_smart_gateway_router)

# Brain LLM Router
from backend.api.brain_llm_router import router as brain_llm_router

app.include_router(brain_llm_router)

# Brain Cognitive Streaming
from backend.api.brain_cognitive_streaming import router as brain_streaming_router

app.include_router(brain_streaming_router)

# Brain Agent Manager
from backend.api.brain_agent_manager import router as brain_agent_manager_router

app.include_router(brain_agent_manager_router)

# Brain Task Scheduler
from backend.api.brain_task_scheduler import router as brain_task_scheduler_router

app.include_router(brain_task_scheduler_router)

# ============================================================================
# DATA MODELS (Pydantic)
# ============================================================================


class CognitiveMode(BaseModel):
    mode: str  # seed, growth, full
    layers: int
    confidence: float
    active: bool


class ReasoningLevel(BaseModel):
    level: int
    name: str
    confidence: float
    status: str
    timestamp: str


class MCPServer(BaseModel):
    id: str
    name: str
    type: str
    status: str
    url: str
    last_ping: str


class AgentTask(BaseModel):
    id: str
    name: str
    description: str
    status: str  # pending, running, complete, error
    priority: int
    progress: float
    created_at: str
    completed_at: str = None


class MemoryEntry(BaseModel):
    id: str
    type: str  # episodic, semantic, procedural, working, long_term
    content: str
    importance: int
    tags: List[str]
    timestamp: str
    access_count: int


class Checkpoint(BaseModel):
    id: str
    name: str
    timestamp: str
    files_changed: int
    lines_added: int
    lines_removed: int
    description: str
    branch: str


class OrchestraAgent(BaseModel):
    id: str
    name: str
    tier: int
    instrument: str
    status: str
    task: str
    progress: float
    color: str


class SystemStatus(BaseModel):
    status: str
    uptime: str
    confidence: float
    active_layers: int
    total_layers: int
    components: Dict[str, str]


class AGENTSFile(BaseModel):
    id: str
    path: str
    scope: str
    sections: Dict[str, str]
    last_modified: str


# ============================================================================
# IN-MEMORY DATA STORE (Rapid Prototyping)
# ============================================================================

# Cognitive State
cognitive_state = {"mode": "growth", "layers": 3, "confidence": 0.87, "active": True}

# Reasoning Levels
reasoning_levels = [
    {
        "level": 1,
        "name": "Brain Loader",
        "confidence": 0.95,
        "status": "active",
        "timestamp": datetime.now().isoformat(),
    },
    {
        "level": 2,
        "name": "Rule of 2",
        "confidence": 0.88,
        "status": "active",
        "timestamp": datetime.now().isoformat(),
    },
    {
        "level": 3,
        "name": "Rule of 4",
        "confidence": 0.82,
        "status": "processing",
        "timestamp": datetime.now().isoformat(),
    },
]

# MCP Servers
mcp_servers = [
    {
        "id": "1",
        "name": "GitHub",
        "type": "git",
        "status": "connected",
        "url": "https://api.github.com",
        "last_ping": datetime.now().isoformat(),
    },
    {
        "id": "2",
        "name": "Slack",
        "type": "messaging",
        "status": "connected",
        "url": "https://slack.com/api",
        "last_ping": datetime.now().isoformat(),
    },
    {
        "id": "3",
        "name": "PostgreSQL",
        "type": "database",
        "status": "connected",
        "url": "postgresql://localhost:5432",
        "last_ping": datetime.now().isoformat(),
    },
    {
        "id": "4",
        "name": "Filesystem",
        "type": "storage",
        "status": "connected",
        "url": "file://local",
        "last_ping": datetime.now().isoformat(),
    },
]

# Background Agents
agents = [
    {
        "id": "agent-1",
        "name": "Code Analyzer",
        "description": "Analyzing codebase structure",
        "status": "running",
        "priority": 1,
        "progress": 65.0,
        "created_at": datetime.now().isoformat(),
    },
    {
        "id": "agent-2",
        "name": "Test Runner",
        "description": "Running unit tests",
        "status": "pending",
        "priority": 2,
        "progress": 0.0,
        "created_at": datetime.now().isoformat(),
    },
    {
        "id": "agent-3",
        "name": "Doc Generator",
        "description": "Generating documentation",
        "status": "complete",
        "priority": 3,
        "progress": 100.0,
        "created_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
    },
]

# Persistent Memory
memories = [
    {
        "id": "mem-1",
        "type": "episodic",
        "content": "Implemented AMOSL compiler with 8 invariants",
        "importance": 9,
        "tags": ["compiler", "amosl", "milestone"],
        "timestamp": datetime.now().isoformat(),
        "access_count": 42,
    },
    {
        "id": "mem-2",
        "type": "semantic",
        "content": "Architecture pattern: Layered cognitive system",
        "importance": 8,
        "tags": ["architecture", "pattern"],
        "timestamp": datetime.now().isoformat(),
        "access_count": 28,
    },
    {
        "id": "mem-3",
        "type": "procedural",
        "content": "How to validate cognitive invariants",
        "importance": 7,
        "tags": ["validation", "invariants"],
        "timestamp": datetime.now().isoformat(),
        "access_count": 15,
    },
]

# Checkpoints
checkpoints = [
    {
        "id": "cp-1",
        "name": "Initial Setup",
        "timestamp": datetime.now().isoformat(),
        "files_changed": 12,
        "lines_added": 450,
        "lines_removed": 0,
        "description": "Project initialization",
        "branch": "main",
    },
    {
        "id": "cp-2",
        "name": "AMOSL Complete",
        "timestamp": datetime.now().isoformat(),
        "files_changed": 8,
        "lines_added": 1200,
        "lines_removed": 45,
        "description": "Compiler implementation",
        "branch": "main",
    },
    {
        "id": "cp-3",
        "name": "Dashboard Built",
        "timestamp": datetime.now().isoformat(),
        "files_changed": 15,
        "lines_added": 2100,
        "lines_removed": 120,
        "description": "Frontend implementation",
        "branch": "main",
    },
]

# Agent Orchestra
orchestra_agents = [
    {
        "id": "orch-1",
        "name": "Frontend Virtuoso",
        "tier": 1,
        "instrument": "strings",
        "status": "performing",
        "task": "Implement React component",
        "progress": 65.0,
        "color": "#f59e0b",
    },
    {
        "id": "orch-2",
        "name": "Backend Bassist",
        "tier": 1,
        "instrument": "winds",
        "status": "performing",
        "task": "Build API endpoint",
        "progress": 80.0,
        "color": "#3b82f6",
    },
    {
        "id": "orch-3",
        "name": "Test Percussionist",
        "tier": 2,
        "instrument": "percussion",
        "status": "waiting",
        "task": "Write unit tests",
        "progress": 0.0,
        "color": "#ef4444",
    },
]

# AGENTS.md Files
agents_files = [
    {
        "id": "global",
        "path": "~/.config/AMOS/AGENTS.md",
        "scope": "global",
        "sections": {"overview": "Global preferences", "tech_stack": "Python, TypeScript"},
        "last_modified": datetime.now().isoformat(),
    },
    {
        "id": "project",
        "path": "./AGENTS.md",
        "scope": "project",
        "sections": {
            "overview": "AMOS Dashboard Project",
            "architecture": "14-layer cognitive system",
        },
        "last_modified": datetime.now().isoformat(),
    },
]


# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()

# ============================================================================
# API ENDPOINTS
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "AMOS API",
        "version": "3.0.0",
        "description": "Absolute Meta Operating System - Cognitive Backend",
        "creator": "Trang Phan",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "components": {
            "cognitive": "active",
            "memory": "active",
            "agents": "active",
            "mcp": "active",
        },
    }


# ============================================================================
# PRODUCTION HEALTH CHECKS (Kubernetes/Docker)
# ============================================================================

try:
    from backend.health import health_checker

    HEALTH_CHECKER_AVAILABLE = True
except ImportError:
    HEALTH_CHECKER_AVAILABLE = False


@app.get("/health/live")
async def liveness_probe():
    """
    Liveness probe for Kubernetes/Docker.
    Returns 200 if the application is running.
    Used to determine if container should be restarted.
    """
    if HEALTH_CHECKER_AVAILABLE:
        return health_checker.liveness()
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/health/ready")
async def readiness_probe():
    """
    Readiness probe for Kubernetes/Docker.
    Returns 200 if the application is ready to accept traffic.
    Checks all dependencies (database, external services, etc.)
    """
    if HEALTH_CHECKER_AVAILABLE:
        return await health_checker.readiness()
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============================================================================
# COGNITIVE MODE ENDPOINTS
# ============================================================================


@app.get("/api/cognitive/mode", response_model=CognitiveMode)
async def get_cognitive_mode():
    """Get current cognitive mode"""
    return CognitiveMode(**cognitive_state)


@app.post("/api/cognitive/mode")
async def set_cognitive_mode(mode: str):
    """Set cognitive mode (seed, growth, full)"""
    global cognitive_state
    if mode not in ["seed", "growth", "full"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Use: seed, growth, full")

    layers = {"seed": 1, "growth": 3, "full": 14}
    cognitive_state = {
        "mode": mode,
        "layers": layers[mode],
        "confidence": 0.87 if mode == "growth" else (0.91 if mode == "seed" else 0.94),
        "active": True,
    }

    # Broadcast update to all connected clients
    await manager.broadcast({"type": "cognitive_mode_changed", "data": cognitive_state})

    return cognitive_state


# ============================================================================
# REASONING ENDPOINTS
# ============================================================================


@app.get("/api/reasoning/levels", response_model=list[ReasoningLevel])
async def get_reasoning_levels():
    """Get all reasoning levels (L1-L3)"""
    return [ReasoningLevel(**level) for level in reasoning_levels]


@app.get("/api/reasoning/level/{level_id}")
async def get_reasoning_level(level_id: int):
    """Get specific reasoning level"""
    level = next((l for l in reasoning_levels if l["level"] == level_id), None)
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    return ReasoningLevel(**level)


# ============================================================================
# MCP ENDPOINTS
# ============================================================================


@app.get("/api/mcp/servers", response_model=list[MCPServer])
async def get_mcp_servers():
    """Get all MCP servers"""
    return [MCPServer(**server) for server in mcp_servers]


@app.post("/api/mcp/servers/{server_id}/connect")
async def connect_mcp_server(server_id: str):
    """Connect to an MCP server"""
    server = next((s for s in mcp_servers if s["id"] == server_id), None)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    server["status"] = "connected"
    server["last_ping"] = datetime.now().isoformat()

    await manager.broadcast({"type": "mcp_server_connected", "data": server})

    return MCPServer(**server)


@app.post("/api/mcp/servers/{server_id}/disconnect")
async def disconnect_mcp_server(server_id: str):
    """Disconnect from an MCP server"""
    server = next((s for s in mcp_servers if s["id"] == server_id), None)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    server["status"] = "disconnected"

    await manager.broadcast({"type": "mcp_server_disconnected", "data": server})

    return MCPServer(**server)


# ============================================================================
# BACKGROUND AGENTS ENDPOINTS
# ============================================================================


@app.get("/api/agents/tasks", response_model=list[AgentTask])
async def get_agent_tasks():
    """Get all agent tasks"""
    return [AgentTask(**task) for task in agents]


@app.post("/api/agents/tasks")
async def create_agent_task(task: Dict[str, Any]):
    """Create a new agent task"""
    new_task = {
        "id": f"agent-{len(agents) + 1}",
        "name": task.get("name", "New Task"),
        "description": task.get("description", ""),
        "status": "pending",
        "priority": task.get("priority", 1),
        "progress": 0.0,
        "created_at": datetime.now().isoformat(),
    }
    agents.append(new_task)

    await manager.broadcast({"type": "agent_task_created", "data": new_task})

    return AgentTask(**new_task)


@app.post("/api/agents/tasks/{task_id}/cancel")
async def cancel_agent_task(task_id: str):
    """Cancel an agent task"""
    task = next((t for t in agents if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task["status"] = "cancelled"

    await manager.broadcast({"type": "agent_task_cancelled", "data": task})

    return AgentTask(**task)


# ============================================================================
# PERSISTENT MEMORY ENDPOINTS
# ============================================================================


@app.get("/api/memory/entries", response_model=list[MemoryEntry])
async def get_memory_entries(type: str = None):
    """Get memory entries (optionally filtered by type)"""
    filtered = memories
    if type:
        filtered = [m for m in memories if m["type"] == type]
    return [MemoryEntry(**entry) for entry in filtered]


@app.post("/api/memory/entries")
async def create_memory_entry(entry: Dict[str, Any]):
    """Create a new memory entry"""
    new_entry = {
        "id": f"mem-{len(memories) + 1}",
        "type": entry.get("type", "semantic"),
        "content": entry.get("content", ""),
        "importance": entry.get("importance", 5),
        "tags": entry.get("tags", []),
        "timestamp": datetime.now().isoformat(),
        "access_count": 0,
    }
    memories.append(new_entry)

    await manager.broadcast({"type": "memory_entry_created", "data": new_entry})

    return MemoryEntry(**new_entry)


@app.get("/api/memory/search")
async def search_memory(query: str):
    """Search memory entries"""
    results = [m for m in memories if query.lower() in m["content"].lower()]
    return {"query": query, "results": [MemoryEntry(**r) for r in results], "count": len(results)}


# ============================================================================
# CHECKPOINTS ENDPOINTS
# ============================================================================


@app.get("/api/checkpoints", response_model=list[Checkpoint])
async def get_checkpoints():
    """Get all checkpoints"""
    return [Checkpoint(**cp) for cp in checkpoints]


@app.post("/api/checkpoints")
async def create_checkpoint(checkpoint: Dict[str, Any]):
    """Create a new checkpoint"""
    new_checkpoint = {
        "id": f"cp-{len(checkpoints) + 1}",
        "name": checkpoint.get("name", f"Checkpoint {len(checkpoints) + 1}"),
        "timestamp": datetime.now().isoformat(),
        "files_changed": checkpoint.get("files_changed", 0),
        "lines_added": checkpoint.get("lines_added", 0),
        "lines_removed": checkpoint.get("lines_removed", 0),
        "description": checkpoint.get("description", ""),
        "branch": checkpoint.get("branch", "main"),
    }
    checkpoints.append(new_checkpoint)

    await manager.broadcast({"type": "checkpoint_created", "data": new_checkpoint})

    return Checkpoint(**new_checkpoint)


@app.post("/api/checkpoints/{checkpoint_id}/rewind")
async def rewind_to_checkpoint(checkpoint_id: str):
    """Rewind to a specific checkpoint"""
    checkpoint = next((c for c in checkpoints if c["id"] == checkpoint_id), None)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    await manager.broadcast({"type": "checkpoint_rewind", "data": checkpoint})

    return {
        "message": f"Rewound to checkpoint {checkpoint_id}",
        "checkpoint": Checkpoint(**checkpoint),
    }


# ============================================================================
# AGENT ORCHESTRA ENDPOINTS
# ============================================================================


@app.get("/api/orchestra/agents", response_model=list[OrchestraAgent])
async def get_orchestra_agents():
    """Get all orchestra agents"""
    return [OrchestraAgent(**agent) for agent in orchestra_agents]


@app.get("/api/orchestra/status")
async def get_orchestra_status():
    """Get orchestra performance status"""
    performing = len([a for a in orchestra_agents if a["status"] == "performing"])
    complete = len([a for a in orchestra_agents if a["status"] == "complete"])

    return {
        "performing": performing,
        "complete": complete,
        "waiting": len(orchestra_agents) - performing - complete,
        "message": f"{performing} agents performing in harmony",
    }


# ============================================================================
# AGENTS.MD ENDPOINTS
# ============================================================================


@app.get("/api/agents-md/files", response_model=list[AGENTSFile])
async def get_agents_md_files():
    """Get all AGENTS.md files"""
    return [AGENTSFile(**file) for file in agents_files]


@app.get("/api/agents-md/files/{file_id}")
async def get_agents_md_file(file_id: str):
    """Get specific AGENTS.md file"""
    file = next((f for f in agents_files if f["id"] == file_id), None)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return AGENTSFile(**file)


@app.put("/api/agents-md/files/{file_id}")
async def update_agents_md_file(file_id: str, sections: Dict[str, str]):
    """Update AGENTS.md file sections"""
    file = next((f for f in agents_files if f["id"] == file_id), None)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    file["sections"].update(sections)
    file["last_modified"] = datetime.now().isoformat()

    await manager.broadcast({"type": "agents_md_updated", "data": file})

    return AGENTSFile(**file)


# ============================================================================
# SYSTEM STATUS ENDPOINTS
# ============================================================================


@app.get("/api/system/status", response_model=SystemStatus)
async def get_system_status():
    """Get overall system status"""
    return SystemStatus(
        status="operational",
        uptime="running",
        confidence=cognitive_state["confidence"],
        active_layers=cognitive_state["layers"],
        total_layers=14,
        components={
            "mcp": "active",
            "agents": "active",
            "memory": "active",
            "checkpoints": "ready",
        },
    )


@app.get("/api/system/metrics")
async def get_system_metrics():
    """Get system metrics"""
    return {
        "components": {
            "mcp_servers": len(mcp_servers),
            "agent_tasks": len(agents),
            "memory_entries": len(memories),
            "checkpoints": len(checkpoints),
            "orchestra_agents": len(orchestra_agents),
        },
        "performance": {
            "confidence": cognitive_state["confidence"],
            "active_layers": cognitive_state["layers"],
            "mode": cognitive_state["mode"],
        },
    }


# ============================================================================
# AXIOM ONE EXECUTION SLOT ENDPOINTS
# ============================================================================

# Import AXIOM One
_amos_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(_amos_root))

try:
    from axiom_one import (
        BackendIntegratedOrchestrator,
        BackendIntegrationConfig,
        SlotMode,
    )

    _AXIOM_ONE_CORE_AVAILABLE = True
    _axiom_orchestrator: Optional[BackendIntegratedOrchestrator] = None
except ImportError:
    _AXIOM_ONE_CORE_AVAILABLE = False
    _axiom_orchestrator = None


def get_axiom_orchestrator() -> Optional[BackendIntegratedOrchestrator]:
    """Get or create AXIOM One orchestrator."""
    global _axiom_orchestrator
    if _axiom_orchestrator is None and _AXIOM_ONE_CORE_AVAILABLE:
        _axiom_orchestrator = BackendIntegratedOrchestrator(
            BackendIntegrationConfig(repo_path=Path.cwd())
        )
    return _axiom_orchestrator


@app.post("/api/v1/slots")
async def create_execution_slot(objective: str, mode: str = "local"):
    """Create and execute an AXIOM One Execution Slot."""
    if not _AXIOM_ONE_CORE_AVAILABLE:
        raise HTTPException(status_code=503, detail="AXIOM One not available")

    orchestrator = get_axiom_orchestrator()
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    mode_map = {
        "local": SlotMode.LOCAL,
        "managed": SlotMode.MANAGED,
        "orch": SlotMode.ORCHESTRATION,
        "orchestration": SlotMode.ORCHESTRATION,
    }

    slot_mode = mode_map.get(mode.lower(), SlotMode.LOCAL)
    slot = await orchestrator.execute_slot(objective=objective, mode=slot_mode)

    return {
        "slot_id": slot.slot_id,
        "status": slot.status.value,
        "mode": slot.mode.value,
        "objective": slot.objective,
        "created_at": slot.created_at,
        "events": len(slot.event_log),
        "verification_bundle": slot.verification_bundle,
    }


@app.get("/api/v1/slots")
async def list_execution_slots():
    """List all active Execution Slots."""
    if not _AXIOM_ONE_CORE_AVAILABLE:
        return {"available": False, "slots": []}

    orchestrator = get_axiom_orchestrator()
    if not orchestrator:
        return {"available": False, "slots": []}

    slots = orchestrator.list_active_slots()
    return {
        "available": True,
        "count": len(slots),
        "slots": [
            {
                "slot_id": s.slot_id,
                "status": s.status.value,
                "mode": s.mode.value,
                "events": len(s.event_log),
            }
            for s in slots
        ],
    }


@app.get("/api/v1/slots/{slot_id}")
async def get_execution_slot(slot_id: str):
    """Get Execution Slot details."""
    if not _AXIOM_ONE_CORE_AVAILABLE:
        raise HTTPException(status_code=503, detail="AXIOM One not available")

    orchestrator = get_axiom_orchestrator()
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    slot = orchestrator.get_slot(slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")

    return {
        "slot_id": slot.slot_id,
        "status": slot.status.value,
        "mode": slot.mode.value,
        "objective": slot.objective,
        "created_at": slot.created_at,
        "completion_time": slot.completion_time,
        "events": [
            {"timestamp": e.timestamp, "type": e.event_type, "data": e.data} for e in slot.event_log
        ],
        "artifacts": slot.artifacts,
        "verification_bundle": slot.verification_bundle,
        "failure_reason": slot.failure_reason,
    }


@app.post("/api/v1/slots/{slot_id}/rollback")
async def rollback_execution_slot(slot_id: str):
    """Roll back an Execution Slot's changes."""
    if not _AXIOM_ONE_CORE_AVAILABLE:
        raise HTTPException(status_code=503, detail="AXIOM One not available")

    orchestrator = get_axiom_orchestrator()
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    success = orchestrator.slot_manager.rollback(slot_id)
    if not success:
        raise HTTPException(status_code=400, detail="Rollback failed or not possible")

    return {"success": True, "slot_id": slot_id, "message": "Slot rolled back"}


@app.get("/api/v1/slots/status")
async def get_axiom_status():
    """Get AXIOM One backend status."""
    if not _AXIOM_ONE_CORE_AVAILABLE:
        return {
            "available": False,
            "backend_connected": False,
            "orchestrator_ready": False,
        }

    orchestrator = get_axiom_orchestrator()
    if not orchestrator:
        return {
            "available": True,
            "backend_connected": False,
            "orchestrator_ready": False,
        }

    status = orchestrator.get_backend_status()
    status["available"] = True
    return status


# ============================================================================
# WEBSOCKET ENDPOINT (Real-time Updates)
# ============================================================================


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await manager.connect(websocket)

    try:
        # Send initial data
        await websocket.send_json(
            {
                "type": "connected",
                "data": {
                    "cognitive_mode": cognitive_state,
                    "system_status": "operational",
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

        # Keep connection alive and handle messages
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)

                # Handle different message types
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

                elif data.get("type") == "subscribe":
                    channel = data.get("channel", "all")
                    await websocket.send_json({"type": "subscribed", "channel": channel})

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)
        print(f"WebSocket error: {e}")


# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
