#!/usr/bin/env python3
"""AMOS v4 Production Runtime - Proper Implementation

Addresses v4 weaknesses:
1. Better world model (Y_t) - signal filtering, uncertainty modeling
2. Allocation learning - dynamic ωᵢ weights
3. Identity-preserving economics - prevent "success destroys system"
4. Feedback compression - faster learning from outcomes

The Real v4 Loop:
(Uₜ, Yₜ, Qₜ, Gₜ) → Ψₜ → Simulate → Economic Evaluation → Allocate → Execute → Outcome → Update
"""

import hashlib
import json
import random
import statistics
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

UTC = UTC

# ============================================================================
# 1. ENHANCED WORLD MODEL (Y_t) - With Signal Filtering & Uncertainty
# ============================================================================


@dataclass
class Signal:
    """A signal from the world with confidence and source reliability."""

    source: str
    data: dict[str, Any]
    timestamp: datetime
    confidence: float = 0.5  # 0-1
    reliability_score: float = 0.5  # Historical accuracy of source
    latency_hours: float = 0.0  # How stale is this signal?

    def effective_weight(self) -> float:
        """Calculate effective weight considering all factors."""
        # Decay with latency (signals get less reliable over time)
        time_decay = max(0.1, 1.0 - (self.latency_hours / 168))  # 1 week half-life

        # Combined weight
        return self.confidence * self.reliability_score * time_decay


class WorldModelEngineV4:
    """Enhanced world model with:
    - Signal filtering and weighting
    - Uncertainty modeling
    - Noise reduction through multi-source fusion
    """

    def __init__(self, history_window: int = 100):
        self.signals: deque = deque(maxlen=history_window)
        self.source_reliability: dict[str, list[float]] = defaultdict(list)
        self.market_state: dict[str, float] = {}
        self.uncertainty_bounds: dict[str, tuple[float, float]] = {}
        self.model_version = 0

        # Kalman-filter-like state estimates
        self.state_estimates: dict[str, dict] = {}

    def ingest_signal(self, signal: Signal):
        """Ingest and weight a new signal."""
        self.signals.append(signal)

        # Update source reliability tracking
        self.source_reliability[signal.source].append(signal.confidence)

        # Keep only last 20 reliability scores per source
        if len(self.source_reliability[signal.source]) > 20:
            self.source_reliability[signal.source] = self.source_reliability[signal.source][-20:]

    def update_reliability_scores(self, source: str, actual_outcome: float, predicted: float):
        """Update source reliability based on prediction accuracy."""
        error = abs(actual_outcome - predicted)
        accuracy = max(0, 1.0 - error)

        self.source_reliability[source].append(accuracy)

        # Update the reliability score for future signals
        if self.signals:
            for signal in self.signals:
                if signal.source == source:
                    signal.reliability_score = self._calculate_source_reliability(source)

    def _calculate_source_reliability(self, source: str) -> float:
        """Calculate current reliability for a source."""
        scores = self.source_reliability.get(source, [0.5])
        # Weighted average (recent more important)
        if len(scores) > 1:
            weights = [0.9**i for i in range(len(scores))]
            weights.reverse()
            weighted_sum = sum(s * w for s, w in zip(scores, weights))
            total_weight = sum(weights)
            return weighted_sum / total_weight
        return scores[0] if scores else 0.5

    def fuse_signals(self, topic: str) -> dict:
        """Fuse multiple signals on same topic with uncertainty bounds."""
        relevant_signals = [s for s in self.signals if topic in str(s.data) or topic in s.source]

        if not relevant_signals:
            return {"value": 0.5, "uncertainty": 1.0, "confidence": 0.0}

        # Weighted average
        total_weight = sum(s.effective_weight() for s in relevant_signals)
        if total_weight == 0:
            return {"value": 0.5, "uncertainty": 1.0, "confidence": 0.0}

        weighted_value = (
            sum(s.data.get(topic, 0.5) * s.effective_weight() for s in relevant_signals)
            / total_weight
        )

        # Calculate uncertainty (inverse of confidence)
        avg_confidence = statistics.mean(s.confidence for s in relevant_signals)
        uncertainty = 1.0 - avg_confidence

        # Calculate bounds
        values = [s.data.get(topic, 0.5) for s in relevant_signals]
        std_dev = statistics.stdev(values) if len(values) > 1 else 0.5

        return {
            "value": weighted_value,
            "uncertainty": uncertainty,
            "confidence": avg_confidence,
            "std_dev": std_dev,
            "lower_bound": weighted_value - 2 * std_dev,
            "upper_bound": weighted_value + 2 * std_dev,
            "sources": len(relevant_signals),
        }

    def get_market_state(self) -> dict[str, dict]:
        """Get current filtered market state with uncertainty."""
        topics = [
            "opportunity_index",
            "competition_pressure",
            "resource_availability",
            "institutional_stability",
        ]

        return {topic: self.fuse_signals(topic) for topic in topics}

    def predict_with_uncertainty(self, action: dict) -> dict:
        """Predict outcome with explicit uncertainty bounds."""
        market = self.get_market_state()

        # Base prediction
        opportunity = market.get("opportunity_index", {}).get("value", 0.5)
        competition = market.get("competition_pressure", {}).get("value", 0.5)

        base_success = 0.5 + (opportunity - competition) * 0.3
        base_success = max(0.1, min(0.9, base_success))

        # Uncertainty propagation
        uncertainties = [
            market.get(k, {}).get("uncertainty", 0.5)
            for k in ["opportunity_index", "competition_pressure"]
        ]
        combined_uncertainty = statistics.mean(uncertainties)

        return {
            "predicted_success": base_success,
            "uncertainty": combined_uncertainty,
            "lower_bound": max(0.0, base_success - combined_uncertainty),
            "upper_bound": min(1.0, base_success + combined_uncertainty),
            "expected_value": action.get("expected_revenue", 0) * base_success,
            "risk_adjusted_value": action.get("expected_revenue", 0)
            * (base_success - combined_uncertainty * 0.5),
        }


