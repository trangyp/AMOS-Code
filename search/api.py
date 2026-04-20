"""AMOS Search API Endpoints.

REST API for equation search and discovery.

Author: AMOS Search Team
Version: 2.0.0
"""

from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from search.engine import EquationSearchEngine

router = APIRouter(prefix="/search", tags=["Search"])


# Pydantic Models
class SearchRequest(BaseModel):
    """Search request body."""

    query: str = Field(default="", description="Search query string")
    tags: list[str] = Field(default=[], description="Filter by tags")
    category: str = Field(None, description="Filter by category")
    author: str = Field(None, description="Filter by author")
    verified_only: bool = Field(False, description="Only verified equations")
    difficulty_min: int = Field(None, ge=1, le=10)
    difficulty_max: int = Field(None, ge=1, le=10)
    sort_by: str = Field(
        default="relevance", regex="^(relevance|newest|oldest|name_asc|name_desc|usage|difficulty)$"
    )
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class SearchResultItem(BaseModel):
    """Single search result."""

    id: str
    score: float
    name: str
    formula: str
    description: str
    tags: list[str]
    author: str
    created_at: str
    highlights: dict[str, list[str]]


class FacetCounts(BaseModel):
    """Facet aggregation counts."""

    tags: dict[str, int]
    categories: dict[str, int]
    authors: dict[str, int]


class SearchResponseModel(BaseModel):
    """Search response."""

    total: int
    took_ms: int
    page: int
    per_page: int
    total_pages: int
    results: list[SearchResultItem]
    facets: FacetCounts
    suggestions: list[str]


class SuggestResponse(BaseModel):
    """Auto-suggest response."""

    query: str
    suggestions: list[str]


class SimilarEquationsResponse(BaseModel):
    """Similar equations response."""

    equation_id: str
    similar: list[SearchResultItem]


# Dependency injection
def get_search_engine() -> EquationSearchEngine:
    """Get search engine instance."""
    from config import settings

    return EquationSearchEngine(settings.ELASTICSEARCH_URL)


# API Endpoints
@router.post("/", response_model=SearchResponseModel)
async def search_equations(
    request: SearchRequest,
    search: EquationSearchEngine = Depends(get_search_engine),
) -> SearchResponseModel:
    """Search equations with filters and facets."""
    # Build filters
    filters: dict[str, Any] = {}
    if request.tags:
        filters["tags"] = request.tags
    if request.category:
        filters["category"] = request.category
    if request.author:
        filters["author"] = request.author
    if request.verified_only:
        filters["verified"] = True
    if request.difficulty_min:
        filters["difficulty_min"] = request.difficulty_min
    if request.difficulty_max:
        filters["difficulty_max"] = request.difficulty_max

    # Execute search
    result = await search.search(
        query=request.query,
        filters=filters if filters else None,
        sort_by=request.sort_by,
        page=request.page,
        per_page=request.per_page,
    )

    # Calculate total pages
    total_pages = (result.total + request.per_page - 1) // request.per_page

    return SearchResponseModel(
        total=result.total,
        took_ms=result.took_ms,
        page=request.page,
        per_page=request.per_page,
        total_pages=total_pages,
        results=[
            SearchResultItem(
                id=r.id,
                score=r.score,
                name=r.name,
                formula=r.formula,
                description=r.description,
                tags=r.tags,
                author=r.author,
                created_at=r.created_at.isoformat(),
                highlights=r.highlight,
            )
            for r in result.results
        ],
        facets=FacetCounts(
            tags=result.facets.get("tags", {}),
            categories=result.facets.get("categories", {}),
            authors=result.facets.get("authors", {}),
        ),
        suggestions=result.suggestions,
    )


@router.get("/", response_model=SearchResponseModel)
async def search_equations_get(
    q: str = Query(default="", description="Search query"),
    tags: list[str] = Query(default=[], description="Filter by tags"),
    category: str = Query(None, description="Filter by category"),
    author: str = Query(None, description="Filter by author"),
    verified: bool = Query(False, description="Only verified equations"),
    sort: str = Query(default="relevance", description="Sort order"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    search: EquationSearchEngine = Depends(get_search_engine),
) -> SearchResponseModel:
    """GET endpoint for equation search (browser-friendly)."""
    request = SearchRequest(
        query=q,
        tags=tags,
        category=category,
        author=author,
        verified_only=verified,
        sort_by=sort,
        page=page,
        per_page=per_page,
    )
    return await search_equations(request, search)


@router.get("/suggest", response_model=SuggestResponse)
async def get_suggestions(
    q: str = Query(..., min_length=2, description="Query prefix"),
    size: int = Query(default=5, ge=1, le=10),
    search: EquationSearchEngine = Depends(get_search_engine),
) -> SuggestResponse:
    """Get auto-complete suggestions."""
    suggestions = await search.get_suggestions(q, size)
    return SuggestResponse(query=q, suggestions=suggestions)


@router.get("/similar/{equation_id}", response_model=SimilarEquationsResponse)
async def get_similar_equations(
    equation_id: str,
    size: int = Query(default=5, ge=1, le=20),
    search: EquationSearchEngine = Depends(get_search_engine),
) -> SimilarEquationsResponse:
    """Find similar equations."""
    similar = await search.get_similar(equation_id, size)

    return SimilarEquationsResponse(
        equation_id=equation_id,
        similar=[
            SearchResultItem(
                id=r.id,
                score=r.score,
                name=r.name,
                formula=r.formula,
                description=r.description,
                tags=r.tags,
                author=r.author,
                created_at=r.created_at.isoformat(),
                highlights=r.highlight,
            )
            for r in similar
        ],
    )


@router.post("/admin/reindex")
async def reindex_all(
    search: EquationSearchEngine = Depends(get_search_engine),
) -> dict[str, Any]:
    """Admin: Reindex all equations from database."""
    # This would typically fetch from database
    # For demo, return status
    return {
        "status": "started",
        "message": "Reindex job started",
        "check_status": "Use GET /search/admin/status",
    }


@router.get("/admin/health")
async def search_health(
    search: EquationSearchEngine = Depends(get_search_engine),
) -> dict[str, Any]:
    """Check search engine health."""
    health = await search.health_check()
    return health


@router.get("/facets/tags")
async def get_popular_tags(
    limit: int = Query(default=20, ge=1, le=100),
    search: EquationSearchEngine = Depends(get_search_engine),
) -> dict[str, Any]:
    """Get popular tags with counts."""
    # Simple aggregation query
    body = {"size": 0, "aggs": {"popular_tags": {"terms": {"field": "tags", "size": limit}}}}

    response = await search.es.search(index=search.INDEX_NAME, body=body)
    buckets = response["aggregations"]["popular_tags"]["buckets"]

    return {"tags": [{"name": b["key"], "count": b["doc_count"]} for b in buckets]}
