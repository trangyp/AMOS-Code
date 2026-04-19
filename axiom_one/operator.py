#!/usr/bin/env python3
"""AXIOM One Operator - Local-First Developer Surface
====================================================

Beats Claude Code on:
- Terminal-native speed (no latency to cloud)
- Editor-native integration (VS Code, vim, emacs)
- Scriptability (composable Unix-style workflows)
- Local model support (no API keys needed)
- Branch-aware operations
- Policy-aware from the start

The Operator is the local execution mode of AXIOM One.
It lives inside your terminal and editor, not in a browser.

Author: AMOS System
Version: 3.0.0
"""

from __future__ import annotations


import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .execution_slot import (
    ExecutionSlot,
    ExecutionSlotManager,
    SlotBudget,
    SlotMode,
    ToolPermissions,
)


@dataclass
class OperatorConfig:
    """Configuration for the Operator."""

    repo_path: Path = field(default_factory=Path.cwd)
    editor: str = "vscode"  # vscode, vim, emacs, cursor
    terminal: str = "native"  # native, tmux, screen
    local_model: str = None  # ollama, llamafile, etc
    mcp_servers: list[str] = field(default_factory=list)
    auto_commit: bool = False
    policy_checks: bool = True
    verbose: bool = False


class Operator:
    """
    Local-first developer surface for AXIOM One.

    This is the equivalent of Claude Code, but:
    - Faster (no network round-trips)
    - More integrated (native to your editor)
    - More scriptable (composable)
    - Works offline (local models supported)
    """

    def __init__(self, config: OperatorConfig | None = None):
        self.config = config or OperatorConfig()
        self.slot_manager = ExecutionSlotManager()
        self._current_slot: ExecutionSlot | None = None
        self._tool_registry: dict[str, Any] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register default Operator tools."""
        self._tool_registry = {
            "read": self._tool_read,
            "write": self._tool_write,
            "edit": self._tool_edit,
            "bash": self._tool_bash,
            "grep": self._tool_grep,
            "glob": self._tool_glob,
            "git": self._tool_git,
            "test": self._tool_test,
            "lint": self._tool_lint,
        }

    def start_session(self, objective: str, **kwargs) -> ExecutionSlot:
        """Start a new Operator session (local slot)."""
        slot = ExecutionSlot.create_local(
            objective=objective,
            repo_path=self.config.repo_path,
            tool_permissions=ToolPermissions(
                read=True,
                write=True,
                execute=True,
                bash=True,
                web=True,
                mcp_servers=self.config.mcp_servers,
            ),
            budget=SlotBudget(
                max_time_seconds=600,
                max_cost_usd=0.0,  # Local = free
            ),
            **kwargs,
        )
        slot.mode = SlotMode.LOCAL
        self.slot_manager.allocate(slot)
        self._current_slot = slot
        return slot

    def execute_tool(self, tool_name: str, **params) -> dict[str, Any]:
        """Execute a tool in the current session."""
        if self._current_slot is None:
            raise RuntimeError("No active session. Call start_session() first.")

        # Check permissions
        if not self._current_slot.tool_permissions.can_use_tool(tool_name):
            return {"success": False, "error": f"Tool '{tool_name}' not permitted in this session"}

        # Log the tool call
        self._current_slot.log_event(
            "tool_call",
            tool=tool_name,
            params=params,
        )

        # Execute
        handler = self._tool_registry.get(tool_name)
        if handler is None:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        try:
            result = handler(**params)
            self._current_slot.budget.used_tool_calls += 1

            # Log result
            self._current_slot.log_event(
                "tool_result",
                tool=tool_name,
                success=result.get("success", False),
            )

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Tool implementations
    def _tool_read(self, path: str, offset: int = 0, limit: int = None) -> dict[str, Any]:
        """Read a file."""
        try:
            full_path = self.config.repo_path / path
            content = full_path.read_text()
            lines = content.splitlines()

            if offset or limit:
                lines = lines[offset : offset + limit] if limit else lines[offset:]
                content = "\n".join(lines)

            return {
                "success": True,
                "content": content,
                "lines": len(content.splitlines()),
                "path": str(full_path),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_write(self, path: str, content: str) -> dict[str, Any]:
        """Write a file."""
        try:
            full_path = self.config.repo_path / path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Track for rollback
            if full_path.exists():
                self._current_slot.rollback_path.modified_files.append(path)
            else:
                self._current_slot.rollback_path.created_files.append(path)

            full_path.write_text(content)
            self._current_slot.budget.used_file_changes += 1

            return {"success": True, "path": str(full_path), "bytes": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_edit(self, path: str, old_string: str, new_string: str) -> dict[str, Any]:
        """Edit a file by replacing old_string with new_string."""
        try:
            full_path = self.config.repo_path / path
            content = full_path.read_text()

            if old_string not in content:
                return {"success": False, "error": "old_string not found in file"}

            # Track for rollback
            if path not in self._current_slot.rollback_path.modified_files:
                self._current_slot.rollback_path.modified_files.append(path)

            new_content = content.replace(old_string, new_string, 1)
            full_path.write_text(new_content)
            self._current_slot.budget.used_file_changes += 1

            return {"success": True, "path": str(full_path), "replaced": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_bash(self, command: str, timeout: int = 30) -> dict[str, Any]:
        """Execute a bash command."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.config.repo_path,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_grep(self, pattern: str, path: str = ".", glob: str = "*") -> dict[str, Any]:
        """Search for pattern in files."""
        try:
            import fnmatch
            import re

            matches = []
            search_path = self.config.repo_path / path

            # Use os.walk with directory pruning for efficient scanning
            exclude_dirs = {
                ".venv",
                "__pycache__",
                ".git",
                "node_modules",
                ".pytest_cache",
                ".mypy_cache",
                ".ruff_cache",
            }
            max_file_size = 1024 * 1024  # 1MB limit

            for root, dirs, files in os.walk(search_path):
                # Prune excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]

                for file in files:
                    # Check glob pattern match
                    if not fnmatch.fnmatch(file, glob):
                        continue

                    file_path = Path(root) / file

                    try:
                        # Check file size before reading
                        stat = file_path.stat()
                        if stat.st_size > max_file_size:
                            continue  # Skip large files

                        content = file_path.read_text(errors="ignore")
                        for i, line in enumerate(content.splitlines(), 1):
                            if re.search(pattern, line):
                                matches.append(
                                    {
                                        "path": str(file_path.relative_to(self.config.repo_path)),
                                        "line": i,
                                        "content": line[:100],
                                    }
                                )
                    except Exception:
                        pass

            return {"success": True, "matches": matches, "count": len(matches)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_glob(self, pattern: str, path: str = ".") -> dict[str, Any]:
        """Find files matching pattern."""
        try:
            search_path = self.config.repo_path / path
            matches = list(search_path.rglob(pattern))

            return {
                "success": True,
                "files": [str(p.relative_to(self.config.repo_path)) for p in matches],
                "count": len(matches),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_git(self, command: str) -> dict[str, Any]:
        """Execute git command."""
        return self._tool_bash(f"git {command}")

    def _tool_test(self, test_path: str = None) -> dict[str, Any]:
        """Run tests."""
        if test_path:
            return self._tool_bash(f"python -m pytest {test_path} -v")
        return self._tool_bash("python -m pytest -v")

    def _tool_lint(self, path: str = ".") -> dict[str, Any]:
        """Run linter."""
        return self._tool_bash(f"python -m ruff check {path}")

    def complete_session(
        self, success: bool, result: dict[str, Any] = None
    ) -> ExecutionSlot | None:
        """Complete the current session."""
        if self._current_slot is None:
            return None

        slot = self.slot_manager.complete(self._current_slot.slot_id, success, result)
        self._current_slot = None
        return slot

    def get_status(self) -> dict[str, Any]:
        """Get current Operator status."""
        active_slots = self.slot_manager.list_active()
        return {
            "repo": str(self.config.repo_path),
            "editor": self.config.editor,
            "active_sessions": len(active_slots),
            "current_session": self._current_slot.slot_id if self._current_slot else None,
            "tools_available": list(self._tool_registry.keys()),
        }


# CLI interface
def main():
    """CLI entry point for Operator."""
    import argparse

    parser = argparse.ArgumentParser(description="AXIOM One Operator")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository path")
    parser.add_argument("--editor", default="vscode", help="Editor integration")
    parser.add_argument("--start", help="Start a session with objective")
    parser.add_argument("--tool", help="Execute tool")
    parser.add_argument("--status", action="store_true", help="Show status")

    args = parser.parse_args()

    config = OperatorConfig(
        repo_path=args.repo,
        editor=args.editor,
    )
    operator = Operator(config)

    if args.status:
        print(operator.get_status())
    elif args.start:
        slot = operator.start_session(args.start)
        print(f"Started session: {slot.slot_id}")
    elif args.tool:
        result = operator.execute_tool(args.tool)
        print(result)
    else:
        print("AXIOM One Operator - Local Developer Surface")
        print(f"Repo: {config.repo_path}")
        print("Use --start 'objective' to begin")


if __name__ == "__main__":
    main()
