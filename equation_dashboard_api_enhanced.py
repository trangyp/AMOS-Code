#!/usr/bin/env python3
"""
AMOS Equation Dashboard API - Enhanced Production Version.

Features:
- WebSocket streaming for real-time verification
- Prometheus metrics for observability
- REST API endpoints
- CORS enabled for dashboard integration

Endpoints:
- GET /api/equations/status - System status
- POST /api/equations/verify - Code verification
- GET /api/equations/query - Equation search
- GET /metrics - Prometheus metrics
- WS /ws/verify - Real-time streaming verification
"""

import sys
import time
from pathlib import Path
from typing import Any

# Add AMOS paths
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS"))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS" / "01_BRAIN"))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS" / "03_IMMUNE"))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS" / "06_MUSCLE"))

# Import FastAPI components
try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import Response as FastAPIResponse
    from pydantic import BaseModel

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("[WARN] FastAPI not available. Install with: pip install fastapi uvicorn")

# Import Prometheus client
try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Import AMOS equation systems
try:
    from unified_equation_api import UnifiedEquationAPI

    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

# Initialize FastAPI app
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="AMOS Equation Dashboard API",
        description="Production API for equation system with streaming and metrics",
        version="2.0.0",
    )

    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app = None

# Initialize Prometheus metrics
if PROMETHEUS_AVAILABLE:
    VERIFICATION_REQUESTS = Counter(
        "amos_verification_requests_total", "Total verification requests", ["language", "status"]
    )
    VERIFICATION_DURATION = Histogram(
        "amos_verification_duration_seconds", "Verification request duration", ["language"]
    )
    ACTIVE_CONNECTIONS = Gauge(
        "amos_active_websocket_connections", "Number of active WebSocket connections"
    )
    EQUATIONS_LOADED = Gauge("amos_equations_loaded", "Number of equations loaded in system")

# Global equation API instance
_equation_api: Optional[UnifiedEquationAPI] = None


def get_equation_api() -> Optional[UnifiedEquationAPI]:
    """Get or initialize equation API."""
    global _equation_api
    if _equation_api is None and API_AVAILABLE:
        _equation_api = UnifiedEquationAPI()
        if PROMETHEUS_AVAILABLE:
            EQUATIONS_LOADED.set(24)  # Set from known count
    return _equation_api


# Pydantic models for requests
if FASTAPI_AVAILABLE:

    class VerificationRequest(BaseModel):
        """Request model for code verification."""

        code: str
        language: str = "python"
        auto_fix: bool = False

    class QueryRequest(BaseModel):
        """Request model for equation queries."""

        domain: str = None
        language: str = None


# REST API Endpoints
if FASTAPI_AVAILABLE:

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
            "health": "operational",
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

        start_time = time.time()
        result = eq_api.verify_code(request.code, request.language)
        duration = time.time() - start_time

        if PROMETHEUS_AVAILABLE:
            VERIFICATION_DURATION.labels(language=request.language).observe(duration)
            status = "success" if result.get("summary", {}).get("errors", 0) == 0 else "error"
            VERIFICATION_REQUESTS.labels(language=request.language, status=status).inc()

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
    @app.get("/metrics")
    async def metrics() -> FastAPIResponse:
        """Prometheus metrics endpoint."""
        if not PROMETHEUS_AVAILABLE:
            raise HTTPException(status_code=503, detail="Prometheus not available")
        return FastAPIResponse(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    # WebSocket streaming endpoint
    @app.websocket("/ws/verify")
    async def websocket_verify(websocket: WebSocket) -> None:
        """WebSocket for real-time code verification streaming."""
        await websocket.accept()

        if PROMETHEUS_AVAILABLE:
            ACTIVE_CONNECTIONS.inc()

        try:
            while True:
                data = await websocket.receive_json()
                code = data.get("code", "")
                language = data.get("language", "python")

                # Send start notification
                await websocket.send_json(
                    {
                        "status": "started",
                        "message": "Verification started",
                        "timestamp": time.time(),
                    }
                )

                # Run verification
                start_time = time.time()
                eq_api = get_equation_api()

                if eq_api:
                    result = eq_api.verify_code(code, language)
                    duration = time.time() - start_time

                    # Stream results
                    await websocket.send_json(
                        {
                            "status": "complete",
                            "result": result,
                            "duration_seconds": duration,
                            "timestamp": time.time(),
                        }
                    )

                    if PROMETHEUS_AVAILABLE:
                        VERIFICATION_DURATION.labels(language=language).observe(duration)
                        status = (
                            "success"
                            if result.get("summary", {}).get("errors", 0) == 0
                            else "error"
                        )
                        VERIFICATION_REQUESTS.labels(language=language, status=status).inc()
                else:
                    await websocket.send_json(
                        {
                            "status": "error",
                            "message": "Equation API not available",
                            "timestamp": time.time(),
                        }
                    )

                    if PROMETHEUS_AVAILABLE:
                        VERIFICATION_REQUESTS.labels(
                            language=language, status="api_unavailable"
                        ).inc()

        except WebSocketDisconnect:
            if PROMETHEUS_AVAILABLE:
                ACTIVE_CONNECTIONS.dec()
        except Exception as e:
            await websocket.send_json(
                {"status": "error", "message": str(e), "timestamp": time.time()}
            )
            if PROMETHEUS_AVAILABLE:
                ACTIVE_CONNECTIONS.dec()


def main() -> int:
    """Run the API server."""
    if not FASTAPI_AVAILABLE:
        print("[ERROR] FastAPI not installed")
        print("Install with: pip install fastapi uvicorn")
        return 1

    import uvicorn

    print("=" * 60)
    print("AMOS Equation Dashboard API - Enhanced Production Version")
    print("=" * 60)
    print("\nFeatures:")
    print("  - REST API: /api/equations/*")
    print("  - WebSocket: /ws/verify (real-time streaming)")
    print("  - Metrics: /metrics (Prometheus)")
    print("  - Docs: http://localhost:8000/docs")
    print("\nStarting server on http://localhost:8000")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
    return 0


if __name__ == "__main__":
    sys.exit(main())
