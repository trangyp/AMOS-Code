#!/usr/bin/env python3
"""AMOS Memory Store - Vector-based memory system for AI agents.

Implements 2025 AI memory patterns (Mem0, vector databases, semantic search):
- Episodic memory: Conversation history and specific interactions
- Semantic memory: Concepts, facts, and relationships with embeddings
- Procedural memory: Learned behaviors and patterns
- Vector similarity search for context retrieval
- Multi-session persistence with session management
- Integration with Knowledge Graph (#68) and Prompt Registry (#73)

Component #74 - Agent Memory & Context Management Layer
"""

from __future__ import annotations

import asyncio
import hashlib
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Protocol

import numpy as np


class MemoryType(Enum):
    """Types of agent memory."""

    EPISODIC = "episodic"  # Specific interactions/conversations
    SEMANTIC = "semantic"  # Facts, concepts, knowledge
    PROCEDURAL = "procedural"  # Learned behaviors, patterns


class MemoryScope(Enum):
    """Scope of memory visibility."""

    SESSION = "session"  # Current session only
    USER = "user"  # Persistent per user
    GLOBAL = "global"  # Shared across all users


@dataclass
class MemoryEntry:
    """A single memory entry with embeddings."""

    memory_id: str
    content: str
    memory_type: MemoryType
    scope: MemoryScope

    # Context
    session_id: str = None
    user_id: str = None
    agent_id: str = None

    # Vector embedding for semantic search (simulated with numpy)
    embedding: list[float] = None
    embedding_model: str = "text-embedding-3-small"

    # Metadata
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    importance_score: float = 1.0  # 0-10, higher = more important

    # For semantic memory: related concepts
    related_concepts: list[str] = field(default_factory=list)

    # For episodic memory: conversation context
    conversation_turn: int = None
    speaker: str = None  # "user", "agent", "system"

    # Tags for categorization
    tags: list[str] = field(default_factory=list)

    # Source reference
    source_prompt_id: str = None
    source_execution_id: str = None

    def compute_embedding(self, dimension: int = 1536) -> list[float]:
        """Compute a deterministic embedding vector from content."""
        # Simulate embedding computation using hash
        # In production, this would call an embedding API (OpenAI, etc.)
        hash_val = hashlib.sha256(self.content.encode()).hexdigest()

        # Generate pseudo-random but deterministic embedding
        np.random.seed(int(hash_val[:16], 16))
        embedding = np.random.randn(dimension).astype(np.float32)

        # Normalize to unit vector
        embedding = embedding / np.linalg.norm(embedding)

        return embedding.tolist()

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "content": self.content[:200] + "..." if len(self.content) > 200 else self.content,
            "memory_type": self.memory_type.value,
            "scope": self.scope.value,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "created_at": datetime.fromtimestamp(self.created_at).isoformat(),
            "access_count": self.access_count,
            "importance_score": self.importance_score,
            "tags": self.tags,
        }


@dataclass
class SessionContext:
    """Context for a conversation session."""

    session_id: str
    user_id: str = None
    agent_id: str = None
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)

    # Conversation state
    conversation_turns: list[dict[str, Any]] = field(default_factory=list)
    current_turn: int = 0

    # Working memory - recent relevant memories
    active_memories: list[str] = field(default_factory=list)  # memory_ids

    # Context window management
    max_context_tokens: int = 4000
    current_context_tokens: int = 0

    # Session metadata
    total_interactions: int = 0
    session_summary: str = ""

    def add_turn(self, speaker: str, content: str) -> dict[str, Any]:
        """Add a conversation turn."""
        turn = {
            "turn": self.current_turn,
            "speaker": speaker,
            "content": content,
            "timestamp": time.time(),
        }
        self.conversation_turns.append(turn)
        self.current_turn += 1
        self.total_interactions += 1
        self.last_active = time.time()
        return turn

    def get_recent_context(self, max_turns: int = 10) -> str:
        """Get recent conversation context as formatted text."""
        recent = self.conversation_turns[-max_turns:] if self.conversation_turns else []
        lines = []
        for turn in recent:
            speaker_label = "User" if turn["speaker"] == "user" else "Assistant"
            lines.append(f"{speaker_label}: {turn['content']}")
        return "\n".join(lines)


