#!/usr/bin/env python3
"""evolution_controller.py - AMOS Evolution Controller

Manages controlled evolution of canonical components.
Ensures evolution follows AMOS Constitutional Law 3.

Part of AMOS Canon - One Source of Truth
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class EvolutionPhase(Enum):
    """Phases of component evolution."""
    PROPOSED = "proposed"
    VALIDATED = "validated"
    TESTED = "tested"
    DEPLOYED = "deployed"
    RETIRED = "retired"


class EvolutionController:
    """Canonical evolution controller for AMOS."""

    def __init__(self) -> None:
        self._initialized = False
        self._canonical_id = "evolution_controller"
        self._evolutions: dict[str, Any] = {}

    def initialize(self) -> bool:
        """Initialize canonical evolution controller."""
        self._initialized = True
        return True

    def propose_evolution(self, component: str, change: str,
                          evidence: dict[str, Any]) -> str:
        """Propose an evolution with supporting evidence."""
        ts = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        evolution_id = f"evo_{component}_{ts}"
        self._evolutions[evolution_id] = {
            "component": component,
            "change": change,
            "evidence": evidence,
            "phase": EvolutionPhase.PROPOSED.value,
            "proposed": datetime.now(timezone.utc).isoformat()
            "approved": False
        }
        return evolution_id

    def approve_evolution(self, evolution_id: str) -> bool:
        """Approve an evolution for testing."""
        if evolution_id not in self._evolutions:
            return False
        self._evolutions[evolution_id]["phase"] = EvolutionPhase.VALIDATED.value
        self._evolutions[evolution_id]["approved"] = True
        return True

    def get_state(self) -> dict[str, Any]:
        """Get canonical state."""
        return {
            "component": self._canonical_id,
            "initialized": self._initialized,
            "active_evolutions": len(self._evolutions),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        }


_INSTANCE: Optional[EvolutionController] = None


def get_evolution_controller() -> EvolutionController:
    """Get canonical singleton."""
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = EvolutionController()
    return _INSTANCE
