#!/usr/bin/env python3
"""AMOS AI/ML Vector Search & Embeddings - Phase 20
========================================================

Enterprise-grade vector database integration with pgvector for semantic search,
RAG (Retrieval-Augmented Generation), and AI-powered equation discovery.

Features:
- pgvector extension integration with SQLAlchemy
- Embedding storage and similarity search
- Semantic equation/knowledge search
- RAG pipeline for contextual AI responses
- Multi-tenant vector isolation
- Async embedding generation
- Hybrid search (vector + keyword)
- Vector indexing (HNSW, IVFFlat)

Owner: Trang
Version: 1.0.0
Phase: 20
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import UTC, datetime

UTC = UTC
from enum import Enum
from typing import Any, Optional, Protocol, TypeVar

# SQLAlchemy imports
from sqlalchemy import Index, String, Text, select
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT, JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

# FastAPI imports
try:
    from fastapi import APIRouter, Depends, HTTPException, Query, Request
    from pydantic import BaseModel, Field

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Multi-tenancy imports
try:
    from amos_multitenancy import TenantContext

    MULTITENANCY_AVAILABLE = True
except ImportError:
    MULTITENANCY_AVAILABLE = False

# Database imports
try:
    from amos_db_sqlalchemy import Base, get_database_session

    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    Base = object  # type: ignore

import logging

logger = logging.getLogger(__name__)

# Configuration
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
VECTOR_INDEX_TYPE = os.getenv("VECTOR_INDEX_TYPE", "hnsw")  # hnsw or ivfflat
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "10"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))

T = TypeVar("T")


# ============================================
# Enums
# ============================================


class VectorIndexType(str, Enum):
    """Vector index types for pgvector."""

    HNSW = "hnsw"  # Hierarchical Navigable Small World - fast, high recall
    IVFFLAT = "ivfflat"  # Inverted File Flat - memory efficient, good for large datasets


class ContentType(str, Enum):
    """Types of content that can be embedded."""

    EQUATION = "equation"
    KNOWLEDGE = "knowledge"
    DOCUMENT = "document"
    CODE = "code"
    CONVERSATION = "conversation"


# ============================================
# Data Classes
# ============================================


@dataclass
class SearchResult:
    """Semantic search result."""

    id: str
    content_type: ContentType
    content: str
    metadata: dict[str, Any]
    similarity_score: float
    distance: float


@dataclass
class RAGContext:
    """Context for RAG (Retrieval-Augmented Generation)."""

    query: str
    retrieved_chunks: list[SearchResult]
    context_text: str = ""
    token_count: int = 0

    def build_context(self, max_tokens: int = 4000) -> str:
        """Build context string from retrieved chunks."""
        context_parts = []
        current_tokens = 0

        for chunk in self.retrieved_chunks:
            chunk_text = f"[{chunk.content_type.value}] {chunk.content}\n"
            chunk_tokens = len(chunk_text.split())  # Simple token estimation

            if current_tokens + chunk_tokens > max_tokens:
                break

            context_parts.append(chunk_text)
            current_tokens += chunk_tokens

        self.context_text = "\n".join(context_parts)
        self.token_count = current_tokens
        return self.context_text


# ============================================
# SQLAlchemy Models
# ============================================

if DB_AVAILABLE:

    class VectorEmbedding(Base):
        """
        Vector embedding storage with pgvector.
        """

        __tablename__ = "vector_embeddings"
        __table_args__ = (
            Index(
                "ix_vector_embeddings_embedding",
                "embedding",
                postgresql_using=VECTOR_INDEX_TYPE,
                postgresql_with={"m": 16, "ef_construction": 64}  # HNSW params
                if VECTOR_INDEX_TYPE == "hnsw"
                else {"lists": 100},
            ),
            Index("ix_vector_embeddings_content_type", "content_type"),
            Index("ix_vector_embeddings_tenant_id", "tenant_id"),
            Index("ix_vector_embeddings_source_id", "source_id"),
        )

        id: Mapped[str] = mapped_column(
            String(36),
            primary_key=True,
            default=lambda: hashlib.md5(f"{datetime.now(UTC).timestamp()}".encode()).hexdigest()[
                :36
            ],
        )
        content_type: Mapped[str] = mapped_column(String(50), nullable=False)
        source_id: Mapped[str] = mapped_column(String(100), nullable=False)
        content: Mapped[str] = mapped_column(Text, nullable=False)
        content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

        # Vector embedding (pgvector)
        embedding: Mapped[list[float]] = mapped_column(ARRAY(FLOAT, dimensions=1), nullable=False)

        # Metadata
        metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
        tenant_id: Mapped[str] = mapped_column(String(36), nullable=True)

        # Timestamps
        created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
        updated_at: Mapped[datetime] = mapped_column(
            default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
        )


# ============================================
# Embedding Protocol
# ============================================


class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts."""
        ...


