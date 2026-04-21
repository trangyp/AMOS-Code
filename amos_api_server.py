#!/usr/bin/env python3
"""AMOS Production API Server - Unified 6-Repo API

Real production server providing:
- Health checks
- 6-repo linking status  
- Brain cognitive functions
- WebSocket streaming

Usage:
    python3 amos_api_server.py
    uvicorn amos_api_server:app --reload
"""

from __future__ import annotations

import asyncio
import json
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# FastAPI imports
try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    print("❌ FastAPI not installed. Run: pip install fastapi uvicorn")
    FASTAPI_AVAILABLE = False
    sys.exit(1)

# AMOS imports
try:
    from amos_brain import think, get_cognitive_runtime
    from amos_unified_api import AMOS, AMOSResult
    AMOS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  AMOS import warning: {e}")
    AMOS_AVAILABLE = False

# Global state
_amos_instance: AMOS | None = None
_startup_time = datetime.now(timezone.utc)


# Pydantic models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    uptime_seconds: float
    version: str = "3.0.0"


class RepoStatus(BaseModel):
    name: str
    role: str
    path: str
    linked: bool


class RepoLinkResponse(BaseModel):
    total: int
    linked: int
    failed: int
    repos: list[RepoStatus]


class ThinkRequest(BaseModel):
    query: str
    domain: str = "general"


class ThinkResponse(BaseModel):
    success: bool
    reasoning: list[str]
    confidence: str
    law_compliant: bool
    layer: str


# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global _amos_instance
    
    # Startup
    if AMOS_AVAILABLE:
        _amos_instance = AMOS()
        result = _amos_instance.initialize()
        print(f"✅ AMOS initialized: {result.data}")
    else:
        print("⚠️  AMOS not available - running in limited mode")
    
    yield
    
    # Shutdown
    print("🛑 API server shutting down")


# Create app
app = FastAPI(
    title="AMOS Unified API",
    description="Production API for 6-repo AMOS ecosystem",
    version="3.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=dict)
async def root():
    """API info endpoint."""
    return {
        "name": "AMOS Unified API",
        "version": "3.0.0",
        "status": "operational",
        "features": ["health", "repos", "brain", "websocket"],
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    uptime = (datetime.now(timezone.utc) - _startup_time).total_seconds()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=uptime,
    )


@app.get("/repos", response_model=RepoLinkResponse)
async def get_repos():
    """Get status of all 6 linked repositories."""
    repos = [
        ("AMOS-Code", "core", "AMOS_REPOS/AMOS-Code"),
        ("AMOS-Consulting", "api_hub", "AMOS_REPOS/AMOS-Consulting"),
        ("AMOS-Claws", "operator_frontend", "AMOS_REPOS/AMOS-Claws"),
        ("AMOS-Invest", "investor_frontend", "AMOS_REPOS/AMOS-Invest"),
        ("Mailinhconect", "product_frontend", "AMOS_REPOS/Mailinhconect"),
        ("AMOS-UNIVERSE", "knowledge", "AMOS_REPOS/AMOS-UNIVERSE"),
    ]
    
    repo_list = []
    linked_count = 0
    
    for name, role, path in repos:
        repo_path = Path(path)
        exists = repo_path.exists()
        if exists:
            linked_count += 1
        repo_list.append(RepoStatus(
            name=name,
            role=role,
            path=str(repo_path.absolute()),
            linked=exists,
        ))
    
    return RepoLinkResponse(
        total=len(repos),
        linked=linked_count,
        failed=len(repos) - linked_count,
        repos=repo_list,
    )


@app.post("/brain/think", response_model=ThinkResponse)
async def brain_think(request: ThinkRequest):
    """Use AMOS brain to think/analyze."""
    if not AMOS_AVAILABLE or _amos_instance is None:
        raise HTTPException(status_code=503, detail="AMOS brain not available")
    
    result = _amos_instance.think(request.query, request.domain)
    
    return ThinkResponse(
        success=result.success,
        reasoning=result.reasoning,
        confidence=result.confidence,
        law_compliant=result.law_compliant,
        layer=result.layer,
    )


@app.get("/brain/status")
async def brain_status():
    """Get AMOS brain status."""
    if not AMOS_AVAILABLE:
        return {"available": False, "error": "AMOS not installed"}
    
    try:
        runtime = get_cognitive_runtime()
        engines = runtime.list_available_engines()
        return {
            "available": True,
            "engines": len(engines),
            "initialized": _amos_instance is not None,
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


@app.websocket("/ws/health")
async def websocket_health(websocket: WebSocket):
    """WebSocket for real-time health streaming."""
    await websocket.accept()
    try:
        while True:
            uptime = (datetime.now(timezone.utc) - _startup_time).total_seconds()
            await websocket.send_json({
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime_seconds": uptime,
            })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        print("WebSocket client disconnected")


def main():
    """Run the API server."""
    import uvicorn
    print("🚀 Starting AMOS Unified API Server")
    print("📚 API docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
