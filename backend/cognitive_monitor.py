from __future__ import annotations

from typing import Any, Optional

"""AMOS Real-Time Cognitive Monitor

Streams live brain activity, kernel state, and cognitive metrics via WebSocket.
Connects to actual working brain for real-time monitoring.

Usage:
    monitor = get_cognitive_monitor()
    await monitor.start_streaming(websocket)
"""

import asyncio
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from pathlib import Path

# Paths
_AMOS_ROOT = Path(__file__).parent.parent.resolve()

from amos_brain_working import think


@dataclass
class BrainStateSnapshot:
    """Real-time brain state snapshot."""

    timestamp: str
    status: str
    legality: float
    sigma: float
    mode: str
    active_entities: list[str]
    active_relations: list[dict[str, Any]]
    cycle_count: int


@dataclass
class CognitiveMetrics:
    """Aggregated cognitive performance metrics."""

    timestamp: str
    requests_per_minute: float
    avg_legality: float
    avg_sigma: float
    success_rate: float
    mode_distribution: dict[str, int]


class CognitiveMonitor:
    """
    Real-time cognitive activity monitor.

    Streams actual brain state with configurable intervals.
    Maintains history for trend analysis.
    """

    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self._snapshots: list[BrainStateSnapshot] = []
        self._metrics_history: list[CognitiveMetrics] = []
        self._streaming = False
        self._cycle_count = 0
        self._start_time = time.time()

    async def get_current_state(self) -> BrainStateSnapshot:
        """Capture current brain state."""
        # Query brain with status check
        result = think("_monitor_status_check", {"monitor": True})

        self._cycle_count += 1

        # Extract state from kernel result if available
        kernel_result = result.get("kernel_result", {})
        state_graph = kernel_result.get("U_t", {})

        # Build snapshot
        snapshot = BrainStateSnapshot(
            timestamp=datetime.now(UTC).isoformat(),
            status=result.get("status", "UNKNOWN"),
            legality=result.get("legality", 0.0),
            sigma=result.get("sigma", 0.0),
            mode=result.get("mode", "UNKNOWN"),
            active_entities=list(state_graph.get("vertices", []))
            if isinstance(state_graph, dict)
            else [],
            active_relations=[
                {"source": k[0], "target": k[1], "props": v}
                for k, v in (
                    state_graph.get("edges", {}) if isinstance(state_graph, dict) else {}
                ).items()
            ],
            cycle_count=self._cycle_count,
        )

        # Store in history
        self._snapshots.append(snapshot)
        if len(self._snapshots) > self.history_size:
            self._snapshots.pop(0)

        return snapshot

    def compute_metrics(self, window_seconds: int = 60) -> CognitiveMetrics:
        """Compute aggregated metrics over time window."""
        now = time.time()
        cutoff = now - window_seconds

        # Filter recent snapshots
        recent = [
            s for s in self._snapshots if datetime.fromisoformat(s.timestamp).timestamp() > cutoff
        ]

        if not recent:
            return CognitiveMetrics(
                timestamp=datetime.now(UTC).isoformat(),
                requests_per_minute=0.0,
                avg_legality=0.0,
                avg_sigma=0.0,
                success_rate=0.0,
                mode_distribution={},
            )

        # Calculate metrics
        total = len(recent)
        success_count = sum(1 for s in recent if s.status == "SUCCESS")

        # Mode distribution
        modes: dict[str, int] = {}
        for s in recent:
            modes[s.mode] = modes.get(s.mode, 0) + 1

        metrics = CognitiveMetrics(
            timestamp=datetime.now(UTC).isoformat(),
            requests_per_minute=total * (60 / window_seconds),
            avg_legality=sum(s.legality for s in recent) / total,
            avg_sigma=sum(s.sigma for s in recent) / total,
            success_rate=success_count / total,
            mode_distribution=modes,
        )

        self._metrics_history.append(metrics)
        if len(self._metrics_history) > 100:
            self._metrics_history.pop(0)

        return metrics

    async def stream_state(self, websocket, interval: float = 1.0, metrics_interval: float = 10.0):
        """
        Stream brain state to WebSocket client.

        Args:
            websocket: FastAPI WebSocket connection
            interval: Seconds between state updates
            metrics_interval: Seconds between metrics updates
        """
        self._streaming = True
        last_metrics = 0.0

        try:
            while self._streaming:
                # Get current state
                state = await self.get_current_state()

                # Send state update
                await websocket.send_json({"type": "brain_state", "data": asdict(state)})

                # Send metrics periodically
                now = time.time()
                if now - last_metrics >= metrics_interval:
                    metrics = self.compute_metrics()
                    await websocket.send_json(
                        {"type": "cognitive_metrics", "data": asdict(metrics)}
                    )
                    last_metrics = now

                # Wait before next update
                await asyncio.sleep(interval)

        except Exception:
            self._streaming = False
            raise

    def stop_streaming(self):
        """Stop active streaming."""
        self._streaming = False

    def get_trend_analysis(self, minutes: int = 5) -> dict[str, Any]:
        """Analyze trends over specified period."""
        cutoff = time.time() - (minutes * 60)

        relevant = [
            s for s in self._snapshots if datetime.fromisoformat(s.timestamp).timestamp() > cutoff
        ]

        if len(relevant) < 2:
            return {"error": "Insufficient data for trend analysis"}

        # Compute trends
        legality_values = [s.legality for s in relevant]
        sigma_values = [s.sigma for s in relevant]

        return {
            "period_minutes": minutes,
            "sample_count": len(relevant),
            "legality_trend": {
                "start": legality_values[0],
                "end": legality_values[-1],
                "change": legality_values[-1] - legality_values[0],
                "avg": sum(legality_values) / len(legality_values),
                "min": min(legality_values),
                "max": max(legality_values),
            },
            "sigma_trend": {
                "start": sigma_values[0],
                "end": sigma_values[-1],
                "change": sigma_values[-1] - sigma_values[0],
                "avg": sum(sigma_values) / len(sigma_values),
                "min": min(sigma_values),
                "max": max(sigma_values),
            },
            "mode_transitions": self._count_mode_transitions(relevant),
            "overall_health": self._assess_health(relevant),
        }

    def _count_mode_transitions(self, snapshots: list[BrainStateSnapshot]) -> int:
        """Count number of mode transitions in snapshots."""
        if len(snapshots) < 2:
            return 0

        transitions = 0
        for i in range(1, len(snapshots)):
            if snapshots[i].mode != snapshots[i - 1].mode:
                transitions += 1

        return transitions

    def _assess_health(self, snapshots: list[BrainStateSnapshot]) -> str:
        """Assess overall brain health."""
        if not snapshots:
            return "unknown"

        recent = snapshots[-10:] if len(snapshots) >= 10 else snapshots

        # Check for concerning patterns
        emergency_count = sum(1 for s in recent if s.mode == "EMERGENCY")
        low_legality = sum(1 for s in recent if s.legality < 0.5)

        if emergency_count >= len(recent) * 0.5:
            return "critical"
        elif emergency_count > 0 or low_legality >= len(recent) * 0.3:
            return "degraded"
        else:
            return "healthy"

    def get_summary(self) -> dict[str, Any]:
        """Get monitor summary."""
        uptime = time.time() - self._start_time

        return {
            "uptime_seconds": uptime,
            "snapshots_collected": len(self._snapshots),
            "metrics_computed": len(self._metrics_history),
            "current_health": self._assess_health(
                self._snapshots[-100:] if self._snapshots else []
            ),
            "is_streaming": self._streaming,
            "cycle_count": self._cycle_count,
        }


# Global monitor instance
_cognitive_monitor: Optional[CognitiveMonitor] = None


def get_cognitive_monitor() -> CognitiveMonitor:
    """Get or create global cognitive monitor."""
    global _cognitive_monitor
    if _cognitive_monitor is None:
        _cognitive_monitor = CognitiveMonitor()
    return _cognitive_monitor
