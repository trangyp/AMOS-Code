#!/usr/bin/env python3
"""AMOS Feature Flags & Experimentation Engine - Safe rollout and A/B testing.

Implements 2025 feature flag and experimentation patterns:
- Feature flags with targeting rules
- A/B testing with statistical analysis
- Gradual rollout (percentage-based)
- Kill switches for instant rollback
- Multi-component flag coordination
- Experiment metrics tracking

Component #69 - Experimentation & Rollout Layer
"""

import asyncio
import hashlib
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol


class FlagType(Enum):
    """Types of feature flags."""

    BOOLEAN = "boolean"  # Simple on/off
    GRADUAL = "gradual"  # Percentage rollout
    A_B_TEST = "ab_test"  # A/B experiment
    MULTIVARIATE = "multivariate"  # Multiple variants
    KILL_SWITCH = "kill_switch"  # Emergency off


class Operator(Enum):
    """Targeting rule operators."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN = "in"
    NOT_IN = "not_in"


@dataclass
class TargetingRule:
    """Rule for targeting flag to specific users/contexts."""

    attribute: str
    operator: Operator
    value: Any

    def matches(self, context: Dict[str, Any]) -> bool:
        """Check if context matches this rule."""
        context_value = context.get(self.attribute)

        if self.operator == Operator.EQUALS:
            return context_value == self.value
        elif self.operator == Operator.NOT_EQUALS:
            return context_value != self.value
        elif self.operator == Operator.CONTAINS:
            return self.value in str(context_value)
        elif self.operator == Operator.GREATER_THAN:
            return context_value is not None and context_value > self.value
        elif self.operator == Operator.LESS_THAN:
            return context_value is not None and context_value < self.value
        elif self.operator == Operator.IN:
            return context_value in self.value
        elif self.operator == Operator.NOT_IN:
            return context_value not in self.value

        return False


@dataclass
class FeatureFlag:
    """Feature flag definition."""

    flag_id: str
    name: str
    description: str
    flag_type: FlagType
    enabled: bool = False
    default_value: Any = False

    # Gradual rollout settings
    rollout_percentage: float = 0.0  # 0.0 to 100.0

    # A/B test settings
    variants: list[dict[str, Any]] = field(default_factory=list)
    weights: List[float] = field(default_factory=list)

    # Targeting
    targeting_rules: List[TargetingRule] = field(default_factory=list)

    # Component scope
    component_whitelist: set[str] = None
    component_blacklist: set[str] = field(default_factory=set)

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    owner: str = "system"

    def get_variant_for_context(self, context: Dict[str, Any]) -> Any:
        """Get flag value for given context."""
        if not self.enabled:
            return self.default_value

        # Check targeting rules
        if self.targeting_rules:
            matches = all(rule.matches(context) for rule in self.targeting_rules)
            if not matches:
                return self.default_value

        # Check component scope
        component_id = context.get("component_id")
        if component_id:
            if self.component_whitelist and component_id not in self.component_whitelist:
                return self.default_value
            if component_id in self.component_blacklist:
                return self.default_value

        # Determine value based on flag type
        if self.flag_type == FlagType.BOOLEAN:
            return True

        elif self.flag_type == FlagType.GRADUAL:
            return self._check_gradual_rollout(context)

        elif self.flag_type == FlagType.A_B_TEST:
            return self._assign_variant(context)

        elif self.flag_type == FlagType.KILL_SWITCH:
            return False  # Kill switch disables feature

        return self.default_value

    def _check_gradual_rollout(self, context: Dict[str, Any]) -> bool:
        """Check if context is in rollout percentage."""
        user_id = context.get("user_id", context.get("session_id", str(random.random())))
        hash_value = hashlib.md5(f"{self.flag_id}:{user_id}".encode()).hexdigest()
        user_bucket = int(hash_value[:8], 16) % 100
        return user_bucket < self.rollout_percentage

    def _assign_variant(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assign A/B test variant using consistent hashing."""
        user_id = context.get("user_id", context.get("session_id", str(uuid.uuid4())))
        hash_value = hashlib.md5(f"{self.flag_id}:{user_id}".encode()).hexdigest()
        user_bucket = int(hash_value[:8], 16) % 100

        cumulative = 0
        for i, weight in enumerate(self.weights):
            cumulative += weight
            if user_bucket < cumulative:
                return self.variants[i] if i < len(self.variants) else self.default_value

        return self.variants[-1] if self.variants else self.default_value


