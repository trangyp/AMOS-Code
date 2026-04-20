#!/usr/bin/env python3
"""Axiom One - Workflow Persistence Layer.

Real SQLite-based persistence for:
- Workflows
- Tasks
- Agent actions
- Audit logs

Integrates with agent fleet for durable state.
"""

import json
import logging
import sqlite3
import threading
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowPersistence:
    """SQLite persistence for agent workflows."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path.home() / ".axiom_one" / "workflows.db")

        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS workflows (
                    workflow_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    results TEXT
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    description TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    input_data TEXT,
                    output_data TEXT,
                    error TEXT,
                    quality_score REAL,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id)
                );

                CREATE TABLE IF NOT EXISTS agent_actions (
                    action_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    input_snapshot TEXT,
                    output_snapshot TEXT,
                    duration_ms INTEGER,
                    timestamp TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_tasks_workflow
                    ON tasks(workflow_id);
                CREATE INDEX IF NOT EXISTS idx_actions_agent
                    ON agent_actions(agent_id);
                CREATE INDEX IF NOT EXISTS idx_actions_task
                    ON agent_actions(task_id);
            """)
            conn.commit()

        logger.info(f"Database initialized: {self.db_path}")

    def save_workflow(self, workflow: Any) -> None:
        """Save workflow to database."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO workflows
                    (workflow_id, name, description, status, created_at, completed_at, results)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        workflow.workflow_id,
                        workflow.name,
                        workflow.description,
                        workflow.status.value,
                        workflow.created_at,
                        workflow.completed_at,
                        json.dumps(workflow.results) if workflow.results else None,
                    ),
                )
                conn.commit()

    def save_task(self, task: Any) -> None:
        """Save task to database."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO tasks
                    (task_id, workflow_id, description, agent_type, priority, status,
                     input_data, output_data, error, quality_score, created_at, started_at, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task.task_id,
                        task.parent_workflow_id if hasattr(task, "parent_workflow_id") else None,
                        task.description,
                        task.agent_type.value,
                        task.priority.value,
                        task.status.value,
                        json.dumps(task.input_data),
                        json.dumps(task.output) if task.output else None,
                        task.error,
                        task.quality_score,
                        task.created_at,
                        task.started_at,
                        task.completed_at,
                    ),
                )
                conn.commit()

    def save_action(self, action: Any) -> None:
        """Save agent action to database."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO agent_actions
                    (action_id, agent_id, task_id, action_type, input_snapshot,
                     output_snapshot, duration_ms, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        action.action_id,
                        action.agent_id,
                        action.task_id,
                        action.action_type,
                        json.dumps(action.input_snapshot),
                        json.dumps(action.output_snapshot),
                        action.duration_ms,
                        action.timestamp,
                    ),
                )
                conn.commit()

    def get_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Get workflow by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM workflows WHERE workflow_id = ?", (workflow_id,)
            ).fetchone()

            if row:
                return dict(row)
            return None

    def get_workflow_tasks(self, workflow_id: str) -> list[dict[str, Any]]:
        """Get all tasks for a workflow."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM tasks WHERE workflow_id = ? ORDER BY created_at", (workflow_id,)
            ).fetchall()

            return [dict(row) for row in rows]

    def list_workflows(self, limit: int = 100) -> list[dict[str, Any]]:
        """List recent workflows."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM workflows
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

            return [dict(row) for row in rows]

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            workflow_count = conn.execute("SELECT COUNT(*) FROM workflows").fetchone()[0]

            task_count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

            action_count = conn.execute("SELECT COUNT(*) FROM agent_actions").fetchone()[0]

            status_breakdown = conn.execute(
                "SELECT status, COUNT(*) FROM workflows GROUP BY status"
            ).fetchall()

            return {
                "workflows": workflow_count,
                "tasks": task_count,
                "actions": action_count,
                "status_breakdown": {status: count for status, count in status_breakdown},
                "database_path": self.db_path,
            }

    def export_to_json(self, output_path: str) -> None:
        """Export all data to JSON."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            workflows = conn.execute("SELECT * FROM workflows").fetchall()
            tasks = conn.execute("SELECT * FROM tasks").fetchall()
            actions = conn.execute("SELECT * FROM agent_actions").fetchall()

            data = {
                "workflows": [dict(row) for row in workflows],
                "tasks": [dict(row) for row in tasks],
                "actions": [dict(row) for row in actions],
                "exported_at": datetime.now(UTC).isoformat(),
            }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported to {output_path}")


