"""Memory Indexer — Fast Memory Retrieval Indexing

Indexes archived memories for efficient search and retrieval,
maintains index structures, and optimizes query performance.

Owner: Trang
Version: 1.0.0
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime

UTC = UTC
from typing import Any


@dataclass
class IndexEntry:
    """An index entry for a memory."""

    memory_id: str
    tags: list[str]
    keywords: list[str]
    timestamp: datetime
    access_count: int = 0
    last_accessed: datetime = None


@dataclass
class MemoryIndex:
    """A memory index structure."""

    index_id: str
    name: str
    entries: dict[str, IndexEntry] = field(default_factory=dict)
    tag_index: dict[str, set[str]] = field(default_factory=dict)
    keyword_index: dict[str, set[str]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class MemoryIndexer:
    """Indexes memories for fast retrieval.

    Maintains multiple index structures for efficient
    searching by tags, keywords, and time.
    """

    def __init__(self):
        self.indices: dict[str, MemoryIndex] = {}
        self.default_index_id: str = None

    def create_index(self, name: str) -> MemoryIndex:
        """Create a new memory index."""
        index_id = f"index_{len(self.indices) + 1}"

        index = MemoryIndex(
            index_id=index_id,
            name=name,
        )

        self.indices[index_id] = index

        # Set as default if first index
        if self.default_index_id is None:
            self.default_index_id = index_id

        return index

    def add_to_index(self, index_id: str, entry: IndexEntry) -> bool:
        """Add an entry to an index."""
        if index_id not in self.indices:
            return False

        index = self.indices[index_id]
        index.entries[entry.memory_id] = entry

        # Update tag index
        for tag in entry.tags:
            if tag not in index.tag_index:
                index.tag_index[tag] = set()
            index.tag_index[tag].add(entry.memory_id)

        # Update keyword index
        for keyword in entry.keywords:
            if keyword not in index.keyword_index:
                index.keyword_index[keyword] = set()
            index.keyword_index[keyword].add(entry.memory_id)

        return True

    def remove_from_index(self, index_id: str, memory_id: str) -> bool:
        """Remove an entry from an index."""
        if index_id not in self.indices:
            return False

        index = self.indices[index_id]

        if memory_id not in index.entries:
            return False

        entry = index.entries[memory_id]

        # Remove from tag index
        for tag in entry.tags:
            if tag in index.tag_index:
                index.tag_index[tag].discard(memory_id)

        # Remove from keyword index
        for keyword in entry.keywords:
            if keyword in index.keyword_index:
                index.keyword_index[keyword].discard(memory_id)

        del index.entries[memory_id]
        return True

    def search_by_tags(
        self, index_id: str, tags: list[str], match_all: bool = True
    ) -> list[IndexEntry]:
        """Search index by tags."""
        if index_id not in self.indices:
            return []

        index = self.indices[index_id]

        # Get memory IDs for each tag
        tag_sets = [index.tag_index.get(tag, set()) for tag in tags]

        if not tag_sets:
            return []

        # Intersection (all) or union (any)
        if match_all:
            memory_ids = set.intersection(*tag_sets)
        else:
            memory_ids = set.union(*tag_sets)

        return [index.entries[mid] for mid in memory_ids if mid in index.entries]

    def search_by_keywords(self, index_id: str, keywords: list[str]) -> list[IndexEntry]:
        """Search index by keywords."""
        if index_id not in self.indices:
            return []

        index = self.indices[index_id]

        # Get memory IDs for each keyword
        keyword_sets = [index.keyword_index.get(kw, set()) for kw in keywords]

        if not keyword_sets:
            return []

        # Union of all matches
        memory_ids = set.union(*keyword_sets)

        return [index.entries[mid] for mid in memory_ids if mid in index.entries]

    def record_access(self, index_id: str, memory_id: str) -> bool:
        """Record access to a memory for LRU tracking."""
        if index_id not in self.indices:
            return False

        index = self.indices[index_id]

        if memory_id not in index.entries:
            return False

        entry = index.entries[memory_id]
        entry.access_count += 1
        entry.last_accessed = datetime.now(UTC)

        return True

    def get_most_accessed(self, index_id: str, limit: int = 10) -> list[IndexEntry]:
        """Get most frequently accessed memories."""
        if index_id not in self.indices:
            return []

        index = self.indices[index_id]

        sorted_entries = sorted(index.entries.values(), key=lambda e: e.access_count, reverse=True)

        return sorted_entries[:limit]

    def get_recently_accessed(self, index_id: str, limit: int = 10) -> list[IndexEntry]:
        """Get recently accessed memories."""
        if index_id not in self.indices:
            return []

        index = self.indices[index_id]

        # Filter entries with last_accessed
        accessed = [e for e in index.entries.values() if e.last_accessed is not None]

        sorted_entries = sorted(accessed, key=lambda e: e.last_accessed, reverse=True)

        return sorted_entries[:limit]

    def get_index_stats(self, index_id: str) -> dict[str, Any]:
        """Get statistics for an index."""
        if index_id not in self.indices:
            return None

        index = self.indices[index_id]

        return {
            "total_entries": len(index.entries),
            "unique_tags": len(index.tag_index),
            "unique_keywords": len(index.keyword_index),
            "total_accesses": sum(e.access_count for e in index.entries.values()),
        }


if __name__ == "__main__":
    print("Memory Indexer Module")
    print("=" * 50)

    indexer = MemoryIndexer()

    # Create index
    index = indexer.create_index("Main Memory Index")
    print(f"Created: {index.name}")

    # Add entries
    entry1 = IndexEntry(
        memory_id="mem_001",
        tags=["learning", "important"],
        keywords=["neural", "network"],
        timestamp=datetime.now(UTC),
    )
    indexer.add_to_index(index.index_id, entry1)

    entry2 = IndexEntry(
        memory_id="mem_002",
        tags=[["learning"], ["practice"]],
        keywords=["reinforcement", "training"],
        timestamp=datetime.now(UTC),
    )
    indexer.add_to_index(index.index_id, entry2)

    # Search
    results = indexer.search_by_tags(index.index_id, ["learning"])
    print(f"Tag search results: {len(results)}")

    stats = indexer.get_index_stats(index.index_id)
    print(f"Index stats: {stats}")

    print("Memory Indexer ready")
