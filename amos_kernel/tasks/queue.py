from __future__ import annotations

"""Task Queue - Async task execution for kernel workflows"""

import json
import sqlite3
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Kernel task definition."""

    id: str
    task_type: str
    payload: dict[str, Any]
    status: TaskStatus
    priority: int
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: dict | None = None
    error: Optional[str] = None


class TaskQueue:
    """SQLite-backed task queue for async workflow execution."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path.home() / ".amos_kernel" / "tasks.db")
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._handlers: dict[str, Callable[[dict], dict]] = {}
        self._running = False
        self._worker_thread: threading.Optional[Thread] = None
        self._lock = threading.Lock()

    def _init_db(self) -> None:
        """Initialize task database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    task_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    result TEXT,
                    error TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_priority ON tasks(priority)")
            conn.commit()

    def register_handler(self, task_type: str, handler: Callable[[dict], dict]) -> None:
        """Register task handler."""
        self._handlers[task_type] = handler

    def submit(
        self,
        task_type: str,
        payload: dict[str, Any],
        priority: int = 5,
    ) -> str:
        """Submit task to queue."""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            task_type=task_type,
            payload=payload,
            status=TaskStatus.PENDING,
            priority=priority,
            created_at=datetime.now(UTC).isoformat(),
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    task.id,
                    task.task_type,
                    json.dumps(task.payload),
                    task.status.value,
                    task.priority,
                    task.created_at,
                    None,
                    None,
                    None,
                    None,
                ),
            )
            conn.commit()

        return task_id

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if row:
                return self._row_to_task(row)
            return None

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
    ) -> list[Task]:
        """List tasks."""
        with sqlite3.connect(self.db_path) as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE status = ? ORDER BY priority DESC, created_at LIMIT ?",
                    (status.value, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM tasks ORDER BY priority DESC, created_at LIMIT ?", (limit,)
                ).fetchall()
            return [self._row_to_task(r) for r in rows]

    def start_worker(self, interval: float = 1.0) -> None:
        """Start background worker thread."""
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, args=(interval,))
        self._worker_thread.daemon = True
        self._worker_thread.start()

    def stop_worker(self) -> None:
        """Stop background worker."""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)

    def _worker_loop(self, interval: float) -> None:
        """Worker thread main loop."""
        while self._running:
            try:
                self._process_pending()
            except Exception as e:
                print(f"Task worker error: {e}")
            time.sleep(interval)

    def _process_pending(self) -> None:
        """Process pending tasks."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """SELECT * FROM tasks
                    WHERE status = ?
                    ORDER BY priority DESC, created_at
                    LIMIT 1""",
                (TaskStatus.PENDING.value,),
            ).fetchone()

            if not row:
                return

            task = self._row_to_task(row)

            # Mark as running
            started_at = datetime.now(UTC).isoformat()
            conn.execute(
                "UPDATE tasks SET status = ?, started_at = ? WHERE id = ?",
                (TaskStatus.RUNNING.value, started_at, task.id),
            )
            conn.commit()

        # Execute task
        handler = self._handlers.get(task.task_type)
        if handler:
            try:
                result = handler(task.payload)
                self._complete_task(task.id, result)
            except Exception as e:
                self._fail_task(task.id, str(e))
        else:
            self._fail_task(task.id, f"No handler for task type: {task.task_type}")

    def _complete_task(self, task_id: str, result: dict) -> None:
        """Mark task as completed."""
        completed_at = datetime.now(UTC).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE tasks SET status = ?, completed_at = ?, result = ? WHERE id = ?",
                (TaskStatus.COMPLETED.value, completed_at, json.dumps(result), task_id),
            )
            conn.commit()

    def _fail_task(self, task_id: str, error: str) -> None:
        """Mark task as failed."""
        completed_at = datetime.now(UTC).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE tasks SET status = ?, completed_at = ?, error = ? WHERE id = ?",
                (TaskStatus.FAILED.value, completed_at, error, task_id),
            )
            conn.commit()

    def _row_to_task(self, row: tuple) -> Task:
        """Convert database row to Task."""
        return Task(
            id=row[0],
            task_type=row[1],
            payload=json.loads(row[2]),
            status=TaskStatus(row[3]),
            priority=row[4],
            created_at=row[5],
            started_at=row[6],
            completed_at=row[7],
            result=json.loads(row[8]) if row[8] else None,
            error=row[9],
        )

    def get_stats(self) -> dict[str, int]:
        """Get queue statistics."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            pending = conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE status = ?", (TaskStatus.PENDING.value,)
            ).fetchone()[0]
            running = conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE status = ?", (TaskStatus.RUNNING.value,)
            ).fetchone()[0]
            completed = conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE status = ?", (TaskStatus.COMPLETED.value,)
            ).fetchone()[0]
            failed = conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE status = ?", (TaskStatus.FAILED.value,)
            ).fetchone()[0]

        return {
            "total": total,
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
        }


# Global queue instance
_queue: Optional[TaskQueue] = None


def get_task_queue() -> TaskQueue:
    """Get global task queue."""
    global _queue
    if _queue is None:
        _queue = TaskQueue()
    return _queue


def submit_workflow_task(
    workflow_id: str,
    raw_input: dict[str, Any],
    priority: int = 5,
) -> str:
    """Submit workflow execution as async task."""
    from ..workflows import get_workflow_engine

    queue = get_task_queue()

    def handler(payload: dict) -> dict:
        engine = get_workflow_engine()
        result = engine.execute(
            workflow_id=payload["workflow_id"],
            raw_input=payload["raw_input"],
        )
        return {
            "workflow_id": result.workflow_id,
            "success": result.success,
            "steps": len(result.steps),
            "law_passed": result.law_validation.passed if result.law_validation else False,
            "collapse_risk": result.law_validation.collapse_risk if result.law_validation else 1.0,
        }

    queue.register_handler("workflow", handler)

    return queue.submit(
        task_type="workflow",
        payload={"workflow_id": workflow_id, "raw_input": raw_input},
        priority=priority,
    )