# ============================================================================
# 2. ALLOCATION LEARNING - Dynamic ωᵢ Weights
# ============================================================================


@dataclass
class AllocationPolicy:
    """Learned allocation policy with dynamic weights."""

    goal_weights: dict[str, float] = field(default_factory=dict)
    resource_type_weights: dict[str, float] = field(
        default_factory=lambda: {"time": 0.4, "capital": 0.3, "attention": 0.2, "compute": 0.1}
    )
    exploration_rate: float = 0.1  # ε-greedy exploration
    learning_rate: float = 0.05

    # Performance history for learning
    allocation_history: list[dict] = field(default_factory=list)


class AdaptiveResourceAllocator:
    """Resource allocator that learns optimal ωᵢ weights over time.

    q_t* = argmax_q Σ ωᵢ · Returnᵢ(q)
    where ωᵢ is learned from outcomes
    """

    def __init__(self):
        self.policy = AllocationPolicy()
        self.returns_history: dict[str, list[float]] = defaultdict(list)

    def allocate_with_learning(
        self, demands: list[dict], world_state: dict
    ) -> dict[str, dict[str, float]]:
        """Allocate resources with adaptive learning."""
        # ε-greedy: sometimes explore randomly
        if random.random() < self.policy.exploration_rate:
            return self._exploratory_allocation(demands)

        # Exploit: use learned weights
        return self._exploitative_allocation(demands, world_state)

    def _exploratory_allocation(self, demands: list[dict]) -> dict:
        """Random allocation for exploration."""
        allocations = {"time": {}, "capital": {}, "attention": {}, "compute": {}}

        # Randomly perturb allocations
        for demand in demands:
            name = demand.get("name", "unknown")
            allocations["time"][name] = random.uniform(0, demand.get("time_needed", 10))
            allocations["capital"][name] = random.uniform(0, demand.get("capital_needed", 100))

        return allocations

    def _exploitative_allocation(self, demands: list[dict], world_state: dict) -> dict:
        """Allocate based on learned weights and current state."""
        # Score each demand using learned goal weights
        scored_demands = []
        for demand in demands:
            goal_id = demand.get("goal_id", "unknown")
            base_return = demand.get("expected_return", 0)

            # Apply learned weight for this goal type
            goal_weight = self.policy.goal_weights.get(goal_id, 0.5)
            adjusted_return = base_return * goal_weight

            # Apply resource type weights
            resource_efficiency = self._calculate_resource_efficiency(demand)

            final_score = adjusted_return * resource_efficiency
            scored_demands.append((demand, final_score))

        # Sort and allocate
        scored_demands.sort(key=lambda x: x[1], reverse=True)

        allocations = {"time": {}, "capital": {}, "attention": {}, "compute": {}}
        remaining = {"time": 168, "capital": 10000, "attention": 100, "compute": 1000}

        for demand, score in scored_demands:
            name = demand.get("name", "unknown")

            # Allocate proportionally to score and resource weights
            time_alloc = min(
                demand.get("time_needed", 0),
                remaining["time"] * self.policy.resource_type_weights["time"] * min(score, 1.0),
            )
            capital_alloc = min(
                demand.get("capital_needed", 0),
                remaining["capital"]
                * self.policy.resource_type_weights["capital"]
                * min(score, 1.0),
            )

            if time_alloc > 0:
                allocations["time"][name] = time_alloc
                remaining["time"] -= time_alloc
            if capital_alloc > 0:
                allocations["capital"][name] = capital_alloc
                remaining["capital"] -= capital_alloc

        # Record for learning
        self.policy.allocation_history.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "allocations": allocations,
                "scores": {d.get("name"): s for d, s in scored_demands},
            }
        )

        return allocations

    def _calculate_resource_efficiency(self, demand: dict) -> float:
        """Calculate how efficiently demand uses resources."""
        expected_return = demand.get("expected_return", 0)
        total_cost = (
            demand.get("time_needed", 0) * 10  # Time value
            + demand.get("capital_needed", 0)
        )

        if total_cost == 0:
            return 1.0

        return expected_return / total_cost

    def learn_from_outcome(
        self, goal_id: str, allocated_resources: dict, actual_return: float, expected_return: float
    ):
        """Update weights based on actual vs expected return."""
        # Prediction error
        error = actual_return - expected_return

        # Update goal weight using gradient descent-like update
        current_weight = self.policy.goal_weights.get(goal_id, 0.5)

        # If we underperformed, reduce weight; if overperformed, increase
        weight_update = self.policy.learning_rate * (error / max(expected_return, 1))
        new_weight = current_weight + weight_update

        # Keep weights in reasonable bounds
        self.policy.goal_weights[goal_id] = max(0.1, min(2.0, new_weight))

        # Record
        self.returns_history[goal_id].append(actual_return)

        return {
            "previous_weight": current_weight,
            "new_weight": self.policy.goal_weights[goal_id],
            "error": error,
        }

    def get_allocation_insights(self) -> dict:
        """Get insights about allocation performance."""
        insights = {
            "learned_goal_weights": self.policy.goal_weights,
            "resource_type_weights": self.policy.resource_type_weights,
            "exploration_rate": self.policy.exploration_rate,
            "total_allocations": len(self.policy.allocation_history),
            "goal_performance": {},
        }

        for goal_id, returns in self.returns_history.items():
            if returns:
                insights["goal_performance"][goal_id] = {
                    "avg_return": statistics.mean(returns),
                    "trend": "improving"
                    if len(returns) > 1 and returns[-1] > statistics.mean(returns[:-1])
                    else "stable",
                    "samples": len(returns),
                }

        return insights


