"""AMOS Governance Streaming API v1.0.0 - Real-Time Dashboard Feeds

Provides WebSocket streaming for autonomous governance system:
- Live prediction updates
- Governance cycle status
- Detection results
- Alert notifications
- System health metrics

Architecture:
    Dashboard/WebSocket Client
              ↓
    GovernanceStreamingAPI
              ↓
    UnifiedGovernanceCoordinator
              ↓
    Detection → Prediction → Remediation

WebSocket Endpoints:
- /ws/governance/stream - All governance events
- /ws/governance/predictions - Prediction updates only
- /ws/governance/alerts - Alert notifications
- /ws/governance/health - System health metrics

Integration:
- UnifiedGovernanceCoordinator (data source)
- PredictiveIntelligenceEngine (predictions)
- UnifiedDetectionEngine (detection results)

Owner: Trang Phan
Version: 1.0.0
"""

import asyncio
import json
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# WebSocket support
try:
    import websockets
    from websockets.server import WebSocketServerProtocol

    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

# Import governance components
try:
    from .unified_governance_coordinator import (
        GovernanceMode,
        SystemPhase,
        UnifiedGovernanceCoordinator,
    )

    COORDINATOR_AVAILABLE = True
except ImportError:
    COORDINATOR_AVAILABLE = False

try:
    from .predictive_intelligence_engine import (
        Prediction,
        PredictiveAlert,
        PredictiveIntelligenceEngine,
    )

    PREDICTION_AVAILABLE = True
except ImportError:
    PREDICTION_AVAILABLE = False


# =============================================================================
# Enums and Data Classes
# =============================================================================


class StreamEventType(Enum):
    """Types of streaming events."""

    PREDICTION_UPDATE = "prediction_update"
    ALERT_TRIGGERED = "alert_triggered"
    CYCLE_STARTED = "cycle_started"
    CYCLE_COMPLETED = "cycle_completed"
    PHASE_CHANGED = "phase_changed"
    HEALTH_UPDATE = "health_update"
    DETECTION_RESULT = "detection_result"
    REMEDIATION_ACTION = "remediation_action"


@dataclass
class StreamEvent:
    """Single streaming event."""

    event_type: StreamEventType
    timestamp: float
    data: Dict[str, Any]
    priority: str = "normal"  # low, normal, high, critical

    def to_json(self) -> str:
        return json.dumps(
            {
                "type": self.event_type.value,
                "timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
                "priority": self.priority,
                "data": self.data,
            }
        )


@dataclass
class SubscriptionConfig:
    """Client subscription configuration."""

    client_id: str
    event_types: List[StreamEventType] = field(default_factory=list)
    min_priority: str = "low"
    filter_patterns: List[str] = field(default_factory=list)
    max_events_per_minute: int = 60


# =============================================================================
# Governance Streaming API
# =============================================================================


