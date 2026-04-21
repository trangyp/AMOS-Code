#!/usr/bin/env python3
"""AXIOM One Execution Slot - Core Primitive
============================================

The Execution Slot is the fundamental unit of work in AXIOM One.
It replaces "conversation" as the core primitive with a structured,
reproducible, verifiable execution context.

Required Fields:
- repo_snapshot: Git state, file hashes, dependencies
- environment_snapshot: Env vars, feature flags, secrets hash
- tool_permissions: What tools this slot can use
- budget: Time, cost, token limits
- objective: Clear goal with success criteria
- acceptance_tests: How to verify success
- rollback_path: How to undo if needed
- event_log: Immutable history of actions

Author: AMOS System
Version: 3.0.0
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone, timezone

UTC = UTC

from enum import Enum, auto
from pathlib import Path
from typing import Any


class SlotStatus(Enum):
    """Status of an execution slot."""

    PENDING = auto()
    ALLOCATED = auto()
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()
    FAILED = auto()
    ROLLED_BACK = auto()
    CANCELLED = auto()


class SlotMode(Enum):
    """Operating mode for the slot."""

    LOCAL = "local"  # Like Claude Code - terminal/editor native
    MANAGED = "managed"  # Like Devin - isolated workspace
    ORCHESTRATION = "orch"  # Supervisor managing sub-slots


@dataclass
class RepoSnapshot:
    """Immutable capture of repository state."""

    repo_path: Path
    git_commit: str
    git_branch: str
    file_hashes: dict[str, str] = field(default_factory=dict)
    dirty_files: list[str] = field(default_factory=list)
    remotes: dict[str, str] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def compute_hash(self) -> str:
        """Compute deterministic hash of this snapshot."""
        data = {
            "commit": self.git_commit,
            "branch": self.git_branch,
            "files": self.file_hashes,
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


@dataclass
class EnvironmentSnapshot:
    """Capture of execution environment."""

    env_vars: dict[str, str] = field(default_factory=dict)
    feature_flags: dict[str, bool] = field(default_factory=dict)
    secrets_hash: str = ""  # Hash only, not actual secrets
    python_version: str = ""
    dependencies: dict[str, str] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def capture_current(cls, mask_secrets: bool = True) -> EnvironmentSnapshot:
        """Capture current environment."""
        import os
        import sys

        env_vars = dict(os.environ)
        if mask_secrets:
            # Hash sensitive values
            secrets_hash = hashlib.sha256(
                json.dumps(env_vars, sort_keys=True).encode()
            ).hexdigest()[:16]
            env_vars = {k: "***" for k in env_vars}
        else:
            secrets_hash = ""

        return cls(
            env_vars=env_vars,
            secrets_hash=secrets_hash,
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        )


@dataclass
class ToolPermissions:
    """What tools this slot is allowed to use."""

    read: bool = True
    write: bool = True
    execute: bool = True
    bash: bool = True
    web: bool = True
    mcp_servers: list[str] = field(default_factory=list)
    allowed_paths: list[str] = field(default_factory=list)
    blocked_paths: list[str] = field(default_factory=list)

    def can_use_tool(self, tool_name: str) -> bool:
        """Check if a specific tool is allowed."""
        tool_map = {
            "read": self.read,
            "write": self.write,
            "execute": self.execute,
            "bash": self.bash,
            "web": self.web,
        }
        return tool_map.get(tool_name, False)


@dataclass
class SlotBudget:
    """Resource budget for this slot."""

    max_time_seconds: float = 300.0
    max_cost_usd: float = 1.0
    max_tokens: int = 100000
    max_tool_calls: int = 100
    max_file_changes: int = 50

    used_time_seconds: float = 0.0
    used_cost_usd: float = 0.0
    used_tokens: int = 0
    used_tool_calls: int = 0
    used_file_changes: int = 0

    def is_exceeded(self) -> bool:
        """Check if any budget limit is exceeded."""
        return (
            self.used_time_seconds >= self.max_time_seconds
            or self.used_cost_usd >= self.max_cost_usd
            or self.used_tokens >= self.max_tokens
            or self.used_tool_calls >= self.max_tool_calls
            or self.used_file_changes >= self.max_file_changes
        )

    def remaining_pct(self) -> dict[str, float]:
        """Return remaining budget percentages."""
        return {
            "time": max(
                0, (self.max_time_seconds - self.used_time_seconds) / self.max_time_seconds * 100
            ),
            "cost": max(0, (self.max_cost_usd - self.used_cost_usd) / self.max_cost_usd * 100),
            "tokens": max(0, (self.max_tokens - self.used_tokens) / self.max_tokens * 100),
            "tool_calls": max(
                0, (self.max_tool_calls - self.used_tool_calls) / self.max_tool_calls * 100
            ),
        }


@dataclass
class AcceptanceCriteria:
    """Criteria for accepting the slot's output."""

    tests_must_pass: list[str] = field(default_factory=list)
    lint_must_pass: bool = True
    type_check_must_pass: bool = True
    security_scan_must_pass: bool = True
    performance_regression_threshold: float = 0.1  # 10% max regression
    min_code_coverage: float = 0.0
    required_reviews: int = 0

    def to_verification_bundle(self) -> dict[str, Any]:
        """Convert to verification bundle format."""
        return {
            "tests": self.tests_must_pass,
            "lint": self.lint_must_pass,
            "type_check": self.type_check_must_pass,
            "security_scan": self.security_scan_must_pass,
            "perf_threshold": self.performance_regression_threshold,
            "coverage": self.min_code_coverage,
            "reviews": self.required_reviews,
        }


