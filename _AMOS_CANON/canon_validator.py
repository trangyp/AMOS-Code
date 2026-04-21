#!/usr/bin/env python3
"""Canon Validator - Validates compliance with canonical standards."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .canon_core import CanonCore, CanonCategory, CanonPriority


@dataclass
class ValidationIssue:
    code: str
    message: str
    severity: CanonPriority
    line: int | None = None
    column: int | None = None
    suggestion: str = ""


@dataclass
class ValidationResult:
    passed: bool
    file_path: str
    issues: list[ValidationIssue] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def add_issue(
        self,
        code: str,
        message: str,
        severity: CanonPriority,
        line: int | None = None,
        column: int | None = None,
        suggestion: str = "",
    ) -> None:
        self.issues.append(
            ValidationIssue(
                code=code,
                message=message,
                severity=severity,
                line=line,
                column=column,
                suggestion=suggestion,
            )
        )
        if severity in (CanonPriority.CRITICAL, CanonPriority.HIGH):
            self.passed = False


class CanonValidator:
    def __init__(self, core: CanonCore | None = None):
        self._core = core or CanonCore()

    def validate_file(self, file_path: Path) -> ValidationResult:
        result = ValidationResult(passed=True, file_path=str(file_path))
        if not file_path.exists():
            result.add_issue(
                "FILE_NOT_FOUND",
                f"File not found: {file_path}",
                CanonPriority.CRITICAL,
            )
            return result
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            result.add_issue(
                "READ_ERROR",
                f"Could not read file: {e}",
                CanonPriority.CRITICAL,
            )
            return result
        self._check_syntax(file_path, content, result)
        self._check_bare_except(content, result)
        self._check_datetime_deprecated(content, result)
        return result

    def _check_syntax(
        self, file_path: Path, content: str, result: ValidationResult
    ) -> None:
        if file_path.suffix != ".py":
            return
        try:
            ast.parse(content)
        except SyntaxError as e:
            result.add_issue(
                "SYNTAX_ERROR",
                f"Syntax error: {e.msg}",
                CanonPriority.CRITICAL,
                e.lineno,
                e.offset,
                "Fix the syntax error",
            )

    def _check_bare_except(self, content: str, result: ValidationResult) -> None:
        pattern = r"^\s*except:$"
        for match in re.finditer(pattern, content, re.MULTILINE):
            line_num = content[: match.start()].count("\n") + 1
            result.add_issue(
                "BARE_EXCEPT",
                "Bare except clause found",
                CanonPriority.HIGH,
                line_num,
                suggestion="Use 'except Exception:'",
            )

    def _check_datetime_deprecated(self, content: str, result: ValidationResult) -> None:
        pattern = r"datetime\.utcnow\(\)"
        for match in re.finditer(pattern, content):
            line_num = content[: match.start()].count("\n") + 1
            result.add_issue(
                "DEPRECATED_DATETIME",
                "Deprecated datetime.utcnow() found",
                CanonPriority.MEDIUM,
                line_num,
                suggestion="Use datetime.now(timezone.utc)",
            )
        if "from datetime import UTC" in content:
            line_num = content.find("from datetime import UTC")
            line_num = content[:line_num].count("\n") + 1
            result.add_issue(
                "MALFORMED_UTC",
                "Malformed UTC import",
                CanonPriority.MEDIUM,
                line_num,
                suggestion="Use 'from datetime import datetime, timezone'",
            )

    def validate_directory(
        self, dir_path: Path, pattern: str = "*.py"
    ) -> list[ValidationResult]:
        results = []
        if not dir_path.exists():
            return [
                ValidationResult(
                    passed=False,
                    file_path=str(dir_path),
                    issues=[
                        ValidationIssue(
                            "DIR_NOT_FOUND",
                            f"Directory not found: {dir_path}",
                            CanonPriority.CRITICAL,
                        )
                    ],
                )
            ]
        for file_path in dir_path.rglob(pattern):
            results.append(self.validate_file(file_path))
        return results

    def get_summary(self, results: list[ValidationResult]) -> dict[str, Any]:
        total_files = len(results)
        passed_files = sum(1 for r in results if r.passed)
        total_issues = sum(len(r.issues) for r in results)
        critical_issues = sum(
            1 for r in results for i in r.issues if i.severity == CanonPriority.CRITICAL
        )
        return {
            "total_files": total_files,
            "passed_files": passed_files,
            "failed_files": total_files - passed_files,
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