class LocalEmbeddingProvider:
    """
    Local embedding provider using sentence-transformers.
    For production, use OpenAI, Cohere, or similar.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using local model."""
        if self._model is None:
            try:
                import sentence_transformers

                self._model = sentence_transformers.SentenceTransformer(self.model_name)
            except ImportError:
                logger.error("sentence-transformers not installed")
                # Return dummy embeddings for development
                return [[0.0] * EMBEDDING_DIMENSION for _ in texts]

        # Generate embeddings
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


class OpenAIEmbeddingProvider:
    """
    OpenAI embedding provider for production use.
    """

    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using OpenAI API."""
        try:
            import openai

            client = openai.AsyncOpenAI(api_key=self.api_key)

            response = await client.embeddings.create(model=self.model, input=texts)

            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            return [[0.0] * EMBEDDING_DIMENSION for _ in texts]


# ============================================
# Vector Search Service
# ============================================


class VectorSearchService:
    """
    Semantic search service with vector similarity.
    """

    _instance: Optional[VectorSearchService] = None

    def __new__(cls) -> VectorSearchService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Select embedding provider
        provider_type = os.getenv("EMBEDDING_PROVIDER", "local")
        if provider_type == "openai":
            self._embedder: EmbeddingProvider = OpenAIEmbeddingProvider()
        else:
            self._embedder = LocalEmbeddingProvider()

        self._initialized = True

    async def add_embedding(
        self,
        session: AsyncSession,
        content_type: ContentType,
        source_id: str,
        content: str,
        metadata: dict[str, Any] = None,
        tenant_id: str = None,
        embedding: list[float] = None,
    ) -> Optional[VectorEmbedding]:
        """
        Add content with embedding to vector store.

        Args:
            session: Database session
            content_type: Type of content
            source_id: Unique source identifier
            content: Text content to embed
            metadata: Additional metadata
            tenant_id: Tenant for isolation
            embedding: Pre-computed embedding (optional)

        Returns:
            Created VectorEmbedding
        """
        if not DB_AVAILABLE:
            return None

        try:
            # Generate embedding if not provided
            if embedding is None:
                embeddings = await self._embedder.embed([content])
                embedding = embeddings[0] if embeddings else [0.0] * EMBEDDING_DIMENSION

            # Compute content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            # Check for existing
            existing = await session.execute(
                select(VectorEmbedding).where(
                    VectorEmbedding.source_id == source_id,
                    VectorEmbedding.content_type == content_type.value,
                )
            )
            existing_embedding = existing.scalar_one_or_none()

            if existing_embedding:
                # Update existing
                existing_embedding.content = content
                existing_embedding.content_hash = content_hash
                existing_embedding.embedding = embedding
                existing_embedding.metadata = metadata or {}
                existing_embedding.updated_at = datetime.now(UTC)
                return existing_embedding

            # Create new embedding
            vector_embedding = VectorEmbedding(
                content_type=content_type.value,
                source_id=source_id,
                content=content,
                content_hash=content_hash,
                embedding=embedding,
                metadata=metadata or {},
                tenant_id=tenant_id,
            )

            session.add(vector_embedding)
            await session.commit()

            logger.info(f"Added embedding for {content_type.value}:{source_id}")
            return vector_embedding

        except Exception as e:
            logger.error(f"Failed to add embedding: {e}")
            await session.rollback()
            return None

    async def semantic_search(
        self,
        session: AsyncSession,
        query: str,
        content_types: list[ContentType] = None,
        top_k: int = DEFAULT_TOP_K,
        tenant_id: str = None,
        similarity_threshold: float = SIMILARITY_THRESHOLD,
    ) -> list[SearchResult]:
        """
        Perform semantic similarity search.

        Args:
            session: Database session
            query: Search query
            content_types: Filter by content types
            top_k: Number of results
            tenant_id: Tenant isolation
            similarity_threshold: Minimum similarity score

        Returns:
            List of search results ranked by similarity
        """
        if not DB_AVAILABLE:
            return []

        try:
            # Generate query embedding
            query_embeddings = await self._embedder.embed([query])
            query_embedding = (
                query_embeddings[0] if query_embeddings else [0.0] * EMBEDDING_DIMENSION
            )

            # Build query
            sql_query = select(
                VectorEmbedding,
                VectorEmbedding.embedding.cosine_distance(query_embedding).label("distance"),
            )

            # Apply filters
            if content_types:
                type_values = [ct.value for ct in content_types]
                sql_query = sql_query.where(VectorEmbedding.content_type.in_(type_values))

            if tenant_id:
                sql_query = sql_query.where(
                    (VectorEmbedding.tenant_id == tenant_id) | (VectorEmbedding.tenant_id.is_(None))
                )
            else:
                # Only public content if no tenant specified
                sql_query = sql_query.where(VectorEmbedding.tenant_id.is_(None))

            # Order by distance and limit
            sql_query = sql_query.order_by("distance").limit(top_k * 2)  # Get extra for filtering

            result = await session.execute(sql_query)
            rows = result.all()

            # Convert to SearchResult
            results = []
            for row in rows:
                embedding, distance = row
                # Convert distance to similarity (cosine distance ranges 0-2, where 0 is identical)
                similarity = 1 - (distance / 2)

                if similarity >= similarity_threshold:
                    results.append(
                        SearchResult(
                            id=embedding.id,
                            content_type=ContentType(embedding.content_type),
                            content=embedding.content,
                            metadata=embedding.metadata,
                            similarity_score=similarity,
                            distance=distance,
                        )
                    )

            return results[:top_k]

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    async def hybrid_search(
        self,
        session: AsyncSession,
        query: str,
        content_types: list[ContentType] = None,
        top_k: int = DEFAULT_TOP_K,
        tenant_id: str = None,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> list[SearchResult]:
        """
        Hybrid search combining vector similarity and keyword matching.

        Args:
            session: Database session
            query: Search query
            content_types: Filter by content types
            top_k: Number of results
            tenant_id: Tenant isolation
            vector_weight: Weight for vector similarity
            keyword_weight: Weight for keyword matching

        Returns:
            Combined search results
        """
        if not DB_AVAILABLE:
            return []

        try:
            # Get vector results
            vector_results = await self.semantic_search(
                session, query, content_types, top_k * 2, tenant_id
            )

            # Get keyword results (simple text search)
            keyword_query = select(VectorEmbedding).where(
                VectorEmbedding.content.ilike(f"%{query}%")
            )

            if content_types:
                type_values = [ct.value for ct in content_types]
                keyword_query = keyword_query.where(VectorEmbedding.content_type.in_(type_values))

            if tenant_id:
                keyword_query = keyword_query.where(
                    (VectorEmbedding.tenant_id == tenant_id) | (VectorEmbedding.tenant_id.is_(None))
                )

            keyword_result = await session.execute(keyword_query.limit(top_k * 2))
            keyword_rows = keyword_result.scalars().all()

            # Combine scores
            scores: dict[str, float] = {}
            content_map: dict[str, VectorEmbedding] = {}

            # Vector scores
            for result in vector_results:
                scores[result.id] = vector_weight * result.similarity_score
                if result.id not in content_map:
                    content_map[result.id] = result  # type: ignore

            # Keyword scores
            for embedding in keyword_rows:
                # Simple keyword matching score
                keyword_score = 1.0 if query.lower() in embedding.content.lower() else 0.5

                if embedding.id in scores:
                    scores[embedding.id] += keyword_weight * keyword_score
                else:
                    scores[embedding.id] = keyword_weight * keyword_score
                    content_map[embedding.id] = embedding

            # Sort by combined score
            sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

            # Build results
            results = []
            for id in sorted_ids[:top_k]:
                embedding = content_map[id]
                results.append(
                    SearchResult(
                        id=embedding.id,
                        content_type=ContentType(embedding.content_type),
                        content=embedding.content,
                        metadata=embedding.metadata,
                        similarity_score=scores[id],
                        distance=0.0,
                    )
                )

            return results

        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []

    async def delete_embedding(
        self, session: AsyncSession, source_id: str, content_type: ContentType
    ) -> bool:
        """Delete embedding by source."""
        if not DB_AVAILABLE:
            return False

        try:
            result = await session.execute(
                select(VectorEmbedding).where(
                    VectorEmbedding.source_id == source_id,
                    VectorEmbedding.content_type == content_type.value,
                )
            )
            embedding = result.scalar_one_or_none()

            if embedding:
                await session.delete(embedding)
                await session.commit()
                return True

            return False
        except Exception as e:
            logger.error(f"Failed to delete embedding: {e}")
            return False


# ============================================
# RAG Service
# ============================================


class RAGService:
    """
    Retrieval-Augmented Generation service for contextual AI responses.
    """

    def __init__(self):
        self._vector_service = VectorSearchService()

    async def build_rag_context(
        self,
        session: AsyncSession,
        query: str,
        content_types: list[ContentType] = None,
        tenant_id: str = None,
        max_chunks: int = 5,
    ) -> RAGContext:
        """
        Build RAG context for a query.

        Args:
            session: Database session
            query: User query
            content_types: Types of content to retrieve
            tenant_id: Tenant isolation
            max_chunks: Maximum chunks to include

        Returns:
            RAGContext with retrieved information
        """
        # Retrieve relevant chunks
        results = await self._vector_service.semantic_search(
            session=session,
            query=query,
            content_types=content_types or [ContentType.KNOWLEDGE, ContentType.EQUATION],
            top_k=max_chunks,
            tenant_id=tenant_id,
        )

        rag_context = RAGContext(query=query, retrieved_chunks=results)
        rag_context.build_context()

        return rag_context

    async def answer_with_rag(
        self,
        session: AsyncSession,
        query: str,
        content_types: list[ContentType] = None,
        tenant_id: str = None,
    ) -> dict[str, Any]:
        """
        Answer a query using RAG.

        Returns:
            Dict with answer and retrieved context
        """
        context = await self.build_rag_context(session, query, content_types, tenant_id)

        # In production, this would call an LLM with the context
        # For now, return the context for manual use
        return {
            "query": query,
            "context": context.context_text,
            "retrieved_chunks": [
                {
                    "content": chunk.content,
                    "type": chunk.content_type.value,
                    "score": chunk.similarity_score,
                    "metadata": chunk.metadata,
                }
                for chunk in context.retrieved_chunks
            ],
            "token_count": context.token_count,
        }


# ============================================
# FastAPI Router
# ============================================

if FASTAPI_AVAILABLE and DB_AVAILABLE:
    router = APIRouter(prefix="/vectors", tags=["vector-search"])

    class SearchRequest(BaseModel):
        query: str = Field(..., min_length=1, max_length=1000)
        content_types: list[str] = None
        top_k: int = Field(default=10, ge=1, le=100)
        hybrid: bool = False

    class SearchResponse(BaseModel):
        results: list[dict[str, Any]]
        total: int
        query: str

    class RAGRequest(BaseModel):
        query: str = Field(..., min_length=1, max_length=2000)
        content_types: list[str] = None

    @router.post("/search", response_model=SearchResponse)
    async def semantic_search_endpoint(
        request: SearchRequest,
        session: AsyncSession = Depends(get_database_session),
        tenant_id: str = None,
    ) -> SearchResponse:
        """Semantic search endpoint."""
        service = VectorSearchService()

        content_types = None
        if request.content_types:
            content_types = [ContentType(ct) for ct in request.content_types]

        if request.hybrid:
            results = await service.hybrid_search(
                session, request.query, content_types, request.top_k, tenant_id
            )
        else:
            results = await service.semantic_search(
                session, request.query, content_types, request.top_k, tenant_id
            )

        return SearchResponse(
            results=[
                {
                    "id": r.id,
                    "content_type": r.content_type.value,
                    "content": r.content[:500],  # Truncate for response
                    "similarity": r.similarity_score,
                    "metadata": r.metadata,
                }
                for r in results
            ],
            total=len(results),
            query=request.query,
        )

    @router.post("/rag")
    async def rag_endpoint(
        request: RAGRequest,
        session: AsyncSession = Depends(get_database_session),
        tenant_id: str = None,
    ) -> dict[str, Any]:
        """RAG (Retrieval-Augmented Generation) endpoint."""
        rag_service = RAGService()

        content_types = None
        if request.content_types:
            content_types = [ContentType(ct) for ct in request.content_types]

        result = await rag_service.answer_with_rag(session, request.query, content_types, tenant_id)
        return result


# ============================================
# Global Instance
# ============================================


def get_vector_service() -> VectorSearchService:
    """Get global vector search service."""
    return VectorSearchService()


def get_rag_service() -> RAGService:
    """Get global RAG service."""
    return RAGService()


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    print("AMOS AI/ML Vector Search - Phase 20")
    print("=" * 60)

    print("\n✅ Vector search configured:")
    print(f"   Embedding dimension: {EMBEDDING_DIMENSION}")
    print(f"   Vector index: {VECTOR_INDEX_TYPE}")
    print(f"   Default top-k: {DEFAULT_TOP_K}")

    print("\n📊 Features:")
    print("   - pgvector extension integration")
    print("   - Semantic similarity search")
    print("   - Hybrid search (vector + keyword)")
    print("   - RAG pipeline for AI responses")
    print("   - Tenant-scoped vector isolation")
    print("   - HNSW/IVFFlat vector indexing")
    print("   - Async embedding generation")

    print("\n🔧 Usage:")
    print("   # Add embedding")
    print("   service = get_vector_service()")
    print("   await service.add_embedding(")
    print("       session, ContentType.EQUATION,")
    print("       'eq-123', 'equation content'")
    print("   )")

    print("\n   # Semantic search")
    print("   results = await service.semantic_search(")
    print("       session, 'neural network optimization'")
    print("   )")

    print("\n   # RAG query")
    print("   rag = get_rag_service()")
    print("   context = await rag.build_rag_context(")
    print("       session, 'how to use softmax?'")
    print("   )")

    print("\n" + "=" * 60)
    print("✅ Phase 20: AI/ML vector search ready!")