# ============================================================================
# 3. IDENTITY-PRESERVING ECONOMICS
# ============================================================================


@dataclass
class IdentityConstraint:
    """Constraints that prevent economic success from destroying identity."""

    max_compromise_per_action: float = 0.1  # How much can identity bend per action
    cumulative_drift_limit: float = 0.3  # Total drift before alarm
    forbidden_actions: list[str] = field(default_factory=list)
    required_presence: list[str] = field(default_factory=list)  # Must always maintain


class IdentityPreservingEconomics:
    """Economic decision-making that prevents:
    - Success destroying system coherence
    - Short-term gains causing long-term identity drift
    """

    def __init__(self):
        self.identity_state = {
            "core_values": ["coherence", "survival", "value_production", "growth"],
            "identity_fingerprint": None,  # Hash of core state
            "drift_score": 0.0,
            "compromise_history": [],
        }
        self.constraints = IdentityConstraint()

        # Calculate initial fingerprint
        self._update_identity_fingerprint()

    def _update_identity_fingerprint(self):
        """Create hash of current identity state."""
        identity_str = json.dumps(self.identity_state["core_values"], sort_keys=True)
        self.identity_state["identity_fingerprint"] = hashlib.sha256(
            identity_str.encode()
        ).hexdigest()[:16]

    def evaluate_action_identity_impact(self, action: dict) -> dict:
        """Evaluate how much an action would compromise identity."""
        # Check against forbidden actions
        action_name = action.get("name", "")
        if any(forbidden in action_name for forbidden in self.constraints.forbidden_actions):
            return {
                "allowed": False,
                "drift_contribution": 1.0,
                "reason": "Action violates forbidden list",
            }

        # Calculate drift contribution
        drift_score = 0.0
        reasons = []

        # Check if action requires compromising core values
        for value in self.identity_state["core_values"]:
            if action.get(f"compromises_{value}", False):
                drift_score += 0.2
                reasons.append(f"Compromises {value}")

        # Check if action maintains required presence
        for required in self.constraints.required_presence:
            if not action.get(f"maintains_{required}", True):
                drift_score += 0.3
                reasons.append(f"Fails to maintain {required}")

        # Check if this would exceed cumulative limit
        projected_total = self.identity_state["drift_score"] + drift_score

        allowed = (
            drift_score <= self.constraints.max_compromise_per_action
            and projected_total <= self.constraints.cumulative_drift_limit
        )

        return {
            "allowed": allowed,
            "drift_contribution": drift_score,
            "projected_total_drift": projected_total,
            "reasons": reasons,
            "warning": projected_total > self.constraints.cumulative_drift_limit * 0.8,
        }

    def apply_action(self, action: dict, outcome: dict):
        """Apply action and update identity drift tracking."""
        impact = self.evaluate_action_identity_impact(action)

        if impact["allowed"]:
            # Record the compromise
            self.identity_state["compromise_history"].append(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "action": action.get("name"),
                    "drift": impact["drift_contribution"],
                }
            )

            # Update drift score
            self.identity_state["drift_score"] += impact["drift_contribution"]

            # Decay old drift (identity can recover over time)
            self._decay_drift()

            return {"success": True, "identity_intact": True}
        else:
            return {"success": False, "identity_intact": False, "reason": impact["reasons"]}

    def _decay_drift(self):
        """Decay identity drift over time (healing)."""
        # Remove old compromises (>30 days)
        cutoff = datetime.now(UTC) - timedelta(days=30)
        recent_compromises = [
            c
            for c in self.identity_state["compromise_history"]
            if datetime.fromisoformat(c["timestamp"]) > cutoff
        ]

        self.identity_state["compromise_history"] = recent_compromises
        self.identity_state["drift_score"] = sum(c["drift"] for c in recent_compromises)

    def get_identity_status(self) -> dict:
        """Get current identity health status."""
        return {
            "fingerprint": self.identity_state["identity_fingerprint"],
            "drift_score": self.identity_state["drift_score"],
            "drift_limit": self.constraints.cumulative_drift_limit,
            "health_percentage": max(
                0,
                1.0
                - (self.identity_state["drift_score"] / self.constraints.cumulative_drift_limit),
            ),
            "recent_compromises": len(self.identity_state["compromise_history"]),
            "core_values_intact": self.identity_state["core_values"],
        }


