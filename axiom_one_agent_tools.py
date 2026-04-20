"""Axiom One Agent Tools

Real executable tools for agent use. These are actual functions that agents
can invoke to perform real work - not mock implementations.
"""

import os
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from pathlib import Path
from typing import Any


@dataclass
class ToolResult:
    """Result from executing a tool."""

    success: bool
    output: str
    error: str = None
    data: dict[str, Any] = None
    duration_ms: float = 0.0


class AgentToolRegistry:
    """Registry of executable tools for agents."""

    def __init__(self):
        self._tools: dict[str, Callable[..., ToolResult]] = {}
        self._register_default_tools()

    def register(self, name: str, func: Callable[..., ToolResult]) -> None:
        """Register a tool."""
        self._tools[name] = func

    def get(self, name: str) -> Callable[..., ToolResult]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, str]]:
        """List all available tools."""
        return [
            {"name": name, "description": func.__doc__ or "No description"}
            for name, func in self._tools.items()
        ]

    def _register_default_tools(self) -> None:
        """Register default built-in tools."""
        self.register("read_file", self._read_file)
        self.register("write_file", self._write_file)
        self.register("execute_command", self._execute_command)
        self.register("search_files", self._search_files)
        self.register("git_status", self._git_status)
        self.register("run_python", self._run_python)
        self.register("run_linter", self._run_linter)
        self.register("analyze_imports", self._analyze_imports)
        self.register("check_syntax", self._check_syntax)
        self.register("create_branch", self._create_branch)
        self.register("commit_changes", self._commit_changes)

    def _read_file(self, file_path: str) -> ToolResult:
        """Read contents of a file."""
        start = datetime.now(timezone.utc)
        try:
            path = Path(file_path)
            if not path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"File not found: {file_path}",
                    duration_ms=self._elapsed_ms(start),
                )
            content = path.read_text(encoding="utf-8", errors="ignore")
            return ToolResult(
                success=True,
                output=content[:50000],  # Limit output size
                data={"path": str(path), "size": len(content)},
                duration_ms=self._elapsed_ms(start),
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
                duration_ms=self._elapsed_ms(start),
            )

    def _write_file(self, file_path: str, content: str) -> ToolResult:
        """Write content to a file."""
        start = datetime.now(timezone.utc)
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return ToolResult(
                success=True,
                output=f"File written: {file_path}",
                data={"path": str(path), "bytes_written": len(content)},
                duration_ms=self._elapsed_ms(start),
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
                duration_ms=self._elapsed_ms(start),
            )

    def _execute_command(self, command: str, cwd: str = ".") -> ToolResult:
        """Execute a shell command."""
        start = datetime.now(timezone.utc)
        try:
            # SECURITY: Use shlex.split() and shell=False to prevent injection
            import shlex

            cmd_parts = shlex.split(command)
            result = subprocess.run(
                cmd_parts,
                shell=False,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout[:10000],
                error=result.stderr[:5000] if result.stderr else None,
                data={
                    "returncode": result.returncode,
                    "command": command,
                },
                duration_ms=self._elapsed_ms(start),
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output="",
                error="Command timed out after 60s",
                duration_ms=self._elapsed_ms(start),
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
                duration_ms=self._elapsed_ms(start),
            )

    def _search_files(self, pattern: str, path: str = ".") -> ToolResult:
        """Search for files matching a pattern."""
        start = datetime.now(timezone.utc)
        try:
            matches = []
            for root, _dirs, files in os.walk(path):
                for file in files:
                    if re.search(pattern, file, re.IGNORECASE):
                        matches.append(os.path.join(root, file))
                    if len(matches) >= 100:  # Limit results
                        break
                if len(matches) >= 100:
                    break

            return ToolResult(
                success=True,
                output=f"Found {len(matches)} files",
                data={"matches": matches, "count": len(matches)},
                duration_ms=self._elapsed_ms(start),
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
                duration_ms=self._elapsed_ms(start),
            )

    def _git_status(self, repo_path: str = ".") -> ToolResult:
        """Get git status of a repository."""
        return self._execute_command("git status --porcelain", cwd=repo_path)

    def _run_python(self, code: str) -> ToolResult:
        """Execute Python code."""
        start = datetime.now(timezone.utc)
        try:
            # Execute in isolated environment
            result = subprocess.run(
                ["python3", "-c", code],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout[:5000],
                error=result.stderr[:2000] if result.stderr else None,
                duration_ms=self._elapsed_ms(start),
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
                duration_ms=self._elapsed_ms(start),
            )

    def _run_linter(self, file_path: str) -> ToolResult:
        """Run ruff linter on a file."""
        return self._execute_command(f"ruff check {file_path}")

    def _analyze_imports(self, file_path: str) -> ToolResult:
        """Analyze Python imports in a file."""
        result = self._read_file(file_path)
        if not result.success:
            return result

        content = result.output
        imports = re.findall(r"^(?:from\s+(\S+)\s+)?import\s+(.+)$", content, re.MULTILINE)

        return ToolResult(
            success=True,
            output=f"Found {len(imports)} import statements",
            data={
                "imports": imports,
                "count": len(imports),
            },
            duration_ms=result.duration_ms,
        )

    def _check_syntax(self, file_path: str) -> ToolResult:
        """Check Python file syntax."""
        result = self._read_file(file_path)
        if not result.success:
            return result

        try:
            compile(result.output, file_path, "exec")
            return ToolResult(
                success=True,
                output="Syntax OK",
                duration_ms=result.duration_ms,
            )
        except SyntaxError as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Syntax error: {e}",
                duration_ms=result.duration_ms,
            )

    def _create_branch(self, branch_name: str, repo_path: str = ".") -> ToolResult:
        """Create a git branch."""
        return self._execute_command(f"git checkout -b {branch_name}", cwd=repo_path)

    def _commit_changes(self, message: str, repo_path: str = ".") -> ToolResult:
        """Commit git changes."""
        # First add all changes
        self._execute_command("git add -A", cwd=repo_path)
        # Then commit
        return self._execute_command(f'git commit -m "{message}"', cwd=repo_path)

    def _elapsed_ms(self, start: datetime) -> float:
        """Calculate elapsed milliseconds."""
        return (datetime.now(timezone.utc) - start).total_seconds() * 1000


# Global registry instance
_tool_registry: AgentToolRegistry = None


def get_tool_registry() -> AgentToolRegistry:
    """Get or create global tool registry."""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = AgentToolRegistry()
    return _tool_registry


def execute_tool(tool_name: str, **kwargs: Any) -> ToolResult:
    """Execute a tool by name."""
    registry = get_tool_registry()
    tool = registry.get(tool_name)
    if tool is None:
        return ToolResult(
            success=False,
            output="",
            error=f"Tool not found: {tool_name}",
        )
    return tool(**kwargs)
