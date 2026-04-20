"""Fast Web Runtime API - High-precision web retrieval endpoints."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from amos_fast_web_runtime import (
    FastWebRuntime,
    SufficiencyGate,
    WebBudgets,
    get_fast_web_runtime,
    web_query,
)

router = APIRouter(prefix="/web", tags=["fast-web-runtime"])


class WebQueryRequest(BaseModel):
    """Web query request with budget controls."""

    query: str = Field(..., min_length=1, max_length=500)
    path: str = Field(default="auto", pattern="^(auto|fast|deep)$")
    max_search_queries: int = Field(default=2, ge=1, le=5)
    max_page_opens: int = Field(default=4, ge=1, le=10)
    max_deep_reads: int = Field(default=2, ge=1, le=5)
    confidence_threshold: float = Field(default=0.85, ge=0.0, le=1.0)


class WebQueryResponse(BaseModel):
    """Web query response with timing and metadata."""

    answer: str
    path: str
    time_ms: float
    pages_fetched: int
    confidence: Optional[float] = None
    sources: list[dict[str, Any]]


@router.post("/query", response_model=WebQueryResponse)
async def web_query_endpoint(request: WebQueryRequest) -> WebQueryResponse:
    """
    Execute fast web query with tight budgets.

    Equation: WebQuery → RankFast → ReadLittle → AnswerEarly → DeepenOnlyIfNeeded
    """
    budgets = WebBudgets(
        max_search_queries=request.max_search_queries,
        max_page_opens=request.max_page_opens,
        max_deep_reads=request.max_deep_reads,
    )

    sufficiency = SufficiencyGate(
        confidence_threshold=request.confidence_threshold,
    )

    runtime = FastWebRuntime(
        budgets=budgets,
        sufficiency=sufficiency,
    )

    try:
        result = await runtime.query(request.query, path=request.path)

        return WebQueryResponse(
            answer=result["answer"],
            path=result["path"],
            time_ms=result["time_ms"],
            pages_fetched=result["pages_fetched"],
            confidence=result.get("confidence"),
            sources=result["sources"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await runtime.close()


@router.get("/query")
async def web_query_get(
    q: str = Query(..., min_length=1, max_length=500),
    path: str = Query(default="auto", pattern="^(auto|fast|deep)$"),
) -> WebQueryResponse:
    """Simple GET web query."""
    try:
        result = await web_query(q, path=path)

        return WebQueryResponse(
            answer=result["answer"],
            path=result["path"],
            time_ms=result["time_ms"],
            pages_fetched=result["pages_fetched"],
            confidence=result.get("confidence"),
            sources=result["sources"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def web_runtime_health() -> dict[str, Any]:
    """Fast Web Runtime health check."""
    runtime = get_fast_web_runtime()
    return {
        "status": "healthy",
        "cache_entries": len(runtime.cache._page_cache),
        "authority_domains": len(runtime._authority_domains),
    }
