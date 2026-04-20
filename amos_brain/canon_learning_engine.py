from __future__ import annotations

"""Canon Learning Engine - Learning with canonical knowledge integration.

Uses real AMOS Canon definitions to guide learning processes:
- Canon-aware pattern recognition
- Domain-specific learning strategies
- Knowledge-driven procedure generation
- Real-time Canon enrichment during learning

Creator: Trang Phan
Version: 3.0.0
"""

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from .canon_knowledge_engine import CanonKnowledgeEntry, get_canon_knowledge_engine


@dataclass
class LearningPattern:
    """A learned pattern with Canon context."""

    pattern_id: str
    domain: str
    description: str
    canon_sources: list[str] = field(default_factory=list)
    applicability_score: float = 0.0
    usage_count: int = 0
    success_rate: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CanonLearningResult:
    """Result of Canon-guided learning."""

    learned_patterns: list[LearningPattern] = field(default_factory=list)
    canon_sources_used: list[str] = field(default_factory=list)
    learning_time_ms: float = 0.0
    domain_coverage: dict[str, int] = field(default_factory=dict)


class CanonLearningEngine:
    """Learning engine with Canon knowledge integration.

    Uses canonical definitions from AMOS Canon files to guide
    pattern recognition and learning processes.
    """

    def __init__(self) -> None:
        self._knowledge_engine = None
        self._initialized = False
        self._pattern_cache: dict[str, LearningPattern] = {}

    def initialize(self) -> bool:
        """Initialize with Canon knowledge engine."""
        if self._initialized:
            return True

        self._knowledge_engine = get_canon_knowledge_engine()
        self._initialized = True
        return True

    def learn_from_task(
        self,
        task_description: str,
        task_domain: str,
        outcome: str,
        success: bool,
    ) -> CanonLearningResult:
        """Learn from a task execution with Canon guidance.

        Args:
            task_description: Description of the task
            task_domain: Domain of the task
            outcome: Outcome/result of the task
            success: Whether the task succeeded

        Returns:
            CanonLearningResult with learned patterns
        """
        if not self._initialized:
            self.initialize()

        start_time = time.perf_counter()

        # Get relevant Canon knowledge
        canon_entries = self._find_relevant_canon(task_description, task_domain)

        # Extract patterns with Canon context
        patterns = self._extract_patterns(task_description, task_domain, canon_entries, success)

        # Cache patterns
        for pattern in patterns:
            self._pattern_cache[pattern.pattern_id] = pattern

        learning_time_ms = (time.perf_counter() - start_time) * 1000

        return CanonLearningResult(
            learned_patterns=patterns,
            canon_sources_used=[e.source_file for e in canon_entries[:5]],
            learning_time_ms=learning_time_ms,
            domain_coverage={task_domain: len(patterns)},
        )

    def _find_relevant_canon(self, task: str, domain: str) -> list[CanonKnowledgeEntry]:
        """Find Canon knowledge relevant to learning task."""
        if not self._knowledge_engine:
            return []

        entries = []

        # Search in task domain
        index = self._knowledge_engine.get_domain_knowledge(domain)
        if index:
            entries.extend(index.search(task))

        # Search in cognitive domain for learning patterns
        cog_index = self._knowledge_engine.get_domain_knowledge("cognitive")
        if cog_index:
            entries.extend(cog_index.search("learn pattern task"))

        # Remove duplicates
        seen = set()
        unique = []
        for e in entries:
            if e.key not in seen:
                seen.add(e.key)
                unique.append(e)

        return unique[:8]

    def _extract_patterns(
        self,
        task: str,
        domain: str,
        canon_entries: list[CanonKnowledgeEntry],
        success: bool,
    ) -> list[LearningPattern]:
        """Extract learning patterns with Canon enrichment."""
        patterns = []

        # Create pattern from task
        task_hash = hashlib.sha256(task.encode()).hexdigest()[:12]
        pattern_id = f"learn_{domain}_{task_hash}"

        # Build Canon context
        canon_sources = [e.key for e in canon_entries[:3]]

        # Calculate applicability based on Canon support
        applicability = 0.6 + (0.1 * min(len(canon_sources), 3))

        pattern = LearningPattern(
            pattern_id=pattern_id,
            domain=domain,
            description=task[:100],
            canon_sources=canon_sources,
            applicability_score=applicability,
            usage_count=1,
            success_rate=1.0 if success else 0.0,
            metadata={
                "task_type": self._classify_task(task),
                "canon_entries_count": len(canon_entries),
            },
        )
        patterns.append(pattern)

        # Create additional patterns from Canon entries
        for i, entry in enumerate(canon_entries[:3]):
            canon_pattern = self._create_canon_pattern(entry, domain, i)
            if canon_pattern:
                patterns.append(canon_pattern)

        return patterns

    def _create_canon_pattern(
        self, entry: CanonKnowledgeEntry, domain: str, index: int
    ) -> Optional[LearningPattern]:
        """Create a learning pattern from a Canon entry."""
        pattern_id = f"canon_{entry.key}_{index}"

        # Extract description from entry
        description = entry.key
        if isinstance(entry.content, dict):
            if "meta" in entry.content and isinstance(entry.content["meta"], dict):
                meta = entry.content["meta"]
                if "description" in meta:
                    description = meta["description"][:100]

        return LearningPattern(
            pattern_id=pattern_id,
            domain=domain,
            description=description,
            canon_sources=[entry.key],
            applicability_score=0.85,
            usage_count=0,
            success_rate=0.9,  # High confidence for Canon-derived patterns
            metadata={
                "entry_type": entry.entry_type,
                "source_file": entry.source_file,
            },
        )

    def _classify_task(self, task: str) -> str:
        """Classify task type from description."""
        task_lower = task.lower()

        if "code" in task_lower or "program" in task_lower:
            return "coding"
        elif "design" in task_lower or "architect" in task_lower:
            return "design"
        elif "analyze" in task_lower or "review" in task_lower:
            return "analysis"
        elif "debug" in task_lower or "fix" in task_lower:
            return "debugging"
        elif "test" in task_lower:
            return "testing"
        else:
            return "general"

    def find_applicable_patterns(self, task: str, domain: str) -> list[LearningPattern]:
        """Find previously learned patterns applicable to task."""
        task_lower = task.lower()
        applicable = []

        for pattern in self._pattern_cache.values():
            # Check domain match
            if pattern.domain != domain:
                continue

            # Check description similarity
            if any(word in task_lower for word in pattern.description.lower().split()):
                applicable.append(pattern)

        # Sort by applicability score
        return sorted(applicable, key=lambda x: x.applicability_score, reverse=True)

    def get_learning_stats(self) -> dict[str, Any]:
        """Get learning engine statistics."""
        if not self._initialized:
            return {"error": "Not initialized"}

        canon_stats = self._knowledge_engine.get_stats() if self._knowledge_engine else {}

        return {
            "patterns_cached": len(self._pattern_cache),
            "domains": list(set(p.domain for p in self._pattern_cache.values())),
            "canon_entries_available": canon_stats.get("total_entries", 0),
            "canon_domains": canon_stats.get("domains", 0),
        }


# Global instance
_canon_learning_engine: Optional[CanonLearningEngine] = None


def get_canon_learning_engine() -> CanonLearningEngine:
    """Get or create global Canon learning engine."""
    global _canon_learning_engine
    if _canon_learning_engine is None:
        _canon_learning_engine = CanonLearningEngine()
        _canon_learning_engine.initialize()
    return _canon_learning_engine


def canon_learn(task: str, domain: str, outcome: str, success: bool) -> CanonLearningResult:
    """Learn from task with Canon enrichment - convenience function.

    Usage:
        result = canon_learn(
            "Design API authentication",
            "api",
            "JWT tokens implemented",
            success=True
        )
        print(f"Patterns learned: {len(result.learned_patterns)}")
    """
    engine = get_canon_learning_engine()
    return engine.learn_from_task(task, domain, outcome, success)
