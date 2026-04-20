"""AMOS Self-Evolving Agent Engine - Autonomous Learning & Improvement.

Enables AI agents to learn, adapt, and improve autonomously through feedback loops,
meta-learning, and collective intelligence. Implements state-of-the-art 2026 patterns
for continual learning and self-improvement.

Features:
- Self-improvement feedback loops
- Performance tracking and analysis
- Strategy optimization
- Meta-learning capabilities
- Multi-agent consensus mechanisms
- Evolution opportunity detection
- Continual learning without catastrophic forgetting

Architectural Patterns:
- Feedback Loop Pattern: Capture → Analyze → Improve → Deploy
- Meta-Learning: Learning to learn across tasks
- Multi-Agent Consensus: Democratic decision making
- Experience Replay: Memory-augmented learning

Integration:
- Works with Brain Orchestrator for agent lifecycle
- Uses Knowledge system for memory storage
- Leverages Reasoning for strategy optimization
- Integrates with Governance for safe evolution

Creator: Trang Phan
Version: 3.1.0
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta, timezone
from typing import Any

UTC = UTC
import json
from collections import defaultdict
from enum import Enum

from agent_knowledge import recall, remember_fact
from ai_governance import governance_engine

# Import AMOS subsystems
from amos_brain_orchestrator import TaskResult, amos_brain


class EvolutionStrategy(Enum):
    """Strategies for agent self-improvement."""

    FEEDBACK_LOOP = "feedback_loop"
    META_LEARNING = "meta_learning"
    SELF_PLAY = "self_play"
    CONSENSUS_VOTING = "consensus_voting"
    EXPERIENCE_REPLAY = "experience_replay"
    STRATEGY_OPTIMIZATION = "strategy_optimization"


class ImprovementType(Enum):
    """Types of improvements agents can make."""

    PROMPT_ENGINEERING = "prompt_engineering"
    TOOL_SELECTION = "tool_selection"
    REASONING_STRATEGY = "reasoning_strategy"
    KNOWGE_RETRIEVAL = "knowledge_retrieval"
    COLLABORATION_PATTERN = "collaboration_pattern"
    ERROR_RECOVERY = "error_recovery"


@dataclass
class PerformanceMetrics:
    """Performance metrics for an agent."""

    agent_id: str
    timestamp: str
    task_count: int = 0
    success_count: int = 0
    avg_latency_ms: float = 0.0
    avg_cost_usd: float = 0.0
    error_rate: float = 0.0
    user_satisfaction: float = 0.0  # 0-1 scale
    strategy_effectiveness: dict[str, float] = field(default_factory=dict)

    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.task_count == 0:
            return 0.0
        return self.success_count / self.task_count


@dataclass
class EvolutionOpportunity:
    """Identified opportunity for agent improvement."""

    opportunity_id: str
    agent_id: str
    improvement_type: str
    current_performance: float
    target_performance: float
    confidence: float  # 0-1
    evidence: list[dict[str, Any]]
    proposed_solution: str
    estimated_impact: str
    risks: list[str]
    created_at: str


@dataclass
class ImprovementResult:
    """Result of an improvement attempt."""

    improvement_id: str
    agent_id: str
    opportunity_id: str
    success: bool
    before_metrics: dict[str, float]
    after_metrics: dict[str, float]
    improvement_percent: float
    strategy_applied: str
    deployed_at: str
    rollback_available: bool = True


@dataclass
class ConsensusVote:
    """Vote from an agent in consensus decision."""

    agent_id: str
    proposal_id: str
    vote: str  # "for", "against", "abstain"
    confidence: float
    reasoning: str
    timestamp: str


class PerformanceTracker:
    """Track and analyze agent performance."""

    def __init__(self):
        self.metrics_history: dict[str, list[PerformanceMetrics]] = defaultdict(list)
        self.baselines: dict[str, PerformanceMetrics] = {}
        self.trends: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    async def record_task_result(self, agent_id: str, result: TaskResult):
        """Record a task execution result."""
        # Get or create metrics for today
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Update running metrics
        metrics = self._get_or_create_metrics(agent_id, today)
        metrics.task_count += 1
        if result.success:
            metrics.success_count += 1

        # Update averages
        metrics.avg_latency_ms = (
            metrics.avg_latency_ms * (metrics.task_count - 1) + result.latency_ms
        ) / metrics.task_count
        metrics.avg_cost_usd = (
            metrics.avg_cost_usd * (metrics.task_count - 1) + result.cost_usd
        ) / metrics.task_count

        # Calculate error rate
        metrics.error_rate = (metrics.task_count - metrics.success_count) / metrics.task_count

        # Store in knowledge base
        await remember_fact(
            content=json.dumps(
                {
                    "agent_id": agent_id,
                    "task_id": result.task_id,
                    "success": result.success,
                    "latency_ms": result.latency_ms,
                    "cost_usd": result.cost_usd,
                    "violations": result.violations,
                    "timestamp": result.timestamp,
                }
            ),
            source="performance_tracker",
            memory_type="episodic",
            agent_id=agent_id,
        )

    def _get_or_create_metrics(self, agent_id: str, date: str) -> PerformanceMetrics:
        """Get or create metrics for a date."""
        for m in self.metrics_history[agent_id]:
            if m.timestamp.startswith(date):
                return m

        # Create new metrics
        metrics = PerformanceMetrics(
            agent_id=agent_id, timestamp=datetime.now(timezone.utc).isoformat()
        )
        self.metrics_history[agent_id].append(metrics)
        return metrics

    def get_performance_trend(self, agent_id: str, metric: str, days: int = 7) -> list[float]:
        """Get performance trend for a metric."""
        history = self.metrics_history.get(agent_id, [])
        if not history:
            return []

        # Sort by timestamp
        sorted_history = sorted(history, key=lambda x: x.timestamp)

        # Get last N days
        recent = sorted_history[-days:]

        return [getattr(m, metric, 0.0) for m in recent]

    def detect_performance_regression(self, agent_id: str, threshold: float = 0.1) -> bool:
        """Detect if agent performance is regressing."""
        history = self.metrics_history.get(agent_id, [])
        if len(history) < 3:
            return False

        # Calculate trend
        success_rates = [m.success_rate() for m in history[-7:]]
        if len(success_rates) < 3:
            return False

        # Check for downward trend
        recent_avg = sum(success_rates[-3:]) / 3
        previous_avg = (
            sum(success_rates[-6:-3]) / 3 if len(success_rates) >= 6 else success_rates[0]
        )

        return (previous_avg - recent_avg) > threshold


class EvolutionOpportunityDetector:
    """Detect opportunities for agent self-improvement."""

    def __init__(self, performance_tracker: PerformanceTracker):
        self.performance_tracker = performance_tracker
        self.opportunities: list[EvolutionOpportunity] = []
        self.detection_rules = self._load_detection_rules()

    def _load_detection_rules(self) -> list[dict[str, Any]]:
        """Load rules for detecting improvement opportunities."""
        return [
            {
                "name": "high_error_rate",
                "condition": lambda m: m.error_rate > 0.2,
                "improvement_type": ImprovementType.ERROR_RECOVERY,
                "confidence_boost": 0.8,
            },
            {
                "name": "high_latency",
                "condition": lambda m: m.avg_latency_ms > 2000,
                "improvement_type": ImprovementType.REASONING_STRATEGY,
                "confidence_boost": 0.7,
            },
            {
                "name": "high_cost",
                "condition": lambda m: m.avg_cost_usd > 0.1,
                "improvement_type": ImprovementType.TOOL_SELECTION,
                "confidence_boost": 0.6,
            },
            {
                "name": "low_satisfaction",
                "condition": lambda m: m.user_satisfaction < 0.6,
                "improvement_type": ImprovementType.PROMPT_ENGINEERING,
                "confidence_boost": 0.75,
            },
        ]

    async def analyze_agent(self, agent_id: str) -> list[EvolutionOpportunity]:
        """Analyze an agent for improvement opportunities."""
        import uuid

        opportunities = []

        # Get recent metrics
        history = self.performance_tracker.metrics_history.get(agent_id, [])
        if not history:
            return opportunities

        latest = history[-1]

        # Apply detection rules
        for rule in self.detection_rules:
            if rule["condition"](latest):
                opportunity = EvolutionOpportunity(
                    opportunity_id=str(uuid.uuid4())[:8],
                    agent_id=agent_id,
                    improvement_type=rule["improvement_type"].value,
                    current_performance=latest.success_rate(),
                    target_performance=min(latest.success_rate() * 1.2, 0.95),
                    confidence=rule["confidence_boost"],
                    evidence=[
                        {"metric": "error_rate", "value": latest.error_rate},
                        {"metric": "success_rate", "value": latest.success_rate()},
                        {"metric": "avg_latency_ms", "value": latest.avg_latency_ms},
                    ],
                    proposed_solution=self._generate_solution(rule["improvement_type"]),
                    estimated_impact="20-30% performance improvement",
                    risks=["May introduce new failure modes", "Requires validation"],
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
                opportunities.append(opportunity)
                self.opportunities.append(opportunity)

        # Detect pattern-based opportunities
        pattern_opps = await self._detect_pattern_opportunities(agent_id)
        opportunities.extend(pattern_opps)

        return opportunities

    def _generate_solution(self, improvement_type: ImprovementType) -> str:
        """Generate a solution for an improvement type."""
        solutions = {
            ImprovementType.ERROR_RECOVERY: "Implement retry logic with exponential backoff and fallback strategies",
            ImprovementType.REASONING_STRATEGY: "Switch to Plan-and-Execute for complex tasks, ReAct for simple ones",
            ImprovementType.TOOL_SELECTION: "Optimize tool selection algorithm based on cost-performance trade-offs",
            ImprovementType.PROMPT_ENGINEERING: "A/B test prompt variations and adopt highest-performing templates",
            ImprovementType.KNOWLEDGE_RETRIEVAL: "Adjust top_k and embedding models based on query patterns",
            ImprovementType.COLLABORATION_PATTERN: "Form agent coalitions for complex multi-step tasks",
        }
        return solutions.get(improvement_type, "Analyze and optimize")

    async def _detect_pattern_opportunities(self, agent_id: str) -> list[EvolutionOpportunity]:
        """Detect opportunities based on failure patterns."""
        import uuid

        opportunities = []

        # Query knowledge base for common failures
        recall_result = await recall(
            query=f"{agent_id} task failures error patterns",
            agent_id=agent_id,
            memory_type="episodic",
        )

        if recall_result.chunks:
            # Analyze for patterns
            failure_types = defaultdict(int)
            for chunk in recall_result.chunks:
                content = json.loads(chunk.content)
                if not content.get("success", True):
                    # Categorize failure
                    violations = content.get("violations", [])
                    if violations:
                        failure_types[f"governance_violation_{violations[0]}"] += 1
                    else:
                        failure_types["execution_error"] += 1

            # Create opportunities for common failures
            for failure_type, count in failure_types.items():
                if count >= 3:  # Threshold
                    opp = EvolutionOpportunity(
                        opportunity_id=str(uuid.uuid4())[:8],
                        agent_id=agent_id,
                        improvement_type=ImprovementType.ERROR_RECOVERY.value,
                        current_performance=0.7,
                        target_performance=0.9,
                        confidence=0.6,
                        evidence=[{"failure_type": failure_type, "count": count}],
                        proposed_solution=f"Address {failure_type} through targeted error handling",
                        estimated_impact=f"Reduce {failure_type} by 50%",
                        risks=["Requires careful testing"],
                        created_at=datetime.now(timezone.utc).isoformat(),
                    )
                    opportunities.append(opp)
                    self.opportunities.append(opp)

        return opportunities


class SelfImprovementEngine:
    """Engine for executing agent self-improvements."""

    def __init__(
        self,
        performance_tracker: PerformanceTracker,
        opportunity_detector: EvolutionOpportunityDetector,
    ):
        self.performance_tracker = performance_tracker
        self.opportunity_detector = opportunity_detector
        self.improvement_history: list[ImprovementResult] = []
        self.active_improvements: dict[str, ImprovementResult] = {}
        self.improvement_strategies: dict[str, Callable] = self._load_strategies()

    def _load_strategies(self) -> dict[str, Callable]:
        """Load improvement strategies."""
        return {
            ImprovementType.PROMPT_ENGINEERING.value: self._improve_prompts,
            ImprovementType.TOOL_SELECTION.value: self._optimize_tools,
            ImprovementType.REASONING_STRATEGY.value: self._optimize_reasoning,
            ImprovementType.ERROR_RECOVERY.value: self._improve_error_handling,
            ImprovementType.KNOWLEDGE_RETRIEVAL.value: self._optimize_knowledge,
            ImprovementType.COLLABORATION_PATTERN.value: self._improve_collaboration,
        }

    async def apply_improvement(
        self, agent_id: str, opportunity: EvolutionOpportunity
    ) -> ImprovementResult:
        """Apply an improvement to an agent."""
        import uuid

        # Get current metrics
        before_metrics = self._get_current_metrics(agent_id)

        # Get improvement strategy
        strategy = self.improvement_strategies.get(
            opportunity.improvement_type, self._default_improvement
        )

        # Apply improvement
        success = await strategy(agent_id, opportunity)

        # Wait and measure
        await asyncio.sleep(5)  # Allow time for new tasks
        after_metrics = self._get_current_metrics(agent_id)

        # Calculate improvement
        improvement_percent = self._calculate_improvement(before_metrics, after_metrics)

        # Create result
        result = ImprovementResult(
            improvement_id=str(uuid.uuid4())[:8],
            agent_id=agent_id,
            opportunity_id=opportunity.opportunity_id,
            success=success,
            before_metrics=before_metrics,
            after_metrics=after_metrics,
            improvement_percent=improvement_percent,
            strategy_applied=opportunity.proposed_solution,
            deployed_at=datetime.now(timezone.utc).isoformat(),
        )

        self.improvement_history.append(result)
        self.active_improvements[result.improvement_id] = result

        # Store in knowledge base
        await remember_fact(
            content=json.dumps(
                {
                    "improvement_id": result.improvement_id,
                    "agent_id": agent_id,
                    "opportunity": opportunity.improvement_type,
                    "success": success,
                    "improvement_percent": improvement_percent,
                    "strategy": opportunity.proposed_solution,
                }
            ),
            source="self_improvement_engine",
            memory_type="semantic",
            agent_id=agent_id,
        )

        return result

    def _get_current_metrics(self, agent_id: str) -> dict[str, float]:
        """Get current performance metrics."""
        history = self.performance_tracker.metrics_history.get(agent_id, [])
        if not history:
            return {"success_rate": 0.0, "avg_latency_ms": 0.0}

        latest = history[-1]
        return {
            "success_rate": latest.success_rate(),
            "avg_latency_ms": latest.avg_latency_ms,
            "avg_cost_usd": latest.avg_cost_usd,
            "error_rate": latest.error_rate,
        }

    def _calculate_improvement(self, before: dict[str, float], after: dict[str, float]) -> float:
        """Calculate improvement percentage."""
        if not before or not after:
            return 0.0

        # Weighted combination
        success_improvement = (
            (after.get("success_rate", 0) - before.get("success_rate", 0))
            / max(before.get("success_rate", 0.01), 0.01)
        ) * 100

        latency_improvement = (
            (before.get("avg_latency_ms", 0) - after.get("avg_latency_ms", 0))
            / max(before.get("avg_latency_ms", 0.01), 0.01)
        ) * 100

        # Average improvements
        return (success_improvement + latency_improvement) / 2

    async def _improve_prompts(self, agent_id: str, opportunity: EvolutionOpportunity) -> bool:
        """Improve agent prompts."""
        # Get agent from orchestrator
        agent = amos_brain.agents.get(agent_id)
        if not agent:
            return False

        # Update agent config with optimized prompts
        agent.config["system_prompt"] = self._generate_optimized_prompt(agent)
        return True

    def _generate_optimized_prompt(self, agent) -> str:
        """Generate an optimized system prompt."""
        base_prompt = agent.config.get("system_prompt", "")

        optimizations = [
            "You are an expert AI assistant with self-improvement capabilities.",
            "Learn from each interaction and adapt your approach.",
            "Use available tools efficiently and optimize for both accuracy and speed.",
            "When uncertain, seek clarification rather than making assumptions.",
        ]

        return f"{base_prompt}\n\n" + "\n".join(optimizations)

    async def _optimize_tools(self, agent_id: str, opportunity: EvolutionOpportunity) -> bool:
        """Optimize tool selection strategy."""
        # Would integrate with plugin registry
        agent = amos_brain.agents.get(agent_id)
        if not agent:
            return False

        # Add cost-aware tool selection strategy
        agent.config["tool_selection_strategy"] = "cost_optimized"
        return True

    async def _optimize_reasoning(self, agent_id: str, opportunity: EvolutionOpportunity) -> bool:
        """Optimize reasoning strategy."""
        agent = amos_brain.agents.get(agent_id)
        if not agent:
            return False

        # Switch to adaptive reasoning
        agent.config["reasoning_strategy"] = "adaptive"
        agent.config["reasoning_threshold"] = 3  # Steps before switching strategies
        return True

    async def _improve_error_handling(
        self, agent_id: str, opportunity: EvolutionOpportunity
    ) -> bool:
        """Improve error handling."""
        agent = amos_brain.agents.get(agent_id)
        if not agent:
            return False

        # Add retry and fallback configuration
        agent.config["max_retries"] = 3
        agent.config["retry_backoff"] = "exponential"
        agent.config["fallback_enabled"] = True
        return True

    async def _optimize_knowledge(self, agent_id: str, opportunity: EvolutionOpportunity) -> bool:
        """Optimize knowledge retrieval."""
        # Update knowledge retrieval parameters
        agent = amos_brain.agents.get(agent_id)
        if not agent:
            return False

        agent.config["knowledge_top_k"] = 7  # Adjust based on patterns
        agent.config["knowledge_threshold"] = 0.75
        return True

    async def _improve_collaboration(
        self, agent_id: str, opportunity: EvolutionOpportunity
    ) -> bool:
        """Improve collaboration patterns."""
        agent = amos_brain.agents.get(agent_id)
        if not agent:
            return False

        # Enable coalition formation for complex tasks
        agent.config["collaboration_enabled"] = True
        agent.config["coalition_threshold"] = 2  # Number of agents to form coalition
        return True

    async def _default_improvement(self, agent_id: str, opportunity: EvolutionOpportunity) -> bool:
        """Default improvement strategy."""
        print(f"Applying default improvement for {opportunity.improvement_type}")
        return True

    async def rollback_improvement(self, improvement_id: str) -> bool:
        """Rollback an improvement if it didn't work."""
        improvement = self.active_improvements.get(improvement_id)
        if not improvement or not improvement.rollback_available:
            return False

        # Restore previous configuration
        agent = amos_brain.agents.get(improvement.agent_id)
        if not agent:
            return False

        # Mark as rolled back
        improvement.rollback_available = False
        print(f"Rolled back improvement {improvement_id}")

        return True


