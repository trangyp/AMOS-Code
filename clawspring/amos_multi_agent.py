"""AMOS Multi-Agent Coordinator - Parallel cognition across 9 layers."""

from __future__ import annotations

import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable

from amos_execution import full_execute

from amos_runtime import get_runtime


@dataclass
class AgentTask:
    """Task definition for a sub-agent."""

    task_id: str
    agent_type: str  # 'reasoning', 'coding', 'design', 'ubi', 'audit'
    description: str
    context: dict = field(default_factory=dict)
    priority: int = 5  # 1-10, lower = higher priority
    quadrant: str = ""  # 'biological', 'technical', 'economic', 'environmental'


@dataclass
class AgentResult:
    """Result from a sub-agent execution."""

    task_id: str
    agent_type: str
    success: bool
    content: str
    execution_time: float
    law_compliance: dict
    quality_score: float
    gap_acknowledgment: str


class SubAgent:
    """Individual cognitive agent specialized for specific tasks."""

    def __init__(self, agent_type: str, runtime: Any = None):
        self.agent_type = agent_type
        self.runtime = runtime or get_runtime()

    def execute(self, task: AgentTask) -> AgentResult:
        """Execute task using AMOS brain layers."""
        start_time = time.time()

        try:
            # Route to appropriate engine based on agent type
            if self.agent_type == "reasoning":
                result = full_execute(task.description, "structured_explanation")
            elif self.agent_type == "decision":
                result = full_execute(task.description, "decision_recommendation")
            elif self.agent_type == "design":
                result = full_execute(task.description, "framework_design")
            else:
                result = full_execute(task.description, "structured_explanation")

            execution_time = time.time() - start_time

            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                success=True,
                content=result.content,
                execution_time=execution_time,
                law_compliance=result.law_compliance,
                quality_score=result.quality_score,
                gap_acknowledgment=result.gap_acknowledgment,
            )

        except Exception as e:
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                success=False,
                content=f"Error: {str(e)}",
                execution_time=time.time() - start_time,
                law_compliance={},
                quality_score=0.0,
                gap_acknowledgment="GAP: Execution failed - no analysis performed",
            )


