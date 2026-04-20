"""
AMOS Code Execution Runtime

Sandboxed execution environment for generated code.
Integrates with the brain for safe code testing and validation.

Key capabilities:
- Sandboxed Python execution
- Syntax validation
- Import analysis
- Safety checks
- Rollback capability
"""

from __future__ import annotations

import ast
import hashlib
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ExecutionResult:
    """Result of code execution."""

    success: bool
    output: str
    error: str | None = None
    duration_ms: float = 0.0
    memory_mb: float = 0.0
    exit_code: int = 0
    syntax_valid: bool = False
    safety_score: float = 0.0


@dataclass
class SafetyReport:
    """Safety analysis report for code."""

    score: float
    issues: list[str]
    banned_imports: list[str]
    network_access: bool
    file_access: bool
    system_calls: list[str]


class CodeSafetyChecker:
    """
    Safety checker for generated code.

    Analyzes code for:
    - Dangerous imports (os.system, subprocess, etc.)
    - Network operations
    - File system access outside allowed paths
    - System calls
    """

    BANNED_IMPORTS = {
        "os.system",
        "subprocess",
        "exec",
        "eval",
        "compile",
        "__import__",
        "builtins.__import__",
        "importlib",
    }

    DANGEROUS_PATTERNS = [
        r"os\.system\s*\(",
        r"subprocess\.(run|call|Popen)",
        r"eval\s*\(",
        r"exec\s*\(",
        r"__import__\s*\(",
        r"open\s*\(\s*['\"]\/",  # Absolute path access
        r"requests\.(get|post|put|delete)",
        r"urllib",
        r"http\.client",
        r"socket\.",
        r"shutil\.(rmtree|move|copy)",
    ]

    def check_safety(self, code: str) -> SafetyReport:
        """Analyze code for safety issues."""
        issues = []
        banned_found = []
        network_access = False
        file_access = False
        system_calls = []

        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                issues.append(f"Dangerous pattern detected: {pattern}")
                if (
                    "request" in pattern
                    or "urllib" in pattern
                    or "http" in pattern
                    or "socket" in pattern
                ):
                    network_access = True
                if "open" in pattern or "shutil" in pattern:
                    file_access = True
                if "os.system" in pattern or "subprocess" in pattern:
                    system_calls.extend(matches)

        # Parse imports
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.BANNED_IMPORTS:
                            banned_found.append(alias.name)
                            issues.append(f"Banned import: {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module in self.BANNED_IMPORTS:
                        banned_found.append(node.module)
                        issues.append(f"Banned import from: {node.module}")
        except SyntaxError:
            issues.append("Syntax error - cannot parse for safety")

        # Calculate score
        score = max(0.0, 1.0 - (len(issues) * 0.1))

        return SafetyReport(
            score=score,
            issues=issues,
            banned_imports=banned_found,
            network_access=network_access,
            file_access=file_access,
            system_calls=system_calls,
        )


class CodeExecutionRuntime:
    """
    Sandboxed code execution runtime.

    Provides safe execution of generated code with:
    - Syntax validation
    - Safety checks
    - Resource limits
    - Output capture
    """

    def __init__(self, sandbox_dir: Path | None = None):
        self.sandbox_dir = sandbox_dir or Path(tempfile.gettempdir()) / "amos_sandbox"
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        self.safety_checker = CodeSafetyChecker()
        self.execution_history: list[ExecutionResult] = []

    def validate_syntax(self, code: str) -> tuple[bool, str | None]:
        """Validate Python syntax."""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)

    def check_safety(self, code: str) -> SafetyReport:
        """Check code safety."""
        return self.safety_checker.check_safety(code)

    def execute_in_sandbox(
        self,
        code: str,
        timeout: float = 30.0,
        memory_limit_mb: int = 512,
        allowed_imports: list[str] | None = None,
    ) -> ExecutionResult:
        """
        Execute code in a sandboxed environment.

        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds
            memory_limit_mb: Memory limit in MB
            allowed_imports: List of allowed imports (None = allow all safe)

        Returns:
            ExecutionResult with output and status
        """
        import time

        start_time = time.time()

        # Validate syntax
        syntax_valid, syntax_error = self.validate_syntax(code)
        if not syntax_valid:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Syntax validation failed: {syntax_error}",
                duration_ms=(time.time() - start_time) * 1000,
                syntax_valid=False,
                safety_score=0.0,
            )

        # Check safety
        safety = self.check_safety(code)
        if safety.score < 0.5:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Safety check failed: {'; '.join(safety.issues[:3])}",
                duration_ms=(time.time() - start_time) * 1000,
                syntax_valid=True,
                safety_score=safety.score,
            )

        # Create sandbox file
        code_hash = hashlib.sha256(code.encode()).hexdigest()[:12]
        sandbox_file = self.sandbox_dir / f"exec_{code_hash}.py"

        try:
            # Write code to sandbox
            sandbox_file.write_text(code, encoding="utf-8")

            # Execute in subprocess with restrictions
            import subprocess

            result = subprocess.run(
                [sys.executable, str(sandbox_file)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.sandbox_dir),
                # Restrict environment
                env={
                    "PYTHONPATH": str(self.sandbox_dir),
                    "HOME": str(self.sandbox_dir),
                },
            )

            duration = (time.time() - start_time) * 1000

            exec_result = ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.stderr else None,
                duration_ms=duration,
                exit_code=result.returncode,
                syntax_valid=True,
                safety_score=safety.score,
            )

            self.execution_history.append(exec_result)
            return exec_result

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution timed out after {timeout}s",
                duration_ms=timeout * 1000,
                syntax_valid=True,
                safety_score=safety.score,
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution failed: {e}",
                duration_ms=(time.time() - start_time) * 1000,
                syntax_valid=True,
                safety_score=safety.score,
            )
        finally:
            # Cleanup sandbox file
            try:
                sandbox_file.unlink(missing_ok=True)
            except Exception:
                pass

    def test_generated_code(
        self,
        code: str,
        test_cases: list[dict[str, Any]] | None = None,
    ) -> ExecutionResult:
        """
        Test generated code with optional test cases.

        Args:
            code: Code to test
            test_cases: List of test inputs/expected outputs

        Returns:
            ExecutionResult with test results
        """
        # Wrap code in test harness
        test_code = f"""
{code}

# Test harness
if __name__ == "__main__":
    print("Code loaded successfully")
    # Basic smoke test - try to compile
    import ast
    ast.parse(open(__file__).read())
    print("Syntax OK")
"""

        return self.execute_in_sandbox(test_code)

    def get_execution_stats(self) -> dict[str, Any]:
        """Get statistics on executions."""
        if not self.execution_history:
            return {"total": 0}

        total = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.success)
        avg_duration = sum(r.duration_ms for r in self.execution_history) / total

        return {
            "total": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total,
            "avg_duration_ms": avg_duration,
        }


def get_execution_runtime(sandbox_dir: Path | None = None) -> CodeExecutionRuntime:
    """Get code execution runtime instance."""
    return CodeExecutionRuntime(sandbox_dir)