@dataclass
class MemoryQuery:
    """Query for retrieving memories."""

    query_text: str
    memory_types: list[MemoryType] = None
    scope: Optional[MemoryScope] = None
    user_id: str = None
    session_id: str = None

    # Search parameters
    top_k: int = 5
    min_similarity: float = 0.7
    time_range_hours: int = None
    tags: list[str] = None


@dataclass
class MemorySearchResult:
    """Result from memory search."""

    memory: MemoryEntry
    similarity_score: float
    relevance_explanation: str = None


class VectorStore(Protocol):
    """Protocol for vector storage backends."""

    async def store_embedding(
        self, memory_id: str, embedding: list[float], metadata: dict[str, Any]
    ) -> bool:
        """Store an embedding with metadata."""
        ...

    async def search_similar(
        self, query_embedding: list[float], top_k: int = 5, filters: dict[str, Any] = None
    ) -> list[tuple[str, float]]:
        """Search for similar embeddings. Returns list of (memory_id, score)."""
        ...

    async def delete_embedding(self, memory_id: str) -> bool:
        """Delete an embedding."""
        ...


class InMemoryVectorStore:
    """In-memory vector store for embeddings."""

    def __init__(self):
        self.embeddings: dict[str, list[float]] = {}
        self.metadata: dict[str, dict[str, Any]] = {}

    async def store_embedding(
        self, memory_id: str, embedding: list[float], metadata: dict[str, Any]
    ) -> bool:
        self.embeddings[memory_id] = embedding
        self.metadata[memory_id] = metadata
        return True

    async def search_similar(
        self, query_embedding: list[float], top_k: int = 5, filters: dict[str, Any] = None
    ) -> list[tuple[str, float]]:
        """Cosine similarity search."""
        query_vec = np.array(query_embedding)

        scores = []
        for memory_id, emb in self.embeddings.items():
            # Apply filters if provided
            if filters:
                meta = self.metadata.get(memory_id, {})
                skip = False
                for key, value in filters.items():
                    if meta.get(key) != value:
                        skip = True
                        break
                if skip:
                    continue

            # Compute cosine similarity
            emb_vec = np.array(emb)
            similarity = np.dot(query_vec, emb_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(emb_vec)
            )
            scores.append((memory_id, float(similarity)))

        # Sort by similarity (highest first) and return top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    async def delete_embedding(self, memory_id: str) -> bool:
        if memory_id in self.embeddings:
            del self.embeddings[memory_id]
            del self.metadata[memory_id]
            return True
        return False


