"""Kernel API Server - FastAPI REST and WebSocket endpoints"""

import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.responses import JSONResponse

    HAVE_FASTAPI = True
except ImportError:
    HAVE_FASTAPI = False
    FastAPI = object
    WebSocket = object

from ..core.law import UniversalLawKernel
from ..core.state import UniversalStateModel
from ..events.bus import KernelEvent, get_event_bus
from ..runtime.doctor import check as doctor_check
from ..workflows import WorkflowResult, get_workflow_engine


class KernelAPI:
    """FastAPI application for kernel endpoints."""

    def __init__(self):
        self.app = (
            FastAPI(
                title="AMOS Kernel API",
                description="Kernel-first architecture REST API",
                version="7.0.0",
                lifespan=self._lifespan,
            )
            if HAVE_FASTAPI
            else None
        )
        self.workflow_engine = get_workflow_engine()
        self.event_bus = get_event_bus()
        self.active_websockets: set[WebSocket] = set()

        if self.app:
            self._setup_routes()

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        """Lifespan manager for startup/shutdown."""
        # Startup
        self.event_bus.subscribe("*", self._on_kernel_event)
        yield
        # Shutdown
        for ws in list(self.active_websockets):
            await ws.close()

    def _on_kernel_event(self, event: KernelEvent) -> None:
        """Broadcast events to WebSocket clients."""
        asyncio.create_task(self._broadcast_event(event))

    async def _broadcast_event(self, event: KernelEvent) -> None:
        """Broadcast to all connected WebSockets."""
        message = {
            "type": event.event_type,
            "source": event.source,
            "payload": event.payload,
            "timestamp": event.timestamp,
        }
        disconnected = []
        for ws in self.active_websockets:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.active_websockets.discard(ws)

    def _setup_routes(self) -> None:
        """Setup HTTP and WebSocket routes."""

        @self.app.get("/health")
        async def health() -> dict:
            """Health check endpoint."""
            status = doctor_check()
            return {
                "healthy": status.healthy,
                "score": status.health_score,
                "checks": status.checks,
            }

        @self.app.get("/version")
        async def version() -> dict:
            """Version endpoint."""
            from ... import __version__

            return {
                "version": __version__,
                "kernel": "7.0.0",
                "architecture": "kernel-first",
                "layers": ["law", "state", "interaction", "deterministic", "observe", "repair"],
            }

        @self.app.post("/workflow")
        async def execute_workflow(request: dict) -> dict:
            """Execute workflow through kernel."""
            workflow_id = request.get("id", "api-workflow")
            raw_input = request.get("input", {})
            validate_laws = request.get("validate_laws", True)

            result = self.workflow_engine.execute(
                workflow_id=workflow_id,
                raw_input=raw_input,
                validate_laws=validate_laws,
            )

            return self._workflow_result_to_dict(result)

        @self.app.post("/law/validate")
        async def validate_laws(request: dict) -> dict:
            """Validate laws for given input."""
            law = UniversalLawKernel()

            from ...core.law import BiologicalConstraint, QuadrantIntegrity, StabilityConstraint

            bio = request.get("biological", {})
            load = sum(v for v in bio.values() if isinstance(v, (int, float)))

            result = law.validate_invariants(
                contradictions=request.get("contradictions", 0),
                has_internal=bool(request.get("internal")),
                has_external=bool(request.get("external")),
                has_feedback=request.get("feedback", True),
                stability=StabilityConstraint(0.1, 0.2),
                bio=BiologicalConstraint(load, 100.0),
                quadrants=QuadrantIntegrity(1.0, 1.0, 1.0, 1.0),
                communication_text=request.get("text", ""),
            )

            return {
                "passed": result.passed,
                "healthy": result.healthy,
                "collapse_risk": result.collapse_risk,
                "results": [
                    {"name": r.name, "passed": r.passed, "score": r.score} for r in result.results
                ],
            }

        @self.app.get("/state")
        async def get_state() -> dict:
            """Get current kernel state model info."""
            model = UniversalStateModel()
            return {
                "model": "UniversalStateModel",
                "quadrants": ["biological", "cognitive", "system", "environment"],
                "capabilities": ["normalize", "validate", "integrity"],
            }

        @self.app.get("/equations")
        async def list_equations() -> dict:
            """List all available equations."""
            from ..equations import get_executor

            executor = get_executor()
            equations = [
                {
                    "name": name,
                    "domain": executor._get_domain(name),
                }
                for name in executor._equations.keys()
            ]
            return {
                "count": len(equations),
                "equations": equations,
            }

        @self.app.post("/equation/execute")
        async def execute_equation(request: dict) -> dict:
            """Execute an equation through kernel."""
            from ..equations import get_executor

            executor = get_executor()

            name = request.get("name", "sigmoid")
            params = request.get("params", {})

            result = executor.execute(name, params)

            return {
                "equation": result.equation,
                "domain": result.domain,
                "success": result.success,
                "result": result.result,
                "law_passed": result.law_passed,
                "collapse_risk": result.collapse_risk,
                "execution_time_ms": result.execution_time_ms,
                "timestamp": result.timestamp,
            }

        @self.app.post("/equation/batch")
        async def execute_batch(request: dict) -> dict:
            """Execute multiple equations in batch."""
            from ..equations import get_executor

            executor = get_executor()

            batch = request.get("batch", [])
            results = []

            for item in batch:
                name = item.get("name", "sigmoid")
                params = item.get("params", {})
                result = executor.execute(name, params)
                results.append(
                    {
                        "equation": result.equation,
                        "success": result.success,
                        "result": result.result,
                        "law_passed": result.law_passed,
                    }
                )

            return {
                "batch_size": len(batch),
                "results": results,
            }

        @self.app.websocket("/ws")
        async def websocket_endpoint(ws: WebSocket):
            """WebSocket for real-time kernel events."""
            await ws.accept()
            self.active_websockets.add(ws)
            try:
                while True:
                    message = await ws.receive_text()
                    data = json.loads(message)

                    if data.get("action") == "ping":
                        await ws.send_json({"type": "pong", "time": datetime.now(UTC).isoformat()})
                    elif data.get("action") == "workflow":
                        result = self.workflow_engine.execute(
                            workflow_id=data.get("id", "ws-workflow"),
                            raw_input=data.get("input", {}),
                        )
                        await ws.send_json(
                            {
                                "type": "workflow_complete",
                                "result": self._workflow_result_to_dict(result),
                            }
                        )
            except WebSocketDisconnect:
                self.active_websockets.discard(ws)
            except Exception as e:
                await ws.send_json({"type": "error", "message": str(e)})
                self.active_websockets.discard(ws)

    def _workflow_result_to_dict(self, result: WorkflowResult) -> dict:
        """Convert WorkflowResult to dict."""
        return {
            "workflow_id": result.workflow_id,
            "success": result.success,
            "steps": [
                {
                    "name": s.name,
                    "status": s.status,
                    "result": s.result,
                    "started_at": s.started_at,
                    "completed_at": s.completed_at,
                }
                for s in result.steps
            ],
            "law_validation": {
                "passed": result.law_validation.passed,
                "collapse_risk": result.law_validation.collapse_risk,
            }
            if result.law_validation
            else None,
            "drift_detected": result.drift_detected,
            "repairs_proposed": result.repairs_proposed,
        }


def create_app() -> Optional[FastAPI]:
    """Factory for FastAPI app."""
    if not HAVE_FASTAPI:
        return None
    api = KernelAPI()
    return api.app


if __name__ == "__main__":
    if HAVE_FASTAPI:
        import uvicorn

        uvicorn.run(create_app(), host="0.0.0.0", port=8000)
    else:
        print("FastAPI not installed. Run: pip install fastapi uvicorn")
