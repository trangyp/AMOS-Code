"""BLOOD budget_manager stub — Re-exports from 04_BLOOD"""
import sys
from pathlib import Path

blood_path = Path(__file__).parent.parent / "04_BLOOD"
if str(blood_path) not in sys.path:
    sys.path.insert(0, str(blood_path))

from budget_manager import Budget, BudgetCategory, BudgetManager

__all__ = ["BudgetManager", "Budget", "BudgetCategory"]
