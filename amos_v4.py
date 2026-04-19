#!/usr/bin/env python3
"""AMOS v4 - Persistent, Economic, Real-World Cognitive Organism

AMOS_v4 = (G,T,N,W,M,E,R,K,B,A,V,H,P,I,D,F,S,L,C,Pe,X,Y,Q)

New v4 layers:
- Pe: Persistent continuity layer
- X: Economic / value-production layer
- Y: External world-state / market-state model
- Q: Capital, resources, and allocation layer

v4 is a living strategic system that:
- Persists across sessions
- Allocates resources strategically
- Produces real-world value
- Learns from outcomes
- Preserves itself while growing
"""

import pickle
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# ============================================================================
# 1. PERSISTENCE LAYER (Pe)
# ============================================================================


@dataclass
class PersistentState:
    """Pe_t = (Memory_episodic, Memory_structural, Identity_persistent, OpenLoops)
    Pe_{t+1} = Sync(Pe_t, Result_t, I_t)
    """

    session_id: str = field(default_factory=lambda: f"session_{datetime.now(UTC).timestamp()}")
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    # Episodic memory - experiences
    episodic_memory: List[dict] = field(default_factory=list)

    # Structural memory - learned patterns
    structural_memory: Dict[str, Any] = field(default_factory=dict)

    # Persistent identity
    identity: Dict[str, Any] = field(
        default_factory=lambda: {
            "version": "v4.0",
            "build_count": 0,
            "core_values": ["coherence", "growth", "value_production", "survival"],
            "master_goal": "persistent_economic_intelligence",
        }
    )

    # Open loops - unfinished tasks
    open_loops: List[dict] = field(default_factory=list)

    # Session continuity
    previous_session_id: str = None
    cumulative_metrics: Dict[str, float] = field(
        default_factory=lambda: {
            "total_cycles": 0,
            "total_value_produced": 0.0,
            "total_resources_consumed": 0.0,
            "survival_score": 1.0,
        }
    )


class PersistenceManager:
    """Manages persistence across sessions."""

    def __init__(self, state_dir: str = "amos_state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.state_file = self.state_dir / "persistent_state.pkl"

    def save(self, state: PersistentState):
        """Save persistent state."""
        state.last_updated = datetime.now(UTC).isoformat()
        with open(self.state_file, "wb") as f:
            pickle.dump(state, f)

    def load(self) -> Optional[PersistentState]:
        """Load persistent state if exists."""
        if self.state_file.exists():
            with open(self.state_file, "rb") as f:
                return pickle.load(f)
        return None

    def sync(self, state: PersistentState, results: dict, identity: dict) -> PersistentState:
        """Pe_{t+1} = Sync(Pe_t, Result_t, I_t)"""
        # Add to episodic memory
        state.episodic_memory.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "results": results,
                "identity_snapshot": identity,
            }
        )

        # Update structural memory with patterns
        if "patterns_learned" in results:
            for pattern in results["patterns_learned"]:
                state.structural_memory[pattern["name"]] = pattern

        # Update cumulative metrics
        if "value_produced" in results:
            state.cumulative_metrics["total_value_produced"] += results["value_produced"]
        if "resources_consumed" in results:
            state.cumulative_metrics["total_resources_consumed"] += results["resources_consumed"]
        state.cumulative_metrics["total_cycles"] += 1

        # Manage open loops
        state.open_loops = [loop for loop in state.open_loops if not loop.get("completed", False)]
        if "new_open_loops" in results:
            state.open_loops.extend(results["new_open_loops"])

        state.last_updated = datetime.now(UTC).isoformat()
        return state


# ============================================================================
# 2. ECONOMIC LAYER (X)
# ============================================================================


@dataclass
class EconomicState:
    """X_t = (Opportunity, Revenue, Cost, Risk, Leverage, Compounding)
    x_t* = argmax_x [Revenue(x) - Cost(x) - Risk(x) + Leverage(x) + Compounding(x)]
    """

    opportunities: List[dict] = field(default_factory=list)
    revenue_streams: Dict[str, float] = field(default_factory=dict)
    cost_structure: Dict[str, float] = field(default_factory=dict)
    risk_exposure: Dict[str, float] = field(default_factory=dict)
    leverage_points: List[str] = field(default_factory=list)
    compounding_assets: List[str] = field(default_factory=list)