class AMOSMemoryStore:
    """
    Central memory store for AMOS ecosystem.

    Implements 2025 AI memory patterns (Mem0 architecture):
    - Episodic memory: Conversation history and interactions
    - Semantic memory: Facts, concepts, with vector embeddings
    - Procedural memory: Learned behaviors and patterns
    - Multi-session persistence
    - Semantic similarity search
    - Context window optimization

    Use cases:
    - Persistent agent memory across sessions
    - Context-aware responses using relevant past interactions
    - Knowledge accumulation and retrieval
    - Conversation summarization and continuity

    Integration Points:
    - #68 Knowledge Graph Memory: For structured knowledge
    - #73 Prompt Registry: Inject relevant memories into prompts
    - #67 Workflow Orchestrator: Session-aware workflow execution
    """

    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.vector_store = vector_store or InMemoryVectorStore()

        # In-memory storage
        self.memories: dict[str, MemoryEntry] = {}
        self.sessions: dict[str, SessionContext] = {}

        # Indexes for efficient retrieval
        self.user_memories: dict[str, list[str]] = {}  # user_id -> memory_ids
        self.session_memories: dict[str, list[str]] = {}  # session_id -> memory_ids
        self.tag_index: dict[str, list[str]] = {}  # tag -> memory_ids
        self.type_index: dict[MemoryType, list[str]] = {}  # type -> memory_ids

        # Configuration
        self.max_session_age_hours = 24
        self.embedding_dimension = 1536
        self.similarity_threshold = 0.7

    async def initialize(self) -> None:
        """Initialize memory store."""
        print("[MemoryStore] Initialized")
        print(f"  - Active memories: {len(self.memories)}")
        print(f"  - Active sessions: {len(self.sessions)}")
        print(f"  - Embedding dimension: {self.embedding_dimension}")

    def create_session(
        self, user_id: str = None, agent_id: str = None, max_context_tokens: int = 4000
    ) -> SessionContext:
        """Create a new conversation session."""
        session_id = f"session_{uuid.uuid4().hex[:12]}"

        session = SessionContext(
            session_id=session_id,
            user_id=user_id,
            agent_id=agent_id,
            max_context_tokens=max_context_tokens,
        )

        self.sessions[session_id] = session

        # Load user's long-term memories into session context
        if user_id and user_id in self.user_memories:
            relevant_memories = self._get_relevant_user_memories(user_id, limit=10)
            session.active_memories = [m.memory_id for m in relevant_memories]

        print(f"[MemoryStore] Created session: {session_id}")
        if user_id:
            print(f"  User: {user_id}")
            print(f"  Loaded {len(session.active_memories)} relevant memories")

        return session

    def _get_relevant_user_memories(self, user_id: str, limit: int = 10) -> list[MemoryEntry]:
        """Get most relevant memories for a user."""
        if user_id not in self.user_memories:
            return []

        memory_ids = self.user_memories[user_id]
        memories = [self.memories[mid] for mid in memory_ids if mid in self.memories]

        # Sort by importance and recency
        memories.sort(key=lambda m: (m.importance_score, m.last_accessed), reverse=True)

        return memories[:limit]

    def add_memory(
        self,
        content: str,
        memory_type: MemoryType,
        scope: MemoryScope = MemoryScope.SESSION,
        session_id: str = None,
        user_id: str = None,
        agent_id: str = None,
        importance_score: float = 1.0,
        tags: list[str] = None,
        related_concepts: list[str] = None,
        speaker: str = None,
        conversation_turn: int = None,
        source_prompt_id: str = None,
        source_execution_id: str = None,
    ) -> MemoryEntry:
        """Add a new memory entry."""
        memory_id = f"mem_{uuid.uuid4().hex[:16]}"

        # Create memory entry
        memory = MemoryEntry(
            memory_id=memory_id,
            content=content,
            memory_type=memory_type,
            scope=scope,
            session_id=session_id,
            user_id=user_id,
            agent_id=agent_id,
            importance_score=importance_score,
            tags=tags or [],
            related_concepts=related_concepts or [],
            speaker=speaker,
            conversation_turn=conversation_turn,
            source_prompt_id=source_prompt_id,
            source_execution_id=source_execution_id,
        )

        # Compute and store embedding
        memory.embedding = memory.compute_embedding(self.embedding_dimension)

        # Store in indexes
        self.memories[memory_id] = memory

        # Update vector store
        asyncio.create_task(
            self.vector_store.store_embedding(
                memory_id,
                memory.embedding,
                {
                    "memory_type": memory_type.value,
                    "scope": scope.value,
                    "user_id": user_id,
                    "session_id": session_id,
                    "tags": tags or [],
                },
            )
        )

        # Update indexes
        if user_id:
            if user_id not in self.user_memories:
                self.user_memories[user_id] = []
            self.user_memories[user_id].append(memory_id)

        if session_id:
            if session_id not in self.session_memories:
                self.session_memories[session_id] = []
            self.session_memories[session_id].append(memory_id)

        for tag in tags or []:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            self.tag_index[tag].append(memory_id)

        if memory_type not in self.type_index:
            self.type_index[memory_type] = []
        self.type_index[memory_type].append(memory_id)

        print(f"[MemoryStore] Added {memory_type.value} memory: {memory_id[:20]}...")

        return memory

    def add_conversation_turn(
        self, session_id: str, speaker: str, content: str, importance_score: float = 1.0
    ) -> tuple[SessionContext, MemoryEntry]:
        """Add a conversation turn as episodic memory."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        # Add to session conversation
        turn = session.add_turn(speaker, content)

        # Store as episodic memory
        memory = self.add_memory(
            content=content,
            memory_type=MemoryType.EPISODIC,
            scope=MemoryScope.SESSION,
            session_id=session_id,
            user_id=session.user_id,
            agent_id=session.agent_id,
            importance_score=importance_score,
            speaker=speaker,
            conversation_turn=turn["turn"],
            tags=["conversation", speaker],
        )

        # Update session's active memories
        session.active_memories.append(memory.memory_id)

        # Promote to long-term if important
        if importance_score >= 7.0 and session.user_id:
            self._promote_to_long_term(memory, session.user_id)

        return session, memory

    def _promote_to_long_term(self, memory: MemoryEntry, user_id: str) -> None:
        """Promote a session memory to user long-term memory."""
        memory.scope = MemoryScope.USER
        memory.user_id = user_id

        if user_id not in self.user_memories:
            self.user_memories[user_id] = []

        if memory.memory_id not in self.user_memories[user_id]:
            self.user_memories[user_id].append(memory.memory_id)

        print(f"[MemoryStore] Promoted to long-term: {memory.memory_id[:20]}...")

    async def search_memories(self, query: MemoryQuery) -> list[MemorySearchResult]:
        """Search for relevant memories using semantic similarity."""
        # Compute query embedding
        query_hash = hashlib.sha256(query.query_text.encode()).hexdigest()
        np.random.seed(int(query_hash[:16], 16))
        query_embedding = np.random.randn(self.embedding_dimension).astype(np.float32)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        # Build filters
        filters = {}
        if query.scope:
            filters["scope"] = query.scope.value
        if query.user_id:
            filters["user_id"] = query.user_id
        if query.session_id:
            filters["session_id"] = query.session_id

        # Search vector store
        similar = await self.vector_store.search_similar(
            query_embedding.tolist(),
            top_k=query.top_k * 2,  # Get extra for filtering
            filters=filters if filters else None,
        )

        # Filter and score results
        results = []
        for memory_id, similarity in similar:
            if memory_id not in self.memories:
                continue

            memory = self.memories[memory_id]

            # Filter by memory type
            if query.memory_types and memory.memory_type not in query.memory_types:
                continue

            # Filter by minimum similarity
            if similarity < query.min_similarity:
                continue

            # Filter by time range
            if query.time_range_hours:
                cutoff = time.time() - (query.time_range_hours * 3600)
                if memory.created_at < cutoff:
                    continue

            # Filter by tags
            if query.tags and not any(tag in memory.tags for tag in query.tags):
                continue

            # Update access stats
            memory.last_accessed = time.time()
            memory.access_count += 1

            results.append(MemorySearchResult(memory=memory, similarity_score=similarity))

        # Sort by combined score (similarity * importance)
        results.sort(key=lambda r: r.similarity_score * r.memory.importance_score, reverse=True)

        return results[: query.top_k]

    def get_context_for_prompt(
        self,
        session_id: str,
        query_text: str,
        max_memories: int = 5,
        include_conversation: bool = True,
        max_conversation_turns: int = 5,
    ) -> str:
        """Get formatted context for prompt injection."""
        if session_id not in self.sessions:
            return ""

        session = self.sessions[session_id]

        # Build query
        query = MemoryQuery(
            query_text=query_text,
            session_id=session_id,
            user_id=session.user_id,
            top_k=max_memories,
            min_similarity=self.similarity_threshold,
        )

        # Search for relevant memories
        # Note: Using asyncio.run for sync context, in production use async
        try:
            # Check if we're in async context
            asyncio.get_running_loop()
            # In async context - for demo, use synchronous approach
            relevant_memories = []
            for memory_id in session.active_memories[:max_memories]:
                if memory_id in self.memories:
                    relevant_memories.append(
                        MemorySearchResult(memory=self.memories[memory_id], similarity_score=0.8)
                    )
        except RuntimeError:
            # No running loop, use asyncio.run for async operation
            try:
                relevant_memories = asyncio.run(self.search_memories(query))
            except Exception:
                relevant_memories = []

        # Build context string
        context_parts = []

        # Add conversation history
        if include_conversation and session.conversation_turns:
            context_parts.append("## Recent Conversation")
            context_parts.append(session.get_recent_context(max_conversation_turns))
            context_parts.append("")

        # Add relevant memories
        if relevant_memories:
            context_parts.append("## Relevant Context from Memory")
            for result in relevant_memories:
                memory = result.memory
                type_label = memory.memory_type.value.capitalize()
                context_parts.append(f"[{type_label}] {memory.content}")
            context_parts.append("")

        return "\n".join(context_parts)

    def summarize_session(self, session_id: str) -> str:
        """Generate a summary of a conversation session."""
        if session_id not in self.sessions:
            return ""

        session = self.sessions[session_id]

        # Count by type
        episodic_count = sum(
            1
            for mid in self.session_memories.get(session_id, [])
            if mid in self.memories and self.memories[mid].memory_type == MemoryType.EPISODIC
        )

        summary = f"""Session Summary:
- Session ID: {session_id}
- User: {session.user_id or "Anonymous"}
- Duration: {self._format_duration(time.time() - session.created_at)}
- Total Turns: {session.current_turn}
- Memories Created: {episodic_count}
- Context Tokens: {session.current_context_tokens}/{session.max_context_tokens}
"""

        return summary

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable form."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds / 60)}m"
        else:
            return f"{seconds / 3600:.1f}h"

    def get_user_memory_stats(self, user_id: str) -> dict[str, Any]:
        """Get memory statistics for a user."""
        if user_id not in self.user_memories:
            return {"error": "User not found"}

        memory_ids = self.user_memories[user_id]
        memories = [self.memories[mid] for mid in memory_ids if mid in self.memories]

        # Count by type
        type_counts = {}
        for memory in memories:
            t = memory.memory_type.value
            type_counts[t] = type_counts.get(t, 0) + 1

        # Count by tag
        tag_counts = {}
        for memory in memories:
            for tag in memory.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Get most important memories
        important = sorted(memories, key=lambda m: m.importance_score, reverse=True)[:5]

        return {
            "user_id": user_id,
            "total_memories": len(memories),
            "by_type": type_counts,
            "by_tag": tag_counts,
            "most_important": [m.content[:100] + "..." for m in important],
            "avg_importance": sum(m.importance_score for m in memories) / len(memories)
            if memories
            else 0,
        }

    def cleanup_old_sessions(self, max_age_hours: int = None) -> int:
        """Clean up old session data."""
        max_age = max_age_hours or self.max_session_age_hours
        cutoff = time.time() - (max_age * 3600)

        removed = 0
        sessions_to_remove = []

        for session_id, session in self.sessions.items():
            if session.last_active < cutoff:
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            del self.sessions[session_id]
            # Keep session memories but mark as orphaned
            removed += 1

        print(f"[MemoryStore] Cleaned up {removed} old sessions")
        return removed

    def export_user_memories(self, user_id: str) -> list[dict[str, Any]]:
        """Export all memories for a user."""
        if user_id not in self.user_memories:
            return []

        memory_ids = self.user_memories[user_id]
        return [self.memories[mid].to_dict() for mid in memory_ids if mid in self.memories]

    def import_memories(self, memories: list[dict[str, Any]], user_id: str) -> int:
        """Import memories for a user."""
        imported = 0
        for mem_data in memories:
            try:
                memory = MemoryEntry(
                    memory_id=mem_data.get("memory_id", f"mem_{uuid.uuid4().hex[:16]}"),
                    content=mem_data["content"],
                    memory_type=MemoryType(mem_data.get("memory_type", "semantic")),
                    scope=MemoryScope.USER,
                    user_id=user_id,
                    importance_score=mem_data.get("importance_score", 1.0),
                    tags=mem_data.get("tags", []),
                )
                memory.embedding = memory.compute_embedding(self.embedding_dimension)

                self.memories[memory.memory_id] = memory

                if user_id not in self.user_memories:
                    self.user_memories[user_id] = []
                self.user_memories[user_id].append(memory.memory_id)

                imported += 1
            except Exception as e:
                print(f"[MemoryStore] Failed to import memory: {e}")

        print(f"[MemoryStore] Imported {imported} memories for user {user_id}")
        return imported


# ============================================================================
# DEMO
# ============================================================================


async def demo_memory_store():
    """Demonstrate AMOS Memory Store capabilities."""
    print("\n" + "=" * 70)
    print("AMOS MEMORY STORE - COMPONENT #74")
    print("=" * 70)

    store = AMOSMemoryStore()
    await store.initialize()

    print("\n[1] Creating conversation sessions...")

    # Create session for user
    session1 = store.create_session(
        user_id="user_123", agent_id="support_agent", max_context_tokens=4000
    )

    session2 = store.create_session(
        user_id="user_456", agent_id="coding_agent", max_context_tokens=8000
    )

    print(f"  ✓ Session 1: {session1.session_id} (User: user_123)")
    print(f"  ✓ Session 2: {session2.session_id} (User: user_456)")

    print("\n[2] Adding episodic memories (conversation turns)...")

    # Simulate conversation in session 1
    turns = [
        ("user", "Hi, I need help with my account. I can't log in.", 3.0),
        ("agent", "I'd be happy to help! Can you tell me your username or email?", 2.0),
        ("user", "It's john.doe@example.com", 2.0),
        (
            "agent",
            "Thanks! I see your account. It looks like your password expired. Let me reset it.",
            5.0,
        ),
        ("user", "Oh, that makes sense. I haven't changed it in a while.", 4.0),
        (
            "agent",
            "I've reset your password. Check your email for the new temporary password.",
            5.0,
        ),
        ("user", "Got it! Thanks for the quick help.", 3.0),
    ]

    for speaker, content, importance in turns:
        store.add_conversation_turn(session1.session_id, speaker, content, importance)

    print(f"  ✓ Added {len(turns)} conversation turns to session 1")

    # Simulate coding conversation in session 2
    code_turns = [
        ("user", "How do I implement a binary search in Python?", 4.0),
        (
            "agent",
            "Binary search is efficient! Here's how:\n```python\ndef binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1\n```",
            6.0,
        ),
        ("user", "Thanks! What's the time complexity?", 3.0),
        ("agent", "O(log n) time complexity. Much better than linear search's O(n)!", 5.0),
    ]

    for speaker, content, importance in code_turns:
        store.add_conversation_turn(session2.session_id, speaker, content, importance)

    print(f"  ✓ Added {len(code_turns)} conversation turns to session 2")

    print("\n[3] Adding semantic memories (facts and knowledge)...")

    # Add user preferences as semantic memory
    store.add_memory(
        content="User prefers technical explanations with code examples",
        memory_type=MemoryType.SEMANTIC,
        scope=MemoryScope.USER,
        user_id="user_456",
        importance_score=8.0,
        tags=["preference", "learning_style"],
    )

    store.add_memory(
        content="User has account at TechCorp since 2023, Premium tier",
        memory_type=MemoryType.SEMANTIC,
        scope=MemoryScope.USER,
        user_id="user_123",
        importance_score=7.0,
        tags=["account", "subscription"],
    )

    # Add global knowledge
    store.add_memory(
        content="Python list comprehension syntax: [x for x in iterable if condition]",
        memory_type=MemoryType.SEMANTIC,
        scope=MemoryScope.GLOBAL,
        importance_score=6.0,
        tags=["python", "syntax", "reference"],
    )

    print("  ✓ Added 3 semantic memories (2 user-specific, 1 global)")

    print("\n[4] Adding procedural memories (learned behaviors)...")

    store.add_memory(
        content="When user asks about algorithms, always provide time complexity analysis",
        memory_type=MemoryType.PROCEDURAL,
        scope=MemoryScope.USER,
        user_id="user_456",
        importance_score=7.0,
        tags=["behavior", "algorithms"],
    )

    print("  ✓ Added 1 procedural memory")

    print("\n[5] Retrieving context for prompt injection...")

    context = store.get_context_for_prompt(
        session_id=session1.session_id, query_text="account password login help", max_memories=3
    )

    print("  Context for Session 1 (password help query):")
    print("  " + "-" * 50)
    for line in context.split("\n")[:10]:
        print(f"  {line}")
    print("  " + "-" * 50)

    print("\n[6] Searching memories semantically...")

    query = MemoryQuery(
        query_text="How do I search efficiently in a sorted list?",
        user_id="user_456",
        top_k=3,
        min_similarity=0.5,
    )

    results = await store.search_memories(query)

    print(f"  Found {len(results)} relevant memories:")
    for i, result in enumerate(results, 1):
        mem = result.memory
        print(f"    {i}. [{mem.memory_type.value}] (similarity: {result.similarity_score:.2f})")
        print(f"       {mem.content[:80]}...")

    print("\n[7] Generating session summaries...")

    summary1 = store.summarize_session(session1.session_id)
    print("  Session 1 Summary:")
    for line in summary1.split("\n"):
        print(f"    {line}")

    print("\n[8] User memory statistics...")

    stats = store.get_user_memory_stats("user_456")
    print("  User user_456:")
    print(f"    Total memories: {stats['total_memories']}")
    print(f"    By type: {stats['by_type']}")
    print(f"    By tag: {dict(list(stats['by_tag'].items())[:3])}")

    print("\n[9] Memory store statistics...")

    total_memories = len(store.memories)
    total_sessions = len(store.sessions)
    episodic = len(store.type_index.get(MemoryType.EPISODIC, []))
    semantic = len(store.type_index.get(MemoryType.SEMANTIC, []))
    procedural = len(store.type_index.get(MemoryType.PROCEDURAL, []))

    print(f"  Total memories: {total_memories}")
    print(f"  - Episodic: {episodic}")
    print(f"  - Semantic: {semantic}")
    print(f"  - Procedural: {procedural}")
    print(f"  Active sessions: {total_sessions}")
    print(f"  Users with memories: {len(store.user_memories)}")

    print("\n[10] Testing memory persistence simulation...")

    # Export user memories
    exported = store.export_user_memories("user_123")
    print(f"  Exported {len(exported)} memories for user_123")

    # Simulate import to new store
    store2 = AMOSMemoryStore()
    imported = store2.import_memories(exported, "user_123_new")
    print(f"  Imported {imported} memories to new user account")

    print("\n" + "=" * 70)
    print("MEMORY STORE DEMO COMPLETE")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Episodic memory (conversation history)")
    print("  ✓ Semantic memory (facts and knowledge)")
    print("  ✓ Procedural memory (learned behaviors)")
    print("  ✓ Multi-session context management")
    print("  ✓ Vector-based semantic search")
    print("  ✓ Context injection for prompts")
    print("  ✓ User-specific memory persistence")
    print("  ✓ Memory statistics and summaries")
    print("  ✓ Import/export functionality")
    print("\nIntegration Points:")
    print("  • #68 Knowledge Graph Memory: Structured knowledge")
    print("  • #73 Prompt Registry: Context injection")
    print("  • #67 Workflow Orchestrator: Session-aware execution")
    print("  • #72 LLM Router: Memory-aware routing")


if __name__ == "__main__":
    asyncio.run(demo_memory_store())
