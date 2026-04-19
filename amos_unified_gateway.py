#!/usr/bin/env python3
"""AMOS Unified Gateway - Real Integration Using Brain Facade
===========================================================

Production API gateway using actual AMOS brain systems:
- BrainClient facade for cognitive operations
- AMOSAgent for autonomous task execution
- HybridOrchestrator for neural-symbolic reasoning
- CognitiveControlKernel for routing decisions

NO MOCK CODE - All integrations use real brain classes.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add project root to path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# Real brain imports - fail fast if not available
try:
    from amos_brain.facade import BrainClient, BrainResponse
    from amos_agentic_ai import AMOSAgent, AgentType, create_agent
    from amos_hybrid_orchestrator import HybridNeuralSymbolicOrchestrator, Paradigm
    from amos_cognitive_control_kernel import AMOSCognitiveControlKernel as CognitiveControlKernel, RuntimeMode
    BRAIN_AVAILABLE = True
except ImportError as e:
    BRAIN_AVAILABLE = False
    raise RuntimeError(f"AMOS Brain systems required but not available: {e}")

# FastAPI - required for API layer
try:
    from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from pydantic import BaseModel, Field
except ImportError as e:
    raise RuntimeError(f"FastAPI required but not available: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AMOS-Gateway")


# =============================================================================
# REAL DATA MODELS
# =============================================================================

class ChatRequest(BaseModel):
    """Real chat request model."""
    message: str = Field(..., min_length=1, max_length=10000)
    workspace_id: str = Field(..., min_length=1)
    context: list[dict] = Field(default_factory=list)
    model: str | None = None
    temperature: float = Field(default=0.7, ge=0, le=2)


class ChatResponse(BaseModel):
    """Real chat response with brain metadata."""
    id: str
    message: str
    model: str
    confidence: str
    law_compliant: bool
    violations: list[str]
    reasoning: list[str]
    domain: str
    processing_time_ms: float
    timestamp: str


class AgentRunRequest(BaseModel):
    """Real agent execution request."""
    agent_type: str = Field(..., pattern="^(code_review|repo_scan|fix_generator|security_audit|performance_check|architect|custom)$")
    target_repo: str | None = None
    task_description: str = Field(..., min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    paradigm: str = Field(default="HYBRID", pattern="^(NEURAL|SYMBOLIC|HYBRID)$")


class AgentRunResponse(BaseModel):
    """Real agent run response."""
    task_id: str
    agent_id: str
    status: str
    agent_type: str
    paradigm: str
    estimated_duration_seconds: int
    queue_position: int
    timestamp: str


class AgentStatusResponse(BaseModel):
    """Real agent status with execution results."""
    task_id: str
    agent_id: str
    status: str  # idle, planning, executing, replanning, completed, failed
    agent_type: str
    paradigm: str
    progress: int  # 0-100
    current_step: str | None = None
    total_steps: int = 0
    completed_steps: int = 0
    logs: list[str] = Field(default_factory=list)
    result: dict[str, Any] | None = None
    error: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    duration_seconds: float | None = None


class RepoScanRequest(BaseModel):
    """Real repository scan request."""
    repo_url: str = Field(..., min_length=1)
    branch: str = "main"
    scan_types: list[str] = Field(default_factory=lambda: ["security", "style", "architecture"])
    depth: str = Field(default="standard", pattern="^(quick|standard|deep)$")


# =============================================================================
# REAL BRAIN INTEGRATION CLASSES
# =============================================================================

@dataclass
class GatewayState:
    """Gateway state with real brain instances."""
    brain_client: BrainClient | None = None
    orchestrator: HybridNeuralSymbolicOrchestrator | None = None
    control_kernel: CognitiveControlKernel | None = None
    active_agents: dict[str, AMOSAgent] = field(default_factory=dict)
    task_store: dict[str, dict] = field(default_factory=dict)
    initialized: bool = False


class BrainIntegration:
    """Real integration with AMOS brain systems."""
    
    def __init__(self):
        self._state = GatewayState()
    
    async def initialize(self) -> dict[str, bool]:
        """Initialize all brain subsystems."""
        logger.info("Initializing AMOS brain integration...")
        
        # Initialize brain client (real facade)
        self._state.brain_client = BrainClient(repo_path=str(ROOT))
        
        # Initialize hybrid orchestrator (neural-symbolic)
        self._state.orchestrator = HybridNeuralSymbolicOrchestrator(max_workers=4)
        
        # Initialize cognitive control kernel (routing)
        self._state.control_kernel = CognitiveControlKernel()
        
        self._state.initialized = True
        
        status = {
            "brain_client": self._state.brain_client is not None,
            "orchestrator": self._state.orchestrator is not None,
            "control_kernel": self._state.control_kernel is not None,
        }
        
        logger.info(f"Brain integration initialized: {status}")
        return status
    
    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """Process chat using real brain facade."""
        if not self._state.initialized:
            raise RuntimeError("Brain integration not initialized")
        
        start_time = asyncio.get_event_loop().time()
        
        # Use real BrainClient.think() method
        brain_result: BrainResponse = self._state.brain_client.think(
            question=request.message,
            context=request.context,
        )
        
        processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        return ChatResponse(
            id=str(uuid.uuid4()),
            message=brain_result.content,
            model=request.model or "amos-brain",
            confidence=brain_result.confidence,
            law_compliant=brain_result.law_compliant,
            violations=brain_result.violations,
            reasoning=brain_result.reasoning,
            domain=brain_result.domain,
            processing_time_ms=processing_time,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    
    async def run_agent(self, request: AgentRunRequest) -> AgentRunResponse:
        """Execute agent using real AMOSAgent class."""
        if not self._state.initialized:
            raise RuntimeError("Brain integration not initialized")
        
        task_id = str(uuid.uuid4())
        
        # Create real agent using factory function
        agent = await create_agent(
            name=f"{request.agent_type}_{task_id[:8]}",
            agent_type=AgentType.TASK,
            tools=["file_system", "code_analyzer", "repo_scanner"],
        )
        
        # Store agent reference
        self._state.active_agents[task_id] = agent
        
        # Store task info
        self._state.task_store[task_id] = {
            "task_id": task_id,
            "agent_id": agent.get_status()["name"],
            "agent_type": request.agent_type,
            "paradigm": request.paradigm,
            "status": "starting",
            "request": request.model_dump(),
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Start execution in background
        asyncio.create_task(self._execute_agent_task(task_id, agent, request))
        
        return AgentRunResponse(
            task_id=task_id,
            agent_id=agent.get_status()["name"],
            status="starting",
            agent_type=request.agent_type,
            paradigm=request.paradigm,
            estimated_duration_seconds=300,
            queue_position=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    
    async def _execute_agent_task(
        self,
        task_id: str,
        agent: AMOSAgent,
        request: AgentRunRequest
    ) -> None:
        """Execute agent task using real AMOSAgent.execute()."""
        try:
            # Update status
            self._state.task_store[task_id]["status"] = "running"
            
            # Execute using real agent
            result = await agent.execute(
                goal=request.task_description,
                max_steps=20 if request.depth == "deep" else 10,
            )
            
            # Store results
            self._state.task_store[task_id].update({
                "status": "completed" if result.success else "failed",
                "result": {
                    "success": result.success,
                    "actions_taken": len(result.actions_taken),
                    "resources_used": result.resources_used,
                    "final_output": result.final_output,
                },
                "logs": result.logs,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": result.execution_time_seconds,
            })
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            self._state.task_store[task_id].update({
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now(timezone.utc).isoformat(),
            })
    
    def get_agent_status(self, task_id: str) -> AgentStatusResponse | None:
        """Get real agent status."""
        task = self._state.task_store.get(task_id)
        if not task:
            return None
        
        agent = self._state.active_agents.get(task_id)
        agent_status = agent.get_status() if agent else {}
        
        return AgentStatusResponse(
            task_id=task_id,
            agent_id=task.get("agent_id", ""),
            status=task.get("status", "unknown"),
            agent_type=task.get("agent_type", ""),
            paradigm=task.get("paradigm", "HYBRID"),
            progress=agent_status.get("progress", 0),
            current_step=agent_status.get("current_action"),
            total_steps=agent_status.get("total_steps", 0),
            completed_steps=agent_status.get("completed_steps", 0),
            logs=task.get("logs", []),
            result=task.get("result"),
            error=task.get("error"),
            started_at=task.get("started_at"),
            completed_at=task.get("completed_at"),
            duration_seconds=task.get("duration_seconds"),
        )
    
    async def spawn_hybrid_agent(
        self,
        role: str,
        paradigm: Paradigm,
        task: str
    ) -> dict[str, Any]:
        """Spawn real hybrid agent using orchestrator."""
        if not self._state.orchestrator:
            raise RuntimeError("Orchestrator not initialized")
        
        # Spawn real agent through orchestrator
        agent = self._state.orchestrator.spawn_agent(
            role=role,
            paradigm=paradigm,
        )
        
        # Execute task
        result = agent.execute(task)
        
        return {
            "agent_id": agent.agent_id,
            "result": {
                "success": result.success,
                "output": result.output,
                "paradigm": result.paradigm.value,
                "confidence": result.confidence,
                "law_compliance": result.law_compliance,
            }
        }


# =============================================================================
# FASTAPI APPLICATION WITH REAL BRAIN INTEGRATION
# =============================================================================

# Global brain integration instance
brain_integration = BrainIntegration()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan with real brain initialization."""
    # Startup
    logger.info("Starting AMOS Unified Gateway with real brain integration...")
    
    if not BRAIN_AVAILABLE:
        logger.error("AMOS Brain systems not available - cannot start")
        raise RuntimeError("Brain systems required")
    
    status = await brain_integration.initialize()
    logger.info(f"Brain systems initialized: {status}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AMOS Unified Gateway...")


