"""Canon Query Engine - Domain-aware brain query processing with Canon context.

Integrates AMOS Canon definitions into brain query processing for:
- Domain-aware query enrichment
- Canonical term resolution
- Agent registry lookups
- Engine capability detection

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from amos_brain.canon_bridge import get_canon_bridge
from amos_brain.cognitive_engine import get_cognitive_engine


@dataclass
class CanonQueryResult:
    """Result from a Canon-aware query."""

    query: str
    domain: str
    canon_terms_used: list[str]
    canon_agents_consulted: list[str]
    canon_engines_referenced: list[str]
    response: str
    confidence: float
    metadata: dict[str, Any]


class CanonQueryEngine:
    """Engine for processing brain queries with Canon context enrichment.

    Makes canonical definitions available during brain query processing
    to improve response quality and domain accuracy.
    """

    def __init__(self):
        self._canon_bridge = None
        self._cognitive_engine = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the Canon query engine."""
        if self._initialized:
            return True

        self._canon_bridge = await get_canon_bridge()
        self._cognitive_engine = get_cognitive_engine()
        await self._cognitive_engine.initialize()
        self._initialized = True
        return True

    async def query(
        self,
        query: str,
        domain: str = "general",
        context: dict[str, Any] | None = None,
    ) -> CanonQueryResult:
        """Process a query with Canon context enrichment.

        Args:
            query: The query string
            domain: Domain for Canon context (brain, agent, kernel, etc.)
            context: Additional context for the query

        Returns:
            CanonQueryResult with enriched response
        """
        if not self._initialized:
            await self.initialize()

        # Get Canon context for domain
        canon_ctx = self._canon_bridge.get_context_for_domain(domain)

        # Enrich query with Canon terms
        enriched_query = self._canon_bridge.enrich_query(query, domain)

        # Build Canon metadata
        canon_metadata = {
            "domain": canon_ctx.domain,
            "terms_available": len(canon_ctx.glossary_terms),
            "applicable_agents": canon_ctx.applicable_agents,
            "relevant_engines": canon_ctx.relevant_engines,
        }

        # Process through cognitive engine
        cog_result = await self._cognitive_engine.process(
            thought=enriched_query,
            context={**(context or {}), "canon_context": canon_metadata},
        )

        return CanonQueryResult(
            query=query,
            domain=domain,
            canon_terms_used=list(canon_ctx.glossary_terms.keys()),
            canon_agents_consulted=canon_ctx.applicable_agents,
            canon_engines_referenced=canon_ctx.relevant_engines,
            response=cog_result.content if hasattr(cog_result, "content") else str(cog_result),
            confidence=getattr(cog_result, "confidence", 0.5),
            metadata={
                "canon_context": canon_metadata,
                "original_query": query,
                "enriched_query": enriched_query,
            },
        )

    async def multi_domain_query(
        self,
        query: str,
        domains: list[str],
        context: dict[str, Any] | None = None,
    ) -> list[CanonQueryResult]:
        """Query across multiple domains and aggregate results.

        Args:
            query: The query string
            domains: List of domains to query
            context: Additional context

        Returns:
            List of CanonQueryResult for each domain
        """
        if not self._initialized:
            await self.initialize()

        results = []
        for domain in domains:
            result = await self.query(query, domain, context)
            results.append(result)
        return results

    def get_domain_suggestions(self, query: str) -> list[str]:
        """Suggest relevant domains based on query content.

        Args:
            query: The query string

        Returns:
            List of suggested domain names
        """
        query_lower = query.lower()
        suggestions = []

        # Domain keyword mappings
        domain_keywords = {
            "brain": ["cognitive", "think", "reason", "brain", "mind"],
            "agent": ["agent", "task", "action", "execute"],
            "kernel": ["kernel", "core", "runtime", "execute"],
            "api": ["api", "endpoint", "rest", "http"],
            "database": ["database", "db", "sql", "postgres"],
            "security": ["security", "auth", "encrypt", "protect"],
        }

        for domain, keywords in domain_keywords.items():
            if any(kw in query_lower for kw in keywords):
                suggestions.append(domain)

        return suggestions if suggestions else ["general"]


# Singleton instance
_canon_query_engine: CanonQueryEngine | None = None


async def get_canon_query_engine() -> CanonQueryEngine:
    """Get or create the Canon query engine singleton."""
    global _canon_query_engine
    if _canon_query_engine is None:
        _canon_query_engine = CanonQueryEngine()
        await _canon_query_engine.initialize()
    return _canon_query_engine


async def canon_query(
    query: str,
    domain: str = "general",
    context: dict[str, Any] | None = None,
) -> CanonQueryResult:
    """Convenience function for Canon-aware queries.

    Usage:
        result = await canon_query("How do agents work?", domain="agent")
        print(result.response)
        print(f"Terms used: {result.canon_terms_used}")
    """
    engine = await get_canon_query_engine()
    return await engine.query(query, domain, context)
