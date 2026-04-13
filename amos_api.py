#!/usr/bin/env python3
"""
AMOS Brain REST API - FastAPI-based HTTP interface.

Provides endpoints:
  GET  /          - API info and links
  GET  /health    - Health check
  GET  /status    - Brain status and capabilities
  POST /decide    - Analyze a decision with Rule of 2/4
  POST /analyze   - Deep systems analysis
  GET  /laws      - List Global Laws L1-L6
  POST /laws/check - Check text compliance
  GET  /memory    - Query reasoning history
  POST /memory/search - Search memory

Usage:
  uvicorn amos_api:app --reload
  
Interactive docs:
  http://localhost:8000/docs (Swagger UI)
  http://localhost:8000/redoc (ReDoc)
"""
from __future__ import annotations

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Any
from dataclasses import dataclass
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# AMOS brain imports
from amos_brain import get_amos_integration, GlobalLaws
from amos_brain.cookbook import (
    ArchitectureDecision,
    ProjectPlanner,
    ProblemDiagnosis,
    TechnologySelection,
    RiskAssessment,
)
from amos_brain.memory import get_brain_memory


# ── Pydantic Models ─────────────────────────────────────────────────────────

class DecideRequest(BaseModel):
    problem: str = Field(..., description="The decision or problem to analyze")
    context: dict[str, Any] = Field(default={}, description="Optional context")
    options: list[str] = Field(default=[], description="Optional options to consider")


class DecideResponse(BaseModel):
    problem: str
    rule_of_two: dict[str, Any]
    rule_of_four: dict[str, Any]
    recommendations: list[str]
    assumptions: list[str]
    uncertainties: list[str]
    processed_at: str


class AnalyzeRequest(BaseModel):
    topic: str = Field(..., description="Topic or system to analyze")
    workflow: str = Field(default="root_cause", description="Analysis workflow type")


class LawsCheckRequest(BaseModel):
    text: str = Field(..., description="Text to check for compliance")
    check_l4: bool = Field(default=True, description="Check L4 structural integrity")
    check_l5: bool = Field(default=True, description="Check L5 communication style")


class MemorySearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, ge=1, le=100)


# ── FastAPI App ────────────────────────────────────────────────────────────

app = FastAPI(
    title="AMOS Brain API",
    description="RESTful interface to AMOS cognitive architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AMOS instance
_amos = None


def get_amos():
    """Get or create AMOS brain instance."""
    global _amos
    if _amos is None:
        _amos = get_amos_integration()
    return _amos


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """API information."""
    return {
        "name": "AMOS Brain API",
        "version": "1.0.0",
        "description": "Cognitive architecture with Rule of 2 and Rule of 4",
        "links": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "status": "/status",
            "laws": "/laws",
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        amos = get_amos()
        status = amos.get_status()
        return {
            "status": "healthy" if status['initialized'] else "unhealthy",
            "brain_loaded": status['brain_loaded'],
            "engines": status['engines_count'],
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/status")
async def status():
    """Get brain status and capabilities."""
    amos = get_amos()
    s = amos.get_status()
    return {
        "initialized": s['initialized'],
        "brain_loaded": s['brain_loaded'],
        "engines_count": s['engines_count'],
        "laws_active": s['laws_active'],
        "domains_covered": s['domains_covered'],
        "laws_summary": amos.get_laws_summary(),
    }


@app.post("/decide", response_model=DecideResponse)
async def decide(request: DecideRequest):
    """
    Analyze a decision using AMOS Rule of 2 (dual perspectives) 
    and Rule of 4 (four quadrants).
    """
    amos = get_amos()
    
    result = amos.analyze_with_rules(request.problem, request.context)
    
    return DecideResponse(
        problem=request.problem,
        rule_of_two={
            "confidence": result['rule_of_two']['confidence'],
            "recommendation": result['rule_of_two']['recommendation'],
        },
        rule_of_four={
            "quadrants": result['rule_of_four']['quadrants_analyzed'],
            "completeness": result['rule_of_four']['completeness_score'],
        },
        recommendations=result.get('recommendations', []),
        assumptions=result.get('assumptions', []),
        uncertainties=result.get('uncertainty_flags', []),
        processed_at=datetime.utcnow().isoformat(),
    )


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Perform deep systems analysis using cookbook workflows.
    """
    workflows = {
        "architecture": ArchitectureDecision,
        "project": ProjectPlanner,
        "diagnosis": ProblemDiagnosis,
        "technology": TechnologySelection,
        "risk": RiskAssessment,
        "root_cause": ProblemDiagnosis,
    }
    
    workflow_class = workflows.get(request.workflow, ProblemDiagnosis)
    result = workflow_class.run(request.topic)
    
    return {
        "workflow": request.workflow,
        "topic": request.topic,
        "confidence": result.confidence,
        "recommendations": result.recommendations,
        "memory_id": result.memory_id,
    }


@app.get("/laws")
async def laws():
    """List AMOS Global Laws L1-L6."""
    amos = get_amos()
    return {
        "laws": amos.get_laws_summary(),
    }


@app.post("/laws/check")
async def laws_check(request: LawsCheckRequest):
    """Check text compliance with Global Laws."""
    laws = GlobalLaws()
    issues = []
    
    if request.check_l4:
        statements = [s.strip() for s in request.text.split(".") if s.strip()]
        consistent, contradictions = laws.check_l4_integrity(statements)
        if not consistent:
            issues.extend(contradictions)
    
    if request.check_l5:
        ok, violations = laws.l5_communication_check(request.text)
        if not ok:
            issues.extend(violations)
    
    return {
        "text_preview": request.text[:100] + "..." if len(request.text) > 100 else request.text,
        "compliant": len(issues) == 0,
        "issues": issues,
        "checks_performed": ["L4" if request.check_l4 else None, "L5" if request.check_l5 else None],
    }


@app.get("/memory")
async def memory(limit: int = Query(10, ge=1, le=100)):
    """Get recent reasoning history."""
    mem = get_brain_memory()
    history = mem.get_reasoning_history(limit=limit)
    
    return {
        "count": len(history),
        "items": [
            {
                "problem": h.get('problem', 'Unknown')[:50],
                "timestamp": h.get('timestamp'),
                "tags": h.get('tags', []),
            }
            for h in history
        ],
    }


@app.post("/memory/search")
async def memory_search(request: MemorySearchRequest):
    """Search reasoning memory."""
    mem = get_brain_memory()
    results = mem.query_reasoning(request.query, limit=request.limit)
    
    return {
        "query": request.query,
        "count": len(results),
        "results": results,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
