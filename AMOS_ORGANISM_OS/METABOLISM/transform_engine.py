# Stub to re-export from 07_METABOLISM
import sys
from pathlib import Path

metabolism_path = Path(__file__).parent.parent / "07_METABOLISM"
if str(metabolism_path) not in sys.path:
    sys.path.insert(0, str(metabolism_path))

from transform_engine import (
    TransformEngine,
    Transform,
    TransformContext,
    get_transform_engine,
)

__all__ = [
    "TransformEngine",
    "Transform",
    "TransformContext",
    "get_transform_engine",
]
