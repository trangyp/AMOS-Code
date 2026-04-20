"""METABOLISM module — Alias for 07_METABOLISM"""

import importlib.util
from pathlib import Path

# Load modules from 07_METABOLISM using importlib
_07_METABOLISM_PATH = Path(__file__).parent.parent / "07_METABOLISM"

# cleanup_engine
_spec_ce = importlib.util.spec_from_file_location(
    "_clean_eng", _07_METABOLISM_PATH / "cleanup_engine.py"
)
_mod_ce = importlib.util.module_from_spec(_spec_ce)
_spec_ce.loader.exec_module(_mod_ce)
CleanupEngine = _mod_ce.CleanupEngine
CleanupPolicy = _mod_ce.CleanupPolicy
CleanupTask = _mod_ce.CleanupTask
get_cleanup_engine = _mod_ce.get_cleanup_engine

# io_router
_spec_ir = importlib.util.spec_from_file_location("_io_rtr", _07_METABOLISM_PATH / "io_router.py")
_mod_ir = importlib.util.module_from_spec(_spec_ir)
_spec_ir.loader.exec_module(_mod_ir)
IORouter = _mod_ir.IORouter
Route = _mod_ir.Route
RouteConfig = _mod_ir.RouteConfig
get_io_router = _mod_ir.get_io_router

# transform_engine
_spec_te = importlib.util.spec_from_file_location(
    "_trans_eng", _07_METABOLISM_PATH / "transform_engine.py"
)
_mod_te = importlib.util.module_from_spec(_spec_te)
_spec_te.loader.exec_module(_mod_te)
TransformEngine = _mod_te.TransformEngine
Transform = _mod_te.Transform
TransformContext = _mod_te.TransformContext
get_transform_engine = _mod_te.get_transform_engine

# pipeline_engine
_spec_pe = importlib.util.spec_from_file_location(
    "_pipe_eng", _07_METABOLISM_PATH / "pipeline_engine.py"
)
_mod_pe = importlib.util.module_from_spec(_spec_pe)
_spec_pe.loader.exec_module(_mod_pe)
PipelineEngine = _mod_pe.PipelineEngine
Pipeline = _mod_pe.Pipeline
PipelineStage = _mod_pe.PipelineStage
get_pipeline_engine = _mod_pe.get_pipeline_engine

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
