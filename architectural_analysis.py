#!/usr/bin/env python3
"""
Comprehensive Architectural Analysis for AMOS Codebase
Identifies and fixes architectural issues using state-of-the-art patterns.
"""

import ast
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ArchitectureIssue:
    """Represents an architectural issue found in the codebase."""

    issue_type: str
    severity: str  # critical, high, medium, low
    file_path: str
    line_number: int
    description: str
    remediation: str
    category: str  # authority, boundary, dependency, coupling, etc.


@dataclass
class AnalysisResult:
    """Complete analysis result."""

    total_files: int
    issues: list[ArchitectureIssue] = field(default_factory=list)
    files_with_os_environ: list[str] = field(default_factory=list)
    files_with_direct_imports: list[str] = field(default_factory=list)
    singleton_pattern_violations: list[str] = field(default_factory=list)
    hidden_dependencies: list[str] = field(default_factory=list)

    def get_issues_by_category(self) -> dict[str, list[ArchitectureIssue]]:
        result = defaultdict(list)
        for issue in self.issues:
            result[issue.category].append(issue)
        return dict(result)

    def get_critical_issues(self) -> list[ArchitectureIssue]:
        return [i for i in self.issues if i.severity == "critical"]

    def get_high_issues(self) -> list[ArchitectureIssue]:
        return [i for i in self.issues if i.severity == "high"]


class ArchitectureAnalyzer:
    """Analyzes Python codebase for architectural issues."""

    # Patterns to check
    OS_ENVIRON_PATTERNS = [
        r"os\.environ\[",
        r"os\.environ\.get\(",
        r"os\.getenv\(",
        r"getenv\(",
    ]

    SINGLETON_PATTERNS = [
        r"@lru_cache\(maxsize=1\)",
        r"@lru_cache\(\)",
    ]

    # Files that should use singleton pattern
    SINGLETON_EXPECTED = [
        "get_brain",
        "get_state_manager",
        "get_monitor",
        "get_meta_controller",
        "get_agent_bridge",
        "get_metrics",
    ]

    def __init__(self, repo_path: Union[str, Path]):
        self.repo_path = Path(repo_path)
        self.issues: list[ArchitectureIssue] = []
        self.python_files: list[Path] = []

    def analyze(self) -> AnalysisResult:
        """Run complete architectural analysis."""
        self._collect_python_files()
        self._analyze_os_environ_usage()
        self._analyze_singleton_patterns()
        self._analyze_hidden_dependencies()
        self._analyze_layer_violations()
        self._analyze_import_patterns()

        return AnalysisResult(
            total_files=len(self.python_files),
            issues=self.issues,
            files_with_os_environ=self._get_files_with_pattern(self.OS_ENVIRON_PATTERNS),
            singleton_pattern_violations=self._find_singleton_violations(),
            hidden_dependencies=self._find_hidden_dependencies(),
        )

    def _collect_python_files(self):
        """Collect all Python files in the repo."""
        exclude_dirs = {
            "__pycache__",
            ".venv",
            "venv",
            ".git",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
        }

        for path in self.repo_path.rglob("*.py"):
            if not any(excluded in str(path) for excluded in exclude_dirs):
                self.python_files.append(path)

    def _analyze_os_environ_usage(self):
        """Find direct os.environ usage (hidden interfaces)."""
        for file_path in self.python_files:
            try:
                content = file_path.read_text()
                for pattern in self.OS_ENVIRON_PATTERNS:
                    matches = list(re.finditer(pattern, content))
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1
                        # Check if it's in amos_brain/config.py (allowed)
                        if "amos_brain/config.py" not in str(file_path):
                            self.issues.append(
                                ArchitectureIssue(
                                    issue_type="hidden_interface",
                                    severity="high",
                                    file_path=str(file_path.relative_to(self.repo_path)),
                                    line_number=line_num,
                                    description=f"Direct os.environ access found (pattern: {pattern})",
                                    remediation="Move to amos_brain/config.py and import from there",
                                    category="hidden_interface",
                                )
                            )
            except Exception:
                pass

    def _analyze_singleton_patterns(self):
        """Check for proper singleton pattern usage."""
        for file_path in self.python_files:
            try:
                content = file_path.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check if function should be cached but isn't
                        if any(expected in node.name for expected in self.SINGLETON_EXPECTED):
                            has_cache = any(
                                isinstance(dec, ast.Name)
                                and dec.id == "lru_cache"
                                or isinstance(dec, ast.Call)
                                and isinstance(dec.func, ast.Name)
                                and dec.func.id == "lru_cache"
                                for dec in node.decorator_list
                            )
                            if not has_cache:
                                self.issues.append(
                                    ArchitectureIssue(
                                        issue_type="authority_inversion",
                                        severity="medium",
                                        file_path=str(file_path.relative_to(self.repo_path)),
                                        line_number=node.lineno,
                                        description=f"Function '{node.name}' should use @lru_cache for singleton pattern",
                                        remediation=f"Add @lru_cache(maxsize=1) decorator to {node.name}",
                                        category="authority",
                                    )
                                )
            except Exception:
                pass

    def _analyze_hidden_dependencies(self):
        """Find hidden/undeclared dependencies."""
        for file_path in self.python_files:
            try:
                content = file_path.read_text()

                # Check for subprocess calls (potential hidden dependencies)
                if "subprocess" in content and "import subprocess" in content:
                    self.issues.append(
                        ArchitectureIssue(
                            issue_type="shadow_dependency",
                            severity="medium",
                            file_path=str(file_path.relative_to(self.repo_path)),
                            line_number=1,
                            description="Uses subprocess - may have hidden system dependencies",
                            remediation="Document subprocess dependencies in requirements or configuration",
                            category="dependency",
                        )
                    )

                # Check for hardcoded paths
                hardcoded_paths = re.findall(r'["\'](?:/[^"\']+|\.[./][^"\']+)["\']', content)
                for path in hardcoded_paths:
                    if any(x in path for x in ["usr/", "opt/", "var/", "etc/", ".amos", "/tmp/"]):
                        self.issues.append(
                            ArchitectureIssue(
                                issue_type="hardcoded_path",
                                severity="low",
                                file_path=str(file_path.relative_to(self.repo_path)),
                                line_number=1,
                                description=f"Hardcoded path detected: {path[:30]}...",
                                remediation="Use configuration or environment variables for paths",
                                category="configuration",
                            )
                        )
            except Exception:
                pass

    def _analyze_layer_violations(self):
        """Analyze for layer violations (simplified)."""
        # Check for circular imports
        for file_path in self.python_files:
            try:
                content = file_path.read_text()
                tree = ast.parse(content)

                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)

                # Check for problematic import patterns
                if "amos_brain" in str(file_path):
                    # amos_brain should not import from higher-level modules
                    problematic = ["amos_api", "amos_server", "amos_dashboard"]
                    for imp in imports:
                        for prob in problematic:
                            if prob in str(imp):
                                self.issues.append(
                                    ArchitectureIssue(
                                        issue_type="layer_violation",
                                        severity="high",
                                        file_path=str(file_path.relative_to(self.repo_path)),
                                        line_number=1,
                                        description=f"amos_brain importing from higher layer: {imp}",
                                        remediation="Move shared code to amos_brain or use dependency inversion",
                                        category="boundary",
                                    )
                                )
            except Exception:
                pass

    def _analyze_import_patterns(self):
        """Analyze import patterns for folklore dependencies."""
        for file_path in self.python_files:
            try:
                content = file_path.read_text()
                tree = ast.parse(content)

                # Find try/except ImportError blocks (optional dependencies)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Try):
                        has_import_error = any(
                            isinstance(handler.type, ast.Name) and handler.type.id == "ImportError"
                            for handler in node.handlers
                            if handler.type
                        )
                        if has_import_error:
                            self.issues.append(
                                ArchitectureIssue(
                                    issue_type="folklore_dependency",
                                    severity="low",
                                    file_path=str(file_path.relative_to(self.repo_path)),
                                    line_number=node.lineno,
                                    description="Optional import with fallback - may hide dependency issues",
                                    remediation="Document optional dependencies explicitly in pyproject.toml",
                                    category="dependency",
                                )
                            )
            except Exception:
                pass

    def _get_files_with_pattern(self, patterns: list[str]) -> list[str]:
        """Get files matching patterns."""
        result = []
        for file_path in self.python_files:
            try:
                content = file_path.read_text()
                for pattern in patterns:
                    if re.search(pattern, content):
                        result.append(str(file_path.relative_to(self.repo_path)))
                        break
            except Exception:
                pass
        return result

    def _find_singleton_violations(self) -> list[str]:
        """Find files that should use singleton pattern but don't."""
        result = []
        for file_path in self.python_files:
            try:
                content = file_path.read_text()
                for expected in self.SINGLETON_EXPECTED:
                    if f"def {expected}(" in content:
                        if "@lru_cache" not in content:
                            result.append(str(file_path.relative_to(self.repo_path)))
            except Exception:
                pass
        return list(set(result))

    def _find_hidden_dependencies(self) -> list[str]:
        """Find files with hidden dependencies."""
        result = []
        for file_path in self.python_files:
            try:
                content = file_path.read_text()
                if "os.environ" in content or "os.getenv" in content:
                    if "config" not in str(file_path):
                        result.append(str(file_path.relative_to(self.repo_path)))
            except Exception:
                pass
        return result


