#!/usr/bin/env python3
"""AMOS Task Automation - Real task execution with brain integration."""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from amos_brain_working import think
from amos_tools import ToolRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos_task")


@dataclass
class TaskResult:
    """Result of task execution."""

    success: bool
    output: str
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class TaskAutomation:
    """Automate tasks using AMOS brain and tools."""

    def __init__(self):
        self.registry = ToolRegistry()
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register default automation tools."""
        self.registry.register("run_command", self._run_shell_command)
        self.registry.register("analyze_code", self._analyze_code)
        self.registry.register("brain_think", self._brain_think)
        self.registry.register("file_read", self._file_read)
        self.registry.register("file_write", self._file_write)

    def _run_shell_command(self, command: str, cwd: Optional[str] = None) -> str:
        """Run shell command safely."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.stdout if result.returncode == 0 else result.stderr
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Error: {e}"

    def _analyze_code(self, file_path: str) -> dict[str, Any]:
        """Analyze code file."""
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            content = path.read_text()
            lines = content.split("\n")

            return {
                "lines": len(lines),
                "chars": len(content),
                "has_main": 'if __name__ == "__main__"' in content,
                "has_typing": "from typing" in content or "-> " in content,
                "functions": content.count("def "),
                "classes": content.count("class "),
            }
        except Exception as e:
            return {"error": str(e)}

    def _brain_think(self, request: str, context: Optional[dict] = None) -> dict[str, Any]:
        """Use brain to think about request."""
        result = think(request, context)
        # Convert StateGraph to serializable dict
        if isinstance(result, dict):
            return {
                k: str(v)
                if not isinstance(v, (str, int, float, bool, list, dict, type(None)))
                else v
                for k, v in result.items()
            }
        return {"result": str(result)}

    def _file_read(self, path: str) -> str:
        """Read file contents."""
        try:
            return Path(path).read_text()
        except Exception as e:
            return f"Error reading file: {e}"

    def _file_write(self, path: str, content: str) -> bool:
        """Write file contents."""
        try:
            Path(path).write_text(content)
            return True
        except Exception as e:
            logger.error(f"Error writing file: {e}")
            return False

    def _serialize_output(self, output: Any) -> str:
        """Serialize output to string, handling non-JSON objects."""
        if isinstance(output, str):
            return output
        try:
            return json.dumps(output, indent=2, default=str)
        except (TypeError, ValueError):
            return str(output)

    def execute(self, task_name: str, **kwargs: Any) -> TaskResult:
        """Execute a registered task."""
        tool = self.registry.get(task_name)
        if not tool:
            return TaskResult(
                success=False,
                output="",
                error=f"Unknown task: {task_name}",
            )

        try:
            output = tool(**kwargs)
            return TaskResult(
                success=True,
                output=self._serialize_output(output),
            )
        except Exception as e:
            return TaskResult(
                success=False,
                output="",
                error=str(e),
            )

    def automate(self, goal: str, steps: list[dict[str, Any]]) -> list[TaskResult]:
        """Run automated sequence of tasks."""
        results = []

        for i, step in enumerate(steps, 1):
            task_name = step.get("task")
            params = step.get("params", {})

            logger.info(f"Step {i}/{len(steps)}: {task_name}")
            result = self.execute(task_name, **params)
            results.append(result)

            if not result.success:
                logger.error(f"Step {i} failed: {result.error}")
                break

        return results


def main() -> int:
    """Demo task automation."""
    print("=" * 60)
    print("AMOS Task Automation Demo")
    print("=" * 60)

    automation = TaskAutomation()

    # Demo 1: Brain think
    print("\n[1] Brain analysis:")
    result = automation.execute("brain_think", request="Analyze Python best practices")
    print(f"  Status: {'✓' if result.success else '✗'}")
    if result.success:
        data = json.loads(result.output)
        print(f"  Legality: {data.get('legality')}")
        print(f"  Mode: {data.get('mode')}")

    # Demo 2: Code analysis
    print("\n[2] Code analysis:")
    result = automation.execute("analyze_code", file_path="amos_brain_working.py")
    print(f"  Status: {'✓' if result.success else '✗'}")
    if result.success:
        data = json.loads(result.output)
        print(f"  Lines: {data.get('lines')}")
        print(f"  Functions: {data.get('functions')}")

    # Demo 3: File read
    print("\n[3] File read:")
    result = automation.execute("file_read", path="README.md")
    print(f"  Status: {'✓' if result.success else '✗'}")
    if result.success:
        lines = result.output.split("\n")[:5]
        for line in lines:
            print(f"    {line[:60]}...")

    # Demo 4: Automation sequence
    print("\n[4] Automation sequence:")
    steps = [
        {"task": "brain_think", "params": {"request": "Plan code refactoring"}},
        {"task": "analyze_code", "params": {"file_path": "amos_tools.py"}},
    ]
    results = automation.automate("Code analysis workflow", steps)
    for i, r in enumerate(results, 1):
        print(f"  Step {i}: {'✓' if r.success else '✗'}")

    print("\n" + "=" * 60)
    print("✅ Task automation demo complete")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
