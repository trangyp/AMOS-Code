"""Persistence Store - SQLite-backed state storage for kernel"""

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

from ..workflows import WorkflowResult


class KernelStore:
    """SQLite persistence for kernel workflows and state."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path.home() / ".amos_kernel" / "kernel.db")
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    steps_count INTEGER NOT NULL,
                    law_passed INTEGER,
                    collapse_risk REAL,
                    drift_detected INTEGER NOT NULL,
                    repairs_proposed INTEGER NOT NULL,
                    result_json TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_workflow(self, result: WorkflowResult) -> None:
        """Save workflow result to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO workflows
                    (id, created_at, success, steps_count, law_passed,
                     collapse_risk, drift_detected, repairs_proposed, result_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    result.workflow_id,
                    datetime.now(UTC).isoformat(),
                    1 if result.success else 0,
                    len(result.steps),
                    1 if (result.law_validation and result.law_validation.passed) else 0,
                    result.law_validation.collapse_risk if result.law_validation else 0.0,
                    1 if result.drift_detected else 0,
                    result.repairs_proposed,
                    json.dumps(self._workflow_to_dict(result)),
                ),
            )
            conn.commit()

    def get_workflow(self, workflow_id: str) -> Optional[dict]:
        """Retrieve workflow by ID."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,)).fetchone()
            if row:
                return {
                    "id": row[0],
                    "created_at": row[1],
                    "success": bool(row[2]),
                    "steps_count": row[3],
                    "law_passed": bool(row[4]),
                    "collapse_risk": row[5],
                    "drift_detected": bool(row[6]),
                    "repairs_proposed": row[7],
                    "result": json.loads(row[8]),
                }
            return None

    def list_workflows(self, limit: int = 100) -> list[dict]:
        """List recent workflows."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM workflows ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
            return [
                {
                    "id": r[0],
                    "created_at": r[1],
                    "success": bool(r[2]),
                    "steps_count": r[3],
                    "law_passed": bool(r[4]),
                    "collapse_risk": r[5],
                    "drift_detected": bool(r[6]),
                    "repairs_proposed": r[7],
                }
                for r in rows
            ]

    def save_event(self, event_type: str, source: str, payload: dict) -> None:
        """Save kernel event."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO events (timestamp, event_type, source, payload) VALUES (?, ?, ?, ?)",
                (datetime.now(UTC).isoformat(), event_type, source, json.dumps(payload)),
            )
            conn.commit()

    def get_events(self, event_type: Optional[str] = None, limit: int = 100) -> list[dict]:
        """Get kernel events."""
        with sqlite3.connect(self.db_path) as conn:
            if event_type:
                rows = conn.execute(
                    "SELECT * FROM events WHERE event_type = ? ORDER BY timestamp DESC LIMIT ?",
                    (event_type, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,)
                ).fetchall()
            return [
                {
                    "id": r[0],
                    "timestamp": r[1],
                    "event_type": r[2],
                    "source": r[3],
                    "payload": json.loads(r[4]),
                }
                for r in rows
            ]

    def get_stats(self) -> dict:
        """Get persistence statistics."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM workflows").fetchone()[0]
            successful = conn.execute(
                "SELECT COUNT(*) FROM workflows WHERE success = 1"
            ).fetchone()[0]
            events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            return {
                "total_workflows": total,
                "successful_workflows": successful,
                "failed_workflows": total - successful,
                "total_events": events,
                "db_path": self.db_path,
            }

    def _workflow_to_dict(self, result: WorkflowResult) -> dict:
        """Convert WorkflowResult to dict."""
        return {
            "workflow_id": result.workflow_id,
            "success": result.success,
            "steps": [
                {
                    "name": s.name,
                    "status": s.status,
                    "result": s.result,
                    "started_at": s.started_at,
                    "completed_at": s.completed_at,
                }
                for s in result.steps
            ],
            "law_validation": {
                "passed": result.law_validation.passed,
                "collapse_risk": result.law_validation.collapse_risk,
            }
            if result.law_validation
            else None,
            "drift_detected": result.drift_detected,
            "repairs_proposed": result.repairs_proposed,
        }


def get_store(db_path: Optional[str] = None) -> KernelStore:
    """Factory for kernel store."""
    return KernelStore(db_path)
