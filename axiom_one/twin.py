#!/usr/bin/env python3
"""AXIOM One Twin - Digital Twin of Codebase and Runtime

Tracks repo graph, runtime graph, schema graph, incident graph.
Enables environment replay and failure reproduction.
Author: AMOS System
Version: 3.0.0
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class RepoGraph:
    """Graph representation of repository."""

    files: dict[str, dict[str, Any]] = field(default_factory=dict)
    imports: dict[str, list[str]] = field(default_factory=dict)
    dependencies: dict[str, list[str]] = field(default_factory=dict)

    def add_file(self, path: str, content_hash: str, size: int, imports: list[str]) -> None:
        self.files[path] = {"hash": content_hash, "size": size}
        self.imports[path] = imports


@dataclass
class RuntimeGraph:
    """Graph representation of runtime state."""

    services: dict[str, dict[str, Any]] = field(default_factory=dict)
    endpoints: list[dict[str, Any]] = field(default_factory=list)
    databases: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class EnvironmentState:
    """Capturable environment state."""

    repo_graph: RepoGraph = field(default_factory=RepoGraph)
    runtime_graph: RuntimeGraph = field(default_factory=RuntimeGraph)
    env_vars: Dict[str, str] = field(default_factory=dict)
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def compute_signature(self) -> str:
        """Compute unique signature for this state."""
        data = json.dumps(
            {
                "files": list(self.repo_graph.files.keys()),
                "services": list(self.runtime_graph.services.keys()),
            },
            sort_keys=True,
        )
        return hashlib.sha256(data.encode()).hexdigest()[:16]


class Twin:
    """Digital twin of codebase and runtime."""

    def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path or Path.cwd()
        self._states: Dict[str, EnvironmentState] = {}
        self._incidents: list[dict[str, Any]] = []

    def capture_state(self, label: str = None) -> EnvironmentState:
        """Capture current environment state."""
        state = EnvironmentState()

        # Capture repo files using os.walk for efficient scanning
        exclude_dirs = {
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
        }
        max_file_size = 5 * 1024 * 1024  # 5MB limit

        for root, dirs, files in os.walk(self.repo_path):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(self.repo_path))

                try:
                    # Check file size before reading
                    stat = file_path.stat()
                    if stat.st_size > max_file_size:
                        continue  # Skip large files

                    # Read file content for hashing
                    content = file_path.read_bytes()
                    state.repo_graph.add_file(
                        rel_path,
                        hashlib.sha256(content).hexdigest()[:16],
                        len(content),
                        [],
                    )
                except OSError:
                    # Skip files we can't read
                    pass

        signature = state.compute_signature()
        label = label or f"state_{signature}"
        self._states[label] = state

        return state

    def replay_failure(self, state_label: str) -> Optional[EnvironmentState]:
        """Replay a captured failure state."""
        return self._states.get(state_label)

    def compare_states(self, state_a: str, state_b: str) -> Dict[str, Any]:
        """Compare two environment states."""
        a = self._states.get(state_a)
        b = self._states.get(state_b)

        if not a or not b:
            return {"error": "State not found"}

        files_a = set(a.repo_graph.files.keys())
        files_b = set(b.repo_graph.files.keys())

        return {
            "added_files": list(files_b - files_a),
            "removed_files": list(files_a - files_b),
            "common_files": list(files_a & files_b),
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="AXIOM One Twin")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--capture", help="Capture state with label")
    parser.add_argument("--compare", nargs=2, metavar=("A", "B"), help="Compare two states")
    args = parser.parse_args()

    twin = Twin(args.repo)

    if args.capture:
        state = twin.capture_state(args.capture)
        print(f"Captured state: {args.capture}")
        print(f"Signature: {state.compute_signature()}")
        print(f"Files: {len(state.repo_graph.files)}")
    elif args.compare:
        diff = twin.compare_states(args.compare[0], args.compare[1])
        print(json.dumps(diff, indent=2))
    else:
        print("AXIOM One Twin - Environment Replay System")


if __name__ == "__main__":
    main()
