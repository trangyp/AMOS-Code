"""
Cashflow Tracker — Income and expense monitoring

Tracks cash movements, balances, and flow analysis over time.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class CashflowType(Enum):
    """Type of cashflow entry."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    RESERVE = "reserve"


class CashflowStatus(Enum):
    """Status of a cashflow entry."""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RECURRING = "recurring"


@dataclass
class CashflowRecord:
    """A single cashflow entry."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    cashflow_type: CashflowType = CashflowType.EXPENSE
    amount: float = 0.0
    currency: str = "USD"
    description: str = ""
    category: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: CashflowStatus = CashflowStatus.COMPLETED
    source: str = ""  # Where it came from
    destination: str = ""  # Where it went
    tags: List[str] = field(default_factory=list)
    recurring: bool = False
    recurrence_period: Optional[str] = None  # daily, weekly, monthly
    related_record_id: Optional[str] = None  # For transfers
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "cashflow_type": self.cashflow_type.value,
            "status": self.status.value,
        }


@dataclass
class BalanceSnapshot:
    """Balance at a specific point in time."""
    timestamp: str
    balance: float
    currency: str
    pending_in: float
    pending_out: float


class CashflowTracker:
    """
    Tracks cash movements and provides flow analysis.

    Monitors income, expenses, transfers, and provides
    trend analysis and forecasting input.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.records: List[CashflowRecord] = []
        self.initial_balance: float = 0.0
        self.currency: str = "USD"

        self._load_data()

    def _load_data(self):
        """Load cashflow records from disk."""
        cashflow_file = self.data_dir / "cashflow.json"
        if cashflow_file.exists():
            try:
                data = json.loads(cashflow_file.read_text())
                self.initial_balance = data.get("initial_balance", 0.0)
                self.currency = data.get("currency", "USD")

                for record_data in data.get("records", []):
                    record = CashflowRecord(
                        id=record_data["id"],
                        cashflow_type=CashflowType(record_data["cashflow_type"]),
                        amount=record_data["amount"],
                        currency=record_data["currency"],
                        description=record_data["description"],
                        category=record_data["category"],
                        timestamp=record_data["timestamp"],
                        status=CashflowStatus(record_data["status"]),
                        source=record_data.get("source", ""),
                        destination=record_data.get("destination", ""),
                        tags=record_data.get("tags", []),
                        recurring=record_data.get("recurring", False),
                        recurrence_period=record_data.get("recurrence_period"),
                        related_record_id=record_data.get("related_record_id"),
                        metadata=record_data.get("metadata", {}),
                    )
                    self.records.append(record)
            except Exception as e:
                print(f"[CASHFLOW] Error loading data: {e}")

    def save(self):
        """Save cashflow records to disk."""
        cashflow_file = self.data_dir / "cashflow.json"
        data = {
            "saved_at": datetime.utcnow().isoformat(),
            "initial_balance": self.initial_balance,
            "currency": self.currency,
            "records": [r.to_dict() for r in self.records],
        }
        cashflow_file.write_text(json.dumps(data, indent=2))

    def record(
        self,
        cashflow_type: CashflowType,
        amount: float,
        description: str,
        category: str = "",
        source: str = "",
        destination: str = "",
        tags: Optional[List[str]] = None,
    ) -> CashflowRecord:
        """Record a cashflow entry."""
        record = CashflowRecord(
            cashflow_type=cashflow_type,
            amount=amount,
            currency=self.currency,
            description=description,
            category=category,
            source=source,
            destination=destination,
            tags=tags or [],
        )

        self.records.append(record)
        self.save()
        return record

    def income(
        self,
        amount: float,
        description: str,
        source: str = "",
        category: str = "income",
    ) -> CashflowRecord:
        """Record income."""
        return self.record(CashflowType.INCOME, amount, description, category, source)

    def expense(
        self,
        amount: float,
        description: str,
        destination: str = "",
        category: str = "expense",
    ) -> CashflowRecord:
        """Record expense."""
        return self.record(CashflowType.EXPENSE, amount, description, category, destination=destination)

    def get_balance(self, include_pending: bool = False) -> Dict[str, float]:
        """Calculate current balance."""
        completed = [r for r in self.records if r.status == CashflowStatus.COMPLETED]

        total_income = sum(r.amount for r in completed if r.cashflow_type == CashflowType.INCOME)
        total_expense = sum(r.amount for r in completed if r.cashflow_type == CashflowType.EXPENSE)

        balance = self.initial_balance + total_income - total_expense

        result = {
            "available": balance,
            "initial": self.initial_balance,
            "total_income": total_income,
            "total_expense": total_expense,
        }

        if include_pending:
            pending = [r for r in self.records if r.status == CashflowStatus.PENDING]
            pending_in = sum(r.amount for r in pending if r.cashflow_type == CashflowType.INCOME)
            pending_out = sum(r.amount for r in pending if r.cashflow_type == CashflowType.EXPENSE)
            result["pending_in"] = pending_in
            result["pending_out"] = pending_out
            result["projected"] = balance + pending_in - pending_out

        return result

    def get_flow_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get cashflow summary for a period."""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        recent = [r for r in self.records if r.timestamp > cutoff and r.status == CashflowStatus.COMPLETED]

        income_recs = [r for r in recent if r.cashflow_type == CashflowType.INCOME]
        expense_recs = [r for r in recent if r.cashflow_type == CashflowType.EXPENSE]

        total_in = sum(r.amount for r in income_recs)
        total_out = sum(r.amount for r in expense_recs)

        by_category = {}
        for r in recent:
            cat = r.category or "uncategorized"
            if cat not in by_category:
                by_category[cat] = {"in": 0, "out": 0}
            if r.cashflow_type == CashflowType.INCOME:
                by_category[cat]["in"] += r.amount
            else:
                by_category[cat]["out"] += r.amount

        return {
            "period_days": days,
            "total_income": total_in,
            "total_expense": total_out,
            "net_flow": total_in - total_out,
            "transaction_count": len(recent),
            "avg_daily_in": total_in / days if days > 0 else 0,
            "avg_daily_out": total_out / days if days > 0 else 0,
            "by_category": by_category,
        }

    def get_trend(self, periods: int = 6, period_days: int = 30) -> List[Dict[str, Any]]:
        """Get cashflow trend over multiple periods."""
        trends = []
        now = datetime.utcnow()

        for i in range(periods):
            end = now - timedelta(days=i * period_days)
            start = end - timedelta(days=period_days)

            period_records = [
                r for r in self.records
                if start.isoformat() <= r.timestamp < end.isoformat()
                and r.status == CashflowStatus.COMPLETED
            ]

            income = sum(r.amount for r in period_records if r.cashflow_type == CashflowType.INCOME)
            expense = sum(r.amount for r in period_records if r.cashflow_type == CashflowType.EXPENSE)

            trends.append({
                "period": i,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "income": income,
                "expense": expense,
                "net": income - expense,
            })

        return list(reversed(trends))

    def get_status(self) -> Dict[str, Any]:
        """Get overall cashflow status."""
        balance = self.get_balance(include_pending=True)
        summary_30 = self.get_flow_summary(30)

        return {
            "currency": self.currency,
            "balance": balance,
            "last_30_days": summary_30,
            "total_records": len(self.records),
            "active_categories": list(set(r.category for r in self.records if r.category)),
        }


# Global instance
_TRACKER: Optional[CashflowTracker] = None


def get_cashflow_tracker(data_dir: Optional[Path] = None) -> CashflowTracker:
    """Get or create global cashflow tracker."""
    global _TRACKER
    if _TRACKER is None:
        _TRACKER = CashflowTracker(data_dir)
    return _TRACKER


if __name__ == "__main__":
    print("Cashflow Tracker (04_BLOOD)")
    print("=" * 40)

    tracker = get_cashflow_tracker()

    print("\nRecording sample transactions...")
    tracker.income(1000.0, "Initial funding", "operator", "setup")
    tracker.expense(50.0, "API tokens", "openai", "tokens")
    tracker.expense(25.0, "Server costs", "hosting", "infrastructure")

    print("\nBalance:")
    balance = tracker.get_balance(include_pending=True)
    print(f"  Available: ${balance['available']:.2f}")
    print(f"  Total Income: ${balance['total_income']:.2f}")
    print(f"  Total Expense: ${balance['total_expense']:.2f}")

    print("\n30-day Summary:")
    summary = tracker.get_flow_summary(30)
    print(f"  Net Flow: ${summary['net_flow']:.2f}")
    print(f"  Transactions: {summary['transaction_count']}")