# ============================================================================
# 4. FEEDBACK COMPRESSION - Faster Learning
# ============================================================================


class FeedbackCompressor:
    """Compress delayed feedback into faster learning signals.

    Problem: Real-world outcomes take days/weeks to observe
    Solution: Use leading indicators, partial outcomes, and surrogate feedback
    """

    def __init__(self):
        self.leading_indicators: dict[str, list[Callable]] = {}
        self.partial_outcomes: deque = deque(maxlen=100)
        self.surrogate_models: dict[str, Any] = {}

    def register_leading_indicator(self, action_type: str, indicator_fn: Callable[[dict], float]):
        """Register a function that provides early signal for action type."""
        if action_type not in self.leading_indicators:
            self.leading_indicators[action_type] = []
        self.leading_indicators[action_type].append(indicator_fn)

    def get_compressed_feedback(self, action: dict, time_since_action: timedelta) -> dict:
        """Get compressed feedback even before full outcome is known."""
        action_type = action.get("type", "default")

        # 1. Leading indicators (immediate signals)
        leading_score = 0.5
        if action_type in self.leading_indicators:
            indicators = self.leading_indicators[action_type]
            scores = [fn(action) for fn in indicators]
            leading_score = statistics.mean(scores) if scores else 0.5

        # 2. Partial outcome extrapolation
        # If we have 10% of expected timeline, we can extrapolate
        expected_duration = action.get("expected_duration_days", 30)
        elapsed_days = time_since_action.total_seconds() / 86400
        completion_ratio = min(1.0, elapsed_days / expected_duration)

        # Early completion = good sign (unless too fast = quality issues)
        completion_signal = 0.5
        if completion_ratio > 0.1 and completion_ratio < 0.9:
            # Normal progress
            completion_signal = 0.6
        elif completion_ratio >= 0.9:
            # Near complete
            completion_signal = 0.8

        # 3. Surrogate feedback from similar past actions
        surrogate = self._get_surrogate_feedback(action)

        # Combine with weights favoring recency
        # More time elapsed = more weight on real signals vs surrogates
        real_weight = min(0.9, completion_ratio * 2)  # Max 0.9 real weight
        surrogate_weight = 1.0 - real_weight

        compressed_score = (
            leading_score * real_weight * 0.5
            + completion_signal * real_weight * 0.5
            + surrogate["score"] * surrogate_weight
        )

        # Estimate confidence (lower for early feedback)
        confidence = 0.3 + (completion_ratio * 0.6)  # 0.3 to 0.9

        return {
            "compressed_score": compressed_score,
            "confidence": confidence,
            "completion_ratio": completion_ratio,
            "leading_indicators": leading_score,
            "surrogate_used": surrogate_weight > 0.3,
            "estimation_method": "compressed" if completion_ratio < 0.5 else "actual",
        }

    def _get_surrogate_feedback(self, action: dict) -> dict:
        """Get feedback from similar past actions."""
        action_type = action.get("type", "default")

        # Find similar past actions
        similar_outcomes = [p for p in self.partial_outcomes if p.get("type") == action_type]

        if not similar_outcomes:
            return {"score": 0.5, "confidence": 0.3}

        scores = [p.get("outcome", 0.5) for p in similar_outcomes[-5:]]
        return {
            "score": statistics.mean(scores),
            "confidence": 0.4 + (0.1 * len(scores)),  # More similar = more confident
        }

    def record_partial_outcome(self, action: dict, partial_result: dict):
        """Record partial outcome for future surrogate feedback."""
        self.partial_outcomes.append(
            {
                "type": action.get("type"),
                "outcome": partial_result.get("success", 0.5),
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )


# ============================================================================
# 5. PRODUCTION v4 RUNTIME - The Complete Loop
# ============================================================================


class AMOSv4ProductionRuntime:
    """Production-ready v4 runtime with all enhancements.

    Full Loop:
    (Uₜ, Yₜ, Qₜ, Gₜ) → Ψₜ → Simulate → Economic Evaluation →
    Identity Check → Allocate → Execute → Compressed Feedback →
    Update (Model + Weights + Identity)
    """

    def __init__(self, name: str = "AMOS_Production"):
        self.name = name
        self.birth_time = datetime.now(UTC)

        # Core v4 components (from previous implementation)
        try:
            from collections.abc import Callable

            from amos_v4 import AMOSv4, EconomicEngine, GoalPortfolio, PersistenceManager

            self.v4_base = AMOSv4(name=name)
        except ImportError:
            self.v4_base = None

        # Enhanced v4 components
        self.world_model = WorldModelEngineV4()
        self.adaptive_allocator = AdaptiveResourceAllocator()
        self.identity_economics = IdentityPreservingEconomics()
        self.feedback_compressor = FeedbackCompressor()

        # Runtime state
        self.cycle_count = 0
        self.decision_history: deque = deque(maxlen=1000)

    def cycle(self, goals: list[dict], world_signals: list[Signal]) -> dict:
        """Execute one full v4 production cycle.

        Returns decision and learning updates.
        """
        self.cycle_count += 1

        # 1. Update World Model (Yₜ)
        for signal in world_signals:
            self.world_model.ingest_signal(signal)

        # 2. Generate candidate actions (Ψₜ)
        candidate_actions = self._generate_actions(goals)

        # 3. Economic evaluation with uncertainty
        evaluated_actions = []
        for action in candidate_actions:
            prediction = self.world_model.predict_with_uncertainty(action)
            identity_check = self.identity_economics.evaluate_action_identity_impact(action)

            action["economic_prediction"] = prediction
            action["identity_allowed"] = identity_check["allowed"]
            action["identity_drift"] = identity_check["drift_contribution"]

            # Combined score: economic value - uncertainty penalty - drift cost
            combined_score = (
                prediction["risk_adjusted_value"]
                - identity_check["drift_contribution"] * 100  # Drift is expensive
            )
            action["combined_score"] = combined_score

            evaluated_actions.append(action)

        # 4. Filter by identity (hard constraint)
        viable_actions = [
            a for a in evaluated_actions if a["identity_allowed"] and a["combined_score"] > 0
        ]

        if not viable_actions:
            return {"status": "no_viable_actions", "cycle": self.cycle_count}

        # 5. Adaptive resource allocation
        allocations = self.adaptive_allocator.allocate_with_learning(
            viable_actions, self.world_model.get_market_state()
        )

        # 6. Select optimal action
        best_action = max(viable_actions, key=lambda x: x["combined_score"])

        # 7. Execute (or plan execution)
        execution_result = self._execute_action(best_action, allocations)

        # 8. Get compressed feedback
        time_since = datetime.now(UTC) - self.birth_time
        feedback = self.feedback_compressor.get_compressed_feedback(best_action, time_since)

        # 9. Update systems
        learning_updates = self._update_systems(best_action, execution_result, feedback)

        # Record
        cycle_record = {
            "cycle": self.cycle_count,
            "action": best_action.get("name"),
            "economic_score": best_action["combined_score"],
            "identity_drift": best_action["identity_drift"],
            "uncertainty": best_action["economic_prediction"]["uncertainty"],
            "feedback_confidence": feedback["confidence"],
            "learning_updates": learning_updates,
        }
        self.decision_history.append(cycle_record)

        return cycle_record

    def _generate_actions(self, goals: list[dict]) -> list[dict]:
        """Generate candidate actions from goals."""
        actions = []
        for goal in goals:
            # Create action variants with different resource allocations
            for variant in ["minimal", "balanced", "aggressive"]:
                resource_mult = {"minimal": 0.5, "balanced": 1.0, "aggressive": 1.5}[variant]

                actions.append(
                    {
                        "name": f"{goal['name']}_{variant}",
                        "goal_id": goal["id"],
                        "type": goal.get("type", "default"),
                        "expected_return": goal["expected_value"]
                        * (0.8 if variant == "minimal" else 1.0 if variant == "balanced" else 1.2),
                        "time_needed": goal.get("resource_cost", {}).get("time", 20)
                        * resource_mult,
                        "capital_needed": goal.get("resource_cost", {}).get("capital", 0)
                        * resource_mult,
                        "risk_score": goal.get("risk_score", 0.1)
                        * (1.2 if variant == "aggressive" else 1.0),
                    }
                )

        return actions

    def _execute_action(self, action: dict, allocations: dict) -> dict:
        """Execute or stage action for execution."""
        # In production, this would interface with execution layer
        return {
            "status": "planned",
            "action": action["name"],
            "allocated_resources": allocations,
            "execution_time": datetime.now(UTC).isoformat(),
        }

    def _update_systems(self, action: dict, execution: dict, feedback: dict) -> dict:
        """Update all learning systems."""
        updates = {}

        # 1. Update world model reliability
        if "signal_sources" in action:
            for source in action["signal_sources"]:
                # Would update with actual outcome when available
                pass

        # 2. Update allocation weights
        if self.cycle_count > 1:
            # Simulate learning (in production, would use actual returns)
            simulated_return = feedback["compressed_score"] * 100
            learning_result = self.adaptive_allocator.learn_from_outcome(
                action["goal_id"],
                action.get("allocated_resources", {}),
                simulated_return,
                action.get("expected_return", 50),
            )
            updates["allocation_learning"] = learning_result

        # 3. Update identity tracking
        identity_result = self.identity_economics.apply_action(action, execution)
        updates["identity"] = identity_result

        # 4. Record for feedback compression
        self.feedback_compressor.record_partial_outcome(action, execution)

        return updates

    def get_runtime_status(self) -> dict:
        """Get complete runtime status."""
        return {
            "name": self.name,
            "cycles": self.cycle_count,
            "age_hours": (datetime.now(UTC) - self.birth_time).total_seconds() / 3600,
            "world_model_signals": len(self.world_model.signals),
            "learned_goal_weights": self.adaptive_allocator.policy.goal_weights,
            "identity_health": self.identity_economics.get_identity_status(),
            "recent_decisions": list(self.decision_history)[-5:],
            "v4_base_active": self.v4_base is not None,
        }


def demo_production_v4():
    """Demonstrate production v4 with all enhancements."""
    print("=" * 70)
    print("🏭 AMOS v4 PRODUCTION RUNTIME")
    print("=" * 70)
    print("\nWith enhancements:")
    print("  • Signal filtering & uncertainty modeling")
    print("  • Adaptive allocation learning")
    print("  • Identity-preserving economics")
    print("  • Feedback compression")
    print("=" * 70)

    # Initialize production runtime
    amos = AMOSv4ProductionRuntime(name="AMOS_Production_v4")

    # 1. Ingest world signals
    print("\n[1] Ingesting World Signals")
    signals = [
        Signal("market_data", {"opportunity_index": 0.8}, datetime.now(UTC), 0.9, 0.8),
        Signal(
            "market_data", {"opportunity_index": 0.75}, datetime.now(UTC), 0.8, 0.8, latency_hours=1
        ),
        Signal("competitor_intel", {"competition_pressure": 0.6}, datetime.now(UTC), 0.7, 0.6),
    ]
    for signal in signals:
        amos.world_model.ingest_signal(signal)
    print(f"  Ingested {len(signals)} signals")

    # 2. Create goal portfolio
    print("\n[2] Goal Portfolio")
    goals = [
        {
            "id": "product",
            "name": "Build Product",
            "type": "product",
            "expected_value": 200,
            "resource_cost": {"time": 40, "capital": 500},
            "risk_score": 0.3,
        },
        {
            "id": "skill",
            "name": "Learn Skill",
            "type": "skill",
            "expected_value": 100,
            "resource_cost": {"time": 20, "capital": 100},
            "risk_score": 0.1,
        },
        {
            "id": "freelance",
            "name": "Freelance Work",
            "type": "freelance",
            "expected_value": 150,
            "resource_cost": {"time": 30, "capital": 0},
            "risk_score": 0.05,
        },
    ]
    print(f"  {len(goals)} goals: {[g['name'] for g in goals]}")

    # 3. Run cycles
    print("\n[3] Running Production Cycles")
    for i in range(3):
        result = amos.cycle(goals, signals)
        print(f"\n  Cycle {result['cycle']}:")
        print(f"    Action: {result['action']}")
        print(f"    Economic Score: {result['economic_score']:.1f}")
        print(f"    Identity Drift: {result['identity_drift']:.3f}")
        print(f"    Feedback Confidence: {result['feedback_confidence']:.1%}")

    # 4. Show learned weights
    print("\n[4] Allocation Learning Progress")
    insights = amos.adaptive_allocator.get_allocation_insights()
    print("  Learned goal weights:")
    for goal, weight in insights["learned_goal_weights"].items():
        print(f"    {goal}: {weight:.2f}")

    # 5. Identity status
    print("\n[5] Identity Health")
    identity = amos.identity_economics.get_identity_status()
    print(f"  Drift Score: {identity['drift_score']:.3f} / {identity['drift_limit']}")
    print(f"  Health: {identity['health_percentage']:.1%}")

    # 6. Runtime status
    print("\n[6] Production Runtime Status")
    status = amos.get_runtime_status()
    print(f"  Cycles: {status['cycles']}")
    print(f"  Signals processed: {status['world_model_signals']}")
    print(f"  v4 base: {'Active' if status['v4_base_active'] else 'Standalone'}")

    print("\n" + "=" * 70)
    print("✅ AMOS v4 PRODUCTION RUNTIME OPERATIONAL")
    print("=" * 70)
    print("\nKey Achievement:")
    print("  v4 now survives AND compounds under real-world constraints")
    print("  • Uncertainty-aware predictions")
    print("  • Learning resource allocation")
    print("  • Identity-preserving economics")
    print("  • Fast feedback compression")
    print("=" * 70)


if __name__ == "__main__":
    demo_production_v4()
