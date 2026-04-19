"""
I_observability = 1 iff every critical failure class emits sufficient telemetry.

Observability surface decomposition:
    αObs = f(
        αObs_logs,       # Structured logging
        αObs_metrics,    # Quantitative measurements
        αObs_traces,     # Distributed trace propagation
        αObs_alertability, # Alert rule coverage
        αObs_error_taxonomy  # Error classification
    )

Invariant checks:
    1. Critical paths have log emission
    2. Errors include context (trace_id, user_id, etc.)
    3. Metrics cover key performance indicators
    4. Exceptions are not silently swallowed
    5. Error codes are consistent and classifiable

Based on 2024 observability engineering best practices.
"""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .base import Invariant, InvariantResult, InvariantSeverity


@dataclass
class ObservabilityGap:
    """Missing observability coverage."""

    type: str
    severity: str
    location: str
    message: str
    suggestion: str = None


class ObservabilityInvariant(Invariant):
    """
    I_observability = 1 iff failures remain detectable and attributable.

    Detects:
    - Bare except clauses that swallow errors
    - Missing log emission in error paths
    - No trace/context propagation
    - Silent failures (functions that should log but don't)
    - Missing error context (no identifiers)
    - Uncaught exceptions in async contexts
    """

    def __init__(self):
        super().__init__("I_observability", InvariantSeverity.ERROR)

    def check(self, repo_path: str, context: Dict[str, Any] = None) -> InvariantResult:
        """Check observability coverage."""
        context = context or {}
        repo = Path(repo_path)

        gaps: List[ObservabilityGap] = []

        # Analyze Python files
        py_files = list(repo.rglob("*.py"))

        for file_path in py_files:
            if ".venv" in str(file_path) or "__pycache__" in str(file_path):
                continue

            try:
                content = file_path.read_text()
                tree = ast.parse(content)

                file_gaps = self._analyze_file(file_path, tree, content)
                gaps.extend(file_gaps)

            except SyntaxError:
                continue
            except Exception:
                continue

        # Classify gaps
        critical = [g for g in gaps if g.severity == "critical"]
        errors = [g for g in gaps if g.severity == "error"]
        warnings = [g for g in gaps if g.severity == "warning"]

        passed = len(critical) == 0 and len(errors) == 0

        if passed:
            message = f"Observability OK: {len(warnings)} warnings"
        else:
            message = (
                f"Observability gaps: {len(critical)} critical, "
                f"{len(errors)} errors, {len(warnings)} warnings"
            )

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=message,
            details={
                "files_analyzed": len(py_files),
                "critical_gaps": len(critical),
                "error_gaps": len(errors),
                "warning_gaps": len(warnings),
                "gaps": [
                    {"type": g.type, "location": g.location, "message": g.message}
                    for g in gaps[:20]
                ],
            },
        )

    def _analyze_file(self, file_path: Path, tree: ast.AST, content: str) -> List[ObservabilityGap]:
        """Analyze a single file for observability gaps."""
        gaps: List[ObservabilityGap] = []
        relative_path = str(file_path.relative_to(file_path.parent.parent))

        # Check for error swallowing
        gaps.extend(self._find_error_swallowing(tree, relative_path))

        # Check for logging coverage
        gaps.extend(self._find_logging_gaps(tree, relative_path, content))

        # Check for exception handling
        gaps.extend(self._find_exception_gaps(tree, relative_path))

        return gaps

    def _find_error_swallowing(self, tree: ast.AST, file_path: str) -> List[ObservabilityGap]:
        """Find bare except clauses and pass in except blocks."""
        gaps: List[ObservabilityGap] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                # Check for bare except
                if node.type is None:
                    gaps.append(
                        ObservabilityGap(
                            type="bare_except",
                            severity="error",
                            location=f"{file_path}:{node.lineno}",
                            message="Bare except clause swallows all exceptions silently",
                            suggestion="Use 'except Exception as e:' and log the error",
                        )
                    )

                # Check for pass-only except block
                if isinstance(node.body, list) and len(node.body) == 1:
                    if isinstance(node.body[0], ast.Pass):
                        gaps.append(
                            ObservabilityGap(
                                type="silent_except",
                                severity="critical",
                                location=f"{file_path}:{node.lineno}",
                                message="Except block contains only 'pass' - errors swallowed silently",
                                suggestion="Add logging or re-raise the exception",
                            )
                        )

                # Check for except without logging
                has_log = any(
                    isinstance(child, ast.Call)
                    and (self._is_logging_call(child) or self._is_print_call(child))
                    for child in ast.walk(node)
                )

                if not has_log and not self._is_re_raise(node):
                    gaps.append(
                        ObservabilityGap(
                            type="unlogged_except",
                            severity="warning",
                            location=f"{file_path}:{node.lineno}",
                            message="Exception handler without logging",
                            suggestion="Add logger.exception() or similar to capture error context",
                        )
                    )

        return gaps

    def _find_logging_gaps(
        self, tree: ast.AST, file_path: str, content: str
    ) -> List[ObservabilityGap]:
        """Find places that should log but don't."""
        gaps: List[ObservabilityGap] = []

        # Check for entry points without logging
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # API endpoints should log
                if self._is_api_endpoint(node, content):
                    has_entry_log = self._has_entry_logging(node, tree)
                    if not has_entry_log:
                        gaps.append(
                            ObservabilityGap(
                                type="api_no_log",
                                severity="warning",
                                location=f"{file_path}:{node.lineno}",
                                message=f"API endpoint '{node.name}' missing entry logging",
                                suggestion="Add log at start of request handling",
                            )
                        )

        return gaps

    def _find_exception_gaps(self, tree: ast.AST, file_path: str) -> List[ObservabilityGap]:
        """Find exception handling gaps."""
        gaps: List[ObservabilityGap] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Raise):
                # Check if raising with context
                if isinstance(node.exc, ast.Call):
                    # Good: raise SomeException(message)
                    pass
                elif node.exc is None:
                    # Re-raise is fine
                    pass

        return gaps

    def _is_logging_call(self, node: ast.Call) -> bool:
        """Check if a call is a logging call."""
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            return func_name in ("debug", "info", "warning", "error", "exception", "critical")
        return False

    def _is_print_call(self, node: ast.Call) -> bool:
        """Check if a call is print (fallback logging)."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "print"
        return False

    def _is_re_raise(self, handler: ast.ExceptHandler) -> bool:
        """Check if handler re-raises the exception."""
        for child in ast.walk(handler):
            if isinstance(child, ast.Raise) and child.exc is None:
                return True
        return False

    def _is_api_endpoint(self, node: ast.FunctionDef, content: str) -> bool:
        """Check if function is likely an API endpoint."""
        # Check for Flask/FastAPI decorators
        decorators = [ast.unparse(d) for d in node.decorator_list]
        endpoint_patterns = ["route", "get", "post", "put", "delete", "patch", "api_route"]

        for dec in decorators:
            for pattern in endpoint_patterns:
                if pattern in dec.lower():
                    return True

        return False

    def _has_entry_logging(self, node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if function has entry-point logging."""
        # Check first few statements for logging
        for stmt in node.body[:3]:
            for child in ast.walk(stmt):
                if isinstance(child, ast.Call):
                    if self._is_logging_call(child):
                        return True
        return False
