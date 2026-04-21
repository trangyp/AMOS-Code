#!/usr/bin/env python3
"""Canon Bridge - Bridges _AMOS_CANON with AMOS organism components."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .canon_core import CanonCore
from .canon_loader import CanonLoader
from .canon_enforcer import CanonEnforcer
from .canon_registry import CanonRegistry


@dataclass
class BridgeStatus:
    timestamp: str
    canon_loaded: bool = False
    glossary_count: int = 0
    agents_count: int = 0
    kernels_count: int = 0
    rules_count: int = 0
    standards_count: int = 0
    ready: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "canon_loaded": self.canon_loaded,
            "glossary_count": self.glossary_count,
            "agents_count": self.agents_count,
            "kernels_count": self.kernels_count,
            "rules_count": self.rules_count,
            "standards_count": self.standards_count,
            "ready": self.ready,
        }


class CanonBridge:
    _instance: CanonBridge | None = None

    def __new__(cls) -> CanonBridge:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self._core = CanonCore()
        self._loader: CanonLoader | None = None
        self._enforcer = CanonEnforcer(self._core)
        self._registry = CanonRegistry(self._core)
        self._status = BridgeStatus(timestamp=datetime.now(timezone.utc).isoformat())

    async def initialize(self) -> bool:
        from .canon_loader import get_canon_loader
        self._loader = await get_canon_loader()
        self._core = self._loader.get_core()
        self._enforcer = CanonEnforcer(self._core)
        self._registry = CanonRegistry(self._core)
        stats = self._core.get_stats()
        self._status = BridgeStatus(
            timestamp=datetime.now(timezone.utc).isoformat(),
            canon_loaded=self._loader.ready,
            glossary_count=stats.get("total_glossary_entries", 0),
            agents_count=stats.get("total_agents", 0),
            kernels_count=stats.get("total_kernels", 0),
            rules_count=stats.get("total_rules", 0),
            standards_count=stats.get("total_standards", 0),
            ready=self._loader.ready,
        )
        return self._status.ready

    def get_status(self) -> dict[str, Any]:
        return self._status.to_dict()

    def get_core(self) -> CanonCore:
        return self._core

    def get_loader(self) -> CanonLoader | None:
        return self._loader

    def get_enforcer(self) -> CanonEnforcer:
        return self._enforcer

    def get_registry(self) -> CanonRegistry:
        return self._registry

    def sync_to_organism(self) -> dict[str, Any]:
        if not self._loader:
            return {"error": "Bridge not initialized"}
        glossary = self._registry.export_registry("glossary")
        agents = self._registry.export_registry("agents")
        kernels = self._registry.export_registry("kernels")
        return {
            "glossary_synced": len(glossary),
            "agents_synced": len(agents),
            "kernels_synced": len(kernels),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def validate_organism_compliance(self) -> dict[str, Any]:
        from .canon_validator import CanonValidator
        validator = CanonValidator(self._core)
        dirs_to_check = ["AMOS_ORGANISM_OS", "amos_brain", "backend/api"]
        all_results = []
        for dir_name in dirs_to_check:
            dir_path = Path(dir_name)
            if dir_path.exists():
                results = validator.validate_directory(dir_path)
                all_results.extend(results)
        summary = validator.get_summary(all_results)
        return {
            "validation_summary": summary,
            "total_issues": summary.get("total_issues", 0),
            "critical_issues": summary.get("critical_issues", 0),
            "compliant": summary.get("critical_issues", 0) == 0,
        }


_bridge: CanonBridge | None = None


async def get_canon_bridge() -> CanonBridge:
    global _bridge
    if _bridge is None:
        _bridge = CanonBridge()
        await _bridge.initialize()
    return _bridge


def get_bridge_sync() -> CanonBridge | None:
    return _bridge
