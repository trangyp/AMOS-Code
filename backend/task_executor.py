"""Real Task Executor - Production async task execution.

Replaces mock Celery with real async execution via AMOS orchestrators.
Integrates with Brain v2 for intelligent task optimization.
"""


import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

# Import real orchestrator bridge
try:
    from backend.real_orchestrator_bridge import get_real_orchestrator_bridge
except ImportError:
    from real_orchestrator_bridge import get_real_orchestrator_bridge

# Brain v2 integration for intelligent task execution
try:
    from amos_brain.api_integration import brain_process_sync
    from amos_brain.brain_event_processor import emit_event

    _BRAIN_TASK_EXECUTOR_AVAILABLE = True
except ImportError:
    _BRAIN_TASK_EXECUTOR_AVAILABLE = False


class TaskState(Enum):
    """Task execution states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Async task with real orchestrator execution."""

    id: str
    name: str
    description: str
    priority: str
    state: TaskState = TaskState.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    domain: str = "unknown"
    engines_used: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    progress: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "domain": self.domain,
            "engines_used": self.engines_used,
            "duration_ms": self.duration_ms,
            "progress": self.progress,
        }


class AMOSTaskExecutor:
    """Real task executor using AMOS orchestrators.

    Uses MasterOrchestrator, TaskExecutionIntegration, OrganismBridge
    for real cognitive task execution.
    """

    _instance: Optional[AMOSTaskExecutor] = None

    def __new__(cls) -> AMOSTaskExecutor:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._tasks: Dict[str, Task] = {}
        self._running_tasks: Set[str] = set()
        self._bridge = get_real_orchestrator_bridge()
        self._initialized = False
        self._max_concurrent = 10
        self._semaphore = asyncio.Semaphore(self._max_concurrent)

    async def initialize(self) -> bool:
        """Initialize the task executor."""
        if self._initialized:
            return True

        print("[AMOSTaskExecutor] Initializing...")

        # Initialize orchestrator bridge
        bridge_ready = await self._bridge.initialize()
        if not bridge_ready:
            print("  ⚠️ Bridge initialization failed")

        self._initialized = True
        print("  ✓ Task executor ready")
        return True

    async def submit_task(
        self,
        name: str,
        description: str,
        priority: str = "MEDIUM",
        context: Dict[str, Any] = None,
    ) -> Task:
        """Submit a task for execution."""
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        task = Task(
            id=task_id,
            name=name,
            description=description,
            priority=priority.upper(),
        )

        self._tasks[task_id] = task

        # Start execution immediately (background)
        asyncio.create_task(self._execute_task(task_id, context))

        return task

    async def _execute_task(
        self,
        task_id: str,
        context: Dict[str, Any] = None,
    ) -> None:
        """Execute task through real orchestrator."""
        task = self._tasks.get(task_id)
        if not task:
            return

        async with self._semaphore:
            self._running_tasks.add(task_id)
            task.state = TaskState.RUNNING
            task.started_at = datetime.now(UTC)
            task.progress = 10

            try:
                # Execute through real orchestrator bridge
                result = await self._bridge.execute_task(
                    task_description=task.description,
                    priority=task.priority,
                    context=context,
                )

                # Update task with real results
                task.progress = 100
                task.state = TaskState.COMPLETED if result.success else TaskState.FAILED
                task.completed_at = datetime.now(UTC)
                task.duration_ms = result.duration_ms
                task.domain = result.domain
                task.engines_used = result.engines_used

                if result.success:
                    task.result = {
                        "output": result.output,
                        "execution_type": result.execution_type,
                        "artifacts": result.artifacts,
                        "organism_enhancements": result.organism_enhancements,
                    }
                else:
                    task.error = result.error

            except Exception as e:
                task.state = TaskState.FAILED
                task.error = str(e)
                task.completed_at = datetime.now(UTC)

            finally:
                self._running_tasks.discard(task_id)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self._tasks.get(task_id)

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        return task.to_dict()

    def list_tasks(
        self,
        state: Optional[TaskState] = None,
        limit: int = 100,
    ) -> List[dict[str, Any]]:
        """List tasks with optional filtering."""
        tasks = list(self._tasks.values())

        if state:
            tasks = [t for t in tasks if t.state == state]

        # Sort by created_at descending
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        return [t.to_dict() for t in tasks[:limit]]

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        task = self._tasks.get(task_id)
        if not task:
            return False

        if task.state in (TaskState.PENDING, TaskState.RUNNING):
            task.state = TaskState.CANCELLED
            task.completed_at = datetime.now(UTC)
            self._running_tasks.discard(task_id)
            return True

        return False

    def get_executor_status(self) -> Dict[str, Any]:
        """Get executor status."""
        bridge_status = self._bridge.get_status()

        return {
            "initialized": self._initialized,
            "total_tasks": len(self._tasks),
            "running_tasks": len(self._running_tasks),
            "pending_tasks": sum(1 for t in self._tasks.values() if t.state == TaskState.PENDING),
            "completed_tasks": sum(
                1 for t in self._tasks.values() if t.state == TaskState.COMPLETED
            ),
            "failed_tasks": sum(1 for t in self._tasks.values() if t.state == TaskState.FAILED),
            "max_concurrent": self._max_concurrent,
            "orchestrator_status": bridge_status,
        }

    async def optimize_task_with_brain(self, task_id: str) -> Dict[str, Any]:
        """Use Brain v2 to optimize task execution parameters.

        Args:
            task_id: Task ID to optimize

        Returns:
            Optimization recommendations
        """
        task = self._tasks.get(task_id)
        if not task:
            return {"error": "Task not found", "task_id": task_id}

        if not _BRAIN_TASK_EXECUTOR_AVAILABLE:
            return {"optimization": "brain_not_available", "task_id": task_id}

        try:
            # Emit task optimization event
            emit_event(
                "executor.task_optimization_requested",
                {
                    "task_id": task_id,
                    "task_name": task.name,
                    "task_description": task.description,
                    "current_priority": task.priority,
                    "task_state": task.state.value,
                },
            )

            # Get brain optimization
            result = brain_process_sync(
                f"Optimize task execution: {task.name}",
                {
                    "task_id": task_id,
                    "task_name": task.name,
                    "task_description": task.description,
                    "priority": task.priority,
                    "state": task.state.value,
                    "domain": task.domain,
                    "engines_used": task.engines_used,
                    "duration_ms": task.duration_ms,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

            return {
                "task_id": task_id,
                "optimization": result.get("optimization", {}),
                "recommended_priority": result.get("recommended_priority", task.priority),
                "execution_strategy": result.get("execution_strategy", "standard"),
                "resource_allocation": result.get("resource_allocation", {}),
                "brain_processed": True,
            }
        except Exception as e:
            return {
                "optimization": "error",
                "error": str(e),
                "task_id": task_id,
                "brain_processed": False,
            }


# Global executor instance
_executor: Optional[AMOSTaskExecutor] = None


def get_task_executor() -> AMOSTaskExecutor:
    """Get or create the task executor."""
    global _executor
    if _executor is None:
        _executor = AMOSTaskExecutor()
    return _executor


# Convenience functions for API
async def submit_agent_task(
    role: str,
    paradigm: str = "HYBRID",
    name: Optional[str] = None,
    task_description: str = "",
) -> str:
    """Submit an agent spawn task.

    Args:
        role: Agent role (architect, reviewer, auditor, executor)
        paradigm: Cognitive paradigm
        name: Agent name
        task_description: Task to execute

    Returns:
        Task ID
    """
    executor = get_task_executor()
    await executor.initialize()

    task = await executor.submit_task(
        name=name or f"agent_{role}",
        description=task_description or f"Spawn {role} agent with {paradigm} paradigm",
        priority="HIGH",
        context={"role": role, "paradigm": paradigm, "agent_name": name},
    )

    return task.id


async def submit_orchestration_task(
    task_description: str,
    agents: Optional[List[str] ] = None,
    require_consensus: bool = True,
    session_id: Optional[str] = None,
) -> str:
    """Submit an orchestration task.

    Args:
        task_description: The task to orchestrate
        agents: List of agent roles to use
        require_consensus: Whether to require consensus
        session_id: Session ID for memory

    Returns:
        Task ID
    """
    executor = get_task_executor()
    await executor.initialize()

    task = await executor.submit_task(
        name="multi_agent_orchestration",
        description=task_description,
        priority="HIGH",
        context={
            "agents": agents or [],
            "require_consensus": require_consensus,
            "session_id": session_id,
        },
    )

    return task.id


async def get_task_result(task_id: str) -> Dict[str, Any]:
    """Get task result by ID."""
    executor = get_task_executor()
    return executor.get_task_status(task_id)


async def cancel_task(task_id: str) -> bool:
    """Cancel a task."""
    executor = get_task_executor()
    return executor.cancel_task(task_id)


async def get_executor_status() -> Dict[str, Any]:
    """Get task executor status."""
    executor = get_task_executor()
    return executor.get_executor_status()


# Alias for compatibility with code expecting TaskExecutor
TaskExecutor = AMOSTaskExecutor
