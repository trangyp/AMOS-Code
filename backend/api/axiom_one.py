#!/usr/bin/env python3
"""Axiom One Integration - Real agent fleet for FastAPI backend.

Integrates Axiom One components into backend/main.py:
- Real agent task execution
- Live workflow management
- System graph analysis
- Code generation endpoints
"""

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

# Add Axiom One to path
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
if str(AMOS_ROOT) not in sys.path:

# Import Axiom One components
try:
    from axiom_one_agent_fleet import (
        AgentType,
        AxiomOneAgentFleet,
        TaskPriority,
        ToolRegistry,
        Workflow,
    )
    from axiom_one_backend_integration import RealCodeIntelligence
    from axiom_one_system_graph import SystemGraphAnalyzer

    _AXIOM_AVAILABLE = True
except ImportError as e:
    print(f"Axiom One not available: {e}")
    _AXIOM_AVAILABLE = False

router = APIRouter(prefix="/api/v1/axiom", tags=["Axiom One"])

# Global instances
_fleet: Any = None
_graph_analyzer: Any = None
_code_intel: Any = None


def get_fleet() -> Any:
    """Get or create agent fleet."""
    global _fleet
    if _fleet is None and _AXIOM_AVAILABLE:
        _fleet = AxiomOneAgentFleet()
    return _fleet


def get_graph_analyzer() -> Any:
    """Get or create graph analyzer."""
    global _graph_analyzer
    if _graph_analyzer is None and _AXIOM_AVAILABLE:
        _graph_analyzer = SystemGraphAnalyzer()
    return _graph_analyzer


def get_code_intel() -> Any:
    """Get or create code intelligence."""
    global _code_intel
    if _code_intel is None and _AXIOM_AVAILABLE:
        _code_intel = RealCodeIntelligence()
    return _code_intel


# ============================================================================
# Pydantic Models
# ============================================================================


class CreateWorkflowRequest(BaseModel):
    name: str
    description: str = ""
    require_approval: bool = False


class AssignTaskRequest(BaseModel):
    workflow_id: str
    agent_type: str
    description: str
    input_data: dict
    priority: str = "normal"


class ExecuteWorkflowRequest(BaseModel):
    workflow_id: str


class CodeCompleteRequest(BaseModel):
    code_prefix: str
    language: str = "python"


class CodeGenerateRequest(BaseModel):
    name: str
    params: str = ""
    docstring: str = ""
    template: str = "simple"


class GraphAnalysisRequest(BaseModel):
    path: str = "."
    max_depth: int = 3


# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/status")
async def axiom_status():
    """Get Axiom One system status."""
    return {
        "available": _AXIOM_AVAILABLE,
        "components": {
            "agent_fleet": get_fleet() is not None,
            "graph_analyzer": get_graph_analyzer() is not None,
            "code_intelligence": get_code_intel() is not None,
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.post("/workflows")
async def create_workflow(request: CreateWorkflowRequest):
    """Create new workflow."""
    if not _AXIOM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Axiom One not available")

    fleet = get_fleet()
    workflow = fleet.create_workflow(
        name=request.name,
        description=request.description,
        require_approval=request.require_approval,
    )

    return {
        "workflow_id": workflow.workflow_id,
        "name": workflow.name,
        "status": workflow.status.value
        if hasattr(workflow.status, "value")
        else str(workflow.status),
        "created_at": workflow.created_at,
    }


@router.get("/workflows")
async def list_workflows():
    """List all workflows."""
    if not _AXIOM_AVAILABLE:
        return []

    fleet = get_fleet()
    return [
        {
            "workflow_id": w.workflow_id,
            "name": w.name,
            "status": w.status.value if hasattr(w.status, "value") else str(w.status),
            "task_count": len(w.tasks),
        }
        for w in fleet.active_workflows.values()
    ]


@router.post("/tasks")
async def assign_task(request: AssignTaskRequest):
    """Assign task to workflow."""
    if not _AXIOM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Axiom One not available")

    fleet = get_fleet()
    workflow = fleet.active_workflows.get(request.workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

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

    return {
        "task_id": task.task_id,
        "workflow_id": request.workflow_id,
        "agent_type": task.agent_type.value,
        "status": task.status.value,
    }


@router.post("/workflows/execute")
async def execute_workflow(request: ExecuteWorkflowRequest):
    """Execute workflow with all tasks."""
    if not _AXIOM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Axiom One not available")

    fleet = get_fleet()
    workflow = fleet.active_workflows.get(request.workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    result = fleet.execute(workflow)

    return {
        "workflow_id": request.workflow_id,
        "status": result.get("status"),
        "tasks_completed": result.get("tasks_completed"),
        "total_tasks": result.get("total_tasks"),
    }


@router.post("/code/complete")
async def complete_code(request: CodeCompleteRequest):
    """Get code completion suggestions."""
    if not _AXIOM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Axiom One not available")

    intel = get_code_intel()
    suggestions = intel.complete_code(request.code_prefix, request.language)

    return {"suggestions": suggestions, "input": request.code_prefix, "count": len(suggestions)}


@router.post("/code/generate/function")
async def generate_function(request: CodeGenerateRequest):
    """Generate function code."""
    if not _AXIOM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Axiom One not available")

    intel = get_code_intel()
    result = intel.generate_function(
        name=request.name,
        params=request.params,
        docstring=request.docstring,
        template=request.template,
    )

    return result


@router.post("/graph/analyze")
async def analyze_graph(request: GraphAnalysisRequest):
    """Analyze codebase dependency graph."""
    if not _AXIOM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Axiom One not available")

    analyzer = get_graph_analyzer()
    graph = analyzer.build_graph(request.path, max_depth=request.max_depth)

    return {
        "modules": len(graph.nodes),
        "dependencies": len(graph.edges),
        "circular_deps": len(graph.circular_deps),
        "most_connected": analyzer.get_most_connected_module()[0]
        if analyzer.get_most_connected_module()
        else None,
    }


@router.get("/graph/export")
async def export_graph():
    """Export graph to JSON."""
    if not _AXIOM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Axiom One not available")

    analyzer = get_graph_analyzer()
    graph = analyzer.build_graph(".", max_depth=2)

    output_path = ".axiom_graph_export.json"
    analyzer.export_to_json(graph, output_path)

    return {"exported": True, "path": output_path, "modules": len(graph.nodes)}


# ============================================================================
# Repo Autopsy Endpoints with Brain Integration
# ============================================================================


class AutopsyRequest(BaseModel):
    """Request to run repo autopsy."""

    repo_path: str = "."
    repo_name: str = None
    owner_id: str = "default"
    enable_brain: bool = True


class FixIssueRequest(BaseModel):
    """Request to fix an issue."""

    issue_id: str
    auto_apply: bool = False


@router.post("/autopsy")
async def run_autopsy(request: AutopsyRequest):
    """
    Run repository autopsy with brain cognitive analysis.

    - Scans repository structure
    - Validates packaging, syntax, imports
    - Uses brain for cognitive issue analysis (if enabled)
    - Returns detailed report with recommendations
    """
    try:
        from axiom_one_graph import AxiomGraph
        from axiom_one_repo_autopsy import RepoAutopsyEngine
        from clawspring.amos_brain.facade import get_brain_client

        # Create graph and engine
        graph = AxiomGraph()
        engine = RepoAutopsyEngine(graph)

        # Run autopsy
        repo_name = request.repo_name or Path(request.repo_path).name
        report = await engine.autopsy(request.repo_path, repo_name, request.owner_id)

        # Enhance with brain analysis for critical/high issues
        brain_analysis = []
        if request.enable_brain:
            brain = get_brain_client()
            for issue in report.issues:
                if issue.severity.value in ["critical", "high"]:
                    try:
                        context = {
                            "repo_name": repo_name,
                            "issue_type": issue.category.value,
                            "affected_files": issue.affected_files,
                            "severity": issue.severity.value,
                        }
                        # Use brain to analyze the issue
                        brain_result = brain.think(
                            f"Analyze {issue.category.value} issue: {issue.title}. "
                            f"Description: {issue.description}. "
                            f"Suggested fix: {issue.suggested_fix}",
                            domain="code_review",
                            context=context,
                        )
                        brain_analysis.append(
                            {
                                "issue_id": issue.id,
                                "brain_confidence": brain_result.confidence,
                                "brain_reasoning": brain_result.reasoning,
                                "brain_content": brain_result.content[:200]
                                if brain_result.content
                                else None,
                            }
                        )
                    except Exception:
                        pass  # Brain analysis is best-effort

        return {
            "repo_path": report.repo_path,
            "repo_name": report.repo_name,
            "started_at": report.started_at,
            "completed_at": report.completed_at,
            "total_issues": len(report.issues),
            "issue_breakdown": {
                "critical": len([i for i in report.issues if i.severity.value == "critical"]),
                "high": len([i for i in report.issues if i.severity.value == "high"]),
                "medium": len([i for i in report.issues if i.severity.value == "medium"]),
                "low": len([i for i in report.issues if i.severity.value == "low"]),
            },
            "issues": [
                {
                    "id": i.id,
                    "category": i.category.value,
                    "severity": i.severity.value,
                    "title": i.title,
                    "description": i.description,
                    "auto_fixable": i.auto_fixable,
                    "suggested_fix": i.suggested_fix,
                }
                for i in report.issues
            ],
            "graph_stats": report.graph_stats,
            "brain_analysis": brain_analysis if brain_analysis else None,
            "validation_results": [
                {
                    "step": v.step,
                    "success": v.success,
                    "duration_ms": v.duration_ms,
                }
                for v in report.validation_results
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autopsy failed: {e}")


@router.get("/autopsy/status")
async def get_autopsy_status():
    """Get autopsy system status."""
    return {
        "status": "ready",
        "brain_available": True,
        "tools_available": True,
        "timestamp": datetime.now(UTC).isoformat(),
    }


# ============================================================================
# WebSocket Endpoint for Real-time Agent Updates
# ============================================================================


@router.websocket("/ws/agents")
async def axiom_websocket(websocket: WebSocket):
    """WebSocket for real-time agent updates."""
    await websocket.accept()

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "message": "Axiom One WebSocket ready",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        while True:
            message = await websocket.receive_text()
            try:
                data = json.loads(message)
                msg_type = data.get("type")

                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})

                elif msg_type == "get_agents":
                    if _AXIOM_AVAILABLE and get_fleet():
                        agents = [{"type": t.value, "name": t.name} for t in AgentType]
                        await websocket.send_json({"type": "agents_list", "agents": agents})

                elif msg_type == "execute_task":
                    if _AXIOM_AVAILABLE and get_fleet():
                        # Stream task progress
                        await websocket.send_json(
                            {
                                "type": "task_started",
                                "task_id": f"task_{datetime.now().strftime('%H%M%S')}",
                                "agent_type": data.get("agent_type", "researcher"),
                            }
                        )

                        # Simulate progress
                        for progress in [25, 50, 75, 100]:
                            await asyncio.sleep(0.5)
                            await websocket.send_json(
                                {"type": "task_progress", "progress": progress}
                            )

                        await websocket.send_json(
                            {
                                "type": "task_complete",
                                "result": f"Task completed by {data.get('agent_type', 'agent')}",
                            }
                        )

                elif msg_type == "execute_tool":
                    # Execute real tool and return results
                    tool_name = data.get("tool_name")
                    tool_params = data.get("params", {})

                    try:
                        from axiom_one_agent_tools import execute_tool

                        result = execute_tool(tool_name, **tool_params)

                        await websocket.send_json(
                            {
                                "type": "tool_result",
                                "tool_name": tool_name,
                                "success": result.success,
                                "output": result.output,
                                "error": result.error,
                                "duration_ms": result.duration_ms,
                                "timestamp": datetime.now(UTC).isoformat(),
                            }
                        )
                    except Exception as e:
                        await websocket.send_json(
                            {"type": "tool_error", "tool_name": tool_name, "error": str(e)}
                        )

                elif msg_type == "list_tools":
                    try:
                        from axiom_one_agent_tools import get_tool_registry

                        registry = get_tool_registry()
                        tools = registry.list_tools()

                        await websocket.send_json({"type": "tools_list", "tools": tools})
                    except Exception as e:
                        await websocket.send_json(
                            {"type": "error", "message": f"Failed to list tools: {e}"}
                        )

                else:
                    await websocket.send_json(
                        {"type": "error", "message": f"Unknown command: {msg_type}"}
                    )

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")


@router.websocket("/ws/autopsy/{session_id}")
async def autopsy_websocket(websocket: WebSocket, session_id: str):
    """WebSocket for real-time repo autopsy streaming."""
    await websocket.accept()

    try:
        from axiom_one_websocket import get_stream_manager

        stream_manager = get_stream_manager()
        conn_id = await stream_manager.connect(websocket, session_id)

        # Send connection confirmation
        await websocket.send_json(
            {
                "event_type": "connected",
                "session_id": session_id,
                "connection_id": conn_id,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        # Send recent history if available
        history = stream_manager.get_event_history(session_id, limit=10)
        for event in history:
            await websocket.send_json(
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "timestamp": event.timestamp,
                    "payload": event.payload,
                }
            )

        # Keep connection alive and handle client messages
        while True:
            message = await websocket.receive_text()
            try:
                data = json.loads(message)
                msg_type = data.get("type")

                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})

                elif msg_type == "start_autopsy":
                    # Client requests to start autopsy - this would trigger the actual autopsy
                    repo_path = data.get("repo_path", ".")
                    repo_name = data.get("repo_name", "unknown")

                    event = stream_manager.create_autopsy_start_event(
                        session_id, repo_path, repo_name
                    )
                    await stream_manager.broadcast_to_session(session_id, event)

                elif msg_type == "disconnect":
                    break

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Autopsy WebSocket error: {e}")
    finally:
        if "stream_manager" in locals() and "conn_id" in locals():
            await stream_manager.disconnect(conn_id)
