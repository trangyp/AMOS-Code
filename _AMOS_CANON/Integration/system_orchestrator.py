#!/usr/bin/env python3
"""system_orchestrator.py - AMOS System Orchestrator

Central orchestration layer for AMOS canonical components.
Coordinates initialization and lifecycle management.

Part of AMOS Canon - One Source of Truth
"""

from __future__ import annotations
from typing import Any, Optional
from datetime import datetime, timezone


class SystemOrchestrator:
    """Canonical system orchestrator for AMOS."""

    def __init__(self) -> None:
        self._initialized = False
        self._canonical_id = "system_orchestrator"
        self._components: dict[str, Any] = {}
        self._initialization_order: list[str] = []

    def initialize(self) -> bool:
        """Initialize canonical system orchestrator."""
        self._initialized = True
        return True

    def register_component(self, name: str, component: Any,
                           dependencies: list[str] | None = None) -> None:
        """Register a component with orchestrator."""
        self._components[name] = {
            "component": component,
            "dependencies": dependencies or [],
            "initialized": False
        }

    def initialize_component(self, name: str) -> bool:
        """Initialize a registered component."""
        if name not in self._components:
            return False
        entry = self._components[name]
        # Initialize dependencies first
        for dep in entry["dependencies"]:
            if not self.initialize_component(dep):
                return False
        # Initialize this component
        comp = entry["component"]
        if hasattr(comp, "initialize"):
            comp.initialize()
        entry["initialized"] = True
        return True

    def get_state(self) -> dict[str, Any]:
        """Get canonical state."""
        return {
            "component": self._canonical_id,
            "initialized": self._initialized,
            "components_registered": len(self._components),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


_INSTANCE: Optional[SystemOrchestrator] = None


def get_system_orchestrator() -> SystemOrchestrator:
    """Get canonical singleton."""
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = SystemOrchestrator()
    return _INSTANCE
