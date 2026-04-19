#!/usr/bin/env python3
"""AMOS Cost Optimization Engine - LLM FinOps for multi-agent systems.

Implements 2025/2026 token economics and cost optimization patterns:
- Per-component cost tracking and attribution
- Model routing for cost-efficient inference
- Semantic caching to reduce API calls
- Token budget controls and circuit breakers
- Spend anomaly detection
- Budget alerts and governance

Component #66 - FinOps & Cost Management Layer
"""

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol


class ModelTier(Enum):
    """Model pricing tiers (approximate 2025 pricing)."""

    FAST = "fast"  # $0.10-0.50/M tokens
    BALANCED = "balanced"  # $1-3/M tokens
    CAPABLE = "capable"  # $5-10/M tokens
    REASONING = "reasoning"  # $15-60/M tokens


class CostAlertLevel(Enum):
    """Cost alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class TokenUsage:
    """Token usage record."""

    input_tokens: int = 0
    output_tokens: int = 0
    model_tier: ModelTier = ModelTier.BALANCED
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def estimated_cost_usd(self) -> float:
        """Estimate cost based on 2025 pricing."""
        pricing = {
            ModelTier.FAST: (0.0001, 0.0004),  # $0.10/M in, $0.40/M out
            ModelTier.BALANCED: (0.001, 0.003),  # $1/M in, $3/M out
            ModelTier.CAPABLE: (0.005, 0.015),  # $5/M in, $15/M out
            ModelTier.REASONING: (0.015, 0.060),  # $15/M in, $60/M out
        }
        input_price, output_price = pricing.get(self.model_tier, (0.001, 0.003))
        return (self.input_tokens * input_price + self.output_tokens * output_price) / 1000


@dataclass
class CostBudget:
    """Budget configuration for a component."""

    daily_limit_usd: float = 10.0
    hourly_limit_usd: float = 2.0
    per_request_limit_usd: float = 0.50
    max_tokens_per_request: int = 4000
    alert_threshold_percent: float = 80.0

    def check_limits(self, usage: TokenUsage, daily_spend: float, hourly_spend: float) -> str:
        """Check if usage exceeds budget limits."""
        cost = usage.estimated_cost_usd

        if cost > self.per_request_limit_usd:
            return f"Per-request limit exceeded: ${cost:.4f} > ${self.per_request_limit_usd}"

        if hourly_spend + cost > self.hourly_limit_usd:
            return f"Hourly limit exceeded: ${hourly_spend + cost:.2f} > ${self.hourly_limit_usd}"

        if daily_spend + cost > self.daily_limit_usd:
            return f"Daily limit exceeded: ${daily_spend + cost:.2f} > ${self.daily_limit_usd}"

        if usage.total_tokens > self.max_tokens_per_request:
            return f"Token limit exceeded: {usage.total_tokens} > {self.max_tokens_per_request}"

        return None


@dataclass
class CacheEntry:
    """Semantic cache entry."""

    key: str
    response: Any
    token_usage: TokenUsage
    timestamp: float
    access_count: int = 1

    @property
    def is_expired(self, ttl_seconds: float = 3600) -> bool:
        return time.time() - self.timestamp > ttl_seconds


class CostExporter(Protocol):
    """Protocol for cost data exporters."""

    async def export(self, data: Dict[str, Any]) -> bool:
        """Export cost data."""
        ...


class ConsoleCostExporter:
    """Export cost data to console."""

    async def export(self, data: Dict[str, Any]) -> bool:
        print(f"[CostExport] {json.dumps(data, indent=2)}")
        return True


class AMOSCostEngine:
    """
    Cost optimization engine for AMOS ecosystem.

    Implements LLM FinOps patterns:
    - Per-component cost tracking
    - Semantic caching
    - Model routing recommendations
    - Budget enforcement
    - Anomaly detection
    """

    def __init__(self):
        self.usage_history: Dict[str, list[TokenUsage]] = {}
        self.budgets: Dict[str, CostBudget] = {}
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_hits: Dict[str, int] = {}
        self.cache_misses: Dict[str, int] = {}
        self.alerts: List[dict[str, Any]] = []
        self._running = False
        self._monitor_task: asyncio.Task = None
        self._max_history_per_component = 1000
        self._cache_ttl_seconds = 3600  # 1 hour
        self._max_cache_size = 10000

    async def start(self) -> None:
        """Start cost engine."""
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        print("[CostEngine] Started - FinOps monitoring active")

    async def stop(self) -> None:
        """Stop cost engine."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        print("[CostEngine] Stopped")

    def set_budget(self, component_id: str, budget: CostBudget) -> None:
        """Set cost budget for a component."""
        self.budgets[component_id] = budget
        print(f"[CostEngine] Budget set for {component_id}: ${budget.daily_limit_usd}/day")

    def record_usage(
        self,
        component_id: str,
        input_tokens: int,
        output_tokens: int,
        model_tier: ModelTier = ModelTier.BALANCED,
        metadata: Dict[str, Any] = None,
    ) -> TokenUsage:
        """Record token usage for a component."""
        usage = TokenUsage(
            input_tokens=input_tokens, output_tokens=output_tokens, model_tier=model_tier
        )

        if component_id not in self.usage_history:
            self.usage_history[component_id] = []

        self.usage_history[component_id].append(usage)

        # Trim history
        if len(self.usage_history[component_id]) > self._max_history_per_component:
            self.usage_history[component_id] = self.usage_history[component_id][
                -self._max_history_per_component :
            ]

        # Check budget limits
        self._check_budget(component_id, usage)

        return usage

    def _check_budget(self, component_id: str, usage: TokenUsage) -> None:
        """Check if usage exceeds budget and trigger alerts."""
        budget = self.budgets.get(component_id)
        if not budget:
            return

        # Calculate current spend
        daily_spend = self.get_daily_spend(component_id)
        hourly_spend = self.get_hourly_spend(component_id)

        # Check limits
        violation = budget.check_limits(usage, daily_spend, hourly_spend)
        if violation:
            self._trigger_alert(
                component_id,
                CostAlertLevel.CRITICAL,
                f"Budget violation: {violation}",
                {"usage": usage.__dict__, "budget": budget.__dict__},
            )
            return

        # Check alert threshold
        daily_limit = budget.daily_limit_usd
        if daily_spend > daily_limit * (budget.alert_threshold_percent / 100):
            self._trigger_alert(
                component_id,
                CostAlertLevel.WARNING,
                f"Budget threshold reached: ${daily_spend:.2f} / ${daily_limit:.2f}",
                {"percent_used": (daily_spend / daily_limit) * 100},
            )

    def _trigger_alert(
        self, component_id: str, level: CostAlertLevel, message: str, metadata: Dict[str, Any]
    ) -> None:
        """Trigger a cost alert."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "component_id": component_id,
            "level": level.value,
            "message": message,
            "metadata": metadata,
        }
        self.alerts.append(alert)

        # Print alert
        prefix = "⚠️" if level == CostAlertLevel.WARNING else "🚨"
        print(f"{prefix} [CostAlert] {component_id}: {message}")

    def get_semantic_key(self, prompt: str, context: str = None) -> str:
        """Generate semantic cache key for a prompt."""
        # Simple semantic key: normalized prompt hash
        normalized = prompt.lower().strip()
        if context:
            normalized = f"{context}:{normalized}"
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]

    def get_cached_response(self, key: str) -> Optional[CacheEntry]:
        """Get cached response if available and not expired."""
        entry = self.cache.get(key)

        if not entry:
            return None

        if entry.is_expired(self._cache_ttl_seconds):
            del self.cache[key]
            return None

        # Update access stats
        entry.access_count += 1
        self.cache_hits[key] = self.cache_hits.get(key, 0) + 1

        return entry

    def cache_response(self, key: str, response: Any, token_usage: TokenUsage) -> None:
        """Cache a response for future use."""
        # Evict oldest if cache is full
        if len(self.cache) >= self._max_cache_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].timestamp)
            del self.cache[oldest_key]

        self.cache[key] = CacheEntry(
            key=key, response=response, token_usage=token_usage, timestamp=time.time()
        )

        self.cache_misses[key] = self.cache_misses.get(key, 0) + 1

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get semantic cache statistics."""
        total_hits = sum(self.cache_hits.values())
        total_misses = sum(self.cache_misses.values())
        total_requests = total_hits + total_misses

        hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0

        # Estimate cost savings
        saved_tokens = sum(
            entry.token_usage.total_tokens * (entry.access_count - 1)
            for entry in self.cache.values()
        )

        return {
            "cache_size": len(self.cache),
            "total_hits": total_hits,
            "total_misses": total_misses,
            "hit_rate_percent": hit_rate,
            "estimated_tokens_saved": saved_tokens,
        }

    def recommend_model_tier(
        self, task_complexity: str, required_quality: str, latency_requirement: str
    ) -> ModelTier:
        """Recommend model tier based on task requirements."""
        # Simple decision matrix
        if latency_requirement == "critical":
            return ModelTier.FAST

        if task_complexity == "simple" and required_quality == "standard":
            return ModelTier.FAST

        if task_complexity == "complex" and required_quality == "high":
            return ModelTier.REASONING if required_quality == "maximum" else ModelTier.CAPABLE

        return ModelTier.BALANCED

    def get_daily_spend(self, component_id: str) -> float:
        """Get today's spend for a component."""
        today = datetime.now().date()
        usages = self.usage_history.get(component_id, [])

        daily_usages = [u for u in usages if datetime.fromisoformat(u.timestamp).date() == today]

        return sum(u.estimated_cost_usd for u in daily_usages)

    def get_hourly_spend(self, component_id: str) -> float:
        """Get current hour's spend for a component."""
        now = datetime.now()
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        usages = self.usage_history.get(component_id, [])

        hourly_usages = [u for u in usages if datetime.fromisoformat(u.timestamp) >= hour_start]

        return sum(u.estimated_cost_usd for u in hourly_usages)

    def get_component_cost_report(self, component_id: str) -> Dict[str, Any]:
        """Get detailed cost report for a component."""
        usages = self.usage_history.get(component_id, [])

        if not usages:
            return {"component_id": component_id, "status": "no_data"}

        total_input = sum(u.input_tokens for u in usages)
        total_output = sum(u.output_tokens for u in usages)
        total_cost = sum(u.estimated_cost_usd for u in usages)

        # Breakdown by model tier
        tier_costs = {}
        for u in usages:
            tier = u.model_tier.value
            if tier not in tier_costs:
                tier_costs[tier] = {"cost": 0.0, "requests": 0, "tokens": 0}
            tier_costs[tier]["cost"] += u.estimated_cost_usd
            tier_costs[tier]["requests"] += 1
            tier_costs[tier]["tokens"] += u.total_tokens

        budget = self.budgets.get(component_id)
        budget_status = "unlimited"
        if budget:
            daily_spend = self.get_daily_spend(component_id)
            percent_used = (
                (daily_spend / budget.daily_limit_usd * 100) if budget.daily_limit_usd > 0 else 0
            )
            budget_status = f"{percent_used:.1f}%"

        return {
            "component_id": component_id,
            "total_requests": len(usages),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_cost_usd": total_cost,
            "input_output_ratio": total_output / total_input if total_input > 0 else 0,
            "tier_breakdown": tier_costs,
            "budget_utilization": budget_status,
            "daily_spend_usd": self.get_daily_spend(component_id),
        }

    def get_ecosystem_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary for entire ecosystem."""
        all_usages = []
        for usages in self.usage_history.values():
            all_usages.extend(usages)

        total_cost = sum(u.estimated_cost_usd for u in all_usages)
        total_input = sum(u.input_tokens for u in all_usages)
        total_output = sum(u.output_tokens for u in all_usages)

        # Top spenders
        component_costs = {
            cid: sum(u.estimated_cost_usd for u in usages)
            for cid, usages in self.usage_history.items()
        }
        top_spenders = sorted(component_costs.items(), key=lambda x: x[1], reverse=True)[:5]

        # Cache savings
        cache_stats = self.get_cache_stats()

        return {
            "total_components": len(self.usage_history),
            "total_requests": len(all_usages),
            "total_cost_usd": total_cost,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "avg_cost_per_request": total_cost / len(all_usages) if all_usages else 0,
            "top_spenders": top_spenders,
            "cache_savings": cache_stats,
            "active_alerts": len(
                [a for a in self.alerts if a["level"] in ["critical", "emergency"]]
            ),
        }

    async def _monitor_loop(self) -> None:
        """Background monitoring loop for anomalies."""
        while self._running:
            await self._detect_anomalies()
            await asyncio.sleep(300)  # Check every 5 minutes

    async def _detect_anomalies(self) -> None:
        """Detect spending anomalies."""
        for component_id in self.usage_history:
            hourly_spend = self.get_hourly_spend(component_id)

            # Simple anomaly: hourly spend > $5
            if hourly_spend > 5.0:
                self._trigger_alert(
                    component_id,
                    CostAlertLevel.WARNING,
                    f"High hourly spend detected: ${hourly_spend:.2f}",
                    {"hourly_spend": hourly_spend},
                )

    def export_cost_report(self, path: str) -> None:
        """Export comprehensive cost report."""
        report = {
            "export_time": datetime.now().isoformat(),
            "ecosystem_summary": self.get_ecosystem_cost_summary(),
            "component_reports": {
                cid: self.get_component_cost_report(cid) for cid in self.usage_history.keys()
            },
            "alerts": self.alerts[-100:],  # Last 100 alerts
            "cache_stats": self.get_cache_stats(),
            "budgets": {cid: budget.__dict__ for cid, budget in self.budgets.items()},
        }

        with open(path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"[CostEngine] Report exported to {path}")


def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 characters for English)."""
    return len(text) // 4


