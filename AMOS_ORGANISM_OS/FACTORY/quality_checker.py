"""FACTORY quality_checker stub — Re-exports from 13_FACTORY"""

import sys
from pathlib import Path

factory_path = Path(__file__).parent.parent / "13_FACTORY"
if str(factory_path) not in sys.path:
    sys.path.insert(0, str(factory_path))

from quality_checker import QualityChecker, QualityReport

__all__ = ["QualityChecker", "QualityReport"]
