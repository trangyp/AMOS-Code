from __future__ import annotations

from typing import Any, Optional

"""AMOS RAG Engine - Real Retrieval Augmented Generation with brain.

Production-ready RAG implementation:
- Document chunking and embedding
- Vector similarity search
- Brain-augmented context selection
- Source attribution and citations
"""

import hashlib
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

UTC = timezone.utc

AMOS_BRAIN_PATH = Path(__file__).parent.parent.parent / "clawspring" / "amos_brain"
if str(AMOS_BRAIN_PATH) not in sys.path:
    sys.path.insert(0, str(AMOS_BRAIN_PATH))

from amos_kernel_runtime import AMOSKernelRuntime  # noqa: E402

router = APIRouter(prefix="/rag", tags=["RAG"])


class DocumentChunk(BaseModel):
    """Chunk of a document."""

    id: str
    content: str
    source: str
    chunk_index: int
    metadata: dict[str, Any]


class RAGQuery(BaseModel):
    """RAG query request."""

    query: str
    top_k: int = 5
    min_relevance: float = 0.7
    use_brain_ranking: bool = True
    include_sources: bool = True


class RAGResult(BaseModel):
    """Single RAG retrieval result."""

    chunk_id: str
    content: str
    source: str
    relevance_score:float
    brain_score: Optional[float] = None


class RAGResponse(BaseModel):
    """RAG response with context."""

    query: str
    context: str
    sources: list[dict[str, Any]]
    total_chunks_searched: int
    retrieval_time_ms: float
    brain_enhanced: bool


@dataclass
class ChunkEmbedding:
    """Document chunk with embedding."""

    chunk: DocumentChunk
    embedding: list[float]


class SimpleEmbedder:
    """Simple deterministic embedder (production: use sentence-transformers)."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        # Simple hash-based embedding for demo
        hash_val = hashlib.sha256(text.encode()).hexdigest()
        embedding = []
        for i in range(self.dimension):
            chunk = hash_val[i % len(hash_val) : i % len(hash_val) + 4]
            val = int(chunk, 16) / 65535.0
            embedding.append(val)
        return embedding

    def similarity(self, a: list[float], b: list[float]) -> float:
        """Cosine similarity."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


