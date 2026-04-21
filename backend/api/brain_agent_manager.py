"""AMOS Brain Agent Manager API

Real-time agent spawning, monitoring, and orchestration via BrainClient.
Direct integration with MasterOrchestrator for complex agent workflows.

Creator: Trang Phan
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

# Import BrainClient facade
try:
    from clawspring.agents.amos_brain.facade import BrainClient
    from clawspring.agents.amos_brain.master_orchestrator import MasterOrchestrator

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False

router = APIRouter(prefix="/api/v1/brain/agents", tags=["Brain Agent Manager"])


class AgentSpawnRequest(BaseModel):
    """Request to spawn a new agent."""

    agent_type: str = Field(..., description="Type of agent to spawn")
    task: str = Field(..., min_length=1, description="Task for the agent")
    context: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10)
    timeout_seconds: int = Field(default=300, ge=10)


class AgentSpawnResponse(BaseModel):
    """Response after spawning an agent."""

    agent_id: str
    agent_type: str
    task: str
    status: str
    spawn_timestamp: str
    estimated_completion: str
    orchestrator_task_id: str


class AgentStatus(BaseModel):
    """Current status of an agent."""

    agent_id: str
    status: str  # pending, running, completed, failed
    progress_percent: float
    current_step: str
    thoughts: list[str]
    legality_score: float
    confidence: float
    last_update: str


class AgentResult(BaseModel):
    """Result from a completed agent."""

    agent_id: str
    status: str
    result: dict[str, Any]
    reasoning: str
    execution_time_ms: float
    memory_entries_saved: int
    timestamp: str


class BrainAgentManager:
    """Manager for brain-powered agent spawning and control."""

    def __init__(self):
        self._agents: dict[str, AgentStatus] = {}
        self._results: dict[str, AgentResult] = {}
        self._active_tasks: dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def spawn_agent(
        self,
        request: AgentSpawnRequest,
    ) -> AgentSpawnResponse:
        """Spawn a new agent using brain orchestration."""
        agent_id = str(uuid4())
        spawn_time = datetime.now(UTC)

        # Create initial status
        status = AgentStatus(
            agent_id=agent_id,
            status="pending",
            progress_percent=0.0,
            current_step="initializing",
            thoughts=[],
            legality_score=1.0,
            confidence=0.8,
            last_update=spawn_time.isoformat(),
        )

        async with self._lock:
            self._agents[agent_id] = status

        # Start agent execution
        task = asyncio.create_task(self._execute_agent(agent_id, request))
        self._active_tasks[agent_id] = task

        return AgentSpawnResponse(
            agent_id=agent_id,
            agent_type=request.agent_type,
            task=request.task,
            status="pending",
            spawn_timestamp=spawn_time.isoformat(),
            estimated_completion=None,
            orchestrator_task_id=None,
        )

    async def _execute_agent(
        self,
        agent_id: str,
        request: AgentSpawnRequest,
    ) -> None:
        """Execute agent with brain integration."""
        start_time = time.time()

        try:
            async with self._lock:
                if agent_id in self._agents:
                    self._agents[agent_id].status = "running"
                    self._agents[agent_id].current_step = "brain_thinking"
                    self._agents[agent_id].last_update = datetime.now(UTC).isoformat()

            if _BRAIN_AVAILABLE:
                client = BrainClient()
                orchestrator = MasterOrchestrator()

                # Step 1: Brain analysis
                async with self._lock:
                    if agent_id in self._agents:
                        self._agents[agent_id].current_step = "analyzing_task"
                        self._agents[agent_id].progress_percent = 10.0

                think_result = await client.think(
                    thought=f"Analyze and plan: {request.task}",
                    context={
                        "agent_type": request.agent_type,
                        "priority": request.priority,
                        **request.context,
                    },
                    use_legality=True,
                )

                async with self._lock:
                    if agent_id in self._agents:
                        self._agents[agent_id].thoughts.append(
                            think_result.get("response", "Task analyzed")
                        )
                        self._agents[agent_id].legality_score = think_result.get(
                            "legality_score", 1.0
                        )
                        self._agents[agent_id].progress_percent = 30.0

                # Step 2: Orchestrate cognitive task
                async with self._lock:
                    if agent_id in self._agents:
                        self._agents[agent_id].current_step = "executing_task"
                        self._agents[agent_id].progress_percent = 40.0

                orchestration_result = await orchestrator.orchestrate_cognitive_task(
                    task_type=request.agent_type,
                    inputs={
                        "task": request.task,
                        "analysis": think_result,
                        **request.context,
                    },
                )

                async with self._lock:
                    if agent_id in self._agents:
                        self._agents[agent_id].progress_percent = 80.0
                        self._agents[agent_id].current_step = "finalizing"

                # Complete
                execution_time_ms = (time.time() - start_time) * 1000

                result = AgentResult(
                    agent_id=agent_id,
                    status="completed",
                    result=orchestration_result,
                    reasoning=think_result.get("response", ""),
                    execution_time_ms=execution_time_ms,
                    memory_entries_saved=0,
                    timestamp=datetime.now(UTC).isoformat(),
                )

                async with self._lock:
                    self._results[agent_id] = result
                    if agent_id in self._agents:
                        self._agents[agent_id].status = "completed"
                        self._agents[agent_id].progress_percent = 100.0
                        self._agents[agent_id].last_update = datetime.now(UTC).isoformat()

            else:
                # Fallback without brain
                async with self._lock:
                    if agent_id in self._agents:
                        self._agents[agent_id].status = "failed"
                        self._agents[agent_id].current_step = "brain_unavailable"
                        self._agents[agent_id].last_update = datetime.now(UTC).isoformat()

        except Exception as e:
            async with self._lock:
                if agent_id in self._agents:
                    self._agents[agent_id].status = "failed"
                    self._agents[agent_id].current_step = f"error: {e!s}"
                    self._agents[agent_id].last_update = datetime.now(UTC).isoformat()

    def get_agent_status(self, agent_id: str) -> AgentStatus:
        """Get current status of an agent."""
        return self._agents.get(agent_id)

    def get_agent_result(self, agent_id: str) -> AgentResult:
        """Get result of a completed agent."""
        return self._results.get(agent_id)

    def list_agents(
        self,
        status_filter: str = None,
    ) -> list[AgentStatus]:
        """List all agents, optionally filtered by status."""
        agents = list(self._agents.values())
        if status_filter:
            agents = [a for a in agents if a.status == status_filter]
        return agents

    async def cancel_agent(self, agent_id: str) -> bool:
        """Cancel a running agent."""
        async with self._lock:
            if agent_id in self._active_tasks:
                task = self._active_tasks[agent_id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            if agent_id in self._agents:
                self._agents[agent_id].status = "cancelled"
                self._agents[agent_id].last_update = datetime.now(UTC).isoformat()

            return True

    async def cleanup_completed(self, max_age_seconds: int = 3600) -> int:
        """Clean up completed/failed agents older than max_age."""
        cutoff = datetime.now(UTC).timestamp() - max_age_seconds
        cleaned = 0

        async with self._lock:
            to_remove = []
            for agent_id, agent in self._agents.items():
                if agent.status in ("completed", "failed", "cancelled"):
                    update_time = datetime.fromisoformat(agent.last_update).timestamp()
                    if update_time < cutoff:
                        to_remove.append(agent_id)

            for agent_id in to_remove:
                del self._agents[agent_id]
                if agent_id in self._results:
                    del self._results[agent_id]
                if agent_id in self._active_tasks:
                    del self._active_tasks[agent_id]
                cleaned += 1

        return cleaned

    def get_stats(self) -> dict[str, Any]:
        """Get manager statistics."""
        statuses = {"pending": 0, "running": 0, "completed": 0, "failed": 0, "cancelled": 0}
        for agent in self._agents.values():
            if agent.status in statuses:
                statuses[agent.status] += 1

        return {
            "total_agents": len(self._agents),
            "active_tasks": len(self._active_tasks),
            "completed_results": len(self._results),
            "by_status": statuses,
            "brain_available": _BRAIN_AVAILABLE,
        }


# Global agent manager
agent_manager = BrainAgentManager()


@router.post("/spawn", response_model=AgentSpawnResponse)
async def spawn_agent_endpoint(request: AgentSpawnRequest) -> AgentSpawnResponse:
    """Spawn a new brain-powered agent."""
    return await agent_manager.spawn_agent(request)


@router.get("/status/{agent_id}", response_model=AgentStatus)
async def get_agent_status(agent_id: str) -> AgentStatus:
    """Get status of a specific agent."""
    status = agent_manager.get_agent_status(agent_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return status


@router.get("/result/{agent_id}", response_model=AgentResult)
async def get_agent_result(agent_id: str) -> AgentResult:
    """Get result of a completed agent."""
    result = agent_manager.get_agent_result(agent_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found or agent still running")
    return result


@router.get("/list")
async def list_agents(status: str = None) -> list[AgentStatus]:
    """List all agents with optional status filter."""
    return agent_manager.list_agents(status)


@router.post("/cancel/{agent_id}")
async def cancel_agent(agent_id: str) -> dict[str, str]:
    """Cancel a running agent."""
    success = await agent_manager.cancel_agent(agent_id)
    return {"agent_id": agent_id, "cancelled": str(success)}


@router.post("/cleanup")
async def cleanup_agents(max_age_seconds: int = 3600) -> dict[str, int]:
    """Clean up old completed agents."""
    cleaned = await agent_manager.cleanup_completed(max_age_seconds)
    return {"cleaned": cleaned}


@router.get("/stats")
async def get_manager_stats() -> dict[str, Any]:
    """Get agent manager statistics."""
    return agent_manager.get_stats()


@router.websocket("/ws/{agent_id}")
async def agent_websocket(websocket: WebSocket, agent_id: str) -> None:
    """WebSocket for real-time agent monitoring.

    Streams agent status updates as they happen.
    """
    await websocket.accept()

    try:
        # Send initial status
        status = agent_manager.get_agent_status(agent_id)
        if status:
            await websocket.send_json(
                {
                    "type": "status",
                    "data": status.model_dump(),
                }
            )
        else:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": "Agent not found",
                }
            )
            await websocket.close()
            return

        # Stream updates until agent completes
        last_status = status.status if status else None
        while True:
            await asyncio.sleep(1)

            current = agent_manager.get_agent_status(agent_id)
            if current is None:
                break

            if current.status != last_status:
                await websocket.send_json(
                    {
                        "type": "status_update",
                        "data": current.model_dump(),
                    }
                )
                last_status = current.status

            if current.status in ("completed", "failed", "cancelled"):
                result = agent_manager.get_agent_result(agent_id)
                if result:
                    await websocket.send_json(
                        {
                            "type": "result",
                            "data": result.model_dump(),
                        }
                    )
                break

        await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
