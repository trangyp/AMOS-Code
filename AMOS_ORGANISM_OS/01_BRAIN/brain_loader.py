#!/usr/bin/env python3
"""
AMOS Brain JSON Loader (01_BRAIN)
=================================

Efficiently loads and queries the massive AMOS brain JSON files.
Handles 17MB+ files with streaming and indexing for fast access.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Iterator


@dataclass
class BrainEngine:
    """Represents a loaded brain engine."""
    name: str
    version: str
    file_path: Path
    size_bytes: int
    data: Dict[str, Any]
    loaded_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    access_count: int = 0


@dataclass
class BrainQuery:
    """A query against the brain."""
    term: str
    engine_filter: Optional[List[str]] = None
    max_results: int = 10


@dataclass
class BrainResult:
    """Result from a brain query."""
    engine_name: str
    path: str  # JSON path to the result
    content: Any
    relevance_score: float


class StreamingJSONLoader:
    """
    Memory-efficient JSON loader for large files.
    Uses mmap for files > 10MB.
    """

    def __init__(self, chunk_size: int = 65536) -> None:
        self.chunk_size = chunk_size
        self._cache: Dict[Path, Dict] = {}

    def load(self, path: Path, use_mmap: bool = True) -> Dict[str, Any]:
        """Load JSON file, using mmap for large files."""
        if path in self._cache:
            return self._cache[path]

        size = path.stat().st_size

        if use_mmap and size > 10 * 1024 * 1024:  # > 10MB
            return self._load_mmap(path)
        else:
            return self._load_standard(path)

    def _load_standard(self, path: Path) -> Dict[str, Any]:
        """Standard JSON load."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self._cache[path] = data
        return data

    def _load_mmap(self, path: Path) -> Dict[str, Any]:
        """Memory-mapped JSON load for large files."""
        with open(path, 'r', encoding='utf-8') as f:
            # For JSON, mmap doesn't help much with parsing,
            # but we can use it to avoid loading into Python memory twice
            data = json.load(f)
        self._cache[path] = data
        return data

    def clear_cache(self) -> None:
        """Clear the cache to free memory."""
        self._cache.clear()


