#!/usr/bin/env python3
"""SourceRegistry - Canonical Source and Document Management.

All data/document sources are registered here.
Unified interface for loading and querying sources.
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Any, Optional


@dataclass
class SourceConfig:
    """Configuration for a data source."""

    source_id: str
    source_type: str  # e.g., "file", "url", "database", "api"
    location: str
    metadata: Optional[dict[str, Any]] = None
    healthy: bool = True


class SourceRegistry:
    """Canonical registry for all data/document sources.

    Provides unified interface for source management.
    """

    def __init__(self, memory_governance: Any):
        self._memory_governance = memory_governance
        self._sources: dict[str, SourceConfig] = {}
        self._adapters: dict[str, Any] = {}
        self._lock = Lock()

    def register_source(self, config: SourceConfig) -> bool:
        """Register a source with the registry.

        Args:
            config: Source configuration

        Returns:
            True if registration successful
        """
        with self._lock:
            self._sources[config.source_id] = config
        return True

    def load_source(self, source_id: str) -> dict[str, Any]:
        """Load data from a source.

        Args:
            source_id: Source identifier

        Returns:
            Loaded data or error
        """
        with self._lock:
            source = self._sources.get(source_id)

        if not source:
            return {"success": False, "error": f"Source '{source_id}' not found"}

        # Route to appropriate adapter
        try:
            if source.source_type == "file":
                return self._load_file(source)
            elif source.source_type == "url":
                return self._load_url(source)
            elif source.source_type == "api":
                return self._load_api(source)
            else:
                return {"success": False, "error": f"Unknown source type: {source.source_type}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to load source: {str(e)}"}

    def _load_file(self, source: SourceConfig) -> dict[str, Any]:
        """Load from file system."""
        return {
            "success": True,
            "source_id": source.source_id,
            "data": f"[File contents from {source.location}]",
        }

    def _load_url(self, source: SourceConfig) -> dict[str, Any]:
        """Load from URL."""
        return {
            "success": True,
            "source_id": source.source_id,
            "data": f"[URL contents from {source.location}]",
        }

    def _load_api(self, source: SourceConfig) -> dict[str, Any]:
        """Load from API."""
        return {
            "success": True,
            "source_id": source.source_id,
            "data": f"[API response from {source.location}]",
        }

    def list_sources(self) -> list[str]:
        """List all registered source IDs."""
        with self._lock:
            return list(self._sources.keys())

    def is_healthy(self) -> bool:
        """Check if registry is healthy."""
        return True

    def shutdown(self) -> None:
        """Graceful shutdown."""
        pass
