"""
07_METABOLISM — Pipeline and Transform Engine
==============================================

The metabolic system of AMOS. Handles data pipelines, transforms,
IO routing, and cleanup operations.

Role: Pipelines, transforms, IO routing and cleanup
Kernel refs: PIPELINE_KERNEL, TRANSFORM_KERNEL, AMOS_Metabolism_Engine

Owner: Trang
Version: 1.0.0
"""

from .pipeline_engine import PipelineEngine, Pipeline, PipelineStage
from .transform_engine import TransformEngine, Transform, TransformContext
from .io_router import IORouter, Route, RouteConfig
from .cleanup_engine import CleanupEngine, CleanupTask, CleanupPolicy

__all__ = [
    # Pipeline engine
    "PipelineEngine",
    "Pipeline",
    "PipelineStage",
    # Transform engine
    "TransformEngine",
    "Transform",
    "TransformContext",
    # IO Router
    "IORouter",
    "Route",
    "RouteConfig",
    # Cleanup engine
    "CleanupEngine",
    "CleanupTask",
    "CleanupPolicy",
]
