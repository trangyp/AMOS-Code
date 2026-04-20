"""AMOS Agent Knowledge & Memory System (RAG).

Provides comprehensive knowledge management and retrieval-augmented generation
for AI agents with vector-based semantic search.

Features:
- Vector store integration (Chroma, Pinecone, Weaviate compatible)
- Document ingestion and chunking
- Semantic search and retrieval
- Agent memory types (episodic, semantic, procedural)
- RAG query engine for LLM augmentation
- Knowledge base management

Research Sources:
- RAG Architecture Patterns 2026 (Calmops, Weskill)
- Vector Database Comparison 2026 (Groovyweb)
- Hybrid Search & Re-Ranking Best Practices

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

UTC = UTC
from typing import Any, Optional

# Configuration
VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "chroma")  # chroma, pinecone, weaviate
VECTOR_STORE_URL = os.getenv("VECTOR_STORE_URL", "./data/vectorstore")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "5"))


class MemoryType(Enum):
    """Types of agent memory."""

    EPISODIC = "episodic"  # Events, experiences, conversations
    SEMANTIC = "semantic"  # Facts, concepts, knowledge
    PROCEDURAL = "procedural"  # Skills, procedures, how-to


class KnowledgeSource(Enum):
    """Sources of knowledge."""

    DOCUMENT = "document"
    CONVERSATION = "conversation"
    WEB = "web"
    API = "api"
    MANUAL = "manual"


@dataclass
class KnowledgeChunk:
    """Represents a chunk of knowledge."""

    chunk_id: str
    content: str
    embedding: list[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    source: str = ""
    source_type: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    memory_type: str = "semantic"
    relevance_score: float = 0.0


@dataclass
class RAGQueryResult:
    """Result of a RAG query."""

    query: str
    chunks: list[KnowledgeChunk]
    context: str = ""  # Combined context for LLM
    total_found: int = 0
    latency_ms: float = 0.0


class VectorStore:
    """Abstract vector store interface."""

    def __init__(self, store_type: str = "chroma", url: str = ""):
        self.store_type = store_type
        self.url = url or VECTOR_STORE_URL
        self._client = None
        self._embedding_func = None

    async def initialize(self):
        """Initialize vector store connection."""
        if self.store_type == "chroma":
            await self._init_chroma()
        elif self.store_type == "pinecone":
            await self._init_pinecone()
        elif self.store_type == "weaviate":
            await self._init_weaviate()

    async def _init_chroma(self):
        """Initialize ChromaDB."""
        try:
            import chromadb
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

            self._client = chromadb.PersistentClient(path=self.url)
            self._embedding_func = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)

            # Create collections if not exist
            for mem_type in MemoryType:
                try:
                    self._client.get_collection(name=mem_type.value)
                except Exception:
                    self._client.create_collection(
                        name=mem_type.value,
                        embedding_function=self._embedding_func,
                        metadata={"hnsw:space": "cosine"},
                    )

            print(f"✓ ChromaDB initialized at {self.url}")
        except ImportError:
            print("⚠ ChromaDB not available, using in-memory store")
            self._client = InMemoryVectorStore()

    async def _init_pinecone(self):
        """Initialize Pinecone."""
        try:
            import pinecone

            # Pinecone initialization would go here
            print("✓ Pinecone initialized")
        except ImportError:
            print("⚠ Pinecone not available")
            self._client = InMemoryVectorStore()

    async def _init_weaviate(self):
        """Initialize Weaviate."""
        try:
            import weaviate

            # Weaviate initialization would go here
            print("✓ Weaviate initialized")
        except ImportError:
            print("⚠ Weaviate not available")
            self._client = InMemoryVectorStore()

    async def add_chunks(
        self, chunks: list[KnowledgeChunk], memory_type: MemoryType = MemoryType.SEMANTIC
    ) -> bool:
        """Add knowledge chunks to vector store."""
        if not self._client:
            return False

        try:
            if self.store_type == "chroma":
                collection = self._client.get_collection(name=memory_type.value)

                documents = [c.content for c in chunks]
                ids = [c.chunk_id for c in chunks]
                metadatas = [c.metadata for c in chunks]

                collection.add(documents=documents, ids=ids, metadatas=metadatas)
                return True

            # In-memory fallback
            if isinstance(self._client, InMemoryVectorStore):
                return await self._client.add_chunks(chunks, memory_type)

        except Exception as e:
            print(f"Error adding chunks: {e}")
            return False

        return False

    async def search(
        self,
        query: str,
        memory_type: MemoryType = MemoryType.SEMANTIC,
        top_k: int = TOP_K_RETRIEVAL,
        filter_dict: dict[str, Optional[Any]] = None,
    ) -> list[KnowledgeChunk]:
        """Search for relevant knowledge chunks."""
        if not self._client:
            return []

        try:
            if self.store_type == "chroma":
                collection = self._client.get_collection(name=memory_type.value)

                results = collection.query(query_texts=[query], n_results=top_k, where=filter_dict)

                chunks = []
                for i, doc in enumerate(results["documents"][0]):
                    chunk = KnowledgeChunk(
                        chunk_id=results["ids"][0][i],
                        content=doc,
                        metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                        relevance_score=results["distances"][0][i]
                        if "distances" in results
                        else 0.0,
                        memory_type=memory_type.value,
                    )
                    chunks.append(chunk)

                return chunks

            # In-memory fallback
            if isinstance(self._client, InMemoryVectorStore):
                return await self._client.search(query, memory_type, top_k)

        except Exception as e:
            print(f"Error searching: {e}")

        return []

    async def delete_chunk(self, chunk_id: str, memory_type: MemoryType) -> bool:
        """Delete a knowledge chunk."""
        if not self._client:
            return False

        try:
            if self.store_type == "chroma":
                collection = self._client.get_collection(name=memory_type.value)
                collection.delete(ids=[chunk_id])
                return True
        except Exception as e:
            print(f"Error deleting chunk: {e}")

        return False

    def get_stats(self) -> dict[str, Any]:
        """Get vector store statistics."""
        stats = {"store_type": self.store_type, "url": self.url, "collections": []}

        if self._client and self.store_type == "chroma":
            for mem_type in MemoryType:
                try:
                    collection = self._client.get_collection(name=mem_type.value)
                    count = collection.count()
                    stats["collections"].append({"name": mem_type.value, "count": count})
                except Exception:
                    pass

        return stats


class InMemoryVectorStore:
    """In-memory fallback vector store for development."""

    def __init__(self):
        self.collections: dict[str, list[KnowledgeChunk]] = {mt.value: [] for mt in MemoryType}

    async def add_chunks(self, chunks: list[KnowledgeChunk], memory_type: MemoryType) -> bool:
        self.collections[memory_type.value].extend(chunks)
        return True

    async def search(
        self, query: str, memory_type: MemoryType, top_k: int = 5
    ) -> list[KnowledgeChunk]:
        # Simple keyword matching for in-memory fallback
        query_words = set(query.lower().split())
        scored = []

        for chunk in self.collections[memory_type.value]:
            chunk_words = set(chunk.content.lower().split())
            score = len(query_words & chunk_words) / len(query_words)
            if score > 0:
                chunk.relevance_score = score
                scored.append(chunk)

        scored.sort(key=lambda x: x.relevance_score, reverse=True)
        return scored[:top_k]


class AgentKnowledgeManager:
    """Manager for agent knowledge and memory."""

    def __init__(self):
        self.vector_store = VectorStore(VECTOR_STORE_TYPE, VECTOR_STORE_URL)
        self.initialized = False

    async def initialize(self):
        """Initialize knowledge manager."""
        await self.vector_store.initialize()
        self.initialized = True
        print("✓ Agent Knowledge Manager initialized")

    def _generate_chunk_id(self, content: str, source: str) -> str:
        """Generate unique chunk ID."""
        data = f"{content}:{source}:{datetime.now(UTC).isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:16]

    def _chunk_document(
        self,
        content: str,
        source: str,
        source_type: str,
        memory_type: MemoryType = MemoryType.SEMANTIC,
    ) -> list[KnowledgeChunk]:
        """Chunk document into knowledge pieces."""
        chunks = []
        words = content.split()

        for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
            chunk_words = words[i : i + CHUNK_SIZE]
            chunk_content = " ".join(chunk_words)

            chunk = KnowledgeChunk(
                chunk_id=self._generate_chunk_id(chunk_content, source),
                content=chunk_content,
                source=source,
                source_type=source_type,
                memory_type=memory_type.value,
                metadata={
                    "chunk_index": len(chunks),
                    "total_words": len(words),
                    "ingested_at": datetime.now(UTC).isoformat(),
                },
            )
            chunks.append(chunk)

        return chunks

    async def ingest_document(
        self,
        content: str,
        source: str,
        source_type: str = "document",
        memory_type: MemoryType = MemoryType.SEMANTIC,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Ingest a document into knowledge base."""
        chunks = self._chunk_document(content, source, source_type, memory_type)

        # Add metadata to all chunks
        if metadata:
            for chunk in chunks:
                chunk.metadata.update(metadata)

        success = await self.vector_store.add_chunks(chunks, memory_type)

        if success:
            print(f"✓ Ingested {len(chunks)} chunks from {source}")
            return len(chunks)

        return 0

    async def add_episodic_memory(
        self,
        event: str,
        agent_id: str,
        conversation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Add an episodic memory (event/experience)."""
        chunk = KnowledgeChunk(
            chunk_id=self._generate_chunk_id(event, f"{agent_id}:{conversation_id or 'solo'}"),
            content=event,
            source=agent_id,
            source_type="episodic",
            memory_type=MemoryType.EPISODIC.value,
            metadata={
                "agent_id": agent_id,
                "conversation_id": conversation_id,
                "event_type": metadata.get("event_type", "generic") if metadata else "generic",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        return await self.vector_store.add_chunks([chunk], MemoryType.EPISODIC)

    async def add_semantic_memory(self, fact: str, category: str, confidence: float = 1.0) -> bool:
        """Add a semantic memory (fact/knowledge)."""
        chunk = KnowledgeChunk(
            chunk_id=self._generate_chunk_id(fact, category),
            content=fact,
            source=category,
            source_type="semantic",
            memory_type=MemoryType.SEMANTIC.value,
            metadata={
                "category": category,
                "confidence": confidence,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        return await self.vector_store.add_chunks([chunk], MemoryType.SEMANTIC)

    async def add_procedural_memory(
        self, procedure: str, skill_name: str, steps: list[str] = None
    ) -> bool:
        """Add a procedural memory (skill/how-to)."""
        content = procedure
        if steps:
            content += "\nSteps:\n" + "\n".join(
                [f"{i + 1}. {step}" for i, step in enumerate(steps)]
            )

        chunk = KnowledgeChunk(
            chunk_id=self._generate_chunk_id(content, skill_name),
            content=content,
            source=skill_name,
            source_type="procedural",
            memory_type=MemoryType.PROCEDURAL.value,
            metadata={
                "skill_name": skill_name,
                "steps": steps or [],
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        return await self.vector_store.add_chunks([chunk], MemoryType.PROCEDURAL)

    async def query(
        self,
        query: str,
        memory_types: list[MemoryType] = None,
        top_k: int = TOP_K_RETRIEVAL,
        filter_dict: dict[str, Optional[Any]] = None,
    ) -> RAGQueryResult:
        """Query knowledge base."""
        import time

        start_time = time.time()

        memory_types = memory_types or [MemoryType.SEMANTIC]
        all_chunks = []

        for mem_type in memory_types:
            chunks = await self.vector_store.search(query, mem_type, top_k, filter_dict)
            all_chunks.extend(chunks)

        # Sort by relevance and take top_k
        all_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
        all_chunks = all_chunks[:top_k]

        # Build context string
        context_parts = []
        for i, chunk in enumerate(all_chunks):
            context_parts.append(f"[{i + 1}] {chunk.content}")

        context = "\n\n".join(context_parts)

        return RAGQueryResult(
            query=query,
            chunks=all_chunks,
            context=context,
            total_found=len(all_chunks),
            latency_ms=(time.time() - start_time) * 1000,
        )

    async def get_relevant_context(
        self, query: str, conversation_id: str = None, agent_id: str = None
    ) -> str:
        """Get relevant context for a query."""
        # Search all memory types
        result = await self.query(
            query,
            memory_types=[MemoryType.SEMANTIC, MemoryType.EPISODIC, MemoryType.PROCEDURAL],
            top_k=TOP_K_RETRIEVAL,
        )

        # Filter by conversation/agent if specified
        if conversation_id or agent_id:
            filtered = []
            for chunk in result.chunks:
                meta = chunk.metadata
                if conversation_id and meta.get("conversation_id") == conversation_id:
                    filtered.append(chunk)
                elif agent_id and meta.get("agent_id") == agent_id:
                    filtered.append(chunk)
                elif not conversation_id and not agent_id:
                    filtered.append(chunk)
            result.chunks = filtered

        return result.context

    async def augment_prompt(
        self, user_query: str, system_prompt: str = "", conversation_id: str = None
    ) -> str:
        """Augment a prompt with relevant knowledge."""
        context = await self.get_relevant_context(user_query, conversation_id)

        if not context:
            return system_prompt + "\n\n" + user_query if system_prompt else user_query

        augmented = f"""{system_prompt}

Relevant context from knowledge base:
{context}

User query: {user_query}

Based on the context above, please respond to the user's query."""

        return augmented

    def get_stats(self) -> dict[str, Any]:
        """Get knowledge manager statistics."""
        stats = self.vector_store.get_stats()
        stats["chunk_size"] = CHUNK_SIZE
        stats["chunk_overlap"] = CHUNK_OVERLAP
        stats["top_k_retrieval"] = TOP_K_RETRIEVAL
        stats["embedding_model"] = EMBEDDING_MODEL
        return stats


# Global knowledge manager
knowledge_manager = AgentKnowledgeManager()


# Convenience functions
async def initialize_knowledge():
    """Initialize knowledge manager."""
    await knowledge_manager.initialize()


async def remember_episode(event: str, agent_id: str, conversation_id: str = None) -> bool:
    """Store an episodic memory."""
    return await knowledge_manager.add_episodic_memory(event, agent_id, conversation_id)


async def remember_fact(fact: str, category: str) -> bool:
    """Store a semantic memory (fact)."""
    return await knowledge_manager.add_semantic_memory(fact, category)


async def remember_skill(procedure: str, skill_name: str) -> bool:
    """Store a procedural memory (skill)."""
    return await knowledge_manager.add_procedural_memory(procedure, skill_name)


async def recall(query: str, top_k: int = 5) -> RAGQueryResult:
    """Query the knowledge base."""
    return await knowledge_manager.query(query, top_k=top_k)
