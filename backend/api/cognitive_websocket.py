"""Cognitive WebSocket API - Real-time brain processing.

Real WebSocket endpoints that use the actual BrainClient facade
to process cognitive queries, spawn agents, and stream results.
"""

from __future__ import annotations




import asyncio
import json
import sys
import uuid
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# Add repo root to path
_REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "clawspring" / "amos_brain"))

# Import real brain facade
try:
    from amos_brain.agent_fabric_kernel import get_agent_fabric_kernel
    from amos_brain.facade import BrainClient

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False
    BrainClient = None

router = APIRouter()

# Active cognitive sessions
_cognitive_sessions: Dict[str, dict[str, Any]] = {}


class CognitiveWebSocketManager:
    """Manage cognitive WebSocket connections with real brain integration."""

    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.brain_clients: Dict[str, BrainClient] = {}

    async def connect(self, session_id: str, websocket: WebSocket) -> Optional[BrainClient]:
        """Accept connection and initialize brain client."""
        await websocket.accept()
        self.connections[session_id] = websocket

        # Initialize real brain client for this session
        if _BRAIN_AVAILABLE and BrainClient:
            client = BrainClient(repo_path=str(_REPO_ROOT))
            self.brain_clients[session_id] = client

            # Send connection success
            await websocket.send_json(
                {
                    "type": "cognitive_connected",
                    "session_id": session_id,
                    "brain_available": True,
                    "capabilities": [
                        "think",
                        "decide",
                        "validate",
                        "spawn_agent",
                        "simulate",
                        "autopsy",
                    ],
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
            return client
        else:
            await websocket.send_json(
                {
                    "type": "cognitive_connected",
                    "session_id": session_id,
                    "brain_available": False,
                    "error": "BrainClient not available",
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
            return None

    def disconnect(self, session_id: str):
        """Remove connection and cleanup."""
        self.connections.pop(session_id, None)
        self.brain_clients.pop(session_id, None)
        _cognitive_sessions.pop(session_id, None)

    async def send_progress(
        self, session_id: str, operation: str, step: int, total: int, message: str
    ):
        """Send progress update."""
        if session_id in self.connections:
            await self.connections[session_id].send_json(
                {
                    "type": "progress",
                    "operation": operation,
                    "step": step,
                    "total": total,
                    "percent": round((step / total) * 100, 1),
                    "message": message,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )

    async def send_result(self, session_id: str, result_type: str, data: dict):
        """Send final result."""
        if session_id in self.connections:
            await self.connections[session_id].send_json(
                {
                    "type": "result",
                    "result_type": result_type,
                    "data": data,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )

    async def send_error(self, session_id: str, error: str, details: str = ""):
        """Send error message."""
        if session_id in self.connections:
            await self.connections[session_id].send_json(
                {
                    "type": "error",
                    "error": error,
                    "details": details,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )


# Global manager instance
_manager = CognitiveWebSocketManager()


@router.websocket("/ws/cognitive")
async def cognitive_websocket(websocket: WebSocket):
    """Real-time cognitive processing WebSocket.

    Processes cognitive queries through the BrainClient facade:
    - think: General cognitive processing
    - decide: Decision making with options
    - validate: Action validation
    - spawn_agent: Launch bounded AI agent
    - simulate: Run deployment simulation
    - autopsy: Start repo autopsy
    """
    session_id = str(uuid.uuid4())
    client = await _manager.connect(session_id, websocket)

    if not client:
        await websocket.close(code=1011, reason="Brain not available")
        return

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await _manager.send_error(session_id, "Invalid JSON", "Message must be valid JSON")
                continue

            msg_type = message.get("type")

            # Handle cognitive operations
            if msg_type == "think":
                await _handle_think(session_id, client, message)
            elif msg_type == "decide":
                await _handle_decide(session_id, client, message)
            elif msg_type == "validate":
                await _handle_validate(session_id, client, message)
            elif msg_type == "spawn_agent":
                await _handle_spawn_agent(session_id, client, message)
            elif msg_type == "simulate":
                await _handle_simulate(session_id, client, message)
            elif msg_type == "autopsy":
                await _handle_autopsy(session_id, client, message)
            elif msg_type == "get_agent_status":
                await _handle_get_agent_status(session_id, client, message)
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                await _manager.send_error(
                    session_id,
                    f"Unknown message type: {msg_type}",
                    "Supported types: think, decide, validate, spawn_agent, simulate, autopsy",
                )

    except WebSocketDisconnect:
        _manager.disconnect(session_id)
    except Exception as e:
        await _manager.send_error(session_id, "WebSocket error", str(e))
        _manager.disconnect(session_id)


async def _handle_think(session_id: str, client: BrainClient, message: dict):
    """Handle cognitive thinking request."""
    query = message.get("query", "")
    if not query:
        await _manager.send_error(session_id, "Missing query")
        return

    await _manager.send_progress(session_id, "think", 1, 3, "Processing query...")

    # Use real brain
    response = client.think(query)

    await _manager.send_progress(session_id, "think", 2, 3, "Analyzing reasoning...")

    result = {
        "success": response.success,
        "content": response.content,
        "reasoning": response.reasoning,
        "confidence": response.confidence,
        "law_compliant": response.law_compliant,
        "violations": response.violations,
        "domain": response.domain,
    }

    await _manager.send_progress(session_id, "think", 3, 3, "Complete")
    await _manager.send_result(session_id, "think", result)


async def _handle_decide(session_id: str, client: BrainClient, message: dict):
    """Handle decision request."""
    query = message.get("query", "")
    options = message.get("options", [])

    if not query or not options:
        await _manager.send_error(session_id, "Missing query or options")
        return

    await _manager.send_progress(session_id, "decide", 1, 2, "Analyzing options...")

    decision = client.decide(query, options)

    await _manager.send_progress(session_id, "decide", 2, 2, "Decision ready")

    result = {
        "approved": decision.approved,
        "decision_id": decision.decision_id,
        "reasoning": decision.reasoning,
        "risk_level": decision.risk_level,
        "law_violations": decision.law_violations,
        "alternative_actions": decision.alternative_actions,
    }

    await _manager.send_result(session_id, "decide", result)


async def _handle_validate(session_id: str, client: BrainClient, message: dict):
    """Handle action validation request."""
    action = message.get("action", "")
    if not action:
        await _manager.send_error(session_id, "Missing action")
        return

    is_valid, violations = client.validate_action(action)

    result = {
        "action": action,
        "valid": is_valid,
        "violations": violations,
        "safe_to_execute": is_valid and not violations,
    }

    await _manager.send_result(session_id, "validate", result)


async def _handle_spawn_agent(session_id: str, client: BrainClient, message: dict):
    """Handle agent spawn request."""
    agent_class = message.get("agent_class", "repo-debugger")
    task = message.get("task", "")
    authorized_by = message.get("authorized_by", "websocket_user")

    if not task:
        await _manager.send_error(session_id, "Missing task objective")
        return

    await _manager.send_progress(session_id, "spawn_agent", 1, 3, "Registering agent...")

    try:
        agent_result = client.spawn_agent(agent_class, task, authorized_by)

        await _manager.send_progress(session_id, "spawn_agent", 2, 3, "Agent spawned")

        # Store session
        _cognitive_sessions[session_id] = {
            "agent_id": agent_result["agent_id"],
            "run_id": agent_result["run_id"],
            "class": agent_class,
        }

        await _manager.send_progress(session_id, "spawn_agent", 3, 3, "Ready")

        await _manager.send_result(session_id, "spawn_agent", agent_result)

    except Exception as e:
        await _manager.send_error(session_id, "Agent spawn failed", str(e))


async def _handle_get_agent_status(session_id: str, client: BrainClient, message: dict):
    """Get agent run status."""
    run_id = message.get("run_id")
    if not run_id and session_id in _cognitive_sessions:
        run_id = _cognitive_sessions[session_id].get("run_id")

    if not run_id:
        await _manager.send_error(session_id, "No run_id provided or found")
        return

    status = client.get_agent_run(run_id)

    if status:
        await _manager.send_result(session_id, "agent_status", status)
    else:
        await _manager.send_error(session_id, "Agent run not found")


async def _handle_simulate(session_id: str, client: BrainClient, message: dict):
    """Handle simulation request."""
    target = message.get("target", "")
    scenarios = message.get("scenarios")

    if not target:
        await _manager.send_error(session_id, "Missing target (PR/commit)")
        return

    await _manager.send_progress(session_id, "simulate", 1, 4, "Creating scenarios...")

    try:
        result = client.simulate_deployment(target, scenarios)

        await _manager.send_progress(session_id, "simulate", 2, 4, "Running simulation...")
        await asyncio.sleep(1)
        await _manager.send_progress(session_id, "simulate", 3, 4, "Computing impact...")
        await asyncio.sleep(0.5)

        # Get full results
        full_result = client.get_simulation_result(result["simulation_id"])

        await _manager.send_progress(session_id, "simulate", 4, 4, "Complete")

        if full_result:
            await _manager.send_result(session_id, "simulate", full_result)
        else:
            await _manager.send_result(session_id, "simulate", result)

    except Exception as e:
        await _manager.send_error(session_id, "Simulation failed", str(e))


async def _handle_autopsy(session_id: str, client: BrainClient, message: dict):
    """Handle repo autopsy request."""
    failure_type = message.get("failure_type", "build_failure")
    priority = message.get("priority", "p2")

    await _manager.send_progress(session_id, "autopsy", 1, 8, "Collecting evidence...")

    try:
        result = client.autopsy_repo(failure_type, priority)

        await _manager.send_progress(session_id, "autopsy", 4, 8, "Analyzing patterns...")
        await asyncio.sleep(1)
        await _manager.send_progress(session_id, "autopsy", 6, 8, "Generating fixes...")

        # Get full report
        full_report = client.get_autopsy_report(result["session_id"])

        await _manager.send_progress(session_id, "autopsy", 8, 8, "Complete")

        if full_report:
            await _manager.send_result(session_id, "autopsy", full_report)
        else:
            await _manager.send_result(session_id, "autopsy", result)

    except Exception as e:
        await _manager.send_error(session_id, "Autopsy failed", str(e))