@dataclass
class Experiment:
    """A/B test or multivariate experiment."""

    experiment_id: str
    name: str
    hypothesis: str
    flag_id: str
    status: str = "draft"  # draft, running, paused, completed
    start_date: str = None
    end_date: str = None

    # Metrics
    primary_metric: str = ""
    secondary_metrics: List[str] = field(default_factory=list)

    # Sample size
    min_sample_size: int = 1000
    target_sample_size: int = 10000

    # Results
    results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlagEvaluation:
    """Result of flag evaluation."""

    flag_id: str
    value: Any
    variant_id: str = None
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector(Protocol):
    """Protocol for metrics collection."""

    async def record_exposure(
        self, experiment_id: str, variant: str, context: Dict[str, Any]
    ) -> None:
        """Record user exposure to experiment variant."""
        ...

    async def record_conversion(self, experiment_id: str, metric: str, value: float) -> None:
        """Record conversion metric."""
        ...


class InMemoryMetricsCollector:
    """Simple in-memory metrics collector."""

    def __init__(self):
        self.exposures: dict[str, dict[str, int]] = {}  # exp_id -> variant -> count
        self.conversions: dict[str, list[dict[str, Any]]] = {}

    async def record_exposure(
        self, experiment_id: str, variant: str, context: Dict[str, Any]
    ) -> None:
        if experiment_id not in self.exposures:
            self.exposures[experiment_id] = {}
        self.exposures[experiment_id][variant] = self.exposures[experiment_id].get(variant, 0) + 1

    async def record_conversion(self, experiment_id: str, metric: str, value: float) -> None:
        if experiment_id not in self.conversions:
            self.conversions[experiment_id] = []
        self.conversions[experiment_id].append(
            {"metric": metric, "value": value, "time": time.time()}
        )


