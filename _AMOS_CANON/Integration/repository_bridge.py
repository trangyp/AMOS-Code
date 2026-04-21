#!/usr/bin/env python3
"""repository_bridge.py - AMOS Repository Bridge

Connects AMOS Canon with repository subsystems.
Provides unified access to all AMOS repositories.

Part of AMOS Canon - One Source of Truth
"""

from __future__ import annotations
from typing import Any, Optional
from datetime import datetime, timezone
from pathlib import Path


class RepositoryBridge:
    """Canonical bridge to AMOS repository ecosystem."""

    def __init__(self) -> None:
        self._initialized = False
        self._canonical_id = "repository_bridge"
        self._repos: dict[str, Path] = {}

    def initialize(self) -> bool:
        """Initialize canonical repository bridge."""
        self._initialized = True
        self._discover_repositories()
        return True

    def _discover_repositories(self) -> None:
        """Discover AMOS repositories in ecosystem."""
        base = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
        repos = [
            ("AMOS-Code", base / "AMOS_REPOS" / "AMOS-Code"),
            ("AMOS-Consulting", base / "AMOS_REPOS" / "AMOS-Consulting"),
            ("AMOS-Claws", base / "AMOS_REPOS" / "AMOS-Claws"),
            ("AMOS-Invest", base / "AMOS_REPOS" / "AMOS-Invest"),
            ("AMOS-UNIVERSE", base / "AMOS_REPOS" / "AMOS-UNIVERSE"),
        ]
        for name, path in repos:
            if path.exists():
                self._repos[name] = path

    def get_repository(self, name: str) -> Optional[Path]:
        """Get path to named repository."""
        return self._repos.get(name)

    def list_repositories(self) -> list[str]:
        """List all discovered repositories."""
        return list(self._repos.keys())

    def get_state(self) -> dict[str, Any]:
        """Get canonical state."""
        return {
            "component": self._canonical_id,
            "initialized": self._initialized,
            "repositories": len(self._repos),
            "repo_names": list(self._repos.keys()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


_INSTANCE: Optional[RepositoryBridge] = None


def get_repository_bridge() -> RepositoryBridge:
    """Get canonical singleton."""
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = RepositoryBridge()
    return _INSTANCE
