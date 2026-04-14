"""METABOLISM module — Alias for 07_METABOLISM"""

import sys
from pathlib import Path

metabolism_path = Path(__file__).parent.parent / "07_METABOLISM"
if str(metabolism_path) not in sys.path:
    sys.path.insert(0, str(metabolism_path))

from cleanup_engine import CleanupEngine, CleanupPolicy, CleanupTask, get_cleanup_engine
from io_router import IORouter, Route, RouteConfig, get_io_router
from pipeline_engine import Pipeline, PipelineEngine, PipelineStage, get_pipeline_engine
from transform_engine import Transform, TransformContext, TransformEngine, get_transform_engine

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