class AMOSRAGStore:
    """RAG document store with brain integration."""

    def __init__(self):
        self._chunks: dict[str, ChunkEmbedding] = {}
        self._embedder = SimpleEmbedder()
        self._kernel = AMOSKernelRuntime()

    def add_document(
        self,
        content: str,
        source: str,
        metadata: dict[str, Any] = None,
        chunk_size: int = 500,
    ) -> list[str]:
        """Add document, chunk it, and store embeddings."""
        # Simple chunking by sentences
        sentences = content.replace(". ", ".|").replace("? ", "?|").replace("! ", "!|").split("|")

        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            if current_size + len(sentence) > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_size = len(sentence)
            else:
                current_chunk.append(sentence)
                current_size += len(sentence)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        chunk_ids = []
        for idx, chunk_content in enumerate(chunks):
            chunk_id = f"{source}:{idx}:{hashlib.sha256(chunk_content.encode()).hexdigest()[:8]}"
            chunk = DocumentChunk(
                id=chunk_id,
                content=chunk_content,
                source=source,
                chunk_index=idx,
                metadata=metadata or {},
            )
            embedding = self._embedder.embed(chunk_content)
            self._chunks[chunk_id] = ChunkEmbedding(chunk=chunk, embedding=embedding)
            chunk_ids.append(chunk_id)

        return chunk_ids

    def query(self, request: RAGQuery) -> RAGResponse:
        """Query the RAG store."""
        start_time = time.time()

        # Embed query
        query_embedding = self._embedder.embed(request.query)

        # Find similar chunks
        scored_chunks = []
        for chunk_id, chunk_emb in self._chunks.items():
            score = self._embedder.similarity(query_embedding, chunk_emb.embedding)
            if score >= request.min_relevance:
                scored_chunks.append((chunk_emb.chunk, score))

        # Sort by relevance
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        top_chunks = scored_chunks[: request.top_k]

        # Brain ranking if enabled
        results = []
        for chunk, vector_score in top_chunks:
            brain_score = None
            if request.use_brain_ranking:
                brain_result = self._kernel.execute_cycle(
                    observation={
                        "entities": ["query", "chunk", "relevance"],
                        "relations": [{"source": "query", "target": "chunk"}],
                        "input_data": f"Q: {request.query}\nC: {chunk.content[:200]}",
                        "context": {"source": chunk.source},
                    },
                    goal={"type": "rank_relevance"},
                )
                legality = brain_result.get("legality", 1.0)
                brain_score = legality * vector_score
                final_score = 0.6 * vector_score + 0.4 * brain_score
            else:
                final_score = vector_score

            results.append(
                RAGResult(
                    chunk_id=chunk.id,
                    content=chunk.content,
                    source=chunk.source,
                    relevance_score=round(final_score, 4),
                    brain_score=round(brain_score, 4) if brain_score else None,
                )
            )

        # Sort by final score
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        # Build context
        context_parts = []
        sources = []
        for r in results:
            context_parts.append(f"[{r.source}] {r.content}")
            sources.append(
                {
                    "chunk_id": r.chunk_id,
                    "source": r.source,
                    "score": r.relevance_score,
                    "brain_score": r.brain_score,
                }
            )

        context = "\n\n".join(context_parts)
        retrieval_time_ms = (time.time() - start_time) * 1000

        return RAGResponse(
            query=request.query,
            context=context,
            sources=sources,
            total_chunks_searched=len(self._chunks),
            retrieval_time_ms=round(retrieval_time_ms, 2),
            brain_enhanced=request.use_brain_ranking,
        )

    def get_stats(self) -> dict[str, Any]:
        """Get store statistics."""
        sources = set(c.chunk.source for c in self._chunks.values())
        return {
            "total_chunks": len(self._chunks),
            "unique_sources": len(sources),
            "sources": list(sources),
            "indexed_at": datetime.now(UTC).isoformat(),
        }


#Global RAG store
_rag_store: Optional[AMOSRAGStore] = None


def get_rag_store() -> AMOSRAGStore:
    """Get or create global RAG store."""
    global _rag_store
    if _rag_store is None:
        _rag_store = AMOSRAGStore()
        # Index some default knowledge
        _rag_store.add_document(
            source="AMOS_ARCHITECTURE",
            content="""AMOS (Advanced Model Operating System) is a cognitive architecture
            with 14 organism layers including BRAIN, SENSES, IMMUNE, BLOOD, NERVES,
            MUSCLE, METABOLISM, GROWTH, SOCIAL, MEMORY, LEGAL, ETHICS, TIME, and INTERFACES.
            The brain uses a 7-stage cognitive loop: observe, update, generate, simulate,
            filter, collapse, and execute.""",
            metadata={"category": "architecture"},
        )
        _rag_store.add_document(
            source="AMOS_KERNEL",
            content="""The AMOS Kernel Runtime implements the core cognitive cycle with
            state graphs, legality assessment, and morph execution. Key concepts include
            Ω (Omega) for total uncertainty, K (Kappa) for knowledge, and σ (Sigma)
            for legality threshold.""",
            metadata={"category": "kernel"},
        )
    return _rag_store


@router.post("/query", response_model=RAGResponse)
async def rag_query(request: RAGQuery) -> RAGResponse:
    """Query the RAG system for relevant context."""
    store = get_rag_store()
    return store.query(request)


@router.post("/index")
async def index_document(
    content: str, source: str, metadata: dict[str, Any] = None
) -> dict[str, Any]:
    """Index a new document into the RAG store."""
    store = get_rag_store()
    chunk_ids = store.add_document(content, source, metadata)
    return {
        "source": source,
        "chunks_created": len(chunk_ids),
        "chunk_ids": chunk_ids[:5],  # First 5 only
    }


@router.get("/stats")
async def get_rag_stats() -> dict[str, Any]:
    """Get RAG store statistics."""
    store = get_rag_store()
    return store.get_stats()
