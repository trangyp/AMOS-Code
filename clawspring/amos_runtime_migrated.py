"""AMOS Runtime - Migrated to use standalone amos_brain package.

This module provides backward compatibility for clawspring while
using the unified amos_brain package.

All functionality is now delegated to the standalone package
which provides:
- 16 core brain modules
- Tutorial, CLI, Launcher
- 32 integration tests
- Cookbook workflows
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add parent dir to path for standalone amos_brain
_parent_dir = Path(__file__).parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

# Import from standalone package
from amos_brain import AMOSBrainIntegration, get_amos_integration


def get_runtime() -> AMOSBrainIntegration:
    """Get AMOS runtime - now returns the unified brain integration.

    Maintains backward compatibility with clawspring's API
    while using the standalone amos_brain package.
    """
    return get_amos_integration()


def analyze_task(task: str, context: dict | None = None) -> dict:
    """Analyze a task with AMOS brain - delegated to standalone package.

    Args:
        task: Task description to analyze
        context: Optional context dict

    Returns:
        Analysis result with Rule of 2, Rule of 4, and recommendations
    """
    amos = get_amos_integration()

    # Run analysis
    result = amos.analyze_with_rules(task)

    # Enhance result with runtime-like structure for compatibility
    return {
        "task": task,
        "perspectives": result.get("rule_of_two", {}).get("perspectives", []),
        "quadrant_analysis": result.get("rule_of_four", {}).get("quadrants_analyzed", []),
        "recommendations": result.get("recommendations", []),
        "assumptions": result.get("assumptions", []),
        "uncertainty_flags": result.get("uncertainty_flags", []),
        "confidence": result.get("structural_integrity_score", 0.0),
    }


# Backward compatibility class
class AMOSRuntime:
    """Legacy AMOSRuntime wrapper - delegates to standalone package.

    Maintains API compatibility with existing clawspring code.
    """

    def __init__(self):
        self._amos = None

    @property
    def amos(self) -> AMOSBrainIntegration:
        """Lazy-load AMOS brain integration."""
        if self._amos is None:
            self._amos = get_amos_integration()
        return self._amos

    def bootstrap(self):
        """Initialize - now handled automatically by singleton."""
        return self

    def get_identity(self) -> dict:
        """Get system identity."""
        return {
            "system_name": "AMOS",
            "os_name": "AMOS_OS",
            "primary_purpose": "Design, analyse, and improve systems using structurally precise, biologically grounded, ethically governed reasoning.",
            "creator": "Trang Phan",
        }

    def get_law_summary(self) -> list[dict]:
        """Get global laws summary."""
        return [
            {"id": "L1", "name": "Law of Law", "priority": 1},
            {"id": "L2", "name": "Rule of 2", "priority": 2},
            {"id": "L3", "name": "Rule of 4", "priority": 3},
            {"id": "L4", "name": "Structural Integrity", "priority": 4},
            {"id": "L5", "name": "Communication", "priority": 5},
            {"id": "L6", "name": "UBI Alignment", "priority": 6},
        ]

    def execute_cognitive_task(self, task: str, context: dict | None = None) -> dict:
        """Execute task with AMOS brain."""
        return analyze_task(task, context)


# Singleton instance
_runtime_instance: AMOSRuntime | None = None


def get_runtime_legacy() -> AMOSRuntime:
    """Get legacy runtime wrapper (for backward compatibility)."""
    global _runtime_instance
    if _runtime_instance is None:
        _runtime_instance = AMOSRuntime()
    return _runtime_instance


# Export main functions for clawspring compatibility
__all__ = [
    "get_runtime",
    "get_runtime_legacy",
    "analyze_task",
    "AMOSRuntime",
    "AMOSBrainIntegration",
]
