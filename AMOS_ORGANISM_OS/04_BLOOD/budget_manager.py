"""
Budget Manager — Financial planning and category tracking

Handles budgeting across categories, expense tracking, and
budget variance analysis.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class BudgetCategory(Enum):
    """Budget categories for the organism."""
    INFRASTRUCTURE = "infrastructure"  # Servers, compute
    TOKENS = "tokens"  # AI API costs
    DEVELOPMENT = "development"  # Dev tools, licenses
    RESEARCH = "research"  # Research resources
    OPERATIONS = "operations"  # Day-to-day operations
    EMERGENCY = "emergency"  # Reserve fund
    GROWTH = "growth"  # Expansion investments


@dataclass
class Budget:
    """A budget for a specific category."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    category: BudgetCategory = BudgetCategory.OPERATIONS
    name: str = ""
    period: str = "monthly"  # daily, weekly, monthly, yearly
    allocated: float = 0.0
    spent: float = 0.0
    currency: str = "USD"
    start_date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    end_date: Optional[str] = None
    alerts_enabled: bool = True
    alert_threshold: float = 0.8  # Alert at 80% usage
    archived: bool = False
    notes: str = ""

    @property
    def remaining(self) -> float:
        """Calculate remaining budget."""
        return self.allocated - self.spent

    @property
    def utilization(self) -> float:
        """Calculate utilization rate."""
        if self.allocated == 0:
            return 0.0
        return self.spent / self.allocated

    @property
    def alert_triggered(self) -> bool:
        """Check if budget alert should trigger."""
        return self.alerts_enabled and self.utilization >= self.alert_threshold

    def spend(self, amount: float, description: str = "") -> bool:
        """Record spending against this budget."""
        if self.spent + amount > self.allocated:
            return False
        self.spent += amount
        return True

    def adjust(self, new_amount: float):
        """Adjust budget allocation."""
        self.allocated = new_amount

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "category": self.category.value,
            "remaining": self.remaining,
            "utilization": self.utilization,
            "alert_triggered": self.alert_triggered,
        }


