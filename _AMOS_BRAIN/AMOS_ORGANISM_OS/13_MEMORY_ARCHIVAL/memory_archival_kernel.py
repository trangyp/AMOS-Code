#!/usr/bin/env python3
"""AMOS Memory Archival Kernel - 13_MEMORY_ARCHIVAL Subsystem

Responsible for:
- Long-term memory storage and persistence
- Memory indexing and retrieval
- Memory consolidation and compression
- Experience logging and archival
- Memory lifecycle management (hot/warm/cold storage)
- Semantic memory search and similarity matching
"""

from __future__ import annotations

import hashlib
import json
import logging
import zlib
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.memory")


class MemoryPriority(Enum):
    """Priority levels for memory retention."""

    CRITICAL = 5  # Never forget (core identity, safety rules)
    HIGH = 4  # Long-term retention (important learnings)
    MEDIUM = 3  # Standard retention (general experiences)
    LOW = 2  # Short-term retention (routine events)
    EPHEMERAL = 1  # Temporary (debug info, transient states)


class MemoryType(Enum):
    """Types of memories stored."""

    EXPERIENCE = auto()  # Events and experiences
    KNOWLEDGE = auto()  # Facts and learnings
    SKILL = auto()  # Abilities and procedures
    DECISION = auto()  # Decision history
    PERCEPTION = auto()  # Sensory inputs
    REFLECTION = auto()  # Self-analysis and insights
    GOAL = auto()  # Goals and objectives


class StorageTier(Enum):
    """Storage tiers for memory lifecycle management."""

    HOT = auto()  # Active RAM - frequently accessed
    WARM = auto()  # Local disk - occasionally accessed
    COLD = auto()  # Compressed archive - rarely accessed
    FROZEN = auto()  # Deep archive - backup only


@dataclass
class MemoryEntry:
    """A single memory entry."""

    memory_id: str
    memory_type: MemoryType
    content: dict[str, Any]
    priority: MemoryPriority
    created_at: str
    last_accessed: str
    access_count: int = 0
    tags: list[str] = field(default_factory=list)
    associations: list[str] = field(default_factory=list)
    embedding: Optional[list[float]] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.last_accessed:
            self.last_accessed = self.created_at

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type.name,
            "content": self.content,
            "priority": self.priority.name,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "tags": self.tags,
            "associations": self.associations,
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryEntry:
        """Create from dictionary."""
        return cls(
            memory_id=data["memory_id"],
            memory_type=MemoryType[data["memory_type"]],
            content=data["content"],
            priority=MemoryPriority[data["priority"]],
            created_at=data["created_at"],
            last_accessed=data["last_accessed"],
            access_count=data.get("access_count", 0),
            tags=data.get("tags", []),
            associations=data.get("associations", []),
            embedding=data.get("embedding"),
        )


@dataclass
class MemoryIndex:
    """Index entry for memory lookup."""

    memory_id: str
    memory_type: MemoryType
    priority: MemoryPriority
    storage_tier: StorageTier
    tags: set[str]
    created_at: str
    last_accessed: str
    size_bytes: int
    checksum: str


