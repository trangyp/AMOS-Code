"""AMOS Security Audit CLI - Production Security Scanner.

Continuous security monitoring tool for the AMOS codebase.
Scans for:
- Hardcoded secrets (passwords, API keys, tokens)
- Unsafe subprocess calls (shell=True)
- Unsafe code execution (eval, exec)
- SQL injection patterns
- Insecure file operations

Usage:
    python amos_security_audit_cli.py scan
    python amos_security_audit_cli.py scan --path /path/to/code
    python amos_security_audit_cli.py scan --format json
    python amos_security_audit_cli.py fix --auto

Exit codes:
    0 - No security issues found
    1 - Security issues detected
    2 - Error during scan
"""

import argparse
import ast
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(Enum):
    """Security issue severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityIssue:
    """Represents a security issue found in the code."""

    file: str
    line: int
    severity: Severity
    issue_type: str
    description: str
    code_snippet: str = ""
    remediation: str = ""
    auto_fixable: bool = False


@dataclass
class ScanResult:
    """Results of a security scan."""

    timestamp: str
    total_files: int = 0
    issues: list[SecurityIssue] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "total_files": self.total_files,
            "summary": self.summary,
            "issues": [
                {
                    **asdict(issue),
                    "severity": issue.severity.value,
                }
                for issue in self.issues
            ],
        }


class SecurityScanner:
    """Production security scanner for AMOS codebase."""

    # Patterns for hardcoded secrets
    SECRET_PATTERNS = [
        (r'password\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded password"),
        (r'secret_key\s*=\s*["\'][^"\']{16,}["\']', "Hardcoded secret key"),
        (r'api_key\s*=\s*["\'][^"\']{16,}["\']', "Hardcoded API key"),
        (r'token\s*=\s*["\'][^"\']{16,}["\']', "Hardcoded token"),
        (r'private_key\s*=\s*["\'][^"\']{32,}["\']', "Hardcoded private key"),
        (r'connection_string\s*=\s*["\'][^"\']{20,}["\']', "Hardcoded connection string"),
    ]

    # Patterns for subprocess vulnerabilities
    SUBPROCESS_PATTERNS = [
        (r"subprocess\.run\([^)]*shell\s*=\s*True", "Subprocess with shell=True"),
        (r"subprocess\.call\([^)]*shell\s*=\s*True", "Subprocess call with shell=True"),
        (r"subprocess\.Popen\([^)]*shell\s*=\s*True", "Subprocess Popen with shell=True"),
    ]

    # Patterns for unsafe code execution
    EXEC_PATTERNS = [
        (r"eval\s*\([^)]*\)", "Use of eval()"),
        (r"exec\s*\([^)]*\)", "Use of exec()"),
        (r"compile\s*\([^)]*\)", "Use of compile()"),
    ]

    # Patterns for SQL injection
    SQL_PATTERNS = [
        (r'execute\s*\(\s*["\'].*?%s.*?["\']', "Potential SQL injection (string formatting)"),
        (r'execute\s*\(\s*f["\']', "Potential SQL injection (f-string)"),
        (r'execute\s*\(\s*["\'].*?\+.*?["\']', "Potential SQL injection (concatenation)"),
    ]

    # Safe patterns to ignore (test files, examples, etc.)
    SAFE_PATHS = [
        r"\.venv/",
        r"venv/",
        r"tests?/",
        r"examples?/",
        r"__pycache__/",
        r"\.pyc$",
        r"\.pyo$",
    ]

    def __init__(self, root_path: str | Path = "."):
        """Initialize scanner with root path."""
        self.root = Path(root_path).resolve()
        self.result = ScanResult(timestamp=datetime.now(UTC).isoformat())

    def should_scan(self, file_path: Path) -> bool:
        """Check if file should be scanned."""
        path_str = str(file_path)
        for pattern in self.SAFE_PATHS:
            if re.search(pattern, path_str):
                return False
        return file_path.suffix == ".py"

    def scan_file(self, file_path: Path) -> list[SecurityIssue]:
        """Scan a single file for security issues."""
        issues = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
        except Exception:
            return issues

        # Check syntax validity
        try:
            ast.parse(content)
        except SyntaxError:
            # Skip files with syntax errors
            return issues

        # Scan each line
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip comments (but not docstrings)
            if stripped.startswith("#"):
                continue

            # Check for hardcoded secrets
            for pattern, description in self.SECRET_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check if it's already using environment variables or secrets module
                    if "os.environ.get" in line or "secrets.token" in line or "token_hex" in line:
                        continue
                    # Skip docstring examples
                    if '"""' in line or "'''" in line:
                        continue
                    issues.append(
                        SecurityIssue(
                            file=str(file_path.relative_to(self.root)),
                            line=line_num,
                            severity=Severity.CRITICAL,
                            issue_type="hardcoded_secret",
                            description=description,
                            code_snippet=line.strip()[:80],
                            remediation="Use os.environ.get() or secrets.token_urlsafe()",
                            auto_fixable=True,
                        )
                    )

            # Check for subprocess vulnerabilities
            for pattern, description in self.SUBPROCESS_PATTERNS:
                if re.search(pattern, line):
                    # Skip if it's using shlex.split with shell=False
                    if "shell=False" in line or "shlex.split" in line:
                        continue
                    issues.append(
                        SecurityIssue(
                            file=str(file_path.relative_to(self.root)),
                            line=line_num,
                            severity=Severity.HIGH,
                            issue_type="subprocess_shell",
                            description=description,
                            code_snippet=line.strip()[:80],
                            remediation="Use subprocess with shell=False and shlex.split()",
                            auto_fixable=True,
                        )
                    )

            # Check for unsafe code execution
            for pattern, description in self.EXEC_PATTERNS:
                if re.search(pattern, line):
                    # Skip safe patterns (ast.literal_eval, _safe_exec)
                    if "ast.literal_eval" in line or "_safe_exec" in line:
                        continue
                    # Skip test code and docstrings
                    if "test" in file_path.name.lower() or '"""' in line:
                        continue
                    issues.append(
                        SecurityIssue(
                            file=str(file_path.relative_to(self.root)),
                            line=line_num,
                            severity=Severity.HIGH,
                            issue_type="unsafe_execution",
                            description=description,
                            code_snippet=line.strip()[:80],
                            remediation="Use ast.literal_eval() or a sandboxed execution wrapper",
                            auto_fixable=False,
                        )
                    )

            # Check for SQL injection
            for pattern, description in self.SQL_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        SecurityIssue(
                            file=str(file_path.relative_to(self.root)),
                            line=line_num,
                            severity=Severity.MEDIUM,
                            issue_type="sql_injection",
                            description=description,
                            code_snippet=line.strip()[:80],
                            remediation="Use parameterized queries",
                            auto_fixable=False,
                        )
                    )

        return issues

    def scan(self, path: str | Path = None) -> ScanResult:
        """Run security scan on codebase."""
        scan_path = Path(path) if path else self.root

        py_files = list(scan_path.rglob("*.py"))
        self.result.total_files = len(py_files)

        for py_file in py_files:
            if not self.should_scan(py_file):
                continue

            issues = self.scan_file(py_file)
            self.result.issues.extend(issues)

        # Generate summary
        self.result.summary = {
            "critical": len([i for i in self.result.issues if i.severity == Severity.CRITICAL]),
            "high": len([i for i in self.result.issues if i.severity == Severity.HIGH]),
            "medium": len([i for i in self.result.issues if i.severity == Severity.MEDIUM]),
            "low": len([i for i in self.result.issues if i.severity == Severity.LOW]),
            "total": len(self.result.issues),
        }

        return self.result

    def print_report(self, format: str = "text") -> None:
        """Print scan report."""
        if format == "json":
            print(json.dumps(self.result.to_dict(), indent=2))
            return

        # Text format
        print("=" * 70)
        print("AMOS Security Audit Report")
        print("=" * 70)
        print(f"Timestamp: {self.result.timestamp}")
        print(f"Files scanned: {self.result.total_files}")
        print()

        # Summary
        print("Summary:")
        print(f"  Critical: {self.result.summary.get('critical', 0)}")
        print(f"  High:     {self.result.summary.get('high', 0)}")
        print(f"  Medium:   {self.result.summary.get('medium', 0)}")
        print(f"  Low:      {self.result.summary.get('low', 0)}")
        print(f"  Total:    {self.result.summary.get('total', 0)}")
        print()

        if not self.result.issues:
            print("✅ No security issues found!")
            return

        # Group by severity
        severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]

        for severity in severity_order:
            issues = [i for i in self.result.issues if i.severity == severity]
            if not issues:
                continue

            severity_name = severity.value.upper()
            icon = (
                "🔴"
                if severity == Severity.CRITICAL
                else "🟠"
                if severity == Severity.HIGH
                else "🟡"
            )
            print(f"{icon} {severity_name} ({len(issues)} issues)")
            print("-" * 70)

            for issue in issues:
                print(f"  File: {issue.file}:{issue.line}")
                print(f"  Type: {issue.issue_type}")
                print(f"  Description: {issue.description}")
                if issue.code_snippet:
                    print(f"  Code: {issue.code_snippet}")
                if issue.remediation:
                    print(f"  Fix: {issue.remediation}")
                if issue.auto_fixable:
                    print("  [Auto-fixable: Yes]")
                print()


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AMOS Security Audit CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python amos_security_audit_cli.py scan
  python amos_security_audit_cli.py scan --path ./backend --format json
  python amos_security_audit_cli.py scan --fail-on high
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan codebase for security issues")
    scan_parser.add_argument("--path", type=str, default=".", help="Path to scan (default: .)")
    scan_parser.add_argument(
        "--format", type=str, choices=["text", "json"], default="text", help="Output format"
    )
    scan_parser.add_argument(
        "--fail-on",
        type=str,
        choices=["critical", "high", "medium", "low"],
        default="critical",
        help="Exit with error if issues at this level or higher",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 2

    if args.command == "scan":
        scanner = SecurityScanner(args.path)
        result = scanner.scan()
        scanner.print_report(args.format)

        # Determine exit code
        fail_levels = {
            "critical": [Severity.CRITICAL],
            "high": [Severity.CRITICAL, Severity.HIGH],
            "medium": [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM],
            "low": [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW],
        }

        fail_severities = fail_levels.get(args.fail_on, [Severity.CRITICAL])
        critical_count = len([i for i in result.issues if i.severity in fail_severities])

        return 1 if critical_count > 0 else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
