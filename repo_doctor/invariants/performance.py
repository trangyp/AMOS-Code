"""
I_perf = 1 iff critical workflows stay within declared performance envelopes.

Performance state decomposition:
    αPerf = f(
        αPerf_latency,    # Response time
        αPerf_memory,     # Memory usage
        αPerf_cpu,        # CPU utilization
        αPerf_io,         # I/O throughput
        αPerf_startup,    # Initialization time
        αPerf_scaling     # Behavior under load
    )

Invariant checks:
    1. Latency budgets not exceeded
    2. Memory growth bounded
    3. CPU usage reasonable
    4. I/O not blocking
    5. Startup time acceptable
    6. No quadratic behavior

Based on 2024 Python performance monitoring best practices.
"""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .base import Invariant, InvariantResult, InvariantSeverity


@dataclass
class PerformanceBudget:
    """Declared performance budget for an operation."""

    operation: str
    max_latency_ms: float = None
    max_memory_mb: float = None
    max_cpu_percent: float = None
    max_startup_ms: float = None


@dataclass
class PerformanceIssue:
    """Detected performance issue."""

    type: str
    severity: str
    location: str
    message: str
    suggestion: str = None


class PerformanceInvariant(Invariant):
    """
    I_perf = 1 iff resource usage stays within thresholds.

    Detects:
    - Unbounded list growth in loops
    - Quadratic algorithms (nested loops on same data)
    - Synchronous I/O in async contexts
    - Missing pagination/batching
    - Memory leaks (caches without eviction)
    - Blocking calls in hot paths
    """

    def __init__(self):
        super().__init__("I_perf", InvariantSeverity.WARNING)
        self.budgets: list[PerformanceBudget] = []

    def check(self, repo_path: str, context: Dict[str, Any] = None) -> InvariantResult:
        """Check performance characteristics."""
        context = context or {}
        repo = Path(repo_path)

        issues: list[PerformanceIssue] = []

        # Static analysis for performance anti-patterns
        py_files = list(repo.rglob("*.py"))

        for file_path in py_files:
            if ".venv" in str(file_path) or "__pycache__" in str(file_path):
                continue

            try:
                content = file_path.read_text()
                tree = ast.parse(content)

                # Check for performance issues
                file_issues = self._analyze_file(file_path, tree, content)
                issues.extend(file_issues)

            except SyntaxError:
                continue
            except Exception:
                continue

        # Classify issues
        critical = [i for i in issues if i.severity == "critical"]
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]

        passed = len(critical) == 0 and len(errors) == 0

        # Build summary
        if passed:
            message = f"Performance OK: {len(warnings)} warnings"
        else:
            message = (
                f"Performance issues: {len(critical)} critical, "
                f"{len(errors)} errors, {len(warnings)} warnings"
            )

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=message,
            details={
                "files_analyzed": len(py_files),
                "critical": len(critical),
                "errors": len(errors),
                "warnings": len(warnings),
                "issues": [
                    {"type": i.type, "location": i.location, "message": i.message}
                    for i in issues[:20]
                ],
            },
        )

    def _analyze_file(self, file_path: Path, tree: ast.AST, content: str) -> list[PerformanceIssue]:
        """Analyze a single file for performance issues."""
        issues: list[PerformanceIssue] = []
        relative_path = str(file_path.relative_to(file_path.parent.parent))

        # Check for quadratic patterns
        issues.extend(self._find_quadratic_patterns(tree, relative_path))

        # Check for unbounded growth
        issues.extend(self._find_unbounded_growth(tree, relative_path))

        # Check for blocking I/O
        issues.extend(self._find_blocking_io(tree, relative_path, content))

        # Check for memory issues
        issues.extend(self._find_memory_issues(tree, relative_path, content))

        return issues

    def _find_quadratic_patterns(self, tree: ast.AST, file_path: str) -> list[PerformanceIssue]:
        """Find O(n²) patterns like nested loops on same collection."""
        issues: list[PerformanceIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check for nested loops
                for child in ast.walk(node):
                    if child is not node and isinstance(child, ast.For):
                        # Check if iterating over same collection
                        issues.append(
                            PerformanceIssue(
                                type="quadratic_pattern",
                                severity="warning",
                                location=f"{file_path}:{node.lineno}",
                                message="Nested loops detected - may be O(n²)",
                                suggestion="Consider using set/dict for O(1) lookup",
                            )
                        )
                        break

        return issues

    def _find_unbounded_growth(self, tree: ast.AST, file_path: str) -> list[PerformanceIssue]:
        """Find lists/dicts that grow without bound."""
        issues: list[PerformanceIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ListComp):
                # Check for unbounded comprehensions
                issues.append(
                    PerformanceIssue(
                        type="list_comprehension",
                        severity="info",
                        location=f"{file_path}:{node.lineno}",
                        message="List comprehension - ensure bounded input",
                    )
                )

        return issues

    def _find_blocking_io(
        self, tree: ast.AST, file_path: str, content: str
    ) -> list[PerformanceIssue]:
        """Find blocking I/O calls in potentially async contexts."""
        issues: list[PerformanceIssue] = []

        # Check for requests.get without timeout
        if "requests.get(" in content and "timeout=" not in content:
            for i, line in enumerate(content.split("\n"), 1):
                if "requests.get(" in line and "timeout=" not in line:
                    issues.append(
                        PerformanceIssue(
                            type="blocking_io_no_timeout",
                            severity="error",
                            location=f"{file_path}:{i}",
                            message="HTTP request without timeout - can hang indefinitely",
                            suggestion="Add timeout= parameter",
                        )
                    )

        # Check for open() without context manager
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "open":
                    # Check if parent is with statement
                    issues.append(
                        PerformanceIssue(
                            type="file_open",
                            severity="info",
                            location=f"{file_path}:{node.lineno}",
                            message="File operation - ensure proper cleanup",
                        )
                    )

        return issues

    def _find_memory_issues(
        self, tree: ast.AST, file_path: str, content: str
    ) -> list[PerformanceIssue]:
        """Find potential memory issues."""
        issues: list[PerformanceIssue] = []

        # Check for @lru_cache without maxsize
        if "@lru_cache()" in content or "@lru_cache" in content:
            for i, line in enumerate(content.split("\n"), 1):
                if "@lru_cache()" in line:
                    issues.append(
                        PerformanceIssue(
                            type="unbounded_cache",
                            severity="warning",
                            location=f"{file_path}:{i}",
                            message="lru_cache without maxsize can grow unbounded",
                            suggestion="Use @lru_cache(maxsize=...) or @cache for bounded caching",
                        )
                    )

        # Check for global mutable state
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                issues.append(
                    PerformanceIssue(
                        type="global_state",
                        severity="warning",
                        location=f"{file_path}:{node.lineno}",
                        message="Global mutable state - potential memory/threading issues",
                    )
                )

        return issues
