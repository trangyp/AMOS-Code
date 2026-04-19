#!/usr/bin/env python3
"""AMOS Task Queue System
=======================

Central task queue for cross-subsystem coordination.
Routes tasks to appropriate agents and tracks execution.

Owner: Trang
Version: 1.0.0
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """A task in the queue."""

    id: str
    title: str
    description: str
    task_type: str
    source_subsystem: str
    target_agent: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any] ] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class TaskAssignment:
    """Task assigned to an agent."""

    task_id: str
    agent_id: str
    assigned_at: str
    expected_duration: int  # seconds


class TaskQueue:
    """Central task queue for AMOS organism.
    Manages task lifecycle from creation to completion.
    """

    def __init__(self, organism_root: Path) -> None:
        self.root = organism_root
        self.queue_dir = organism_root / "07_METABOLISM" / "task_queue"
        self.queue_dir.mkdir(parents=True, exist_ok=True)

        self.tasks: Dict[str, Task] = {}
        self.assignments: Dict[str, TaskAssignment] = {}
        self.task_history: List[str] = []

        self._load_state()

    def _load_state(self) -> None:
        """Load persisted tasks from disk."""
        state_file = self.queue_dir / "queue_state.json"
        if state_file.exists():
            try:
                with open(state_file, encoding="utf-8") as f:
                    data = json.load(f)

                for task_data in data.get("tasks", []):
                    task = Task(
                        id=task_data["id"],
                        title=task_data["title"],
                        description=task_data["description"],
                        task_type=task_data["task_type"],
                        source_subsystem=task_data["source_subsystem"],
                        target_agent=task_data.get("target_agent"),
                        priority=TaskPriority[task_data.get("priority", "MEDIUM")],
                        status=TaskStatus[task_data.get("status", "PENDING")],
                        created_at=task_data["created_at"],
                        started_at=task_data.get("started_at"),
                        completed_at=task_data.get("completed_at"),
                        params=task_data.get("params", {}),
                        result=task_data.get("result"),
                        error_message=task_data.get("error_message"),
                        retry_count=task_data.get("retry_count", 0),
                        max_retries=task_data.get("max_retries", 3),
                    )
                    self.tasks[task.id] = task

                self.task_history = data.get("task_history", [])

            except Exception as e:
                print(f"[TASK_QUEUE] Error loading state: {e}")

    def _save_state(self) -> None:
        """Persist tasks to disk."""
        state_file = self.queue_dir / "queue_state.json"

        data = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "total_tasks": len(self.tasks),
            "pending": len(self.get_pending_tasks()),
            "running": len(self.get_running_tasks()),
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "task_type": t.task_type,
                    "source_subsystem": t.source_subsystem,
                    "target_agent": t.target_agent,
                    "priority": t.priority.name,
                    "status": t.status.name,
                    "created_at": t.created_at,
                    "started_at": t.started_at,
                    "completed_at": t.completed_at,
                    "params": t.params,
                    "result": t.result,
                    "error_message": t.error_message,
                    "retry_count": t.retry_count,
                    "max_retries": t.max_retries,
                }
                for t in self.tasks.values()
            ],
            "task_history": self.task_history[-100:],  # Keep last 100
        }

        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def submit_task(
        self,
        title: str,
        description: str,
        task_type: str,
        source_subsystem: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        target_agent: Optional[str] = None,
        params: Optional[Dict[str, Any] ] = None,
    ) -> Task:
        """Submit a new task to the queue."""
        task = Task(
            id=str(uuid.uuid4())[:8],
            title=title,
            description=description,
            task_type=task_type,
            source_subsystem=source_subsystem,
            target_agent=target_agent,
            priority=priority,
            params=params or {},
        )

        self.tasks[task.id] = task
        self._save_state()

        print(f"[TASK_QUEUE] Submitted: {title} ({task.id})")
        return task

    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """Assign a pending task to an agent."""
        task = self.tasks.get(task_id)
        if not task or task.status != TaskStatus.PENDING:
            return False

        task.status = TaskStatus.ASSIGNED
        task.target_agent = agent_id
        task.started_at = datetime.now(UTC).isoformat()

        assignment = TaskAssignment(
            task_id=task_id,
            agent_id=agent_id,
            assigned_at=datetime.now(UTC).isoformat(),
            expected_duration=300,  # 5 minutes default
        )
        self.assignments[task_id] = assignment

        self._save_state()
        print(f"[TASK_QUEUE] Assigned {task_id} to {agent_id}")
        return True

    def start_task(self, task_id: str) -> bool:
        """Mark a task as running."""
        task = self.tasks.get(task_id)
        if not task or task.status != TaskStatus.ASSIGNED:
            return False

        task.status = TaskStatus.RUNNING
        self._save_state()
        return True

    def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Mark a task as completed with result."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(UTC).isoformat()
        task.result = result

        self.task_history.append(task_id)
        if task_id in self.assignments:
            del self.assignments[task_id]

        self._save_state()
        print(f"[TASK_QUEUE] Completed: {task_id}")
        return True

    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark a task as failed."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        task.error_message = error
        task.retry_count += 1

        if task.retry_count >= task.max_retries:
            task.status = TaskStatus.FAILED
            self.task_history.append(task_id)
            print(f"[TASK_QUEUE] Failed (max retries): {task_id}")
        else:
            # Retry
            task.status = TaskStatus.PENDING
            print(f"[TASK_QUEUE] Retry {task.retry_count}/{task.max_retries}: {task_id}")

        if task_id in self.assignments:
            del self.assignments[task_id]

        self._save_state()
        return True

    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks sorted by priority."""
        pending = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
        return sorted(pending, key=lambda x: x.priority.value, reverse=True)

    def get_running_tasks(self) -> List[Task]:
        """Get all running tasks."""
        return [t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]

    def get_tasks_for_agent(self, agent_id: str) -> List[Task]:
        """Get tasks assigned to a specific agent."""
        return [
            t
            for t in self.tasks.values()
            if t.target_agent == agent_id and t.status in [TaskStatus.ASSIGNED, TaskStatus.RUNNING]
        ]

    def process_next_task(self, available_agents: List[str]) -> Optional[Task]:
        """Process the next pending task if agents available."""
        pending = self.get_pending_tasks()
        if not pending or not available_agents:
            return None

        task = pending[0]
        agent = available_agents[0]

        if self.assign_task(task.id, agent):
            return task
        return None

    def get_status(self) -> Dict[str, Any]:
        """Get queue status."""
        status_counts = dict.fromkeys(TaskStatus, 0)
        for task in self.tasks.values():
            status_counts[task.status] += 1

        return {
            "status": "operational",
            "total_tasks": len(self.tasks),
            "pending": status_counts[TaskStatus.PENDING],
            "assigned": status_counts[TaskStatus.ASSIGNED],
            "running": status_counts[TaskStatus.RUNNING],
            "completed": status_counts[TaskStatus.COMPLETED],
            "failed": status_counts[TaskStatus.FAILED],
            "active_assignments": len(self.assignments),
        }

    def cleanup_old_tasks(self, max_age_hours: int = 24) -> int:
        """Remove completed/failed tasks older than max_age."""
        cutoff = datetime.now(UTC).timestamp() - (max_age_hours * 3600)
        to_remove = []

        for task_id, task in self.tasks.items():
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                created_ts = datetime.fromisoformat(
                    task.created_at.replace("Z", "+00:00")
                ).timestamp()
                if created_ts < cutoff:
                    to_remove.append(task_id)

        for task_id in to_remove:
            del self.tasks[task_id]

        if to_remove:
            self._save_state()
            print(f"[TASK_QUEUE] Cleaned up {len(to_remove)} old tasks")

        return len(to_remove)


