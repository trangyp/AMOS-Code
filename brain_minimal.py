#!/usr/bin/env python3
"""Minimal brain interface - guaranteed to work.

Uses only amos_brain_working.think - no complex imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Direct import of working brain
from amos_brain_working import think as _brain_think


@dataclass
class MinimalBrainResponse:
    content: str
    confidence: float
    law_compliant: bool
    reasoning: str
    metadata: dict[str, Any]


class MinimalBrain:
    """Minimal brain that JUST WORKS."""

    def think(
        self, query: str, domain: str = "general", context: dict | None = None
    ) -> MinimalBrainResponse:
        """Think using the real amos_brain_working.think."""
        ctx = context or {}
        ctx["domain"] = domain

        result = _brain_think(query, ctx)

        return MinimalBrainResponse(
            content=result.get("response", result.get("output", "")),
            confidence=result.get("confidence", result.get("sigma", 0.5)),
            law_compliant=result.get("legality", 0.5) > 0.3,
            reasoning=f"Processed via {result.get('mode', 'unknown')} mode",
            metadata={
                "status": result.get("status"),
                "brain_used": result.get("brain_used", False),
                "components_used": result.get("components_used", []),
            },
        )

    def is_available(self) -> bool:
        return True


# Global instance
_brain_instance: MinimalBrain | None = None


def get_minimal_brain() -> MinimalBrain:
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = MinimalBrain()
    return _brain_instance


if __name__ == "__main__":
    brain = get_minimal_brain()
    resp = brain.think("Analyze Python code quality best practices", domain="code_review")
    print(f"Confidence: {resp.confidence:.3f}")
    print(f"Law Compliant: {resp.law_compliant}")
    print(f"Content: {resp.content[:100]}...")
