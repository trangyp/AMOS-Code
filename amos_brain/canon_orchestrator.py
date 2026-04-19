"""Canon Orchestrator - Coordinate Canon-aware brain components.

Integrates all Canon-integrated components for unified task execution:
- Canon Knowledge Engine for context
- Canon Cognitive Processor for enrichment
- Canon Reasoning Engine for decisions
- Canon Learning Engine for pattern recognition
- Canon Memory System for knowledge retention

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from .canon_knowledge_engine import get_canon_knowledge_engine
from .canon_cognitive_processor import get_canon_cognitive_processor
from .canon_reasoning_engine import get_canon_reasoning_engine
from .canon_learning_engine import get_canon_learning_engine
from .canon_memory_system import get_canon_memory_system


@dataclass
class OrchestrationResult:
    """Result of Canon-orchestrated task execution."""

    task_id: str
    success: bool
    result: str
    canon_context: dict[str, Any] = field(default_factory=dict)
    reasoning_path: list[str] = field(default_factory=list)
    memories_accessed: list[str] = field(default_factory=list)
    patterns_applied: list[str] = field(default_factory=list)
    processing_time_ms: float = 0.0


class CanonOrchestrator:
    """Orchestrate Canon-aware brain components for unified execution.

    Coordinates all Canon-integrated components to provide
    comprehensive Canon-enriched task processing.
    """

    def __init__(self) -> None:
        self._knowledge_engine = None
        self._cognitive_processor = None
        self._reasoning_engine = None
        self._learning_engine = None
        self._memory_system = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize all Canon components."""
        if self._initialized:
            return True

        self._knowledge_engine = get_canon_knowledge_engine()
        self._cognitive_processor = get_canon_cognitive_processor()
        self._reasoning_engine = get_canon_reasoning_engine()
        self._learning_engine = get_canon_learning_engine()
        self._memory_system = get_canon_memory_system()
        self._initialized = True
        return True

    def execute_task(
        self,
        task: str,
        domain: str = "general",
        context: dict[str, Any] | None = None,
    ) -> OrchestrationResult:
        """Execute task with full Canon orchestration.

        Args:
            task: Task description
            domain: Domain for Canon context
            context: Additional context

        Returns:
            OrchestrationResult with Canon enrichment
        """
        if not self._initialized:
            self.initialize()

        start_time = time.perf_counter()
        task_id = f"task_{int(start_time * 1000)}"

        reasoning_path = []

        # Step 1: Search relevant memories
        memories = self._memory_system.search(task, domain)
        memories_accessed = [m.memory_id for m in memories[:3]]
        reasoning_path.append(f"Accessed {len(memories_accessed)} relevant memories")

        # Step 2: Process with Canon cognitive enrichment
        cog_result = self._cognitive_processor.process_with_canon(
            task, domain, context or {}
        )
        reasoning_path.append(
            f"Cognitive processing: {cog_result.confidence:.0%} confidence"
        )

        # Step 3: Apply Canon reasoning if decision needed
        reason_result = None
        if "should" in task.lower() or "best" in task.lower():
            reason_result = self._reasoning_engine.reason(
                problem=task,
                domain=domain,
            )
            reasoning_path.append(f"Reasoning: {reason_result.decision[:30]}...")

        # Step 4: Learn from execution
        learn_result = self._learning_engine.learn_from_task(
            task_description=task,
            task_domain=domain,
            outcome=cog_result.result[:100],
            success=cog_result.success,
        )
        reasoning_path.append(f"Learned {len(learn_result.learned_patterns)} patterns")

        # Step 5: Store execution memory
        memory = self._memory_system.store(
            content=f"Executed: {task}\nResult: {cog_result.result[:100]}",
            domain=domain,
            metadata={
                "task_id": task_id,
                "confidence": cog_result.confidence,
                "canon_sources": cog_result.canon_sources,
            },
        )
        reasoning_path.append(f"Stored memory: {memory.memory_id}")

        processing_time_ms = (time.perf_counter() - start_time) * 1000

        # Build Canon context
        canon_context = {
            "knowledge_entries": self._knowledge_engine.get_stats(),
            "cognitive_confidence": cog_result.confidence,
            "cognitive_terms_used": list(cog_result.canon_terms_used.keys())[:5],
            "patterns_learned": len(learn_result.learned_patterns),
            "canon_sources": cog_result.canon_sources[:3],
        }

        if reason_result:
            canon_context["reasoning_confidence"] = reason_result.confidence
            canon_context["decision"] = reason_result.decision

        return OrchestrationResult(
            task_id=task_id,
            success=cog_result.success,
            result=cog_result.result,
            canon_context=canon_context,
            reasoning_path=reasoning_path,
            memories_accessed=memories_accessed,
            patterns_applied=[p.pattern_id for p in learn_result.learned_patterns[:3]],
            processing_time_ms=processing_time_ms,
        )

    def get_orchestrator_stats(self) -> dict[str, Any]:
        """Get orchestrator statistics."""
        if not self._initialized:
            return {"error": "Not initialized"}

        return {
            "initialized": self._initialized,
            "knowledge_engine": self._knowledge_engine.get_stats(),
            "memory_system": self._memory_system.get_memory_stats(),
            "learning_engine": self._learning_engine.get_learning_stats(),
        }


# Global instance
_canon_orchestrator: CanonOrchestrator | None = None


def get_canon_orchestrator() -> CanonOrchestrator:
    """Get or create global Canon orchestrator."""
    global _canon_orchestrator
    if _canon_orchestrator is None:
        _canon_orchestrator = CanonOrchestrator()
        _canon_orchestrator.initialize()
    return _canon_orchestrator


def canon_orchestrate(task: str, domain: str = "general") -> OrchestrationResult:
    """Execute task with full Canon orchestration - convenience function.

    Usage:
        result = canon_orchestrate(
            "How should we design the brain architecture?",
            domain="cognitive"
        )
        print(f"Success: {result.success}")
        print(f"Result: {result.result}")
        print(f"Canon context: {result.canon_context}")
    """
    orchestrator = get_canon_orchestrator()
    return orchestrator.execute_task(task, domain)
