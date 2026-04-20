"""AMOS AI Cost Management & Budget Control System.

Provides comprehensive cost tracking, budgeting, and optimization for AI/LLM
operations. Essential for production systems to control token costs and
prevent budget overruns.

Features:
- Token usage tracking and cost calculation
- Budget allocation and enforcement
- Rate limiting based on budget
- Cost optimization recommendations
- Real-time cost dashboards
- Alerting on budget thresholds
- Multi-tenant cost attribution

Research Sources:
- LLM Token Management 2026 (Silentinfotech, Redis)
- AI Agent Cost Optimization 2026 (Moltbook)
- LLM API Cost Comparison 2026 (Zenvanriel)

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timedelta, timezone
from typing import Any

UTC = UTC
import asyncio
from collections import defaultdict
from enum import Enum

# Cost configuration
DEFAULT_BUDGET_USD = float(os.getenv("DEFAULT_AI_BUDGET_USD", "100.0"))
BUDGET_ALERT_THRESHOLD = float(os.getenv("BUDGET_ALERT_THRESHOLD", "0.8"))
COST_TRACKING_ENABLED = os.getenv("COST_TRACKING_ENABLED", "true").lower() == "true"

# 2026 LLM Pricing (per 1M tokens)
LLM_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    "claude-3-opus": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    "gemini-2.0-pro": {"input": 3.50, "output": 10.50},
}


class BudgetPeriod(Enum):
    """Budget period types."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class AlertLevel(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class TokenUsage:
    """Tracks token usage for a request."""

    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int = 0
    cost_usd: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    agent_id: str = ""
    request_id: str = ""

    def __post_init__(self):
        if self.total_tokens == 0:
            self.total_tokens = self.input_tokens + self.output_tokens
        if self.cost_usd == 0.0:
            self.cost_usd = self.calculate_cost()

    def calculate_cost(self) -> float:
        """Calculate cost based on pricing."""
        pricing = LLM_PRICING.get(self.model, {"input": 1.0, "output": 3.0})
        input_cost = (self.input_tokens / 1_000_000) * pricing["input"]
        output_cost = (self.output_tokens / 1_000_000) * pricing["output"]
        return round(input_cost + output_cost, 6)


@dataclass
class Budget:
    """Represents a budget allocation."""

    budget_id: str
    name: str
    allocated_usd: float
    spent_usd: float = 0.0
    period: str = "monthly"
    start_date: str = ""
    end_date: str = ""
    alerts_enabled: bool = True
    alert_threshold: float = 0.8
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def remaining(self) -> float:
        """Get remaining budget."""
        return max(0.0, self.allocated_usd - self.spent_usd)

    def utilization_percent(self) -> float:
        """Get budget utilization percentage."""
        if self.allocated_usd == 0:
            return 0.0
        return (self.spent_usd / self.allocated_usd) * 100

    def is_exceeded(self) -> bool:
        """Check if budget is exceeded."""
        return self.spent_usd >= self.allocated_usd

    def should_alert(self) -> bool:
        """Check if alert should be triggered."""
        return self.alerts_enabled and self.utilization_percent() >= (self.alert_threshold * 100)


@dataclass
class CostAlert:
    """Represents a cost alert."""

    alert_id: str
    budget_id: str
    alert_level: str
    message: str
    utilization_percent: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    acknowledged: bool = False


