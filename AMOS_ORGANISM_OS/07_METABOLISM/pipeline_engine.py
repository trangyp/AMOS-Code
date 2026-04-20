"""Pipeline Engine — Multi-stage data processing pipelines

Defines and executes multi-stage pipelines for data transformation,
processing, and routing through the organism.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class StageStatus(Enum):
    """Status of a pipeline stage."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineStage:
    """A single stage in a pipeline."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    stage_type: str = ""  # transform, filter, route, validate
    config: dict[str, Any] = field(default_factory=dict)
    status: StageStatus = StageStatus.PENDING
    input_data: Any = None
    output_data: Any = None
    error: str = ""
    start_time: str = None
    end_time: str = None
    depends_on: list[str] = field(default_factory=list)
    next_stages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "status": self.status.value,
        }


@dataclass
class Pipeline:
    """A multi-stage pipeline definition."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    stages: list[PipelineStage] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    status: str = "draft"  # draft, running, completed, failed
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_stage(self, stage: PipelineStage) -> PipelineStage:
        """Add a stage to the pipeline."""
        self.stages.append(stage)
        return stage

    def get_stage(self, stage_id: str) -> Optional[PipelineStage]:
        """Get a stage by ID."""
        for stage in self.stages:
            if stage.id == stage_id:
                return stage
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "stages": [s.to_dict() for s in self.stages],
        }


