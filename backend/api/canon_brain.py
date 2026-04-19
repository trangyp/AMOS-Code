"""Canon Brain API - REST endpoints for Canon-aware brain queries.

Provides API endpoints that integrate AMOS Canon definitions with brain
processing for domain-aware query responses.

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from amos_brain.canon_query_engine import CanonQueryEngine

router = APIRouter(prefix="/canon-brain", tags=["Canon Brain"])

# Initialize engine singleton
_canon_query_engine: CanonQueryEngine | None = None


async def get_engine() -> CanonQueryEngine:
    """Get or initialize the Canon query engine."""
    global _canon_query_engine
    if _canon_query_engine is None:
        _canon_query_engine = CanonQueryEngine()
        await _canon_query_engine.initialize()
    return _canon_query_engine


class CanonQueryRequest(BaseModel):
    """Request body for Canon-aware queries."""

    query: str
    domain: str = "general"
    context: dict[str, Any] | None = None


class CanonQueryResponse(BaseModel):
    """Response from Canon-aware query processing."""

    query: str
    domain: str
    canon_terms_used: list[str]
    canon_agents_consulted: list[str]
    canon_engines_referenced: list[str]
    response: str
    confidence: float
    metadata: dict[str, Any]


@router.get("/domains/suggest")
async def suggest_domains(
    q: str = Query(..., description="Query string to analyze"),
) -> dict[str, Any]:
    """Get domain suggestions based on query content.

    Example:
        GET /canon-brain/domains/suggest?q=brain cognitive task
    """
    engine = await get_engine()
    suggestions = engine.get_domain_suggestions(q)
    return {
        "query": q,
        "suggested_domains": suggestions,
        "count": len(suggestions),
    }


@router.post("/query", response_model=CanonQueryResponse)
async def canon_query_endpoint(
    request: CanonQueryRequest,
) -> CanonQueryResponse:
    """Process a query with Canon context enrichment.

    This endpoint integrates AMOS Canon definitions (glossary terms,
    agent registry, engine specs) into brain query processing for
    domain-aware responses.

    Example:
        POST /canon-brain/query
        {
            "query": "How do agents work?",
            "domain": "agent",
            "context": {"user_id": "123"}
        }
    """
    try:
        engine = await get_engine()
        result = await engine.query(
            query=request.query,
            domain=request.domain,
            context=request.context,
        )
        return CanonQueryResponse(
            query=result.query,
            domain=result.domain,
            canon_terms_used=result.canon_terms_used,
            canon_agents_consulted=result.canon_agents_consulted,
            canon_engines_referenced=result.canon_engines_referenced,
            response=result.response,
            confidence=result.confidence,
            metadata=result.metadata,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Canon query processing failed: {str(e)}",
        )


@router.post("/query/multi-domain")
async def multi_domain_query(
    request: CanonQueryRequest,
    domains: list[str] = Query(..., description="Domains to query"),
) -> list[CanonQueryResponse]:
    """Query across multiple domains and aggregate results.

    Example:
        POST /canon-brain/query/multi-domain?domains=brain&domains=agent
        {
            "query": "How do agents work?",
            "context": {"user_id": "123"}
        }
    """
    try:
        engine = await get_engine()
        results = await engine.multi_domain_query(
            query=request.query,
            domains=domains,
            context=request.context,
        )
        return [
            CanonQueryResponse(
                query=r.query,
                domain=r.domain,
                canon_terms_used=r.canon_terms_used,
                canon_agents_consulted=r.canon_agents_consulted,
                canon_engines_referenced=r.canon_engines_referenced,
                response=r.response,
                confidence=r.confidence,
                metadata=r.metadata,
            )
            for r in results
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Multi-domain query failed: {str(e)}",
        )


@router.get("/canon/status")
async def canon_status() -> dict[str, Any]:
    """Get Canon integration status.

    Returns information about Canon loader status, available terms,
    agents, and engines.
    """
    from amos_canon_integration import get_canon_loader
    from amos_brain.canon_bridge import get_canon_bridge

    try:
        canon_loader = get_canon_loader()
        canon_bridge = await get_canon_bridge()

        status = canon_loader.get_status()
        brain_context = canon_bridge.get_context_for_domain("brain")
        agent_context = canon_bridge.get_context_for_domain("agent")
        kernel_context = canon_bridge.get_context_for_domain("kernel")

        return {
            "canon_loaded": status.ready,
            "total_terms": status.total_terms,
            "total_agents": status.total_agents,
            "total_engines": status.total_engines,
            "loaded_files": status.loaded_files,
            "failed_files": status.failed_files,
            "domains": {
                "brain": {
                    "terms": len(brain_context.glossary_terms),
                    "agents": len(brain_context.applicable_agents),
                    "engines": len(brain_context.relevant_engines),
                },
                "agent": {
                    "terms": len(agent_context.glossary_terms),
                    "agents": len(agent_context.applicable_agents),
                    "engines": len(agent_context.relevant_engines),
                },
                "kernel": {
                    "terms": len(kernel_context.glossary_terms),
                    "agents": len(kernel_context.applicable_agents),
                    "engines": len(kernel_context.relevant_engines),
                },
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Canon status check failed: {str(e)}",
        )