@dataclass
class Expense:
    """A single expense record."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    amount: float = 0.0
    currency: str = "USD"
    category: BudgetCategory = BudgetCategory.OPERATIONS
    budget_id: str = ""
    description: str = ""
    vendor: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tags: List[str] = field(default_factory=list)
    approved: bool = False
    approved_by: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "category": self.category.value,
        }


class BudgetManager:
    """
    Manages budgets across categories for the AMOS organism.

    Tracks allocations, expenses, and provides variance analysis.
    Integrates with the resource engine for unified resource management.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.budgets: Dict[str, Budget] = {}
        self.expenses: List[Expense] = []

        self._load_data()

        # Create default budgets if none exist
        if not self.budgets:
            self._init_default_budgets()

    def _init_default_budgets(self):
        """Create default monthly budgets."""
        defaults = [
            Budget(
                category=BudgetCategory.TOKENS,
                name="Monthly Token Budget",
                period="monthly",
                allocated=100.0,
                currency="USD",
            ),
            Budget(
                category=BudgetCategory.INFRASTRUCTURE,
                name="Infrastructure Costs",
                period="monthly",
                allocated=50.0,
                currency="USD",
            ),
            Budget(
                category=BudgetCategory.DEVELOPMENT,
                name="Development Tools",
                period="monthly",
                allocated=30.0,
                currency="USD",
            ),
            Budget(
                category=BudgetCategory.EMERGENCY,
                name="Emergency Reserve",
                period="monthly",
                allocated=200.0,
                currency="USD",
                alert_threshold=0.5,  # Alert at 50% (lower threshold for reserve)
            ),
        ]

        for budget in defaults:
            self.budgets[budget.id] = budget

        self.save()

    def _load_data(self):
        """Load budgets and expenses from disk."""
        budgets_file = self.data_dir / "budgets.json"
        if budgets_file.exists():
            try:
                data = json.loads(budgets_file.read_text())
                for budget_data in data.get("budgets", []):
                    budget = Budget(
                        id=budget_data["id"],
                        category=BudgetCategory(budget_data["category"]),
                        name=budget_data["name"],
                        period=budget_data["period"],
                        allocated=budget_data["allocated"],
                        spent=budget_data["spent"],
                        currency=budget_data["currency"],
                        start_date=budget_data["start_date"],
                        end_date=budget_data.get("end_date"),
                        alerts_enabled=budget_data["alerts_enabled"],
                        alert_threshold=budget_data["alert_threshold"],
                        archived=budget_data["archived"],
                        notes=budget_data["notes"],
                    )
                    self.budgets[budget.id] = budget

                for exp_data in data.get("expenses", []):
                    expense = Expense(
                        id=exp_data["id"],
                        amount=exp_data["amount"],
                        currency=exp_data["currency"],
                        category=BudgetCategory(exp_data["category"]),
                        budget_id=exp_data["budget_id"],
                        description=exp_data["description"],
                        vendor=exp_data["vendor"],
                        timestamp=exp_data["timestamp"],
                        tags=exp_data.get("tags", []),
                        approved=exp_data["approved"],
                        approved_by=exp_data["approved_by"],
                    )
                    self.expenses.append(expense)
            except Exception as e:
                print(f"[BUDGET] Error loading data: {e}")

    def save(self):
        """Save budgets and expenses to disk."""
        budgets_file = self.data_dir / "budgets.json"
        data = {
            "saved_at": datetime.utcnow().isoformat(),
            "budgets": [b.to_dict() for b in self.budgets.values()],
            "expenses": [e.to_dict() for e in self.expenses],
        }
        budgets_file.write_text(json.dumps(data, indent=2))

    def create_budget(
        self,
        category: BudgetCategory,
        name: str,
        amount: float,
        period: str = "monthly",
        currency: str = "USD",
    ) -> Budget:
        """Create a new budget."""
        budget = Budget(
            category=category,
            name=name,
            period=period,
            allocated=amount,
            currency=currency,
        )
        self.budgets[budget.id] = budget
        self.save()
        return budget

    def record_expense(
        self,
        amount: float,
        category: BudgetCategory,
        description: str,
        budget_id: Optional[str] = None,
        vendor: str = "",
        tags: Optional[List[str]] = None,
    ) -> Optional[Expense]:
        """Record an expense against a budget."""
        # Find matching budget if not specified
        if budget_id is None:
            for bid, budget in self.budgets.items():
                if budget.category == category and not budget.archived:
                    budget_id = bid
                    break

        if budget_id is None or budget_id not in self.budgets:
            return None

        budget = self.budgets[budget_id]

        # Check if expense can be recorded
        if not budget.spend(amount, description):
            return None

        expense = Expense(
            amount=amount,
            currency=budget.currency,
            category=category,
            budget_id=budget_id,
            description=description,
            vendor=vendor,
            tags=tags or [],
        )

        self.expenses.append(expense)
        self.save()

        return expense

    def get_budget_status(self, budget_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status for a budget."""
        budget = self.budgets.get(budget_id)
        if not budget:
            return None

        # Get related expenses
        related_expenses = [
            e.to_dict() for e in self.expenses if e.budget_id == budget_id
        ]

        return {
            "budget": budget.to_dict(),
            "expenses": related_expenses,
            "expense_count": len(related_expenses),
        }

    def get_overview(self) -> Dict[str, Any]:
        """Get overview of all budgets."""
        total_allocated = sum(b.allocated for b in self.budgets.values())
        total_spent = sum(b.spent for b in self.budgets.values())

        by_category = {}
        for budget in self.budgets.values():
            cat = budget.category.value
            if cat not in by_category:
                by_category[cat] = {"allocated": 0, "spent": 0, "count": 0}
            by_category[cat]["allocated"] += budget.allocated
            by_category[cat]["spent"] += budget.spent
            by_category[cat]["count"] += 1

        alerts = [
            {"budget_id": bid, "name": b.name, "utilization": b.utilization}
            for bid, b in self.budgets.items()
            if b.alert_triggered
        ]

        return {
            "total_allocated": total_allocated,
            "total_spent": total_spent,
            "total_remaining": total_allocated - total_spent,
            "overall_utilization": total_spent / total_allocated if total_allocated > 0 else 0,
            "budget_count": len(self.budgets),
            "expense_count": len(self.expenses),
            "by_category": by_category,
            "alerts": alerts,
        }

    def get_category_report(self, category: BudgetCategory) -> Dict[str, Any]:
        """Get report for a specific category."""
        category_budgets = [b for b in self.budgets.values() if b.category == category]
        category_expenses = [e for e in self.expenses if e.category == category]

        total_allocated = sum(b.allocated for b in category_budgets)
        total_spent = sum(b.spent for b in category_budgets)

        return {
            "category": category.value,
            "budget_count": len(category_budgets),
            "expense_count": len(category_expenses),
            "total_allocated": total_allocated,
            "total_spent": total_spent,
            "remaining": total_allocated - total_spent,
            "budgets": [b.to_dict() for b in category_budgets],
        }


# Global instance
_MANAGER: Optional[BudgetManager] = None


def get_budget_manager(data_dir: Optional[Path] = None) -> BudgetManager:
    """Get or create global budget manager."""
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = BudgetManager(data_dir)
    return _MANAGER


if __name__ == "__main__":
    print("Budget Manager (04_BLOOD)")
    print("=" * 40)

    manager = get_budget_manager()

    print("\nBudget Overview:")
    overview = manager.get_overview()
    print(f"  Total Allocated: ${overview['total_allocated']:.2f}")
    print(f"  Total Spent: ${overview['total_spent']:.2f}")
    print(f"  Utilization: {overview['overall_utilization']:.1%}")

    print("\nBudgets by Category:")
    for cat, data in overview["by_category"].items():
        print(f"  {cat}: ${data['spent']:.2f} / ${data['allocated']:.2f}")

    # Test expense recording
    print("\nTest expense:")
    exp = manager.record_expense(
        amount=25.0,
        category=BudgetCategory.TOKENS,
        description="API usage test",
    )
    if exp:
        print(f"  Recorded: ${exp.amount} for {exp.description}")
