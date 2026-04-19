"""Canon Memory System - Memory storage with canonical knowledge context.

Integrates AMOS Canon definitions into memory operations:
- Canon-contextualized memory storage
- Domain-aware memory retrieval
- Knowledge-enhanced memory search
- Canonical term resolution in memories

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .canon_knowledge_engine import get_canon_knowledge_engine, CanonKnowledgeEntry


@dataclass
class CanonMemory:
    """A memory entry with Canon context."""

    memory_id: str
    content: str
    domain: str
    timestamp: str
    canon_context: dict[str, Any] = field(default_factory=dict)
    canon_terms: dict[str, str] = field(default_factory=dict)
    related_entries: list[str] = field(default_factory=list)
    access_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class CanonMemorySystem:
    """Memory system with Canon knowledge integration.

    Stores and retrieves memories enriched with canonical context
    from AMOS Canon files.
    """

    def __init__(self) -> None:
        self._knowledge_engine = None
        self._initialized = False
        self._memories: dict[str, CanonMemory] = {}
        self._domain_index: dict[str, list[str]] = {}

    def initialize(self) -> bool:
        """Initialize with Canon knowledge engine."""
        if self._initialized:
            return True

        self._knowledge_engine = get_canon_knowledge_engine()
        self._initialized = True
        return True

    def store(
        self,
        content: str,
        domain: str,
        metadata: dict[str, Any] | None = None,
    ) -> CanonMemory:
        """Store a memory with Canon context.

        Args:
            content: Memory content
            domain: Domain for Canon context
            metadata: Additional metadata

        Returns:
            CanonMemory with enriched context
        """
        if not self._initialized:
            self.initialize()

        # Get Canon context
        canon_entries = self._get_relevant_canon(content, domain)
        canon_terms = self._extract_canon_terms(canon_entries)

        # Generate memory ID
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
        memory_id = f"mem_{domain}_{content_hash}"

        # Create memory
        memory = CanonMemory(
            memory_id=memory_id,
            content=content,
            domain=domain,
            timestamp=datetime.now(timezone.utc).isoformat(),
            canon_context={
                "entries_referenced": [e.key for e in canon_entries[:3]],
                "domain_knowledge_available": len(canon_entries),
            },
            canon_terms=dict(list(canon_terms.items())[:5]),
            related_entries=[e.source_file for e in canon_entries[:3]],
            metadata=metadata or {},
        )

        # Store
        self._memories[memory_id] = memory

        # Index by domain
        if domain not in self._domain_index:
            self._domain_index[domain] = []
        self._domain_index[domain].append(memory_id)

        return memory

    def retrieve(self, memory_id: str) -> CanonMemory | None:
        """Retrieve a memory by ID."""
        if not self._initialized:
            self.initialize()

        memory = self._memories.get(memory_id)
        if memory:
            memory.access_count += 1
        return memory

    def search(self, query: str, domain: str | None = None) -> list[CanonMemory]:
        """Search memories with Canon-enhanced relevance.

        Args:
            query: Search query
            domain: Optional domain filter

        Returns:
            List of matching memories sorted by relevance
        """
        if not self._initialized:
            self.initialize()

        query_lower = query.lower()
        results = []

        # Get memories to search
        if domain and domain in self._domain_index:
            memory_ids = self._domain_index[domain]
        else:
            memory_ids = list(self._memories.keys())

        for mem_id in memory_ids:
            memory = self._memories[mem_id]

            # Check content match
            content_score = self._calculate_content_score(query_lower, memory)

            # Check Canon term match
            canon_score = self._calculate_canon_score(query_lower, memory)

            # Combined score
            total_score = content_score + canon_score

            if total_score > 0:
                results.append((memory, total_score))

        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)

        return [r[0] for r in results[:10]]

    def _get_relevant_canon(self, content: str, domain: str) -> list[CanonKnowledgeEntry]:
        """Get Canon knowledge relevant to memory content."""
        if not self._knowledge_engine:
            return []

        entries = []

        index = self._knowledge_engine.get_domain_knowledge(domain)
        if index:
            entries.extend(index.search(content))

        # Also search core domain
        if domain != "core":
            core_index = self._knowledge_engine.get_domain_knowledge("core")
            if core_index:
                entries.extend(core_index.search(content))

        # Remove duplicates
        seen = set()
        unique = []
        for e in entries:
            if e.key not in seen:
                seen.add(e.key)
                unique.append(e)

        return unique[:5]

    def _extract_canon_terms(self, entries: list[CanonKnowledgeEntry]) -> dict[str, str]:
        """Extract terms from Canon entries."""
        terms = {}

        for entry in entries:
            if not isinstance(entry.content, dict):
                continue

            if "meta" in entry.content and isinstance(entry.content["meta"], dict):
                meta = entry.content["meta"]
                codename = meta.get("codename", entry.key)
                description = meta.get("description", "")
                if codename and description:
                    terms[codename] = description[:100]

        return terms

    def _calculate_content_score(self, query: str, memory: CanonMemory) -> float:
        """Calculate content relevance score."""
        score = 0.0
        content_lower = memory.content.lower()

        # Exact phrase match
        if query in content_lower:
            score += 2.0

        # Word match
        query_words = set(query.split())
        content_words = set(content_lower.split())
        matching_words = query_words & content_words
        score += len(matching_words) * 0.5

        return score

    def _calculate_canon_score(self, query: str, memory: CanonMemory) -> float:
        """Calculate Canon context relevance score."""
        score = 0.0

        # Check Canon terms
        for term, description in memory.canon_terms.items():
            term_lower = term.lower()
            desc_lower = description.lower()

            if query in term_lower or query in desc_lower:
                score += 1.5

            # Word match in Canon terms
            query_words = set(query.split())
            term_words = set(term_lower.split())
            desc_words = set(desc_lower.split())

            score += len(query_words & term_words) * 0.3
            score += len(query_words & desc_words) * 0.2

        return score

    def get_domain_memories(self, domain: str) -> list[CanonMemory]:
        """Get all memories for a domain."""
        memory_ids = self._domain_index.get(domain, [])
        return [self._memories[mid] for mid in memory_ids if mid in self._memories]

    def get_memory_stats(self) -> dict[str, Any]:
        """Get memory system statistics."""
        return {
            "total_memories": len(self._memories),
            "domains": len(self._domain_index),
            "domain_breakdown": {domain: len(ids) for domain, ids in self._domain_index.items()},
            "total_accesses": sum(m.access_count for m in self._memories.values()),
        }


# Global instance
_canon_memory_system: CanonMemorySystem | None = None


def get_canon_memory_system() -> CanonMemorySystem:
    """Get or create global Canon memory system."""
    global _canon_memory_system
    if _canon_memory_system is None:
        _canon_memory_system = CanonMemorySystem()
        _canon_memory_system.initialize()
    return _canon_memory_system


def canon_store(content: str, domain: str, metadata: dict | None = None) -> CanonMemory:
    """Store memory with Canon context - convenience function."""
    system = get_canon_memory_system()
    return system.store(content, domain, metadata)


def canon_search(query: str, domain: str | None = None) -> list[CanonMemory]:
    """Search memories with Canon enhancement - convenience function."""
    system = get_canon_memory_system()
    return system.search(query, domain)
