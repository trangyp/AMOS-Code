#!/usr/bin/env python3
"""AMOS Code Quality Analyzer - Real code analysis with brain integration."""

from __future__ import annotations

import ast
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from amos_brain_working import think
from amos_task_automation import TaskAutomation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos_quality")


@dataclass
class QualityIssue:
    """Code quality issue found."""

    file_path: str
    line: int
    severity: str
    category: str
    message: str
    suggestion: str | None = None


@dataclass
class FileQualityReport:
    """Quality report for a single file."""

    file_path: str
    total_lines: int
    issues: list[QualityIssue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "total_lines": self.total_lines,
            "issue_count": len(self.issues),
            "metrics": self.metrics,
            "score": round(self.score, 2),
            "issues": [
                {
                    "line": i.line,
                    "severity": i.severity,
                    "category": i.category,
                    "message": i.message,
                    "suggestion": i.suggestion,
                }
                for i in self.issues
            ],
        }


class CodeQualityAnalyzer:
    """Analyze code quality with automated fixes."""

    def __init__(self):
        self.task_auto = TaskAutomation()

    def analyze_file(self, file_path: str | Path) -> FileQualityReport:
        """Analyze a single Python file."""
        path = Path(file_path)
        if not path.exists():
            return FileQualityReport(file_path=str(path), total_lines=0, issues=[], score=0.0)

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            return FileQualityReport(
                file_path=str(path),
                total_lines=0,
                issues=[QualityIssue(str(path), 0, "error", "io", str(e), None)],
                score=0.0,
            )

        lines = content.split("\n")
        issues: list[QualityIssue] = []

        # Check 1: Python 3.9 compatibility
        if "| None" in content and "from __future__ import annotations" not in content:
            for i, line in enumerate(lines, 1):
                if "| None" in line and not line.strip().startswith("#"):
                    issues.append(
                        QualityIssue(
                            str(path),
                            i,
                            "warning",
                            "python39",
                            "Python 3.10+ union syntax without future import",
                            "Add 'from __future__ import annotations'",
                        )
                    )

        # Check 2: Bare except clauses
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped == "except:" or stripped.startswith("except :"):
                issues.append(
                    QualityIssue(
                        str(path),
                        i,
                        "error",
                        "exception",
                        "Bare except clause catches all exceptions including SystemExit",
                        "Use 'except Exception:' instead",
                    )
                )

        # Check 3: Deprecated datetime.utcnow()
        if "datetime.utcnow()" in content:
            for i, line in enumerate(lines, 1):
                if "datetime.utcnow()" in line:
                    issues.append(
                        QualityIssue(
                            str(path),
                            i,
                            "warning",
                            "deprecation",
                            "datetime.utcnow() is deprecated",
                            "Use datetime.now(timezone.utc)",
                        )
                    )

        # Check 4: Mutable default arguments
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for default in node.args.defaults:
                        if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            issues.append(
                                QualityIssue(
                                    str(path),
                                    node.lineno,
                                    "error",
                                    "mutable_default",
                                    f"Mutable default argument in function '{node.name}'",
                                    "Use None and initialize inside function",
                                )
                            )
        except SyntaxError:
            pass

        # Check 5: TODO/FIXME without reference
        for i, line in enumerate(lines, 1):
            stripped = line.strip().lower()
            if "# todo" in stripped or "# fixme" in stripped:
                if not re.search(r"#[\s]*(TODO|FIXME)[\s:]+[A-Z]+-\d+", line, re.I):
                    issues.append(
                        QualityIssue(
                            str(path),
                            i,
                            "info",
                            "todo",
                            "TODO/FIXME comment without ticket reference",
                            "Add ticket reference like TODO: ABC-123",
                        )
                    )

        # Calculate metrics
        metrics = {
            "blank_lines": sum(1 for l in lines if not l.strip()),
            "comment_lines": sum(1 for l in lines if l.strip().startswith("#")),
            "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith("#")]),
            "functions": content.count("def "),
            "classes": content.count("class "),
            "imports": content.count("import ") + content.count("from "),
        }

        # Calculate score (100 - penalties)
        score = 100.0
        for issue in issues:
            if issue.severity == "error":
                score -= 5
            elif issue.severity == "warning":
                score -= 2
            elif issue.severity == "info":
                score -= 0.5

        return FileQualityReport(
            file_path=str(path),
            total_lines=len(lines),
            issues=issues,
            metrics=metrics,
            score=max(0, score),
        )

    def analyze_directory(self, directory: str | Path) -> list[FileQualityReport]:
        """Analyze all Python files in directory."""
        reports = []
        path = Path(directory)

        for py_file in path.rglob("*.py"):
            # Skip hidden and cache directories
            if any(p.startswith(".") for p in py_file.parts):
                continue
            if "__pycache__" in str(py_file):
                continue

            report = self.analyze_file(py_file)
            reports.append(report)

        return reports

    def get_brain_recommendations(self, reports: list[FileQualityReport]) -> list[str]:
        """Get brain recommendations for code quality issues."""
        # Summarize issues
        error_count = sum(len(r.issues) for r in reports)
        file_count = len([r for r in reports if r.issues])

        if error_count == 0:
            return ["No critical issues found. Codebase is in good shape!"]

        # Use brain for recommendations
        try:
            result = think(
                f"Code quality analysis found {error_count} issues in {file_count} files. "
                "What are the top 3 priorities for fixing code quality issues?",
                {"context": "code_quality", "issue_count": error_count},
            )
            return [str(result.get("response", "Continue fixing issues systematically"))]
        except Exception as e:
            return [f"Brain consultation failed: {e}"]

    def generate_report(self, reports: list[FileQualityReport]) -> str:
        """Generate comprehensive quality report."""
        total_files = len(reports)
        files_with_issues = len([r for r in reports if r.issues])
        total_issues = sum(len(r.issues) for r in reports)

        error_count = sum(1 for r in reports for i in r.issues if i.severity == "error")
        warning_count = sum(1 for r in reports for i in r.issues if i.severity == "warning")

        avg_score = sum(r.score for r in reports) / len(reports) if reports else 0

        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "summary": {
                "total_files": total_files,
                "files_with_issues": files_with_issues,
                "total_issues": total_issues,
                "errors": error_count,
                "warnings": warning_count,
                "average_score": round(avg_score, 2),
            },
            "recommendations": self.get_brain_recommendations(reports),
            "files": [r.to_dict() for r in reports if r.issues],
        }

        return json.dumps(report, indent=2)


def main() -> int:
    """Run code quality analysis."""
    print("=" * 70)
    print("AMOS Code Quality Analyzer")
    print("=" * 70)

    analyzer = CodeQualityAnalyzer()

    # Analyze current directory
    print("\nAnalyzing Python files...")
    reports = analyzer.analyze_directory(".")

    # Generate and print report
    json_report = analyzer.generate_report(reports)
    print(json_report)

    # Summary
    error_files = [r for r in reports if any(i.severity == "error" for i in r.issues)]
    warning_files = [r for r in reports if any(i.severity == "warning" for i in r.issues)]

    print("\n" + "=" * 70)
    print(f"Files analyzed: {len(reports)}")
    print(f"Files with errors: {len(error_files)}")
    print(f"Files with warnings: {len(warning_files)}")
    print(f"Average quality score: {sum(r.score for r in reports) / len(reports):.1f}/100")
    print("=" * 70)

    return 1 if error_files else 0


if __name__ == "__main__":
    sys.exit(main())