class AICostManager:
    """Manages AI costs and budgets."""

    def __init__(self):
        self.token_usage: list[TokenUsage] = []
        self.budgets: dict[str, Budget] = {}
        self.alerts: list[CostAlert] = []
        self.usage_by_agent: dict[str, list[TokenUsage]] = defaultdict(list)
        self.usage_by_model: dict[str, list[TokenUsage]] = defaultdict(list)
        self.daily_usage: dict[str, float] = defaultdict(float)
        self.max_history = 10000
        self._lock = asyncio.Lock()

        # Initialize default budget
        self._init_default_budget()

    def _init_default_budget(self):
        """Initialize default system budget."""
        default_budget = Budget(
            budget_id="default",
            name="System Default Budget",
            allocated_usd=DEFAULT_BUDGET_USD,
            period=BudgetPeriod.MONTHLY.value,
            alert_threshold=BUDGET_ALERT_THRESHOLD,
        )
        self.budgets["default"] = default_budget

    async def track_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        agent_id: str = "",
        request_id: str = "",
    ) -> TokenUsage:
        """Track token usage and calculate cost."""
        if not COST_TRACKING_ENABLED:
            return TokenUsage(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                agent_id=agent_id,
                request_id=request_id,
            )

        async with self._lock:
            usage = TokenUsage(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                agent_id=agent_id,
                request_id=request_id,
            )

            # Add to history
            self.token_usage.append(usage)

            # Trim history if needed
            if len(self.token_usage) > self.max_history:
                self.token_usage = self.token_usage[-self.max_history :]

            # Track by agent
            if agent_id:
                self.usage_by_agent[agent_id].append(usage)

            # Track by model
            self.usage_by_model[model].append(usage)

            # Track daily usage
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            self.daily_usage[today] += usage.cost_usd

            # Update budgets
            await self._update_budgets(usage.cost_usd)

            return usage

    async def _update_budgets(self, cost: float):
        """Update all active budgets with new cost."""
        for budget in self.budgets.values():
            budget.spent_usd += cost

            # Check for alerts
            if budget.should_alert() and budget.alerts_enabled:
                await self._create_alert(budget)

    async def _create_alert(self, budget: Budget):
        """Create a budget alert."""
        import uuid

        utilization = budget.utilization_percent()

        if utilization >= 100:
            level = AlertLevel.CRITICAL.value
            message = f"Budget '{budget.name}' EXCEEDED! Spent: ${budget.spent_usd:.2f} / ${budget.allocated_usd:.2f}"
        elif utilization >= 90:
            level = AlertLevel.WARNING.value
            message = f"Budget '{budget.name}' at {utilization:.1f}%! Spent: ${budget.spent_usd:.2f} / ${budget.allocated_usd:.2f}"
        else:
            level = AlertLevel.INFO.value
            message = f"Budget '{budget.name}' at {utilization:.1f}% threshold"

        alert = CostAlert(
            alert_id=str(uuid.uuid4())[:8],
            budget_id=budget.budget_id,
            alert_level=level,
            message=message,
            utilization_percent=utilization,
        )

        self.alerts.append(alert)

        # Log alert
        print(f"🚨 Cost Alert [{level.upper()}]: {message}")

    def create_budget(
        self,
        name: str,
        allocated_usd: float,
        period: str = "monthly",
        alert_threshold: float = 0.8,
        metadata: dict[str, Any] = None,
    ) -> Budget:
        """Create a new budget."""
        import uuid

        # Calculate period dates
        now = datetime.now(timezone.utc)
        if period == BudgetPeriod.DAILY.value:
            start = now.strftime("%Y-%m-%d")
            end = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        elif period == BudgetPeriod.WEEKLY.value:
            start = now.strftime("%Y-%m-%d")
            end = (now + timedelta(weeks=1)).strftime("%Y-%m-%d")
        elif period == BudgetPeriod.YEARLY.value:
            start = now.strftime("%Y-01-01")
            end = now.strftime("%Y-12-31")
        else:  # monthly
            start = now.strftime("%Y-%m-01")
            next_month = now.replace(day=28) + timedelta(days=4)
            end = (next_month - timedelta(days=next_month.day)).strftime("%Y-%m-%d")

        budget = Budget(
            budget_id=str(uuid.uuid4())[:8],
            name=name,
            allocated_usd=allocated_usd,
            period=period,
            start_date=start,
            end_date=end,
            alert_threshold=alert_threshold,
            metadata=metadata or {},
        )

        self.budgets[budget.budget_id] = budget
        return budget

    def get_budget(self, budget_id: str) -> Budget:
        """Get budget by ID."""
        return self.budgets.get(budget_id)

    def list_budgets(self) -> list[Budget]:
        """List all budgets."""
        return list(self.budgets.values())

    def check_budget_available(
        self, budget_id: str = "default", estimated_cost: float = 0.0
    ) -> bool:
        """Check if budget has remaining funds."""
        budget = self.budgets.get(budget_id)
        if not budget:
            return True  # No budget = no restriction

        return budget.remaining() >= estimated_cost

    def get_cost_summary(self, days: int = 30) -> dict[str, Any]:
        """Get cost summary for specified period."""
        if not self.token_usage:
            return {
                "total_cost_usd": 0.0,
                "total_tokens": 0,
                "request_count": 0,
                "models_used": [],
                "daily_average": 0.0,
            }

        # Filter by date
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        recent_usage = [u for u in self.token_usage if datetime.fromisoformat(u.timestamp) > cutoff]

        total_cost = sum(u.cost_usd for u in recent_usage)
        total_tokens = sum(u.total_tokens for u in recent_usage)

        # Group by model
        model_costs = defaultdict(float)
        for u in recent_usage:
            model_costs[u.model] += u.cost_usd

        # Daily usage
        daily_costs = defaultdict(float)
        for u in recent_usage:
            day = datetime.fromisoformat(u.timestamp).strftime("%Y-%m-%d")
            daily_costs[day] += u.cost_usd

        return {
            "period_days": days,
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "request_count": len(recent_usage),
            "models_used": [{"model": m, "cost_usd": round(c, 4)} for m, c in model_costs.items()],
            "daily_average": round(total_cost / days, 4) if days > 0 else 0,
            "daily_breakdown": dict(daily_costs),
        }

    def get_agent_costs(self, agent_id: str, days: int = 30) -> dict[str, Any]:
        """Get cost breakdown for a specific agent."""
        usage = self.usage_by_agent.get(agent_id, [])

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        recent_usage = [u for u in usage if datetime.fromisoformat(u.timestamp) > cutoff]

        total_cost = sum(u.cost_usd for u in recent_usage)
        total_tokens = sum(u.total_tokens for u in recent_usage)

        # By model
        by_model = defaultdict(lambda: {"cost": 0.0, "tokens": 0})
        for u in recent_usage:
            by_model[u.model]["cost"] += u.cost_usd
            by_model[u.model]["tokens"] += u.total_tokens

        return {
            "agent_id": agent_id,
            "period_days": days,
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "request_count": len(recent_usage),
            "by_model": {
                m: {"cost_usd": round(d["cost"], 4), "tokens": d["tokens"]}
                for m, d in by_model.items()
            },
        }

    def get_optimization_recommendations(self) -> list[dict[str, Any]]:
        """Get cost optimization recommendations."""
        recommendations = []

        summary = self.get_cost_summary(days=7)

        # Check for expensive models
        expensive_models = [m for m in summary.get("models_used", []) if m["cost_usd"] > 10.0]
        if expensive_models:
            recommendations.append(
                {
                    "type": "model_optimization",
                    "priority": "high",
                    "message": f"High spending on premium models: {', '.join(m['model'] for m in expensive_models)}. Consider using smaller models for non-critical tasks.",
                    "potential_savings": "60-80%",
                }
            )

        # Check for high daily variance
        daily = summary.get("daily_breakdown", {})
        if daily:
            costs = list(daily.values())
            avg = sum(costs) / len(costs)
            variance = max(costs) - min(costs)
            if variance > avg * 2:
                recommendations.append(
                    {
                        "type": "usage_pattern",
                        "priority": "medium",
                        "message": "High variance in daily spending detected. Consider implementing rate limiting or caching.",
                        "potential_savings": "20-40%",
                    }
                )

        # Check budget utilization
        for budget in self.budgets.values():
            if budget.utilization_percent() > 90:
                recommendations.append(
                    {
                        "type": "budget_alert",
                        "priority": "critical",
                        "message": f"Budget '{budget.name}' at {budget.utilization_percent():.1f}%. Consider increasing budget or reducing usage.",
                        "budget_id": budget.budget_id,
                    }
                )

        # General recommendations
        if summary["total_tokens"] > 1000000:  # 1M tokens
            recommendations.append(
                {
                    "type": "caching",
                    "priority": "medium",
                    "message": "High token volume detected. Implement response caching for repeated queries.",
                    "potential_savings": "30-50%",
                }
            )

        return recommendations

    def get_alerts(
        self, level: str = None, acknowledged: bool = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get cost alerts with filtering."""
        alerts = self.alerts

        if level:
            alerts = [a for a in alerts if a.alert_level == level]

        if acknowledged is not None:
            alerts = [a for a in alerts if a.acknowledged == acknowledged]

        alerts = alerts[-limit:]

        return [
            {
                "alert_id": a.alert_id,
                "budget_id": a.budget_id,
                "alert_level": a.alert_level,
                "message": a.message,
                "utilization_percent": a.utilization_percent,
                "timestamp": a.timestamp,
                "acknowledged": a.acknowledged,
            }
            for a in alerts
        ]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False

    def reset_budget(self, budget_id: str) -> bool:
        """Reset a budget's spent amount."""
        budget = self.budgets.get(budget_id)
        if budget:
            budget.spent_usd = 0.0
            return True
        return False


# Global cost manager
cost_manager = AICostManager()


# Convenience functions
async def track_llm_cost(
    model: str, input_tokens: int, output_tokens: int, agent_id: str = ""
) -> TokenUsage:
    """Track LLM usage cost."""
    return await cost_manager.track_usage(model, input_tokens, output_tokens, agent_id)


def create_budget(name: str, amount_usd: float, period: str = "monthly") -> Budget:
    """Create a budget."""
    return cost_manager.create_budget(name, amount_usd, period)


def get_cost_report(days: int = 30) -> dict[str, Any]:
    """Get cost report."""
    return cost_manager.get_cost_summary(days)


def get_optimization_tips() -> list[dict[str, Any]]:
    """Get optimization recommendations."""
    return cost_manager.get_optimization_recommendations()
