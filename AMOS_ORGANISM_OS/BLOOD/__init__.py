"""BLOOD module — Alias for 04_BLOOD"""

import sys
from pathlib import Path

blood_path = Path(__file__).parent.parent / "04_BLOOD"
if str(blood_path) not in sys.path:
    sys.path.insert(0, str(blood_path))

from budget_manager import Budget, BudgetCategory, BudgetManager
from cashflow_tracker import CashflowRecord, CashflowTracker, CashflowType
from forecast_engine import Forecast, ForecastEngine, ForecastModel
from resource_engine import ResourceAllocation, ResourceEngine, ResourcePool

__all__ = [
    "ResourceEngine",
    "ResourcePool",
    "ResourceAllocation",
    "BudgetManager",
    "Budget",
    "BudgetCategory",
    "CashflowTracker",
    "CashflowRecord",
    "CashflowType",
    "ForecastEngine",
    "Forecast",
    "ForecastModel",
]
