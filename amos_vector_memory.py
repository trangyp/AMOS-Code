#!/usr/bin/env python3
"""AMOS Vector Memory & RAG System v1.0.0
=======================================

Semantic memory with vector embeddings and Retrieval-Augmented Generation (RAG).

Features:
  - ChromaDB vector store for embeddings
  - Sentence-transformers for text embedding
  - RAG pipeline: query → retrieve → augment → generate
  - Semantic search across memories
  - Integration with 5-tier memory system
  - Metadata filtering for precise retrieval
  - Persistent storage with SQLite backend

Architecture:
  ┌─────────────────────────────────────────────────────────────┐
  │                    AMOSVectorMemory                         │
  ├─────────────────────────────────────────────────────────────┤
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
  │  │  Embedding   │  │    Vector    │  │     RAG      │       │
  │  │   Service    │→ │    Store     │→ │   Pipeline   │       │
  │  │              │  │  (ChromaDB)  │  │              │       │
  │  └──────────────┘  └──────────────┘  └──────────────┘       │
  └─────────────────────────────────────────────────────────────┘

Usage:
    from amos_vector_memory import AMOSVectorMemory
  vm = AMOSVectorMemory()
  vm.initialize()

  # Store memory
  vm.add_memory(
      content="Important architectural decision...",
      memory_type="episodic",
      metadata={"session_id": "abc123"}
  )

  # Semantic search
  results = vm.search("architecture decisions", k=5)

  # RAG query
  response = vm.rag_query("What architecture decisions were made?")

Requirements:
  pip install chromadb sentence-transformers

Author: Trang Phan
Version: 1.0.0
"""

import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Try to import optional dependencies
try:
    import chromadb
    from chromadb.config import Settings

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


@dataclass
class VectorMemoryEntry:
    """A vector memory entry."""

    id: str
    content: str
    embedding: List[float] = field(default_factory=list)
    memory_type: str = "semantic"  # episodic, semantic, procedural
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    relevance_score: float = 0.0


