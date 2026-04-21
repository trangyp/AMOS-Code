#!/usr/bin/env python3
"""
law_engine.py - AMOS Canonical Law Engine

Enforces AMOS Constitutional Laws across all components.
Provides law compliance verification and enforcement.

Part of AMOS Canon - One Source of Truth
"""

from __future__ import annotations
from typing import Any, Optional, Callable
from datetime import datetime, timezone
from enum import Enum


class LawPriority(Enum):
    """Priority levels for AMOS Laws."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LawViolation:
    """Represents a violation of an AMOS Law."""

    def __init__(self, law_id: str, message: str, priority: LawPriority) -> None:
        self.law_id = law_id
        self.message = message
        self.priority = priority
        self.timestamp = datetime.now(timezone.utc).isoformat()


class LawEngine:
    """Canonical law enforcement engine for AMOS."""

    def __init__(self) -> None:
        self._initialized = False
        self._canonical_id = "law_engine"
        self._laws: dict[str, dict[str, Any]] = {}
        self._violations: list[LawViolation] = []

    def initialize(self) -> bool:
        """Initialize canonical law engine."""
        self._initialized = True
        self._register_constitutional_laws()
        return True

    def _register_constitutional_laws(self) -> None:
        """Register AMOS Constitutional Laws."""
        self._laws = {
            "LAW_0": {
                "name": "Single Process",
                "description": "Exactly one process. No subprocesses.",
                "priority": LawPriority.CRITICAL
            },
            "LAW_1": {
                "name": "Source of Truth",
                "description": "One canonical source for each concept.",
                "priority": LawPriority.CRITICAL
            },
            "LAW_2": {
                "name": "Explicit Contracts",
                "description": "All interactions via explicit contracts.",
                "priority": LawPriority.HIGH
            },
            "LAW_3": {
                "name": "Evidence-Based Evolution",
                "description": "Evolution triggered by evidence.",
                "priority": LawPriority.HIGH
            }
        }

    def check_compliance(self, component: str, action: str) -> list[LawViolation]:
        """Check if action complies with all laws."""
        violations = []
        # Law 0: Check for subprocess creation
        if "subprocess" in action.lower():
            violations.append(LawViolation(
                "LAW_0", f"Subprocess detected in {component}", LawPriority.CRITICAL
            ))
        return violations

    def get_state(self) -> dict[str, Any]:
        """Get canonical state."""
        return {
            "component": self._canonical_id,
            "initialized": self._initialized,
            "laws_registered": len(self._laws),
            "violations_count": len(self._violations),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


_INSTANCE: Optional[LawEngine] = None


def get_law_engine() -> LawEngine:
    """Get canonical singleton."""
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = LawEngine()
    return _INSTANCE
