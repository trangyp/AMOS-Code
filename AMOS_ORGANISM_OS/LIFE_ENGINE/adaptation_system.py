"""LIFE_ENGINE adaptation_system stub — Re-exports from 11_LIFE_ENGINE"""

import sys
from pathlib import Path

life_path = Path(__file__).parent.parent / "11_LIFE_ENGINE"
if str(life_path) not in sys.path:
    sys.path.insert(0, str(life_path))

from adaptation_system import AdaptationStrategy, AdaptationSystem, EnvironmentFeedback

__all__ = ["AdaptationSystem", "AdaptationStrategy", "EnvironmentFeedback"]
