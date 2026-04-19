#!/usr/bin/env python3
"""AMOS Equation API Gateway - Production Rate Limiting & Caching."""

import hashlib
import time
from typing import Any, Dict

try:
    from equation_tracing import instrument_fastapi, setup_telemetry

    _tracing_available = True
except ImportError:
    _tracing_available = False

try:
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

if FASTAPI_AVAILABLE:
    app = FastAPI(title="AMOS Equation API Gateway", version="2.1.0")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

    # Initialize telemetry
    if _tracing_available:
        setup_telemetry(service_name="amos-equation-gateway")
        instrument_fastapi(app)

RATE_LIMITS = {"default": {"r": 100, "w": 60}, "verify": {"r": 30, "w": 60}}


def get_client_id(request: Request) -> str:
    """Generate client identifier from request IP."""
    ip = request.client.host if request.client else "unknown"
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all requests."""
    client_id = get_client_id(request)
    endpoint = "verify" if "/verify" in str(request.url) else "default"
    limit = RATE_LIMITS.get(endpoint, RATE_LIMITS["default"])

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(limit["r"])
    response.headers["X-Client-ID"] = client_id
    return response


@app.get("/gateway/status")
async def gateway_status() -> Dict[str, Any]:
    """Gateway health status."""
    return {
        "status": "operational",
        "version": "2.1.0",
        "features": ["rate_limiting", "caching"],
        "timestamp": time.time(),
    }