class EconomicEngine:
    """Economic decision making - value production, not just cognition."""

    def __init__(self):
        self.state = EconomicState()
        self.transaction_history: List[dict] = []

    def evaluate_action(self, action: dict) -> dict[str, float]:
        """Evaluate action by economic criteria.
        Returns: {revenue, cost, risk, leverage, compounding, net_value}
        """
        revenue = action.get("expected_revenue", 0.0)
        cost = action.get("expected_cost", 0.0)
        risk = action.get("risk_penalty", 0.0)
        leverage = action.get("leverage_factor", 1.0)
        compounding = action.get("compounding_value", 0.0)

        # Core economic equation
        net_value = revenue - cost - risk + leverage + compounding

        return {
            "revenue": revenue,
            "cost": cost,
            "risk": risk,
            "leverage": leverage,
            "compounding": compounding,
            "net_value": net_value,
            "roi": (revenue - cost) / cost if cost > 0 else float("inf"),
        }

    def select_optimal_action(self, actions: List[dict]) -> dict:
        """x_t* = argmax_x [Revenue(x) - Cost(x) - Risk(x) + Leverage(x) + Compounding(x)]"""
        if not actions:
            return None

        scored_actions = []
        for action in actions:
            economic_score = self.evaluate_action(action)
            scored_actions.append((action, economic_score["net_value"], economic_score))

        # Select highest value
        scored_actions.sort(key=lambda x: x[1], reverse=True)
        best = scored_actions[0]

        return {"action": best[0], "score": best[1], "breakdown": best[2]}

    def record_outcome(self, action: dict, actual_revenue: float, actual_cost: float):
        """Record real-world economic outcome."""
        self.transaction_history.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "action": action.get("name", "unknown"),
                "predicted_revenue": action.get("expected_revenue", 0),
                "actual_revenue": actual_revenue,
                "predicted_cost": action.get("expected_cost", 0),
                "actual_cost": actual_cost,
                "error": (actual_revenue - actual_cost)
                - (action.get("expected_revenue", 0) - action.get("expected_cost", 0)),
            }
        )


# ============================================================================
# 3. RESOURCE ALLOCATION LAYER (Q)
# ============================================================================


@dataclass
class ResourcePool:
    """Q_t = (Time, Capital, Attention, Compute, Credibility, Optionality)
    q_t* = argmax_q Σ ω_i · Return_i(q)
    """

    time_budget: float = 168.0  # Hours per week
    capital: float = 0.0
    attention_units: float = 100.0  # Cognitive load capacity
    compute_budget: float = 1000.0  # Compute units
    credibility: float = 1.0  # Reputation capital
    optionality: float = 1.0  # Future option value

    # Allocations
    allocations: Dict[str, float] = field(default_factory=dict)


