"""Canon Agent - Domain-aware task execution with canonical knowledge.

Integrates AMOS Canon definitions into agent task processing to provide:
- Canonical term resolution during task execution
- Domain-specific agent selection from Canon registry
- Knowledge enrichment from canonical definitions

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from amos_brain.canon_bridge import get_canon_bridge


@dataclass
class TaskPlan:
    """Task execution plan with Canon context."""

    task_id: str
    task_type: str
    domain: str
    steps: list[dict[str, Any]]
    canon_terms: dict[str, str] = field(default_factory=dict)
    applicable_agents: list[str] = field(default_factory=list)
    relevant_engines: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class CanonAgent:
    """Agent that executes tasks with Canon knowledge integration.

    The CanonAgent bridges task execution with canonical definitions
    to ensure domain-accurate processing and agent selection.
    """

    def __init__(self, agent_id: str, domain: str = "general"):
        self.agent_id = agent_id
        self.domain = domain
        self._canon_bridge = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the Canon agent with Canon bridge."""
        if self._initialized:
            return True

        self._canon_bridge = await get_canon_bridge()
        self._initialized = True
        return True

    async def plan_task(
        self,
        task_description: str,
        task_type: str,
        context: dict[str, Any] | None = None,
    ) -> TaskPlan:
        """Create a task plan enriched with Canon context.

        Args:
            task_description: Description of the task
            task_type: Type of task (e.g., "code_review", "analysis")
            context: Additional execution context

        Returns:
            TaskPlan with Canon-enriched metadata
        """
        if not self._initialized:
            await self.initialize()

        # Detect domain from task description
        domain = self._detect_domain(task_description)

        # Get Canon context for the domain
        canon_ctx = self._canon_bridge.get_context_for_domain(domain)

        # Get Canon terms from context
        canon_terms = canon_ctx.glossary_terms

        # Select applicable agents
        agents = canon_ctx.applicable_agents if canon_ctx.applicable_agents else ["general_agent"]

        # Select relevant engines
        engines = canon_ctx.relevant_engines if canon_ctx.relevant_engines else []

        # Build execution steps
        steps = self._build_execution_steps(task_type, agents, engines)

        # Generate task ID
        import hashlib

        task_hash = hashlib.sha256(f"{self.agent_id}:{task_description}".encode()).hexdigest()[:12]

        return TaskPlan(
            task_id=f"task_{task_hash}",
            task_type=task_type,
            domain=domain,
            steps=steps,
            canon_terms=canon_terms,
            applicable_agents=agents,
            relevant_engines=engines,
            metadata={
                "agent_id": self.agent_id,
                "original_description": task_description,
                "canon_context": {
                    "terms_count": len(canon_terms),
                    "agents_count": len(agents),
                    "engines_count": len(engines),
                },
            },
        )

    def _detect_domain(self, task_description: str) -> str:
        """Detect the domain from task description."""
        desc_lower = task_description.lower()

        domain_keywords = {
            "brain": ["cognitive", "think", "reason", "brain", "mind", "intelligence"],
            "agent": ["agent", "task", "action", "execute", "autonomous"],
            "kernel": ["kernel", "core", "runtime", "execute", "engine"],
            "api": ["api", "endpoint", "rest", "http", "gateway"],
            "database": ["database", "db", "sql", "postgres", "query"],
            "security": ["security", "auth", "encrypt", "protect", "access"],
        }

        for domain, keywords in domain_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                return domain

        return self.domain

    def _build_execution_steps(
        self,
        task_type: str,
        agents: list[str],
        engines: list[str],
    ) -> list[dict[str, Any]]:
        """Build execution steps based on task type and Canon context."""
        steps = []

        # Initial analysis step
        steps.append(
            {
                "step": 1,
                "action": "analyze",
                "description": f"Analyze task using {task_type} methodology",
                "agents": [agents[0]] if agents else [],
            }
        )

        # Execution steps with agents
        for i, agent in enumerate(agents[:3], start=2):  # Max 3 agents
            steps.append(
                {
                    "step": i,
                    "action": "execute",
                    "description": f"Execute with {agent}",
                    "agent": agent,
                }
            )

        # Engine processing if available
        if engines:
            steps.append(
                {
                    "step": len(steps) + 1,
                    "action": "process",
                    "description": f"Process with engines: {', '.join(engines[:2])}",
                    "engines": engines[:2],
                }
            )

        # Final verification
        steps.append(
            {
                "step": len(steps) + 1,
                "action": "verify",
                "description": "Verify task completion",
            }
        )

        return steps

    async def execute_task(self, task_plan: TaskPlan) -> dict[str, Any]:
        """Execute a task plan with Canon context.

        Args:
            task_plan: The task plan to execute

        Returns:
            Execution result with Canon metadata
        """
        if not self._initialized:
            await self.initialize()

        # Simulate execution (real implementation would call actual agents/engines)
        results = []
        for step in task_plan.steps:
            result = await self._execute_step(step, task_plan)
            results.append(result)

        return {
            "task_id": task_plan.task_id,
            "task_type": task_plan.task_type,
            "domain": task_plan.domain,
            "success": all(r.get("success", False) for r in results),
            "steps_executed": len(results),
            "canon_terms_used": len(task_plan.canon_terms),
            "agents_involved": task_plan.applicable_agents,
            "engines_used": task_plan.relevant_engines,
            "step_results": results,
        }

    async def _execute_step(self, step: dict[str, Any], task_plan: TaskPlan) -> dict[str, Any]:
        """Execute a single step of the task plan."""
        action = step.get("action", "unknown")

        # In real implementation, this would call the actual agent/engine
        # For now, return simulated success
        return {
            "step": step.get("step", 0),
            "action": action,
            "success": True,
            "description": step.get("description", ""),
        }

    def get_canon_info(self) -> dict[str, Any]:
        """Get Canon information available to this agent."""
        if not self._initialized or not self._canon_bridge:
            return {"error": "Agent not initialized"}

        ctx = self._canon_bridge.get_context_for_domain(self.domain)
        return {
            "domain": self.domain,
            "terms_available": len(ctx.glossary_terms),
            "agents_available": len(ctx.applicable_agents),
            "engines_available": len(ctx.relevant_engines),
        }


# Singleton registry
_canon_agents: dict[str, CanonAgent] = {}


async def get_canon_agent(agent_id: str, domain: str = "general") -> CanonAgent:
    """Get or create a Canon agent.

    Usage:
        agent = await get_canon_agent("brain_agent", domain="brain")
        plan = await agent.plan_task("Analyze code", "analysis")
        result = await agent.execute_task(plan)
    """
    global _canon_agents

    key = f"{agent_id}:{domain}"
    if key not in _canon_agents:
        agent = CanonAgent(agent_id, domain)
        await agent.initialize()
        _canon_agents[key] = agent

    return _canon_agents[key]
