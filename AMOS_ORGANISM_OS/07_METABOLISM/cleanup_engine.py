"""Cleanup Engine — Resource cleanup and maintenance

Manages cleanup tasks, temporary file removal, and
system maintenance operations.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class CleanupPolicy(Enum):
    """Policy for cleanup operations."""

    DELETE = "delete"  # Remove immediately
    ARCHIVE = "archive"  # Move to archive
    COMPRESS = "compress"  # Compress then archive
    TRUNCATE = "truncate"  # Truncate old entries


class TaskStatus(Enum):
    """Status of a cleanup task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class CleanupTask:
    """A cleanup task definition."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    target_pattern: str = ""  # Files/paths to clean
    policy: CleanupPolicy = CleanupPolicy.DELETE
    max_age_days: int = 7
    min_size_mb: int = None  # Only if larger than this
    dry_run: bool = True  # Preview without deleting
    schedule: str = "daily"  # daily, weekly, on_demand
    last_run: str = None
    last_status: TaskStatus = TaskStatus.PENDING
    items_cleaned: int = 0
    space_reclaimed_mb: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "policy": self.policy.value,
            "last_status": self.last_status.value,
        }


class CleanupEngine:
    """Manages system cleanup and maintenance.

    Handles temporary file cleanup, log rotation, and
    general maintenance tasks.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.tasks: Dict[str, CleanupTask] = []
        self.cleanup_handlers: Dict[CleanupPolicy, Callable] = {}

        self._load_tasks()
        self._register_default_handlers()

        # Create default cleanup tasks if none exist
        if not self.tasks:
            self._init_default_tasks()

    def _load_tasks(self):
        """Load saved cleanup tasks."""
        tasks_file = self.data_dir / "cleanup_tasks.json"
        if tasks_file.exists():
            try:
                data = json.loads(tasks_file.read_text())
                for t_data in data.get("tasks", []):
                    task = CleanupTask(
                        id=t_data["id"],
                        name=t_data["name"],
                        target_pattern=t_data["target_pattern"],
                        policy=CleanupPolicy(t_data["policy"]),
                        max_age_days=t_data["max_age_days"],
                        min_size_mb=t_data.get("min_size_mb"),
                        dry_run=t_data.get("dry_run", True),
                        schedule=t_data.get("schedule", "daily"),
                        last_run=t_data.get("last_run"),
                        last_status=TaskStatus(t_data.get("last_status", "pending")),
                        items_cleaned=t_data.get("items_cleaned", 0),
                        space_reclaimed_mb=t_data.get("space_reclaimed_mb", 0.0),
                        created_at=t_data["created_at"],
                        enabled=t_data.get("enabled", True),
                    )
                    self.tasks.append(task)
            except Exception as e:
                print(f"[CLEANUP] Error loading tasks: {e}")

    def save(self):
        """Save cleanup tasks to disk."""
        tasks_file = self.data_dir / "cleanup_tasks.json"
        data = {
            "saved_at": datetime.now(UTC).isoformat(),
            "tasks": [t.to_dict() for t in self.tasks],
        }
        tasks_file.write_text(json.dumps(data, indent=2))

    def _register_default_handlers(self):
        """Register default cleanup handlers."""
        self.cleanup_handlers[CleanupPolicy.DELETE] = self._handle_delete
        self.cleanup_handlers[CleanupPolicy.ARCHIVE] = self._handle_archive
        self.cleanup_handlers[CleanupPolicy.TRUNCATE] = self._handle_truncate

    def _init_default_tasks(self):
        """Create default cleanup tasks."""
        defaults = [
            CleanupTask(
                name="Clean Old Logs",
                target_pattern="logs/*.log",
                policy=CleanupPolicy.ARCHIVE,
                max_age_days=30,
                schedule="weekly",
                dry_run=False,
            ),
            CleanupTask(
                name="Clean Temp Files",
                target_pattern="tmp/*",
                policy=CleanupPolicy.DELETE,
                max_age_days=1,
                schedule="daily",
                dry_run=False,
            ),
            CleanupTask(
                name="Clean Output Cache",
                target_pattern="output/cache/*",
                policy=CleanupPolicy.DELETE,
                max_age_days=7,
                schedule="daily",
                dry_run=False,
            ),
        ]

        for task in defaults:
            self.tasks.append(task)

        self.save()

    def create_task(
        self,
        name: str,
        target_pattern: str,
        policy: CleanupPolicy,
        max_age_days: int = 7,
        schedule: str = "daily",
    ) -> CleanupTask:
        """Create a new cleanup task."""
        task = CleanupTask(
            name=name,
            target_pattern=target_pattern,
            policy=policy,
            max_age_days=max_age_days,
            schedule=schedule,
        )
        self.tasks.append(task)
        self.save()
        return task

    def execute_task(self, task_id: str, base_path: Optional[Path] = None) -> Dict[str, Any]:
        """Execute a specific cleanup task."""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return {"success": False, "error": "Task not found"}

        if not task.enabled:
            return {"success": False, "error": "Task disabled"}

        task.last_run = datetime.now(UTC).isoformat()
        task.last_status = TaskStatus.RUNNING

        handler = self.cleanup_handlers.get(task.policy)
        if not handler:
            task.last_status = TaskStatus.FAILED
            self.save()
            return {"success": False, "error": f"No handler for policy: {task.policy}"}

        try:
            result = handler(task, base_path)
            task.last_status = TaskStatus.COMPLETED
            task.items_cleaned = result.get("items_cleaned", 0)
            task.space_reclaimed_mb = result.get("space_reclaimed_mb", 0.0)
            self.save()
            return {
                "success": True,
                "task": task.name,
                **result,
            }
        except Exception as e:
            task.last_status = TaskStatus.FAILED
            self.save()
            return {"success": False, "error": str(e)}

    def execute_all(self, base_path: Optional[Path] = None) -> Dict[str, Any]:
        """Execute all enabled cleanup tasks."""
        results = []
        total_cleaned = 0
        total_space = 0.0

        for task in self.tasks:
            if task.enabled:
                result = self.execute_task(task.id, base_path)
                results.append(
                    {
                        "task_id": task.id,
                        "task_name": task.name,
                        **result,
                    }
                )
                if result["success"]:
                    total_cleaned += result.get("items_cleaned", 0)
                    total_space += result.get("space_reclaimed_mb", 0.0)

        return {
            "tasks_executed": len(results),
            "total_items_cleaned": total_cleaned,
            "total_space_reclaimed_mb": total_space,
            "results": results,
        }

    # Cleanup handlers
    def _handle_delete(self, task: CleanupTask, base_path: Path) -> Dict[str, Any]:
        """Handle delete policy."""
        import glob

        if base_path is None:
            base_path = Path(__file__).parent.parent

        items_cleaned = 0
        space_reclaimed = 0.0

        pattern = str(base_path / task.target_pattern)
        cutoff = datetime.now(UTC) - timedelta(days=task.max_age_days)

        for path in glob.glob(pattern):
            path_obj = Path(path)
            if path_obj.exists():
                stat = path_obj.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime)

                if mtime < cutoff:
                    size_mb = stat.st_size / (1024 * 1024)

                    if not task.dry_run:
                        if path_obj.is_file():
                            path_obj.unlink()
                        elif path_obj.is_dir():
                            import shutil

                            shutil.rmtree(path)

                    items_cleaned += 1
                    space_reclaimed += size_mb

        return {
            "items_cleaned": items_cleaned,
            "space_reclaimed_mb": space_reclaimed,
            "dry_run": task.dry_run,
        }

    def _handle_archive(self, task: CleanupTask, base_path: Path) -> Dict[str, Any]:
        """Handle archive policy."""
        import glob
        import shutil

        if base_path is None:
            base_path = Path(__file__).parent.parent

        archive_dir = base_path / "archive"
        archive_dir.mkdir(exist_ok=True)

        items_cleaned = 0
        space_reclaimed = 0.0

        pattern = str(base_path / task.target_pattern)
        cutoff = datetime.now(UTC) - timedelta(days=task.max_age_days)

        for path in glob.glob(pattern):
            path_obj = Path(path)
            if path_obj.exists():
                stat = path_obj.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime)

                if mtime < cutoff:
                    size_mb = stat.st_size / (1024 * 1024)

                    if not task.dry_run:
                        dest = archive_dir / path_obj.name
                        shutil.move(str(path_obj), str(dest))

                    items_cleaned += 1
                    space_reclaimed += size_mb

        return {
            "items_cleaned": items_cleaned,
            "space_reclaimed_mb": space_reclaimed,
            "dry_run": task.dry_run,
            "archive_dir": str(archive_dir),
        }

    def _handle_truncate(self, task: CleanupTask, base_path: Path) -> Dict[str, Any]:
        """Handle truncate policy for log files."""
        import glob

        if base_path is None:
            base_path = Path(__file__).parent.parent

        items_cleaned = 0

        pattern = str(base_path / task.target_pattern)

        for path in glob.glob(pattern):
            path_obj = Path(path)
            if path_obj.is_file() and not task.dry_run:
                # Keep only last N lines (simplified)
                lines = path_obj.read_text().split("\n")
                if len(lines) > 1000:
                    path_obj.write_text("\n".join(lines[-1000:]))
                    items_cleaned += 1

        return {
            "items_cleaned": items_cleaned,
            "space_reclaimed_mb": 0.0,  # Hard to estimate
            "dry_run": task.dry_run,
        }

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a cleanup task."""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return None

        return {
            "task": task.to_dict(),
            "next_run": self._get_next_run(task),
        }

    def _get_next_run(self, task: CleanupTask) -> str:
        """Calculate next scheduled run time."""
        if not task.last_run:
            return "ASAP"

        last = datetime.fromisoformat(task.last_run)

        if task.schedule == "daily":
            next_run = last + timedelta(days=1)
        elif task.schedule == "weekly":
            next_run = last + timedelta(weeks=1)
        else:
            return None

        return next_run.isoformat()

    def list_tasks(self, enabled_only: bool = False) -> List[dict]:
        """List all cleanup tasks."""
        tasks = self.tasks
        if enabled_only:
            tasks = [t for t in tasks if t.enabled]

        return [
            {
                "id": t.id,
                "name": t.name,
                "policy": t.policy.value,
                "schedule": t.schedule,
                "enabled": t.enabled,
                "last_run": t.last_run,
                "last_status": t.last_status.value,
            }
            for t in tasks
        ]


# Global instance
_ENGINE: Optional[CleanupEngine] = None


def get_cleanup_engine(data_dir: Optional[Path] = None) -> CleanupEngine:
    """Get or create global cleanup engine."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = CleanupEngine(data_dir)
    return _ENGINE


if __name__ == "__main__":
    print("Cleanup Engine (07_METABOLISM)")
    print("=" * 40)

    engine = get_cleanup_engine()

    print("\nCleanup Tasks:")
    for task in engine.list_tasks(enabled_only=True):
        print(f"  - {task['name']} ({task['schedule']})")
        print(f"    Last run: {task['last_run'] or 'Never'}")
        print(f"    Status: {task['last_status']}")

    print("\nNote: Tasks are in dry-run mode by default.")
    print("Set dry_run=False to actually clean files.")