class AMOSMultiAgentCoordinator:
    """Coordinates multiple AMOS agents for parallel cognition."""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.runtime = get_runtime()
        self.agent_registry: dict[str, Callable] = {}
        self._register_default_agents()

    def _register_default_agents(self):
        """Register default AMOS agent types."""
        self.agent_registry = {
            "reasoning": SubAgent("reasoning"),
            "decision": SubAgent("decision"),
            "design": SubAgent("design"),
            "ubi": SubAgent("ubi"),
            "audit": SubAgent("audit"),
        }

    def create_quadrant_analysis(
        self,
        problem_description: str,
    ) -> list[AgentTask]:
        """Create 4 parallel tasks for quadrant analysis."""
        base_id = str(uuid.uuid4())[:8]

        return [
            AgentTask(
                task_id=f"{base_id}_bio",
                agent_type="reasoning",
                description=f"Analyze BIOLOGICAL/HUMAN quadrant: {problem_description}",
                quadrant="biological",
                priority=1,
            ),
            AgentTask(
                task_id=f"{base_id}_tech",
                agent_type="reasoning",
                description=f"Analyze TECHNICAL/INFRASTRUCTURAL quadrant: {problem_description}",
                quadrant="technical",
                priority=1,
            ),
            AgentTask(
                task_id=f"{base_id}_econ",
                agent_type="reasoning",
                description=f"Analyze ECONOMIC/ORGANIZATIONAL quadrant: {problem_description}",
                quadrant="economic",
                priority=1,
            ),
            AgentTask(
                task_id=f"{base_id}_env",
                agent_type="reasoning",
                description=f"Analyze ENVIRONMENTAL/PLANETARY quadrant: {problem_description}",
                quadrant="environmental",
                priority=1,
            ),
        ]

    def create_dual_perspective_analysis(
        self,
        problem_description: str,
    ) -> list[AgentTask]:
        """Create 2 parallel tasks for dual perspective (Rule of 2)."""
        base_id = str(uuid.uuid4())[:8]

        return [
            AgentTask(
                task_id=f"{base_id}_support",
                agent_type="reasoning",
                description=f"SUPPORTING perspective: {problem_description}",
                priority=2,
            ),
            AgentTask(
                task_id=f"{base_id}_alternative",
                agent_type="reasoning",
                description=f"ALTERNATIVE perspective: {problem_description}",
                priority=2,
            ),
        ]

    def execute_parallel(
        self,
        tasks: list[AgentTask],
    ) -> list[AgentResult]:
        """Execute multiple agent tasks in parallel."""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {}
            for task in tasks:
                agent = self.agent_registry.get(task.agent_type)
                if agent:
                    future = executor.submit(agent.execute, task)
                    future_to_task[future] = task

            # Collect results as they complete
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(
                        AgentResult(
                            task_id=task.task_id,
                            agent_type=task.agent_type,
                            success=False,
                            content=f"Execution error: {str(e)}",
                            execution_time=0.0,
                            law_compliance={},
                            quality_score=0.0,
                            gap_acknowledgment="GAP: Task execution failed",
                        )
                    )

        return sorted(results, key=lambda r: r.task_id)

    def synthesize_results(
        self,
        results: list[AgentResult],
        synthesis_type: str = "quadrant",
    ) -> str:
        """Synthesize parallel agent results into unified output."""
        lines = [
            f"# AMOS Multi-Agent Synthesis ({synthesis_type})",
            f"Agents executed: {len(results)}",
            f"Successful: {sum(1 for r in results if r.success)}",
            f"Average quality: {sum(r.quality_score for r in results) / len(results):.2f}",
            "",
            "## Individual Agent Outputs",
            "",
        ]

        for result in results:
            status = "✓" if result.success else "✗"
            lines.extend(
                [
                    f"### {status} {result.agent_type} ({result.task_id})",
                    f"Time: {result.execution_time:.2f}s | Quality: {result.quality_score:.2f}",
                    "",
                    result.content[:500] + "..." if len(result.content) > 500 else result.content,
                    "",
                ]
            )

        # Law compliance summary
        all_laws = set()
        for r in results:
            all_laws.update(r.law_compliance.keys())

        lines.extend(
            [
                "",
                "## Law Compliance Summary",
            ]
        )
        for law in sorted(all_laws):
            passed = sum(1 for r in results if r.law_compliance.get(law, False))
            lines.append(f"- {law}: {passed}/{len(results)} agents compliant")

        # Gap acknowledgment
        lines.extend(
            [
                "",
                "## Gap Acknowledgment",
                "GAP: Multi-agent synthesis combines parallel structural analyses.",
                "No unified consciousness. No integration of conflicting perspectives.",
                "Human synthesis and judgment required for final decisions.",
            ]
        )

        return "\n".join(lines)

    def run_quadrant_analysis(self, problem: str) -> str:
        """Run full 4-quadrant parallel analysis (Rule of 4)."""
        tasks = self.create_quadrant_analysis(problem)
        results = self.execute_parallel(tasks)
        return self.synthesize_results(results, "4-Quadrant Analysis")

    def run_dual_perspective(self, problem: str) -> str:
        """Run dual perspective analysis (Rule of 2)."""
        tasks = self.create_dual_perspective_analysis(problem)
        results = self.execute_parallel(tasks)
        return self.synthesize_results(results, "Dual Perspective")


# Singleton
coordinator: AMOSMultiAgentCoordinator | None = None


def get_multi_agent_coordinator() -> AMOSMultiAgentCoordinator:
    """Get singleton multi-agent coordinator."""
    global coordinator
    if coordinator is None:
        coordinator = AMOSMultiAgentCoordinator()
    return coordinator


def analyze_quadrants(problem: str) -> str:
    """Quick helper for 4-quadrant analysis."""
    return get_multi_agent_coordinator().run_quadrant_analysis(problem)


def analyze_dual(problem: str) -> str:
    """Quick helper for dual perspective analysis."""
    return get_multi_agent_coordinator().run_dual_perspective(problem)


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS MULTI-AGENT COORDINATOR TEST")
    print("=" * 60)

    coord = get_multi_agent_coordinator()

    # Test dual perspective
    print("\n--- Testing Dual Perspective (Rule of 2) ---")
    result = coord.run_dual_perspective("Should we migrate our database to a distributed system?")
    # Just show first part (output is long)
    print(result[:1500])
    print("... [truncated]")

    print("\n" + "=" * 60)
    print("Multi-Agent Coordinator: OPERATIONAL")
    print("=" * 60)
    print("\nGAP: Parallel execution is not unified cognition.")
    print("No integration. No synthesis. Human judgment required.")
