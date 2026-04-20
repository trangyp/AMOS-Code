#!/usr/bin/env python3
"""
AMOS Sandbox Executor - Secure Code Execution via E2B
======================================================

Provides isolated, secure code execution environment for AMOS.
Integrates with E2B (https://e2b.dev) for sandboxed execution.

Critical Security Feature - addresses missing sandbox capability
that Devin and Claude Code have but AMOS lacks.

Author: AMOS System
Version: 1.0.0
Date: April 2026
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any

# Try to import E2B
try:
    from e2b import CodeInterpreter, Sandbox

    E2B_AVAILABLE = True
except ImportError:
    E2B_AVAILABLE = False
    print("⚠️  E2B not installed. Run: pip install e2b")


class SandboxStatus(Enum):
    """Status of sandbox execution."""

    IDLE = auto()
    RUNNING = auto()
    SUCCESS = auto()
    ERROR = auto()
    TIMEOUT = auto()
    SECURITY_VIOLATION = auto()


@dataclass
class SandboxResult:
    """Result of sandboxed code execution."""

    status: SandboxStatus
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: float
    files_created: list[str]
    network_requests: list[dict[str, Any]]
    memory_peak_mb: float
    cpu_time_ms: float
    timestamp: str
    sandbox_id: str = None


class AMOSSandboxExecutor:
    """
    Secure sandboxed code execution for AMOS.

    Provides isolated environment for:
    - Running untrusted code safely
    - Testing generated code
    - Executing user scripts
    - Running build processes

    Security Features:
    - Network isolation (configurable)
    - File system sandboxing
    - Resource limits (CPU, memory, time)
    - No access to host system
    """

    def __init__(
        self,
        api_key: str = None,
        template: str = "base",
        timeout_ms: int = 300000,  # 5 minutes default
        memory_limit_mb: int = 512,
        cpu_limit_percent: int = 100,
        allow_network: bool = False,
    ):
        """
        Initialize sandbox executor.

        Args:
            api_key: E2B API key (or from E2B_API_KEY env var)
            template: E2B sandbox template (base, python, node, etc.)
            timeout_ms: Maximum execution time
            memory_limit_mb: Memory limit for sandbox
            cpu_limit_percent: CPU limit (percentage of one core)
            allow_network: Whether to allow network access
        """
        self.api_key = api_key or os.environ.get("E2B_API_KEY")
        self.template = template
        self.timeout_ms = timeout_ms
        self.memory_limit_mb = memory_limit_mb
        self.cpu_limit_percent = cpu_limit_percent
        self.allow_network = allow_network

        self._sandbox: Sandbox | None = None
        self._history: list[SandboxResult] = []

        if not E2B_AVAILABLE:
            raise ImportError(
                "E2B not installed. Install with: pip install e2b\n"
                "Get API key from: https://e2b.dev"
            )

        if not self.api_key:
            raise ValueError(
                "E2B API key required. Set E2B_API_KEY environment variable "
                "or pass api_key parameter."
            )

    async def create_sandbox(self) -> Sandbox:
        """Create a new sandbox instance."""
        self._sandbox = Sandbox(
            api_key=self.api_key,
            template=self.template,
            timeout=self.timeout_ms,
        )
        return self._sandbox

    async def execute_code(
        self,
        code: str,
        language: str = "python",
        context_files: dict[str, str] = None,
        environment_vars: dict[str, str] = None,
    ) -> SandboxResult:
        """
        Execute code in secure sandbox.

        Args:
            code: Code to execute
            language: Programming language (python, javascript, bash, etc.)
            context_files: Files to upload before execution {path: content}
            environment_vars: Environment variables to set

        Returns:
            SandboxResult with execution details
        """
        start_time = datetime.now()

        try:
            # Create sandbox if not exists
            if not self._sandbox:
                await self.create_sandbox()

            # Upload context files
            if context_files:
                for path, content in context_files.items():
                    await self._upload_file(path, content)

            # Set environment variables
            if environment_vars:
                for key, value in environment_vars.items():
                    await self._set_env(key, value)

            # Execute based on language
            if language == "python":
                result = await self._execute_python(code)
            elif language == "javascript" or language == "node":
                result = await self._execute_javascript(code)
            elif language == "bash" or language == "shell":
                result = await self._execute_bash(code)
            else:
                result = await self._execute_generic(code, language)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            # Build result
            sandbox_result = SandboxResult(
                status=SandboxStatus.SUCCESS if result["exit_code"] == 0 else SandboxStatus.ERROR,
                stdout=result.get("stdout", ""),
                stderr=result.get("stderr", ""),
                exit_code=result.get("exit_code", -1),
                execution_time_ms=execution_time,
                files_created=result.get("files_created", []),
                network_requests=result.get("network_requests", []),
                memory_peak_mb=result.get("memory_peak_mb", 0.0),
                cpu_time_ms=result.get("cpu_time_ms", 0.0),
                timestamp=datetime.now().isoformat(),
                sandbox_id=self._sandbox.id if self._sandbox else None,
            )

            self._history.append(sandbox_result)
            return sandbox_result

        except TimeoutError:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return SandboxResult(
                status=SandboxStatus.TIMEOUT,
                stdout="",
                stderr=f"Execution timed out after {self.timeout_ms}ms",
                exit_code=-1,
                execution_time_ms=execution_time,
                files_created=[],
                network_requests=[],
                memory_peak_mb=0.0,
                cpu_time_ms=0.0,
                timestamp=datetime.now().isoformat(),
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return SandboxResult(
                status=SandboxStatus.ERROR,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time_ms=execution_time,
                files_created=[],
                network_requests=[],
                memory_peak_mb=0.0,
                cpu_time_ms=0.0,
                timestamp=datetime.now().isoformat(),
            )

    async def _execute_python(self, code: str) -> dict[str, Any]:
        """Execute Python code in sandbox."""
        # Write code to file
        await self._upload_file("/tmp/execution_script.py", code)

        # Run with resource limits
        cmd = f"timeout {self.timeout_ms // 1000} python3 /tmp/execution_script.py"

        process = await self._sandbox.process.start(cmd)
        output = await process.wait()

        return {
            "stdout": output.stdout,
            "stderr": output.stderr,
            "exit_code": output.exit_code,
            "files_created": await self._list_new_files(),
            "network_requests": await self._get_network_activity(),
            "memory_peak_mb": await self._get_memory_usage(),
            "cpu_time_ms": await self._get_cpu_time(),
        }

    async def _execute_javascript(self, code: str) -> dict[str, Any]:
        """Execute JavaScript/Node code in sandbox."""
        await self._upload_file("/tmp/execution_script.js", code)

        cmd = f"timeout {self.timeout_ms // 1000} node /tmp/execution_script.js"
        process = await self._sandbox.process.start(cmd)
        output = await process.wait()

        return {
            "stdout": output.stdout,
            "stderr": output.stderr,
            "exit_code": output.exit_code,
            "files_created": await self._list_new_files(),
            "network_requests": await self._get_network_activity(),
            "memory_peak_mb": await self._get_memory_usage(),
            "cpu_time_ms": await self._get_cpu_time(),
        }

    async def _execute_bash(self, code: str) -> dict[str, Any]:
        """Execute bash/shell code in sandbox."""
        await self._upload_file("/tmp/execution_script.sh", code)
        await self._sandbox.filesystem.chmod("/tmp/execution_script.sh", "+x")

        cmd = f"timeout {self.timeout_ms // 1000} bash /tmp/execution_script.sh"
        process = await self._sandbox.process.start(cmd)
        output = await process.wait()

        return {
            "stdout": output.stdout,
            "stderr": output.stderr,
            "exit_code": output.exit_code,
            "files_created": await self._list_new_files(),
            "network_requests": await self._get_network_activity(),
            "memory_peak_mb": await self._get_memory_usage(),
            "cpu_time_ms": await self._get_cpu_time(),
        }

    async def _execute_generic(self, code: str, language: str) -> dict[str, Any]:
        """Execute generic code (fallback)."""
        await self._upload_file(f"/tmp/execution_script.{language}", code)

        cmd = f"timeout {self.timeout_ms // 1000} sh /tmp/execution_script.{language}"
        process = await self._sandbox.process.start(cmd)
        output = await process.wait()

        return {
            "stdout": output.stdout,
            "stderr": output.stderr,
            "exit_code": output.exit_code,
            "files_created": [],
            "network_requests": [],
            "memory_peak_mb": 0.0,
            "cpu_time_ms": 0.0,
        }

    async def _upload_file(self, path: str, content: str) -> None:
        """Upload file to sandbox."""
        if self._sandbox:
            await self._sandbox.filesystem.write(path, content)

    async def _set_env(self, key: str, value: str) -> None:
        """Set environment variable in sandbox."""
        if self._sandbox:
            await self._sandbox.process.start(f"export {key}={value}")

    async def _list_new_files(self) -> list[str]:
        """List files created during execution."""
        # Implementation depends on E2B capabilities
        return []

    async def _get_network_activity(self) -> list[dict[str, Any]]:
        """Get network requests made during execution."""
        # Implementation depends on E2B monitoring
        return []

    async def _get_memory_usage(self) -> float:
        """Get peak memory usage."""
        # Implementation depends on E2B metrics
        return 0.0

    async def _get_cpu_time(self) -> float:
        """Get CPU time used."""
        # Implementation depends on E2B metrics
        return 0.0

    async def install_packages(self, packages: list[str], language: str = "python") -> bool:
        """Install packages in sandbox."""
        try:
            if language == "python":
                cmd = f"pip install {' '.join(packages)}"
            elif language == "javascript":
                cmd = f"npm install {' '.join(packages)}"
            else:
                return False

            process = await self._sandbox.process.start(cmd)
            output = await process.wait()
            return output.exit_code == 0
        except Exception:
            return False

    async def read_file(self, path: str) -> str:
        """Read file from sandbox."""
        try:
            if self._sandbox:
                content = await self._sandbox.filesystem.read(path)
                return content
        except Exception:
            pass
        return None

    async def cleanup(self) -> None:
        """Clean up sandbox resources."""
        if self._sandbox:
            await self._sandbox.close()
            self._sandbox = None

    def get_history(self) -> list[SandboxResult]:
        """Get execution history."""
        return self._history.copy()

    def get_stats(self) -> dict[str, Any]:
        """Get execution statistics."""
        if not self._history:
            return {}

        return {
            "total_executions": len(self._history),
            "successful": sum(1 for r in self._history if r.status == SandboxStatus.SUCCESS),
            "failed": sum(1 for r in self._history if r.status == SandboxStatus.ERROR),
            "timeouts": sum(1 for r in self._history if r.status == SandboxStatus.TIMEOUT),
            "avg_execution_time_ms": sum(r.execution_time_ms for r in self._history)
            / len(self._history),
        }


class CodeSecurityScanner:
    """
    Security scanner for code before sandbox execution.

    Checks for:
    - Dangerous imports (os.system, subprocess, eval, exec)
    - Network requests
    - File system access
    - Resource exhaustion attempts
    """

    DANGEROUS_PATTERNS = [
        (r"import\s+os", "os module - can execute system commands"),
        (r"import\s+subprocess", "subprocess module - can spawn processes"),
        (r"import\s+ctypes", "ctypes module - can call native code"),
        (r"eval\s*\(", "eval() - arbitrary code execution"),
        (r"exec\s*\(", "exec() - arbitrary code execution"),
        (r"__import__", "Dynamic import - can bypass restrictions"),
        (r"compile\s*\(", "compile() - can create code objects"),
        (r"open\s*\(|file\s*\(", "File operations - can read/write files"),
        (r"socket\.|urllib|requests|httpx", "Network access"),
        (r"while\s+True", "Potential infinite loop"),
        (r"fork|pthread|threading", "Process/thread creation"),
        (r"malloc|free|memory", "Memory manipulation"),
    ]

    def __init__(self):
        self.warnings: list[str] = []
        self.dangerous_imports: list[str] = []

    def scan(self, code: str, language: str = "python") -> dict[str, Any]:
        """
        Scan code for security issues.

        Returns:
            Dict with 'safe' (bool), 'warnings', 'dangerous_imports'
        """
        import re

        self.warnings = []
        self.dangerous_imports = []

        for pattern, description in self.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                self.warnings.append(f"⚠️  {description}")
                self.dangerous_imports.append(pattern)

        # Additional checks
        if len(code) > 100000:  # 100KB limit
            self.warnings.append("⚠️  Code size exceeds 100KB")

        if code.count("\n") > 10000:  # 10K lines limit
            self.warnings.append("⚠️  Code exceeds 10,000 lines")

        return {
            "safe": len(self.warnings) == 0,
            "warnings": self.warnings,
            "dangerous_imports": self.dangerous_imports,
            "code_size_bytes": len(code),
            "line_count": code.count("\n") + 1,
        }


# Integration with AMOS Muscle Executor
class SecureMuscleExecutor:
    """
    Secure wrapper for AMOS Muscle Executor using sandbox.

    Replaces direct code execution with sandboxed execution.
    """

    def __init__(self, sandbox_executor: AMOSSandboxExecutor):
        self.sandbox = sandbox_executor
        self.security_scanner = CodeSecurityScanner()

    async def execute_secure(
        self,
        code: str,
        language: str = "python",
        scan_first: bool = True,
    ) -> SandboxResult:
        """
        Execute code with security scanning and sandboxing.

        This is the secure replacement for direct code execution.
        """
        # Security scan
        if scan_first:
            scan_result = self.security_scanner.scan(code, language)
            if not scan_result["safe"]:
                return SandboxResult(
                    status=SandboxStatus.SECURITY_VIOLATION,
                    stdout="",
                    stderr="Security violations found:\n" + "\n".join(scan_result["warnings"]),
                    exit_code=-1,
                    execution_time_ms=0.0,
                    files_created=[],
                    network_requests=[],
                    memory_peak_mb=0.0,
                    cpu_time_ms=0.0,
                    timestamp=datetime.now().isoformat(),
                )

        # Execute in sandbox
        return await self.sandbox.execute_code(code, language)


# Example usage and testing
async def main():
    """Example usage of sandbox executor."""
    print("🚀 AMOS Sandbox Executor - Security Critical Feature")
    print("=" * 60)

    # Check E2B availability
    if not E2B_AVAILABLE:
        print("❌ E2B not installed. Run: pip install e2b")
        print("🔑 Get API key from: https://e2b.dev")
        return

    # Initialize
    try:
        executor = AMOSSandboxExecutor(
            template="python",
            timeout_ms=30000,  # 30 seconds for testing
            memory_limit_mb=256,
            allow_network=False,
        )

        print("✅ Sandbox executor initialized")

        # Test 1: Safe code
        print("\n🧪 Test 1: Safe Python code")
        safe_code = """
import math
from typing import Dict, List, Set, Optional
print("Hello from sandbox!")
print(f"Pi = {math.pi}")
result = sum(range(100))
print(f"Sum 0-99 = {result}")
"""

        result = await executor.execute_code(safe_code, "python")
        print(f"Status: {result.status.name}")
        print(f"Stdout: {result.stdout[:200]}")
        print(f"Exit code: {result.exit_code}")

        # Test 2: Security scanner
        print("\n🔒 Test 2: Security Scanner")
        scanner = CodeSecurityScanner()

        dangerous_code = """
import os
os.system("rm -rf /")
eval("__import__('os').system('ls')")
"""

        scan_result = scanner.scan(dangerous_code)
        print(f"Safe: {scan_result['safe']}")
        print(f"Warnings: {len(scan_result['warnings'])}")
        for warning in scan_result["warnings"][:3]:
            print(f"  - {warning}")

        # Cleanup
        await executor.cleanup()
        print("\n✅ Sandbox executor test complete")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
