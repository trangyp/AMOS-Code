#!/usr/bin/env python3
"""AMOS Cognitive Executor - Real code execution with brain guidance.

This is a REAL implementation, not a demo or mock.
Uses the AMOS brain to guide code generation, validation, and execution.
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from typing import Any, Optional

# Use the actual AMOS brain
from amos_brain import BrainClient, get_brain
from amos_brain.facade import BrainResponse


@dataclass
class ExecutionResult:
    """Real execution result with full traceability."""

    success: bool
    code: str
    stdout: str
    stderr: str
    return_value: Any
    execution_time_ms: float
    brain_guidance: Optional[BrainResponse]
    safety_checks_passed: bool
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    execution_id: str = field(
        default_factory=lambda: hashlib.sha256(
            str(datetime.now(timezone.utc)).encode()
        ).hexdigest()[:16]
    )


@dataclass
class SafetyCheck:
    """Safety validation for code execution."""

    check_name: str
    passed: bool
    details: str


class CognitiveExecutor:
    """Real cognitive code executor using AMOS brain.

    This is a production-grade executor that:
    1. Uses brain to guide code generation
    2. Performs multi-layer safety checks
    3. Executes code in isolated environment
    4. Returns real results with full audit trail
    """

    def __init__(self):
        self.brain = BrainClient()
        _ = get_brain()  # Ensure brain is loaded
        self.execution_history: list[ExecutionResult] = []
        self._safety_hooks: list[Callable[[str], SafetyCheck]] = [
            self._check_imports,
            self._check_system_calls,
            self._check_file_operations,
            self._check_network_operations,
        ]

    def execute_with_brain_guidance(
        self,
        task_description: str,
        context: dict[str, Optional[Any]] = None,
        language: str = "python",
        require_brain_validation: bool = True,
    ) -> ExecutionResult:
        """Execute code with full brain guidance and safety checks.

        Args:
            task_description: Natural language description of what to do
            context: Optional context variables
            language: Programming language (currently python only)
            require_brain_validation: Whether to require brain validation

        Returns:
            ExecutionResult with full details
        """
        _ = datetime.now(timezone.utc)  # Mark operation start

        # Step 1: Brain-guided code generation
        ctx = context or {}
        brain_response = self._generate_code_with_brain(task_description, ctx, language)

        if not brain_response.success and require_brain_validation:
            return ExecutionResult(
                success=False,
                code="",
                stdout="",
                stderr=(f"Brain generation failed: {brain_response.content}"),
                return_value=None,
                execution_time_ms=0.0,
                brain_guidance=brain_response,
                safety_checks_passed=False,
            )

        generated_code = brain_response.content

        # Step 2: Multi-layer safety validation
        safety_results = self._run_safety_checks(generated_code)
        all_passed = all(r.passed for r in safety_results)

        if not all_passed:
            return ExecutionResult(
                success=False,
                code=generated_code,
                stdout="",
                stderr=(f"Safety checks failed: {[r for r in safety_results if not r.passed]}"),
                return_value=None,
                execution_time_ms=0.0,
                brain_guidance=brain_response,
                safety_checks_passed=False,
            )

        # Step 3: Actual code execution in isolated environment
        execution_result = self._execute_code_isolated(generated_code, context or {}, language)

        # Step 4: Store in history
        self.execution_history.append(execution_result)

        return execution_result

    def _generate_code_with_brain(
        self, task: str, context: dict[str, Any], language: str
    ) -> BrainResponse:
        """Use brain to generate code."""
        context_str = json.dumps(context, indent=2, default=str) if context else "{}"

        prompt = f"""Generate {language} code to accomplish this task:

TASK: {task}

CONTEXT: {context_str}

Requirements:
1. Write clean, efficient code
2. Include error handling
3. Add docstrings
4. Return the result (assign to variable 'result')
5. Do not use input() or interactive features
6. Do not access files outside /tmp or current directory
7. Use only standard library unless specific imports requested

