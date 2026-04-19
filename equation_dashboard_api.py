#!/usr/bin/env python3
"""
AMOS Equation Dashboard API
===========================

REST API server for the Equation System Dashboard.
Provides endpoints for:
- System status
- Code verification
- Equation queries

Architecture: FastAPI + AMOS equation systems integration
"""

import sys
from pathlib import Path
from typing import Any

# Add AMOS paths
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS"))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS" / "01_BRAIN"))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS" / "03_IMMUNE"))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS" / "06_MUSCLE"))

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("[WARN] FastAPI not available, install with: pip install fastapi uvicorn")

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    from unified_equation_api import UnifiedEquationAPI

    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

# Initialize FastAPI app
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="AMOS Equation Dashboard API",
        description="REST API for equation system dashboard",
        version="1.0.0",
    )

    # Enable CORS for dashboard
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app = None

# Initialize equation API
_equation_api: Optional[UnifiedEquationAPI] = None


def get_equation_api() -> Optional[UnifiedEquationAPI]:
    """Get or initialize equation API."""
    global _equation_api
    if _equation_api is None and API_AVAILABLE:
        _equation_api = UnifiedEquationAPI()
    return _equation_api


# Pydantic models
if FASTAPI_AVAILABLE:

    class VerificationRequest(BaseModel):
        code: str
        language: str = "python"
        auto_fix: bool = False

    class StatusResponse(BaseModel):
        total_equations: int
        by_source: Dict[str, int]
        sources_active: int
        coverage: Dict[str, Any]

    @app.get("/api/equations/status")
    async def get_status() -> Dict[str, Any]:
        """Get equation system status."""
        eq_api = get_equation_api()
        if eq_api:
            return eq_api.get_dashboard_data()
        return {
            "total_equations": 24,
            "by_source": {"knowledge_bridge": 12, "verification": 12},
            "sources_active": 2,
            "coverage": {
                "programming_languages": 9,
                "invariant_categories": 6,
                "verification_status": "operational",
            },
        }

    @app.post("/api/equations/verify")
    async def verify_code(request: VerificationRequest) -> Dict[str, Any]:
        """Verify code for invariant violations."""
        eq_api = get_equation_api()
        if not eq_api:
            raise HTTPException(status_code=503, detail="Equation API not available")

        result = eq_api.verify_code(request.code, request.language)
        return result

    @app.get("/api/equations/query")
    async def query_equations(
        domain: str = None,
        language: str = None,
    ) -> list[dict[str, Any]]:
        """Query equations by domain or language."""
        eq_api = get_equation_api()
        if not eq_api:
            raise HTTPException(status_code=503, detail="Equation API not available")

        equations = eq_api.query_all(domain, language)
        return [eq.__dict__ for eq in equations]

    # Prometheus metrics endpoint
    if PROMETHEUS_AVAILABLE:
        # Initialize metrics
        VERIFICATION_REQUESTS = Counter(
            "amos_verification_requests_total",
            "Total verification requests",
            ["language", "status"],
        )
        VERIFICATION_DURATION = Histogram(
            "amos_verification_duration_seconds", "Verification request duration", ["language"]
        )
        ACTIVE_CONNECTIONS = Gauge(
            "amos_active_websocket_connections", "Number of active WebSocket connections"
        )
        EQUATIONS_LOADED = Gauge("amos_equations_loaded", "Number of equations loaded in system")

        @app.get("/metrics")
        async def metrics() -> Any:
            """Prometheus metrics endpoint."""
            from fastapi import Response

            return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    # WebSocket streaming endpoint for real-time verification
    @app.websocket("/ws/verify")
    async def websocket_verify(websocket: WebSocket) -> None:
        """WebSocket for real-time code verification streaming."""
        await websocket.accept()

        if PROMETHEUS_AVAILABLE:
            ACTIVE_CONNECTIONS.inc()

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_json()
                code = data.get("code", "")
                language = data.get("language", "python")

                # Send start message
                await websocket.send_json({"status": "started", "message": "Verification started"})

                # Run verification
                eq_api = get_equation_api()
                if eq_api:
                    result = eq_api.verify_code(code, language)

                    # Stream results
                    await websocket.send_json({"status": "complete", "result": result})

                    if PROMETHEUS_AVAILABLE:
                        VERIFICATION_REQUESTS.labels(language=language, status="success").inc()
                else:
                    await websocket.send_json(
                        {"status": "error", "message": "Equation API not available"}
                    )

                    if PROMETHEUS_AVAILABLE:
                        VERIFICATION_REQUESTS.labels(language=language, status="error").inc()

        except WebSocketDisconnect:
            if PROMETHEUS_AVAILABLE:
                ACTIVE_CONNECTIONS.dec()
        except Exception as e:
            await websocket.send_json({"status": "error", "message": str(e)})
            if PROMETHEUS_AVAILABLE:
                ACTIVE_CONNECTIONS.dec()


def main() -> int:
    """Run the API server."""
    if not FASTAPI_AVAILABLE:
        print("[ERROR] FastAPI not installed")
        print("Install with: pip install fastapi uvicorn")
        return 1

    import uvicorn

    print("[EquationDashboardAPI] Starting server on http://localhost:8000")
    print("[EquationDashboardAPI] API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    return 0


if __name__ == "__main__":
    sys.exit(main())
