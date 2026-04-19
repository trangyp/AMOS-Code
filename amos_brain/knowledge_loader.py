#!/usr/bin/env python3
"""AMOS Brain Master Knowledge Loader
===================================

Loads and integrates the 17.8MB Brain_Master_Os knowledge base
into the cognitive architecture, enabling intelligent reasoning.

Connects:
- Brain_Master_Os_v0.json (17.8MB core knowledge)
- Cognitive architecture (6 laws, reasoning engines)
- Unified runtime (organism integration)

Owner: Trang
"""

from __future__ import annotations


import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class KnowledgeEntry:
    """Single knowledge entry from Brain Master."""

    key: str
    domain: str
    content: dict[str, Any]
    priority: int
    tags: list[str]


class BrainMasterKnowledgeLoader:
    """Loader for Brain_Master_Os core knowledge base.

    Loads 17.8MB of structured knowledge and makes it
    accessible to the cognitive architecture.
    """

    def __init__(self):
        self.knowledge_base: dict[str, Any] = {}
        self.entries: list[KnowledgeEntry] = []
        self.domains: dict[str, list[str]] = {}
        self.loaded = False
        self.stats = {"total_entries": 0, "domains": 0, "memory_mb": 0}

    def load_brain_master(self, path: Optional[Path] = None) -> dict[str, Any]:
        """Load Brain_Master_Os_v0.json knowledge base.

        Args:
            path: Optional path to brain master file

        Returns:
            Loading statistics
        """
        if path is None:
            # Default location
            repo_root = Path(__file__).parent.parent / "_AMOS_BRAIN" / "Core"
            path = repo_root / "AMOS_Brain_Master_Os_v0.json"

        print("🧠 Loading Brain Master Knowledge Base...")
        print(f"   Path: {path}")

        try:
            if not path.exists():
                raise FileNotFoundError(f"Brain Master not found: {path}")

            # Load JSON
            print(f"   Reading {path.stat().st_size / 1024 / 1024:.1f}MB file...")
            with open(path, encoding="utf-8") as f:
                self.knowledge_base = json.load(f)

            # Parse and index
            print("   Parsing knowledge structures...")
            self._parse_knowledge()

            # Update stats
            self.stats["memory_mb"] = path.stat().st_size / 1024 / 1024
            self.stats["total_entries"] = len(self.entries)
            self.stats["domains"] = len(self.domains)
            self.loaded = True

            print("✅ Brain Master loaded successfully!")
            print(f"   Entries: {self.stats['total_entries']}")
            print(f"   Domains: {self.stats['domains']}")
            print(f"   Size: {self.stats['memory_mb']:.1f}MB")

            return self.stats

        except Exception as e:
            print(f"❌ Failed to load Brain Master: {e}")
            return {"error": str(e)}

    def _parse_knowledge(self):
        """Parse knowledge base into searchable entries."""
        if isinstance(self.knowledge_base, dict):
            # Parse dictionary structure
            for key, value in self.knowledge_base.items():
                if isinstance(value, dict):
                    entry = KnowledgeEntry(
                        key=key,
                        domain=value.get("domain", "general"),
                        content=value,
                        priority=value.get("priority", 5),
                        tags=value.get("tags", []),
                    )
                    self.entries.append(entry)

                    # Index by domain
                    domain = entry.domain
                    if domain not in self.domains:
                        self.domains[domain] = []
                    self.domains[domain].append(key)

        elif isinstance(self.knowledge_base, list):
            # Parse list structure
            for i, item in enumerate(self.knowledge_base):
                if isinstance(item, dict):
                    entry = KnowledgeEntry(
                        key=item.get("id", f"entry_{i}"),
                        domain=item.get("domain", "general"),
                        content=item,
                        priority=item.get("priority", 5),
                        tags=item.get("tags", []),
                    )
                    self.entries.append(entry)

                    # Index by domain
                    domain = entry.domain
                    if domain not in self.domains:
                        self.domains[domain] = []
                    self.domains[domain].append(entry.key)

    def query(self, query: str, domain: str = None, limit: int = 5) -> list[KnowledgeEntry]:
        """Query knowledge base.

        Args:
            query: Search query
            domain: Optional domain filter
            limit: Maximum results

        Returns:
            Matching knowledge entries
        """
        if not self.loaded:
            return []

        results = []
        query_lower = query.lower()

        for entry in self.entries:
            # Domain filter
            if domain and entry.domain != domain:
                continue

            # Simple text matching (can be enhanced with embeddings)
            score = 0
            if query_lower in entry.key.lower():
                score += 10
            if query_lower in str(entry.content).lower():
                score += 5
            for tag in entry.tags:
                if query_lower in tag.lower():
                    score += 3

            if score > 0:
                results.append((score, entry))

        # Sort by score and priority
        results.sort(key=lambda x: (x[0], x[1].priority), reverse=True)
        return [r[1] for r in results[:limit]]

    def get_domain(self, domain: str) -> list[KnowledgeEntry]:
        """Get all entries in a domain."""
        if not self.loaded or domain not in self.domains:
            return []

        keys = self.domains[domain]
        return [e for e in self.entries if e.key in keys]

    def get_entry(self, key: str) -> Optional[KnowledgeEntry]:
        """Get specific entry by key."""
        for entry in self.entries:
            if entry.key == key:
                return entry
        return None

    def list_domains(self) -> list[str]:
        """List all available knowledge domains."""
        return list(self.domains.keys())

    def get_stats(self) -> dict[str, Any]:
        """Get loading statistics."""
        return {
            "loaded": self.loaded,
            "total_entries": len(self.entries),
            "domains": len(self.domains),
            "domain_list": self.list_domains(),
            "memory_mb": self.stats.get("memory_mb", 0),
        }


