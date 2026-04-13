"""
04_BLOOD — Resource/Money Engine
=================================

The financial circulatory system of AMOS.
Handles budgeting, cashflow, resource allocation, and forecasting.

Role: Money/blood engine - budgeting, cashflow, investing, forecasting
Kernel refs: FINANCE_KERNEL, RESOURCE_KERNEL

Owner: Trang
Version: 1.0.0
"""

from .resource_engine import ResourceEngine, ResourcePool, ResourceAllocation
from .budget_manager import BudgetManager, Budget, BudgetCategory
from .cashflow_tracker import CashflowTracker, CashflowRecord, CashflowType
from .forecast_engine import ForecastEngine, Forecast, ForecastModel

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