class MemoryArchivalKernel:
    """The Memory Archival Kernel manages long-term memory storage,
    retrieval, and lifecycle management for the AMOS organism.
    """

    def __init__(self, organism_root: Path):
        self.root = organism_root
        self.memory_path = organism_root / "13_MEMORY_ARCHIVAL"
        self.hot_path = self.memory_path / "hot"
        self.warm_path = self.memory_path / "warm"
        self.cold_path = self.memory_path / "cold"
        self.index_path = self.memory_path / "index"

        # Ensure directories
        self.hot_path.mkdir(parents=True, exist_ok=True)
        self.warm_path.mkdir(parents=True, exist_ok=True)
        self.cold_path.mkdir(parents=True, exist_ok=True)
        self.index_path.mkdir(parents=True, exist_ok=True)

        # Memory stores
        self.hot_memories: dict[str, MemoryEntry] = {}
        self.memory_index: dict[str, MemoryIndex] = {}

        # Tag index for fast lookup
        self.tag_index: dict[str, set[str]] = defaultdict(set)

        # Type index
        self.type_index: dict[MemoryType, set[str]] = defaultdict(set)

        # Configuration
        self.config = {
            "hot_capacity": 1000,
            "warm_capacity": 10000,
            "cold_capacity": 100000,
            "compression_threshold": 1024,  # bytes
            "archive_after_days": 30,
            "consolidation_threshold": 0.7,  # similarity threshold
        }

        # Statistics
        self.stats = {
            "memories_created": 0,
            "memories_retrieved": 0,
            "memories_consolidated": 0,
            "memories_archived": 0,
            "total_storage_bytes": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

        # Load existing index
        self._load_index()

        logger.info(f"MemoryArchivalKernel initialized at {self.memory_path}")

    def _load_index(self):
        """Load memory index from disk."""
        index_file = self.index_path / "memory_index.json"
        if index_file.exists():
            try:
                with open(index_file) as f:
                    data = json.load(f)
                    for entry_data in data:
                        index = MemoryIndex(
                            memory_id=entry_data["memory_id"],
                            memory_type=MemoryType[entry_data["memory_type"]],
                            priority=MemoryPriority[entry_data["priority"]],
                            storage_tier=StorageTier[entry_data["storage_tier"]],
                            tags=set(entry_data["tags"]),
                            created_at=entry_data["created_at"],
                            last_accessed=entry_data["last_accessed"],
                            size_bytes=entry_data["size_bytes"],
                            checksum=entry_data["checksum"],
                        )
                        self.memory_index[index.memory_id] = index

                        # Rebuild tag index
                        for tag in index.tags:
                            self.tag_index[tag].add(index.memory_id)

                        # Rebuild type index
                        self.type_index[index.memory_type].add(index.memory_id)

                logger.info(f"Loaded {len(self.memory_index)} memories from index")
            except Exception as e:
                logger.error(f"Failed to load memory index: {e}")

    def _save_index(self):
        """Save memory index to disk."""
        index_file = self.index_path / "memory_index.json"
        try:
            data = []
            for index in self.memory_index.values():
                data.append(
                    {
                        "memory_id": index.memory_id,
                        "memory_type": index.memory_type.name,
                        "priority": index.priority.name,
                        "storage_tier": index.storage_tier.name,
                        "tags": list(index.tags),
                        "created_at": index.created_at,
                        "last_accessed": index.last_accessed,
                        "size_bytes": index.size_bytes,
                        "checksum": index.checksum,
                    }
                )

            with open(index_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memory index: {e}")

    def store_memory(
        self,
        memory_type: MemoryType,
        content: dict[str, Any],
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        tags: Optional[list[str]] = None,
        associations: Optional[list[str]] = None,
    ) -> str:
        """Store a new memory."""
        # Generate memory ID
        content_hash = hashlib.md5(json.dumps(content, sort_keys=True).encode()).hexdigest()[:12]
        memory_id = f"mem_{memory_type.name.lower()}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{content_hash}"

        # Create memory entry
        entry = MemoryEntry(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            priority=priority,
            created_at=datetime.utcnow().isoformat(),
            last_accessed=datetime.utcnow().isoformat(),
            tags=tags or [],
            associations=associations or [],
        )

        # Store in hot tier
        self.hot_memories[memory_id] = entry

        # Create index
        content_bytes = json.dumps(content).encode()
        index = MemoryIndex(
            memory_id=memory_id,
            memory_type=memory_type,
            priority=priority,
            storage_tier=StorageTier.HOT,
            tags=set(tags or []),
            created_at=entry.created_at,
            last_accessed=entry.last_accessed,
            size_bytes=len(content_bytes),
            checksum=hashlib.sha256(content_bytes).hexdigest(),
        )

        self.memory_index[memory_id] = index

        # Update indices
        for tag in tags or []:
            self.tag_index[tag].add(memory_id)
        self.type_index[memory_type].add(memory_id)

        # Persist to warm storage
        self._persist_to_warm(entry)

        self.stats["memories_created"] += 1
        self.stats["total_storage_bytes"] += index.size_bytes

        logger.info(f"Stored memory {memory_id} ({memory_type.name}, {priority.name})")
        return memory_id

    def _persist_to_warm(self, entry: MemoryEntry):
        """Persist memory to warm storage."""
        warm_file = self.warm_path / f"{entry.memory_id}.json"
        try:
            with open(warm_file, "w") as f:
                json.dump(entry.to_dict(), f, indent=2)

            # Update index
            if entry.memory_id in self.memory_index:
                self.memory_index[entry.memory_id].storage_tier = StorageTier.WARM
        except Exception as e:
            logger.error(f"Failed to persist memory {entry.memory_id}: {e}")

    def retrieve_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory by ID."""
        # Check hot cache first
        if memory_id in self.hot_memories:
            entry = self.hot_memories[memory_id]
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow().isoformat()
            self.stats["cache_hits"] += 1
            return entry

        # Check warm storage
        warm_file = self.warm_path / f"{memory_id}.json"
        if warm_file.exists():
            try:
                with open(warm_file) as f:
                    entry = MemoryEntry.from_dict(json.load(f))

                # Promote to hot cache
                self.hot_memories[memory_id] = entry
                entry.access_count += 1
                entry.last_accessed = datetime.utcnow().isoformat()

                # Update index
                if memory_id in self.memory_index:
                    self.memory_index[memory_id].last_accessed = entry.last_accessed
                    self.memory_index[memory_id].storage_tier = StorageTier.HOT

                self.stats["cache_misses"] += 1
                self.stats["memories_retrieved"] += 1

                logger.debug(f"Retrieved memory {memory_id} from warm storage")
                return entry
            except Exception as e:
                logger.error(f"Failed to load memory {memory_id}: {e}")

        self.stats["cache_misses"] += 1
        return None

    def search_by_tags(self, tags: list[str]) -> list[MemoryEntry]:
        """Search memories by tags."""
        # Find intersection of all tag sets
        matching_ids = None
        for tag in tags:
            if tag in self.tag_index:
                if matching_ids is None:
                    matching_ids = self.tag_index[tag].copy()
                else:
                    matching_ids &= self.tag_index[tag]
            else:
                return []

        if not matching_ids:
            return []

        # Retrieve matching memories
        results = []
        for memory_id in matching_ids:
            entry = self.retrieve_memory(memory_id)
            if entry:
                results.append(entry)

        # Sort by priority and access count
        results.sort(key=lambda e: (e.priority.value, e.access_count), reverse=True)

        return results

    def search_by_type(self, memory_type: MemoryType, limit: int = 100) -> list[MemoryEntry]:
        """Search memories by type."""
        memory_ids = list(self.type_index[memory_type])[:limit]

        results = []
        for memory_id in memory_ids:
            entry = self.retrieve_memory(memory_id)
            if entry:
                results.append(entry)

        # Sort by last accessed
        results.sort(key=lambda e: e.last_accessed, reverse=True)

        return results

    def semantic_search(
        self, query_embedding: list[float], top_k: int = 10
    ) -> list[tuple[MemoryEntry, float]]:
        """Search memories by semantic similarity."""

        # Simple cosine similarity (in production, use vector DB)
        def cosine_similarity(a: list[float], b: list[float]) -> float:
            dot = sum(x * y for x, y in zip(a, b))
            norm_a = sum(x * x for x in a) ** 0.5
            norm_b = sum(x * x for x in b) ** 0.5
            return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

        # Score all memories with embeddings
        scored = []
        for memory_id, entry in self.hot_memories.items():
            if entry.embedding:
                score = cosine_similarity(query_embedding, entry.embedding)
                if score > 0.5:  # Threshold
                    scored.append((entry, score))

        # Return top-k
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def consolidate_memories(self, memory_type: MemoryType):
        """Consolidate similar memories of a given type."""
        memories = self.search_by_type(memory_type)

        if len(memories) < 2:
            return

        # Group by similarity (simplified - would use embeddings in production)
        consolidated = 0
        for i, mem1 in enumerate(memories):
            for mem2 in memories[i + 1 :]:
                # Check for duplicate content
                if self._memories_similar(mem1, mem2):
                    # Merge mem2 into mem1
                    mem1.content.update({f"consolidated_{mem2.memory_id}": mem2.content})
                    mem1.access_count += mem2.access_count
                    mem1.tags = list(set(mem1.tags + mem2.tags))

                    # Remove mem2
                    self._delete_memory(mem2.memory_id)
                    consolidated += 1

        self.stats["memories_consolidated"] += consolidated
        logger.info(f"Consolidated {consolidated} {memory_type.name} memories")

    def _memories_similar(self, mem1: MemoryEntry, mem2: MemoryEntry) -> bool:
        """Check if two memories are similar enough to consolidate."""
        # Simple content hash comparison
        content1 = json.dumps(mem1.content, sort_keys=True)
        content2 = json.dumps(mem2.content, sort_keys=True)

        # Check exact match or high overlap
        if content1 == content2:
            return True

        # Check for significant overlap in keys
        keys1 = set(mem1.content.keys())
        keys2 = set(mem2.content.keys())
        overlap = len(keys1 & keys2) / max(len(keys1), len(keys2), 1)

        return overlap > self.config["consolidation_threshold"]

    def _delete_memory(self, memory_id: str):
        """Delete a memory from all storage tiers."""
        # Remove from hot cache
        if memory_id in self.hot_memories:
            del self.hot_memories[memory_id]

        # Remove from index
        if memory_id in self.memory_index:
            index = self.memory_index[memory_id]

            # Remove from tag index
            for tag in index.tags:
                self.tag_index[tag].discard(memory_id)

            # Remove from type index
            self.type_index[index.memory_type].discard(memory_id)

            # Remove from main index
            del self.memory_index[memory_id]

        # Remove from warm storage
        warm_file = self.warm_path / f"{memory_id}.json"
        if warm_file.exists():
            warm_file.unlink()

        # Remove from cold storage
        cold_file = self.cold_path / f"{memory_id}.json.gz"
        if cold_file.exists():
            cold_file.unlink()

    def archive_old_memories(self, days: int = 30):
        """Archive memories older than specified days to cold storage."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        archived = 0

        for memory_id, index in list(self.memory_index.items()):
            if index.storage_tier != StorageTier.COLD:
                last_accessed = datetime.fromisoformat(index.last_accessed)

                if last_accessed < cutoff and index.priority != MemoryPriority.CRITICAL:
                    # Archive to cold storage
                    self._archive_memory(memory_id)
                    archived += 1

        self.stats["memories_archived"] += archived
        logger.info(f"Archived {archived} memories to cold storage")

    def _archive_memory(self, memory_id: str):
        """Move a memory to cold storage."""
        # Load from warm
        entry = self.retrieve_memory(memory_id)
        if not entry:
            return

        # Compress and save to cold storage
        cold_file = self.cold_path / f"{memory_id}.json.gz"
        try:
            data = json.dumps(entry.to_dict()).encode()
            compressed = zlib.compress(data, level=9)

            with open(cold_file, "wb") as f:
                f.write(compressed)

            # Remove from hot cache
            if memory_id in self.hot_memories:
                del self.hot_memories[memory_id]

            # Update index
            self.memory_index[memory_id].storage_tier = StorageTier.COLD

            # Remove from warm storage
            warm_file = self.warm_path / f"{memory_id}.json"
            if warm_file.exists():
                warm_file.unlink()

            logger.debug(f"Archived memory {memory_id}")
        except Exception as e:
            logger.error(f"Failed to archive memory {memory_id}: {e}")

    def get_memory_stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        tier_counts = defaultdict(int)
        type_counts = defaultdict(int)
        priority_counts = defaultdict(int)

        for index in self.memory_index.values():
            tier_counts[index.storage_tier.name] += 1
            type_counts[index.memory_type.name] += 1
            priority_counts[index.priority.name] += 1

        return {
            "total_memories": len(self.memory_index),
            "hot_cache_size": len(self.hot_memories),
            "by_tier": dict(tier_counts),
            "by_type": dict(type_counts),
            "by_priority": dict(priority_counts),
            "total_storage_bytes": self.stats["total_storage_bytes"],
            "cache_hit_rate": self.stats["cache_hits"]
            / max(1, self.stats["cache_hits"] + self.stats["cache_misses"]),
            "memories_created": self.stats["memories_created"],
            "memories_retrieved": self.stats["memories_retrieved"],
            "memories_consolidated": self.stats["memories_consolidated"],
            "memories_archived": self.stats["memories_archived"],
        }

    def get_state(self) -> dict[str, Any]:
        """Get current memory archival state."""
        return {
            "total_memories": len(self.memory_index),
            "hot_cache_size": len(self.hot_memories),
            "memories_created": self.stats["memories_created"],
            "memories_retrieved": self.stats["memories_retrieved"],
            "cache_hit_rate": self.stats["cache_hits"]
            / max(1, self.stats["cache_hits"] + self.stats["cache_misses"]),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def shutdown(self):
        """Shutdown and persist state."""
        self._save_index()
        logger.info("MemoryArchivalKernel shutdown complete")


if __name__ == "__main__":
    # Test the memory archival kernel
    root = Path(__file__).parent.parent
    memory = MemoryArchivalKernel(root)

    print("Memory State (initial):")
    print(json.dumps(memory.get_state(), indent=2))

    print("\n=== Test 1: Store Experiences ===")

    # Store some experiences
    mem1 = memory.store_memory(
        memory_type=MemoryType.EXPERIENCE,
        content={
            "event": "learned_python",
            "skill": "programming",
            "difficulty": "medium",
            "outcome": "success",
        },
        priority=MemoryPriority.HIGH,
        tags=["learning", "python", "programming"],
    )
    print(f"Stored: {mem1}")

    mem2 = memory.store_memory(
        memory_type=MemoryType.KNOWLEDGE,
        content={"fact": "Python uses indentation", "category": "syntax", "verified": True},
        priority=MemoryPriority.MEDIUM,
        tags=["python", "syntax", "facts"],
    )
    print(f"Stored: {mem2}")

    mem3 = memory.store_memory(
        memory_type=MemoryType.EXPERIENCE,
        content={
            "event": "debugged_error",
            "type": "syntax_error",
            "solution": "fixed_indentation",
        },
        priority=MemoryPriority.HIGH,
        tags=["debugging", "python", "learning"],
    )
    print(f"Stored: {mem3}")

    print("\n=== Test 2: Retrieve Memory ===")

    retrieved = memory.retrieve_memory(mem1)
    if retrieved:
        print(f"Retrieved: {retrieved.memory_id}")
        print(f"Content: {retrieved.content}")
        print(f"Access count: {retrieved.access_count}")

    print("\n=== Test 3: Search by Tags ===")

    results = memory.search_by_tags(["python", "learning"])
    print(f"Found {len(results)} memories with tags [python, learning]:")
    for r in results:
        print(f"  - {r.memory_id} ({r.memory_type.name})")

    print("\n=== Test 4: Search by Type ===")

    experiences = memory.search_by_type(MemoryType.EXPERIENCE)
    print(f"Found {len(experiences)} EXPERIENCE memories")

    knowledge = memory.search_by_type(MemoryType.KNOWLEDGE)
    print(f"Found {len(knowledge)} KNOWLEDGE memories")

    print("\n=== Test 5: Memory Statistics ===")

    stats = memory.get_memory_stats()
    print(f"Total memories: {stats['total_memories']}")
    print(f"By type: {stats['by_type']}")
    print(f"By priority: {stats['by_priority']}")

    print("\n=== Test 6: Consolidate Memories ===")

    # Store a similar experience
    mem4 = memory.store_memory(
        memory_type=MemoryType.EXPERIENCE,
        content={
            "event": "learned_python",
            "skill": "programming",
            "difficulty": "medium",
            "outcome": "success",
        },
        priority=MemoryPriority.MEDIUM,
        tags=["learning", "python"],
    )
    print(f"Stored duplicate-like: {mem4}")

    # Consolidate
    memory.consolidate_memories(MemoryType.EXPERIENCE)

    print(f"After consolidation: {memory.get_memory_stats()['total_memories']} memories")

    print("\nFinal State:")
    print(json.dumps(memory.get_state(), indent=2))

    memory.shutdown()
    print("\nMemory Archival Kernel test complete!")