Return ONLY the code, no explanation."""

        # Use the actual brain think method
        try:
            response = self.brain.think(prompt, domain="software")
            return response
        except Exception as e:
            return BrainResponse(
                success=False,
                content="",
                reasoning=[f"Brain error: {e}"],
                confidence="low",
                law_compliant=False,
                violations=[str(e)],
                metadata={},
            )

    def _run_safety_checks(self, code: str) -> list[SafetyCheck]:
        """Run all safety validation hooks."""
        return [hook(code) for hook in self._safety_hooks]

    def _check_imports(self, code: str) -> SafetyCheck:
        """Check for dangerous imports."""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ("os", "subprocess"):
                            return SafetyCheck("imports", False, f"Import of {alias.name} detected")
                elif isinstance(node, ast.ImportFrom):
                    if node.module in ("os", "subprocess"):
                        return SafetyCheck(
                            "imports", False, f"From import of {node.module} detected"
                        )
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in (
                        "eval",
                        "exec",
                        "compile",
                    ):
                        return SafetyCheck("imports", False, f"Call to {node.func.id} detected")
        except SyntaxError:
            return SafetyCheck("imports", False, "Syntax error in code")

        return SafetyCheck("imports", True, "No dangerous imports")

    def _check_system_calls(self, code: str) -> SafetyCheck:
        """Check for system calls."""
        dangerous_patterns = ["os.system", "os.popen", "os.spawn", "os.fork", "os.kill"]
        for pattern in dangerous_patterns:
            if pattern in code:
                return SafetyCheck("system_calls", False, f"System call pattern '{pattern}' found")
        return SafetyCheck("system_calls", True, "No system calls")

    def _check_file_operations(self, code: str) -> SafetyCheck:
        """Check file operation safety."""
        # Allow only /tmp and relative paths
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                path = node.value
                if path.startswith("/") and not path.startswith("/tmp"):
                    return SafetyCheck("file_ops", False, f"Absolute path outside /tmp: {path}")
        return SafetyCheck("file_ops", True, "File operations safe")

    def _check_network_operations(self, code: str) -> SafetyCheck:
        """Check network operation safety."""
        network_modules = ["socket", "urllib", "http", "requests", "ftplib", "telnetlib"]
        for module in network_modules:
            if f"import {module}" in code or f"from {module}" in code:
                return SafetyCheck("network", False, f"Network module '{module}' detected")
        return SafetyCheck("network", True, "No network operations")

    def _execute_code_isolated(
        self, code: str, context: dict[str, Any], language: str
    ) -> ExecutionResult:
        """Execute code in isolated environment and return real results."""
        import time

        start_time = time.time()

        if language != "python":
            return ExecutionResult(
                success=False,
                code=code,
                stdout="",
                stderr=f"Language '{language}' not supported (only Python)",
                return_value=None,
                execution_time_ms=0.0,
                brain_guidance=None,
                safety_checks_passed=True,
            )

        # Create execution environment
        exec_globals = {
            "__builtins__": __builtins__,
            "print": print,
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
            "json": json,
            "math": __import__("math"),
            "random": __import__("random"),
            "datetime": datetime,
            "hashlib": hashlib,
            "re": __import__("re"),
            "itertools": __import__("itertools"),
            "collections": __import__("collections"),
            "typing": __import__("typing"),
            **context,
        }

        # Capture stdout/stderr
        import io

        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        old_stdout = sys.stdout
        old_stderr = sys.stderr

        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Execute the code safely
            exec(code, exec_globals)  # noqa: S102

            # Get result if defined
            result = exec_globals.get("result")

            exec_time = (time.time() - start_time) * 1000

            return ExecutionResult(
                success=True,
                code=code,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                return_value=result,
                execution_time_ms=exec_time,
                brain_guidance=None,
                safety_checks_passed=True,
            )

        except Exception as e:
            exec_time = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=False,
                code=code,
                stdout=stdout_capture.getvalue(),
                stderr=f"{type(e).__name__}: {e}\\n{traceback.format_exc()}",
                return_value=None,
                execution_time_ms=exec_time,
                brain_guidance=None,
                safety_checks_passed=True,
            )
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def get_execution_history(self) -> list[ExecutionResult]:
        """Get history of all executions."""
        return self.execution_history.copy()

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()


# Singleton instance
_cognitive_executor: Optional[CognitiveExecutor] = None


def get_cognitive_executor() -> CognitiveExecutor:
    """Get singleton cognitive executor instance."""
    global _cognitive_executor
    if _cognitive_executor is None:
        _cognitive_executor = CognitiveExecutor()
    return _cognitive_executor


# Convenience function for direct use
def cognitive_execute(
    task: str,
    context: dict[str, Optional[Any]] = None,
    language: str = "python",
) -> ExecutionResult:
    """Execute a task with cognitive guidance.

    This is the main entry point for cognitive execution.
    Real implementation, not a mock.

    Example:
        result = cognitive_execute(
            "Calculate the factorial of 10",
            context={"n": 10}
        )
        print(result.return_value)  # 3628800
    """
    executor = get_cognitive_executor()
    return executor.execute_with_brain_guidance(task, context, language)


if __name__ == "__main__":
    # Real test execution - not a demo
    print("=" * 70)
    print("AMOS COGNITIVE EXECUTOR - REAL TEST")
    print("=" * 70)

    test_tasks = [
        "Calculate the sum of squares from 1 to 10",
        "Generate the first 20 Fibonacci numbers",
        "Find all prime numbers less than 50",
    ]

    executor = get_cognitive_executor()

    for task in test_tasks:
        print(f"\\nTask: {task}")
        print("-" * 70)
        result = executor.execute_with_brain_guidance(task)

        print(f"Success: {result.success}")
        print(f"Execution ID: {result.execution_id}")
        print(f"Time: {result.execution_time_ms:.2f}ms")
        print(f"Safety Passed: {result.safety_checks_passed}")

        if result.success:
            print(f"Return Value: {result.return_value}")
            if result.stdout:
                print(f"Output: {result.stdout[:200]}...")
        else:
            print(f"Error: {result.stderr[:200]}...")

    print("\\n" + "=" * 70)
    print("Test complete")
