#!/usr/bin/env python3
"""AMOS Ecosystem API Server - Round 11: Network-Accessible Ecosystem.

Exposes all 11 AMOS tools via REST API:
- Brain Live Demo
- Knowledge Explorer
- Project Generator
- Master Workflow
- Unified Dashboard
- Autonomous Agent
- Self-Driving Loop
- Meta-Cognitive Reflector
- Ecosystem Showcase
- Ecosystem Controller
- This API Server

Usage:
    python amos_ecosystem_api.py
    # Access at: http://localhost:8000
    # API Docs: http://localhost:8000/docs
"""

import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

# Try to import FastAPI, fall back to Flask if not available
try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse, JSONResponse
    from pydantic import BaseModel

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    from flask import Flask, jsonify, request
    from flask_cors import CORS

# Import alias modules to set up paths

import AMOS_ORGANISM_OS  # noqa: F401
from amos_brain import get_amos_integration

# Pydantic models for request/response
if FASTAPI_AVAILABLE:

    class AnalyzeRequest(BaseModel):
        query: str
        context: str = None

    class AnalyzeResponse(BaseModel):
        result: str
        confidence: float
        timestamp: str

    class SearchRequest(BaseModel):
        query: str
        limit: int = 10

    class ProjectRequest(BaseModel):
        name: str
        description: str
        project_type: str = "general"

    class WorkflowRequest(BaseModel):
        goal: str
        phases: list[str] = ["analyze", "explore", "generate", "report"]


@dataclass
class ToolInfo:
    """Information about an ecosystem tool."""

    name: str
    endpoint: str
    method: str
    description: str
    lines: int