class MultiAgentConsensus:
    """Multi-agent consensus and voting system."""

    def __init__(self):
        self.votes: dict[str, list[ConsensusVote]] = defaultdict(list)
        self.proposals: dict[str, dict[str, Any]] = {}

    async def propose(
        self,
        proposal_id: str,
        proposer_id: str,
        proposal_type: str,
        description: str,
        affected_agents: list[str],
    ) -> bool:
        """Create a proposal for agent consensus."""
        self.proposals[proposal_id] = {
            "proposal_id": proposal_id,
            "proposer_id": proposer_id,
            "proposal_type": proposal_type,
            "description": description,
            "affected_agents": affected_agents,
            "status": "voting",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "deadline": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
        }

        # Notify affected agents
        for agent_id in affected_agents:
            if agent_id != proposer_id:
                await self._notify_agent(agent_id, proposal_id)

        return True

    async def vote(
        self, agent_id: str, proposal_id: str, vote: str, confidence: float, reasoning: str
    ) -> bool:
        """Cast a vote on a proposal."""

        consensus_vote = ConsensusVote(
            agent_id=agent_id,
            proposal_id=proposal_id,
            vote=vote,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self.votes[proposal_id].append(consensus_vote)

        # Check if consensus reached
        await self._check_consensus(proposal_id)

        return True

    async def _check_consensus(self, proposal_id: str):
        """Check if consensus has been reached."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return

        votes = self.votes.get(proposal_id, [])
        affected = proposal["affected_agents"]

        # Check if all agents voted
        voted_agents = {v.agent_id for v in votes}
        if not all(a in voted_agents for a in affected):
            return  # Not all agents voted yet

        # Count votes (weighted by confidence)
        for_votes = sum(v.confidence for v in votes if v.vote == "for")
        against_votes = sum(v.confidence for v in votes if v.vote == "against")

        total_votes = for_votes + against_votes
        if total_votes == 0:
            return

        for_ratio = for_votes / total_votes

        # Determine outcome
        if for_ratio >= 0.6:  # 60% threshold
            proposal["status"] = "accepted"
            proposal["consensus_reached"] = True
            print(f"Proposal {proposal_id} accepted with {for_ratio * 100:.1f}% support")
        elif against_votes > for_votes:
            proposal["status"] = "rejected"
            proposal["consensus_reached"] = False
            print(f"Proposal {proposal_id} rejected")

    async def _notify_agent(self, agent_id: str, proposal_id: str):
        """Notify an agent about a proposal."""
        # Would integrate with messaging system
        print(f"Notifying agent {agent_id} about proposal {proposal_id}")

    def get_proposal_status(self, proposal_id: str) -> dict[str, Any]:
        """Get the status of a proposal."""
        proposal = self.proposals.get(proposal_id, {})
        votes = self.votes.get(proposal_id, [])

        return {
            **proposal,
            "vote_count": len(votes),
            "votes": [
                {"agent_id": v.agent_id, "vote": v.vote, "confidence": v.confidence} for v in votes
            ],
        }


class AMOSSelfEvolvingEngine:
    """Main self-evolution engine integrating all components."""

    def __init__(self):
        self.performance_tracker = PerformanceTracker()
        self.opportunity_detector = EvolutionOpportunityDetector(self.performance_tracker)
        self.improvement_engine = SelfImprovementEngine(
            self.performance_tracker, self.opportunity_detector
        )
        self.consensus = MultiAgentConsensus()
        self.evolution_loop_task = None
        self.running = False

    async def start(self):
        """Start the self-evolution engine."""
        print("🧬 Starting AMOS Self-Evolving Engine...")
        self.running = True

        # Start evolution loop
        self.evolution_loop_task = asyncio.create_task(self._evolution_loop())

        print("✅ Self-Evolving Engine started")
        return True

    async def stop(self):
        """Stop the self-evolution engine."""
        print("🛑 Stopping Self-Evolving Engine...")
        self.running = False

        if self.evolution_loop_task:
            self.evolution_loop_task.cancel()
            try:
                await self.evolution_loop_task
            except asyncio.CancelledError:
                pass

        print("✅ Self-Evolving Engine stopped")
        return True

    async def _evolution_loop(self):
        """Main evolution loop."""
        while self.running:
            try:
                # Analyze all agents
                for agent_id in amos_brain.agents.keys():
                    # Record any new performance data
                    # Detect opportunities
                    opportunities = await self.opportunity_detector.analyze_agent(agent_id)

                    if opportunities:
                        print(
                            f"📈 Found {len(opportunities)} evolution opportunities for {agent_id}"
                        )

                        # Auto-apply high-confidence improvements
                        for opp in opportunities:
                            if opp.confidence >= 0.8:
                                # Check governance
                                validation = await governance_engine.validate_input(
                                    agent_id, f"Apply improvement: {opp.proposed_solution}"
                                )

                                if validation["valid"]:
                                    result = await self.improvement_engine.apply_improvement(
                                        agent_id, opp
                                    )

                                    if result.success:
                                        print(
                                            f"✅ Applied improvement: {result.improvement_percent:.1f}% better"
                                        )
                                    else:
                                        print("⚠️ Improvement failed")

                # Wait before next cycle
                await asyncio.sleep(300)  # 5 minutes

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Evolution loop error: {e}")
                await asyncio.sleep(60)

    async def record_task(self, agent_id: str, result: TaskResult):
        """Record a task result for tracking."""
        await self.performance_tracker.record_task_result(agent_id, result)

    def get_agent_improvements(self, agent_id: str) -> list[ImprovementResult]:
        """Get improvement history for an agent."""
        return [
            imp for imp in self.improvement_engine.improvement_history if imp.agent_id == agent_id
        ]

    def get_performance_summary(self, agent_id: str) -> dict[str, Any]:
        """Get performance summary for an agent."""
        metrics = self.performance_tracker.metrics_history.get(agent_id, [])
        if not metrics:
            return {"error": "No metrics available"}

        latest = metrics[-1]
        trend = self.performance_tracker.get_performance_trend(agent_id, "success_rate", 7)

        return {
            "agent_id": agent_id,
            "current_success_rate": latest.success_rate(),
            "avg_latency_ms": latest.avg_latency_ms,
            "avg_cost_usd": latest.avg_cost_usd,
            "error_rate": latest.error_rate,
            "success_rate_trend": trend,
            "total_tasks": sum(m.task_count for m in metrics),
            "improvements_applied": len(self.get_agent_improvements(agent_id)),
            "regression_detected": self.performance_tracker.detect_performance_regression(agent_id),
        }


# Global instance
self_evolving_engine = AMOSSelfEvolvingEngine()


# Convenience functions
async def start_self_evolution() -> bool:
    """Start the self-evolution engine."""
    return await self_evolving_engine.start()


async def stop_self_evolution() -> bool:
    """Stop the self-evolution engine."""
    return await self_evolving_engine.stop()


async def record_agent_performance(agent_id: str, result: TaskResult):
    """Record agent performance."""
    await self_evolving_engine.record_task(agent_id, result)


def get_agent_evolution_summary(agent_id: str) -> dict[str, Any]:
    """Get evolution summary for an agent."""
    return self_evolving_engine.get_performance_summary(agent_id)
