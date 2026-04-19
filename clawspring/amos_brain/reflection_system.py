from typing import Any

"""Self-Reflection System for AMOS Brain

Implements Self-Refine and Reflexion patterns for iterative improvement.
Based on research: Any-Refine (generate-critic-revise), CRITIC (tool validation).

Architecture:
1. Generate initial output
2. Critique (self-critique or tool-assisted validation)
3. Revise based on critique
4. Iterate until satisfied or max iterations
"""
from __future__ import annotations


import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto

try:
    from .amos_kernel_runtime import AMOSKernelRuntime
except ImportError:
    from amos_kernel_runtime import AMOSKernelRuntime  # noqa: E402


class CritiqueType(Enum):
    """Types of critique."""

    SELF = auto()
    TOOL_VALIDATED = auto()
    EXTERNAL = auto()


@dataclass
class Critique:
    """Critique of generated output."""

    critique_text: str
    issues: list[str]
    severity: float  # 0-1
    suggestions: list[str]
    validated: bool
    validation_data: dict[str, Any] = None


@dataclass
class Revision:
    """Revised output."""

    output: str
    changes_made: list[str]
    confidence: float
    iteration: int


class SelfReflectionSystem:
    """
    Self-reflection with iterative refinement.

    Implements generate-critic-revise loop with optional tool validation.
    """

    def __init__(
        self,
        kernel: AMOSKernelRuntime | None = None,
        max_iterations: int = 3,
        improvement_threshold: float = 0.1,
    ):
        self.kernel = kernel or AMOSKernelRuntime()
        self.max_iterations = max_iterations
        self.improvement_threshold = improvement_threshold

        # Revision history
        self._history: list[dict[str, Any]] = []

    async def refine(
        self,
        initial_output: str,
        context: dict[str, Any],
        critique_fn: Callable[[str, dict], Critique] = None,
        revise_fn: Callable[[str, Critique, dict], str] = None,
    ) -> Revision:
        """
        Refine output through iterative critique and revision.

        Args:
            initial_output: Starting output to refine
            context: Context for critique/revision
            critique_fn: Custom critique function (optional)
            revise_fn: Custom revision function (optional)

        Returns:
            Final revision after iterations
        """
        current_output = initial_output
        current_confidence = 0.5

        for iteration in range(1, self.max_iterations + 1):
            # CRITIQUE PHASE
            critique = await self._generate_critique(
                current_output,
                context or {},
                critique_fn,
            )

            # Check if good enough
            if critique.severity < 0.2 and critique.validated:
                return Revision(
                    output=current_output,
                    changes_made=["No significant issues found"],
                    confidence=current_confidence,
                    iteration=iteration,
                )

            # REVISION PHASE
            new_output = await self._generate_revision(
                current_output,
                critique,
                context or {},
                revise_fn,
            )

            # Check if meaningful improvement
            change_score = self._compute_change_score(current_output, new_output)

            if change_score < self.improvement_threshold:
                # No meaningful change, stop
                break

            current_output = new_output
            current_confidence = min(0.95, current_confidence + 0.15)

            # Record iteration
            self._history.append(
                {
                    "iteration": iteration,
                    "critique": critique,
                    "output_snippet": current_output[:200],
                    "confidence": current_confidence,
                }
            )

        return Revision(
            output=current_output,
            changes_made=[f"Iteration {i + 1}" for i in range(len(self._history))],
            confidence=current_confidence,
            iteration=len(self._history),
        )

    async def _generate_critique(
        self,
        output: str,
        context: dict[str, Any],
        custom_fn: Callable[[str, dict], Critique],
    ) -> Critique:
        """Generate critique of output."""
        if custom_fn:
            return custom_fn(output, context)

        # Use brain kernel for critique
        observation = {
            "output": output,
            "context": context,
            "task": "critique",
        }
        goal = {"type": "critique", "target": "find_issues"}

        cycle_result = self.kernel.execute_cycle(observation, goal)

        # Parse critique from cycle result
        legality = cycle_result.get("legality", 0.5)

        issues = []
        suggestions = []

        if legality < 0.7:
            issues.append("Legality below threshold")
            suggestions.append("Review against AMOS laws")

        if len(output) < 10:
            issues.append("Output too short")
            suggestions.append("Expand with more detail")

        return Critique(
            critique_text="Automated critique based on legality assessment",
            issues=issues,
            severity=max(0.0, 1.0 - legality),
            suggestions=suggestions,
            validated=len(issues) == 0,
        )

    async def _generate_revision(
        self,
        output: str,
        critique: Critique,
        context: dict[str, Any],
        custom_fn: Callable[[str, Critique, dict], str],
    ) -> str:
        """Generate revised output based on critique."""
        if custom_fn:
            return custom_fn(output, critique, context)

        # Use brain kernel for revision
        observation = {
            "output": output,
            "critique": critique.critique_text,
            "issues": critique.issues,
            "suggestions": critique.suggestions,
            "task": "revise",
        }
        goal = {"type": "revision", "target": "improve_output"}

        self.kernel.execute_cycle(observation, goal)

        # Simple revision strategy: add suggestions
        if critique.suggestions:
            revised = f"{output}\n\n[Improved based on: {', '.join(critique.suggestions)}]"
            return revised

        return output

    def _compute_change_score(self, old: str, new: str) -> float:
        """Compute how much output changed."""
        if not old:
            return 1.0 if new else 0.0

        # Simple Jaccard-like similarity
        old_words = set(old.lower().split())
        new_words = set(new.lower().split())

        if not old_words:
            return 1.0 if new_words else 0.0

        common = old_words & new_words
        union = old_words | new_words

        similarity = len(common) / len(union) if union else 1.0
        return 1.0 - similarity

    def get_history(self) -> list[dict[str, Any]]:
        """Get refinement history."""
        return self._history.copy()


# Global reflection system
_global_reflection: SelfReflectionSystem | None = None


def get_reflection_system() -> SelfReflectionSystem:
    """Get or create global reflection system."""
    global _global_reflection
    if _global_reflection is None:
        _global_reflection = SelfReflectionSystem()
    return _global_reflection


if __name__ == "__main__":

    async def test():
        reflector = get_reflection_system()

        result = await reflector.refine(
            "This is a draft answer.",
            {"topic": "test"},
        )

        print(f"Final output: {result.output}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Iterations: {result.iteration}")

    asyncio.run(test())
