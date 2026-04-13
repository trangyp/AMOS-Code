"""AMOS Brain Memory Integration - Persists reasoning to clawspring memory."""
from __future__ import annotations

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

# Import clawspring memory if available
try:
    from clawspring.memory.store import save_memory, MemoryEntry
    CLAWSPRING_MEMORY = True
except ImportError:
    CLAWSPRING_MEMORY = False
    MemoryEntry = None


class BrainMemory:
    """
    Persists AMOS brain reasoning results to memory.

    Provides:
    - Save reasoning results with metadata
    - Query past reasoning by topic/problem
    - Build reasoning history/audit trail
    - Recall relevant past analyses
    """

    MEMORY_NAMESPACE = "amos_brain"
    REASONING_PREFIX = "[AMOS Reasoning]"

    def __init__(self, memory_dir: Path | None = None):
        self.memory_dir = memory_dir
        self._local_cache: dict[str, Any] = {}

    def save_reasoning(
        self,
        problem: str,
        analysis: dict[str, Any],
        tags: list[str] | None = None
    ) -> str:
        """
        Save a reasoning result to memory.

        Args:
            problem: The problem/decision that was analyzed
            analysis: Full analysis result from amos.analyze_with_rules()
            tags: Optional tags for categorization

        Returns:
            Memory entry ID
        """
        # Generate entry ID from problem hash
        entry_id = self._hash_problem(problem)

        # Build memory entry
        entry = {
            "id": entry_id,
            "timestamp": datetime.utcnow().isoformat(),
            "namespace": self.MEMORY_NAMESPACE,
            "problem": problem,
            "problem_preview": problem[:100] + "..." if len(problem) > 100 else problem,
            "analysis_summary": self._summarize_analysis(analysis),
            "full_analysis": analysis,
            "tags": tags or [],
            "rule_of_two_applied": "rule_of_two" in analysis,
            "rule_of_four_applied": "rule_of_four" in analysis,
            "confidence_score": analysis.get("structural_integrity_score", 0.0),
            "recommendations": analysis.get("recommendations", []),
        }

        # Save to clawspring memory if available
        if CLAWSPRING_MEMORY and MemoryEntry is not None:
            memory_text = self._format_for_memory(entry)
            memory_entry = MemoryEntry(
                name=f"{self.REASONING_PREFIX} {entry['problem_preview']}",
                description=f"AMOS brain reasoning for: {entry['problem_preview'][:50]}",
                type="reference",
                content=memory_text,
                scope="user",
                source="model",
                confidence=entry['confidence_score']
            )
            save_memory(memory_entry, scope="user")

        # Also cache locally
        self._local_cache[entry_id] = entry

        return entry_id

    def find_similar_reasoning(
        self,
        problem: str,
        threshold: float = 0.6
    ) -> list[dict[str, Any]]:
        """
        Find past reasoning similar to current problem.

        Args:
            problem: Current problem to compare
            threshold: Similarity threshold (0-1)

        Returns:
            List of similar past reasoning entries
        """
        if not self._local_cache:
            return []

        similar = []
        problem_lower = problem.lower()
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                      'to', 'of', 'and', 'or', 'for', 'in', 'on', 'at', 'with',
                      'should', 'we', 'our', 'us', 'i', 'you', 'it', 'this', 'that'}
        problem_words = set(w for w in problem_lower.split() if w not in stop_words and len(w) > 2)

        for entry_id, entry in self._local_cache.items():
            past_problem = entry["problem"].lower()
            past_words = set(w for w in past_problem.split() if w not in stop_words and len(w) > 2)

            # Calculate Jaccard similarity
            intersection = problem_words & past_words
            union = problem_words | past_words

            if union:
                similarity = len(intersection) / len(union)
                if similarity >= threshold or len(intersection) >= 2:
                    similar.append({
                        "entry": entry,
                        "similarity": similarity,
                        "recommendations": entry.get("recommendations", [])
                    })

        # Sort by similarity descending
        similar.sort(key=lambda x: x["similarity"], reverse=True)
        return similar[:5]  # Top 5

    def get_reasoning_history(
        self,
        limit: int = 10,
        tag_filter: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get recent reasoning history.

        Args:
            limit: Maximum entries to return
            tag_filter: Optional tag to filter by

        Returns:
            List of reasoning entries
        """
        entries = list(self._local_cache.values())

        # Sort by timestamp (newest first)
        entries.sort(key=lambda x: x["timestamp"], reverse=True)

        # Filter by tag if specified
        if tag_filter:
            entries = [e for e in entries if tag_filter in e.get("tags", [])]

        return entries[:limit]

    def get_audit_trail(
        self,
        problem_contains: str | None = None
    ) -> dict[str, Any]:
        """
        Get audit trail of brain reasoning.

        Args:
            problem_contains: Optional filter by problem text

        Returns:
            Audit statistics and entries
        """
        entries = list(self._local_cache.values())

        if problem_contains:
            entries = [e for e in entries if problem_contains.lower() in e["problem"].lower()]

        # Calculate statistics
        total = len(entries)
        with_rule2 = sum(1 for e in entries if e.get("rule_of_two_applied"))
        with_rule4 = sum(1 for e in entries if e.get("rule_of_four_applied"))
        avg_confidence = sum(e.get("confidence_score", 0) for e in entries) / total if total > 0 else 0

        return {
            "total_entries": total,
            "rule_of_two_applied": with_rule2,
            "rule_of_four_applied": with_rule4,
            "average_confidence": avg_confidence,
            "entries": entries,
            "law_compliance": {
                "L2_compliance_rate": with_rule2 / total if total > 0 else 0,
                "L3_compliance_rate": with_rule4 / total if total > 0 else 0,
            }
        }

    def recall_for_problem(self, problem: str) -> dict[str, Any]:
        """
        Recall relevant past reasoning and similar analyses for a problem.

        This is the main interface for using memory during reasoning.

        Args:
            problem: Current problem being analyzed

        Returns:
            Memory context including similar past reasoning and recommendations
        """
        similar = self.find_similar_reasoning(problem)

        if not similar:
            return {
                "has_prior_reasoning": False,
                "context": None,
                "recommendations": []
            }

        # Build context from similar reasoning
        contexts = []
        all_recommendations = []

        for item in similar:
            entry = item["entry"]
            contexts.append({
                "past_problem": entry["problem_preview"],
                "similarity": item["similarity"],
                "timestamp": entry["timestamp"],
                "past_recommendations": entry.get("recommendations", [])
            })
            all_recommendations.extend(entry.get("recommendations", []))

        return {
            "has_prior_reasoning": True,
            "similar_entries": contexts,
            "context": f"Found {len(similar)} similar past reasoning entries",
            "recommendations": list(set(all_recommendations))[:5]  # Unique, top 5
        }

    def _hash_problem(self, problem: str) -> str:
        """Generate hash ID for problem."""
        return hashlib.sha256(problem.encode()).hexdigest()[:16]

    def _summarize_analysis(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Create summary of analysis for memory storage."""
        summary = {
            "recommendations_count": len(analysis.get("recommendations", [])),
            "assumptions_count": len(analysis.get("assumptions", [])),
            "uncertainty_count": len(analysis.get("uncertainty_flags", [])),
            "structural_score": analysis.get("structural_integrity_score", 0.0),
        }

        # Add Rule of 2 summary
        if "rule_of_two" in analysis:
            r2 = analysis["rule_of_two"]
            summary["rule_of_two"] = {
                "confidence": r2.get("confidence", 0.0),
                "perspective_count": len(r2.get("perspectives", []))
            }

        # Add Rule of 4 summary
        if "rule_of_four" in analysis:
            r4 = analysis["rule_of_four"]
            summary["rule_of_four"] = {
                "completeness": r4.get("completeness_score", 0.0),
                "quadrants": r4.get("quadrants_analyzed", [])
            }

        return summary

    def _format_for_memory(self, entry: dict[str, Any]) -> str:
        """Format entry as readable text for memory storage."""
        lines = [
            f"## AMOS Brain Reasoning - {entry['timestamp']}",
            "",
            f"**Problem:** {entry['problem_preview']}",
            "",
            "**Analysis Summary:**",
            f"- Confidence Score: {entry['confidence_score']:.2f}",
            f"- Rule of 2 Applied: {entry['rule_of_two_applied']}",
            f"- Rule of 4 Applied: {entry['rule_of_four_applied']}",
            "",
            "**Recommendations:**",
        ]

        for rec in entry.get("recommendations", []):
            lines.append(f"- {rec}")

        if entry["tags"]:
            lines.extend(["", f"**Tags:** {', '.join(entry['tags'])}"])

        lines.extend(["", f"**Entry ID:** {entry['id']}"])

        return "\n".join(lines)


# Global singleton
_brain_memory: BrainMemory | None = None


def get_brain_memory() -> BrainMemory:
    """Get or create global brain memory instance."""
    global _brain_memory
    if _brain_memory is None:
        _brain_memory = BrainMemory()
    return _brain_memory


def save_reasoning_result(
    problem: str,
    analysis: dict[str, Any],
    tags: list[str] | None = None
) -> str:
    """Convenience function to save reasoning result."""
    memory = get_brain_memory()
    return memory.save_reasoning(problem, analysis, tags)


def recall_reasoning_context(problem: str) -> dict[str, Any]:
    """Convenience function to recall context for a problem."""
    memory = get_brain_memory()
    return memory.recall_for_problem(problem)
