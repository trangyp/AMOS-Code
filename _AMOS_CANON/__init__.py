#!/usr/bin/env python3
"""_AMOS_CANON - Canonical Core for AMOS System.

This module provides the canonical foundation for the AMOS ecosystem.
"""

from __future__ import annotations

from .canon_core import (
    CanonCore,
    CanonDefinition,
    CanonStatus,
    CanonPriority,
    CanonCategory,
    CanonRule,
    CanonStandard,
    CanonGlossaryEntry,
    CanonAgent,
    CanonKernel,
)
from .canon_loader import CanonLoader, get_canon_loader
from .canon_enforcer import CanonEnforcer, Violation
from .canon_validator import CanonValidator, ValidationResult
from .canon_registry import CanonRegistry
from .canon_bridge import CanonBridge, get_canon_bridge

__version__ = "1.0.0"
__author__ = "Trang"

__all__ = [
    "CanonCore",
    "CanonDefinition",
    "CanonStatus",
    "CanonPriority",
    "CanonCategory",
    "CanonRule",
    "CanonStandard",
    "CanonGlossaryEntry",
    "CanonAgent",
    "CanonKernel",
    "CanonLoader",
    "get_canon_loader",
    "CanonEnforcer",
    "Violation",
    "CanonValidator",
    "ValidationResult",
    "CanonRegistry",
    "CanonBridge",
    "get_canon_bridge",
]
