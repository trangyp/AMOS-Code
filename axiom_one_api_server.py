#!/usr/bin/env python3
"""Axiom One - Real API Server for Agent Fleet and System Graph.

Production-ready FastAPI server with:
- Agent fleet management endpoints
- Workflow execution
- System graph API
- Real-time WebSocket updates
- Integration with AMOS brain
"""

import json
import logging
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

# Setup paths
AMOS_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(AMOS_ROOT))
sys.path.insert(0, str(AMOS_ROOT / "clawspring" / "amos_brain"))

# FastAPI imports
from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import Axiom One modules
from axiom_one_agent_fleet import (
    AgentType,
    AxiomOneAgentFleet,
    Workflow,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────────────────────────────────────


class AgentInfo(BaseModel):
    """Agent information response."""

    agent_id: str
    name: str
    type: str
    description: str
    status: str
    capabilities: List[str]
    permissions: List[str]


class CreateWorkflowRequest(BaseModel):
    """Request to create a workflow."""

    name: str
    description: str
    require_approval: bool = False


class AssignTaskRequest(BaseModel):
    """Request to assign a task."""

    agent_type: str
    description: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    priority: str = "normal"
    dependencies: List[str] = Field(default_factory=list)


class WorkflowResponse(BaseModel):
    """Workflow response."""

    workflow_id: str
    name: str
    description: str
    status: str
    tasks: list[dict[str, Any]]
    created_at: str
    completed_at: str = None


class ExecuteResponse(BaseModel):
    """Execution response."""

    workflow_id: str
    status: str
    tasks_completed: int
    tasks_failed: int
    results: Dict[str, Any]


class SystemGraphNode(BaseModel):
    """System graph node."""

    node_id: str
    node_type: str
    name: str
    path: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Global State
# ─────────────────────────────────────────────────────────────────────────────

fleet: Optional[AxiomOneAgentFleet] = None
workflows: Dict[str, Workflow] = {}
connections: List[WebSocket] = []


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI Application
# ─────────────────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global fleet
    logger.info("Starting Axiom One API Server...")
    fleet = AxiomOneAgentFleet()
    logger.info("Agent fleet initialized")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Axiom One API",
    description="Unified Agent Fleet and System Graph API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Agent Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/agents", response_model=list[AgentInfo])
async def list_agents():
    """List all available agents in the fleet."""
    if not fleet:
        raise HTTPException(status_code=503, detail="Fleet not initialized")

    agents = fleet.list_agents()
    return [AgentInfo(**agent) for agent in agents]


@app.get("/agents/{agent_type}")
async def get_agent(agent_type: str):
    """Get specific agent details."""
    if not fleet:
        raise HTTPException(status_code=503, detail="Fleet not initialized")

    try:
        agent_type_enum = AgentType(agent_type)
        agent = fleet.get_agent(agent_type_enum)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "type": agent.agent_type.value,
            "description": agent.description,
            "status": agent.status.value,
            "capabilities": [cap.name for cap in agent.capabilities],
            "permissions": agent.permissions,
            "current_tasks": agent.current_tasks,
            "completed_tasks": agent.completed_tasks,
            "failed_tasks": agent.failed_tasks,
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid agent type: {agent_type}")


# ─────────────────────────────────────────────────────────────────────────────
# Workflow Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@app.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(request: CreateWorkflowRequest):
    """Create a new workflow."""
    if not fleet:
        raise HTTPException(status_code=503, detail="Fleet not initialized")

    workflow = fleet.create_workflow(
        name=request.name,
        description=request.description,
        require_approval=request.require_approval,
    )
    workflows[workflow.workflow_id] = workflow

    return WorkflowResponse(
        workflow_id=workflow.workflow_id,
        name=workflow.name,
        description=workflow.description,
        status=workflow.status.value,
        tasks=[],
        created_at=workflow.created_at,
    )


@app.get("/workflows", response_model=list[WorkflowResponse])
async def list_workflows():
    """List all workflows."""
    return [
        WorkflowResponse(
            workflow_id=w.workflow_id,
            name=w.name,
            description=w.description,
            status=w.status.value,
            tasks=[
                {
                    "task_id": t.task_id,
                    "description": t.description,
                    "agent_type": t.agent_type.value,
                    "status": t.status.value,
                    "quality_score": t.quality_score,
                }
                for t in w.tasks.values()
            ],
            created_at=w.created_at,
            completed_at=w.completed_at,
        )
        for w in workflows.values()
    ]


