"""04_BLOOD — Resource/Money Engine
=================================

The financial circulatory system of AMOS.
Handles budgeting, cashflow, resource allocation, and forecasting.

Role: Money/blood engine - budgeting, cashflow, investing, forecasting
Kernel refs: FINANCE_KERNEL, RESOURCE_KERNEL

Owner: Trang
Version: 1.0.0
"""

from .budget_manager import Budget, BudgetCategory, BudgetManager
from .cashflow_tracker import CashflowRecord, CashflowTracker, CashflowType
from .forecast_engine import Forecast, ForecastEngine, ForecastModel
from .resource_engine import ResourceAllocation, ResourceEngine, ResourcePool

__all__ = [
    # Resource engine
    "ResourceEngine",
    "ResourcePool",
    "ResourceAllocation",
    # Budget management
    "BudgetManager",
    "Budget",
    "BudgetCategory",
    # Cashflow tracking
    "CashflowTracker",
    "CashflowRecord",
    "CashflowType",
    # Forecasting
    "ForecastEngine",
    "Forecast",
    "ForecastModel",
]