@dataclass
class RollbackPath:
    """How to roll back this slot's changes if needed."""

    git_branch_before: str = ""
    git_commit_before: str = ""
    backup_paths: list[Path] = field(default_factory=list)
    created_files: list[str] = field(default_factory=list)
    modified_files: list[str] = field(default_factory=list)
    deleted_files: list[str] = field(default_factory=list)

    def can_rollback(self) -> bool:
        """Check if rollback is possible."""
        return bool(self.git_commit_before) or bool(self.backup_paths)


@dataclass
class SlotEvent:
    """Single event in the slot's event log."""

    timestamp: str
    event_type: str
    data: dict[str, Any] = field(default_factory=dict)
    tool_call: dict[str, Any] = None
    result: dict[str, Any] = None

    @classmethod
    def now(cls, event_type: str, **data) -> SlotEvent:
        """Create an event with current timestamp."""
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            data=data,
        )


@dataclass
class ExecutionSlot:
    """
    Core primitive: A reproducible, verifiable execution context.

    This is NOT a conversation. It is a structured execution environment
    with all context needed to reproduce, verify, and if needed, roll back
    any work performed.
    """

    # Identity
    slot_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    parent_slot_id: str = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Mode
    mode: SlotMode = SlotMode.LOCAL
    status: SlotStatus = SlotStatus.PENDING

    # Snapshots (immutable context)repo_snapshot: RepoSnapshot  =None
    environment_snapshot: EnvironmentSnapshot = None
    working_dir: Path = None

    # Configuration
    tool_permissions: ToolPermissions = field(default_factory=ToolPermissions)
    budget: SlotBudget = field(default_factory=SlotBudget)
    objective: dict[str, Any] = field(default_factory=dict)
    acceptance_criteria: AcceptanceCriteria = field(default_factory=AcceptanceCriteria)

    # State
    rollback_path: RollbackPath = field(default_factory=RollbackPath)
    event_log: list[SlotEvent] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)

    # Sub-slots (for ORCHESTRATION mode)
    child_slots: list[str] = field(default_factory=list)

    # Results
    completion_time: str = None
    verification_bundle: dict[str, Any] = None
    failure_reason: str = None

    def log_event(self, event_type: str, **data) -> None:
        """Add an event to the log."""
        self.event_log.append(SlotEvent.now(event_type, **data))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)

    @classmethod
    def create_local(cls, objective: str, repo_path: Path = None, **kwargs) -> ExecutionSlot:
        """Create a local-mode slot (Claude Code style)."""
        import subprocess

        repo_path = repo_path or Path.cwd()

        # Capture git state
        try:
            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=repo_path, text=True
            ).strip()
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path, text=True
            ).strip()
        except subprocess.CalledProcessError:
            commit = "unknown"
            branch = "unknown"

        return cls(
            mode=SlotMode.LOCAL,
            repo_snapshot=RepoSnapshot(
                repo_path=repo_path,
                git_commit=commit,
                git_branch=branch,
            ),
            environment_snapshot=EnvironmentSnapshot.capture_current(),
            objective={"description": objective, "success_criteria": []},
            **kwargs,
        )

    @classmethod
    def create_managed(cls, objective: str, repo_url: str, **kwargs) -> ExecutionSlot:
        """Create a managed-mode slot (Devin style)."""
        return cls(
            mode=SlotMode.MANAGED,
            repo_snapshot=RepoSnapshot(
                repo_path=Path("/workspace/repo"),
                git_commit="HEAD",
                git_branch="main",
                remotes={"origin": repo_url},
            ),
            environment_snapshot=EnvironmentSnapshot.capture_current(),
            objective={"description": objective, "success_criteria": []},
            **kwargs,
        )

    @classmethod
    def create_orchestration(
        cls, objective: str, child_objectives: list[str], **kwargs
    ) -> ExecutionSlot:
        """Create an orchestration-mode slot (supervisor)."""
        return cls(
            mode=SlotMode.ORCHESTRATION,
            objective={"description": objective, "subtasks": child_objectives},
            **kwargs,
        )