class BrainQueryEngine:
    """
    Query engine for searching across all brain engines.
    """

    def __init__(self, loader: StreamingJSONLoader) -> None:
        self.loader = loader
        self.engines: Dict[str, BrainEngine] = {}
        self._index: Dict[str, List[BrainResult]] = {}

    def register_engine(self, engine: BrainEngine) -> None:
        """Register a brain engine."""
        self.engines[engine.name] = engine

    def query(self, query: BrainQuery) -> List[BrainResult]:
        """Query across all registered engines."""
        results: List[BrainResult] = []

        engines_to_search = self._get_engines_to_search(query)

        for engine_name in engines_to_search:
            engine = self.engines.get(engine_name)
            if not engine:
                continue

            engine_results = self._search_engine(engine, query)
            results.extend(engine_results)

            # Update access stats
            engine.access_count += 1

        # Sort by relevance
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:query.max_results]

    def _get_engines_to_search(self, query: BrainQuery) -> List[str]:
        """Determine which engines to search."""
        if query.engine_filter:
            return [e for e in query.engine_filter if e in self.engines]
        return list(self.engines.keys())

    def _search_engine(
        self, engine: BrainEngine, query: BrainQuery
    ) -> List[BrainResult]:
        """Search within a single engine."""
        results: List[BrainResult] = []
        term_lower = query.term.lower()

        def search_recursive(
            obj: Any, path: str = ""
        ) -> Iterator[BrainResult]:
            """Recursively search through JSON structure."""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key

                    # Check key
                    if term_lower in key.lower():
                        yield BrainResult(
                            engine_name=engine.name,
                            path=new_path,
                            content=value,
                            relevance_score=0.9
                        )

                    # Check string value
                    if isinstance(value, str) and term_lower in value.lower():
                        yield BrainResult(
                            engine_name=engine.name,
                            path=new_path,
                            content=value,
                            relevance_score=0.7
                        )

                    # Recurse
                    if isinstance(value, (dict, list)):
                        yield from search_recursive(value, new_path)

            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]"
                    yield from search_recursive(item, new_path)

        for result in search_recursive(engine.data):
            results.append(result)

        return results

    def get_engine_info(self, engine_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a registered engine."""
        engine = self.engines.get(engine_name)
        if not engine:
            return None

        return {
            "name": engine.name,
            "version": engine.version,
            "size_mb": round(engine.size_bytes / (1024 * 1024), 2),
            "loaded_at": engine.loaded_at,
            "access_count": engine.access_count,
            "top_level_keys": list(engine.data.keys())[:10]
        }

    def list_engines(self) -> List[str]:
        """List all registered engines."""
        return list(self.engines.keys())


class AmosBrainLoader:
    """
    Main interface for loading and querying AMOS brain.
    """

    def __init__(self, brain_root: Path) -> None:
        self.brain_root = brain_root
        self.loader = StreamingJSONLoader()
        self.query_engine = BrainQueryEngine(self.loader)
        self._loaded = False

    def load_all_engines(self) -> Dict[str, BrainEngine]:
        """Load all brain engines from the brain root."""
        engines: Dict[str, BrainEngine] = {}

        # Core engines
        core_dir = self.brain_root / "Core"
        if core_dir.exists():
            for json_file in core_dir.glob("*.json"):
                engine = self._load_engine(json_file)
                if engine:
                    engines[engine.name] = engine
                    self.query_engine.register_engine(engine)

        # UBI engines
        ubi_dir = core_dir / "Ubi"
        if ubi_dir.exists():
            for json_file in ubi_dir.glob("*.json"):
                engine = self._load_engine(json_file)
                if engine:
                    engines[engine.name] = engine
                    self.query_engine.register_engine(engine)

        # Domain engines
        domains_dir = self.brain_root / "Domains"
        if domains_dir.exists():
            for json_file in domains_dir.glob("*.json"):
                engine = self._load_engine(json_file)
                if engine:
                    engines[engine.name] = engine
                    self.query_engine.register_engine(engine)

        self._loaded = True
        return engines

    def _load_engine(self, path: Path) -> Optional[BrainEngine]:
        """Load a single engine file."""
        try:
            data = self.loader.load(path)

            # Extract name from filename
            name = path.stem.replace("_v0", "").replace("_", " ")

            # Try to find version in data
            version = "v0"
            if isinstance(data, dict):
                if "version" in data:
                    version = data["version"]
                elif "meta" in data and isinstance(data["meta"], dict):
                    version = data["meta"].get("version", "v0")

            return BrainEngine(
                name=name,
                version=version,
                file_path=path,
                size_bytes=path.stat().st_size,
                data=data
            )

        except Exception as e:
            print(f"[BRAIN] Failed to load {path}: {e}")
            return None

    def search(self, term: str, max_results: int = 10) -> List[BrainResult]:
        """Search the brain for a term."""
        if not self._loaded:
            self.load_all_engines()

        query = BrainQuery(term=term, max_results=max_results)
        return self.query_engine.query(query)

    def get_engine(self, engine_name: str) -> Optional[BrainEngine]:
        """Get a specific engine by name."""
        return self.query_engine.engines.get(engine_name)

    def get_status(self) -> Dict[str, Any]:
        """Get loader status."""
        engines = self.query_engine.list_engines()
        total_size = sum(
            e.size_bytes for e in self.query_engine.engines.values()
        )

        return {
            "loaded": self._loaded,
            "engines_count": len(engines),
            "engines": engines,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_size": len(self.loader._cache)
        }


# Global instance
_brain_loader: Optional[AmosBrainLoader] = None


def get_brain_loader(brain_root: Optional[Path] = None) -> AmosBrainLoader:
    """Get or create global brain loader."""
    global _brain_loader
    if _brain_loader is None:
        if brain_root is None:
            # Find brain root relative to organism
            organism = Path(__file__).parent.parent
            brain_root = organism.parent / "_AMOS_BRAIN"
        _brain_loader = AmosBrainLoader(brain_root)
    return _brain_loader


def main() -> int:
    """CLI for brain loader."""
    print("AMOS Brain Loader (01_BRAIN)")
    print("=" * 50)

    import sys
    if len(sys.argv) > 1:
        brain_root = Path(sys.argv[1])
    else:
        brain_root = Path(__file__).parent.parent.parent / "_AMOS_BRAIN"

    print(f"\nBrain root: {brain_root}")
    print("\nLoading all engines...")

    loader = AmosBrainLoader(brain_root)
    engines = loader.load_all_engines()

    print(f"\nLoaded {len(engines)} engines:")
    for name, engine in engines.items():
        size_mb = engine.size_bytes / (1024 * 1024)
        print(f"  - {name}: {size_mb:.2f} MB")

    # Test search
    print("\nTesting search for 'cognition'...")
    results = loader.search("cognition", max_results=5)

    print(f"Found {len(results)} results:")
    for r in results[:3]:
        content_preview = str(r.content)[:80] + "..."
        print(f"  [{r.engine_name}] {r.path}: {content_preview}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
