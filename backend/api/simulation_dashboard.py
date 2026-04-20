"""Simulation Dashboard API - Real-time deployment simulation.

Live simulation execution and monitoring using the Simulation Engine:
- Run deployment impact simulations
- Real-time scenario results streaming
- Impact analysis visualization data
- Recommendation tracking
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

UTC = UTC

# Add repo root
_REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
try:
    from amos_brain.facade import BrainClient
    from amos_brain.simulation_engine import (
        Scenario,
        SimulationRequest,
        SimulationType,
        get_simulation_engine,
    )

    _SIMULATION_AVAILABLE = True
except ImportError:
    _SIMULATION_AVAILABLE = False
    BrainClient = None

router = APIRouter(prefix="/simulation", tags=["Simulation Dashboard"])

# Active simulation sessions
_simulation_sessions: dict[str, dict[str, Any]] = {}


class SimulationRunRequest(BaseModel):
    """Request to run a simulation."""

    target: str = Field(..., description="PR number or commit to simulate")
    simulation_type: str = Field(default="deployment_impact", description="Type of simulation")
    scenarios: list[dict[str, Any]] = Field(
        default_factory=lambda: [
            {"name": "normal", "load_factor": 1.0},
            {"name": "peak", "load_factor": 2.0},
            {"name": "stress", "load_factor": 5.0},
        ],
        description="List of scenario configurations",
    )
    repo_path: str = Field(default=".", description="Repository path")


class ScenarioResult(BaseModel):
    """Individual scenario result."""

    name: str
    status: str
    load_factor: float
    latency_p95_ms: float
    throughput_rps: float
    error_rate_percent: float
    cost_per_day: float


class ImpactSummary(BaseModel):
    """Summary of impact analysis."""

    latency_change_percent: float
    throughput_change_percent: float
    error_rate_change_percent: float
    cost_change_percent: float
    failure_probability: float
    rollback_complexity: str


class RecommendationItem(BaseModel):
    """Individual recommendation."""

    priority: str
    category: str
    description: str
    confidence: float


class SimulationResult(BaseModel):
    """Complete simulation result."""

    simulation_id: str
    status: str
    target: str
    confidence_score: float
    scenarios: list[ScenarioResult]
    impact: ImpactSummary
    recommendations: list[RecommendationItem]
    started_at: str
    completed_at: str = None


class SimulationDashboard:
    """Real-time simulation dashboard manager."""

    def __init__(self):
        self.active_simulations: dict[str, dict[str, Any]] = {}
        self.subscribers: dict[str, set[WebSocket]] = {}

    async def run_simulation(self, request: SimulationRunRequest) -> SimulationResult:
        """Run simulation and track progress."""
        if not _SIMULATION_AVAILABLE or not BrainClient:
            raise HTTPException(status_code=503, detail="Simulation engine not available")

        client = BrainClient(repo_path=request.repo_path)

        # Start simulation
        result = client.simulate_deployment(target=request.target, scenarios=request.scenarios)

        sim_id = result["simulation_id"]
        self.active_simulations[sim_id] = {
            "request": request,
            "started_at": datetime.now(UTC).isoformat(),
            "status": "running",
        }

        # Wait and get full results
        await asyncio.sleep(2)
        full_result = client.get_simulation_result(sim_id)

        if full_result:
            self.active_simulations[sim_id]["status"] = "completed"
            self.active_simulations[sim_id]["result"] = full_result

            # Notify subscribers
            await self._notify_subscribers(
                sim_id,
                {"type": "simulation_complete", "simulation_id": sim_id, "result": full_result},
            )

            # Build response
            return SimulationResult(
                simulation_id=sim_id,
                status="completed",
                target=request.target,
                confidence_score=full_result.get("confidence", 0.0),
                scenarios=[],  # Parse from full_result
                impact=ImpactSummary(
                    latency_change_percent=full_result.get("impact", {}).get(
                        "latency_p95_change", 0
                    ),
                    throughput_change_percent=full_result.get("impact", {}).get(
                        "throughput_change", 0
                    ),
                    error_rate_change_percent=full_result.get("impact", {}).get(
                        "error_rate_change", 0
                    ),
                    cost_change_percent=full_result.get("impact", {}).get("cost_change", 0),
                    failure_probability=full_result.get("impact", {}).get("failure_probability", 0),
                    rollback_complexity=full_result.get("impact", {}).get(
                        "rollback_complexity", "unknown"
                    ),
                ),
                recommendations=[
                    RecommendationItem(
                        priority=rec.get("priority", "medium"),
                        category=rec.get("category", "general"),
                        description=rec.get("description", ""),
                        confidence=rec.get("confidence", 0.0),
                    )
                    for rec in full_result.get("recommendations", [])
                ],
                started_at=self.active_simulations[sim_id]["started_at"],
                completed_at=datetime.now(UTC).isoformat(),
            )
        else:
            self.active_simulations[sim_id]["status"] = "pending"
            return SimulationResult(
                simulation_id=sim_id,
                status="pending",
                target=request.target,
                confidence_score=result.get("confidence", 0.0),
                scenarios=[],
                impact=ImpactSummary(
                    latency_change_percent=0,
                    throughput_change_percent=0,
                    error_rate_change_percent=0,
                    cost_change_percent=0,
                    failure_probability=0,
                    rollback_complexity="unknown",
                ),
                recommendations=[],
                started_at=self.active_simulations[sim_id]["started_at"],
                completed_at=None,
            )

    async def subscribe(self, sim_id: str, websocket: WebSocket):
        """Subscribe to simulation updates."""
        if sim_id not in self.subscribers:
            self.subscribers[sim_id] = set()
        self.subscribers[sim_id].add(websocket)

    def unsubscribe(self, sim_id: str, websocket: WebSocket):
        """Unsubscribe from simulation updates."""
        if sim_id in self.subscribers:
            self.subscribers[sim_id].discard(websocket)

    async def _notify_subscribers(self, sim_id: str, message: dict):
        """Notify all subscribers of an update."""
        if sim_id not in self.subscribers:
            return

        dead = set()
        for ws in self.subscribers[sim_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)

        for ws in dead:
            self.subscribers[sim_id].discard(ws)


# Global dashboard instance
_dashboard = SimulationDashboard()


@router.post("/run", response_model=SimulationResult)
async def run_simulation(request: SimulationRunRequest) -> SimulationResult:
    """Run a deployment simulation and return results."""
    return await _dashboard.run_simulation(request)


@router.get("/status/{simulation_id}")
async def get_simulation_status(simulation_id: str) -> dict[str, Any]:
    """Get current status of a simulation."""
    if simulation_id not in _dashboard.active_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    session = _dashboard.active_simulations[simulation_id]
    return {
        "simulation_id": simulation_id,
        "status": session["status"],
        "started_at": session["started_at"],
        "target": session["request"].target,
    }


@router.get("/active")
async def get_active_simulations() -> list[dict[str, Any]]:
    """List all active simulations."""
    return [
        {
            "simulation_id": sim_id,
            "status": data["status"],
            "target": data["request"].target,
            "started_at": data["started_at"],
        }
        for sim_id, data in _dashboard.active_simulations.items()
        if data["status"] in ("running", "pending")
    ]


@router.websocket("/ws/{simulation_id}")
async def simulation_websocket(websocket: WebSocket, simulation_id: str):
    """WebSocket for real-time simulation updates."""
    await websocket.accept()

    # Subscribe to updates
    await _dashboard.subscribe(simulation_id, websocket)

    # Send current status
    if simulation_id in _dashboard.active_simulations:
        session = _dashboard.active_simulations[simulation_id]
        await websocket.send_json(
            {
                "type": "connected",
                "simulation_id": simulation_id,
                "status": session["status"],
                "target": session["request"].target,
            }
        )

        # If completed, send result immediately
        if session["status"] == "completed" and "result" in session:
            await websocket.send_json(
                {
                    "type": "simulation_complete",
                    "simulation_id": simulation_id,
                    "result": session["result"],
                }
            )
    else:
        await websocket.send_json(
            {"type": "error", "message": f"Simulation {simulation_id} not found"}
        )
        await websocket.close()
        return

    try:
        # Keep connection alive and handle commands
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type")

                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})

                elif msg_type == "get_result":
                    # Send current result if available
                    if simulation_id in _dashboard.active_simulations:
                        session = _dashboard.active_simulations[simulation_id]
                        if "result" in session:
                            await websocket.send_json(
                                {
                                    "type": "simulation_result",
                                    "simulation_id": simulation_id,
                                    "result": session["result"],
                                }
                            )

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketDisconnect:
        _dashboard.unsubscribe(simulation_id, websocket)


@router.get("/health")
async def simulation_health() -> dict[str, Any]:
    """Check simulation engine health."""
    return {
        "available": _SIMULATION_AVAILABLE,
        "active_simulations": len(_dashboard.active_simulations),
        "timestamp": datetime.now(UTC).isoformat(),
    }