class ExecutionSlotManager:
    """Manages active execution slots."""

    def __init__(self):
        self._slots: dict[str, ExecutionSlot] = {}
        self._on_slot_complete: list[Callable[[ExecutionSlot], None]] = []

    def allocate(self, slot: ExecutionSlot) -> ExecutionSlot:
        """Allocate a new slot."""
        slot.status = SlotStatus.ALLOCATED
        self._slots[slot.slot_id] = slot
        slot.log_event("allocated", slot_id=slot.slot_id, mode=slot.mode.value)
        return slot

    def get(self, slot_id: str) -> ExecutionSlot:
        """Get a slot by ID."""
        return self._slots.get(slot_id)

    def start(self, slot_id: str) -> ExecutionSlot:
        """Mark a slot as running."""
        slot = self._slots.get(slot_id)
        if slot:
            slot.status = SlotStatus.RUNNING
            slot.log_event("started")
        return slot

    def complete(self, slot_id: str, success: bool, result: dict[str, Any] = None) -> ExecutionSlot:
        """Mark a slot as completed."""
        slot = self._slots.get(slot_id)
        if slot:
            slot.status = SlotStatus.COMPLETED if success else SlotStatus.FAILED
            slot.completion_time = datetime.now(timezone.utc).isoformat()
            slot.artifacts.update(result or {})
            slot.log_event("completed" if success else "failed", result=result)

            for callback in self._on_slot_complete:
                callback(slot)
        return slot

    def on_complete(self, callback: Callable[[ExecutionSlot], None]) -> None:
        """Register callback for slot completion."""
        self._on_slot_complete.append(callback)

    def list_active(self) -> list[ExecutionSlot]:
        """List all active slots."""
        return [
            slot
            for slot in self._slots.values()
            if slot.status in (SlotStatus.ALLOCATED, SlotStatus.RUNNING, SlotStatus.PAUSED)
        ]

    def rollback(self, slot_id: str) -> bool:
        """Roll back a slot's changes using git or file-level operations."""
        slot = self._slots.get(slot_id)
        if not slot or not slot.rollback_path.can_rollback():
            return False

        rollback_path = slot.rollback_path
        errors = []

        # Try git-based rollback first if available
        if rollback_path.git_commit_before:
            try:
                result = subprocess.run(
                    ["git", "reset", "--hard", rollback_path.git_commit_before],
                    capture_output=True,
                    text=True,
                    cwd=slot.working_dir if hasattr(slot, "working_dir") else None,
                    timeout=30,
                )
                if result.returncode == 0:
                    slot.status = SlotStatus.ROLLED_BACK
                    slot.log_event(
                        "rolled_back", {"method": "git", "commit": rollback_path.git_commit_before}
                    )
                    return True
                errors.append(f"Git rollback failed: {result.stderr}")
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
                errors.append(f"Git rollback error: {e}")

        # Fallback to file-level rollback
        # 1. Delete created files (in reverse order to handle directories)
        for file_path in reversed(rollback_path.created_files):
            try:
                full_path = Path(file_path)
                if full_path.exists():
                    if full_path.is_file():
                        full_path.unlink()
                    elif full_path.is_dir():
                        shutil.rmtree(full_path)
            except Exception as e:
                errors.append(f"Failed to delete created file {file_path}: {e}")

        # 2. Restore deleted files from backups
        for backup_path in rollback_path.backup_paths:
            try:
                if backup_path.exists():
                    # Extract original path from backup metadata
                    metadata_path = backup_path.with_suffix(backup_path.suffix + ".meta")
                    if metadata_path.exists():
                        meta = json.loads(metadata_path.read_text())
                        original_path = Path(meta.get("original_path", ""))
                        if original_path and not original_path.exists():
                            shutil.copy2(backup_path, original_path)
                            metadata_path.unlink(missing_ok=True)
            except Exception as e:
                errors.append(f"Failed to restore from backup {backup_path}: {e}")

        # 3. Restore modified files from git or backup
        for file_path in rollback_path.modified_files:
            try:
                full_path = Path(file_path)
                if full_path.exists():
                    # Try git checkout first
                    result = subprocess.run(
                        ["git", "checkout", "--", str(full_path)],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if result.returncode != 0:
                        errors.append(
                            f"Failed to restore modified file {file_path}: {result.stderr}"
                        )
            except Exception as e:
                errors.append(f"Error restoring modified file {file_path}: {e}")

        # Mark as rolled back even if there were some errors
        slot.status = SlotStatus.ROLLED_BACK
        slot.log_event(
            "rolled_back",
            {
                "method": "file_level",
                "errors": errors if errors else None,
                "success": len(errors) == 0,
            },
        )
        return len(errors) == 0


# Global slot manager instance
_slot_manager: ExecutionSlotManager = None


def get_slot_manager() -> ExecutionSlotManager:
    """Get global slot manager."""
    global _slot_manager
    if _slot_manager is None:
        _slot_manager = ExecutionSlotManager()
    return _slot_manager