class PipelineEngine:
    """Executes multi-stage pipelines.

    Manages pipeline definitions, executes stages in order,
    handles dependencies, and routes data between stages.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.pipelines: dict[str, Pipeline] = {}
        self.stage_handlers: dict[str, Callable] = {}

        self._load_pipelines()
        self._register_default_handlers()

    def _load_pipelines(self):
        """Load saved pipelines."""
        pipelines_file = self.data_dir / "pipelines.json"
        if pipelines_file.exists():
            try:
                data = json.loads(pipelines_file.read_text())
                for pipe_data in data.get("pipelines", []):
                    pipeline = Pipeline(
                        id=pipe_data["id"],
                        name=pipe_data["name"],
                        description=pipe_data["description"],
                        created_at=pipe_data["created_at"],
                        status=pipe_data["status"],
                        metadata=pipe_data.get("metadata", {}),
                    )
                    for stage_data in pipe_data.get("stages", []):
                        stage = PipelineStage(
                            id=stage_data["id"],
                            name=stage_data["name"],
                            stage_type=stage_data["stage_type"],
                            config=stage_data.get("config", {}),
                            status=StageStatus(stage_data["status"]),
                            depends_on=stage_data.get("depends_on", []),
                            next_stages=stage_data.get("next_stages", []),
                        )
                        pipeline.stages.append(stage)
                    self.pipelines[pipeline.id] = pipeline
            except Exception as e:
                print(f"[PIPELINE] Error loading pipelines: {e}")

    def save(self):
        """Save pipelines to disk."""
        pipelines_file = self.data_dir / "pipelines.json"
        data = {
            "saved_at": datetime.now(UTC).isoformat(),
            "pipelines": [p.to_dict() for p in self.pipelines.values()],
        }
        pipelines_file.write_text(json.dumps(data, indent=2))

    def _register_default_handlers(self):
        """Register default stage handlers."""
        self.register_handler("transform", self._handle_transform)
        self.register_handler("filter", self._handle_filter)
        self.register_handler("validate", self._handle_validate)
        self.register_handler("route", self._handle_route)
        self.register_handler("log", self._handle_log)

    def register_handler(self, stage_type: str, handler: Callable):
        """Register a handler for a stage type."""
        self.stage_handlers[stage_type] = handler

    def create_pipeline(self, name: str, description: str = "") -> Pipeline:
        """Create a new pipeline."""
        pipeline = Pipeline(name=name, description=description)
        self.pipelines[pipeline.id] = pipeline
        self.save()
        return pipeline

    def execute_pipeline(
        self,
        pipeline_id: str,
        initial_data: Any = None,
        context: dict = None,
    ) -> dict[str, Any]:
        """Execute a pipeline with data."""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return {"success": False, "error": "Pipeline not found"}

        pipeline.status = "running"
        context = context or {}
        results = {}

        # Execute stages in order (simple sequential for now)
        for stage in pipeline.stages:
            # Check dependencies
            if stage.depends_on:
                deps_met = all(
                    results.get(dep, {}).get("status") == StageStatus.COMPLETED.value
                    for dep in stage.depends_on
                )
                if not deps_met:
                    stage.status = StageStatus.SKIPPED
                    results[stage.id] = {"status": StageStatus.SKIPPED.value}
                    continue

            # Execute stage
            stage.input_data = initial_data if stage == pipeline.stages[0] else None
            stage.start_time = datetime.now(UTC).isoformat()
            stage.status = StageStatus.RUNNING

            handler = self.stage_handlers.get(stage.stage_type)
            if handler:
                try:
                    result = handler(stage, context)
                    stage.output_data = result
                    stage.status = StageStatus.COMPLETED
                    results[stage.id] = {
                        "status": StageStatus.COMPLETED.value,
                        "output": result,
                    }
                except Exception as e:
                    stage.error = str(e)
                    stage.status = StageStatus.FAILED
                    results[stage.id] = {
                        "status": StageStatus.FAILED.value,
                        "error": str(e),
                    }
            else:
                stage.error = f"No handler for type: {stage.stage_type}"
                stage.status = StageStatus.FAILED
                results[stage.id] = {
                    "status": StageStatus.FAILED.value,
                    "error": stage.error,
                }

            stage.end_time = datetime.now(UTC).isoformat()

        # Determine overall success
        failed = any(r.get("status") == StageStatus.FAILED.value for r in results.values())
        pipeline.status = "failed" if failed else "completed"

        self.save()

        return {
            "success": not failed,
            "pipeline_id": pipeline_id,
            "results": results,
        }

    # Default handlers
    def _handle_transform(self, stage: PipelineStage, context: dict) -> Any:
        """Transform data using config."""
        transform_type = stage.config.get("transform", "identity")
        if transform_type == "uppercase" and isinstance(stage.input_data, str):
            return stage.input_data.upper()
        elif transform_type == "lowercase" and isinstance(stage.input_data, str):
            return stage.input_data.lower()
        return stage.input_data

    def _handle_filter(self, stage: PipelineStage, context: dict) -> Any:
        """Filter data."""
        condition = stage.config.get("condition", "always")
        if condition == "not_empty":
            return stage.input_data if stage.input_data else None
        return stage.input_data

    def _handle_validate(self, stage: PipelineStage, context: dict) -> Any:
        """Validate data."""
        required = stage.config.get("required_fields", [])
        if isinstance(stage.input_data, dict):
            missing = [f for f in required if f not in stage.input_data]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")
        return stage.input_data

    def _handle_route(self, stage: PipelineStage, context: dict) -> Any:
        """Route data to destination."""
        destination = stage.config.get("destination", "default")
        # Routing logic would go here
        return {"routed_to": destination, "data": stage.input_data}

    def _handle_log(self, stage: PipelineStage, context: dict) -> Any:
        """Log data."""
        message = stage.config.get("message", "Pipeline stage executed")
        print(f"[PIPELINE] {stage.name}: {message}")
        return stage.input_data

    def get_pipeline_status(self, pipeline_id: str) -> dict:
        """Get status of a pipeline."""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return None

        return {
            "id": pipeline.id,
            "name": pipeline.name,
            "status": pipeline.status,
            "stage_count": len(pipeline.stages),
            "stages": [
                {
                    "id": s.id,
                    "name": s.name,
                    "type": s.stage_type,
                    "status": s.status.value,
                }
                for s in pipeline.stages
            ],
        }

    def list_pipelines(self) -> list[dict]:
        """List all pipelines."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "status": p.status,
                "stage_count": len(p.stages),
            }
            for p in self.pipelines.values()
        ]


# Global instance
_ENGINE: Optional[PipelineEngine] = None


def get_pipeline_engine(data_dir: Optional[Path] = None) -> PipelineEngine:
    """Get or create global pipeline engine."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = PipelineEngine(data_dir)
    return _ENGINE


if __name__ == "__main__":
    print("Pipeline Engine (07_METABOLISM)")
    print("=" * 40)

    engine = get_pipeline_engine()

    # Create a sample pipeline
    pipeline = engine.create_pipeline("Sample Pipeline", "Test pipeline")

    # Add stages
    stage1 = PipelineStage(name="Transform", stage_type="transform")
    stage2 = PipelineStage(name="Validate", stage_type="validate")
    stage3 = PipelineStage(name="Log", stage_type="log")

    pipeline.add_stage(stage1)
    pipeline.add_stage(stage2)
    pipeline.add_stage(stage3)

    print(f"\nCreated pipeline: {pipeline.name}")
    print(f"Stages: {len(pipeline.stages)}")

    print("\nPipeline list:")
    for p in engine.list_pipelines():
        print(f"  - {p['name']} ({p['id']})")
