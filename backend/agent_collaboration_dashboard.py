"""AMOS Real-Time Collaboration Dashboard - Live Multi-Agent Visualization.

Provides real-time WebSocket-based dashboard for visualizing agent interactions,
self-evolution progress, performance metrics, and collaboration networks.

Features:
- WebSocket real-time updates
- Agent network graph visualization
- Live message flow monitoring
- Self-evolution progress tracking
- Performance metrics streaming
- Task execution pipeline view
- Interactive agent controls

Architecture:
- WebSocket Manager: Handles client connections
- Event Streamer: Broadcasts system events
- Graph Generator: Builds agent network topology
- Metrics Aggregator: Real-time performance data

Integration:
- Integrates with Brain Orchestrator for agent data
- Uses Self-Evolving Engine for improvement tracking
- Connects to Message Bus for live communication
- Leverages Knowledge system for historical data

Creator: Trang Phan
Version: 3.1.0
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agent_messaging import message_bus
from ai_cost_manager import cost_manager
from ai_governance import governance_engine

# Import AMOS subsystems
from amos_brain_orchestrator import amos_brain, get_health
from amos_self_evolving_engine import self_evolving_engine


class DashboardEventType(Enum):
    """Types of dashboard events."""

    AGENT_CREATED = "agent_created"
    AGENT_STATUS_CHANGE = "agent_status_change"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    MESSAGE_SENT = "message_sent"
    EVOLUTION_OPPORTUNITY = "evolution_opportunity"
    IMPROVEMENT_APPLIED = "improvement_applied"
    GOVERNANCE_VIOLATION = "governance_violation"
    COST_ALERT = "cost_alert"
    METRICS_UPDATE = "metrics_update"
    NETWORK_TOPOLOGY = "network_topology"


@dataclass
class DashboardEvent:
    """Event for dashboard streaming."""

    event_type: str
    timestamp: str
    data: dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


@dataclass
class AgentNode:
    """Agent node for network graph."""

    id: str
    label: str
    type: str
    status: str
    capabilities: list[str]
    metrics: dict[str, Any]
    x: float = 0.0
    y: float = 0.0


@dataclass
class AgentEdge:
    """Edge representing agent interaction."""

    source: str
    target: str
    label: str
    weight: int
    last_active: str


class WebSocketManager:
    """Manage WebSocket connections for real-time dashboard."""

    def __init__(self):
        self.connections: set[Any] = set()
        self.connection_info: dict[Any, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: Any, client_info: dict[str, Any] = None):
        """Register new WebSocket connection."""
        async with self._lock:
            self.connections.add(websocket)
            self.connection_info[websocket] = {
                "connected_at": datetime.now(UTC).isoformat(),
                "client_info": client_info or {},
                "subscribed_events": [],
            }

        print(f"🔌 Dashboard client connected. Total: {len(self.connections)}")

        # Send initial data
        await self._send_initial_data(websocket)

    async def disconnect(self, websocket: Any):
        """Remove WebSocket connection."""
        async with self._lock:
            self.connections.discard(websocket)
            self.connection_info.pop(websocket, None)

        print(f"🔌 Dashboard client disconnected. Total: {len(self.connections)}")

    async def broadcast(self, event: DashboardEvent):
        """Broadcast event to all connected clients."""
        if not self.connections:
            return

        message = json.dumps(
            {
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "event_id": event.event_id,
                "data": event.data,
            }
        )

        # Send to all connections
        disconnected = []
        for ws in self.connections:
            try:
                await ws.send(message)
            except Exception:
                disconnected.append(ws)

        # Clean up disconnected clients
        for ws in disconnected:
            await self.disconnect(ws)

    async def _send_initial_data(self, websocket: Any):
        """Send initial dashboard data to new client."""
        # Send current system state
        await websocket.send(
            json.dumps(
                {
                    "event_type": "initial_state",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "data": {
                        "agents": self._get_agent_summary(),
                        "system_health": await get_health(),
                        "network_topology": self._get_network_topology(),
                    },
                }
            )
        )

    def _get_agent_summary(self) -> list[dict[str, Any]]:
        """Get summary of all agents."""
        return [
            {
                "id": agent.agent_id,
                "type": agent.agent_type,
                "status": agent.status,
                "capabilities": agent.capabilities,
                "total_tasks": agent.total_tasks,
                "success_rate": round(agent.successful_tasks / agent.total_tasks * 100, 1)
                if agent.total_tasks > 0
                else 0,
            }
            for agent in amos_brain.agents.values()
        ]

    def _get_network_topology(self) -> dict[str, Any]:
        """Get current network topology."""
        nodes = []
        edges = []

        # Create nodes for each agent
        for agent in amos_brain.agents.values():
            nodes.append(
                {
                    "id": agent.agent_id,
                    "label": f"{agent.agent_type}\n{agent.agent_id[:8]}",
                    "type": agent.agent_type,
                    "status": agent.status,
                    "capabilities": agent.capabilities,
                }
            )

        # Create edges from message history
        for msg in message_bus._history[-50:]:  # Last 50 messages
            if msg.sender_id != "system" and msg.recipient_id != "broadcast":
                edges.append(
                    {
                        "source": msg.sender_id,
                        "target": msg.recipient_id,
                        "type": msg.message_type,
                        "timestamp": msg.timestamp,
                    }
                )

        return {"nodes": nodes, "edges": edges}


class EventStreamer:
    """Stream system events to dashboard in real-time."""

    def __init__(self, ws_manager: WebSocketManager):
        self.ws_manager = ws_manager
        self.streaming = False
        self.stream_task = None

    async def start(self):
        """Start event streaming."""
        self.streaming = True
        self.stream_task = asyncio.create_task(self._stream_loop())
        print("📡 Event streamer started")

    async def stop(self):
        """Stop event streaming."""
        self.streaming = False
        if self.stream_task:
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass
        print("📡 Event streamer stopped")

    async def _stream_loop(self):
        """Main streaming loop."""
        while self.streaming:
            try:
                # Stream metrics update
                await self._stream_metrics()

                # Stream network topology
                await self._stream_topology()

                # Wait before next update
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Stream error: {e}")
                await asyncio.sleep(10)

    async def _stream_metrics(self):
        """Stream current metrics."""
        metrics = {
            "agents": len(amos_brain.agents),
            "active_agents": len([a for a in amos_brain.agents.values() if a.status == "active"]),
            "busy_agents": len([a for a in amos_brain.agents.values() if a.status == "busy"]),
            "queued_tasks": amos_brain.task_queue.qsize(),
            "running_tasks": len(amos_brain.running_tasks),
            "total_messages": len(message_bus._history),
            "governance_violations": len(governance_engine.violations),
            "active_budgets": len(cost_manager.budgets),
        }

        event = DashboardEvent(
            event_type=DashboardEventType.METRICS_UPDATE.value,
            timestamp=datetime.now(UTC).isoformat(),
            data=metrics,
        )

        await self.ws_manager.broadcast(event)

    async def _stream_topology(self):
        """Stream network topology updates."""
        topology = self.ws_manager._get_network_topology()

        event = DashboardEvent(
            event_type=DashboardEventType.NETWORK_TOPOLOGY.value,
            timestamp=datetime.now(UTC).isoformat(),
            data=topology,
        )

        await self.ws_manager.broadcast(event)

    async def emit_agent_created(self, agent_id: str, agent_type: str):
        """Emit agent created event."""
        event = DashboardEvent(
            event_type=DashboardEventType.AGENT_CREATED.value,
            timestamp=datetime.now(UTC).isoformat(),
            data={"agent_id": agent_id, "agent_type": agent_type},
        )
        await self.ws_manager.broadcast(event)

    async def emit_agent_status_change(self, agent_id: str, old_status: str, new_status: str):
        """Emit agent status change event."""
        event = DashboardEvent(
            event_type=DashboardEventType.AGENT_STATUS_CHANGE.value,
            timestamp=datetime.now(UTC).isoformat(),
            data={"agent_id": agent_id, "old_status": old_status, "new_status": new_status},
        )
        await self.ws_manager.broadcast(event)

    async def emit_task_completed(
        self, agent_id: str, task_id: str, success: bool, latency_ms: float
    ):
        """Emit task completed event."""
        event = DashboardEvent(
            event_type=DashboardEventType.TASK_COMPLETED.value,
            timestamp=datetime.now(UTC).isoformat(),
            data={
                "agent_id": agent_id,
                "task_id": task_id,
                "success": success,
                "latency_ms": latency_ms,
            },
        )
        await self.ws_manager.broadcast(event)

    async def emit_message_sent(self, sender_id: str, recipient_id: str, message_type: str):
        """Emit message sent event."""
        event = DashboardEvent(
            event_type=DashboardEventType.MESSAGE_SENT.value,
            timestamp=datetime.now(UTC).isoformat(),
            data={
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "message_type": message_type,
            },
        )
        await self.ws_manager.broadcast(event)

    async def emit_improvement_applied(
        self, agent_id: str, improvement_type: str, improvement_percent: float
    ):
        """Emit improvement applied event."""
        event = DashboardEvent(
            event_type=DashboardEventType.IMPROVEMENT_APPLIED.value,
            timestamp=datetime.now(UTC).isoformat(),
            data={
                "agent_id": agent_id,
                "improvement_type": improvement_type,
                "improvement_percent": improvement_percent,
            },
        )
        await self.ws_manager.broadcast(event)


class CollaborationDashboard:
    """Main collaboration dashboard controller."""

    def __init__(self):
        self.ws_manager = WebSocketManager()
        self.event_streamer = EventStreamer(self.ws_manager)
        self.running = False

    async def start(self):
        """Start the collaboration dashboard."""
        print("🎯 Starting AMOS Collaboration Dashboard...")

        # Start event streaming
        await self.event_streamer.start()

        self.running = True
        print("✅ Collaboration Dashboard started")
        print("   WebSocket endpoint: ws://localhost:8000/ws/dashboard")
        return True

    async def stop(self):
        """Stop the collaboration dashboard."""
        print("🛑 Stopping Collaboration Dashboard...")

        self.running = False

        # Stop event streaming
        await self.event_streamer.stop()

        # Disconnect all clients
        for ws in list(self.ws_manager.connections):
            await self.ws_manager.disconnect(ws)

        print("✅ Collaboration Dashboard stopped")
        return True

    async def handle_websocket(self, websocket: Any, path: str = None):
        """Handle WebSocket connection."""
        await self.ws_manager.connect(websocket)

        try:
            while self.running:
                # Handle incoming messages from client
                message = await websocket.receive()
                data = json.loads(message)

                # Handle client commands
                command = data.get("command")
                if command == "get_agent_details":
                    agent_id = data.get("agent_id")
                    details = self._get_agent_details(agent_id)
                    await websocket.send(
                        json.dumps({"event_type": "agent_details", "data": details})
                    )

                elif command == "get_evolution_history":
                    agent_id = data.get("agent_id")
                    history = self._get_evolution_history(agent_id)
                    await websocket.send(
                        json.dumps({"event_type": "evolution_history", "data": history})
                    )

                elif command == "trigger_improvement":
                    agent_id = data.get("agent_id")
                    # Trigger manual improvement
                    await self._trigger_manual_improvement(agent_id)

        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            await self.ws_manager.disconnect(websocket)

    def _get_agent_details(self, agent_id: str) -> dict[str, Any]:
        """Get detailed information about an agent."""
        agent = amos_brain.agents.get(agent_id)
        if not agent:
            return {"error": "Agent not found"}

        # Get evolution summary
        evolution = self_evolving_engine.get_performance_summary(agent_id)

        # Get recent messages
        messages = [
            {
                "sender": msg.sender_id,
                "recipient": msg.recipient_id,
                "type": msg.message_type,
                "timestamp": msg.timestamp,
            }
            for msg in message_bus._history[-20:]
            if msg.sender_id == agent_id or msg.recipient_id == agent_id
        ]

        return {
            "agent_id": agent.agent_id,
            "agent_type": agent.agent_type,
            "status": agent.status,
            "capabilities": agent.capabilities,
            "total_tasks": agent.total_tasks,
            "successful_tasks": agent.successful_tasks,
            "success_rate": round(agent.successful_tasks / agent.total_tasks * 100, 1)
            if agent.total_tasks > 0
            else 0,
            "evolution": evolution,
            "recent_messages": messages,
            "config": agent.config,
        }

    def _get_evolution_history(self, agent_id: str) -> list[dict[str, Any]]:
        """Get evolution history for an agent."""
        improvements = self_evolving_engine.get_agent_improvements(agent_id)

        return [
            {
                "improvement_id": imp.improvement_id,
                "type": imp.strategy_applied,
                "success": imp.success,
                "improvement_percent": imp.improvement_percent,
                "deployed_at": imp.deployed_at,
                "before_metrics": imp.before_metrics,
                "after_metrics": imp.after_metrics,
            }
            for imp in improvements
        ]

    async def _trigger_manual_improvement(self, agent_id: str):
        """Trigger a manual improvement for an agent."""
        # Analyze for opportunities
        opportunities = await self_evolving_engine.opportunity_detector.analyze_agent(agent_id)

        if opportunities:
            # Apply first opportunity
            result = await self_evolving_engine.improvement_engine.apply_improvement(
                agent_id, opportunities[0]
            )

            # Emit event
            await self.event_streamer.emit_improvement_applied(
                agent_id, opportunities[0].improvement_type, result.improvement_percent
            )


# Global instance
collaboration_dashboard = CollaborationDashboard()


# Convenience functions
async def start_dashboard() -> bool:
    """Start the collaboration dashboard."""
    return await collaboration_dashboard.start()


async def stop_dashboard() -> bool:
    """Stop the collaboration dashboard."""
    return await collaboration_dashboard.stop()


async def handle_dashboard_websocket(websocket: Any, path: str = None):
    """Handle dashboard WebSocket connections."""
    await collaboration_dashboard.handle_websocket(websocket, path)


# Event emitters for integration
async def emit_agent_created(agent_id: str, agent_type: str):
    """Emit agent created event."""
    await collaboration_dashboard.event_streamer.emit_agent_created(agent_id, agent_type)


async def emit_task_completed(agent_id: str, task_id: str, success: bool, latency_ms: float):
    """Emit task completed event."""
    await collaboration_dashboard.event_streamer.emit_task_completed(
        agent_id, task_id, success, latency_ms
    )


async def emit_message_sent(sender_id: str, recipient_id: str, message_type: str):
    """Emit message sent event."""
    await collaboration_dashboard.event_streamer.emit_message_sent(
        sender_id, recipient_id, message_type
    )


async def emit_improvement_applied(
    agent_id: str, improvement_type: str, improvement_percent: float
):
    """Emit improvement applied event."""
    await collaboration_dashboard.event_streamer.emit_improvement_applied(
        agent_id, improvement_type, improvement_percent
    )