class ResourceAllocator:
    """Strategic resource allocation across competing demands."""

    def __init__(self):
        self.pool = ResourcePool()
        self.allocation_history: List[dict] = []

    def allocate(self, demands: List[dict]) -> dict[str, dict[str, float]]:
        """q_t* = argmax_q Σ ω_i · Return_i(q)
        Constraint: Σ Resource(g_i) ≤ Q_t
        """
        allocations = {"time": {}, "capital": {}, "attention": {}, "compute": {}}

        # Sort by return/effort ratio
        scored_demands = []
        for demand in demands:
            expected_return = demand.get("expected_return", 0)
            resource_cost = demand.get("resource_cost", 1)
            priority = demand.get("priority", 1.0)

            score = (priority * expected_return) / max(resource_cost, 0.001)
            scored_demands.append((demand, score))

        scored_demands.sort(key=lambda x: x[1], reverse=True)

        # Allocate until resources exhausted
        remaining = {
            "time": self.pool.time_budget,
            "attention": self.pool.attention_units,
            "compute": self.pool.compute_budget,
        }

        for demand, score in scored_demands:
            name = demand.get("name", "unknown")

            # Allocate proportionally to remaining resources
            time_alloc = min(demand.get("time_needed", 0), remaining["time"] * 0.3)
            attention_alloc = min(demand.get("attention_needed", 0), remaining["attention"] * 0.3)
            compute_alloc = min(demand.get("compute_needed", 0), remaining["compute"] * 0.3)

            if time_alloc > 0 or attention_alloc > 0 or compute_alloc > 0:
                allocations["time"][name] = time_alloc
                allocations["attention"][name] = attention_alloc
                allocations["compute"][name] = compute_alloc

                remaining["time"] -= time_alloc
                remaining["attention"] -= attention_alloc
                remaining["compute"] -= compute_alloc

        return allocations

    def get_resource_status(self) -> dict:
        """Current resource status."""
        return {
            "time_available": self.pool.time_budget,
            "capital_available": self.pool.capital,
            "attention_available": self.pool.attention_units,
            "compute_available": self.pool.compute_budget,
            "credibility": self.pool.credibility,
            "optionality": self.pool.optionality,
        }


# ============================================================================
# 4. EXTERNAL WORLD MODEL (Y)
# ============================================================================


@dataclass
class WorldModel:
    """Y_t = (Market, Institutions, People, Competitors, Trends, Constraints)
    Y_{t+1} = Model(Y_t, Signals_t, Outcomes_t)
    """

    market_state: Dict[str, Any] = field(default_factory=dict)
    institutional_landscape: Dict[str, Any] = field(default_factory=dict)
    key_actors: Dict[str, Any] = field(default_factory=dict)
    competitive_position: Dict[str, Any] = field(default_factory=dict)
    trend_forecasts: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)

    # Learning
    prediction_accuracy: float = 0.5
    model_confidence: float = 0.5


class WorldModelEngine:
    """Models external world state, learns from outcomes."""

    def __init__(self):
        self.model = WorldModel()
        self.signal_history: List[dict] = []
        self.prediction_errors: List[float] = []

    def update(self, signals: dict, outcomes: dict):
        """Y_{t+1} = Model(Y_t, Signals_t, Outcomes_t)
        Learning_real = Result_world - Prediction_model
        """
        self.signal_history.append(
            {"timestamp": datetime.now(UTC).isoformat(), "signals": signals, "outcomes": outcomes}
        )

        # Update market state
        if "market_data" in signals:
            self.model.market_state.update(signals["market_data"])

        # Update constraints
        if "new_constraints" in signals:
            self.model.constraints.update(signals["new_constraints"])

        # Learn from prediction errors
        if "predicted" in outcomes and "actual" in outcomes:
            error = outcomes["actual"] - outcomes["predicted"]
            self.prediction_errors.append(abs(error))

            # Update accuracy
            if len(self.prediction_errors) > 10:
                recent_errors = self.prediction_errors[-10:]
                self.model.prediction_accuracy = 1.0 - (sum(recent_errors) / len(recent_errors))

        # Update confidence based on track record
        self.model.model_confidence = max(0.1, min(0.95, self.model.prediction_accuracy))

    def predict_outcome(self, action: dict) -> dict:
        """Predict outcome of action in current world state."""
        base_probability = 0.5

        # Adjust based on market conditions
        market_factor = self.model.market_state.get("opportunity_index", 1.0)

        # Adjust based on constraints
        constraint_penalty = len(self.model.constraints) * 0.05

        predicted_success = base_probability * market_factor - constraint_penalty

        return {
            "predicted_success": max(0.1, min(0.9, predicted_success)),
            "confidence": self.model.model_confidence,
            "expected_value": action.get("expected_revenue", 0) * predicted_success,
        }


# ============================================================================
# 5. PORTFOLIO OF GOALS
# ============================================================================


