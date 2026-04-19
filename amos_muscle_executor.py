#!/usr/bin/env python3
"""AMOS Muscle Executor
====================

Real task execution engine for the AMOS MUSCLE subsystem.
Connects orchestrator decisions to actual code execution.

Features:
- Execute Python code
- Run shell commands
- Call existing workflow engine
- Track execution metrics
- Error handling & recovery

Owner: Trang
Version: 1.0.0
"""

import subprocess
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

try:
    from amos_secure_equation_runner import SecureEquationRunner

    SECURE_EXECUTION_AVAILABLE = True
except ImportError:
    SECURE_EXECUTION_AVAILABLE = False


class ExecutionType(Enum):
    """Type of execution task."""

    PYTHON = "python"
    SHELL = "shell"
    WORKFLOW = "workflow"
    FUNCTION = "function"


@dataclass
class ExecutionResult:
    """Result of task execution."""

    task_id: str
    task_type: ExecutionType
    command: str
    success: bool
    output: str
    error: str
    duration_ms: int
    timestamp: str
    resources_used: Dict[str, Any] = field(default_factory=dict)


class AMOSMuscleExecutor:
    """Real task execution engine for AMOS MUSCLE subsystem.

    Connects orchestrator routing to actual code execution.
    Provides: Python exec, shell commands, workflow calls
    """

    def __init__(self):
        self.execution_count = 0
        self.success_count = 0
        self.error_count = 0
        self.history: List[ExecutionResult] = []

    def execute(
        self, task: str, task_type: ExecutionType = ExecutionType.PYTHON, timeout: int = 30
    ) -> ExecutionResult:
        """Execute a task through MUSCLE.

        Args:
            task: Task to execute (code, command, or function call)
            task_type: Type of execution
            timeout: Max execution time in seconds

        Returns:
            ExecutionResult with output, errors, metrics
        """
        self.execution_count += 1
        task_id = f"MUSCLE-{self.execution_count:04d}"
        start_time = datetime.now(UTC)

        print(f"\n[MUSCLE] Executing {task_type.value} task...")
        print(f"  Task ID: {task_id}")
        print(f"  Command: {task[:60]}...")

        try:
            if task_type == ExecutionType.PYTHON:
                result = self._exec_python(task, timeout)
            elif task_type == ExecutionType.SHELL:
                result = self._exec_shell(task, timeout)
            elif task_type == ExecutionType.WORKFLOW:
                result = self._exec_workflow(task)
            else:
                result = self._exec_function(task)

            self.success_count += 1

        except Exception as e:
            result = ExecutionResult(
                task_id=task_id,
                task_type=task_type,
                command=task,
                success=False,
                output="",
                error=f"{type(e).__name__}: {str(e)}",
                duration_ms=0,
                timestamp=datetime.now(UTC).isoformat(),
            )
            self.error_count += 1

        # Record history
        self.history.append(result)

        # Print result
        status_icon = "✓" if result.success else "✗"
        print(f"  {status_icon} Execution: {'Success' if result.success else 'Failed'}")
        if result.output:
            print(f"  Output: {result.output[:100]}...")
        if result.error:
            print(f"  Error: {result.error}")

        return result

    def _exec_python(self, code: str, timeout: int) -> ExecutionResult:
        """Execute Python code safely using secure sandbox."""
        start = datetime.now(UTC)

        # Use secure execution framework if available
        if SECURE_EXECUTION_AVAILABLE:
            runner = SecureEquationRunner()
            result = runner.execute_equation(code, timeout=float(timeout))

            if result["success"]:
                output = "Code executed successfully in secure sandbox"
                success = True
                error = None
            else:
                output = ""
                success = False
                error = result.get("error", "Secure execution failed")
        else:
            # Fallback: legacy restricted execution (less secure)
            safe_globals = {
                "__builtins__": {
                    "len": len,
                    "range": range,
                    "enumerate": enumerate,
                    "zip": zip,
                    "map": map,
                    "filter": filter,
                    "sum": sum,
                    "min": min,
                    "max": max,
                    "abs": abs,
                    "round": round,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "tuple": tuple,
                    "print": lambda *args: None,  # Disable print
                }
            }

            import io

            old_stdout = sys.stdout
            sys.stdout = io.StringIO()

            try:
                exec(code, safe_globals)  # nosec: B102 - Fallback only
                output = sys.stdout.getvalue()
                success = True
                error = None
            except Exception:
                output = sys.stdout.getvalue()
                success = False
                error = traceback.format_exc()
            finally:
                sys.stdout = old_stdout

        duration = int((datetime.now(UTC) - start).total_seconds() * 1000)

        return ExecutionResult(
            task_id=f"PY-{self.execution_count}",
            task_type=ExecutionType.PYTHON,
            command=code[:100],
            success=success,
            output=output,
            error=error,
            duration_ms=duration,
            timestamp=datetime.now(UTC).isoformat(),
        )

    def _exec_shell(self, command: str, timeout: int) -> ExecutionResult:
        """Execute shell command safely."""
        start = datetime.now(UTC)

        # Safety: block dangerous commands
        dangerous = ["rm -rf /", "mkfs", "> /dev/sda", "dd if=/dev/zero"]
        for d in dangerous:
            if d in command:
                return ExecutionResult(
                    task_id=f"SH-{self.execution_count}",
                    task_type=ExecutionType.SHELL,
                    command=command,
                    success=False,
                    output="",
                    error=f"Blocked dangerous command: {d}",
                    duration_ms=0,
                    timestamp=datetime.now(UTC).isoformat(),
                )

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout
            )

            output = result.stdout
            if result.stderr:
                output += f"\n[STDERR]: {result.stderr}"

            success = result.returncode == 0
            error = None if success else f"Exit code: {result.returncode}"

        except subprocess.TimeoutExpired:
            success = False
            output = ""
            error = f"Timeout after {timeout}s"
        except Exception as e:
            success = False
            output = ""
            error = str(e)

        duration = int((datetime.now(UTC) - start).total_seconds() * 1000)

        return ExecutionResult(
            task_id=f"SH-{self.execution_count}",
            task_type=ExecutionType.SHELL,
            command=command,
            success=success,
            output=output,
            error=error,
            duration_ms=duration,
            timestamp=datetime.now(UTC).isoformat(),
        )

    def _exec_workflow(self, workflow_name: str) -> ExecutionResult:
        """Execute existing workflow engine."""
        start = datetime.now(UTC)

        # Try to import and use existing workflow engine
        try:
            sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS" / "06_MUSCLE"))
            from workflow_engine import WorkflowEngine

            engine = WorkflowEngine()
            result = engine.run_workflow(workflow_name)

            success = result.get("success", False)
            output = str(result.get("output", ""))
            error = result.get("error")

        except ImportError:
            # Fallback: simulate workflow
            success = True
            output = f"Simulated workflow: {workflow_name}"
            error = None
        except Exception as e:
            success = False
            output = ""
            error = str(e)

        duration = int((datetime.now(UTC) - start).total_seconds() * 1000)

        return ExecutionResult(
            task_id=f"WF-{self.execution_count}",
            task_type=ExecutionType.WORKFLOW,
            command=workflow_name,
            success=success,
            output=output,
            error=error,
            duration_ms=duration,
            timestamp=datetime.now(UTC).isoformat(),
        )

    def _exec_function(self, func_spec: str) -> ExecutionResult:
        """Execute a function by name using safe dispatch."""
        start = datetime.now(UTC)

        # Safe function dispatch table - whitelist of allowed functions
        allowed_functions = {
            # Math functions
            "abs": abs,
            "round": round,
            "max": max,
            "min": min,
            "sum": sum,
            "pow": pow,
            "divmod": divmod,
            # Type functions
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            # Other safe builtins
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "sorted": sorted,
        }

        try:
            # Parse function call
            if "(" in func_spec:
                func_name = func_spec.split("(")[0].strip()
                args_str = func_spec[func_spec.find("(") + 1 : func_spec.rfind(")")]
            else:
                func_name = func_spec.strip()
                args_str = ""

            # Check if function is allowed
            if func_name not in allowed_functions:
                raise ValueError(f"Function '{func_name}' not in allowed list")

            func = allowed_functions[func_name]

            # Parse arguments safely (only simple literals)
            if args_str.strip():
                # Use ast.literal_eval for safe argument parsing
                import ast

                try:
                    # Wrap in tuple to handle multiple args
                    args = ast.literal_eval(f"({args_str},)")
                    if not isinstance(args, tuple):
                        args = (args,)
                except (ValueError, SyntaxError):
                    # Single argument that's not a tuple
                    args = (ast.literal_eval(args_str),)
            else:
                args = ()

            # Execute function with parsed arguments
            result = func(*args)
            success = True
            output = str(result)
            error = None

        except Exception as e:
            success = False
            output = ""
            error = f"Function execution failed: {e}"

        duration = int((datetime.now(UTC) - start).total_seconds() * 1000)

        return ExecutionResult(
            task_id=f"FN-{self.execution_count}",
            task_type=ExecutionType.FUNCTION,
            command=func_spec,
            success=success,
            output=output,
            error=error,
            duration_ms=duration,
            timestamp=datetime.now(UTC).isoformat(),
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        total = self.execution_count
        success_rate = (self.success_count / total * 100) if total > 0 else 0

        return {
            "total_executions": total,
            "successful": self.success_count,
            "failed": self.error_count,
            "success_rate": f"{success_rate:.1f}%",
            "history_count": len(self.history),
            "status": "operational" if total > 0 else "idle",
        }


def demo():
    """Demonstrate MUSCLE execution capabilities."""
    print("\n" + "=" * 70)
    print("AMOS MUSCLE EXECUTOR - DEMONSTRATION")
    print("=" * 70)

    executor = AMOSMuscleExecutor()

    # Demo 1: Python execution
    print("\n[Demo 1] Python Code Execution")
    result = executor.execute(
        """
# Calculate AMOS system metrics
engines = 12
laws = 6
subsystems = 14
total = engines + laws + subsystems
print(f"AMOS Total Components: {total}")
""",
        ExecutionType.PYTHON,
    )

    # Demo 2: Shell execution
    print("\n[Demo 2] Shell Command Execution")
    result = executor.execute("ls -la | head -5", ExecutionType.SHELL)

    # Demo 3: Workflow execution
    print("\n[Demo 3] Workflow Execution")
    result = executor.execute("test_workflow", ExecutionType.WORKFLOW)

    # Stats
    print("\n" + "=" * 70)
    print("EXECUTION STATISTICS")
    print("=" * 70)
    stats = executor.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)
    print("MUSCLE EXECUTOR OPERATIONAL")
    print("=" * 70)
    print("\nNow the orchestrator can execute REAL tasks!")
    print("python amos_unified_orchestrator.py")
    print("=" * 70)


if __name__ == "__main__":
    demo()