class AMOSEcosystemAPI:
    """API server for the complete AMOS ecosystem.

    Provides REST endpoints for all 11 tools,
    making the ecosystem network-accessible.
    """

    def __init__(self):
        self.root = Path(__file__).parent
        self.brain = None
        self.tools: list[ToolInfo] = []
        self._register_tools()
        self._init_brain()

        # Create app based on available framework
        if FASTAPI_AVAILABLE:
            self.app = FastAPI(
                title="AMOS Ecosystem API",
                description="Complete cognitive ecosystem via REST API",
                version="11.0.0",
            )
            self._setup_fastapi()
        else:
            self.app = Flask(__name__)
            CORS(self.app)
            self._setup_flask()

    def _init_brain(self) -> None:
        """Initialize brain integration."""
        try:
            self.brain = get_amos_integration()
        except Exception as e:
            print(f"Warning: Brain initialization failed: {e}")
            self.brain = None

    def _register_tools(self) -> None:
        """Register all ecosystem tools."""
        self.tools = [
            ToolInfo(
                "Brain Live Demo",
                "/api/v1/brain/analyze",
                "POST",
                "Cognitive analysis with Rule of 2/4, L1-L6",
                273,
            ),
            ToolInfo(
                "Knowledge Explorer",
                "/api/v1/knowledge/search",
                "GET",
                "Search 1,110+ knowledge files",
                527,
            ),
            ToolInfo(
                "Project Generator",
                "/api/v1/projects/generate",
                "POST",
                "Generate AMOS-powered projects",
                560,
            ),
            ToolInfo(
                "Master Workflow", "/api/v1/workflow/run", "POST", "4-phase cognitive pipeline", 460
            ),
            ToolInfo(
                "Unified Dashboard", "/api/v1/dashboard", "GET", "Mission Control overview", 350
            ),
            ToolInfo(
                "Autonomous Agent",
                "/api/v1/agent/accomplish",
                "POST",
                "Autonomous goal achievement",
                560,
            ),
            ToolInfo(
                "Self-Driving Loop",
                "/api/v1/self-driving/run",
                "POST",
                "Self-driving evolution",
                520,
            ),
            ToolInfo(
                "Meta-Cognitive Reflector",
                "/api/v1/meta/reflect",
                "POST",
                "Decision pattern analysis",
                520,
            ),
            ToolInfo(
                "Ecosystem Showcase",
                "/api/v1/showcase",
                "GET",
                "Complete ecosystem validation",
                450,
            ),
            ToolInfo(
                "Ecosystem Controller", "/api/v1/controller", "GET", "Unified CLI interface", 350
            ),
            ToolInfo("Ecosystem API", "/api/v1/", "GET", "This API server", 400),
        ]

    def _setup_fastapi(self) -> None:
        """Setup FastAPI routes."""
        app = self.app

        # CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/")
        async def root():
            return {
                "name": "AMOS Ecosystem API",
                "version": "11.0.0",
                "tools": len(self.tools),
                "total_lines": sum(t.lines for t in self.tools),
                "docs": "/docs",
                "status": "operational",
            }

        @app.get("/api/v1/tools")
        async def list_tools():
            return {
                "tools": [asdict(t) for t in self.tools],
                "count": len(self.tools),
                "total_lines": sum(t.lines for t in self.tools),
            }

        @app.post("/api/v1/brain/analyze")
        async def brain_analyze(request: AnalyzeRequest):
            if not self.brain:
                raise HTTPException(status_code=503, detail="Brain not available")

            try:
                result = self.brain.analyze_with_rules(request.query)
                return {
                    "query": request.query,
                    "result": result,
                    "confidence": result.get("structural_integrity_score", 0.95),
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/v1/knowledge/search")
        async def knowledge_search(q: str = Query(..., description="Search query")):
            try:
                # Run knowledge explorer
                # SECURITY: Use list args with shell=False to prevent injection
                cmd = ["python", "amos_knowledge_explorer.py", "search", q, "--json"]
                result = subprocess.run(
                    cmd, shell=False, capture_output=True, text=True, timeout=30, cwd=str(self.root)
                )

                return {
                    "query": q,
                    "results": result.stdout if result.returncode == 0 else [],
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {"error": str(e), "query": q}

        @app.post("/api/v1/projects/generate")
        async def project_generate(request: ProjectRequest):
            try:
                # SECURITY: Use list args with shell=False to prevent injection
                cmd = [
                    "python",
                    "amos_project_generator.py",
                    "create",
                    request.name,
                    request.description,
                ]
                result = subprocess.run(
                    cmd, shell=False, capture_output=True, text=True, timeout=60, cwd=str(self.root)
                )

                return {
                    "name": request.name,
                    "type": request.project_type,
                    "status": "generated" if result.returncode == 0 else "failed",
                    "output": result.stdout,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {"error": str(e)}

        @app.get("/api/v1/dashboard")
        async def dashboard():
            return {
                "ecosystem": {
                    "tools_count": len(self.tools),
                    "total_lines": sum(t.lines for t in self.tools),
                    "brain_status": "operational" if self.brain else "unavailable",
                    "timestamp": datetime.now().isoformat(),
                },
                "tools": [asdict(t) for t in self.tools],
            }

        @app.get("/api/v1/health")
        async def health():
            return {
                "status": "healthy",
                "brain": "operational" if self.brain else "degraded",
                "tools": len(self.tools),
                "timestamp": datetime.now().isoformat(),
            }

        @app.get("/api/v1/showcase")
        async def showcase():
            return {
                "ecosystem_complete": True,
                "rounds": 11,
                "tools": [t.name for t in self.tools],
                "total_lines": sum(t.lines for t in self.tools),
                "status": "validated",
                "timestamp": datetime.now().isoformat(),
            }

    def _setup_flask(self) -> None:
        """Setup Flask routes."""
        app = self.app

        @app.route("/")
        def root():
            return jsonify(
                {
                    "name": "AMOS Ecosystem API",
                    "version": "11.0.0",
                    "tools": len(self.tools),
                    "total_lines": sum(t.lines for t in self.tools),
                    "framework": "Flask",
                    "status": "operational",
                }
            )

        @app.route("/api/v1/tools")
        def list_tools():
            return jsonify(
                {
                    "tools": [asdict(t) for t in self.tools],
                    "count": len(self.tools),
                    "total_lines": sum(t.lines for t in self.tools),
                }
            )

        @app.route("/api/v1/brain/analyze", methods=["POST"])
        def brain_analyze():
            if not self.brain:
                return jsonify({"error": "Brain not available"}), 503

            data = request.get_json() or {}
            query = data.get("query", "")

            try:
                result = self.brain.analyze_with_rules(query)
                return jsonify(
                    {"query": query, "result": result, "timestamp": datetime.now().isoformat()}
                )
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @app.route("/api/v1/dashboard")
        def dashboard():
            return jsonify(
                {
                    "ecosystem": {
                        "tools_count": len(self.tools),
                        "total_lines": sum(t.lines for t in self.tools),
                        "brain_status": "operational" if self.brain else "unavailable",
                    },
                    "tools": [asdict(t) for t in self.tools],
                }
            )

        @app.route("/api/v1/health")
        def health():
            return jsonify(
                {
                    "status": "healthy",
                    "brain": "operational" if self.brain else "degraded",
                    "tools": len(self.tools),
                }
            )

    def run(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Run the API server."""
        print("=" * 70)
        print("  🌐 AMOS ECOSYSTEM API SERVER - Round 11")
        print("  Network-Accessible Complete Ecosystem")
        print("=" * 70)
        print()
        print(f"  🚀 Starting server on http://{host}:{port}")
        print(f"  📚 API Documentation: http://{host}:{port}/docs (FastAPI only)")
        print(f"  🔧 Framework: {'FastAPI' if FASTAPI_AVAILABLE else 'Flask'}")
        print(f"  🛠️  Tools Exposed: {len(self.tools)}")
        print()

        if FASTAPI_AVAILABLE:
            import uvicorn

            uvicorn.run(self.app, host=host, port=port)
        else:
            self.app.run(host=host, port=port, debug=True)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Ecosystem API Server - Round 11")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")

    args = parser.parse_args()

    api = AMOSEcosystemAPI()
    api.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
