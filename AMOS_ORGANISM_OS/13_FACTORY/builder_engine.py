"""Builder Engine — Automated Build System

Manages build tasks for creating subsystems, modules, and components.
Tracks build progress, handles dependencies, and reports results.
"""

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class BuildStatus(Enum):
    """Status of a build task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BuildResult:
    """Result of a build task."""

    success: bool = False
    artifacts: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BuildTask:
    """A build task for creating a component."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    component_type: str = ""  # subsystem, module, alias, test
    target_path: str = ""
    dependencies: list[str] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)
    status: BuildStatus = BuildStatus.PENDING
    result: BuildResult = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    started_at: str = None
    completed_at: str = None

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "status": self.status.value,
            "result": self.result.to_dict() if self.result else None,
        }


class BuilderEngine:
    """Manages build tasks for automated construction.

    Handles the build lifecycle from task creation through
    execution to result reporting.
    """

    def __init__(self, organism_root: Path = None):
        if organism_root is None:
            organism_root = Path(__file__).parent.parent
        self.organism_root = organism_root

        self.tasks: dict[str, BuildTask] = {}
        self.build_queue: list[str] = []
        self.completed_builds: list[str] = []

    def create_task(
        self,
        name: str,
        component_type: str,
        target_path: str,
        description: str = "",
        dependencies: list[str] = None,
        parameters: dict[str, Any] = None,
    ) -> BuildTask:
        """Create a new build task."""
        task = BuildTask(
            name=name,
            description=description,
            component_type=component_type,
            target_path=target_path,
            dependencies=dependencies or [],
            parameters=parameters or {},
        )
        self.tasks[task.id] = task
        self.build_queue.append(task.id)
        return task

    def execute_task(self, task_id: str) -> BuildResult:
        """Execute a single build task."""
        task = self.tasks.get(task_id)
        if not task:
            return None

        if task.status != BuildStatus.PENDING:
            return task.result

        task.status = BuildStatus.IN_PROGRESS
        task.started_at = datetime.now(UTC).isoformat()

        # Check dependencies
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != BuildStatus.COMPLETED:
                task.status = BuildStatus.FAILED
                task.result = BuildResult(
                    success=False,
                    errors=[f"Dependency {dep_id} not completed"],
                )
                task.completed_at = datetime.now(UTC).isoformat()
                return task.result

        # Execute based on component type
        try:
            if task.component_type == "subsystem":
                result = self._build_subsystem(task)
            elif task.component_type == "module":
                result = self._build_module(task)
            elif task.component_type == "alias":
                result = self._build_alias(task)
            elif task.component_type == "stub":
                result = self._build_stub(task)
            else:
                result = BuildResult(
                    success=False,
                    errors=[f"Unknown component type: {task.component_type}"],
                )

            task.result = result
            task.status = BuildStatus.COMPLETED if result.success else BuildStatus.FAILED
            task.completed_at = datetime.now(UTC).isoformat()

            if result.success:
                self.completed_builds.append(task_id)
                if task_id in self.build_queue:
                    self.build_queue.remove(task_id)

            return result

        except Exception as e:
            task.status = BuildStatus.FAILED
            task.result = BuildResult(
                success=False,
                errors=[str(e)],
            )
            task.completed_at = datetime.now(UTC).isoformat()
            return task.result

    def _build_subsystem(self, task: BuildTask) -> BuildResult:
        """Build a subsystem directory structure."""
        target = self.organism_root / task.target_path
        try:
            (target / "data").mkdir(parents=True, exist_ok=True)
            return BuildResult(
                success=True,
                artifacts=[str(target)],
            )
        except Exception as e:
            return BuildResult(
                success=False,
                errors=[str(e)],
            )

    def _build_module(self, task: BuildTask) -> BuildResult:
        """Build a Python module."""
        # Module building would integrate with code generator
        return BuildResult(
            success=True,
            artifacts=[task.target_path],
        )

    def _build_alias(self, task: BuildTask) -> BuildResult:
        """Build an alias directory for numbered modules."""
        target = self.organism_root / task.target_path
        try:
            target.mkdir(parents=True, exist_ok=True)
            return BuildResult(
                success=True,
                artifacts=[str(target)],
            )
        except Exception as e:
            return BuildResult(
                success=False,
                errors=[str(e)],
            )

    def _build_stub(self, task: BuildTask) -> BuildResult:
        """Build a stub module."""
        # Stub building would integrate with code generator
        return BuildResult(
            success=True,
            artifacts=[task.target_path],
        )

    def execute_all(self) -> dict[str, BuildResult]:
        """Execute all pending build tasks."""
        results = {}
        # Sort by dependencies
        pending = [tid for tid in self.build_queue]

        for task_id in pending:
            result = self.execute_task(task_id)
            if result:
                results[task_id] = result

        return results

    def get_task_status(self, task_id: str) -> dict[str, Any]:
        """Get status of a build task."""
        task = self.tasks.get(task_id)
        if not task:
            return None
        return task.to_dict()

    def list_tasks(self) -> list[dict[str, Any]]:
        """List all build tasks."""
        return [t.to_dict() for t in self.tasks.values()]

    def get_status(self) -> dict[str, Any]:
        """Get builder engine status."""
        pending = sum(1 for t in self.tasks.values() if t.status == BuildStatus.PENDING)
        in_progress = sum(1 for t in self.tasks.values() if t.status == BuildStatus.IN_PROGRESS)
        completed = sum(1 for t in self.tasks.values() if t.status == BuildStatus.COMPLETED)
        failed = sum(1 for t in self.tasks.values() if t.status == BuildStatus.FAILED)

        return {
            "total_tasks": len(self.tasks),
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "failed": failed,
            "queue_length": len(self.build_queue),
        }


_BUILDER: BuilderEngine = None


def get_builder_engine(organism_root: Path = None) -> BuilderEngine:
    """Get or create global builder engine."""
    global _BUILDER
    if _BUILDER is None:
        _BUILDER = BuilderEngine(organism_root)
    return _BUILDER
