#!/usr/bin/env python3
"""
AMOS Brain-Worker Bridge
=========================

Connects the brain loader to the worker engine.
Allows workers to query brain knowledge during task execution.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from brain_loader import get_brain_loader, BrainResult


@dataclass
class TaskContext:
    """Context for a task with brain integration."""
    task_type: str
    description: str
    brain_queries: List[str]
    constraints: Dict[str, Any]


class BrainWorkerBridge:
    """
    Bridge between brain knowledge and worker execution.
    """

    def __init__(self, organism_root: Path) -> None:
        self.root = organism_root
        self.brain_root = organism_root.parent / "_AMOS_BRAIN"
        self._loader = None

    def _ensure_loader(self) -> None:
        """Ensure brain loader is initialized."""
        if self._loader is None:
            self._loader = get_brain_loader(self.brain_root)
            self._loader.load_all_engines()

    def query_brain_for_task(
        self, task_description: str, max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Query the brain for knowledge relevant to a task.
        """
        self._ensure_loader()

        # Extract key terms from task description
        terms = self._extract_terms(task_description)

        all_results: List[BrainResult] = []
        for term in terms:
            results = self._loader.search(term, max_results=3)
            all_results.extend(results)

        # Deduplicate and sort by relevance
        seen = set()
        unique_results = []
        for r in all_results:
            key = (r.engine_name, r.path)
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        unique_results.sort(key=lambda x: x.relevance_score, reverse=True)

        return {
            "terms_queried": terms,
            "results_count": len(unique_results),
            "top_results": [
                {
                    "engine": r.engine_name,
                    "path": r.path,
                    "content": str(r.content)[:200],
                    "relevance": r.relevance_score
                }
                for r in unique_results[:max_results]
            ]
        }

    def _extract_terms(self, description: str) -> List[str]:
        """Extract key search terms from task description."""
        # Simple extraction - can be enhanced with NLP
        terms = []

        # Key domain terms
        domain_keywords = [
            "cognition", "reasoning", "planning", "analysis",
            "design", "architecture", "code", "system",
            "ubi", "biological", "emotional", "somatic",
            "quantum", "logic", "ethics", "audit",
            "legal", "tech", "finance", "health"
        ]

        desc_lower = description.lower()
        for keyword in domain_keywords:
            if keyword in desc_lower:
                terms.append(keyword)

        # Always include the first few words
        first_words = " ".join(description.split()[:3])
        terms.append(first_words)

        return terms[:5]  # Limit to 5 terms

    def get_engine_guidance(self, engine_name: str) -> Dict[str, Any]:
        """Get guidance from a specific brain engine."""
        self._ensure_loader()

        info = self._loader.get_engine_info(engine_name)
        if not info:
            return {"error": f"Engine {engine_name} not found"}

        return {
            "engine": info,
            "guidance": f"Use {engine_name} for tasks requiring its capabilities"
        }

    def enrich_plan_with_brain(
        self, plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich a plan with brain knowledge.
        """
        self._ensure_loader()

        enriched = plan.copy()
        steps = enriched.get("steps", [])

        for step in steps:
            action = step.get("action", "")
            # Query brain for relevant knowledge
            knowledge = self.query_brain_for_task(action, max_results=3)
            step["brain_knowledge"] = knowledge

        enriched["brain_enriched"] = True
        enriched["knowledge_sources"] = self._loader.get_status()["engines"]

        return enriched

    def validate_against_brain(
        self, output: str, task_type: str
    ) -> Dict[str, Any]:
        """
        Validate output against brain knowledge.
        """
        self._ensure_loader()

        # Search for similar patterns in brain
        results = self._loader.search(output[:50], max_results=5)

        # Check alignment with known patterns
        alignment_score = 0.0
        if results:
            alignment_score = sum(r.relevance_score for r in results) / len(results)

        return {
            "alignment_score": alignment_score,
            "similar_patterns_found": len(results),
            "validation_passed": alignment_score > 0.5,
            "reference_engines": list(set(r.engine_name for r in results))
        }


def main() -> int:
    """CLI for brain-worker bridge."""
    print("AMOS Brain-Worker Bridge")
    print("=" * 50)

    import sys
    organism_root = Path(__file__).parent.parent
    bridge = BrainWorkerBridge(organism_root)

    # Test query
    test_task = "Design a cognitive architecture for reasoning"
    print(f"\nQuerying brain for: '{test_task}'")

    result = bridge.query_brain_for_task(test_task)

    print(f"\nTerms queried: {result['terms_queried']}")
    print(f"Results found: {result['results_count']}")

    print("\nTop results:")
    for r in result['top_results']:
        print(f"  [{r['engine']}] {r['path']}")
        print(f"    Relevance: {r['relevance']:.2f}")
        content_str = str(r['content'])
        if len(content_str) > 200:
            content_preview = content_str[:200]
        else:
            content_preview = content_str
        print(f"    Content: {content_preview}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
