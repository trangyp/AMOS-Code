"""AMOS Multi-Agent Cognitive Orchestrator - Parallel engine execution."""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from .engine_executor import execute_cognitive_task, ExecutionResult
except ImportError:
    from engine_executor import execute_cognitive_task, ExecutionResult


@dataclass
class AgentPerspective:
    """A single cognitive agent's perspective on a task."""
    agent_id: str
    engine_name: str
    reasoning: Dict[str, Any]
    confidence: float
    execution_time_ms: float


@dataclass
class ConsensusResult:
    """Synthesized result from multiple cognitive agents."""
    task: str
    perspectives: List[AgentPerspective]
    agreement_score: float
    consensus_view: str
    dissenting_views: List[str]
    recommended_action: str
    laws_checked: List[str]
    violations_found: List[str]
    total_execution_time_ms: float


class MultiAgentOrchestrator:
    """Orchestrates parallel cognitive agents for complex tasks."""

    # Minimum confidence threshold for consensus
    CONFIDENCE_THRESHOLD = 0.6

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._consensus_history: List[ConsensusResult] = []

    def execute_parallel(
        self,
        task: str,
        engines: List[str],
        require_consensus: bool = True
    ) -> ConsensusResult:
        """Execute task through multiple engines in parallel.

        Args:
            task: The task description
            engines: List of cognitive engines to engage
            require_consensus: Whether to synthesize consensus view

        Returns:
            ConsensusResult with perspectives and synthesis
        """
        start = time.time()
        perspectives = []

        # Execute engines in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._run_single_engine, task, eng): eng
                for eng in engines
            }

            for future in as_completed(futures):
                engine = futures[future]
                try:
                    perspective = future.result()
                    perspectives.append(perspective)
                except Exception as e:
                    perspectives.append(AgentPerspective(
                        agent_id=f"agent_{engine}",
                        engine_name=engine,
                        reasoning={"error": str(e)},
                        confidence=0.0,
                        execution_time_ms=0.0
                    ))

        # Synthesize consensus
        result = self._synthesize_consensus(task, perspectives, start)
        self._consensus_history.append(result)
        return result

    def _run_single_engine(self, task: str, engine: str) -> AgentPerspective:
        """Execute a single engine and return perspective."""
        start = time.time()
        result = execute_cognitive_task(task, [engine])
        elapsed = (time.time() - start) * 1000

        reasoning_data = result.reasoning_steps[0] if result.reasoning_steps else {}
        confidence = reasoning_data.get("result", {}).get("confidence", 0.5)

        return AgentPerspective(
            agent_id=f"agent_{engine}_{int(time.time() * 1000)}",
            engine_name=engine,
            reasoning=reasoning_data.get("result", {}),
            confidence=confidence,
            execution_time_ms=elapsed
        )

    def _synthesize_consensus(
        self,
        task: str,
        perspectives: List[AgentPerspective],
        start_time: float
    ) -> ConsensusResult:
        """Synthesize consensus from multiple perspectives."""
        if not perspectives:
            return ConsensusResult(
                task=task,
                perspectives=[],
                agreement_score=0.0,
                consensus_view="No perspectives generated",
                dissenting_views=[],
                recommended_action="Retry with different engines",
                laws_checked=[],
                violations_found=["No agents executed"],
                total_execution_time_ms=(time.time() - start_time) * 1000
            )

        # Calculate agreement based on confidence alignment
        confidences = [p.confidence for p in perspectives]
        avg_confidence = sum(confidences) / len(confidences)
        variance = sum((c - avg_confidence) ** 2 for c in confidences) / len(confidences)
        agreement_score = 1.0 - min(variance * 2, 1.0)

        # Extract key themes from perspectives
        all_themes = []
        for p in perspectives:
            themes = p.reasoning.get("perspectives", [])
            all_themes.extend(themes)

        # Build consensus view
        if agreement_score > 0.7:
            consensus_view = (
                f"Strong agreement ({agreement_score:.0%}) across {len(perspectives)} "
                f"cognitive engines. Average confidence: {avg_confidence:.0%}. "
                f"Key themes: {', '.join(all_themes[:3]) if all_themes else 'Analysis complete'}."
            )
            dissenting = []
        else:
            # Find dissenting views (low confidence outliers)
            dissenting = [
                f"{p.engine_name}: confidence {p.confidence:.0%}"
                for p in perspectives
                if p.confidence < avg_confidence - 0.2
            ]
            consensus_view = (
                f"Partial agreement ({agreement_score:.0%}) with {len(dissenting)} "
                f"dissenting perspectives. Review recommended."
            )

        # Generate recommendation
        if all(p.confidence >= self.CONFIDENCE_THRESHOLD for p in perspectives):
            recommended_action = "Proceed with high-confidence consensus"
        elif agreement_score > 0.5:
            recommended_action = "Proceed with caution - review dissenting views"
        else:
            recommended_action = "Halt - significant disagreement detected, manual review required"

        # Check laws
        laws = ["RULE_OF_2", "RULE_OF_4", "ABSOLUTE_STRUCTURAL_INTEGRITY"]
        violations = self._check_consensus_laws(perspectives)

        return ConsensusResult(
            task=task,
            perspectives=perspectives,
            agreement_score=agreement_score,
            consensus_view=consensus_view,
            dissenting_views=dissenting,
            recommended_action=recommended_action,
            laws_checked=laws,
            violations_found=violations,
            total_execution_time_ms=(time.time() - start_time) * 1000
        )

    def _check_consensus_laws(self, perspectives: List[AgentPerspective]) -> List[str]:
        """Check global laws against the consensus result."""
        violations = []

        # Rule of 2: At least 2 perspectives
        if len(perspectives) < 2:
            violations.append("RULE_OF_2: Only one perspective - contrasting view needed")

        # Check for structural integrity across all perspectives
        for p in perspectives:
            if p.confidence < 0.3:
                violations.append(
                    f"STRUCTURAL_INTEGRITY: {p.engine_name} has low confidence ({p.confidence:.0%})"
                )

        return violations

    def get_consensus_history(self) -> List[ConsensusResult]:
        """Get history of all consensus executions."""
        return self._consensus_history.copy()

    def format_consensus_report(self, result: ConsensusResult) -> str:
        """Format consensus result as human-readable report."""
        lines = [
            "# Multi-Agent Cognitive Consensus",
            "",
            f"**Agreement Score**: {result.agreement_score:.0%}",
            f"**Execution Time**: {result.total_execution_time_ms:.1f}ms",
            f"**Engines Engaged**: {len(result.perspectives)}",
            "",
            "## Consensus View",
            result.consensus_view,
            "",
            "## Individual Perspectives",
        ]

        for p in result.perspectives:
            lines.append(f"\n### {p.engine_name.replace('AMOS_', '').replace('_Engine', '')}")
            lines.append(f"- Confidence: {p.confidence:.0%}")
            lines.append(f"- Execution: {p.execution_time_ms:.1f}ms")
            if "perspectives" in p.reasoning:
                for view in p.reasoning["perspectives"]:
                    lines.append(f"  - {view}")

        if result.dissenting_views:
            lines.extend(["", "## Dissenting Views", ""])
            for d in result.dissenting_views:
                lines.append(f"- ⚠️ {d}")

        lines.extend([
            "",
            "## Recommendation",
            f"**{result.recommended_action}**",
            "",
            f"Laws checked: {', '.join(result.laws_checked)}",
        ])

        if result.violations_found:
            lines.extend(["", "⚠️ Violations:", ""])
            for v in result.violations_found:
                lines.append(f"  - {v}")
        else:
            lines.append("✓ All global laws satisfied")

        return "\n".join(lines)


# Singleton instance
_orchestrator: Optional[MultiAgentOrchestrator] = None


def get_orchestrator() -> MultiAgentOrchestrator:
    """Get or create the singleton orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiAgentOrchestrator()
    return _orchestrator


def run_cognitive_consensus(
    task: str,
    engines: Optional[List[str]] = None
) -> ConsensusResult:
    """Convenience function to run multi-agent consensus."""
    orchestrator = get_orchestrator()
    if engines is None:
        # Default set of diverse engines
        engines = [
            "AMOS_Deterministic_Logic_And_Law_Engine",
            "AMOS_Engineering_And_Mathematics_Engine",
            "AMOS_Strategy_Game_Engine"
        ]
    return orchestrator.execute_parallel(task, engines)


if __name__ == "__main__":
    # Test multi-agent orchestration
    test_task = "Should we implement caching at the application or database layer?"

    print("=" * 70)
    print("AMOS Multi-Agent Cognitive Orchestrator - Test")
    print("=" * 70)
    print(f"\nTask: {test_task}\n")

    result = run_cognitive_consensus(test_task)
    orchestrator = get_orchestrator()
    print(orchestrator.format_consensus_report(result))