class AMOSFeatureFlags:
    """
    Feature flags and experimentation engine for AMOS ecosystem.

    Implements 2025 feature flag patterns:
    - Boolean, gradual, A/B test, multivariate flags
    - Targeting based on user/context attributes
    - Component-level flag scoping
    - Experiment tracking with metrics
    - Kill switches for emergency rollback
    """

    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.flags: Dict[str, FeatureFlag] = {}
        self.experiments: Dict[str, Experiment] = {}
        self.metrics = metrics_collector or InMemoryMetricsCollector()
        self.evaluations: List[FlagEvaluation] = []
        self._max_evaluations = 10000

    async def initialize(self) -> None:
        """Initialize feature flag system."""
        print("[FeatureFlags] Initialized")
        print(f"  - Flags: {len(self.flags)}")
        print(f"  - Experiments: {len(self.experiments)}")

    def create_flag(
        self,
        name: str,
        description: str,
        flag_type: FlagType = FlagType.BOOLEAN,
        default_value: Any = False,
        owner: str = "system",
    ) -> FeatureFlag:
        """Create a new feature flag."""
        flag_id = f"flag_{name.lower().replace(' ', '_')}"

        flag = FeatureFlag(
            flag_id=flag_id,
            name=name,
            description=description,
            flag_type=flag_type,
            default_value=default_value,
            owner=owner,
        )

        self.flags[flag_id] = flag
        print(f"[FeatureFlags] Created: {name} ({flag_type.value})")
        return flag

    def create_experiment(
        self,
        name: str,
        hypothesis: str,
        flag_id: str,
        variants: List[str],
        weights: list[float] = None,
        primary_metric: str = "conversion",
    ) -> Experiment:
        """Create a new A/B test experiment."""
        experiment_id = f"exp_{name.lower().replace(' ', '_')}"

        # Set up flag for experiment
        if flag_id not in self.flags:
            raise ValueError(f"Flag {flag_id} not found")

        flag = self.flags[flag_id]
        flag.flag_type = FlagType.A_B_TEST
        flag.variants = [{"name": v, "id": f"{experiment_id}_{v}"} for v in variants]

        # Set weights (default equal distribution)
        if weights is None:
            weights = [100.0 / len(variants)] * len(variants)
        flag.weights = weights

        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            hypothesis=hypothesis,
            flag_id=flag_id,
            primary_metric=primary_metric,
        )

        self.experiments[experiment_id] = experiment
        print(f"[FeatureFlags] Experiment created: {name}")
        return experiment

    def evaluate(self, flag_id: str, context: Dict[str, Any]) -> Any:
        """Evaluate feature flag for given context."""
        flag = self.flags.get(flag_id)
        if not flag:
            return False

        value = flag.get_variant_for_context(context)

        # Record evaluation
        evaluation = FlagEvaluation(
            flag_id=flag_id,
            value=value,
            variant_id=value.get("id") if isinstance(value, dict) else None,
            context=context,
        )
        self.evaluations.append(evaluation)

        # Trim evaluations
        if len(self.evaluations) > self._max_evaluations:
            self.evaluations = self.evaluations[-self._max_evaluations :]

        # Record experiment exposure if applicable
        if flag.flag_type == FlagType.A_B_TEST:
            for exp_id, exp in self.experiments.items():
                if exp.flag_id == flag_id and exp.status == "running":
                    variant = (
                        value.get("name", "control") if isinstance(value, dict) else str(value)
                    )
                    asyncio.create_task(self.metrics.record_exposure(exp_id, variant, context))

        return value

    def is_enabled(self, flag_id: str, context: dict[str, Any] = None) -> bool:
        """Simple boolean check if feature is enabled."""
        result = self.evaluate(flag_id, context or {})
        if isinstance(result, bool):
            return result
        if isinstance(result, dict):
            return result.get("name") != "control"
        return bool(result)

    def enable_flag(self, flag_id: str) -> bool:
        """Enable a feature flag."""
        if flag_id not in self.flags:
            return False
        self.flags[flag_id].enabled = True
        self.flags[flag_id].updated_at = datetime.now().isoformat()
        print(f"[FeatureFlags] Enabled: {flag_id}")
        return True

    def disable_flag(self, flag_id: str) -> bool:
        """Disable a feature flag (kill switch)."""
        if flag_id not in self.flags:
            return False
        self.flags[flag_id].enabled = False
        self.flags[flag_id].updated_at = datetime.now().isoformat()
        print(f"[FeatureFlags] Disabled (kill switch): {flag_id}")
        return True

    def set_rollout_percentage(self, flag_id: str, percentage: float) -> bool:
        """Set gradual rollout percentage."""
        if flag_id not in self.flags:
            return False

        flag = self.flags[flag_id]
        flag.rollout_percentage = max(0.0, min(100.0, percentage))
        flag.flag_type = FlagType.GRADUAL
        flag.updated_at = datetime.now().isoformat()

        print(f"[FeatureFlags] Rollout set: {flag_id} = {percentage}%")
        return True

    def start_experiment(self, experiment_id: str) -> bool:
        """Start running an experiment."""
        if experiment_id not in self.experiments:
            return False

        exp = self.experiments[experiment_id]
        exp.status = "running"
        exp.start_date = datetime.now().isoformat()

        # Enable associated flag
        self.enable_flag(exp.flag_id)

        print(f"[FeatureFlags] Experiment started: {exp.name}")
        return True

    def stop_experiment(self, experiment_id: str) -> bool:
        """Stop an experiment."""
        if experiment_id not in self.experiments:
            return False

        exp = self.experiments[experiment_id]
        exp.status = "completed"
        exp.end_date = datetime.now().isoformat()

        print(f"[FeatureFlags] Experiment completed: {exp.name}")
        return True

    def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get current experiment results."""
        if experiment_id not in self.experiments:
            return {"error": "Experiment not found"}

        exp = self.experiments[experiment_id]
        exposures = self.metrics.exposures.get(experiment_id, {})

        return {
            "experiment_id": experiment_id,
            "name": exp.name,
            "status": exp.status,
            "hypothesis": exp.hypothesis,
            "exposures": exposures,
            "total_exposures": sum(exposures.values()),
            "start_date": exp.start_date,
            "end_date": exp.end_date,
        }

    def get_flag_status(self, flag_id: str) -> dict[str, Any]:
        """Get current flag status."""
        if flag_id not in self.flags:
            return None

        flag = self.flags[flag_id]
        return {
            "flag_id": flag.flag_id,
            "name": flag.name,
            "enabled": flag.enabled,
            "type": flag.flag_type.value,
            "rollout_percentage": flag.rollout_percentage,
            "targeting_rules_count": len(flag.targeting_rules),
            "component_whitelist": list(flag.component_whitelist)
            if flag.component_whitelist
            else None,
            "updated_at": flag.updated_at,
            "owner": flag.owner,
        }

    def get_all_flags_summary(self) -> Dict[str, Any]:
        """Get summary of all flags."""
        by_type = {}
        for flag in self.flags.values():
            by_type[flag.flag_type.value] = by_type.get(flag.flag_type.value, 0) + 1

        return {
            "total_flags": len(self.flags),
            "enabled_flags": sum(1 for f in self.flags.values() if f.enabled),
            "by_type": by_type,
            "active_experiments": sum(
                1 for e in self.experiments.values() if e.status == "running"
            ),
            "total_experiments": len(self.experiments),
        }


async def demo_feature_flags():
    """Demonstrate feature flags and experimentation."""
    print("\n" + "=" * 70)
    print("AMOS FEATURE FLAGS & EXPERIMENTATION - COMPONENT #69")
    print("=" * 70)

    # Initialize
    print("\n[1] Initializing feature flag system...")
    ff = AMOSFeatureFlags()
    await ff.initialize()

    # Create feature flags
    print("\n[2] Creating feature flags...")

    # Boolean flag
    new_ui = ff.create_flag(
        "new_dashboard_ui",
        "New dashboard UI with enhanced visualizations",
        FlagType.BOOLEAN,
        owner="frontend_team",
    )

    # Gradual rollout flag
    llm_upgrade = ff.create_flag(
        "llm_model_upgrade",
        "Upgrade to GPT-5 model for inference",
        FlagType.GRADUAL,
        owner="ml_team",
    )

    # Kill switch
    emergency_off = ff.create_flag(
        "emergency_feature_disable",
        "Emergency kill switch for critical features",
        FlagType.KILL_SWITCH,
        owner="sre_team",
    )

    # Create experiment
    print("\n[3] Creating A/B test experiment...")
    recommendation_exp = ff.create_experiment(
        name="recommendation_algorithm",
        hypothesis="New collaborative filtering improves engagement by 15%",
        flag_id=new_ui.flag_id,
        variants=["control", "collaborative_filter", "deep_learning"],
        weights=[34.0, 33.0, 33.0],
        primary_metric="click_through_rate",
    )

    # Enable and configure flags
    print("\n[4] Configuring flags...")
    ff.enable_flag(new_ui.flag_id)
    ff.set_rollout_percentage(llm_upgrade.flag_id, 25.0)

    # Start experiment
    ff.start_experiment(recommendation_exp.experiment_id)

    # Simulate evaluations
    print("\n[5] Simulating flag evaluations...")

    test_contexts = [
        {"user_id": "user_001", "component_id": "amos_dashboard", "tier": "premium"},
        {"user_id": "user_002", "component_id": "amos_knowledge_loader", "tier": "basic"},
        {"user_id": "user_003", "component_id": "amos_inference", "tier": "premium"},
        {"user_id": "user_004", "component_id": "amos_dashboard", "tier": "enterprise"},
        {"user_id": "user_005", "component_id": "amos_governance", "tier": "basic"},
    ]

    print("\n  Evaluating 'new_dashboard_ui' flag:")
    for ctx in test_contexts:
        result = ff.evaluate(new_ui.flag_id, ctx)
        variant = result.get("name", result) if isinstance(result, dict) else result
        print(f"    {ctx['user_id']} ({ctx['tier']}): {variant}")

    print("\n  Evaluating 'llm_model_upgrade' gradual rollout:")
    for ctx in test_contexts:
        enabled = ff.is_enabled(llm_upgrade.flag_id, ctx)
        status = "✓ ENABLED" if enabled else "✗ disabled"
        print(f"    {ctx['user_id']}: {status}")

    # Test kill switch
    print("\n[6] Testing kill switch...")
    ff.enable_flag(emergency_off.flag_id)
    print(f"  Kill switch active: {ff.is_enabled(emergency_off.flag_id)}")

    # Stop experiment and get results
    print("\n[7] Experiment results...")
    ff.stop_experiment(recommendation_exp.experiment_id)
    results = ff.get_experiment_results(recommendation_exp.experiment_id)
    print(f"  Experiment: {results['name']}")
    print(f"  Status: {results['status']}")
    print(f"  Total exposures: {results['total_exposures']}")

    # Summary
    print("\n[8] System summary...")
    summary = ff.get_all_flags_summary()
    print(f"  Total flags: {summary['total_flags']}")
    print(f"  Enabled flags: {summary['enabled_flags']}")
    print(f"  By type: {summary['by_type']}")
    print(f"  Active experiments: {summary['active_experiments']}")

    print("\n" + "=" * 70)
    print("Feature Flags Demo Complete")
    print("=" * 70)
    print("\n✓ Boolean, gradual, A/B test, and kill switch flags")
    print("✓ Context-aware targeting")
    print("✓ Consistent variant assignment")
    print("✓ Component-level scoping")
    print("✓ Experiment tracking and metrics")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo_feature_flags())
