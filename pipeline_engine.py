"""Pipeline Engine stub for compatibility."""

from collections.abc import Callable
from typing import Any


class PipelineStage:
    """Represents a pipeline stage."""

    def __init__(self, name: str, func: Callable, config: Dict[str, Any] = None):
        self.name = name
        self.func = func
        self.config = config or {}


class Pipeline:
    """Represents a processing pipeline."""

    def __init__(self, name: str):
        self.name = name
        self.stages: List[PipelineStage] = []

    def add_stage(self, stage: PipelineStage) -> None:
        """Add stage to pipeline."""
        self.stages.append(stage)

    def execute(self, data: Any) -> Any:
        """Execute pipeline on data."""
        result = data
        for stage in self.stages:
            result = stage.func(result, **stage.config)
        return result


class PipelineEngine:
    """Engine for pipeline management."""

    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}

    def create_pipeline(self, name: str) -> Pipeline:
        """Create new pipeline."""
        pipeline = Pipeline(name)
        self.pipelines[name] = pipeline
        return pipeline

    def get_pipeline(self, name: str) -> Optional[Pipeline]:
        """Get pipeline by name."""
        return self.pipelines.get(name)


__all__ = ["Pipeline", "PipelineStage", "PipelineEngine"]