# Create FastAPI app with real lifespan
app = FastAPI(
    title="AMOS Unified Gateway",
    description="Real AMOS brain integration via API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend repos
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://claws.amos.io",
        "https://app.amos.io",
        "https://invest.amos.io",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# REAL API ENDPOINTS
# =============================================================================

@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check with real brain status."""
    return {
        "status": "healthy" if BRAIN_AVAILABLE else "unhealthy",
        "brain_available": BRAIN_AVAILABLE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Real chat endpoint using BrainClient facade."""
    try:
        return await brain_integration.process_chat(request)
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Brain processing error: {str(e)}"
        )


@app.post("/v1/agent/run", response_model=AgentRunResponse, status_code=202)
async def run_agent(request: AgentRunRequest) -> AgentRunResponse:
    """Real agent execution using AMOSAgent."""
    try:
        return await brain_integration.run_agent(request)
    except Exception as e:
        logger.error(f"Agent spawn failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution error: {str(e)}"
        )


@app.get("/v1/agent/status/{task_id}", response_model=AgentStatusResponse)
async def get_agent_status(task_id: str) -> AgentStatusResponse:
    """Get real agent execution status."""
    status = brain_integration.get_agent_status(task_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return status


@app.post("/v1/hybrid/execute")
async def execute_hybrid(
    role: str,
    paradigm: str,
    task: str,
) -> dict[str, Any]:
    """Execute using hybrid neural-symbolic orchestrator."""
    try:
        paradigm_enum = Paradigm[paradigm.upper()]
        result = await brain_integration.spawn_hybrid_agent(
            role=role,
            paradigm=paradigm_enum,
            task=task,
        )
        return result
    except Exception as e:
        logger.error(f"Hybrid execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =============================================================================
# WEBSOCKET WITH REAL BRAIN EVENTS
# =============================================================================

class WebSocketManager:
    """Real WebSocket manager for brain events."""
    
    def __init__(self):
        self._connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self._connections[client_id] = websocket
        logger.info(f"WebSocket client connected: {client_id}")
    
    def disconnect(self, client_id: str):
        if client_id in self._connections:
            del self._connections[client_id]
            logger.info(f"WebSocket client disconnected: {client_id}")
    
    async def broadcast(self, message: dict):
        """Broadcast to all connected clients."""
        disconnected = []
        for client_id, ws in self._connections.items():
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(client_id)
        
        # Clean up disconnected
        for client_id in disconnected:
            self.disconnect(client_id)


ws_manager = WebSocketManager()


@app.websocket("/v1/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """Real WebSocket for brain events."""
    client_id = str(uuid.uuid4())
    await ws_manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            msg_type = data.get("type")
            
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif msg_type == "subscribe":
                channel = data.get("channel")
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": channel,
                })
    
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    if not BRAIN_AVAILABLE:
        logger.error("Cannot start - AMOS brain systems not available")
        sys.exit(1)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
