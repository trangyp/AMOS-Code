"""AMOS Vector Memory System - Semantic Search for AI Agent Memory.

Provides vector-based semantic search capabilities for the AMOS SuperBrain,
enabling RAG (Retrieval-Augmented Generation) and similarity-based memory retrieval.

Features:
- ChromaDB vector database integration
- Sentence-transformer embeddings
- Semantic search over memory entries
- Metadata filtering and hybrid search
- Configurable similarity thresholds

Architecture:
- L4: Vector Store (ChromaDB collections)
- L3: Embedding Service (sentence-transformers)
- L2: Search API (semantic + metadata hybrid)
- L1: Integration Layer (Memory Architecture bridge)

Usage:
    from amos_brain.vector_memory import get_vector_memory

    # Store with embedding
    vm = get_vector_memory()
    vm.store("doc-001", "Python is a programming language",
             metadata={"type": "knowledge", "topic": "programming"})

    # Semantic search
    results = vm.search("What language do programmers use?", k=5)

    # Hybrid search with metadata filter
    results = vm.search("AI frameworks",
                       filter={"type": "knowledge"}, k=3)

Dependencies:
    pip install chromadb sentence-transformers

References:
- ChromaDB 2025 best practices for AI applications
- Sentence-transformers for semantic embeddings
- RAG (Retrieval-Augmented Generation) patterns
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# Data Models
# ============================================================================


@dataclass
class VectorMemoryEntry:
    """A vector memory entry with embedding and metadata.

    Attributes:
        id: Unique identifier
        content: Text content to be embedded
        embedding: Vector embedding (optional, computed if not provided)
        metadata: Additional metadata
        timestamp: Entry timestamp
        score: Similarity score (set after search)
    """

    id: str
    content: str
    embedding: list[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    score: float = 0.0


@dataclass
class SearchResult:
    """Result from vector memory search.

    Attributes:
        entry: The matched entry
        score: Similarity score (0-1, higher is better)
        distance: Distance metric (lower is better)
    """

    entry: VectorMemoryEntry
    score: float
    distance: float


# ============================================================================
# Vector Memory Service
# ============================================================================


class VectorMemoryService:
    """Vector memory service with semantic search capabilities.

    Provides:
    - Text embedding using sentence-transformers
    - Vector storage using ChromaDB
    - Semantic search with metadata filtering
    - Hybrid search combining vector + keyword
    """

    def __init__(
        self,
        collection_name: str = "amos_memory",
        embedding_model: str = "all-MiniLM-L6-v2",
        persist_directory: str = None,
        similarity_threshold: float = 0.7,
    ):
        """Initialize vector memory service.

        Args:
            collection_name: ChromaDB collection name
            embedding_model: Sentence-transformer model name
            persist_directory: Directory for ChromaDB persistence
            similarity_threshold: Minimum similarity score (0-1)
        """
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        self.similarity_threshold = similarity_threshold

        # Set default persistence directory
        if persist_directory is None:
            persist_directory = str(Path.home() / ".amos" / "vector_memory")
        self.persist_directory = persist_directory

        # Initialize components (lazy loading)
        self._chroma_client: Any = None
        self._collection: Any = None
        self._embedding_model: Any = None
        self._initialized = False

        logger.info(f"VectorMemoryService created: collection={collection_name}")

    def _initialize(self) -> bool:
        """Lazy initialization of ChromaDB and embedding model."""
        if self._initialized:
            return True

        try:
            # Import ChromaDB
            import chromadb
            from chromadb.config import Settings

            # Create client with persistence
            self._chroma_client = chromadb.Client(
                Settings(chroma_db_impl="duckdb+parquet", persist_directory=self.persist_directory)
            )

            # Get or create collection
            self._collection = self._chroma_client.get_or_create_collection(
                name=self.collection_name, metadata={"hnsw:space": "cosine"}
            )

            # Initialize embedding model
            from sentence_transformers import SentenceTransformer

            self._embedding_model = SentenceTransformer(self.embedding_model_name)

            self._initialized = True
            logger.info(f"VectorMemoryService initialized: model={self.embedding_model_name}")
            return True

        except ImportError as e:
            logger.error(
                f"Missing dependencies: {e}. Run: pip install chromadb sentence-transformers"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to initialize VectorMemoryService: {e}")
            return False

    def embed(self, text: str) -> list[float]:
        """Generate embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        if not self._initialize():
            raise RuntimeError("VectorMemoryService not initialized")

        # Generate embedding
        embedding = self._embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def store(
        self,
        entry_id: str,
        content: str,
        metadata: dict[str, Any] = None,
        embedding: list[float] = None,
    ) -> bool:
        """Store content in vector memory.

        Args:
            entry_id: Unique identifier
            content: Text content
            metadata: Optional metadata dictionary
            embedding: Optional pre-computed embedding

        Returns:
            True if stored successfully
        """
        if not self._initialize():
            return False

        try:
            # Compute embedding if not provided
            if embedding is None:
                embedding = self.embed(content)

            # Prepare metadata
            meta = metadata or {}
            meta["timestamp"] = datetime.now(UTC).isoformat()
            meta["content_hash"] = hashlib.md5(content.encode()).hexdigest()[:8]

            # Store in ChromaDB
            self._collection.add(
                ids=[entry_id], embeddings=[embedding], documents=[content], metadatas=[meta]
            )

            logger.debug(f"Stored vector entry: {entry_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store vector entry {entry_id}: {e}")
            return False

    def search(
        self, query: str, k: int = 5, filter: dict[str, Any] = None, min_score: float = None
    ) -> list[SearchResult]:
        """Semantic search over vector memory.

        Args:
            query: Search query text
            k: Number of results to return
            filter: Metadata filter (e.g., {"type": "knowledge"})
            min_score: Minimum similarity score (0-1)

        Returns:
            List of search results sorted by relevance
        """
        if not self._initialize():
            return []

        if min_score is None:
            min_score = self.similarity_threshold

        try:
            # Generate query embedding
            query_embedding = self.embed(query)

            # Search in ChromaDB
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=filter,
                include=["documents", "metadatas", "distances"],
            )

            # Convert to SearchResult objects
            search_results = []
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    distance = results["distances"][0][i]
                    # Convert cosine distance to similarity score
                    score = 1 - distance

                    # Skip if below threshold
                    if score < min_score:
                        continue

                    entry = VectorMemoryEntry(
                        id=doc_id,
                        content=results["documents"][0][i],
                        metadata=results["metadatas"][0][i],
                        score=score,
                    )

                    search_results.append(SearchResult(entry=entry, score=score, distance=distance))

            # Sort by score descending
            search_results.sort(key=lambda x: x.score, reverse=True)

            logger.debug(f"Search '{query[:30]}...' returned {len(search_results)} results")
            return search_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def delete(self, entry_id: str) -> bool:
        """Delete entry from vector memory.

        Args:
            entry_id: Entry ID to delete

        Returns:
            True if deleted successfully
        """
        if not self._initialize():
            return False

        try:
            self._collection.delete(ids=[entry_id])
            logger.debug(f"Deleted vector entry: {entry_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete entry {entry_id}: {e}")
            return False

    def clear(self) -> bool:
        """Clear all entries from collection.

        Returns:
            True if cleared successfully
        """
        if not self._initialize():
            return False

        try:
            # Delete all entries
            self._collection.delete(where={})
            logger.info(f"Cleared vector memory collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False

    def get_stats(self) -> dict[str, Any]:
        """Get vector memory statistics.

        Returns:
            Dictionary with statistics
        """
        if not self._initialize():
            return {"status": "not_initialized"}

        try:
            count = self._collection.count()
            return {
                "status": "active",
                "collection": self.collection_name,
                "entries": count,
                "embedding_model": self.embedding_model_name,
                "similarity_threshold": self.similarity_threshold,
                "persist_directory": self.persist_directory,
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"status": "error", "error": str(e)}


# ============================================================================
# Memory Architecture Integration
# ============================================================================


class MemoryVectorBridge:
    """Bridge between tiered memory and vector memory.

    Automatically indexes L2/L3 memory entries into vector store
    for semantic search capabilities.
    """

    def __init__(self, vector_memory: Optional[VectorMemoryService] = None):
        """Initialize bridge.

        Args:
            vector_memory: Vector memory service instance
        """
        if vector_memory is None:
            vector_memory = VectorMemoryService()
        self.vector_memory = vector_memory
        self._enabled = True

    def index_memory_entry(self, entry: Any) -> bool:
        """Index a memory entry into vector store.

        Args:
            entry: Memory entry (from MemoryArchitecture)

        Returns:
            True if indexed successfully
        """
        if not self._enabled:
            return False

        try:
            # Extract content from entry
            content = getattr(entry, "content", str(entry))
            entry_id = getattr(entry, "id", hashlib.md5(content.encode()).hexdigest())

            # Build metadata
            metadata = {
                "memory_type": getattr(entry, "memory_type", "unknown"),
                "session_id": getattr(entry, "session_id", None),
                "priority": getattr(entry, "priority", 0),
                "source": "memory_architecture",
            }

            # Store in vector memory
            return self.vector_memory.store(entry_id, content, metadata)

        except Exception as e:
            logger.warning(f"Failed to index memory entry: {e}")
            return False

    def search_memory(self, query: str, memory_type: str = None, k: int = 5) -> list[SearchResult]:
        """Search memory using semantic query.

        Args:
            query: Search query
            memory_type: Filter by memory type
            k: Number of results

        Returns:
            List of search results
        """
        filter_dict = None
        if memory_type:
            filter_dict = {"memory_type": memory_type}

        return self.vector_memory.search(query, k=k, filter=filter_dict)


# ============================================================================
# Singleton Instance
# ============================================================================
_vector_memory_instance: Optional[VectorMemoryService] = None


def get_vector_memory() -> VectorMemoryService:
    """Get or create singleton vector memory instance.

    Returns:
        VectorMemoryService singleton
    """
    global _vector_memory_instance
    if _vector_memory_instance is None:
        _vector_memory_instance = VectorMemoryService()
    return _vector_memory_instance


def get_memory_vector_bridge() -> MemoryVectorBridge:
    """Get memory-vector bridge instance.

    Returns:
        MemoryVectorBridge instance
    """
    return MemoryVectorBridge(get_vector_memory())


# ============================================================================
# Health Check
# ============================================================================


def check_vector_memory_health() -> dict[str, Any]:
    """Check vector memory system health.

    Returns:
        Health status dictionary
    """
    try:
        vm = get_vector_memory()
        stats = vm.get_stats()

        if stats.get("status") == "active":
            return {
                "status": "healthy",
                "initialized": True,
                "entries": stats.get("entries", 0),
                "model": stats.get("embedding_model"),
            }
        else:
            return {
                "status": "unhealthy",
                "initialized": False,
                "error": stats.get("error", "Unknown error"),
            }

    except Exception as e:
        return {"status": "error", "initialized": False, "error": str(e)}


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: Basic usage
    print("AMOS Vector Memory System Demo")
    print("=" * 50)

    # Get vector memory
    vm = get_vector_memory()

    # Check health
    health = check_vector_memory_health()
    print(f"Health: {health}")

    # Store some knowledge
    vm.store("python-001", "Python is a high-level programming language known for its readability")
    vm.store("python-002", "Python supports multiple programming paradigms including OOP")
    vm.store("ai-001", "Machine learning is a subset of artificial intelligence")
    vm.store("ai-002", "Neural networks are inspired by biological neurons")

    # Search
    print("\nSearching for 'programming language':")
    results = vm.search("programming language", k=3)
    for r in results:
        print(f"  [{r.score:.2f}] {r.entry.content[:50]}...")

    print("\nSearching for 'artificial intelligence':")
    results = vm.search("artificial intelligence", k=3)
    for r in results:
        print(f"  [{r.score:.2f}] {r.entry.content[:50]}...")

    # Stats
    print(f"\nStats: {vm.get_stats()}")