def print_report(result: AnalysisResult):
    """Print analysis report."""
    print("=" * 80)
    print("AMOS ARCHITECTURAL ANALYSIS REPORT")
    print("=" * 80)
    print(f"\nTotal Python files analyzed: {result.total_files}")
    print(f"Total issues found: {len(result.issues)}")
    print(f"Critical issues: {len([i for i in result.issues if i.severity == 'critical'])}")
    print(f"High severity: {len([i for i in result.issues if i.severity == 'high'])}")
    print(f"Medium severity: {len([i for i in result.issues if i.severity == 'medium'])}")
    print(f"Low severity: {len([i for i in result.issues if i.severity == 'low'])}")

    print("\n" + "-" * 80)
    print("ISSUES BY CATEGORY")
    print("-" * 80)
    by_category = result.get_issues_by_category()
    for category, issues in sorted(by_category.items()):
        print(f"\n{category.upper()} ({len(issues)} issues):")
        for issue in issues[:5]:  # Show top 5 per category
            print(f"  [{issue.severity.upper()}] {issue.file_path}:{issue.line_number}")
            print(f"    {issue.description[:70]}...")
            print(f"    Fix: {issue.remediation[:60]}...")
        if len(issues) > 5:
            print(f"  ... and {len(issues) - 5} more")

    print("\n" + "=" * 80)
    print("FILES WITH OS.ENVIRON USAGE (Hidden Interfaces)")
    print("=" * 80)
    for f in sorted(result.files_with_os_environ)[:15]:
        print(f"  - {f}")
    if len(result.files_with_os_environ) > 15:
        print(f"  ... and {len(result.files_with_os_environ) - 15} more")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    analyzer = ArchitectureAnalyzer(".")
    result = analyzer.analyze()
    print_report(result)