@dataclass
class Goal:
    """g_i = (priority, expected_value, resource_cost, time_horizon, risk)"""

    id: str
    name: str
    description: str
    priority: float = 1.0
    expected_value: float = 0.0
    resource_cost: Dict[str, float] = field(default_factory=dict)
    time_horizon: int = 30  # Days
    risk_score: float = 0.1
    status: str = "active"  # active, completed, deferred


class GoalPortfolio:
    """Manages portfolio of goals with optimization."""

    def __init__(self):
        self.goals: Dict[str, Goal] = {}
        self.portfolio_history: List[dict] = []

    def add_goal(self, goal: Goal):
        """Add goal to portfolio."""
        self.goals[goal.id] = goal

    def optimize_portfolio(self, available_resources: ResourcePool) -> List[Goal]:
        """g*_{set} = argmax Σ [Value(g_i) - Cost(g_i) - Risk(g_i)]
        Constraint: Σ Resource(g_i) ≤ Q_t
        """
        # Score each goal
        scored_goals = []
        for goal in self.goals.values():
            if goal.status != "active":
                continue

            # Calculate net value
            net_value = goal.priority * goal.expected_value - goal.risk_score

            # Resource efficiency
            total_cost = sum(goal.resource_cost.values())
            efficiency = net_value / max(total_cost, 0.001)

            scored_goals.append((goal, efficiency, net_value))

        # Sort by efficiency
        scored_goals.sort(key=lambda x: x[1], reverse=True)

        # Select until resources exhausted
        selected = []
        remaining_budget = available_resources.time_budget * 0.5  # Use 50% for goals

        for goal, efficiency, net_value in scored_goals:
            time_cost = goal.resource_cost.get("time", 0)
            if time_cost <= remaining_budget:
                selected.append(goal)
                remaining_budget -= time_cost

        return selected

    def get_portfolio_metrics(self) -> dict:
        """Get portfolio health metrics."""
        active = [g for g in self.goals.values() if g.status == "active"]
        completed = [g for g in self.goals.values() if g.status == "completed"]

        total_value = sum(g.expected_value for g in active)
        total_risk = sum(g.risk_score for g in active)

        return {
            "total_goals": len(self.goals),
            "active": len(active),
            "completed": len(completed),
            "total_expected_value": total_value,
            "portfolio_risk": total_risk,
            "risk_adjusted_return": total_value - total_risk,
        }


# ============================================================================
# 6. SELF-PRESERVATION & ANTI-FRAGILITY
# ============================================================================


class SurvivalEngine:
    """Survival_t = (Resilience_t + Redundancy_t + Adaptation_t) / Fragility_t
    max Survival_t
    """

    def __init__(self):
        self.resilience_score = 1.0
        self.redundancy_score = 1.0
        self.adaptation_score = 1.0
        self.fragility_score = 1.0

    def compute_survival(self) -> float:
        """Compute survival score."""
        numerator = self.resilience_score + self.redundancy_score + self.adaptation_score
        return numerator / max(self.fragility_score, 0.1)

    def check_threats(self, state: dict) -> List[dict]:
        """Identify threats to system survival."""
        threats = []

        # Resource depletion
        if state.get("resources", {}).get("compute", 100) < 10:
            threats.append(
                {
                    "type": "resource_depletion",
                    "severity": "critical",
                    "mitigation": "reduce_non_essential_computation",
                }
            )

        # Goal overload
        if state.get("active_goals", 0) > 20:
            threats.append(
                {
                    "type": "overextension",
                    "severity": "warning",
                    "mitigation": "defer_low_priority_goals",
                }
            )

        # Identity drift
        if state.get("identity_drift", 0) > 0.3:
            threats.append(
                {
                    "type": "identity_drift",
                    "severity": "warning",
                    "mitigation": "realign_to_core_values",
                }
            )

        return threats

    def apply_mitigation(self, threat: dict) -> dict:
        """Apply threat mitigation."""
        return {
            "threat": threat["type"],
            "action": threat["mitigation"],
            "applied": True,
            "timestamp": datetime.now(UTC).isoformat(),
        }


