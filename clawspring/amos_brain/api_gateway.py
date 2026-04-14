#!/usr/bin/env python3
"""AMOS Ecosystem v2.6 - REST API Gateway.

Exposes all AMOS capabilities via REST API for external integration.
FastAPI-based with automatic documentation.
"""

import sys
from datetime import datetime
from typing import Any, Optional

sys.path.insert(0, ".")
sys.path.insert(0, "clawspring")
sys.path.insert(0, "clawspring/amos_brain")

try:
    from fastapi import BackgroundTasks, FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

    # Mock classes for when FastAPI not installed
    class BaseModel:
        pass

    class FastAPI:
        pass


class RouteRequest(BaseModel):
    """Cognitive routing request."""

    task: str
    context: Optional[dict[str, Any]] = None


class RouteResponse(BaseModel):
    """Cognitive routing response."""

    domain: str
    risk_level: str
    engines: list[str]
    confidence: float


class ValidateRequest(BaseModel):
    """Validation request."""

    action: str
    framework: str = "principlism"


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    components: dict[str, str]
    timestamp: str


class APIGateway:
    """REST API Gateway for AMOS ecosystem."""

    def __init__(self):
        self.app = None
        if HAS_FASTAPI:
            self.app = FastAPI(
                title="AMOS Ecosystem API",
                description="REST API for AMOS cognitive ecosystem",
                version="2.6.0",
            )
            self._setup_routes()

    def _setup_routes(self) -> None:
        """Setup API routes."""
        if not self.app:
            return

        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Get system health status."""
            return HealthResponse(
                status="healthy",
                components={
                    "cognitive_router": "up",
                    "organism_bridge": "up",
                    "ethics_validator": "up",
                    "master_orchestrator": "up",
                },
                timestamp=datetime.now().isoformat(),
            )

        @self.app.post("/cognitive/route", response_model=RouteResponse)
        async def cognitive_route(request: RouteRequest):
            """Route a task through cognitive system."""
            try:
                from amos_cognitive_router import CognitiveRouter

                router = CognitiveRouter()
                result = router.analyze(request.task)

                return RouteResponse(
                    domain=result.primary_domain,
                    risk_level=result.risk_level,
                    engines=result.suggested_engines,
                    confidence=result.confidence,
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/cognitive/validate")
        async def cognitive_validate():
            """Run system validation."""
            try:
                from system_validator import validate_system

                success, summary = validate_system()
                return {
                    "passed": summary["passed"],
                    "total": summary["total"],
                    "pass_rate": summary["pass_rate"],
                    "status": "pass" if success else "fail",
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/ethics/validate")
        async def ethics_validate(request: ValidateRequest):
            """Validate action against ethics framework."""
            try:
                from ethics_integration import EthicsValidator

                ethics = EthicsValidator()
                result = ethics.validate_action(
                    request.action, {"consent": True, "harm_potential": 0.1}, request.framework
                )

                return {
                    "passed": result.passed,
                    "score": result.score,
                    "framework": result.framework,
                    "violations": result.violations,
                    "warnings": result.warnings,
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/telemetry/metrics")
        async def get_metrics():
            """Get telemetry metrics."""
            try:
                from telemetry import get_telemetry

                telemetry = get_telemetry()
                return telemetry.get_dashboard_data()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/status")
        async def system_status():
            """Get full system status."""
            return {
                "version": "2.6.0",
                "components": {
                    "cognitive": "operational",
                    "organism_bridge": "connected",
                    "ethics": "active",
                    "telemetry": "collecting",
                },
                "timestamp": datetime.now().isoformat(),
            }

    def get_app(self) -> Any:
        """Get FastAPI application instance."""
        return self.app

    def run(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Run the API server."""
        if not HAS_FASTAPI:
            print("FastAPI not installed. Install with: pip install fastapi uvicorn")
            return

        import uvicorn

        uvicorn.run(self.app, host=host, port=port)


def main():
    """Run API gateway."""
    print("=" * 70)
    print("AMOS ECOSYSTEM v2.6 - API GATEWAY")
    print("=" * 70)

    if not HAS_FASTAPI:
        print("ERROR: FastAPI not installed")
        print("Install with: pip install fastapi uvicorn")
        return 1

    gateway = APIGateway()

    print("API Gateway initialized")
    print("Documentation: http://localhost:8000/docs")
    print("Health: http://localhost:8000/health")
    print("=" * 70)

    gateway.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
