"""METABOLISM module — Alias for 07_METABOLISM

NOTE: This uses sys.path to access 07_METABOLISM modules.
This is a transitional pattern until package structure is fully refactored.
"""

import sys
from pathlib import Path

# Add 07_METABOLISM to path for module access (transitional pattern)
_07_METABOLISM_PATH = Path(__file__).parent.parent / "07_METABOLISM"
if str(_07_METABOLISM_PATH) not in sys.path:
    sys.path.insert(0, str(_07_METABOLISM_PATH))

from cleanup_engine import CleanupEngine, CleanupPolicy, CleanupTask, get_cleanup_engine
from io_router import IORouter, Route, RouteConfig, get_io_router
from transform_engine import Transform, TransformContext, TransformEngine, get_transform_engine
from pipeline_engine import Pipeline, PipelineEngine, PipelineStage, get_pipeline_engine

__all__ = [
    "PipelineEngine",
    "Pipeline",
    "PipelineStage",
    "get_pipeline_engine",
    "TransformEngine",
    "Transform",
    "TransformContext",
    "get_transform_engine",
    "IORouter",
    "Route",
    "RouteConfig",
    "get_io_router",
    "CleanupEngine",
    "CleanupTask",
    "CleanupPolicy",
    "get_cleanup_engine",
]