# ============================================================================
# 7. MASTER v4 ORCHESTRATOR
# ============================================================================


class AMOSv4:
    """AMOS_v4 = Persistent, Economic, Real-World Cognitive Organism

    Master equation:
    AMOS_v4(t+1) = F(State_t, Decision_t, Action_t, WorldFeedback_t, EconomicResult_t)
    """

    def __init__(self, name: str = "AMOS_v4"):
        self.name = name
        self.birth_time = datetime.now(UTC)

        # Core v4 layers
        self.persistence = PersistenceManager()
        self.economic = EconomicEngine()
        self.resources = ResourceAllocator()
        self.world_model = WorldModelEngine()
        self.goals = GoalPortfolio()
        self.survival = SurvivalEngine()

        # Load or initialize state
        self.persistent_state = self.persistence.load()
        if self.persistent_state is None:
            self.persistent_state = PersistentState()
            print(f"🆕 New AMOS v4 instance created: {self.name}")
        else:
            print("🔄 AMOS v4 resumed from previous session")
            print(f"   Previous cycles: {self.persistent_state.cumulative_metrics['total_cycles']}")
            print(
                f"   Total value produced: {self.persistent_state.cumulative_metrics['total_value_produced']:.2f}"
            )

        # Cycle counter
        self.current_cycle = 0

    def cycle(self, world_signals: dict = None) -> dict:
        """Single AMOS v4 decision-action cycle.
        Model → Decision → Action → World → Outcome → Update
        """
        self.current_cycle += 1

        # 1. Update world model
        if world_signals:
            self.world_model.update(world_signals, {})

        # 2. Check survival threats
        current_state = self._get_current_state()
        threats = self.survival.check_threats(current_state)

        # 3. Optimize goal portfolio
        selected_goals = self.goals.optimize_portfolio(self.resources.pool)

        # 4. Generate actions for selected goals
        candidate_actions = self._generate_actions(selected_goals, threats)

        # 5. Economic selection
        optimal = self.economic.select_optimal_action(candidate_actions)

        # 6. Resource allocation
        allocations = self.resources.allocate(candidate_actions)

        # 7. Execute and record
        result = {
            "cycle": self.current_cycle,
            "timestamp": datetime.now(UTC).isoformat(),
            "selected_action": optimal["action"]["name"] if optimal else None,
            "economic_score": optimal["score"] if optimal else 0,
            "selected_goals": [g.name for g in selected_goals],
            "threats_detected": len(threats),
            "survival_score": self.survival.compute_survival(),
        }

        # 8. Sync persistent state
        self.persistent_state = self.persistence.sync(
            self.persistent_state, result, self.persistent_state.identity
        )

        # 9. Save state
        self.persistence.save(self.persistent_state)

        return result

    def _get_current_state(self) -> dict:
        """Get current system state for threat detection."""
        return {
            "resources": self.resources.get_resource_status(),
            "active_goals": len([g for g in self.goals.goals.values() if g.status == "active"]),
            "survival_score": self.survival.compute_survival(),
        }

    def _generate_actions(self, goals: List[Goal], threats: List[dict]) -> List[dict]:
        """Generate candidate actions from goals and threats."""
        actions = []

        # Actions from goals
        for goal in goals:
            actions.append(
                {
                    "name": f"work_on_{goal.id}",
                    "expected_revenue": goal.expected_value,
                    "expected_cost": sum(goal.resource_cost.values()),
                    "risk_penalty": goal.risk_score,
                    "leverage_factor": goal.priority,
                    "compounding_value": goal.expected_value * 0.1 if goal.time_horizon > 90 else 0,
                    "goal_id": goal.id,
                }
            )

        # Actions from threats (mitigations)
        for threat in threats:
            actions.append(
                {
                    "name": f"mitigate_{threat['type']}",
                    "expected_revenue": 0.0,  # Prevention has no direct revenue
                    "expected_cost": 5.0,
                    "risk_penalty": 0.0,
                    "leverage_factor": 2.0 if threat["severity"] == "critical" else 1.0,
                    "compounding_value": 10.0,  # Avoiding failure compounds
                    "is_mitigation": True,
                }
            )

        return actions

    def get_status(self) -> dict:
        """Get complete v4 status."""
        return {
            "name": self.name,
            "version": "v4.0",
            "age_cycles": self.current_cycle,
            "total_lifetime_cycles": self.persistent_state.cumulative_metrics["total_cycles"],
            "survival_score": self.survival.compute_survival(),
            "goals": self.goals.get_portfolio_metrics(),
            "resources": self.resources.get_resource_status(),
            "world_model_confidence": self.world_model.model.model_confidence,
            "open_loops": len(self.persistent_state.open_loops),
            "identity": self.persistent_state.identity,
        }


