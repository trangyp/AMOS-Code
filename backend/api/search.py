from typing import Any, Dict, List, Optional

"""AMOS Search & Discovery API - Hybrid BM25 + Vector + RRF Search

Production-ready search endpoints with lexical, semantic,
and hybrid search capabilities.

Owner: Trang Phan
Version: 2.0.0
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.search import (
    SearchDocument,
    SearchService,
)

router = APIRouter(prefix="/search", tags=["search"])


class DocumentIndexRequest(BaseModel):
    """Request to index a document."""

    doc_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    doc_type: str = Field(default="general", description="Document type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    vector: Optional[list[float]] = Field(None, description="Optional vector embedding")


class SearchRequest(BaseModel):
    """Search request."""

    query: str = Field(..., description="Search query", min_length=1)
    mode: str = Field(default="hybrid", description="Search mode: lexical, vector, hybrid")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results")
    doc_type: Optional[str] = Field(None, description="Filter by document type")


class SearchResultResponse(BaseModel):
    """Individual search result."""

    doc_id: str
    title: str
    content_preview: str
    doc_type: str
    lexical_score: float
    vector_score: float
    hybrid_score: float
    rank: int
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    """Search response."""

    query: str
    mode: str
    total_results: int
    results: List[SearchResultResponse]
    search_time_ms: float


class IndexStatsResponse(BaseModel):
    """Index statistics."""

    total_documents: int
    by_type: Dict[str, int]
    avg_doc_length: float
    vocabulary_size: int


def get_search_service() -> SearchService:
    """Dependency injection for search service."""
    from backend.search import SearchService

    return SearchService()


@router.post("/index", status_code=status.HTTP_201_CREATED)
async def index_document_endpoint(
    request: DocumentIndexRequest, service: SearchService = Depends(get_search_service)
) -> Dict[str, Any]:
    """Index a new document for search.

    Creates searchable document with optional vector embedding.
    """
    doc = SearchDocument(
        doc_id=request.doc_id,
        title=request.title,
        content=request.content,
        doc_type=request.doc_type,
        metadata=request.metadata,
        vector=request.vector,
    )

    success = service.index_document(doc)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to index document"
        )

    return {"doc_id": request.doc_id, "indexed": True, "doc_type": request.doc_type}


@router.post("/query", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest, service: SearchService = Depends(get_search_service)
) -> SearchResponse:
    """Search documents using BM25 + Vector + RRF hybrid ranking.

    Supports three modes:
    - lexical: BM25 text matching only
    - vector: Cosine similarity only (requires vector embeddings)
    - hybrid: RRF fusion of both (default, recommended)
    """
    import time

    start = time.time()

    results = service.search(
        query=request.query, mode=request.mode, top_k=request.top_k, doc_type=request.doc_type
    )

    elapsed = (time.time() - start) * 1000

    return SearchResponse(
        query=request.query,
        mode=request.mode,
        total_results=len(results),
        results=[
            SearchResultResponse(
                doc_id=r.document.doc_id,
                title=r.document.title,
                content_preview=r.document.content[:200] + "..."
                if len(r.document.content) > 200
                else r.document.content,
                doc_type=r.document.doc_type,
                lexical_score=r.lexical_score,
                vector_score=r.vector_score,
                hybrid_score=r.hybrid_score,
                rank=i + 1,
                metadata=r.document.metadata,
            )
            for i, r in enumerate(results)
        ],
        search_time_ms=round(elapsed, 2),
    )


@router.get("/stats", response_model=IndexStatsResponse)
async def get_search_stats(
    service: SearchService = Depends(get_search_service),
) -> IndexStatsResponse:
    """Get search index statistics."""
    stats = service.get_stats()
    return IndexStatsResponse(
        total_documents=stats["total_documents"],
        by_type=stats["by_type"],
        avg_doc_length=stats["avg_doc_length"],
        vocabulary_size=stats["vocabulary_size"],
    )


@router.get("/quick", response_model=SearchResponse)
async def quick_search(
    q: str = Query(..., description="Search query"),
    mode: str = Query(default="hybrid", description="Search mode"),
    top_k: int = Query(default=10, ge=1, le=50),
    service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    """Quick search endpoint with GET method.

    Convenience endpoint for simple search queries.
    """
    start = time.time()
    results = service.search(query=q, mode=mode, top_k=top_k)
    elapsed = (time.time() - start) * 1000

    return SearchResponse(
        query=q,
        mode=mode,
        total_results=len(results),
        results=[
            SearchResultResponse(
                doc_id=r.document.doc_id,
                title=r.document.title,
                content_preview=r.document.content[:200] + "..."
                if len(r.document.content) > 200
                else r.document.content,
                doc_type=r.document.doc_type,
                lexical_score=r.lexical_score,
                vector_score=r.vector_score,
                hybrid_score=r.hybrid_score,
                rank=i + 1,
                metadata=r.document.metadata,
            )
            for i, r in enumerate(results)
        ],
        search_time_ms=round(elapsed, 2),
    )
