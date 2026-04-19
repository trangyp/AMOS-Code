#!/usr/bin/env python3
"""AMOS Production API Server v2.0
===============================

Production-ready FastAPI server exposing AMOS capabilities:
- Hybrid Neural-Symbolic Orchestration
- Tiered Memory System
- Global Laws L1-L6 Enforcement
- MCP Tool Integration
- Repo Doctor Omega Monitoring

Architecture:
- FastAPI for high-performance async API
- WebSocket for real-time agent communication
- Session persistence via memory system
- Automatic law validation middleware

Endpoints:
  POST /api/v1/agents/spawn     - Create specialized agent
  POST /api/v1/orchestrate      - Execute multi-agent task
  POST /api/v1/validate         - Validate action against laws
  GET  /api/v1/memory/{session} - Retrieve session memory
  WS   /ws/agent/{agent_id}     - Real-time agent stream
  GET  /health                  - Health check
  GET  /status                  - Full system status

Author: Trang Phan
Version: 2.0.0
"""


import json
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path
from typing import List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
except ImportError:
    print("Error: FastAPI not installed. Run: pip install fastapi uvicorn pydantic")
    sys.exit(1)

# Global instances
super_brain = None  # CANONICAL: SuperBrain Runtime (ONE BRAIN)
amos_unified = None  # Legacy: Will be absorbed into SuperBrain
memory_manager = None  # Legacy: Will be absorbed into SuperBrain
mcp_bridge = None  # Legacy: Will be absorbed into SuperBrain
repo_doctor = None  # Monitoring: External integration


class AgentSpawnRequest(BaseModel):
    """Request to spawn an agent."""
    role: str = Field(..., description="Agent role: architect, reviewer, auditor, executor")
    paradigm: str = Field(default="HYBRID", description="SYMBOLIC, NEURAL, or HYBRID")
    name: str  = Field(default=None, description="Optional custom name")


class OrchestrateRequest(BaseModel):
    """Request to orchestrate multi-agent task."""
    task: str = Field(..., description="Task description")
    agents: List[str]  = Field(default=None, description="List of agent roles")
    require_consensus: bool = Field(default=True, description="Require consensus")
    session_id: str  = Field(default=None, description="Session ID for memory")


class ValidateRequest(BaseModel):
    """Request to validate action against laws."""
    action: str = Field(..., description="Action description to validate")


class MemoryQueryRequest(BaseModel):
    """Request to query memory."""
    session_id: str = Field(..., description="Session ID")
    query: str  = Field(default=None, description="Optional search query")


class AgentMessage(BaseModel):
    """WebSocket message format."""
    type: str = Field(..., description="message, command, or status")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def initialize_components():
    """Initialize all AMOS components."""
    global super_brain, amos_unified, memory_manager, mcp_bridge, repo_doctor

    print("[AMOS] Initializing Production Server Components...")
    print("[AMOS] SUPER BRAIN CONSOLIDATION ACTIVE")
    print("=" * 70)

    # Initialize SuperBrain (CANONICAL - ONE BRAIN)
    try:
        from amos_brain import get_super_brain, initialize_super_brain
        super_brain = get_super_brain()
        if initialize_super_brain():
            print("  ✓ SuperBrain Runtime initialized (CANONICAL)")
            print(f"    Brain ID: {super_brain.brain_id}")
            print(f"    Status: {super_brain.status}")
        else:
            print("  ✗ SuperBrain Runtime initialization failed")
            super_brain = None
    except Exception as e:
        print(f"  ✗ SuperBrain Runtime: {e}")
        super_brain = None

    # Initialize Unified System (Legacy - will be absorbed)
    try:
        from amos_unified_system import AMOSUnifiedSystem
        amos_unified = AMOSUnifiedSystem()
        if amos_unified.initialize():
            print("  ✓ AMOS Unified System initialized")
        else:
            print("  ✗ AMOS Unified System initialization failed")
            amos_unified = None
    except Exception as e:
        print(f"  ✗ AMOS Unified System: {e}")
        amos_unified = None

    # Initialize Memory Manager
    try:
        from amos_memory_system import AMOSMemoryManager
        memory_manager = AMOSMemoryManager()
        print("  ✓ Memory System initialized")
    except Exception as e:
        print(f"  ✗ Memory System: {e}")
        memory_manager = None

    # Initialize MCP Bridge
    try:
        from amos_mcp_bridge import AMOSMCPBridge
        mcp_bridge = AMOSMCPBridge()
        print("  ✓ MCP Bridge initialized")
    except Exception as e:
        print(f"  ✗ MCP Bridge: {e}")
        mcp_bridge = None

    # Initialize Repo Doctor Omega
    try:
        from repo_doctor_omega.engine import RepoDoctorEngine
        repo_doctor = RepoDoctorEngine(".")
        print("  ✓ Repo Doctor Omega initialized")
    except Exception as e:
        print(f"  ✗ Repo Doctor Omega: {e}")
        repo_doctor = None

    # Summary
    active = sum([amos_unified is not None, memory_manager is not None,
                  mcp_bridge is not None, repo_doctor is not None])
    print(f"\n[AMOS] {active}/4 components active")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    print("\n" + "=" * 70)
    print("AMOS PRODUCTION SERVER v2.0.0")
    print("=" * 70)
    initialize_components()
    print("=" * 70)
    yield
    # Shutdown
    print("\n[AMOS] Shutting down gracefully...")