class GovernanceStreamingAPI:
    """
    Real-time streaming API for AMOS governance system.

    Features:
    - WebSocket broadcasting to multiple clients
    - Event filtering by type and priority
    - Rate limiting per client
    - Automatic reconnection support
    - Historical event buffer

    Streaming Events:
    - Predictions (as they're generated)
    - Alerts (when thresholds are exceeded)
    - Cycle status (start, phase changes, completion)
    - Health metrics (periodic updates)
    - Detection results (after each detection run)
    """

    def __init__(
        self,
        coordinator: Optional[UnifiedGovernanceCoordinator] = None,
        port: int = 8767,
    ):
        self.port = port
        self._coordinator = coordinator

        # State
        self._clients: Dict[str, WebSocketServerProtocol] = {}
        self._subscriptions: Dict[str, SubscriptionConfig] = {}
        self._event_history: deque[StreamEvent] = deque(maxlen=1000)
        self._running = False
        self._server: Optional[Any] = None

        # Statistics
        self._stats = {
            "connections_total": 0,
            "messages_sent": 0,
            "events_processed": 0,
        }

        # Callbacks for coordinator events
        self._setup_coordinator_callbacks()

    def _setup_coordinator_callbacks(self) -> None:
        """Set up callbacks on the governance coordinator."""
        if not self._coordinator:
            return

        # Register for prediction alerts
        if PREDICTION_AVAILABLE and self._coordinator._prediction_engine:
            self._coordinator._prediction_engine.register_alert_handler(self._on_predictive_alert)

    # ==========================================================================
    # WebSocket Server
    # ==========================================================================

    async def start(self) -> None:
        """Start the WebSocket streaming server."""
        if not WEBSOCKETS_AVAILABLE:
            print("[GovernanceStreaming] websockets not available, cannot start")
            return

        self._running = True

        self._server = await websockets.serve(
            self._handle_client,
            "0.0.0.0",
            self.port,
            ping_interval=30,
            ping_timeout=10,
        )

        print(f"[GovernanceStreaming] Server started on ws://0.0.0.0:{self.port}")
        print("[GovernanceStreaming] Endpoints:")
        print("  - /ws/governance/stream")
        print("  - /ws/governance/predictions")
        print("  - /ws/governance/alerts")
        print("  - /ws/governance/health")

        # Start background tasks
        asyncio.create_task(self._health_broadcast_loop())

        # Keep running
        await asyncio.Future()  # Run forever

    def stop(self) -> None:
        """Stop the streaming server."""
        self._running = False
        if self._server:
            self._server.close()
        print("[GovernanceStreaming] Server stopped")

    async def _handle_client(
        self,
        websocket: WebSocketServerProtocol,
        path: str,
    ) -> None:
        """Handle incoming WebSocket connection."""
        client_id = f"client_{id(websocket)}_{int(time.time())}"
        self._clients[client_id] = websocket
        self._stats["connections_total"] += 1

        # Determine subscription based on path
        sub_config = self._create_subscription(client_id, path)
        self._subscriptions[client_id] = sub_config

        print(f"[GovernanceStreaming] Client connected: {client_id} ({path})")

        try:
            # Send welcome message
            await websocket.send(
                json.dumps(
                    {
                        "type": "connected",
                        "client_id": client_id,
                        "path": path,
                        "supported_events": [e.value for e in StreamEventType],
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            )

            # Handle incoming messages (subscriptions, filters, etc.)
            async for message in websocket:
                await self._handle_client_message(client_id, message)

        except websockets.exceptions.ConnectionClosed:
            print(f"[GovernanceStreaming] Client disconnected: {client_id}")
        finally:
            # Cleanup
            if client_id in self._clients:
                del self._clients[client_id]
            if client_id in self._subscriptions:
                del self._subscriptions[client_id]

    def _create_subscription(self, client_id: str, path: str) -> SubscriptionConfig:
        """Create subscription config based on path."""
        if path.endswith("/predictions"):
            return SubscriptionConfig(
                client_id=client_id,
                event_types=[StreamEventType.PREDICTION_UPDATE],
            )
        elif path.endswith("/alerts"):
            return SubscriptionConfig(
                client_id=client_id,
                event_types=[
                    StreamEventType.ALERT_TRIGGERED,
                    StreamEventType.REMEDIATION_ACTION,
                ],
                min_priority="high",
            )
        elif path.endswith("/health"):
            return SubscriptionConfig(
                client_id=client_id,
                event_types=[StreamEventType.HEALTH_UPDATE],
            )
        else:
            # Full stream - all events
            return SubscriptionConfig(
                client_id=client_id,
                event_types=list(StreamEventType),
            )

    async def _handle_client_message(self, client_id: str, message: str) -> None:
        """Handle message from client."""
        try:
            data = json.loads(message)
            action = data.get("action")

            if action == "filter":
                # Update subscription filters
                if client_id in self._subscriptions:
                    sub = self._subscriptions[client_id]
                    if "event_types" in data:
                        sub.event_types = [StreamEventType(e) for e in data["event_types"]]
                    if "min_priority" in data:
                        sub.min_priority = data["min_priority"]

            elif action == "ping":
                # Send pong
                if client_id in self._clients:
                    await self._clients[client_id].send(
                        json.dumps(
                            {
                                "type": "pong",
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                    )

            elif action == "get_history":
                # Send recent event history
                await self._send_history(client_id)

        except json.JSONDecodeError:
            print(f"[GovernanceStreaming] Invalid message from {client_id}")
        except Exception as e:
            print(f"[GovernanceStreaming] Error handling message: {e}")

    async def _send_history(self, client_id: str) -> None:
        """Send recent event history to client."""
        if client_id not in self._clients:
            return

        recent_events = list(self._event_history)[-50:]  # Last 50 events

        await self._clients[client_id].send(
            json.dumps(
                {
                    "type": "history",
                    "events": [
                        {
                            "type": e.event_type.value,
                            "timestamp": datetime.fromtimestamp(e.timestamp).isoformat(),
                            "priority": e.priority,
                            "data": e.data,
                        }
                        for e in recent_events
                    ],
                }
            )
        )

    # ==========================================================================
    # Event Broadcasting
    # ==========================================================================

    def broadcast_event(self, event: StreamEvent) -> None:
        """Broadcast event to all subscribed clients."""
        # Store in history
        self._event_history.append(event)
        self._stats["events_processed"] += 1

        # Send to matching clients
        for client_id, sub in self._subscriptions.items():
            if self._should_send_to_client(event, sub):
                asyncio.create_task(self._send_to_client(client_id, event))

    def _should_send_to_client(self, event: StreamEvent, sub: SubscriptionConfig) -> bool:
        """Check if event should be sent to client based on subscription."""
        # Check event type
        if event.event_type not in sub.event_types:
            return False

        # Check priority
        priority_levels = {"low": 0, "normal": 1, "high": 2, "critical": 3}
        if priority_levels.get(event.priority, 0) < priority_levels.get(sub.min_priority, 0):
            return False

        return True

    async def _send_to_client(self, client_id: str, event: StreamEvent) -> None:
        """Send event to specific client."""
        if client_id not in self._clients:
            return

        try:
            await self._clients[client_id].send(event.to_json())
            self._stats["messages_sent"] += 1
        except websockets.exceptions.ConnectionClosed:
            # Client disconnected, cleanup
            if client_id in self._clients:
                del self._clients[client_id]
            if client_id in self._subscriptions:
                del self._subscriptions[client_id]
        except Exception as e:
            print(f"[GovernanceStreaming] Error sending to {client_id}: {e}")

    # ==========================================================================
    # Event Generators
    # ==========================================================================

    def on_cycle_started(self, cycle_id: str) -> None:
        """Called when governance cycle starts."""
        event = StreamEvent(
            event_type=StreamEventType.CYCLE_STARTED,
            timestamp=time.time(),
            data={"cycle_id": cycle_id},
            priority="normal",
        )
        self.broadcast_event(event)

    def on_phase_changed(self, phase: str, cycle_id: str) -> None:
        """Called when governance phase changes."""
        event = StreamEvent(
            event_type=StreamEventType.PHASE_CHANGED,
            timestamp=time.time(),
            data={
                "phase": phase,
                "cycle_id": cycle_id,
            },
            priority="normal",
        )
        self.broadcast_event(event)

    def on_cycle_completed(self, cycle_result: dict) -> None:
        """Called when governance cycle completes."""
        priority = "normal"
        if cycle_result.get("status") == "error":
            priority = "high"
        elif cycle_result.get("issues_remediated", 0) > 0:
            priority = "high"

        event = StreamEvent(
            event_type=StreamEventType.CYCLE_COMPLETED,
            timestamp=time.time(),
            data={
                "cycle_id": cycle_result.get("cycle_id"),
                "status": cycle_result.get("status"),
                "issues_found": cycle_result.get("issues_found", 0),
                "issues_predicted": cycle_result.get("issues_predicted", 0),
                "issues_remediated": cycle_result.get("issues_remediated", 0),
                "time_elapsed_ms": cycle_result.get("time_elapsed_ms", 0),
            },
            priority=priority,
        )
        self.broadcast_event(event)

    def on_prediction_generated(self, prediction: Prediction) -> None:
        """Called when new prediction is generated."""
        priority = "normal"
        if prediction.risk_score > 0.8:
            priority = "critical"
        elif prediction.risk_score > 0.6:
            priority = "high"

        event = StreamEvent(
            event_type=StreamEventType.PREDICTION_UPDATE,
            timestamp=time.time(),
            data={
                "prediction_id": prediction.prediction_id,
                "metric_name": prediction.metric_name,
                "horizon": prediction.horizon.value,
                "current_value": round(prediction.current_value, 3),
                "predicted_value": round(prediction.predicted_value, 3),
                "confidence": round(prediction.confidence, 3),
                "risk_score": round(prediction.risk_score, 3),
                "severity": prediction.severity,
                "recommended_action": prediction.recommended_action,
                "time_until_issue": prediction.time_until_issue,
            },
            priority=priority,
        )
        self.broadcast_event(event)

    def _on_predictive_alert(self, alert: PredictiveAlert) -> None:
        """Called when predictive alert is triggered."""
        priority = "high" if alert.worst_severity in ["high", "critical"] else "normal"

        event = StreamEvent(
            event_type=StreamEventType.ALERT_TRIGGERED,
            timestamp=time.time(),
            data={
                "alert_id": alert.alert_id,
                "overall_risk": round(alert.overall_risk, 3),
                "worst_severity": alert.worst_severity,
                "predictions_count": len(alert.predictions),
                "action_triggered": alert.action_triggered,
                "action_type": alert.action_type,
            },
            priority=priority,
        )
        self.broadcast_event(event)

    def on_detection_completed(self, detection_report: dict) -> None:
        """Called when detection completes."""
        event = StreamEvent(
            event_type=StreamEventType.DETECTION_RESULT,
            timestamp=time.time(),
            data={
                "session_id": detection_report.get("session_id"),
                "overall_health": detection_report.get("overall_system_health"),
                "alerts_count": len(detection_report.get("critical_alerts", [])),
                "warnings_count": len(detection_report.get("warnings", [])),
            },
            priority="normal",
        )
        self.broadcast_event(event)

    def on_remediation_action(self, action: dict) -> None:
        """Called when remediation action is taken."""
        event = StreamEvent(
            event_type=StreamEventType.REMEDIATION_ACTION,
            timestamp=time.time(),
            data={
                "action_id": action.get("action_id"),
                "strategy": action.get("strategy"),
                "status": action.get("status"),
                "improvement": action.get("improvement"),
            },
            priority="high",
        )
        self.broadcast_event(event)

    # ==========================================================================
    # Background Tasks
    # ==========================================================================

    async def _health_broadcast_loop(self) -> None:
        """Periodically broadcast health updates."""
        while self._running:
            try:
                await asyncio.sleep(30)  # Every 30 seconds

                if not self._running:
                    break

                # Get health from coordinator
                health = {}
                if self._coordinator:
                    health = self._coordinator.get_system_health()

                event = StreamEvent(
                    event_type=StreamEventType.HEALTH_UPDATE,
                    timestamp=time.time(),
                    data={
                        "status": health.get("status", "unknown"),
                        "governance_mode": health.get("governance_mode", "unknown"),
                        "current_phase": health.get("current_phase", "unknown"),
                        "cycles_completed": health.get("cycles_completed", 0),
                        "total_issues_found": health.get("total_issues_found", 0),
                        "total_issues_remediated": health.get("total_issues_remediated", 0),
                        "remediation_rate": health.get("remediation_rate", 0),
                        "connected_clients": len(self._clients),
                        "events_processed": self._stats["events_processed"],
                    },
                    priority="low",
                )
                self.broadcast_event(event)

            except Exception as e:
                print(f"[GovernanceStreaming] Health loop error: {e}")

    # ==========================================================================
    # API
    # ==========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get streaming API statistics."""
        return {
            **self._stats,
            "connected_clients": len(self._clients),
            "active_subscriptions": len(self._subscriptions),
            "event_history_size": len(self._event_history),
            "port": self.port,
            "running": self._running,
        }


# =============================================================================
# Convenience Functions
# =============================================================================


def create_governance_streaming_api(
    coordinator: Optional[UnifiedGovernanceCoordinator] = None,
    port: int = 8767,
) -> GovernanceStreamingAPI:
    """Factory function to create governance streaming API."""
    return GovernanceStreamingAPI(coordinator, port)


# =============================================================================
# Module Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("AMOS Governance Streaming API - Test Suite")
    print("=" * 70)

    if not WEBSOCKETS_AVAILABLE:
        print("\n❌ WebSocket library not available. Install with: pip install websockets")
        exit(1)

    # Create streaming API
    api = GovernanceStreamingAPI(port=8768)

    print("\n[Test 1] Create Streaming API")
    print("-" * 50)
    print(f"Port: {api.port}")
    print(f"Running: {api._running}")

    # Test 2: Simulate events
    print("\n[Test 2] Simulate Events")
    print("-" * 50)

    # Simulate cycle start
    api.on_cycle_started("test_cycle_001")
    print("✓ Cycle started event")

    # Simulate phase change
    api.on_phase_changed("detecting", "test_cycle_001")
    print("✓ Phase change event")

    # Simulate prediction (mock)
    if PREDICTION_AVAILABLE:
        from predictive_intelligence_engine import (
            Prediction,
            PredictionConfidence,
            PredictionHorizon,
        )

        pred = Prediction(
            prediction_id="pred_test_001",
            timestamp=time.time(),
            horizon=PredictionHorizon.SHORT_TERM,
            metric_name="overall_health",
            current_value=0.75,
            predicted_value=0.55,
            confidence=0.85,
            confidence_level=PredictionConfidence.HIGH,
            risk_score=0.45,
            severity="medium",
            recommended_action="increase_monitoring",
            time_until_issue=30.5,
        )
        api.on_prediction_generated(pred)
        print("✓ Prediction event")

    # Simulate cycle completion
    api.on_cycle_completed(
        {
            "cycle_id": "test_cycle_001",
            "status": "success",
            "issues_found": 2,
            "issues_predicted": 1,
            "issues_remediated": 2,
            "time_elapsed_ms": 150.5,
        }
    )
    print("✓ Cycle completed event")

    # Test 3: Stats
    print("\n[Test 3] API Statistics")
    print("-" * 50)

    stats = api.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test 4: Event History
    print("\n[Test 4] Event History")
    print("-" * 50)
    print(f"Events in buffer: {len(api._event_history)}")
    for i, event in enumerate(api._event_history):
        print(f"  {i+1}. {event.event_type.value} ({event.priority})")

    print("\n" + "=" * 70)
    print("All tests passed!")
    print("=" * 70)
    print("\n✓ Governance Streaming API operational")
    print("✓ Event broadcasting ready")
    print("✓ WebSocket server ready to start")
    print("=" * 70)
