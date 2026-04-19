"""BLOOD module — Alias for 04_BLOOD

NOTE: This uses sys.path to access 04_BLOOD modules.
This is a transitional pattern until package structure is fully refactored.
"""

import sys
from pathlib import Path

# Add 04_BLOOD to path for module access (transitional pattern)
_04_BLOOD_PATH = Path(__file__).parent.parent / "04_BLOOD"
if str(_04_BLOOD_PATH) not in sys.path:
    sys.path.insert(0, str(_04_BLOOD_PATH))

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