class KnowledgeEnhancedBrain:
    """Brain with integrated knowledge base.

    Combines cognitive architecture (6 laws) with
    Brain Master knowledge (17.8MB) for intelligent reasoning.
    """

    def __init__(self):
        self.knowledge_loader = BrainMasterKnowledgeLoader()
        self.initialized = False

    def initialize(self, knowledge_path: Optional[Path] = None) -> dict[str, Any]:
        """Initialize brain with knowledge base."""
        print("🧠 Initializing Knowledge-Enhanced Brain...")

        # Load knowledge
        stats = self.knowledge_loader.load_brain_master(knowledge_path)

        if "error" in stats:
            return stats

        self.initialized = True
        print("✅ Brain initialized with knowledge base!")

        return {"status": "initialized", "knowledge_stats": stats}

    def think_with_knowledge(self, problem: str, context: dict = None) -> dict[str, Any]:
        """Think about a problem using knowledge base.

        Retrieves relevant knowledge and applies cognitive reasoning.
        """
        if not self.initialized:
            return {"error": "Brain not initialized"}

        # Query knowledge
        relevant_knowledge = self.knowledge_loader.query(problem, limit=3)

        # Build enhanced context
        enhanced_context = context or {}
        enhanced_context["relevant_knowledge"] = [
            {"key": k.key, "domain": k.domain, "content_preview": str(k.content)[:200]}
            for k in relevant_knowledge
        ]

        # Apply reasoning (would integrate with existing think function)
        return {
            "problem": problem,
            "knowledge_used": len(relevant_knowledge),
            "knowledge_entries": [k.key for k in relevant_knowledge],
            "context": enhanced_context,
            "reasoning": f"Analyzed using {len(relevant_knowledge)} knowledge entries",
        }

    def get_knowledge_summary(self) -> dict[str, Any]:
        """Get summary of loaded knowledge."""
        if not self.initialized:
            return {"error": "Not initialized"}

        stats = self.knowledge_loader.get_stats()

        return {
            "loaded": stats["loaded"],
            "total_entries": stats["total_entries"],
            "domains": stats["domains"],
            "domain_list": stats["domain_list"][:10],  # First 10
            "memory_mb": stats["memory_mb"],
        }


# Global instance
_brain_knowledge: Optional[KnowledgeEnhancedBrain] = None


def get_knowledge_brain() -> KnowledgeEnhancedBrain:
    """Get or create knowledge-enhanced brain instance."""
    global _brain_knowledge
    if _brain_knowledge is None:
        _brain_knowledge = KnowledgeEnhancedBrain()
    return _brain_knowledge


def load_brain_knowledge(path: Optional[Path] = None) -> dict[str, Any]:
    """Convenience function to load brain knowledge."""
    brain = get_knowledge_brain()
    return brain.initialize(path)


def query_knowledge(query: str, domain: str = None, limit: int = 5) -> list[dict]:
    """Convenience function to query knowledge."""
    brain = get_knowledge_brain()
    if not brain.initialized:
        return []

    entries = brain.knowledge_loader.query(query, domain, limit)
    return [
        {
            "key": e.key,
            "domain": e.domain,
            "priority": e.priority,
            "tags": e.tags,
            "content": e.content,
        }
        for e in entries
    ]


def main():
    """Demo the knowledge loader."""
    print("=" * 70)
    print("AMOS BRAIN MASTER KNOWLEDGE LOADER DEMO")
    print("=" * 70)
    print()

    # Initialize
    brain = get_knowledge_brain()
    result = brain.initialize()

    if "error" in result:
        print(f"❌ Failed: {result['error']}")
        return 1

    # Show summary
    summary = brain.get_knowledge_summary()
    print("\n📊 Knowledge Summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")

    # Demo query
    print("\n🔍 Demo Query: 'architecture'")
    results = query_knowledge("architecture", limit=3)
    for i, r in enumerate(results, 1):
        print(f"   {i}. {r['key']} (domain: {r['domain']})")

    print("\n" + "=" * 70)
    print("✅ Brain Master Knowledge Loader Demo Complete!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
