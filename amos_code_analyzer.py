from typing import Any

"""AMOS Code Analyzer
====================
Real code analysis tool for the AMOS brain.
Analyzes Python files for common issues.
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CodeIssue:
    """A code quality issue."""

    file: str
    line: int
    issue_type: str
    message: str
    severity: str = "warning"  # error, warning, info


@dataclass
class AnalysisResult:
    """Result of code analysis."""

    file: str
    issues: list[CodeIssue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def issue_count(self) -> int:
        return len(self.issues)


class AMOSCodeAnalyzer:
    """Analyzes Python code for quality issues."""

    def __init__(self):
        self.rules = [
            self._check_bare_except,
            self._check_long_lines,
            self._check_unused_imports,
            self._check_mutable_defaults,
        ]

    def analyze_file(self, filepath: str | Path) -> AnalysisResult:
        """Analyze a single file."""
        path = Path(filepath)

        if not path.exists():
            return AnalysisResult(
                file=str(path),
                issues=[CodeIssue(str(path), 0, "file_not_found", "File does not exist", "error")],
            )

        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
        except Exception as e:
            return AnalysisResult(
                file=str(path),
                issues=[CodeIssue(str(path), 0, "read_error", str(e), "error")],
            )

        # Try to parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return AnalysisResult(
                file=str(path),
                issues=[CodeIssue(str(path), e.lineno or 0, "syntax_error", str(e), "error")],
            )

        # Run analysis
        issues: list[CodeIssue] = []
        for rule in self.rules:
            found = rule(path, tree, lines)
            issues.extend(found)

        # Calculate metrics
        metrics = {
            "total_lines": len(lines),
            "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith("#")]),
            "function_count": len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
            "class_count": len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
        }

        return AnalysisResult(file=str(path), issues=issues, metrics=metrics)

    def analyze_directory(
        self,
        directory: str | Path,
        pattern: str = "*.py",
        max_files: int = 100,
    ) -> list[AnalysisResult]:
        """Analyze all files in directory."""
        results = []
        path = Path(directory)

        for i, file_path in enumerate(path.rglob(pattern)):
            if i >= max_files:
                break

            result = self.analyze_file(file_path)
            results.append(result)

        return results

    def _check_bare_except(
        self, filepath: Path, tree: ast.AST, lines: list[str]
    ) -> list[CodeIssue]:
        """Check for bare except clauses."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append(
                        CodeIssue(
                            str(filepath),
                            node.lineno,
                            "bare_except",
                            "Bare except clause - use 'except Exception:' instead",
                            "error",
                        )
                    )

        return issues

    def _check_long_lines(self, filepath: Path, tree: ast.AST, lines: list[str]) -> list[CodeIssue]:
        """Check for lines that are too long."""
        issues = []
        max_length = 100

        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                issues.append(
                    CodeIssue(
                        str(filepath),
                        i,
                        "long_line",
                        f"Line too long ({len(line)} > {max_length} characters)",
                        "warning",
                    )
                )

        return issues[:10]  # Limit to avoid overwhelming output

    def _check_unused_imports(
        self, filepath: Path, tree: ast.AST, lines: list[str]
    ) -> list[CodeIssue]:
        """Check for potentially unused imports."""
        issues = []

        imports = {}
        used_names = set()

        for node in ast.walk(tree):
            # Track imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.asname or alias.name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports[name] = node.lineno

            # Track name usage
            elif isinstance(node, ast.Name):
                used_names.add(node.id)

        # Find unused
        for name, line in imports.items():
            if name not in used_names and not name.startswith("_"):
                issues.append(
                    CodeIssue(
                        str(filepath),
                        line,
                        "unused_import",
                        f"Potentially unused import: {name}",
                        "info",
                    )
                )

        return issues[:5]

    def _check_mutable_defaults(
        self, filepath: Path, tree: ast.AST, lines: list[str]
    ) -> list[CodeIssue]:
        """Check for mutable default arguments."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults + node.args.kw_defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append(
                            CodeIssue(
                                str(filepath),
                                node.lineno,
                                "mutable_default",
                                f"Mutable default argument in function '{node.name}' - use None and initialize inside",
                                "error",
                            )
                        )

        return issues


def generate_report(results: list[AnalysisResult]) -> str:
    """Generate human-readable report."""
    lines = ["# Code Analysis Report", ""]

    total_issues = sum(r.issue_count for r in results)
    error_count = sum(1 for r in results for i in r.issues if i.severity == "error")

    lines.append(f"**Files analyzed:** {len(results)}")
    lines.append(f"**Total issues:** {total_issues}")
    lines.append(f"**Errors:** {error_count}")
    lines.append("")

    # Show files with errors first
    for result in results:
        if result.has_errors:
            lines.append(f"## {result.file} ❌")
        else:
            lines.append(f"## {result.file}")

        if result.issues:
            for issue in result.issues:
                icon = (
                    "🔴"
                    if issue.severity == "error"
                    else "🟡"
                    if issue.severity == "warning"
                    else "🔵"
                )
                lines.append(f"{icon} Line {issue.line}: {issue.message}")
        else:
            lines.append("✅ No issues found")

        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    # Demo: analyze this file
    analyzer = AMOSCodeAnalyzer()

    print("=== AMOS Code Analyzer Demo ===\n")

    # Analyze the new files created
    files = [
        "amos_meaning_compiler.py",
        "amos_realtime_streaming.py",
        "amos_github_tool.py",
    ]

    results = []
    for f in files:
        path = Path(f)
        if path.exists():
            result = analyzer.analyze_file(path)
            results.append(result)

            print(f"{f}:")
            print(f"  Lines: {result.metrics.get('total_lines', 0)}")
            print(f"  Functions: {result.metrics.get('function_count', 0)}")
            print(f"  Issues: {result.issue_count}")

            for issue in result.issues[:3]:
                print(f"  - Line {issue.line}: {issue.issue_type}")
            print()

    # Generate report
    report = generate_report(results)
    print("\n" + "=" * 50)
    print(report[:500])
