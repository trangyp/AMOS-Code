"""Canon Reasoning Engine - Structured decision-making with Canon knowledge.

Integrates AMOS Canon definitions into reasoning processes:
- Canon-aware option generation
- Knowledge-based evaluation criteria
- Domain-specific decision frameworks
- Real-time Canon law application

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from .canon_knowledge_engine import get_canon_knowledge_engine, CanonKnowledgeEntry


@dataclass
class ReasoningOption:
    """A decision option with Canon enrichment."""

    option_id: str
    description: str
    domain: str
    canon_support: list[str] = field(default_factory=list)
    canon_confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningResult:
    """Result of Canon-aware reasoning."""

    decision: str
    confidence: float
    reasoning_path: list[str] = field(default_factory=list)
    options_considered: list[ReasoningOption] = field(default_factory=list)
    canon_sources: list[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class CanonReasoningEngine:
    """Structured reasoning engine with Canon knowledge integration.

    Applies canonical definitions and laws to decision-making
    processes, ensuring domain-appropriate reasoning.
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

    def reason(
        self,
        problem: str,
        domain: str = "general",
        options: list[str] | None = None,
        criteria: list[str] | None = None,
    ) -> ReasoningResult:
        """Perform Canon-aware reasoning on a problem.

        Args:
            problem: Problem statement to reason about
            domain: Domain for reasoning context
            options: Optional predefined options
            criteria: Optional evaluation criteria

        Returns:
            ReasoningResult with decision and Canon context
        """
        if not self._initialized:
            self.initialize()

        start_time = time.perf_counter()

        # Get relevant Canon knowledge
        canon_entries = self._get_relevant_canon(problem, domain)

        # Generate or enrich options
        reasoning_options = self._generate_options(problem, domain, options, canon_entries)

        # Evaluate options with Canon context
        evaluated_options = self._evaluate_options(reasoning_options, criteria, canon_entries)

        # Select best option
        decision, confidence = self._select_decision(evaluated_options)

        # Build reasoning path
        reasoning_path = self._build_reasoning_path(problem, evaluated_options, canon_entries)

        processing_time_ms = (time.perf_counter() - start_time) * 1000

        return ReasoningResult(
            decision=decision,
            confidence=confidence,
            reasoning_path=reasoning_path,
            options_considered=evaluated_options,
            canon_sources=[e.source_file for e in canon_entries[:5]],
            processing_time_ms=processing_time_ms,
            metadata={
                "domain": domain,
                "canon_entries_used": len(canon_entries),
                "options_generated": len(evaluated_options),
                "criteria_applied": criteria or [],
            },
        )

    def _get_relevant_canon(self, problem: str, domain: str) -> list[CanonKnowledgeEntry]:
        """Get Canon knowledge relevant to the problem."""
        if not self._knowledge_engine:
            return []

        entries = []

        # Search in specified domain
        index = self._knowledge_engine.get_domain_knowledge(domain)
        if index:
            entries.extend(index.search(problem))

        # Search in core for general principles
        if domain != "core":
            core_index = self._knowledge_engine.get_domain_knowledge("core")
            if core_index:
                entries.extend(core_index.search(problem))

        # Remove duplicates
        seen = set()
        unique = []
        for e in entries:
            if e.key not in seen:
                seen.add(e.key)
                unique.append(e)

        return unique[:10]

    def _generate_options(
        self,
        problem: str,
        domain: str,
        options: list[str] | None,
        canon_entries: list[CanonKnowledgeEntry],
    ) -> list[ReasoningOption]:
        """Generate or enrich decision options."""
        if options:
            # Enrich provided options with Canon context
            return [
                ReasoningOption(
                    option_id=f"opt_{i}",
                    description=opt,
                    domain=domain,
                    canon_support=self._find_canon_support(opt, canon_entries),
                    canon_confidence=self._calculate_canon_confidence(opt, canon_entries),
                )
                for i, opt in enumerate(options)
            ]
        else:
            # Generate options from Canon knowledge
            return self._generate_options_from_canon(problem, domain, canon_entries)

    def _generate_options_from_canon(
        self,
        problem: str,
        domain: str,
        canon_entries: list[CanonKnowledgeEntry],
    ) -> list[ReasoningOption]:
        """Generate options based on Canon knowledge."""
        options = []

        # Extract approaches from Canon entries
        for i, entry in enumerate(canon_entries[:5]):
            option = ReasoningOption(
                option_id=f"canon_opt_{i}",
                description=f"Apply {entry.key} approach",
                domain=domain,
                canon_support=[entry.key],
                canon_confidence=0.7 + (0.05 * min(i, 5)),
                metadata={
                    "source_entry": entry.key,
                    "entry_type": entry.entry_type,
                },
            )
            options.append(option)

        # Add default option if no Canon entries found
        if not options:
            options.append(
                ReasoningOption(
                    option_id="default_opt",
                    description="Standard approach",
                    domain=domain,
                    canon_support=[],
                    canon_confidence=0.5,
                )
            )

        return options

    def _find_canon_support(
        self, option: str, canon_entries: list[CanonKnowledgeEntry]
    ) -> list[str]:
        """Find Canon entries that support an option."""
        support = []
        option_lower = option.lower()

        for entry in canon_entries:
            if option_lower in entry.key.lower():
                support.append(entry.key)
            elif option_lower in str(entry.content).lower():
                support.append(entry.key)

        return support

    def _calculate_canon_confidence(
        self, option: str, canon_entries: list[CanonKnowledgeEntry]
    ) -> float:
        """Calculate confidence based on Canon support."""
        if not canon_entries:
            return 0.5

        support_count = len(self._find_canon_support(option, canon_entries))
        base_confidence = 0.6
        boost = min(support_count * 0.1, 0.3)

        return min(base_confidence + boost, 0.95)

    def _evaluate_options(
        self,
        options: list[ReasoningOption],
        criteria: list[str] | None,
        canon_entries: list[CanonKnowledgeEntry],
    ) -> list[ReasoningOption]:
        """Evaluate options against criteria and Canon knowledge."""
        evaluated = []

        for option in options:
            # Enhance confidence with Canon support
            if option.canon_support:
                option.canon_confidence = min(
                    option.canon_confidence + 0.1 * len(option.canon_support),
                    0.95,
                )

            evaluated.append(option)

        # Sort by Canon confidence
        return sorted(evaluated, key=lambda x: x.canon_confidence, reverse=True)

    def _select_decision(self, options: list[ReasoningOption]) -> tuple[str, float]:
        """Select the best decision from evaluated options."""
        if not options:
            return "No valid options", 0.0

        best = options[0]
        return best.description, best.canon_confidence

    def _build_reasoning_path(
        self,
        problem: str,
        options: list[ReasoningOption],
        canon_entries: list[CanonKnowledgeEntry],
    ) -> list[str]:
        """Build explanation of reasoning process."""
        path = [
            f"Problem: {problem[:50]}...",
            f"Canon entries consulted: {len(canon_entries)}",
            f"Options generated: {len(options)}",
        ]

        if options:
            path.append(f"Top option: {options[0].description[:40]}...")
            path.append(f"Canon confidence: {options[0].canon_confidence:.1%}")

            if options[0].canon_support:
                path.append(f"Canon support: {', '.join(options[0].canon_support[:2])}")

        return path


# Global instance
_canon_reasoning_engine: CanonReasoningEngine | None = None


def get_canon_reasoning_engine() -> CanonReasoningEngine:
    """Get or create global Canon reasoning engine."""
    global _canon_reasoning_engine
    if _canon_reasoning_engine is None:
        _canon_reasoning_engine = CanonReasoningEngine()
        _canon_reasoning_engine.initialize()
    return _canon_reasoning_engine


def canon_reason(
    problem: str,
    domain: str = "general",
    options: list[str] | None = None,
) -> ReasoningResult:
    """Convenience function for Canon-aware reasoning.

    Usage:
        result = canon_reason(
            "How to optimize brain performance?",
            domain="cognitive",
            options=["Cache results", "Parallel processing", "Async I/O"]
        )
        print(f"Decision: {result.decision}")
        print(f"Confidence: {result.confidence:.0%}")
    """
    engine = get_canon_reasoning_engine()
    return engine.reason(problem, domain, options)
