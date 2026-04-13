"""BLOOD resource_engine stub — Re-exports from 04_BLOOD"""
import sys
from pathlib import Path

blood_path = Path(__file__).parent.parent / "04_BLOOD"
if str(blood_path) not in sys.path:
    sys.path.insert(0, str(blood_path))

from resource_engine import ResourceEngine, ResourcePool, ResourceAllocation

__all__ = ["ResourceEngine", "ResourcePool", "ResourceAllocation"]