@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow details."""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    w = workflows[workflow_id]
    return {
        "workflow_id": w.workflow_id,
        "name": w.name,
        "description": w.description,
        "status": w.status.value,
        "current_step": w.current_step_idx,
        "tasks": [
            {
                "task_id": t.task_id,
                "description": t.description,
                "agent_type": t.agent_type.value,
                "status": t.status.value,
                "assigned_agent": t.assigned_agent,
                "quality_score": t.quality_score,
                "error": t.error,
                "started_at": t.started_at,
                "completed_at": t.completed_at,
            }
            for t in w.tasks.values()
        ],
        "created_at": w.created_at,
        "completed_at": w.completed_at,
        "results": w.results,
    }


@app.post("/workflows/{workflow_id}/tasks")
async def assign_task(workflow_id: str, request: AssignTaskRequest):
    """Assign a task to a workflow."""
    if not fleet:
        raise HTTPException(status_code=503, detail="Fleet not initialized")

    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow = workflows[workflow_id]

    try:
        agent_type = AgentType(request.agent_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid agent type: {request.agent_type}")

    task = fleet.assign_task(
        workflow=workflow,
        agent_type=agent_type,
        description=request.description,
        input_data=request.input_data,
        priority=request.priority,
    )

    # Broadcast update
    await broadcast(
        {
            "type": "task_assigned",
            "workflow_id": workflow_id,
            "task_id": task.task_id,
            "agent_type": request.agent_type,
        }
    )

    return {
        "task_id": task.task_id,
        "description": task.description,
        "agent_type": task.agent_type.value,
        "status": task.status.value,
        "created_at": task.created_at,
    }


@app.post("/workflows/{workflow_id}/execute", response_model=ExecuteResponse)
async def execute_workflow(workflow_id: str, background_tasks: BackgroundTasks):
    """Execute a workflow."""
    if not fleet:
        raise HTTPException(status_code=503, detail="Fleet not initialized")

    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow = workflows[workflow_id]

    # Execute in background
    background_tasks.add_task(_execute_workflow_async, workflow_id)

    return ExecuteResponse(
        workflow_id=workflow_id, status="started", tasks_completed=0, tasks_failed=0, results={}
    )


async def _execute_workflow_async(workflow_id: str):
    """Execute workflow asynchronously."""
    workflow = workflows[workflow_id]

    await broadcast(
        {
            "type": "workflow_started",
            "workflow_id": workflow_id,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )

    result = fleet.execute(workflow)

    await broadcast(
        {
            "type": "workflow_completed",
            "workflow_id": workflow_id,
            "status": result["status"],
            "tasks_completed": result["tasks_completed"],
            "tasks_failed": result["tasks_failed"],
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )


# ─────────────────────────────────────────────────────────────────────────────
# System Graph Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/graph/nodes")
async def list_graph_nodes(path: str = ".", node_type: str = None):
    """List system graph nodes."""
    try:
        from axiom_one_agent_fleet import tool_list_directory, tool_search_code

        # Get directory structure
        dir_result = tool_list_directory(path)

        nodes = []
        if dir_result.get("success"):
            for entry in dir_result.get("entries", []):
                if node_type is None or entry["type"] == node_type:
                    nodes.append(
                        SystemGraphNode(
                            node_id=str(uuid.uuid4()),
                            node_type=entry["type"],
                            name=entry["name"],
                            path=entry["path"],
                            metadata={"size": entry.get("size", 0)},
                        )
                    )

        # Get Python files if code type requested
        if node_type is None or node_type == "code":
            search_result = tool_search_code("class |def ", path, "*.py")
            if search_result.get("success"):
                for file_path in search_result.get("files", [])[:20]:
                    nodes.append(
                        SystemGraphNode(
                            node_id=str(uuid.uuid4()),
                            node_type="code",
                            name=Path(file_path).name,
                            path=file_path,
                            metadata={},
                        )
                    )

        return {"nodes": [n.model_dump() for n in nodes], "total": len(nodes), "path": path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph/impact")
async def analyze_impact(path: str):
    """Analyze impact of changing a file."""
    try:
        from axiom_one_agent_fleet import tool_read_file, tool_search_code

        # Read the target file
        file_result = tool_read_file(path)
        if not file_result.get("success"):
            raise HTTPException(status_code=404, detail=f"File not found: {path}")

        # Find imports/dependencies
        content = file_result.get("content", "")
        imports = [
            line.strip()
            for line in content.split("\n")
            if line.strip().startswith("import") or line.strip().startswith("from")
        ]

        # Find files that import this
        filename = Path(path).stem
        dependents = tool_search_code(f"from.*{filename}|import.*{filename}", ".", "*.py")

        return {
            "file": path,
            "imports": imports[:10],
            "dependents": dependents.get("files", [])[:10],
            "impact_score": len(dependents.get("files", [])),
            "risk_level": "high"
            if len(dependents.get("files", [])) > 5
            else "medium"
            if len(dependents.get("files", [])) > 0
            else "low",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# WebSocket
# ─────────────────────────────────────────────────────────────────────────────


async def broadcast(message: Dict[str, Any]):
    """Broadcast message to all connected WebSocket clients."""
    disconnected = []
    for conn in connections:
        try:
            await conn.send_json(message)
        except Exception:
            disconnected.append(conn)

    for conn in disconnected:
        connections.remove(conn)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    connections.append(websocket)

    try:
        await websocket.send_json(
            {"type": "connected", "message": "Connected to Axiom One real-time stream"}
        )

        while True:
            message = await websocket.receive_text()
            try:
                data = json.loads(message)

                if data.get("action") == "ping":
                    await websocket.send_json({"type": "pong"})

                elif data.get("action") == "get_agents":
                    if fleet:
                        await websocket.send_json(
                            {"type": "agents_list", "agents": fleet.list_agents()}
                        )

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketDisconnect:
        connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in connections:
            connections.remove(websocket)


# ─────────────────────────────────────────────────────────────────────────────
# Health and Info
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "fleet_initialized": fleet is not None,
        "workflows_count": len(workflows),
        "websocket_connections": len(connections),
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Axiom One API",
        "version": "1.0.0",
        "features": [
            "agent_fleet",
            "workflow_orchestration",
            "system_graph",
            "real_time_websocket",
        ],
        "endpoints": {
            "agents": "/agents",
            "workflows": "/workflows",
            "graph": "/graph/nodes",
            "websocket": "/ws",
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Axiom One API Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
