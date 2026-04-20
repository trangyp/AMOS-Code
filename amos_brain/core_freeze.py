#!/usr/bin/env python3
"""CoreFreezeEnforcer - Permanent Core File Protection.

LAW 5 COMPLIANCE: Core files are frozen against mutation.
Only core-protected agents can mutate core files.
Normal agents are denied mutation access.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

# Python 3.9 compatibility
UTC = timezone.utc
from pathlib import Path
from threading import Lock
from typing import Any


@dataclass
class CoreFile:
    """Represents a frozen core file."""

    path: str
    hash: str
    frozen_at: str
    allowed_mutators: list[str]


class CoreFreezeEnforcer:
    """Enforces permanent freeze on core files.

    Core files implementing the SuperBrain cannot be mutated
    by normal agents. Only explicitly authorized agents can
    modify core files, and all mutations are audited.

    CORE FILES PROTECTED:
    - super_brain.py (BrainRuntime)
    - kernel_router.py (Kernel/Router)
    - action_gate.py (ActionGate)
    - model_router.py (ModelRouter)
    - tool_registry_governed.py (ToolRegistry)
    - source_registry.py (SourceRegistry)
    - memory_governance.py (MemoryGovernance)
    - clawd_integration.py (ClawdIntegration)
    """

    CORE_FILES = [
        "super_brain.py",
        "kernel_router.py",
        "action_gate.py",
        "model_router.py",
        "tool_registry_governed.py",
        "source_registry.py",
        "memory_governance.py",
        "clawd_integration.py",
        "core_freeze.py",
    ]

    CORE_AGENTS = ["SUPER_BRAIN", "CORE_ADMIN", "SYSTEM"]

    def __init__(self):
        self._frozen_files: dict[str, CoreFile] = {}
        self._lock = Lock()
        self._frozen = False
        self._audit_log: list[dict[str, Any]] = []

    def freeze_core_files(self) -> bool:
        """Freeze all core files.

        Computes hashes of core files and marks them as frozen.
        Any subsequent mutation must be authorized.

        Returns:
            True if freeze successful
        """
        with self._lock:
            core_dir = Path(__file__).parent

            for filename in self.CORE_FILES:
                filepath = core_dir / filename
                if filepath.exists():
                    file_hash = self._compute_file_hash(filepath)
                    self._frozen_files[filename] = CoreFile(
                        path=str(filepath),
                        hash=file_hash,
                        frozen_at=datetime.now(timezone.utc).isoformat(),
                        allowed_mutators=self.CORE_AGENTS.copy(),
                    )

            self._frozen = True

        self._audit(
            "CORE_FREEZE_INIT",
            {
                "files_frozen": len(self._frozen_files),
                "frozen_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        return True

    def _compute_file_hash(self, filepath: Path) -> str:
        """Compute SHA-256 hash of file contents."""
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]

    def can_mutate(self, agent_id: str) -> bool:
        """Check if agent can mutate core files.

        LAW 5 COMPLIANCE: Only core-protected agents can mutate.
        Normal agents are denied.

        Args:
            agent_id: Agent to check

        Returns:
            True only if agent has core mutation permission
        """
        if not self._frozen:
            return True  # Not frozen yet

        if not agent_id:
            return False  # Anonymous agents denied

        # Check if agent is in core agents list
        is_core = any(core in agent_id.upper() for core in self.CORE_AGENTS)

        return is_core

    def check_mutation(self, filepath: str, agent_id: str) -> dict[str, Any]:
        """Check if mutation is allowed and audit it.

        Args:
            filepath: Path to file being mutated
            agent_id: Agent attempting mutation

        Returns:
            Result dict with allowed status
        """
        filename = Path(filepath).name

        # Check if this is a core file
        if filename not in self.CORE_FILES:
            # Not a core file, allow mutation
            return {"allowed": True, "reason": "not_core_file"}

        # Check if agent can mutate
        allowed = self.can_mutate(agent_id)

        # Audit the mutation attempt
        self._audit(
            "MUTATION_ATTEMPT",
            {
                "file": filename,
                "agent_id": agent_id,
                "allowed": allowed,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        if not allowed:
            return {
                "allowed": False,
                "reason": "core_file_frozen",
                "file": filename,
                "agent_id": agent_id,
                "message": f"Agent {agent_id} cannot mutate core file {filename}",
            }

        return {
            "allowed": True,
            "reason": "core_agent_authorized",
            "file": filename,
            "agent_id": agent_id,
        }

    def verify_integrity(self) -> dict[str, Any]:
        """Verify integrity of all frozen core files.

        Returns:
            Integrity check results
        """
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "files_checked": 0,
            "files_modified": [],
            "files_missing": [],
        }

        with self._lock:
            for filename, core_file in self._frozen_files.items():
                filepath = Path(core_file.path)

                if not filepath.exists():
                    results["files_missing"].append(filename)
                    continue

                current_hash = self._compute_file_hash(filepath)
                results["files_checked"] += 1

                if current_hash != core_file.hash:
                    results["files_modified"].append(
                        {
                            "file": filename,
                            "expected_hash": core_file.hash,
                            "actual_hash": current_hash,
                        }
                    )

        return results

    def is_frozen(self) -> bool:
        """Check if core files are frozen."""
        return self._frozen

    def get_frozen_files(self) -> list[str]:
        """Get list of frozen core files."""
        with self._lock:
            return list(self._frozen_files.keys())

    def _audit(self, action: str, details: dict[str, Any]) -> None:
        """Record audit entry."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "details": details,
        }
        self._audit_log.append(entry)

    def is_healthy(self) -> bool:
        """Check if freeze enforcer is healthy."""
        return self._frozen and len(self._frozen_files) > 0

    def shutdown(self) -> None:
        """Graceful shutdown."""
        pass
