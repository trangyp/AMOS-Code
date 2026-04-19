#!/usr/bin/env python3
"""AMOS Multi-Agent Orchestrator (Layer 24)
=========================================

Coordinates multiple cognitive agents working together on complex tasks.
Each agent can specialize in different domains while sharing brain state.

Features:
- Agent spawning with domain specialization
- Inter-agent communication
- Task distribution and coordination
- Consensus building
- Conflict resolution

Usage:
    from amos_brain.multi_agent_orchestrator import MultiAgentOrchestrator

    mao = MultiAgentOrchestrator()

    # Spawn specialized agents
    architect = mao.spawn_agent("architecture", domain="software")
    reviewer = mao.spawn_agent("reviewer", domain="security")
    tester = mao.spawn_agent("tester", domain="qa")

    # Assign collaborative task
    result = mao.orchestrate("Design secure API", agents=[architect, reviewer, tester])

Creator: Trang Phan
System: AMOS vInfinity - Layer 24
"""


import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Agent:
    """Cognitive agent with domain specialization."""

    agent_id: str
    name: str
    domain: str
    capabilities: List[str]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    task_count: int = 0
    status: str = "idle"

    def execute(self, task: str) -> Dict[str, Any]:
        """Execute task using brain cognitive capabilities."""
        from amos_brain import think

        response = think(f"[{self.domain}] {task}")
        self.task_count += 1

        return {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "domain": self.domain,
            "task": task,
            "reasoning": response.reasoning,
            "confidence": response.confidence,
            "law_compliant": response.law_compliant,
            "success": response.success,
        }


