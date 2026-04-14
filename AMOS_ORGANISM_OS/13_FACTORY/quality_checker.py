"""Quality Checker — Build Quality Assurance

Validates generated code and build artifacts for quality,
syntax correctness, and compliance with standards.
"""

from __future__ import annotations

import ast
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class QualityReport:
    """Quality check report for a build artifact."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    artifact_path: str = ""
    passed: bool = False
    score: float = 0.0  # 0-1 quality score
    syntax_valid: bool = False
    style_issues: list[str] = field(default_factory=list)
    security_issues: list[str] = field(default_factory=list)
    complexity_score: float = 0.0
    test_coverage: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class QualityChecker:
    """Checks quality of generated code and artifacts.

    Performs syntax validation, style checks, complexity analysis,
    and generates quality reports.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.reports: dict[str, QualityReport] = {}

    def check_file(self, file_path: Path) -> QualityReport:
        """Check quality of a single file."""
        report = QualityReport(
            artifact_path=str(file_path),
        )

        if not file_path.exists():
            report.passed = False
            report.style_issues = ["File does not exist"]
            self.reports[report.id] = report
            return report

        content = file_path.read_text()

        # Syntax check
        report.syntax_valid = self._check_syntax(content)

        # Style checks
        report.style_issues = self._check_style(content)

        # Complexity check
        report.complexity_score = self._calculate_complexity(content)

        # Security check
        report.security_issues = self._check_security(content)

        # Calculate overall score
        report.score = self._calculate_score(report)
        report.passed = report.syntax_valid and report.score >= 0.7

        self.reports[report.id] = report
        return report

    def _check_syntax(self, content: str) -> bool:
        """Check if Python code is syntactically valid."""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False

    def _check_style(self, content: str) -> list[str]:
        """Check code style issues."""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Line length check
            if len(line) > 100:
                issues.append(f"Line {i} too long ({len(line)} > 100)")

            # Trailing whitespace
            if line.rstrip() != line:
                issues.append(f"Line {i} has trailing whitespace")

        # Check imports at top
        import_lines = [
            i for i, line in enumerate(lines) if line.strip().startswith(("import ", "from "))
        ]
        if import_lines:
            non_import_after_import = False
            for i in range(min(import_lines), len(lines)):
                if (
                    i not in import_lines
                    and lines[i].strip()
                    and not lines[i].strip().startswith("#")
                ):
                    non_import_after_import = True
                if i in import_lines and non_import_after_import:
                    issues.append(f"Import at line {i+1} not at top of file")
                    break

        return issues

    def _calculate_complexity(self, content: str) -> float:
        """Calculate code complexity score (0-1, lower is simpler)."""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return 1.0

        # Count branches
        branches = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                branches += 1
            elif isinstance(node, (ast.Try, ast.ExceptHandler)):
                branches += 1

        # Normalize: 0-5 branches = 0.0-0.5, 10+ branches = 1.0
        score = min(1.0, branches / 10)
        return score

    def _check_security(self, content: str) -> list[str]:
        """Check for basic security issues."""
        issues = []

        # Check for eval/exec usage
        if "eval(" in content:
            issues.append("Uses eval() - security risk")
        if "exec(" in content:
            issues.append("Uses exec() - security risk")

        # Check for hardcoded passwords/tokens
        suspicious = ["password", "secret", "token", "key"]
        for word in suspicious:
            if f'{word} = "' in content.lower() or f"{word} = '" in content.lower():
                issues.append(f"Possible hardcoded {word}")

        return issues

    def _calculate_score(self, report: QualityReport) -> float:
        """Calculate overall quality score."""
        score = 1.0

        # Syntax validity (critical)
        if not report.syntax_valid:
            return 0.0

        # Style issues (minor penalty)
        score -= len(report.style_issues) * 0.02

        # Security issues (major penalty)
        score -= len(report.security_issues) * 0.1

        # Complexity (moderate penalty)
        score -= report.complexity_score * 0.2

        return max(0.0, min(1.0, score))

    def check_directory(self, directory: Path) -> list[QualityReport]:
        """Check all Python files in a directory."""
        reports = []
        for file_path in directory.rglob("*.py"):
            report = self.check_file(file_path)
            reports.append(report)
        return reports

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all quality checks."""
        if not self.reports:
            return {"total": 0, "passed": 0, "failed": 0, "average_score": 0}

        passed = sum(1 for r in self.reports.values() if r.passed)
        avg_score = sum(r.score for r in self.reports.values()) / len(self.reports)

        return {
            "total": len(self.reports),
            "passed": passed,
            "failed": len(self.reports) - passed,
            "average_score": round(avg_score, 2),
            "syntax_valid": sum(1 for r in self.reports.values() if r.syntax_valid),
        }

    def list_reports(self) -> list[dict[str, Any]]:
        """List all quality reports."""
        return [r.to_dict() for r in self.reports.values()]

    def get_status(self) -> dict[str, Any]:
        """Get checker status."""
        summary = self.get_summary()
        return {
            **summary,
            "checks_performed": [
                "syntax_validation",
                "style_check",
                "complexity_analysis",
                "security_scan",
            ],
        }


_CHECKER: Optional[QualityChecker] = None


def get_quality_checker(data_dir: Optional[Path] = None) -> QualityChecker:
    """Get or create global quality checker."""
    global _CHECKER
    if _CHECKER is None:
        _CHECKER = QualityChecker(data_dir)
    return _CHECKER
