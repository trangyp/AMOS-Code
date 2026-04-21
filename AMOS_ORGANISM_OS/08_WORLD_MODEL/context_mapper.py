from __future__ import annotations

"""Context Mapper — Maps environment context to semantic meaning for AMOS."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class ContextMap:
    """A mapping of context to meaning."""

    id: str
    source: str  # e.g., file path, directory
    context_type: str  # e.g., "project", "module", "task"
    properties: dict[str, Any] = field(default_factory=dict)
    semantic_tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class ContextMapper:
    """Maps environment context to semantic understanding.

    Responsibilities:
    - Map file structures to project concepts
    - Tag entities with semantic meaning
    - Identify patterns in context
    - Build contextual understanding
    """

    def __init__(self):
        self._maps: dict[str, ContextMap] = {}
        self._tag_index: dict[str, list[str]] = {}

    def map_context(
        self, source: str, context_type: str = None, properties: dict[str, Any] = None
    ) -> ContextMap:
        """Create a context map for a source."""
        import uuid

        ctx_type = context_type or self._infer_context_type(source)
        props = properties or {}
        tags = self._generate_tags(source, ctx_type, props)

        map_obj = ContextMap(
            id=str(uuid.uuid4())[:8],
            source=source,
            context_type=ctx_type,
            properties=props,
            semantic_tags=tags,
        )

        self._maps[map_obj.id] = map_obj

        # Index by tags
        for tag in tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            self._tag_index[tag].append(map_obj.id)

        return map_obj

    def _infer_context_type(self, source: str) -> str:
        """Infer context type from source path."""
        source = source.lower()

        if "/test" in source or source.startswith("test_") or "_test.py" in source:
            return "test"
        elif "/docs" in source or source.endswith(".md") or source.endswith(".rst"):
            return "documentation"
        elif "/src" in source or source.endswith(".py"):
            return "source"
        elif "/config" in source or source.endswith(".json") or source.endswith(".yaml"):
            return "config"
        elif "/.git" in source:
            return "version_control"
        else:
            return "general"

    def _generate_tags(
        self, source: str, context_type: str, properties: dict[str, Any]
    ) -> list[str]:
        """Generate semantic tags for context."""
        tags = [context_type]

        # Add extension-based tags
        if "." in source:
            ext = source.split(".")[-1]
            tags.append(f"ext:{ext}")

        # Add path-based tags
        if "/" in source:
            parts = source.split("/")
            for part in parts:
                if part and not part.startswith("."):
                    tags.append(f"path:{part}")

        return list(set(tags))

    def find_by_tag(self, tag: str) -> list[ContextMap]:
        """Find context maps by tag."""
        ids = self._tag_index.get(tag, [])
        return [self._maps[mid] for mid in ids if mid in self._maps]

    def get_context(self, source: str) -> Optional[ContextMap]:
        """Get context map for source."""
        for map_obj in self._maps.values():
            if map_obj.source == source:
                return map_obj
        return None

    def map_directory(self, path: str = ".") -> list[ContextMap]:
        """Map all files in directory."""
        import os

        maps = []
        for root, dirs, files in os.walk(path):
            # Skip hidden
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            # Map directory
            dir_map = self.map_context(root, "directory")
            maps.append(dir_map)

            # Map files
            for filename in files:
                if filename.startswith("."):
                    continue
                filepath = os.path.join(root, filename)
                file_map = self.map_context(filepath)
                maps.append(file_map)

        return maps

    def status(self) -> dict[str, Any]:
        """Get mapper status."""
        return {
            "total_maps": len(self._maps),
            "unique_tags": len(self._tag_index),
            "by_type": self._count_by_type(),
        }

    def _count_by_type(self) -> dict[str, int]:
        """Count maps by type."""
        counts: dict[str, int] = {}
        for map_obj in self._maps.values():
            t = map_obj.context_type
            counts[t] = counts.get(t, 0) + 1
        return counts
