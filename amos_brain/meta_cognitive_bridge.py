"""Meta-Cognitive Reflection Bridge.

Integrates meta-cognitive reflection with AMOS Brain cognition.

Provides API for:
- Recording decisions and outcomes
- Reflecting on decision patterns
- Learning from failures
- Parameter adaptation
- Self-improvement playbook generation
"""

from __future__ import annotations


from pathlib import Path
from typing import Any

# Import meta-cognitive reflection engine
try:
    from repo_doctor.meta_cognitive_reflection import (
        MetaCognitiveReflectionEngine,
        ReflectionResult,
    )

    META_COGNITIVE_AVAILABLE = True
except ImportError:
    META_COGNITIVE_AVAILABLE = False


class MetaCognitiveBridge:
    """Bridge between meta-cognitive reflection and AMOS Brain."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self._engine: MetaCognitiveReflectionEngine | None = None

    @property
    def engine(self) -> MetaCognitiveReflectionEngine | None:
        """Lazy initialization of meta-cognitive engine."""
        if self._engine is None and META_COGNITIVE_AVAILABLE:
            self._engine = MetaCognitiveReflectionEngine(self.repo_path)
        return self._engine

    def record_decision(
        self,
        decision_type: str,
        context: dict[str, Any],
        outcome: dict[str, Any],
        confidence: float,
        success: bool,
    ) -> dict[str, Any]:
        """Record a decision for future reflection."""
        if not META_COGNITIVE_AVAILABLE or self.engine is None:
            return {"error": "meta_cognitive_engine not available"}

        record = self.engine.record_decision(decision_type, context, outcome, confidence, success)
        return {
            "decision_id": record.decision_id,
            "timestamp": record.timestamp,
            "type": record.decision_type,
            "success": record.success,
        }

    def record_failure(
        self,
        failure_type: str,
        context: dict[str, Any],
        action_taken: str,
        consequence: str,
    ) -> dict[str, Any]:
        """Record a failure for pattern detection."""
        if not META_COGNITIVE_AVAILABLE or self.engine is None:
            return {"error": "meta_cognitive_engine not available"}

        pattern = self.engine.record_failure(failure_type, context, action_taken, consequence)
        if pattern:
            return {
                "pattern_id": pattern.pattern_id,
                "failure_type": pattern.failure_type,
                "occurrences": pattern.occurrences,
                "severity": pattern.severity.value,
                "is_repeat": pattern.occurrences > 1,
            }
        return {"recorded": True, "new_pattern": True}

    def should_avoid(self, context: dict[str, Any], action: str) -> dict[str, Any]:
        """Check if an action should be avoided based on past failures."""
        if not META_COGNITIVE_AVAILABLE or self.engine is None:
            return {"error": "meta_cognitive_engine not available"}

        should_avoid, reason = self.engine.should_avoid(context, action)
        return {
            "should_avoid": should_avoid,
            "reason": reason,
        }

    def reflect(self) -> dict[str, Any]:
        """Perform comprehensive meta-cognitive reflection."""
        if not META_COGNITIVE_AVAILABLE or self.engine is None:
            return {"error": "meta_cognitive_engine not available"}

        result = self.engine.reflect()
        return result.to_dict()

    def adapt_parameter(self, name: str, performance_delta: float) -> dict[str, Any]:
        """Adapt a parameter based on performance feedback."""
        if not META_COGNITIVE_AVAILABLE or self.engine is None:
            return {"error": "meta_cognitive_engine not available"}

        param = self.engine.adapt_parameter(name, performance_delta)
        if param:
            return param.to_dict()
        return {"error": f"Parameter '{name}' not found"}

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive meta-cognitive status."""
        if not META_COGNITIVE_AVAILABLE or self.engine is None:
            return {"error": "meta_cognitive_engine not available"}

        return self.engine.get_status()

    def get_improvement_suggestions(self) -> dict[str, Any]:
        """Get improvement suggestions."""
        if not META_COGNITIVE_AVAILABLE or self.engine is None:
            return {"error": "meta_cognitive_engine not available"}

        suggestions = self.engine.get_improvement_suggestions()
        return {
            "suggestions": suggestions,
            "count": len(suggestions),
        }


def get_meta_cognitive_bridge(repo_path: str | Path) -> MetaCognitiveBridge:
    """Factory function to get meta-cognitive bridge."""
    return MetaCognitiveBridge(repo_path)
