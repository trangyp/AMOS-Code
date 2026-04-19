from typing import Any, Dict, List, Optional

"""
AMOS Brain-Reading Integration Layer

Connects the Brain-Reading Kernel to the AMOS ecosystem:
- Brain core
- Agent bridge
- Memory system
- Equation runtime
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

from amos_brain_reading_kernel import (
    IntentType,
    StableRead,
    get_brain_reading_kernel,
)


@dataclass
class IntegratedBrainRead:
    """Brain read result integrated with AMOS ecosystem."""

    stable_read: StableRead
    amos_context: Dict[str, Any] = field(default_factory=dict)
    execution_plan: Dict[str, Any] = None
    priority_score: float = 0.0
    routing_decision: str = ""  # brain, agent, equation, clarification
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class BrainReadingIntegrator:
    """
    Integrates Brain-Reading Kernel with AMOS subsystems.

    Routes StableRead outputs to appropriate AMOS handlers:
    - DESIGN → Brain/Architecture
    - REQUEST → Agent/Task
    - QUESTION → Clarification/Search
    - CORRECTION → Self-Healing
    """

    def __init__(self):
        self.kernel = get_brain_reading_kernel()
        self.reading_history: List[IntegratedBrainRead] = []

    async def process_input(
        self, text: str, amos_context: Dict[str, Any] = None, **kwargs
    ) -> IntegratedBrainRead:
        """
        Process input through brain-reading and integrate with AMOS.

        Args:
            text: Raw input text
            amos_context: Current AMOS state (health, active subsystems, etc.)
            **kwargs: Additional context (memory, goals, etc.)

        Returns:
            IntegratedBrainRead with routing decision
        """
        amos_context = amos_context or {}

        # Execute brain reading
        stable_read = await self.kernel.read(
            text=text,
            dialogue_context=kwargs.get("dialogue_context"),
            memory_context=kwargs.get("memory_context"),
            world_context=kwargs.get("world_context"),
            active_goals=kwargs.get("active_goals", []),
        )

        # Compute integration metrics
        priority_score = self._compute_priority(stable_read, amos_context)
        routing_decision = self._route_reading(stable_read, priority_score)
        execution_plan = self._build_execution_plan(stable_read, routing_decision)

        # Create integrated result
        integrated = IntegratedBrainRead(
            stable_read=stable_read,
            amos_context=amos_context,
            execution_plan=execution_plan,
            priority_score=priority_score,
            routing_decision=routing_decision,
        )

        # Store in history
        self.reading_history.append(integrated)

        return integrated

    def _compute_priority(self, stable_read: StableRead, amos_context: Dict[str, Any]) -> float:
        """
        Compute priority score for this reading.

        Factors:
        - Intent urgency
        - Coherence score
        - System health impact
        - User authority
        """
        base_priority = 0.5

        # Intent urgency
        intent_multipliers = {
            IntentType.DISTRESS: 2.0,
            IntentType.CORRECTION: 1.5,
            IntentType.REQUEST: 1.2,
            IntentType.DESIGN: 1.3,
            IntentType.DECISION_SUPPORT: 1.4,
            IntentType.QUESTION: 0.8,
            IntentType.SPECIFICATION: 1.1,
            IntentType.MIXED: 1.0,
        }
        intent_mult = intent_multipliers.get(stable_read.primary_intent[0], 1.0)

        # Coherence confidence
        coherence_factor = stable_read.coherence_score

        # Conflict penalty
        conflict_penalty = len(stable_read.conflicts) * 0.2

        priority = base_priority * intent_mult * coherence_factor - conflict_penalty
        return max(0.0, min(1.0, priority))

    def _route_reading(self, stable_read: StableRead, priority: float) -> str:
        """
        Determine which AMOS subsystem should handle this reading.

        Routing decisions:
        - brain: Architectural/design requests
        - agent: Task execution requests
        - equation: Computation/equation requests
        - clarification: Ambiguous or unstable reads
        - self_heal: Error/correction/criticism
        """
        intent = stable_read.primary_intent[0]
        goal_type = stable_read.compiled_goal.goal_type

        # Check for instability first
        if not stable_read.stable or stable_read.coherence_score < 0.5:
            return "clarification"

        # High-priority distress or correction → Self-healing
        if intent in (IntentType.DISTRESS, IntentType.CORRECTION) and priority > 0.7:
            return "self_heal"

        # Design or specification → Brain
        if intent in (IntentType.DESIGN, IntentType.SPECIFICATION):
            return "brain"

        # Request with design goal → Brain
        if intent == IntentType.REQUEST and goal_type in ("design", "plan"):
            return "brain"

        # Request with simple goal → Agent
        if intent == IntentType.REQUEST and goal_type in ("respond", "execute"):
            return "agent"

        # Question → Clarification pipeline
        if intent == IntentType.QUESTION:
            return "clarification"

        # Decision support → Brain with agent
        if intent == IntentType.DECISION_SUPPORT:
            return "brain"

        # Default based on goal type
        if goal_type == "design":
            return "brain"
        elif goal_type == "respond":
            return "agent"

        return "brain"  # Default to brain for complex processing

    def _build_execution_plan(self, stable_read: StableRead, routing: str) -> Dict[str, Any]:
        """Build execution plan based on routing decision."""

        plans = {
            "brain": {
                "subsystem": "amos_brain",
                "action": "architectural_design",
                "params": {
                    "intent": stable_read.primary_intent[0].name,
                    "goals": stable_read.goal_structure,
                    "constraints": stable_read.constraint_structure,
                    "references": stable_read.reference_structure,
                },
            },
            "agent": {
                "subsystem": "amos_agent",
                "action": "task_execution",
                "params": {
                    "objective": stable_read.compiled_goal.objective,
                    "constraints": stable_read.compiled_goal.constraints,
                },
            },
            "clarification": {
                "subsystem": "amos_brain",
                "action": "clarification_request",
                "params": {
                    "ambiguities": stable_read.ambiguities,
                    "conflicts": [c.id for c in stable_read.conflicts],
                    "missing_bindings": len(stable_read.ambiguities),
                },
            },
            "self_heal": {
                "subsystem": "amos_self_healing",
                "action": "address_criticism",
                "params": {
                    "issues": stable_read.diagnostic_noise,
                    "severity": max((c.severity for c in stable_read.conflicts), default=0.0),
                },
            },
        }

        return plans.get(routing, plans["brain"])

    def get_reading_stats(self) -> Dict[str, Any]:
        """Get statistics on reading history."""
        if not self.reading_history:
            return {"total_reads": 0}

        return {
            "total_reads": len(self.reading_history),
            "stable_reads": sum(1 for r in self.reading_history if r.stable_read.stable),
            "avg_coherence": sum(r.stable_read.coherence_score for r in self.reading_history)
            / len(self.reading_history),
            "avg_priority": sum(r.priority_score for r in self.reading_history)
            / len(self.reading_history),
            "routing_distribution": self._compute_routing_distribution(),
        }

    def _compute_routing_distribution(self) -> Dict[str, int]:
        """Compute distribution of routing decisions."""
        distribution: Dict[str, int] = {}
        for read in self.reading_history:
            routing = read.routing_decision
            distribution[routing] = distribution.get(routing, 0) + 1
        return distribution


# ============================================================================
# FASTAPI INTEGRATION
# ============================================================================

from typing import Any

try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel

    class ReadRequest(BaseModel):
        text: str
        context: Dict[str, Any] = None
        goals: Optional[list[str]] = None

    class ReadResponse(BaseModel):
        utterance_id: str
        intent: str
        confidence: float
        stable: bool
        coherence: float
        routing: str
        priority: float
        chunks: List[dict[str, Any]]
        conflicts: List[dict[str, Any]]
        execution_plan: Dict[str, Any] = None

    def create_brain_reading_router() -> APIRouter:
        """Create FastAPI router for brain-reading endpoints."""
        router = APIRouter(prefix="/brain-reading", tags=["brain-reading"])
        integrator = BrainReadingIntegrator()

        @router.post("/read", response_model=ReadResponse)
        async def read_endpoint(request: ReadRequest) -> ReadResponse:
            """Execute brain-level reading on input text."""
            try:
                result = await integrator.process_input(
                    text=request.text,
                    amos_context=request.context or {},
                    active_goals=request.goals or [],
                )

                return ReadResponse(
                    utterance_id=result.stable_read.utterance_id,
                    intent=result.stable_read.primary_intent[0].name,
                    confidence=result.stable_read.primary_intent[1],
                    stable=result.stable_read.stable,
                    coherence=result.stable_read.coherence_score,
                    routing=result.routing_decision,
                    priority=result.priority_score,
                    chunks=[
                        {
                            "type": chunk.get("type", "unknown"),
                            "content": chunk.get("content", "")[:100],
                        }
                        for chunk in result.stable_read.goal_structure  # Simplified
                    ],
                    conflicts=[
                        {
                            "id": c.id,
                            "type": c.conflict_type.name,
                            "severity": c.severity,
                        }
                        for c in result.stable_read.conflicts
                    ],
                    execution_plan=result.execution_plan,
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @router.get("/stats")
        async def stats_endpoint() -> Dict[str, Any]:
            """Get brain-reading statistics."""
            return integrator.get_reading_stats()

        return router

except ImportError:
    # FastAPI not available
    def create_brain_reading_router() -> None:
        """Placeholder when FastAPI is not available."""
        return None

# ============================================================================
# USAGE EXAMPLE
# ============================================================================


async def example_integration():
    """Example of using the brain-reading integration."""

    integrator = BrainReadingIntegrator()

    # Example 1: Design request
    result1 = await integrator.process_input(
        text="The system is too shallow. Implement a Brain-Reading Kernel with predictive processing.",
        amos_context={"health_score": 0.9, "active_subsystems": ["brain", "kernel"]},
        active_goals=["improve architecture", "deep reading"],
    )

    print("=" * 60)
    print("EXAMPLE 1: Design Request")
    print("=" * 60)
    print(f"Intent: {result1.stable_read.primary_intent[0].name}")
    print(f"Stable: {result1.stable_read.stable}")
    print(f"Coherence: {result1.stable_read.coherence_score:.2f}")
    print(f"Priority: {result1.priority_score:.2f}")
    print(f"Routing: {result1.routing_decision}")
    print(f"Execution: {result1.execution_plan}")

    # Example 2: Question
    result2 = await integrator.process_input(
        text="How does the chunking engine work?",
        amos_context={"health_score": 0.95},
        active_goals=["understand system"],
    )

    print("\n" + "=" * 60)
    print("EXAMPLE 2: Question")
    print("=" * 60)
    print(f"Intent: {result2.stable_read.primary_intent[0].name}")
    print(f"Routing: {result2.routing_decision}")

    # Example 3: Criticism
    result3 = await integrator.process_input(
        text="This implementation is wrong. It fails to detect conflicts properly.",
        amos_context={"health_score": 0.7},
        active_goals=["fix bugs"],
    )

    print("\n" + "=" * 60)
    print("EXAMPLE 3: Criticism")
    print("=" * 60)
    print(f"Intent: {result3.stable_read.primary_intent[0].name}")
    print(f"Routing: {result3.routing_decision}")
    print(f"Priority: {result3.priority_score:.2f}")

    # Stats
    print("\n" + "=" * 60)
    print("READING STATISTICS")
    print("=" * 60)
    stats = integrator.get_reading_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    asyncio.run(example_integration())
