"""Canon Cognitive Processor - Brain processing with Canon knowledge integration.

Real-time integration of AMOS Canon definitions into cognitive processing:
- Canonical term resolution from actual Canon files
- Domain-specific context enrichment
- Canon-aware agent selection
- Real-time knowledge graph access

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional

from .canon_knowledge_engine import CanonKnowledgeEntry, get_canon_knowledge_engine


@dataclass
class CanonCognitiveResult:
    """Cognitive processing result with Canon enrichment."""

    content: str
    domain: str
    confidence: float
    processing_time_ms: float
    canon_sources: list[str] = field(default_factory=list)
    canon_terms_used: dict[str, str] = field(default_factory=dict)
    relevant_entries: list[CanonKnowledgeEntry] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class CanonCognitiveProcessor:
    """Cognitive processor with real-time Canon knowledge access.

    Integrates the Canon Knowledge Engine into brain processing
    to provide canonical context enrichment during task execution.
    """

    def __init__(self) -> None:
        self._knowledge_engine = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize with Canon knowledge engine."""
        if self._initialized:
            return True

        self._knowledge_engine = get_canon_knowledge_engine()
        self._initialized = True
        return True

    def process(
        self,
        query: str,
        domain: str = "general",
        context: dict[str, Optional[Any]] = None,
    ) -> CanonCognitiveResult:
        """Process query with Canon enrichment.

        Args:
            query: Query to process
            domain: Cognitive domain
            context: Additional context

        Returns:
            CanonCognitiveResult with enriched content
        """
        if not self._initialized:
            self.initialize()

        start_time = time.perf_counter()

        # Get relevant Canon knowledge
        relevant_entries = self._find_relevant_knowledge(query, domain)

        # Extract Canon terms
        canon_terms = self._extract_canon_terms(relevant_entries)

        # Build enriched context
        canon_context = self._build_canon_context(relevant_entries, canon_terms)

        # Simulate cognitive processing with Canon context
        processed_content = self._process_with_context(query, canon_context)

        # Calculate confidence based on Canon coverage
        confidence = self._calculate_confidence(len(relevant_entries), len(canon_terms))

        processing_time_ms = (time.perf_counter() - start_time) * 1000

        return CanonCognitiveResult(
            content=processed_content,
            domain=domain,
            confidence=confidence,
            processing_time_ms=processing_time_ms,
            canon_sources=[e.source_file for e in relevant_entries[:5]],
            canon_terms_used=dict(list(canon_terms.items())[:10]),
            relevant_entries=relevant_entries,
            metadata={
                "context": context or {},
                "canon_entries_found": len(relevant_entries),
                "canon_terms_extracted": len(canon_terms),
            },
        )

    def _find_relevant_knowledge(self, query: str, domain: str) -> list[CanonKnowledgeEntry]:
        """Find Canon knowledge relevant to query."""
        if not self._knowledge_engine:
            return []

        # Search in specified domain
        results = []

        # Get domain knowledge
        index = self._knowledge_engine.get_domain_knowledge(domain)
        if index:
            results.extend(index.search(query))

        # Also search in core domain for general knowledge
        if domain != "core":
            core_index = self._knowledge_engine.get_domain_knowledge("core")
            if core_index:
                results.extend(core_index.search(query))

        # Remove duplicates while preserving order
        seen = set()
        unique_results = []
        for entry in results:
            if entry.key not in seen:
                seen.add(entry.key)
                unique_results.append(entry)

        return unique_results[:10]  # Return top 10

    def _extract_canon_terms(self, entries: list[CanonKnowledgeEntry]) -> dict[str, str]:
        """Extract searchable terms from Canon entries."""
        terms = {}

        for entry in entries:
            content = entry.content
            if not isinstance(content, dict):
                continue

            # Extract from meta if available
            if "meta" in content and isinstance(content["meta"], dict):
                meta = content["meta"]
                codename = meta.get("codename", entry.key)
                description = meta.get("description", "")
                if codename and description:
                    terms[codename] = description

            # Extract from layer descriptions
            for key, value in content.items():
                if isinstance(value, dict):
                    if "description" in value:
                        terms[key] = value["description"]
                    elif "overview" in value and isinstance(value["overview"], dict):
                        overview = value["overview"]
                        if "purpose" in overview:
                            terms[key] = overview["purpose"]

        return terms

    def _build_canon_context(
        self,
        entries: list[CanonKnowledgeEntry],
        terms: dict[str, str],
    ) -> str:
        """Build Canon context string for processing."""
        context_parts = []

        # Add entry information
        for entry in entries[:5]:
            context_parts.append(f"[{entry.entry_type.upper()}] {entry.key}")

        # Add relevant terms
        for term, description in list(terms.items())[:5]:
            context_parts.append(f"  {term}: {description[:100]}...")

        return "\n".join(context_parts)

    def _process_with_context(self, query: str, canon_context: str) -> str:
        """Process query with Canon context.

        In real implementation, this would call an LLM or
        reasoning engine with the enriched context.
        """
        # Return Canon-enriched processing result
        if canon_context:
            return f"Processed: {query}\n\n[With Canon Knowledge]\n{canon_context[:500]}..."
        return f"Processed: {query}"

    def _calculate_confidence(self, num_entries: int, num_terms: int) -> float:
        """Calculate confidence score based on Canon coverage."""
        # More Canon knowledge = higher confidence
        base_confidence = 0.6
        entry_boost = min(num_entries * 0.03, 0.2)
        term_boost = min(num_terms * 0.01, 0.1)

        return min(base_confidence + entry_boost + term_boost, 0.95)

    def get_canon_stats(self) -> dict[str, Any]:
        """Get Canon knowledge statistics."""
        if not self._knowledge_engine:
            return {"error": "Not initialized"}
        return self._knowledge_engine.get_stats()


# Global processor instance
_canon_processor: Optional[CanonCognitiveProcessor] = None


def get_canon_cognitive_processor() -> CanonCognitiveProcessor:
    """Get or create global Canon cognitive processor."""
    global _canon_processor
    if _canon_processor is None:
        _canon_processor = CanonCognitiveProcessor()
        _canon_processor.initialize()
    return _canon_processor


def canon_process(query: str, domain: str = "general") -> CanonCognitiveResult:
    """Process query with Canon enrichment - convenience function.

    Usage:
        result = canon_process("How does brain cognition work?", "cognitive")
        print(f"Confidence: {result.confidence}")
        print(f"Canon sources: {result.canon_sources}")
    """
    processor = get_canon_cognitive_processor()
    return processor.process(query, domain)
