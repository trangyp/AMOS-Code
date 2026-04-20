"""Cognitive Engine - Core cognitive processing engine.

Provides structured cognitive operations for the AMOS brain.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc
from typing import Any


from .canon_bridge import get_canon_bridge
from .facade import BrainClient


@dataclass
class CognitiveResult:
    """Result of cognitive processing."""

    content: str
    confidence: str
    domain: str
    processing_time_ms: float
    timestamp: str
    metadata: dict[str, Any]


class CognitiveEngine:
    """Core cognitive processing engine with Canon integration."""

    def __init__(self) -> None:
        self._client: BrainClient | None = None
        self._canon_bridge = None

    async def initialize(self) -> None:
        """Initialize the cognitive engine with Canon."""
        if self._client is None:
            self._client = BrainClient()
        if self._canon_bridge is None:
            self._canon_bridge = await get_canon_bridge()

    async def process(
        self, query: str, domain: str = "general", context: dict[str, Any] = None
    ) -> CognitiveResult:
        """Process a cognitive query.

        Args:
            query: The query to process
            domain: Domain for processing
            context: Additional context

        Returns:
            CognitiveResult with processing results
        """
        await self.initialize()
        start_time = time.perf_counter()

        # Enrich query with Canon context
        canon_context = None
        if self._canon_bridge:
            canon_context = self._canon_bridge.get_context_for_domain(domain)
            query = self._canon_bridge.enrich_query(query, domain)

        if self._client is None:
            return CognitiveResult(
                content="Engine not initialized",
                confidence="low",
                domain=domain,
                processing_time_ms=0.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
                metadata={"error": "initialization_failed"},
            )

        try:
            response = self._client.think(query, domain=domain)
            processing_time_ms = (time.perf_counter() - start_time) * 1000

            return CognitiveResult(
                content=response.content,
                confidence=response.confidence,
                domain=domain,
                processing_time_ms=processing_time_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
                metadata={
                    "law_compliant": response.law_compliant,
                    "violations": response.violations,
                    "context": context or {},
                    "canon_context": {
                        "domain": canon_context.domain if canon_context else None,
                        "terms_available": len(canon_context.glossary_terms)
                        if canon_context
                        else 0,
                        "agents_available": len(canon_context.applicable_agents)
                        if canon_context
                        else 0,
                    },
                },
            )
        except Exception as e:
            processing_time_ms = (time.perf_counter() - start_time) * 1000

            return CognitiveResult(
                content=str(e),
                confidence="low",
                domain=domain,
                processing_time_ms=processing_time_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
                metadata={"error": type(e).__name__},
            )


# Global engine instance
_cognitive_engine: CognitiveEngine | None = None


def get_cognitive_engine() -> CognitiveEngine:
    """Get or create global cognitive engine."""
    global _cognitive_engine
    if _cognitive_engine is None:
        _cognitive_engine = CognitiveEngine()
    return _cognitive_engine
