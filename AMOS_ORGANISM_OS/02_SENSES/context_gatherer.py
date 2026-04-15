"""Context Gatherer — Environment context for AMOS."""

from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ContextSnapshot:
    """A snapshot of environment context."""

    timestamp: str
    cwd: str
    python_version: str
    platform: str
    env_vars: dict[str, str]
    shell: str
    user: str
    hostname: str


class ContextGatherer:
    """Gathers environment context for decision making."""

    def __init__(self):
        self._history: list[ContextSnapshot] = []
        self._sensitive_keys = ["KEY", "SECRET", "TOKEN", "PASSWORD", "API"]

    def gather(self) -> ContextSnapshot:
        """Gather current environment context."""
        # Filter sensitive env vars
        safe_env = {}
        for key, value in os.environ.items():
            if any(s in key.upper() for s in self._sensitive_keys):
                safe_env[key] = "***REDACTED***"
            else:
                safe_env[key] = value

        snapshot = ContextSnapshot(
            timestamp=datetime.utcnow().isoformat(),
            cwd=os.getcwd(),
            python_version=platform.python_version(),
            platform=platform.platform(),
            env_vars=safe_env,
            shell=os.environ.get("SHELL", "unknown"),
            user=os.environ.get("USER", "unknown"),
            hostname=platform.node(),
        )

        self._history.append(snapshot)
        # Keep last 100 snapshots
        if len(self._history) > 100:
            self._history = self._history[-100:]

        return snapshot

    def get_relevant_context(self, task: str) -> dict[str, Any]:
        """Get context relevant to a specific task."""
        ctx = self.gather()

        # Task-specific context filtering
        context = {
            "cwd": ctx.cwd,
            "platform": ctx.platform,
            "python_version": ctx.python_version,
            "user": ctx.user,
        }

        if "python" in task.lower() or "pip" in task.lower():
            context["python_path"] = ctx.env_vars.get("PYTHONPATH", "")
            context["virtual_env"] = ctx.env_vars.get("VIRTUAL_ENV", "")

        if "git" in task.lower():
            context["git_info"] = self._get_git_info()

        if "path" in task.lower() or "file" in task.lower():
            context["path"] = ctx.env_vars.get("PATH", "")

        return context

    def _get_git_info(self) -> dict[str, str]:
        """Get git information if available."""
        try:
            import subprocess

            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            commit = result.stdout.strip() if result.returncode == 0 else "unknown"

            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            remote = result.stdout.strip() if result.returncode == 0 else "unknown"

            return {"commit": commit, "remote": remote}
        except Exception:
            return {"commit": "unknown", "remote": "unknown"}

    def status(self) -> dict[str, Any]:
        """Get gatherer status."""
        return {
            "snapshots_stored": len(self._history),
            "last_snapshot": self._history[-1].timestamp if self._history else None,
        }
