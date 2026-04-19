#!/usr/bin/env python3
"""AMOS Financial Engine (04_BLOOD)
================================

Economic circulatory system for the AMOS Organism.
Handles budgeting, cashflow, resource allocation, and cost tracking.

Owner: Trang
Version: 1.0.0
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class BudgetLine:
    """Single budget allocation."""

    category: str
    allocated: float
    spent: float = 0.0
    currency: str = "USD"
    period: str = "monthly"  # daily, weekly, monthly, yearly


@dataclass
class CashflowEntry:
    """Single cashflow transaction."""

    id: str
    timestamp: str
    direction: str  # inflow, outflow
    amount: float
    category: str
    description: str
    source: str  # subsystem or external


@dataclass
class ResourceAllocation:
    """Resource allocation for a task."""

    task_id: str
    cpu_units: float
    memory_mb: float
    cost_estimate: float
    priority: int
    allocated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class FinancialEngine:
    """Blood subsystem - manages economic circulation.
    Tracks budgets, cashflow, and resource allocation.
    """

    def __init__(self, organism_root: Path) -> None:
        self.root = organism_root
        self.blood_dir = organism_root / "04_BLOOD"
        self.data_dir = self.blood_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.budgets: Dict[str, BudgetLine] = {}
        self.cashflow: List[CashflowEntry] = []
        self.allocations: Dict[str, ResourceAllocation] = {}

        self._load_state()

    def _load_state(self) -> None:
        """Load financial state from disk."""
        state_file = self.data_dir / "financial_state.json"
        if state_file.exists():
            try:
                with open(state_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Load budgets
                for cat, budget_data in data.get("budgets", {}).items():
                    self.budgets[cat] = BudgetLine(**budget_data)

                # Load cashflow
                for entry in data.get("cashflow", []):
                    self.cashflow.append(CashflowEntry(**entry))

            except Exception as e:
                print(f"[BLOOD] Error loading state: {e}")

    def _save_state(self) -> None:
        """Save financial state to disk."""
        state_file = self.data_dir / "financial_state.json"

        data = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "budgets": {
                cat: {
                    "category": b.category,
                    "allocated": b.allocated,
                    "spent": b.spent,
                    "currency": b.currency,
                    "period": b.period,
                }
                for cat, b in self.budgets.items()
            },
            "cashflow": [
                {
                    "id": c.id,
                    "timestamp": c.timestamp,
                    "direction": c.direction,
                    "amount": c.amount,
                    "category": c.category,
                    "description": c.description,
                    "source": c.source,
                }
                for c in self.cashflow[-1000:]  # Keep last 1000
            ],
            "total_allocations": len(self.allocations),
        }

        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def set_budget(self, category: str, amount: float, period: str = "monthly") -> BudgetLine:
        """Set budget for a category."""
        self.budgets[category] = BudgetLine(category=category, allocated=amount, period=period)
        self._save_state()
        return self.budgets[category]

    def record_transaction(
        self, direction: str, amount: float, category: str, description: str, source: str = "system"
    ) -> CashflowEntry:
        """Record a cashflow transaction."""
        import uuid

        entry = CashflowEntry(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(UTC).isoformat() + "Z",
            direction=direction,
            amount=amount,
            category=category,
            description=description,
            source=source,
        )

        self.cashflow.append(entry)

        # Update budget if applicable
        if category in self.budgets and direction == "outflow":
            self.budgets[category].spent += amount

        self._save_state()
        return entry

    def allocate_resources(
        self, task_id: str, cpu_units: float = 1.0, memory_mb: float = 512.0, priority: int = 5
    ) -> ResourceAllocation:
        """Allocate resources for a task with cost estimation."""
        # Cost estimation: $0.001 per CPU unit per hour, $0.0001 per MB
        cost_estimate = (cpu_units * 0.001) + (memory_mb * 0.0001)

        allocation = ResourceAllocation(
            task_id=task_id,
            cpu_units=cpu_units,
            memory_mb=memory_mb,
            cost_estimate=cost_estimate,
            priority=priority,
        )

        self.allocations[task_id] = allocation
        return allocation

    def release_resources(self, task_id: str) -> float:
        """Release resources and return actual cost."""
        if task_id not in self.allocations:
            return None

        allocation = self.allocations.pop(task_id)

        # Record actual cost (estimate for now)
        actual_cost = allocation.cost_estimate

        self.record_transaction(
            direction="outflow",
            amount=actual_cost,
            category="compute",
            description=f"Task {task_id} resource usage",
            source="04_BLOOD",
        )

        return actual_cost

    def get_budget_status(self, category: str) -> Dict[str, Any]:
        """Get budget status for a category."""
        if category not in self.budgets:
            return None

        budget = self.budgets[category]
        remaining = budget.allocated - budget.spent
        if budget.allocated > 0:
            utilization = budget.spent / budget.allocated
        else:
            utilization = 0

        return {
            "category": category,
            "allocated": budget.allocated,
            "spent": budget.spent,
            "remaining": remaining,
            "utilization_rate": utilization,
            "status": (
                "healthy" if utilization < 0.8 else "warning" if utilization < 1.0 else "exhausted"
            ),
        }

    def get_cashflow_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get cashflow summary for period."""
        cutoff = datetime.now(UTC) - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        recent = [c for c in self.cashflow if c.timestamp > cutoff_str]

        inflows = sum(c.amount for c in recent if c.direction == "inflow")
        outflows = sum(c.amount for c in recent if c.direction == "outflow")

        return {
            "period_days": days,
            "transaction_count": len(recent),
            "total_inflow": inflows,
            "total_outflow": outflows,
            "net_flow": inflows - outflows,
            "categories": list(set(c.category for c in recent)),
        }

    def estimate_task_cost(
        self, complexity: str = "medium", duration_minutes: float = 5.0
    ) -> Dict[str, float]:
        """Estimate cost for a task."""
        # Complexity multipliers
        multipliers = {"low": 0.5, "medium": 1.0, "high": 2.0, "very_high": 4.0}

        multiplier = multipliers.get(complexity, 1.0)
        base_rate = 0.01  # $0.01 per minute base

        estimated_cost = base_rate * duration_minutes * multiplier

        return {
            "estimated_cost": estimated_cost,
            "base_rate": base_rate,
            "multiplier": multiplier,
            "duration_minutes": duration_minutes,
        }

    def get_status(self) -> Dict[str, Any]:
        """Get overall financial status."""
        budget_statuses = {cat: self.get_budget_status(cat) for cat in self.budgets.keys()}

        cashflow = self.get_cashflow_summary(days=30)

        return {
            "status": "operational",
            "budget_categories": len(self.budgets),
            "budget_status": budget_statuses,
            "cashflow_30d": cashflow,
            "active_allocations": len(self.allocations),
            "total_transactions": len(self.cashflow),
        }


def main() -> int:
    """CLI for Financial Engine."""
    print("=" * 50)
    print("AMOS Financial Engine (04_BLOOD)")
    print("=" * 50)

    organism_root = Path(__file__).parent.parent
    engine = FinancialEngine(organism_root)

    # Initialize default budgets
    engine.set_budget("compute", 100.0, "monthly")
    engine.set_budget("storage", 50.0, "monthly")
    engine.set_budget("api_calls", 25.0, "monthly")

    print("\nInitialized budgets:")
    for cat in ["compute", "storage", "api_calls"]:
        status = engine.get_budget_status(cat)
        print(f"  {cat}: ${status['allocated']:.2f} allocated")

    # Test allocation
    print("\nAllocating resources for task...")
    alloc = engine.allocate_resources("test_task_001", cpu_units=2.0, memory_mb=1024)
    print(f"  Task ID: {alloc.task_id}")
    print(f"  Estimated cost: ${alloc.cost_estimate:.4f}")

    # Show status
    print("\nFinancial Status:")
    status = engine.get_status()
    print(f"  Budget categories: {status['budget_categories']}")
    print(f"  Active allocations: {status['active_allocations']}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
