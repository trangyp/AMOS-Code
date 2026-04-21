#!/usr/bin/env python3
"""AMOS Canonical Registry

Registry for canonical entities, engines, and components.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CanonicalEntity:
    """A canonical entity in the AMOS system."""
    name: str
    category: str  # engine, agent, kernel, worker
    version: str
    location: str
    status: str = "registered"


class CanonRegistry:
    """Registry for all canonical AMOS entities."""
    
    def __init__(self):
        self.entities: dict[str, CanonicalEntity] = {}
        self._load_core_entities()
    
    def _load_core_entities(self) -> None:
        """Load core canonical entities."""
        core_entities = [
            CanonicalEntity("AMOS_OS", "kernel", "2.0.0", "AMOS_OS.py"),
            CanonicalEntity("AMOS_RUNTIME", "kernel", "1.0.0", "AMOS_RUNTIME.py"),
            CanonicalEntity("AMOS_GODMODE", "controller", "1.0.0", "AMOS_GODMODE.py"),
            CanonicalEntity("7_Intelligents", "framework", "1.0.0", "_AMOS_CANON/Core/7_Intelligents"),
            CanonicalEntity("Cognitive_Stack", "framework", "1.0.0", "_AMOS_CANON/Core/Cognitive_Stack"),
            CanonicalEntity("Ubi", "framework", "1.0.0", "_AMOS_CANON/Core/Ubi"),
            CanonicalEntity("Web", "interface", "1.0.0", "_AMOS_CANON/Core/Web"),
        ]
        for entity in core_entities:
            self.entities[entity.name] = entity
    
    def register(self, entity: CanonicalEntity) -> None:
        """Register a new canonical entity."""
        self.entities[entity.name] = entity
    
    def get(self, name: str) -> CanonicalEntity | None:
        """Get a registered entity."""
        return self.entities.get(name)
    
    def list_by_category(self, category: str) -> list[CanonicalEntity]:
        """List entities by category."""
        return [e for e in self.entities.values() if e.category == category]


def get_registry() -> CanonRegistry:
    """Get the canonical registry instance."""
    return CanonRegistry()
