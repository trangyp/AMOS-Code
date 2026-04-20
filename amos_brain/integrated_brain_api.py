from __future__ import annotations

from typing import Any, Optional

"""Integrated Brain API - High-level brain interface for external systems.

Provides a unified API for accessing brain cognitive capabilities.
"""


from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc


UTC = timezone.utc
from .facade import BrainClient


@dataclass
class BrainResponse:
    """Structured brain response."""

    content: str
    confidence: str
    law_compliant: bool
    reasoning: str
    violations: list[str]
    metadata: dict[str, Any]
    timestamp: str


class IntegratedBrainAPI:
    """High-level brain API for system integration."""

    def __init__(self) -> None:
        self._client: Optional[BrainClient] = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the brain connection."""
        if not self._initialized:
            self._client = BrainClient()
            self._initialized = True

    def think(self, query: str, domain: str = "general") -> BrainResponse:
        """Execute a brain thinking operation.

        Args:
            query: The query to process
            domain: Domain context for processing

        Returns:
            BrainResponse with results and metadata
        """
        self.initialize()
        if self._client is None:
            return BrainResponse(
                content="Brain not available",
                confidence="low",
                law_compliant=False,
                reasoning="Initialization failed",
                violations=["brain_unavailable"],
                metadata={},
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        try:
            response = self._client.think(query, domain=domain)
            return BrainResponse(
                content=response.content,
                confidence=response.confidence,
                law_compliant=response.law_compliant,
                reasoning=str(response.reasoning) if response.reasoning else "",
                violations=response.violations or [],
                metadata=response.metadata or {},
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as e:
            return BrainResponse(
                content=str(e),
                confidence="low",
                law_compliant=False,
                reasoning=f"Error: {type(e).__name__}",
                violations=["processing_error"],
                metadata={"error": str(e)},
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

    def get_status(self) -> dict[str, Any]:
        """Get brain system status."""
        return {
            "initialized": self._initialized,
            "client_ready": self._client is not None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global instance
_integrated_api: Optional[IntegratedBrainAPI] = None


def get_brain_api() -> IntegratedBrainAPI:
    """Get or create global IntegratedBrainAPI instance."""
    global _integrated_api
    if _integrated_api is None:
        _integrated_api = IntegratedBrainAPI()
    return _integrated_api