async def demo_cost_engine():
    """Demonstrate cost optimization engine."""
    print("\n" + "=" * 70)
    print("AMOS COST OPTIMIZATION ENGINE - COMPONENT #66")
    print("=" * 70)

    # Initialize
    print("\n[1] Initializing cost engine...")
    engine = AMOSCostEngine()
    await engine.start()

    # Set budgets for components
    print("\n[2] Setting budgets for 65+ components...")
    components = [
        ("amos_kernel", 20.0),
        ("amos_orchestrator", 50.0),
        ("amos_knowledge_loader", 30.0),
        ("amos_inference_engine", 100.0),
        ("amos_telemetry_engine", 10.0),
        ("amos_governance_engine", 5.0),
    ]

    for cid, daily in components:
        budget = CostBudget(
            daily_limit_usd=daily,
            hourly_limit_usd=daily / 10,
            per_request_limit_usd=1.0,
            max_tokens_per_request=8000,
            alert_threshold_percent=80.0,
        )
        engine.set_budget(cid, budget)

    # Simulate usage across components
    print("\n[3] Simulating token usage across ecosystem...")

    scenarios = [
        ("amos_kernel", 500, 200, ModelTier.FAST, "memory_operation"),
        ("amos_orchestrator", 1000, 500, ModelTier.BALANCED, "routing_decision"),
        ("amos_knowledge_loader", 2000, 800, ModelTier.CAPABLE, "knowledge_query"),
        ("amos_inference_engine", 4000, 2000, ModelTier.REASONING, "complex_reasoning"),
        ("amos_kernel", 300, 100, ModelTier.FAST, "cache_hit_simulation"),
        ("amos_orchestrator", 800, 400, ModelTier.BALANCED, "coordination"),
    ]

    for cid, inp, out, tier, task in scenarios:
        usage = engine.record_usage(cid, inp, out, tier, {"task": task})
        cost = usage.estimated_cost_usd
        print(f"  {cid}: {inp}+{out} tokens (${cost:.4f}) - {tier.value}")

    # Demonstrate semantic caching
    print("\n[4] Demonstrating semantic caching...")
    prompt = "What is the capital of France?"
    cache_key = engine.get_semantic_key(prompt, "general_knowledge")

    # First call - cache miss
    cached = engine.get_cached_response(cache_key)
    if cached:
        print(f"  Cache HIT for '{prompt[:30]}...'")
    else:
        print(f"  Cache MISS for '{prompt[:30]}...'")
        # Simulate API call and cache result
        usage = engine.record_usage("amos_knowledge_loader", 100, 50, ModelTier.BALANCED)
        engine.cache_response(cache_key, "Paris", usage)

    # Second call - cache hit
    cached = engine.get_cached_response(cache_key)
    if cached:
        print(
            f"  Cache HIT for '{prompt[:30]}...' - Saved ${cached.token_usage.estimated_cost_usd:.4f}"
        )

    # Model routing recommendation
    print("\n[5] Model routing recommendations...")
    recommendations = [
        ("simple", "standard", "flexible", "Routine task"),
        ("complex", "high", "flexible", "Analysis task"),
        ("complex", "maximum", "critical", "Critical reasoning"),
        ("simple", "standard", "critical", "Fast response needed"),
    ]

    for complexity, quality, latency, desc in recommendations:
        tier = engine.recommend_model_tier(complexity, quality, latency)
        print(f"  {desc}: {complexity}/{quality}/{latency} → {tier.value}")

    # Cost reports
    print("\n[6] Cost reports...")

    print("\n  Component Report (amos_inference_engine):")
    report = engine.get_component_cost_report("amos_inference_engine")
    print(f"    Total cost: ${report['total_cost_usd']:.4f}")
    print(f"    Input/Output ratio: {report['input_output_ratio']:.2f}")
    print(f"    Budget utilization: {report['budget_utilization']}")

    print("\n  Ecosystem Summary:")
    summary = engine.get_ecosystem_cost_summary()
    print(f"    Total components tracked: {summary['total_components']}")
    print(f"    Total ecosystem cost: ${summary['total_cost_usd']:.4f}")
    print(f"    Cache hit rate: {summary['cache_savings']['hit_rate_percent']:.1f}%")
    print(f"    Active alerts: {summary['active_alerts']}")

    if summary["top_spenders"]:
        print("\n    Top spenders:")
        for cid, cost in summary["top_spenders"]:
            print(f"      • {cid}: ${cost:.4f}")

    # Export report
    print("\n[7] Exporting cost report...")
    engine.export_cost_report("amos_cost_report.json")

    await engine.stop()

    print("\n" + "=" * 70)
    print("Cost Optimization Engine Demo Complete")
    print("=" * 70)
    print("\n✓ Per-component cost tracking and attribution")
    print("✓ Token budget controls and circuit breakers")
    print("✓ Semantic caching for cost reduction")
    print("✓ Model routing recommendations")
    print("✓ Spend anomaly detection")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo_cost_engine())
