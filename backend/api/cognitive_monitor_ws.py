"""AMOS Cognitive Monitor WebSocket API

Real-time brain state streaming endpoint.
Connects to working brain for live cognitive monitoring.
"""

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from backend.cognitive_monitor import get_cognitive_monitor

router = APIRouter(prefix="/cognitive-monitor", tags=["cognitive-monitor"])


class MonitorConfig(BaseModel):
    """Configuration for cognitive monitoring stream."""

    state_interval: float = 1.0  # Seconds between state updates
    metrics_interval: float = 10.0  # Seconds between metrics updates
    history_window: int = 300  # Seconds of history to analyze


@router.websocket("/ws")
async def cognitive_monitor_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time cognitive monitoring.

    Streams:
    - Brain state (status, legality, sigma, mode, entities)
    - Cognitive metrics (success rate, averages, distributions)
    - Trend analysis (5-min health assessment)

    Usage:
        ws = new WebSocket("ws://localhost:8000/api/v1/cognitive-monitor/ws")
        ws.onmessage = (e) => console.log(JSON.parse(e.data))
    """
    await websocket.accept()
    monitor = get_cognitive_monitor()
    config = MonitorConfig()

    try:
        # Send initial connection confirmation
        await websocket.send_json(
            {
                "type": "connected",
                "message": "Cognitive monitor stream started",
                "monitor_summary": monitor.get_summary(),
            }
        )

        # Start streaming
        while True:
            # Get current state
            state = await monitor.get_current_state()

            # Send state update
            await websocket.send_json(
                {
                    "type": "brain_state",
                    "timestamp": state.timestamp,
                    "data": {
                        "status": state.status,
                        "legality": state.legality,
                        "sigma": state.sigma,
                        "mode": state.mode,
                        "active_entities": state.active_entities,
                        "active_relations_count": len(state.active_relations),
                        "cycle_count": state.cycle_count,
                    },
                }
            )

            # Send metrics every metrics_interval seconds (approximate)
            if state.cycle_count % int(config.metrics_interval / config.state_interval) == 0:
                metrics = monitor.compute_metrics(window_seconds=config.history_window)
                trends = monitor.get_trend_analysis(minutes=5)

                await websocket.send_json(
                    {
                        "type": "cognitive_metrics",
                        "timestamp": metrics.timestamp,
                        "data": {
                            "requests_per_minute": metrics.requests_per_minute,
                            "avg_legality": metrics.avg_legality,
                            "avg_sigma": metrics.avg_sigma,
                            "success_rate": metrics.success_rate,
                            "mode_distribution": metrics.mode_distribution,
                            "trend_analysis": trends,
                        },
                    }
                )

            # Wait before next update
            await asyncio.sleep(config.state_interval)

    except WebSocketDisconnect:
        # Client disconnected normally
        pass
    except Exception as e:
        # Send error and close
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass  # Connection may already be closed
        raise


@router.get("/status")
async def get_monitor_status():
    """Get current cognitive monitor status."""
    monitor = get_cognitive_monitor()
    state = await monitor.get_current_state()

    return {
        "monitor": monitor.get_summary(),
        "current_state": {
            "status": state.status,
            "legality": state.legality,
            "sigma": state.sigma,
            "mode": state.mode,
            "entities": len(state.active_entities),
            "relations": len(state.active_relations),
            "cycle": state.cycle_count,
        },
        "trends": monitor.get_trend_analysis(minutes=5),
    }
