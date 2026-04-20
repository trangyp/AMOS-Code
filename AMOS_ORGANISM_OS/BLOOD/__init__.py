"""BLOOD module — Alias for 04_BLOOD"""

import importlib.util
from pathlib import Path

# Load modules from 04_BLOOD using importlib
_04_BLOOD_PATH = Path(__file__).parent.parent / "04_BLOOD"

# budget_manager
_spec_bm = importlib.util.spec_from_file_location(
    "_budget_mgr", _04_BLOOD_PATH / "budget_manager.py"
)
_mod_bm = importlib.util.module_from_spec(_spec_bm)
_spec_bm.loader.exec_module(_mod_bm)
BudgetManager = _mod_bm.BudgetManager
Budget = _mod_bm.Budget
BudgetCategory = _mod_bm.BudgetCategory

# cashflow_tracker
_spec_ct = importlib.util.spec_from_file_location(
    "_cashflow", _04_BLOOD_PATH / "cashflow_tracker.py"
)
_mod_ct = importlib.util.module_from_spec(_spec_ct)
_spec_ct.loader.exec_module(_mod_ct)
CashflowTracker = _mod_ct.CashflowTracker
CashflowRecord = _mod_ct.CashflowRecord
CashflowType = _mod_ct.CashflowType

# forecast_engine
_spec_fe = importlib.util.spec_from_file_location(
    "_forecast", _04_BLOOD_PATH / "forecast_engine.py"
)
_mod_fe = importlib.util.module_from_spec(_spec_fe)
_spec_fe.loader.exec_module(_mod_fe)
ForecastEngine = _mod_fe.ForecastEngine
Forecast = _mod_fe.Forecast
ForecastModel = _mod_fe.ForecastModel

# resource_engine
_spec_re = importlib.util.spec_from_file_location(
    "_resource", _04_BLOOD_PATH / "resource_engine.py"
)
_mod_re = importlib.util.module_from_spec(_spec_re)
_spec_re.loader.exec_module(_mod_re)
ResourceEngine = _mod_re.ResourceEngine
ResourcePool = _mod_re.ResourcePool
ResourceAllocation = _mod_re.ResourceAllocation

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