def main() -> int:
    """CLI for Task Queue."""
    print("=" * 50)
    print("AMOS Task Queue System")
    print("=" * 50)

    organism_root = Path(__file__).parent.parent
    queue = TaskQueue(organism_root)

    # Submit example tasks
    print("\nSubmitting example tasks...")

    queue.submit_task(
        title="Analyze codebase",
        description="Analyze the AMOS codebase for patterns",
        task_type="analysis",
        source_subsystem="01_BRAIN",
        priority=TaskPriority.HIGH,
        target_agent="analyst_agent",
    )

    queue.submit_task(
        title="Generate documentation",
        description="Create documentation for new subsystem",
        task_type="documentation",
        source_subsystem="06_MUSCLE",
        priority=TaskPriority.MEDIUM,
    )

    queue.submit_task(
        title="Security audit",
        description="Run security checks on all subsystems",
        task_type="security",
        source_subsystem="03_IMMUNE",
        priority=TaskPriority.CRITICAL,
    )

    # Show status
    print("\nQueue Status:")
    status = queue.get_status()
    print(f"  Total tasks: {status['total_tasks']}")
    print(f"  Pending: {status['pending']}")
    print(f"  Running: {status['running']}")
    print(f"  Completed: {status['completed']}")

    # Show pending tasks
    print("\nPending Tasks (by priority):")
    for task in queue.get_pending_tasks():
        print(f"  [{task.priority.name}] {task.title} ({task.task_type})")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