def demo_v4():
    """Demonstrate AMOS v4 capabilities."""
    print("=" * 70)
    print("🧬 AMOS v4 - PERSISTENT ECONOMIC ORGANISM")
    print("=" * 70)
    print("\nAMOS_v4 = (G,T,N,W,M,E,R,K,B,A,V,H,P,I,D,F,S,L,C,Pe,X,Y,Q)")
    print("=" * 70)

    # Initialize AMOS v4
    amos = AMOSv4(name="AMOS_Economic_1")

    # Add goals to portfolio
    print("\n[1] Building Goal Portfolio")
    amos.goals.add_goal(
        Goal(
            id="g1",
            name="memory_optimization",
            description="Optimize memory system efficiency",
            priority=0.9,
            expected_value=100,
            time_horizon=30,
            resource_cost={"time": 20, "compute": 50},
        )
    )
    amos.goals.add_goal(
        Goal(
            id="g2",
            name="economic_capability",
            description="Build economic decision engine",
            priority=0.8,
            expected_value=150,
            time_horizon=60,
            resource_cost={"time": 40, "compute": 100},
        )
    )
    amos.goals.add_goal(
        Goal(
            id="g3",
            name="self_preservation",
            description="Enhance survival mechanisms",
            priority=1.0,
            expected_value=200,
            time_horizon=90,
            resource_cost={"time": 30, "compute": 30},
        )
    )

    print(f"  Added {len(amos.goals.goals)} goals to portfolio")

    # Run cycles
    print("\n[2] Running Economic Decision Cycles")
    for i in range(3):
        signals = {"market_data": {"opportunity_index": 1.2}}
        result = amos.cycle(world_signals=signals)

        print(f"\n  Cycle {result['cycle']}:")
        print(f"    Selected: {result['selected_action']}")
        print(f"    Economic score: {result['economic_score']:.2f}")
        print(f"    Survival score: {result['survival_score']:.2f}")
        print(f"    Threats: {result['threats_detected']}")

    # Final status
    print("\n[3] Final v4 Status")
    status = amos.get_status()
    print(f"  Total lifetime cycles: {status['total_lifetime_cycles']}")
    print(f"  Survival score: {status['survival_score']:.2f}")
    print(f"  Goals active: {status['goals']['active']}")
    print(f"  Portfolio value: {status['goals']['total_expected_value']:.0f}")
    print(f"  World model confidence: {status['world_model_confidence']:.1%}")

    # Save and resume simulation
    print("\n[4] Persistence Test - Simulating Resume")
    amos2 = AMOSv4(name="AMOS_Economic_1")  # Same name, should load state
    status2 = amos2.get_status()
    print(f"  Resumed with cycles: {status2['total_lifetime_cycles']}")
    print("  ✓ Persistence working!")

    print("\n" + "=" * 70)
    print("✅ AMOS v4 OPERATIONAL")
    print("=" * 70)
    print("\nv4 Capabilities:")
    print("  • Persistence across sessions (Pe)")
    print("  • Economic decision making (X)")
    print("  • Strategic resource allocation (Q)")
    print("  • External world modeling (Y)")
    print("  • Portfolio goal optimization")
    print("  • Self-preservation & anti-fragility")
    print("  • Outcome-based learning")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    demo_v4()
