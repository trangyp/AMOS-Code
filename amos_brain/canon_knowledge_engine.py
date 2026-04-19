"""Canon Knowledge Engine - Real-time canonical knowledge integration.

Parses and indexes actual AMOS Canon JSON files to provide:
- Canonical term resolution during cognitive processing
- Domain-specific knowledge retrieval
- Canon-aware context enrichment
- Real-time knowledge graph construction

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CanonKnowledgeEntry:
    """Single canonical knowledge entry."""

    key: str
    domain: str
    content: dict[str, Any]
    source_file: str
    entry_type: str  # 'law', 'engine', 'agent', 'kernel', etc.
    tags: list[str] = field(default_factory=list)


@dataclass
class CanonKnowledgeIndex:
    """Indexed canonical knowledge for a domain."""

    domain: str
    entries: list[CanonKnowledgeEntry] = field(default_factory=list)
    terms: dict[str, str] = field(default_factory=dict)
    engines: list[str] = field(default_factory=list)
    agents: list[str] = field(default_factory=list)
    laws: list[dict[str, Any]] = field(default_factory=list)

    def add_entry(self, entry: CanonKnowledgeEntry) -> None:
        """Add entry to index."""
        self.entries.append(entry)

        # Index by type
        if entry.entry_type == "engine":
            self.engines.append(entry.key)
        elif entry.entry_type == "agent":
            self.agents.append(entry.key)
        elif entry.entry_type == "law":
            if isinstance(entry.content, dict):
                self.laws.append(entry.content)

        # Extract terms from content
        self._extract_terms(entry)

    def _extract_terms(self, entry: CanonKnowledgeEntry) -> None:
        """Extract searchable terms from entry content."""
        if not isinstance(entry.content, dict):
            return

        # Extract description if available
        if "description" in entry.content:
            self.terms[entry.key] = entry.content["description"]

        # Extract meta description
        if "meta" in entry.content and isinstance(entry.content["meta"], dict):
            meta = entry.content["meta"]
            if "description" in meta:
                self.terms[entry.key] = meta["description"]
            if "codename" in meta:
                self.terms[meta["codename"]] = meta.get("description", "")

    def search(self, query: str) -> list[CanonKnowledgeEntry]:
        """Search indexed knowledge."""
        query_lower = query.lower()
        query_keywords = set(query_lower.replace("_", " ").split())
        results = []

        for entry in self.entries:
            # Check key match
            if query_lower in entry.key.lower():
                results.append(entry)
                continue

            # Check meta match
            if isinstance(entry.content, dict) and "meta" in entry.content:
                meta = entry.content["meta"]
                if isinstance(meta, dict):
                    meta_str = json.dumps(meta).lower()
                    if any(kw in meta_str for kw in query_keywords):
                        results.append(entry)
                        continue

            # Check content match for keywords
            content_str = json.dumps(entry.content).lower()
            if any(kw in content_str for kw in query_keywords):
                results.append(entry)

        return results


class CanonKnowledgeEngine:
    """Engine for loading and querying canonical knowledge.

    Real-time parser for AMOS Canon JSON files. Loads actual
    canonical definitions and makes them available to brain
    components during cognitive processing.
    """

    def __init__(self, canon_dir: str | None = None) -> None:
        self.canon_dir = canon_dir or os.environ.get(
            "AMOS_CANON_DIR",
            "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/_00_AMOS_CANON",
        )
        self._indices: dict[str, CanonKnowledgeIndex] = {}
        self._loaded = False
        self._total_entries = 0

    def load_canon(self) -> bool:
        """Load all Canon files into knowledge indices.

        Returns:
            True if successful, False otherwise
        """
        if self._loaded:
            return True

        canon_path = Path(self.canon_dir)
        if not canon_path.exists():
            return False

        # Load Core canon files
        core_dir = canon_path / "Core"
        if core_dir.exists():
            self._load_directory(core_dir, "core")

        # Load Domain canon files
        domains_dir = canon_path / "Domains"
        if domains_dir.exists():
            self._load_directory(domains_dir, "domains")

        # Load Cognitive canon files
        cognitive_dir = canon_path / "Cognitive"
        if cognitive_dir.exists():
            self._load_directory(cognitive_dir, "cognitive")

        self._loaded = True
        return True

    def _load_directory(self, directory: Path, domain_prefix: str) -> None:
        """Load all JSON files from a directory."""
        for json_file in directory.rglob("*.json"):
            try:
                self._load_json_file(json_file, domain_prefix)
            except (json.JSONDecodeError, IOError, OSError):
                continue

    def _load_json_file(self, file_path: Path, domain: str) -> None:
        """Load a single Canon JSON file."""
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # Determine entry type from filename
        entry_type = self._detect_entry_type(file_path.name)

        # Handle array of entries
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    self._index_canon_entry(item, domain, str(file_path), entry_type)
        # Handle single entry
        elif isinstance(data, dict):
            self._index_canon_entry(data, domain, str(file_path), entry_type)

    def _detect_entry_type(self, filename: str) -> str:
        """Detect entry type from filename."""
        filename_lower = filename.lower()

        if "engine" in filename_lower:
            return "engine"
        elif "agent" in filename_lower:
            return "agent"
        elif "kernel" in filename_lower:
            return "kernel"
        elif "law" in filename_lower or "canon" in filename_lower:
            return "law"
        elif "cognition" in filename_lower or "brain" in filename_lower:
            return "cognition"
        else:
            return "general"

    def _index_canon_entry(
        self,
        data: dict[str, Any],
        domain: str,
        source_file: str,
        entry_type: str,
    ) -> None:
        """Index a canonical entry."""
        # Get entry key
        key = self._extract_entry_key(data, source_file)

        # Create knowledge entry
        entry = CanonKnowledgeEntry(
            key=key,
            domain=domain,
            content=data,
            source_file=source_file,
            entry_type=entry_type,
        )

        # Add to appropriate index
        if domain not in self._indices:
            self._indices[domain] = CanonKnowledgeIndex(domain=domain)

        self._indices[domain].add_entry(entry)
        self._total_entries += 1

    def _extract_entry_key(self, data: dict[str, Any], source_file: str) -> str:
        """Extract entry key from data or filename."""
        # Try to get key from data
        if len(data) == 1:
            return list(data.keys())[0]

        # Use meta codename if available
        if "meta" in data and isinstance(data["meta"], dict):
            meta = data["meta"]
            if "codename" in meta:
                return meta["codename"]

        # Fallback to source filename
        return Path(source_file).stem

    def get_domain_knowledge(self, domain: str) -> CanonKnowledgeIndex | None:
        """Get knowledge index for a domain."""
        if not self._loaded:
            self.load_canon()
        return self._indices.get(domain)

    def search_all(self, query: str) -> dict[str, list[CanonKnowledgeEntry]]:
        """Search across all domains."""
        if not self._loaded:
            self.load_canon()

        results = {}
        for domain, index in self._indices.items():
            domain_results = index.search(query)
            if domain_results:
                results[domain] = domain_results

        return results

    def get_stats(self) -> dict[str, Any]:
        """Get loading statistics."""
        if not self._loaded:
            self.load_canon()

        return {
            "loaded": self._loaded,
            "total_entries": self._total_entries,
            "domains": len(self._indices),
            "domain_stats": {
                domain: {
                    "entries": len(index.entries),
                    "terms": len(index.terms),
                    "engines": len(index.engines),
                    "agents": len(index.agents),
                    "laws": len(index.laws),
                }
                for domain, index in self._indices.items()
            },
        }

    def enrich_query(self, query: str, domain: str) -> str:
        """Enrich query with canonical context."""
        index = self.get_domain_knowledge(domain)
        if not index:
            return query

        # Find relevant terms
        relevant_terms = []
        for term, description in index.terms.items():
            if term.lower() in query.lower():
                relevant_terms.append(f"{term}: {description}")

        if relevant_terms:
            canon_context = "\n".join(relevant_terms[:5])  # Top 5 terms
            return f"{query}\n\n[Canon Context]\n{canon_context}"

        return query


# Global instance
_canon_knowledge_engine: CanonKnowledgeEngine | None = None


def get_canon_knowledge_engine() -> CanonKnowledgeEngine:
    """Get or create global Canon knowledge engine."""
    global _canon_knowledge_engine
    if _canon_knowledge_engine is None:
        _canon_knowledge_engine = CanonKnowledgeEngine()
        _canon_knowledge_engine.load_canon()
    return _canon_knowledge_engine
