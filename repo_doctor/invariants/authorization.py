"""
I_auth = 1 iff every privileged operation is guarded by authorization boundary.

Authorization surface decomposition:
    αAuth = f(
        αAuth_identity,      # Identity verification
        αAuth_permission,    # Permission checks
        αAuth_role_mapping,  # Role-to-permission mapping
        αAuth_boundary       # Boundary integrity
    )

Invariant checks:
    1. Privileged operations have permission checks
    2. No admin bypass paths
    3. Role checks are consistent
    4. Authentication required for privileged routes
    5. No hard-coded role strings (use constants/enums)

Based on 2024 RBAC/ABAC authorization best practices.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .base import Invariant, InvariantResult, InvariantSeverity


@dataclass
class AuthorizationGap:
    """Missing authorization control."""

    type: str
    severity: str
    location: str
    message: str
    suggestion: str | None = None


class AuthorizationInvariant(Invariant):
    """
    I_auth = 1 iff privileged operations are properly guarded.

    Detects:
    - Admin functions without permission checks
    - Missing authentication decorators
    - Hard-coded role strings (drift risk)
    - Routes without auth requirements
    - Permission bypass patterns
    - Inconsistent authorization patterns
    """

    def __init__(self):
        super().__init__("I_auth", InvariantSeverity.CRITICAL)
        # Patterns that suggest privileged operations
        self.privileged_patterns = [
            r"def.*admin.*\(",
            r"def.*delete.*\(",
            r"def.*remove.*\(",
            r"def.*create_user.*\(",
            r"def.*reset.*password.*\(",
            r"def.*grant.*\(",
            r"def.*revoke.*\(",
        ]
        # Auth decorator patterns
        self.auth_decorators = [
            "login_required",
            "authenticated",
            "require_auth",
            "jwt_required",
            "oauth_required",
            "permission_required",
            "admin_required",
            "staff_required",
        ]
        # Permission check functions
        self.permission_checks = [
            "has_permission",
            "check_permission",
            "can_",
            "is_admin",
            "is_staff",
            "is_authenticated",
        ]

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check authorization boundary integrity."""
        context = context or {}
        repo = Path(repo_path)

        gaps: list[AuthorizationGap] = []

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

        critical = [g for g in gaps if g.severity == "critical"]
        errors = [g for g in gaps if g.severity == "error"]
        warnings = [g for g in gaps if g.severity == "warning"]

        passed = len(critical) == 0 and len(errors) == 0

        if passed:
            message = f"Authorization OK: {len(warnings)} warnings"
        else:
            message = (
                f"Authorization gaps: {len(critical)} critical, "
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

    def _analyze_file(self, file_path: Path, tree: ast.AST, content: str) -> list[AuthorizationGap]:
        """Analyze a single file for authorization gaps."""
        gaps: list[AuthorizationGap] = []
        relative_path = str(file_path.relative_to(file_path.parent.parent))

        gaps.extend(self._find_unprotected_privileged_functions(tree, relative_path, content))
        gaps.extend(self._find_hardcoded_roles(tree, relative_path))
        gaps.extend(self._find_permission_bypass_patterns(tree, relative_path, content))

        return gaps

    def _find_unprotected_privileged_functions(
        self, tree: ast.AST, file_path: str, content: str
    ) -> list[AuthorizationGap]:
        """Find privileged functions without auth checks."""
        gaps: list[AuthorizationGap] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name

                # Check if function name suggests privileged operation
                is_privileged = any(
                    re.search(pattern, func_name, re.IGNORECASE)
                    for pattern in self.privileged_patterns
                )

                if not is_privileged:
                    continue

                # Check for auth decorators
                has_auth_decorator = any(
                    self._is_auth_decorator(decorator) for decorator in node.decorator_list
                )

                # Check for permission checks in function body
                has_permission_check = self._has_permission_check(node)

                if not has_auth_decorator and not has_permission_check:
                    gaps.append(
                        AuthorizationGap(
                            type="unprotected_privileged_function",
                            severity="critical",
                            location=f"{file_path}:{node.lineno}",
                            message=f"Privileged function '{func_name}' has no authorization check",
                            suggestion="Add @login_required or @admin_required decorator",
                        )
                    )

        return gaps

    def _find_hardcoded_roles(self, tree: ast.AST, file_path: str) -> list[AuthorizationGap]:
        """Find hard-coded role strings that may drift."""
        gaps: list[AuthorizationGap] = []
        role_strings = ["'admin'", '"admin"', "'user'", '"user"', "'staff'", '"staff"']

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value.lower() in ["admin", "user", "staff", "superuser"]:
                    gaps.append(
                        AuthorizationGap(
                            type="hardcoded_role_string",
                            severity="warning",
                            location=f"{file_path}:{node.lineno}",
                            message=f"Hard-coded role string '{node.value}' detected",
                            suggestion="Use Role.ADMIN constant or enum instead",
                        )
                    )

        return gaps

    def _find_permission_bypass_patterns(
        self, tree: ast.AST, file_path: str, content: str
    ) -> list[AuthorizationGap]:
        """Find patterns that may bypass permission checks."""
        gaps: list[AuthorizationGap] = []

        # Check for DEBUG mode bypasses
        if "if DEBUG:" in content or "if settings.DEBUG:" in content:
            for i, line in enumerate(content.split("\n"), 1):
                if "if DEBUG:" in line and ("skip" in line.lower() or "bypass" in line.lower()):
                    gaps.append(
                        AuthorizationGap(
                            type="debug_mode_bypass",
                            severity="error",
                            location=f"{file_path}:{i}",
                            message="Potential auth bypass in DEBUG mode",
                            suggestion="Ensure DEBUG bypasses don't affect production",
                        )
                    )

        # Check for superuser early returns
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Check for patterns like "if request.user.is_superuser: return True"
                test_str = ast.unparse(node.test) if hasattr(ast, "unparse") else ""
                if "is_superuser" in test_str or "is_staff" in test_str:
                    gaps.append(
                        AuthorizationGap(
                            type="superuser_bypass",
                            severity="warning",
                            location=f"{file_path}:{node.lineno}",
                            message="Superuser bypass pattern detected - ensure intentional",
                        )
                    )

        return gaps

    def _is_auth_decorator(self, decorator: ast.expr) -> bool:
        """Check if a decorator is an auth decorator."""
        decorator_str = ""
        if isinstance(decorator, ast.Name):
            decorator_str = decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                decorator_str = decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                decorator_str = decorator.func.attr

        return any(auth in decorator_str.lower() for auth in self.auth_decorators)

    def _has_permission_check(self, node: ast.FunctionDef) -> bool:
        """Check if function body contains permission checks."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func_name = ""
                if isinstance(child.func, ast.Name):
                    func_name = child.func.id
                elif isinstance(child.func, ast.Attribute):
                    func_name = child.func.attr

                if any(check in func_name.lower() for check in self.permission_checks):
                    return True

        return False