# Create FastAPI app with comprehensive OpenAPI documentation
app = FastAPI(
    title="AMOS Cognitive Operating System API",
    description="""
    **AMOS (Autonomous Multi-agent Operating System)** - Production API

    A hybrid neural-symbolic cognitive operating system with:
    - **Multi-Agent Orchestration**: Spawn specialized agents (architect, reviewer, auditor, executor)
    - **Global Laws L1-L6**: Safety constraints enforced on all operations
    - **Tiered Memory**: Working, Short-term, Episodic, Semantic, and Procedural memory
    - **MCP Tools**: Filesystem, Git, Web Search, Code Execution, Database
    - **Vector Memory**: Semantic search with ChromaDB and RAG
    - **Self-Evolution**: Autonomous code improvement with human oversight
    - **Authentication**: JWT-based auth with RBAC

    ## Architecture

    ```
    ┌─────────────────────────────────────────────────────────────┐
    │                     AMOS API Layer                          │
    ├─────────────────────────────────────────────────────────────┤
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
    │  │   Agents     │  │  Memory      │  │    Tools     │       │
    │  │  /agents/*   │  │  /memory/*   │  │  /tools/*    │       │
    │  └──────────────┘  └──────────────┘  └──────────────┘       │
    ├─────────────────────────────────────────────────────────────┤
    │                 AMOS Cognitive Engine                       │
    │         (Hybrid Neural-Symbolic Orchestrator)             │
    └─────────────────────────────────────────────────────────────┘
    ```

    ## Authentication

    Most endpoints require JWT authentication. Obtain a token via `/auth/login`.

    ## Rate Limiting

    API requests are rate-limited per IP address (100 requests/minute default).

    ## WebSocket

    Real-time agent communication available at `/ws/agent/{agent_id}`.

    ## Health Checks

    - `/health` - Comprehensive health status
    - `/ready` - Kubernetes readiness probe
    - `/live` - Kubernetes liveness probe
    - `/metrics` - Prometheus metrics
    """,
    version="2.3.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {"name": "System", "description": "System status and health checks"},
        {"name": "Agents", "description": "Agent management and spawning"},
        {"name": "Orchestration", "description": "Multi-agent task execution"},
        {"name": "Memory", "description": "Tiered memory system operations"},
        {"name": "Laws", "description": "Global Laws L1-L6 validation"},
        {"name": "Tools", "description": "MCP tool execution"},
        {"name": "Auth", "description": "Authentication and authorization"},
        {"name": "WebSocket", "description": "Real-time communication"},
    ],
    contact={
        "name": "Trang Phan",
        "email": "trang@amos.ai",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"], response_model=dict)
async def health_check():
    """
    Health check endpoint.

    Returns comprehensive health status of all AMOS components including:
    - AMOS Unified System
    - Memory System
    - MCP Bridge
    - Repo Doctor Omega

    Use this endpoint for monitoring and load balancer health checks.
    """
    # Get SuperBrain health if available
    superbrain_health = {}
    if super_brain is not None:
        try:
            state = super_brain.get_state()
            superbrain_health = {
                "brain_id": state.brain_id if hasattr(state, 'brain_id') else 'unknown',
                "status": state.status if hasattr(state, 'status') else 'unknown',
                "core_frozen": state.core_frozen if hasattr(state, 'core_frozen') else False,
                "health_score": state.health_score if hasattr(state, 'health_score') else 0.0
            }
        except Exception:
            superbrain_health = {"error": "failed to get SuperBrain state"}

    components = {
        "super_brain": super_brain is not None,
        "amos_unified": amos_unified is not None,
        "memory_system": memory_manager is not None,
        "mcp_bridge": mcp_bridge is not None,
        "repo_doctor": repo_doctor is not None,
    }

    # SuperBrain MUST be healthy for overall health
    healthy = super_brain is not None and all(components.values())

    return {
        "status": "healthy" if healthy else "degraded",
        "service": "amos-production-api",
        "version": "2.3.0",
        "super_brain": superbrain_health,
        "components": components,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/status", tags=["System"], response_model=dict)
async def system_status():
    """
    Get full system status.

    Returns comprehensive status information including:
    - Neural provider availability
    - Active agents count
    - Memory system status
    - Law compliance status
    - MCP tools availability
    - Repository health (via Repo Doctor)
    """
    if amos_unified is None:
        raise HTTPException(status_code=503, detail="AMOS Unified System not available")

    try:
        status = amos_unified.get_status()

        # Add Repo Doctor status if available
        if repo_doctor:
            try:
                state = repo_doctor.compute_state()
                status["repo_doctor"] = {
                    "energy": state.compute_energy(),
                    "releaseable": state.is_releaseable(),
                }
            except Exception as e:
                import logging
                logging.getLogger(__name__).debug(f"Repo Doctor status check failed: {e}")

        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/agents/spawn", tags=["Agents"], response_model=dict)
async def spawn_agent(request: AgentSpawnRequest):
    """
    Spawn a new specialized agent.

    Creates an agent with specified role and cognitive paradigm.
    Available roles: architect, reviewer, auditor, executor, synthesizer
    Available paradigms: SYMBOLIC, NEURAL, HYBRID

    The spawned agent can then be used in orchestration tasks.
    """
    if amos_unified is None:
        raise HTTPException(status_code=503, detail="AMOS Unified System not available")

    try:
        agent = amos_unified.spawn_agent(
            role=request.role,
            paradigm=request.paradigm,
            name=request.name
        )

        return {
            "success": True,
            "agent_id": agent.agent_id,
            "name": agent.name,
            "role": agent.role,
            "paradigm": agent.paradigm.name,
            "capabilities": {
                "strengths": agent.capabilities.strengths,
                "constraints": agent.capabilities.constraints,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/orchestrate", tags=["Orchestration"], response_model=dict)
async def orchestrate_task(request: OrchestrateRequest):
    """
    Execute multi-agent orchestration.

    Coordinates multiple specialized agents to complete a complex task.
    Agents collaborate, share perspectives, and reach consensus (if required).

    The orchestration process:
    1. Validates task against Global Laws L1-L6
    2. Spawns specified agents or uses defaults
    3. Executes parallel agent reasoning
    4. Collects and synthesizes agent outputs
    5. Validates final decision against laws
    6. Records outcome to memory (if session provided)

    Returns final decision, agent reasoning, and law compliance status.
    """
    if amos_unified is None:
        raise HTTPException(status_code=503, detail="AMOS Unified System not available")

    try:
        # CANONICAL: Route through SuperBrain orchestration adapter
        from amos_brain.orchestration_adapter import SuperBrainOrchestrationAdapter
        adapter = SuperBrainOrchestrationAdapter(super_brain)

        result = adapter.execute_orchestration(
            task=request.task,
            agents=request.agents,
            require_consensus=request.require_consensus,
            session_id=request.session_id
        )

        return {
            "success": result.success,
            "result": {
                "final_decision": result.final_decision,
                "agents_used": result.agents_used,
                "law_compliant": result.law_compliant,
                "consensus_score": result.consensus_score,
                "execution_time_ms": result.execution_time_ms,
                "metadata": result.metadata
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/validate", tags=["Laws"], response_model=dict)
async def validate_action(request: ValidateRequest):
    """
    Validate action against Global Laws L1-L6.

    Checks if an action complies with AMOS safety constraints:
    - L1: Law of Law (operational scope)
    - L2: Rule of 2 (dual perspective for critical decisions)
    - L3: Rule of 4 (quadrant analysis)
    - L4: Absolute Structural Integrity (repository protection)
    - L5: Post-Theory Communication (clear reasoning)
    - L6: UBI Alignment (human benefit)

    Returns compliance status and any violations detected.
    """
    if amos_unified is None:
        raise HTTPException(status_code=503, detail="AMOS Unified System not available")

    try:
        validation = amos_unified.validate_action(request.action)

        return {
            "success": True,
            "action": request.action,
            "compliant": validation["compliant"],
            "violations": validation["violations"],
            "laws_checked": ["L1", "L2", "L3", "L4", "L5", "L6"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/memory/{session_id}", tags=["Memory"], response_model=dict)
async def get_memory(session_id: str, query: str  = None):
    """
    Retrieve session memory.

    Returns memory summary for the specified session including:
    - Working memory (current context)
    - Short-term memory (recent interactions)
    - Episodic memory (past experiences)
    - Semantic memory (facts and concepts)
    - Procedural memory (skills and procedures)

    Optionally filter by query string for semantic search.
    """
    if memory_manager is None:
        raise HTTPException(status_code=503, detail="Memory system not available")

    try:
        summary = memory_manager.get_memory_summary()

        # Get recent interactions if available
        recent = []
        if hasattr(memory_manager, 'short_term'):
            recent_entries = memory_manager.short_term.get_recent(10)
            recent = [e.content for e in recent_entries]

        return {
            "success": True,
            "session_id": session_id,
            "summary": summary,
            "recent_interactions": recent,
            "query": query,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/superbrain/execute", tags=["SuperBrain"], response_model=dict)
async def superbrain_execute(request: OrchestrateRequest):
    """
    Direct SuperBrain execution endpoint.

    Executes a task through the canonical SuperBrain runtime.
    This is the RECOMMENDED endpoint for all task execution.

    The SuperBrain routes execution through:
    - ActionGate (tool authorization)
    - ModelRouter (model selection)
    - MemoryGovernance (memory recording)

    Returns execution result with full audit trail.
    """
    if super_brain is None:
        raise HTTPException(status_code=503, detail="SuperBrain not available")

    try:
        # Direct SuperBrain execution
        result = super_brain.execute_task(request.task)

        return {
            "success": result.get("success", False),
            "result": result.get("result", ""),
            "brain_id": super_brain.brain_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/agent/{agent_id}")
async def agent_websocket(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for real-time agent communication."""
    await websocket.accept()

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)

            # Process based on message type
            msg_type = message.get("type", "message")
            content = message.get("content", "")

            if msg_type == "command":
                # CANONICAL: Execute through SuperBrain
                if super_brain:
                    result = super_brain.execute_task(content)
                    response = {
                        "type": "result",
                        "content": result.get("result", "No result"),
                        "success": result.get("success", False),
                        "agent_id": agent_id,
                    }
                else:
                    response = {
                        "type": "error",
                        "content": "SuperBrain not available",
                        "agent_id": agent_id,
                    }
            else:
                # Echo with timestamp
                response = {
                    "type": "echo",
                    "content": content,
                    "agent_id": agent_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            await websocket.send_json(response)

    except WebSocketDisconnect:
        print(f"[WS] Agent {agent_id} disconnected")
    except Exception as e:
        print(f"[WS] Error with agent {agent_id}: {e}")


def main():
    """Run the production server."""
    import uvicorn

    print("\n" + "=" * 70)
    print("AMOS Production Server - SUPER BRAIN CONSOLIDATION")
    print("=" * 70)
    print("\nCanonical Endpoints:")
    print("  POST /api/v1/superbrain/execute - Direct SuperBrain (RECOMMENDED)")
    print("\nLegacy Endpoints:")
    print("  GET  /health                    - Health check")
    print("  GET  /status                    - System status")
    print("  POST /api/v1/agents/spawn       - Spawn agent")
    print("  POST /api/v1/orchestrate        - Orchestrate (via SuperBrain)")
    print("  POST /api/v1/validate           - Validate action")
    print("  GET  /api/v1/memory/{session}   - Get memory")
    print("  WS   /ws/agent/{agent_id}       - WebSocket stream")
    print("\n" + "=" * 70)

    uvicorn.run(
        "amos_production_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