@dataclass
class OrchestrationResult:
    """Result of multi-agent orchestration."""

    orchestration_id: str
    task: str
    agents_used: List[str]
    agent_results: list[dict[str, Any]]
    consensus: str
    conflicts: List[str]
    final_decision: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MultiAgentOrchestrator:
    """Multi-Agent Orchestrator - Layer 24.

    Manages multiple cognitive agents working collaboratively:
    - Spawns domain-specialized agents
    - Distributes tasks across agents
    - Collects and synthesizes results
    - Builds consensus or identifies conflicts
    - Resolves conflicts through meta-reasoning

    Integrates with all 23 previous layers:
    - L10: Brain cognitive capabilities
    - L12: Cookbook recipes for workflows
    - L18: Organism execution
    - L23: Knowledge engine access
    """

    VERSION = "24.0.0"
    MAX_AGENTS = 10

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.orchestrations: Dict[str, OrchestrationResult] = {}
        self.orchestrator_id = f"MAO-{uuid.uuid4().hex[:8]}"

    def spawn_agent(
        self, name: str, domain: str, capabilities: list[str ] = None
    ) -> Agent:
        """Spawn a new cognitive agent with domain specialization.

        Args:
            name: Agent name
            domain: Specialization domain (software, legal, design, etc.)
            capabilities: List of specific capabilities

        Returns:
            Spawned agent instance
        """
        if len(self.agents) >= self.MAX_AGENTS:
            raise RuntimeError(f"Maximum agents ({self.MAX_AGENTS}) reached")

        agent_id = f"AGENT-{uuid.uuid4().hex[:8]}"
        agent = Agent(
            agent_id=agent_id,
            name=name,
            domain=domain,
            capabilities=capabilities or [domain, "general"],
        )

        self.agents[agent_id] = agent
        return agent

    def list_agents(self) -> list[dict[str, Any]]:
        """List all active agents."""
        return [
            {
                "id": a.agent_id,
                "name": a.name,
                "domain": a.domain,
                "status": a.status,
                "tasks": a.task_count,
            }
            for a in self.agents.values()
        ]

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)

    def terminate_agent(self, agent_id: str) -> bool:
        """Terminate an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False

    def orchestrate(
        self, task: str, agents: list[Agent ] = None, mode: str = "parallel"
    ) -> OrchestrationResult:
        """Orchestrate multiple agents on a collaborative task.

        Args:
            task: Task to accomplish
            agents: List of agents to use (or all if None)
            mode: "parallel" or "sequential"

        Returns:
            Orchestration result with consensus/decision
        """
        orch_id = f"ORCH-{uuid.uuid4().hex[:8]}"

        # Use all agents if none specified
        agent_list = agents or list(self.agents.values())
        if not agent_list:
            raise RuntimeError("No agents available for orchestration")

        # Execute based on mode
        if mode == "parallel":
            results = self._execute_parallel(task, agent_list)
        else:
            results = self._execute_sequential(task, agent_list)

        # Synthesize results
        consensus = self._build_consensus(results)
        conflicts = self._identify_conflicts(results)
        final_decision = self._make_decision(task, results, consensus, conflicts)

        result = OrchestrationResult(
            orchestration_id=orch_id,
            task=task,
            agents_used=[a.agent_id for a in agent_list],
            agent_results=results,
            consensus=consensus,
            conflicts=conflicts,
            final_decision=final_decision,
        )

        self.orchestrations[orch_id] = result
        return result

    def _execute_parallel(self, task: str, agents: List[Agent]) -> list[dict[str, Any]]:
        """Execute task in parallel across agents."""
        results = []

        with ThreadPoolExecutor(max_workers=len(agents)) as executor:
            futures = {executor.submit(a.execute, task): a for a in agents}

            for future in as_completed(futures):
                agent = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({"agent_id": agent.agent_id, "error": str(e), "success": False})

        return results

    def _execute_sequential(self, task: str, agents: List[Agent]) -> list[dict[str, Any]]:
        """Execute task sequentially through agents."""
        results = []

        for agent in agents:
            result = agent.execute(task)
            results.append(result)

        return results

    def _build_consensus(self, results: list[dict[str, Any]]) -> str :
        """Attempt to build consensus from agent results."""
        # Extract key reasoning points
        all_points = []
        for r in results:
            if "reasoning" in r:
                all_points.extend(r["reasoning"][:2])

        if len(set(all_points)) < len(all_points) * 0.5:
            return "Strong consensus on approach"
        elif len(set(all_points)) < len(all_points) * 0.8:
            return "Partial consensus with minor differences"
        else:
            return None

    def _identify_conflicts(self, results: list[dict[str, Any]]) -> List[str]:
        """Identify conflicts between agent results."""
        conflicts = []

        # Check for law compliance conflicts
        compliant_count = sum(1 for r in results if r.get("law_compliant"))
        if 0 < compliant_count < len(results):
            conflicts.append("Law compliance disagreement")

        # Check for confidence conflicts
        confidences = [r.get("confidence", "medium") for r in results]
        if len(set(confidences)) > 2:
            conflicts.append("Confidence level disagreement")

        return conflicts

    def _make_decision(
        self,
        task: str,
        results: list[dict[str, Any]],
        consensus: str ,
        conflicts: List[str],
    ) -> str:
        """Make final decision based on agent results."""
        from amos_brain import decide
from typing import Final, List
from typing import Dict, Optional

        # Build decision context
        perspectives = []
        for r in results:
            if "reasoning" in r:
                perspectives.extend(r["reasoning"][:1])

        decision = decide(f"Multi-agent task: {task}", options=perspectives[:4])

        return decision.recommendation

    def get_orchestration(self, orch_id: str) -> Optional[OrchestrationResult]:
        """Get orchestration result by ID."""
        return self.orchestrations.get(orch_id)

    def status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            "orchestrator_id": self.orchestrator_id,
            "version": self.VERSION,
            "agents_active": len(self.agents),
            "agents_max": self.MAX_AGENTS,
            "orchestrations": len(self.orchestrations),
            "layer": 24,
            "status": "active",
        }


# Global instance
_mao_instance: Optional[MultiAgentOrchestrator] = None


def get_multi_agent_orchestrator() -> MultiAgentOrchestrator:
    """Get global multi-agent orchestrator."""
    global _mao_instance
    if _mao_instance is None:
        _mao_instance = MultiAgentOrchestrator()
    return _mao_instance


def spawn_agent(name: str, domain: str, capabilities: list[str ] = None) -> Agent:
    """Quick agent spawn."""
    return get_multi_agent_orchestrator().spawn_agent(name, domain, capabilities)


def orchestrate_task(task: str, agents: list[Agent ] = None) -> OrchestrationResult:
    """Quick task orchestration."""
    return get_multi_agent_orchestrator().orchestrate(task, agents)


if __name__ == "__main__":
    print("=" * 70)
    print("AMOS Multi-Agent Orchestrator (Layer 24)")
    print("=" * 70)
    print()

    mao = MultiAgentOrchestrator()

    # Spawn agents
    print("Spawning specialized agents...")
    architect = mao.spawn_agent("System Architect", "software", ["design", "architecture"])
    reviewer = mao.spawn_agent("Security Reviewer", "security", ["audit", "review"])
    tester = mao.spawn_agent("QA Tester", "qa", ["testing", "validation"])

    print(f"  ✓ {architect.name} ({architect.agent_id})")
    print(f"  ✓ {reviewer.name} ({reviewer.agent_id})")
    print(f"  ✓ {tester.name} ({tester.agent_id})")
    print()

    # Orchestrate task
    print("Orchestrating collaborative task...")
    result = mao.orchestrate(
        "Design a secure and scalable API architecture",
        agents=[architect, reviewer, tester],
        mode="parallel",
    )

    print(f"  Orchestration ID: {result.orchestration_id}")
    print(f"  Agents used: {len(result.agents_used)}")
    print(f"  Consensus: {result.consensus or 'None'}")
    print(f"  Conflicts: {len(result.conflicts)}")
    print(f"  Final decision: {result.final_decision[:50]}...")
    print()

    print("=" * 70)
    print("Layer 24: Multi-Agent Orchestrator - Active")
    print("=" * 70)
