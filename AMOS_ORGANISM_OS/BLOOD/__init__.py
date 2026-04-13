"""BLOOD module — Alias for 04_BLOOD"""

import sys
from pathlib import Path

blood_path = Path(__file__).parent.parent / "04_BLOOD"
if str(blood_path) not in sys.path:
    sys.path.insert(0, str(blood_path))

from resource_engine import ResourceEngine, ResourcePool, ResourceAllocation
from budget_manager import BudgetManager, Budget, BudgetCategory
from cashflow_tracker import CashflowTracker, CashflowRecord, CashflowType
from forecast_engine import ForecastEngine, Forecast, ForecastModel

__all__ = [
    "ResourceEngine", "ResourcePool", "ResourceAllocation",
    "BudgetManager", "Budget", "BudgetCategory",
    "CashflowTracker", "CashflowRecord", "CashflowType",
    "ForecastEngine", "Forecast", "ForecastModel",
]