class EmbeddingService:
    """Text embedding service using sentence-transformers."""

    # Default model - lightweight and fast
    DEFAULT_MODEL = "all-MiniLM-L6-v2"

    def __init__(self, model_name: str = None):
        self.model_name = model_name or self.DEFAULT_MODEL
        self._model = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize the embedding model."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            print("[Embedding] sentence-transformers not available")
            return False

        try:
            print(f"[Embedding] Loading model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            self._initialized = True
            print(f"[Embedding] Model loaded (dim: {self.get_dimension()})")
            return True
        except Exception as e:
            print(f"[Embedding] Failed to load model: {e}")
            return False

    def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if not self._initialized or not self._model:
            return None

        try:
            embedding = self._model.encode(text, convert_to_list=True)
            return embedding
        except Exception as e:
            print(f"[Embedding] Failed to embed text: {e}")
            return None

    def embed_batch(self, texts: List[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        if not self._initialized or not self._model:
            return None

        try:
            embeddings = self._model.encode(texts, convert_to_list=True)
            return embeddings
        except Exception as e:
            print(f"[Embedding] Failed to embed batch: {e}")
            return None

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        if self._model:
            return self._model.get_sentence_embedding_dimension()
        return 384  # Default for all-MiniLM-L6-v2


class AMOSVectorMemory:
    """Vector memory system with RAG capabilities."""

    def __init__(self, storage_path: str = None, collection_name: str = "amos_memory"):
        self.storage_path = storage_path or str(
            Path(__file__).parent / "_AMOS_BRAIN" / "vector_memory"
        )
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        self._embedding_service = EmbeddingService()
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize vector memory system."""
        print("[VectorMemory] Initializing...")

        if not CHROMA_AVAILABLE:
            print("  ⚠️ ChromaDB not available, using mock mode")
            self._initialized = True
            return True

        try:
            # Initialize embedding service
            embedding_ready = self._embedding_service.initialize()
            if not embedding_ready:
                print("  ⚠️ Embedding service not available")
                # Continue in mock mode
                self._initialized = True
                return True

            # Initialize ChromaDB client
            settings = Settings(anonymized_telemetry=False, allow_reset=True)

            self._client = chromadb.PersistentClient(path=self.storage_path, settings=settings)

            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name, metadata={"hnsw:space": "cosine"}
            )

            self._initialized = True
            count = self._collection.count()
            print(f"  ✓ VectorMemory initialized ({count} memories)")
            return True

        except Exception as e:
            print(f"  ⚠️ VectorMemory init failed: {e}")
            self._initialized = True  # Mock mode
            return True

    def add_memory(self, content: str, memory_type: str = "semantic", metadata: dict = None) -> str:
        """Add a memory to vector store."""
        if not self._initialized:
            return None

        # Generate ID
        memory_id = str(uuid.uuid4())

        # Generate embedding
        if self._embedding_service._initialized:
            embedding = self._embedding_service.embed(content)
        else:
            # Mock embedding
            embedding = [0.0] * 384

        if embedding is None:
            return None

        # Store in ChromaDB
        if self._collection:
            try:
                meta = {"memory_type": memory_type, "timestamp": time.time(), **(metadata or {})}

                self._collection.add(
                    ids=[memory_id], embeddings=[embedding], documents=[content], metadatas=[meta]
                )
            except Exception as e:
                print(f"[VectorMemory] Failed to store: {e}")
                return None

        return memory_id

    def search(
        self, query: str, k: int = 5, memory_type: str = None, filters: dict = None
    ) -> List[VectorMemoryEntry]:
        """Semantic search across memories."""
        if not self._initialized:
            return []

        # Generate query embedding
        if self._embedding_service._initialized:
            query_embedding = self._embedding_service.embed(query)
        else:
            # Mock embedding
            query_embedding = [0.0] * 384

        if query_embedding is None:
            return []

        # Build where clause
        where_clause = {}
        if memory_type:
            where_clause["memory_type"] = memory_type
        if filters:
            where_clause.update(filters)

        # Query ChromaDB
        if self._collection:
            try:
                results = self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k,
                    where=where_clause if where_clause else None,
                )

                # Convert to entries
                entries = []
                for i, doc_id in enumerate(results["ids"][0]):
                    entry = VectorMemoryEntry(
                        id=doc_id,
                        content=results["documents"][0][i],
                        memory_type=results["metadatas"][0][i].get("memory_type", "unknown"),
                        metadata=results["metadatas"][0][i],
                        relevance_score=results["distances"][0][i],
                        timestamp=results["metadatas"][0][i].get("timestamp", time.time()),
                    )
                    entries.append(entry)

                return entries

            except Exception as e:
                print(f"[VectorMemory] Search failed: {e}")
                return []

        return []

    def rag_query(self, query: str, k: int = 3, context_template: str = None) -> dict:
        """RAG query: retrieve relevant memories and augment."""
        # Retrieve relevant memories
        memories = self.search(query, k=k)

        # Build context
        context_parts = []
        for i, mem in enumerate(memories, 1):
            context_parts.append(f"[{i}] {mem.content}")

        context = "\n\n".join(context_parts)

        # Default template
        template = (
            context_template
            or """
Based on the following retrieved memories:

{context}

Answer the query: {query}

Provide a comprehensive answer using the retrieved information.
""".strip()
        )

        # Augmented prompt
        augmented_prompt = template.format(context=context, query=query)

        return {
            "query": query,
            "retrieved_memories": [
                {"content": m.content, "score": m.relevance_score} for m in memories
            ],
            "context": context,
            "augmented_prompt": augmented_prompt,
            "memory_count": len(memories),
        }

    def get_memory_stats(self) -> dict:
        """Get vector memory statistics."""
        if self._collection:
            try:
                return {
                    "total_memories": self._collection.count(),
                    "embedding_dim": self._embedding_service.get_dimension(),
                    "storage_path": self.storage_path,
                    "collection": self.collection_name,
                    "embedding_model": self._embedding_service.model_name,
                    "initialized": self._initialized,
                }
            except Exception:
                pass

        return {
            "total_memories": 0,
            "embedding_dim": self._embedding_service.get_dimension(),
            "initialized": self._initialized,
        }

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        if self._collection:
            try:
                self._collection.delete(ids=[memory_id])
                return True
            except Exception as e:
                print(f"[VectorMemory] Delete failed: {e}")

        return False

    def clear_all(self) -> bool:
        """Clear all memories."""
        if self._collection:
            try:
                self._collection.delete(where={})
                return True
            except Exception as e:
                print(f"[VectorMemory] Clear failed: {e}")

        return False


def main():
    """Demo vector memory system."""
    print("=" * 70)
    print("AMOS VECTOR MEMORY & RAG SYSTEM v1.0.0")
    print("=" * 70)

    vm = AMOSVectorMemory()
    vm.initialize()

    print("\n[Adding Memories]")
    memories = [
        "AMOS uses a hybrid neural-symbolic architecture combining LLMs with rule-based systems",
        "The 5-tier memory system includes Working, Short-term, Episodic, Semantic, and Procedural memory",
        "Global Laws L1-L6 enforce safety constraints on all system actions",
        "MCP tools provide filesystem, git, web search, and code execution capabilities",
        "The self-evolution engine enables autonomous code improvement with human oversight",
    ]

    memory_ids = []
    for content in memories:
        mid = vm.add_memory(content, memory_type="semantic")
        memory_ids.append(mid)
        print(f"  ✓ Added: {content[:50]}...")

    print("\n[Semantic Search]")
    query = "architecture and design patterns"
    results = vm.search(query, k=3)
    print(f"  Query: '{query}'")
    for i, result in enumerate(results, 1):
        print(f"  [{i}] {result.content[:60]}... (score: {result.relevance_score:.3f})")

    print("\n[RAG Query]")
    rag_result = vm.rag_query("How does AMOS architecture work?", k=3)
    print(f"  Retrieved {rag_result['memory_count']} memories")
    print(f"  Context length: {len(rag_result['context'])} chars")

    print("\n[Stats]")
    stats = vm.get_memory_stats()
    for key, value in stats.items():
        print(f"  • {key}: {value}")

    print("\n" + "=" * 70)
    print("Vector Memory System Ready!")
    print("=" * 70)


if __name__ == "__main__":
    main()