class PersistedAxiomFleet:
    """Agent fleet with SQLite persistence."""

    def __init__(self, db_path: str = None):
        from axiom_one_agent_fleet import AxiomOneAgentFleet

        self.fleet = AxiomOneAgentFleet()
        self.persistence = WorkflowPersistence(db_path)
        self._persist_actions = True

    def create_workflow(self, name: str, description: str = "", require_approval: bool = False):
        """Create and persist workflow."""
        workflow = self.fleet.create_workflow(name, description, require_approval)
        self.persistence.save_workflow(workflow)
        return workflow

    def assign_task(
        self, workflow, agent_type, description: str, input_data: dict, priority: str = "normal"
    ):
        """Assign and persist task."""
        task = self.fleet.assign_task(workflow, agent_type, description, input_data, priority)

        # Link task to workflow
        task.parent_workflow_id = workflow.workflow_id
        self.persistence.save_task(task)

        return task

    def execute(self, workflow):
        """Execute workflow with persistence."""
        # Update workflow status
        workflow.status = (
            self.fleet.workflow_engine.AgentStatus.EXECUTING
            if hasattr(self.fleet.workflow_engine, "AgentStatus")
            else None
        )
        self.persistence.save_workflow(workflow)

        # Execute
        result = self.fleet.execute(workflow)

        # Save results
        for task_id, task in workflow.tasks.items():
            self.persistence.save_task(task)

        self.persistence.save_workflow(workflow)

        # Save actions if available
        if self._persist_actions and hasattr(self.fleet.agent_executor, "audit_log"):
            for action in self.fleet.agent_executor.audit_log:
                self.persistence.save_action(action)

        return result

    def get_workflow_history(self, workflow_id: str) -> dict[str, Any]:
        """Get workflow with task history."""
        workflow = self.persistence.get_workflow(workflow_id)
        if not workflow:
            return None

        tasks = self.persistence.get_workflow_tasks(workflow_id)
        return {"workflow": workflow, "tasks": tasks}

    def list_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """List workflow history."""
        return self.persistence.list_workflows(limit)

    def get_stats(self) -> dict[str, Any]:
        """Get persistence statistics."""
        return self.persistence.get_stats()


def demo_persistence():
    """Demonstrate persistence features."""
    print("=" * 70)
    print("AXIOM ONE WORKFLOW PERSISTENCE")
    print("=" * 70)

    from axiom_one_agent_fleet import AgentType

    # Create persisted fleet
    fleet = PersistedAxiomFleet()

    # Show initial stats
    print("\n📊 Initial Stats:")
    stats = fleet.get_stats()
    print(f"  Workflows: {stats['workflows']}")
    print(f"  Tasks: {stats['tasks']}")
    print(f"  Actions: {stats['actions']}")

    # Create workflow
    print("\n🔧 Creating workflow...")
    workflow = fleet.create_workflow(
        name="persistence_demo", description="Demonstrate workflow persistence"
    )
    print(f"  Workflow ID: {workflow.workflow_id[:8]}...")

    # Assign tasks
    print("\n📋 Assigning tasks...")
    task1 = fleet.assign_task(
        workflow=workflow,
        agent_type=AgentType.RESEARCHER,
        description="Explore codebase",
        input_data={"query": "main", "path": "."},
        priority="high",
    )
    print(f"  Task 1: {task1.task_id[:8]}...")

    task2 = fleet.assign_task(
        workflow=workflow,
        agent_type=AgentType.ARCHITECT,
        description="Analyze architecture",
        input_data={"path": "."},
        priority="normal",
    )
    print(f"  Task 2: {task2.task_id[:8]}...")

    # Execute
    print("\n⚡ Executing workflow...")
    result = fleet.execute(workflow)
    print(f"  Status: {result['status']}")
    print(f"  Tasks completed: {result['tasks_completed']}")

    # Show updated stats
    print("\n📊 Updated Stats:")
    stats = fleet.get_stats()
    print(f"  Workflows: {stats['workflows']}")
    print(f"  Tasks: {stats['tasks']}")
    print(f"  Actions: {stats['actions']}")

    # Retrieve workflow history
    print("\n📜 Workflow History:")
    history = fleet.get_workflow_history(workflow.workflow_id)
    if history:
        print(f"  Workflow: {history['workflow']['name']}")
        print(f"  Tasks: {len(history['tasks'])}")
        for task in history["tasks"]:
            print(f"    - {task['description'][:30]}... ({task['status']})")

    # List all workflows
    print("\n📋 All Workflows:")
    workflows = fleet.list_history(limit=5)
    for wf in workflows:
        print(f"  • {wf['name']} - {wf['status']} - {wf['created_at'][:19]}")

    # Export to JSON
    export_path = ".axiom_workflows_export.json"
    fleet.persistence.export_to_json(export_path)
    print(f"\n💾 Exported to {export_path}")

    print("\n" + "=" * 70)
    print("PERSISTENCE DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo_persistence()
