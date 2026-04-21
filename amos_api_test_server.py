#!/usr/bin/env python3
"""AMOS API Test Server - Lightweight FastAPI server for testing AMOS components."""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# AMOS imports
from amos_brain_working import think
from amos_code_quality_analyzer import CodeQualityAnalyzer
from amos_task_automation import TaskAutomation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos_api")

# Global instances
quality_analyzer = CodeQualityAnalyzer()
task_automation = TaskAutomation()


class ThinkRequest(BaseModel):
    """Request for brain thinking."""

    query: str = Field(..., description="Query to think about")
    context: Optional[dict[str, Any]] = Field(None, description="Additional context")


class ThinkResponse(BaseModel):
    """Response from brain thinking."""

    response: str
    legality: float
    mode: str
    timestamp: str


class AnalyzeRequest(BaseModel):
    """Request for code analysis."""

    file_path: str = Field(..., description="Path to file to analyze")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    components: dict[str, bool]
    timestamp: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("AMOS API Test Server starting...")
    yield
    logger.info("AMOS API Test Server shutting down...")


app = FastAPI(
    title="AMOS API Test Server",
    description="Test API for AMOS brain and automation components",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check API health."""
    components = {
        "brain": True,
        "quality_analyzer": True,
        "task_automation": True,
    }

    # Test brain
    try:
        result = think("health check")
        components["brain"] = "legality" in result
    except Exception as e:
        logger.error(f"Brain health check failed: {e}")
        components["brain"] = False

    return HealthResponse(
        status="healthy" if all(components.values()) else "degraded",
        components=components,
        timestamp=datetime.now(UTC).isoformat(),
    )


@app.post("/brain/think", response_model=ThinkResponse)
async def brain_think(request: ThinkRequest) -> ThinkResponse:
    """Use AMOS brain to think about a query."""
    try:
        result = think(request.query, request.context)

        return ThinkResponse(
            response=str(result.get("response", "")),
            legality=float(result.get("legality", 0.0)),
            mode=str(result.get("mode", "unknown")),
            timestamp=datetime.now(UTC).isoformat(),
        )
    except Exception as e:
        logger.error(f"Brain think error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/file")
async def analyze_file(request: AnalyzeRequest) -> JSONResponse:
    """Analyze a code file for quality issues."""
    try:
        report = quality_analyzer.analyze_file(request.file_path)

        return JSONResponse(
            content={
                "file_path": report.file_path,
                "total_lines": report.total_lines,
                "score": report.score,
                "issues": [
                    {
                        "line": i.line,
                        "severity": i.severity,
                        "category": i.category,
                        "message": i.message,
                    }
                    for i in report.issues
                ],
                "metrics": report.metrics,
            }
        )
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks/list")
async def list_tasks() -> JSONResponse:
    """List available automation tasks."""
    tasks = {
        "analyze_code": "Analyze a Python file for code quality issues",
        "brain_think": "Use AMOS brain to process a query",
        "file_read": "Read contents of a file",
        "file_write": "Write contents to a file",
    }

    return JSONResponse(content={"tasks": tasks})


@app.post("/tasks/execute")
async def execute_task(task_name: str, params: dict[str, Any]) -> JSONResponse:
    """Execute an automation task."""
    try:
        result = task_automation.execute(task_name, **params)

        return JSONResponse(
            content={
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "timestamp": result.timestamp,
            }
        )
    except Exception as e:
        logger.error(f"Task execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main() -> int:
    """Run the API test server."""
    import uvicorn

    print("=" * 70)
    print("AMOS API Test Server")
    print("=" * 70)
    print("\nEndpoints:")
    print("  GET  /health          - Health check")
    print("  POST /brain/think     - Brain thinking")
    print("  POST /analyze/file    - Code quality analysis")
    print("  GET  /tasks/list      - List available tasks")
    print("  POST /tasks/execute   - Execute automation task")
    print("\nDocumentation: http://localhost:8000/docs")
    print("=" * 70)

    uvicorn.run(app, host="0.0.0.0", port=8000)
    return 0


if __name__ == "__main__":
    sys.exit(main())
