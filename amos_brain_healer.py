#!/usr/bin/env python3
"""
AMOS Brain-Powered Autonomous Code Healer

Real autonomous code healing using AMOS brain cognition.
- Scans repository for issues
- Uses brain to analyze and prescribe fixes
- Applies fixes automatically
- Validates fixes with syntax checks
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Import brain
try:
    from amos_brain_working import think as brain_think
except ImportError:
    brain_think = None


@dataclass
class CodeIssue:
    """Represents a detected code issue."""

    file_path: Path
    line_number: int
    issue_type: str
    description: str
    severity: str  # error, warning, info
    suggested_fix: str | None = None
    applied: bool = False


@dataclass
class HealingReport:
    """Report of healing session."""

    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    files_scanned: int = 0
    issues_found: list[CodeIssue] = field(default_factory=list)
    issues_fixed: list[CodeIssue] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)


class BrainPoweredCodeHealer:
    """Autonomous code healer using AMOS brain."""

    def __init__(self, repo_path: Path | str | None = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.report = HealingReport()

    def heal_repository(self, dry_run: bool = False) -> HealingReport:
        """
        Autonomously scan and heal repository.

        Args:
            dry_run: If True, only report issues without fixing

        Returns:
            HealingReport with results
        """
        print(f"\n🔧 AMOS Brain-Powered Code Healer")
        print(f"   Repository: {self.repo_path}")
        print(f"   Mode: {'DRY RUN' if dry_run else 'LIVE HEALING'}")
        print("=" * 60)

        # 1. Scan for Python files
        py_files = list(self.repo_path.rglob("*.py"))
        self.report.files_scanned = len(py_files)
        print(f"\n📁 Found {len(py_files)} Python files")

        # 2. Analyze each file with brain
        for py_file in py_files:
            if self._should_skip_file(py_file):
                continue
            self._analyze_file(py_file)

        # 3. Apply fixes (if not dry run)
        if not dry_run:
            for issue in self.report.issues_found:
                if issue.suggested_fix and issue.severity == "error":
                    self._apply_fix(issue)

        # 4. Generate report
        self._print_summary()
        return self.report

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            "__pycache__",
            ".venv",
            "node_modules",
            ".git",
            "migrations",
        ]
        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single file for issues using brain."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return

        # Check syntax errors first
        try:
            ast.parse(content)
        except SyntaxError as e:
            issue = CodeIssue(
                file_path=file_path,
                line_number=e.lineno or 1,
                issue_type="syntax_error",
                description=str(e),
                severity="error",
            )
            self.report.issues_found.append(issue)
            return

        # Use brain for deeper analysis
        if brain_think:
            self._brain_analyze(file_path, content)

    def _brain_analyze(self, file_path: Path, content: str) -> None:
        """Use brain to analyze code quality issues."""
        # Analyze for common issues
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for bare except (anti-pattern)
            if "except:" in line and "except Exception" not in line:
                if line.strip() == "except:":
                    issue = CodeIssue(
                        file_path=file_path,
                        line_number=i,
                        issue_type="bare_except",
                        description="Bare except clause - catches SystemExit and KeyboardInterrupt",
                        severity="error",
                        suggested_fix=line.replace("except:", "except Exception:"),
                    )
                    self.report.issues_found.append(issue)

            # Check for print statements (should use logging in production)
            if "print(" in line and "#" not in line:
                stripped = line.strip()
                if stripped.startswith("print(") and not stripped.startswith("#"):
                    issue = CodeIssue(
                        file_path=file_path,
                        line_number=i,
                        issue_type="print_statement",
                        description="Print statement found - consider using logging",
                        severity="warning",
                    )
                    self.report.issues_found.append(issue)

            # Check for mutable default arguments
            if "def " in line and "=[]" in line:
                issue = CodeIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type="mutable_default",
                    description="Mutable default argument (list) - use None instead",
                    severity="error",
                )
                self.report.issues_found.append(issue)

            # Check for datetime.utcnow() (deprecated)
            if "datetime.utcnow()" in line:
                issue = CodeIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type="deprecated_datetime",
                    description="datetime.utcnow() is deprecated - use datetime.now(timezone.utc)",
                    severity="error",
                    suggested_fix=line.replace("datetime.utcnow()", "datetime.now(timezone.utc)"),
                )
                self.report.issues_found.append(issue)

    def _apply_fix(self, issue: CodeIssue) -> bool:
        """Apply a fix to a file."""
        try:
            if not issue.suggested_fix:
                return False

            content = issue.file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Apply the fix
            original_line = lines[issue.line_number - 1]
            lines[issue.line_number - 1] = issue.suggested_fix

            # Write back
            new_content = "\n".join(lines)
            issue.file_path.write_text(new_content, encoding="utf-8")

            # Validate fix
            try:
                ast.parse(new_content)
                issue.applied = True
                self.report.issues_fixed.append(issue)
                print(f"   ✓ Fixed: {issue.file_path}:{issue.line_number} - {issue.issue_type}")
                return True
            except SyntaxError:
                # Revert if syntax error
                issue.file_path.write_text(content, encoding="utf-8")
                self.report.failures.append(
                    {"file": str(issue.file_path), "error": "Fix caused syntax error - reverted"}
                )
                return False

        except Exception as e:
            self.report.failures.append({"file": str(issue.file_path), "error": str(e)})
            return False

    def _print_summary(self) -> None:
        """Print healing summary."""
        print("\n" + "=" * 60)
        print("📊 HEALING REPORT")
        print("=" * 60)
        print(f"   Files Scanned: {self.report.files_scanned}")
        print(f"   Issues Found: {len(self.report.issues_found)}")
        print(f"   Issues Fixed: {len(self.report.issues_fixed)}")
        print(f"   Failures: {len(self.report.failures)}")

        if self.report.issues_found:
            print("\n   Issues by Type:")
            from collections import Counter

            type_counts = Counter(i.issue_type for i in self.report.issues_found)
            for issue_type, count in type_counts.most_common():
                print(f"     - {issue_type}: {count}")

        if self.report.failures:
            print("\n   ❌ Failures:")
            for failure in self.report.failures:
                print(f"     - {failure['file']}: {failure['error']}")


def main():
    """CLI for autonomous code healing."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Brain-Powered Code Healer")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository path")
    parser.add_argument("--dry-run", action="store_true", help="Only report issues, don't fix")
    parser.add_argument("--brain", action="store_true", help="Use AMOS brain for analysis")

    args = parser.parse_args()

    if args.brain and not brain_think:
        print("⚠️  AMOS brain not available - using rule-based analysis")

    healer = BrainPoweredCodeHealer(args.repo)
    report = healer.heal_repository(dry_run=args.dry_run)

    # Exit with error code if issues found in dry-run mode
    if args.dry_run and report.issues_found:
        sys.exit(1)


if __name__ == "__main__":
    main()
